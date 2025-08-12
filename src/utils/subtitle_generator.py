#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import logging
from pathlib import Path
from typing import Optional, List, Dict, Any
from dotenv import load_dotenv
import weakref
import gc
from functools import lru_cache
import threading

from .transcription import (
    format_timestamp,
    TranscriptionProcessorFactory,
    ENGINE_OPENAI_WHISPER,
    ENGINE_FASTER_WHISPER
)
from .transcription.gpu_utils import get_gpu_info, clear_gpu_memory

# Load biến môi trường
load_dotenv()

# Cấu hình logging
logging.basicConfig(
    level=os.getenv('LOG_LEVEL', 'INFO'),
    format=os.getenv('LOG_FORMAT', '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
)
logger = logging.getLogger(__name__)

BASE_EN = 'base.en'
BASE = 'base'

# Cache cho GPU info để tránh gọi API liên tục
_gpu_info_cache = {}
_gpu_info_cache_time = 0
GPU_INFO_CACHE_TTL = 30  # 30 giây

@lru_cache(maxsize=128)
def check_subtitle_exists(video_path: str) -> bool:
    """
    Kiểm tra xem video đã có phụ đề chưa (với cache)
    
    Args:
        video_path: Đường dẫn đến file video
        
    Returns:
        bool: True nếu đã có phụ đề, False nếu chưa có
    """
    video_path = Path(video_path)
    # Kiểm tra các định dạng phụ đề phổ biến
    subtitle_extensions = ['.srt', '.vtt', '.ass', '.ssa']
    for ext in subtitle_extensions:
        subtitle_path = video_path.with_suffix(ext)
        if subtitle_path.exists():
            logger.info(f"Found existing subtitle: {subtitle_path}")
            return True
    return False

def _get_cached_gpu_info():
    """Lấy thông tin GPU với cache để tránh gọi API liên tục"""
    global _gpu_info_cache, _gpu_info_cache_time
    import time
    
    current_time = time.time()
    if current_time - _gpu_info_cache_time > GPU_INFO_CACHE_TTL:
        try:
            _gpu_info_cache = get_gpu_info()
            _gpu_info_cache_time = current_time
        except Exception as e:
            logger.warning(f"Could not get GPU info: {e}")
            _gpu_info_cache = {}
    
    return _gpu_info_cache

def _check_and_adjust_vram(model_name, device, engine):
    if device != 'cuda':
        return model_name, device, engine

    try:
        gpu_info = _get_cached_gpu_info()
        available_vram = gpu_info.get('memory_free', 0)
        required_vram = _get_required_vram(model_name, engine)

        if available_vram < required_vram * 1024:
            logger.warning(f"Not enough VRAM ({available_vram}MB) for {model_name} (requires ~{required_vram}GB)")
            model_name = _fallback_model(model_name, engine)
            if model_name is None:
                return model_name, 'cpu', engine  # Fallback to CPU if no suitable model found

    except Exception as e:
        logger.warning(f"Could not check GPU info: {e}")

    return model_name, device, engine

def _get_required_vram(model_name, engine):
    if engine == ENGINE_OPENAI_WHISPER:
        return {'tiny.en': 1, 'base.en': 1, 'small.en': 2}.get(model_name, 1)
    else:  # faster-whisper
        return {'tiny': 0.5, 'base': 0.8, 'small': 1.5, 'medium': 3, 'large-v3': 5}.get(model_name, 1)

def _fallback_model(model_name, engine):
    if engine == ENGINE_OPENAI_WHISPER:
        if model_name == 'small.en':
            logger.info("Falling back to base.en model")
            return 'base.en'
        elif model_name == 'base.en':
            logger.info("Falling back to tiny.en model")
            return 'tiny.en'
    else:  # faster-whisper
        if model_name in ['large-v3', 'distil-large-v3']:
            logger.info("Falling back to medium model")
            return 'medium'
        elif model_name == 'medium':
            logger.info("Falling back to small model")
            return 'small'
        elif model_name == 'small':
            logger.info("Falling back to base model")
            return 'base'
    return None

class TranscriptionManager:
    _instance = None
    _current_model = None
    _current_device = None
    _current_engine = None
    _current_compute_type = None
    _processor = None
    _processor_ref = None  # Weak reference để tránh memory leak
    _initialization_lock = None
    _model_cache = {}  # Cache cho các model đã load
    _max_cache_size = 3  # Giới hạn số model trong cache
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._initialization_lock = threading.Lock()
        return cls._instance

    @classmethod
    def get_instance(cls, model_name=None, device=None, engine=ENGINE_OPENAI_WHISPER, compute_type='float16'):
        if cls._instance is None or cls._needs_reinitialization(model_name, device, engine, compute_type):
            with cls._initialization_lock:
                # Double-check pattern để tránh race condition
                if cls._instance is None or cls._needs_reinitialization(model_name, device, engine, compute_type):
                    cls._clear_previous_model()
                    model_name, device, engine = _check_and_adjust_vram(model_name, device, engine)
                    compute_type = cls._adjust_compute_type(device, engine, compute_type)
                    
                    # Kiểm tra cache trước khi khởi tạo mới
                    cache_key = f"{model_name}_{device}_{engine}_{compute_type}"
                    if cache_key in cls._model_cache:
                        cls._processor = cls._model_cache[cache_key]
                        cls._current_model = model_name
                        cls._current_device = device
                        cls._current_engine = engine
                        cls._current_compute_type = compute_type
                        logger.info(f"Loaded {engine} {model_name} model from cache on {device}")
                    else:
                        cls._initialize_processor(model_name, device, engine, compute_type)
                        # Thêm vào cache
                        cls._add_to_cache(cache_key, cls._processor)
            
        return cls._instance

    @classmethod
    def _add_to_cache(cls, key, processor):
        """Thêm processor vào cache với LRU logic"""
        if len(cls._model_cache) >= cls._max_cache_size:
            # Xóa model cũ nhất
            oldest_key = next(iter(cls._model_cache))
            old_processor = cls._model_cache.pop(oldest_key)
            try:
                # Cleanup model cũ
                if hasattr(old_processor, 'cleanup'):
                    old_processor.cleanup()
                del old_processor
                gc.collect()
            except Exception as e:
                logger.warning(f"Error cleaning up old model: {e}")
        
        cls._model_cache[key] = processor

    @classmethod
    def _needs_reinitialization(cls, model_name, device, engine, compute_type):
        return (model_name and model_name != cls._current_model) or \
               (device and device != cls._current_device) or \
               (engine and engine != cls._current_engine) or \
               (compute_type and compute_type != cls._current_compute_type)

    @classmethod
    def _clear_previous_model(cls):
        if cls._processor is not None:
            try:
                # Sử dụng weak reference để tránh memory leak
                if cls._processor_ref and cls._processor_ref():
                    clear_gpu_memory()
                    logger.info("Cleared previous model from GPU memory")
                cls._processor_ref = None
            except Exception as e:
                logger.warning(f"Could not clear GPU memory: {e}")

    @classmethod
    def _adjust_compute_type(cls, device, engine, compute_type):
        if device == 'cuda' and engine == ENGINE_FASTER_WHISPER:
            try:
                gpu_info = _get_cached_gpu_info()
                available_vram = gpu_info.get('memory_free', 0)
                if available_vram < 3000 and compute_type == 'float16':
                    logger.info("Low VRAM detected, switching to int8 precision")
                    return 'int8'
            except Exception:
                pass
        return compute_type

    @classmethod
    def _initialize_processor(cls, model_name, device, engine, compute_type):
        try:
            cls._processor = TranscriptionProcessorFactory.create_processor(
                engine=engine,
                model_name=model_name,
                device=device,
                compute_type=compute_type
            )
            # Tạo weak reference để tránh memory leak
            cls._processor_ref = weakref.ref(cls._processor)
            
            cls._current_model = model_name
            cls._current_device = device
            cls._current_engine = engine
            cls._current_compute_type = compute_type
            cls._instance = cls()
            logger.info(f"Loaded {engine} {model_name} model on {device}")
        except Exception as e:
            logger.error(f"Failed to load model: {e}")
            if device == 'cuda':
                logger.info("Falling back to CPU")
                return cls.get_instance(model_name, 'cpu', engine, compute_type)
            raise

    def transcribe(self, audio_path):
        if self._processor:
            return self._processor.transcribe_audio(audio_path)
        return None

    def write_srt(self, result, output_path):
        if self._processor:
            return self._processor.write_srt(result, output_path)
        return False

    @classmethod
    def cleanup_cache(cls):
        """Dọn dẹp cache và giải phóng memory"""
        try:
            for key, processor in cls._model_cache.items():
                if hasattr(processor, 'cleanup'):
                    processor.cleanup()
            cls._model_cache.clear()
            gc.collect()
            logger.info("Cleaned up model cache")
        except Exception as e:
            logger.warning(f"Error cleaning up cache: {e}")

def generate_subtitles(
    video_path: str,
    output_path: Optional[str] = None,
    model_name: str = 'base.en',
    device: str = 'cuda',
    engine: str = ENGINE_OPENAI_WHISPER,
    compute_type: str = 'float16',
    force: bool = False
) -> bool:
    """
    Tạo phụ đề cho video sử dụng Whisper hoặc Faster-Whisper
    
    Args:
        video_path: Đường dẫn đến file video
        output_path: Đường dẫn để lưu file phụ đề (mặc định là cùng thư mục với video)
        model_name: Tên model (tiny.en, base.en, small.en cho OpenAI Whisper; tiny, base, small, medium, large-v3, distil-large-v3 cho Faster-Whisper)
        device: Thiết bị chạy model (cuda/cpu)
        engine: Loại engine sử dụng (openai_whisper, faster_whisper)
        compute_type: Loại tính toán cho Faster-Whisper (float16, float32, int8, int8_float16)
        force: Bắt buộc tạo lại phụ đề ngay cả khi đã có
        
    Returns:
        bool: True nếu thành công, False nếu thất bại
    """
    try:
        # Kiểm tra xem đã có phụ đề chưa
        if not force and check_subtitle_exists(video_path):
            logger.info(f"Skipping {video_path} - subtitle already exists")
            return True
            
        # Tạo đường dẫn output nếu không được chỉ định
        if output_path is None:
            video_path = Path(video_path)
            output_path = str(video_path.with_suffix('.srt'))
            
        logger.info(f"Starting subtitle generation for: {video_path}")
        logger.info(f"Using engine: {engine}, model: {model_name}")
        logger.info(f"Device: {device}, compute type: {compute_type}")
        
        manager = TranscriptionManager.get_instance(model_name, device, engine, compute_type)
        result = manager.transcribe(str(video_path))
        if result is None:
            logger.error("Subtitle generation failed")
            return False
            
        # Ghi kết quả ra file SRT
        return manager.write_srt(result, output_path)
        
    except Exception as e:
        logger.error(f"Error generating subtitles: {str(e)}")
        return False

def convert_subtitles_to_srt(folder_path: str) -> bool:
    """
    Tìm và chuyển đổi tất cả các file phụ đề không phải SRT trong thư mục sang định dạng SRT
    
    Args:
        folder_path: Đường dẫn đến thư mục cần quét
        
    Returns:
        bool: True nếu thành công, False nếu thất bại
    """
    try:
        from .subtitle_format_converter import batch_convert_to_srt
        logger.info(f"Bắt đầu quét và chuyển đổi phụ đề trong thư mục: {folder_path}")
        batch_convert_to_srt(folder_path)
        return True
    except Exception as e:
        logger.error(f"Lỗi khi chuyển đổi phụ đề: {str(e)}")
        return False

if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='Generate subtitles for video files')
    parser.add_argument('video_path', help='Path to input video file')
    parser.add_argument('--output', '-o', help='Path to output SRT file')
    parser.add_argument('--model', '-m', help='Model name')
    parser.add_argument('--device', '-d', help='Device to run on (cuda/cpu)')
    parser.add_argument('--engine', '-e', choices=[ENGINE_OPENAI_WHISPER, ENGINE_FASTER_WHISPER], 
                        default=ENGINE_OPENAI_WHISPER, help='Engine to use')
    parser.add_argument('--compute_type', '-c', choices=['float16', 'float32', 'int8', 'int8_float16'],
                        default='float16', help='Compute type for Faster-Whisper')
    parser.add_argument('--force', '-f', action='store_true', help='Force regenerate subtitles even if they exist')
    parser.add_argument('--convert', action='store_true', help='Convert non-SRT subtitles to SRT format')
    
    args = parser.parse_args()
    
    if args.convert:
        success = convert_subtitles_to_srt(args.video_path)
    else:
        success = generate_subtitles(
            args.video_path,
            output_path=args.output,
            model_name=args.model,
            device=args.device,
            engine=args.engine,
            compute_type=args.compute_type,
            force=args.force
        )
    
    if not success:
        exit(1)