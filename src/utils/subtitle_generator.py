import os
import logging
from pathlib import Path
from typing import Optional, List, Dict, Any
from dotenv import load_dotenv

from .transcription import WhisperProcessor, format_timestamp
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

def check_subtitle_exists(video_path: str) -> bool:
    """
    Kiểm tra xem video đã có phụ đề chưa
    
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

def _check_and_adjust_vram(model_name, device):
    if device != 'cuda':
        return model_name, device
    try:
        gpu_info = get_gpu_info()
        available_vram = gpu_info.get('memory_free', 0)
        required_vram = {'tiny.en': 1, BASE_EN: 1, 'small.en': 2}.get(model_name, 1)
        if available_vram < required_vram * 1024:
            logger.warning(f"Not enough VRAM ({available_vram}MB) for {model_name} (requires ~{required_vram}GB)")
            if model_name == 'small.en':
                logger.info(f"Falling back to {BASE_EN} model")
                return BASE_EN, device
            elif model_name == BASE_EN:
                logger.info("Falling back to tiny.en model")
                return 'tiny.en', device
            elif available_vram < 1024:
                logger.info("Not enough VRAM, falling back to CPU")
                return model_name, 'cpu'
    except Exception as e:
        logger.warning(f"Could not check GPU info: {e}")
    return model_name, device

class WhisperManager:
    _instance = None
    _current_model = None
    _current_device = None
    _processor = None

    @classmethod
    def get_instance(cls, model_name=None, device=None):
        if (cls._instance is None or 
            (model_name and model_name != cls._current_model) or
            (device and device != cls._current_device)):
            if cls._processor is not None:
                try:
                    clear_gpu_memory()
                    logger.info("Cleared previous model from GPU memory")
                except Exception as e:
                    logger.warning(f"Could not clear GPU memory: {e}")
            model_name, device = _check_and_adjust_vram(model_name, device)
            try:
                cls._processor = WhisperProcessor(model_name=model_name, device=device)
                cls._current_model = model_name
                cls._current_device = device
                cls._instance = cls()
                logger.info(f"Loaded {model_name} model on {device}")
            except Exception as e:
                logger.error(f"Failed to load model: {e}")
                if device == 'cuda':
                    logger.info("Falling back to CPU")
                    return cls.get_instance(model_name, 'cpu')
                raise
        return cls._instance

    def transcribe(self, audio_path):
        if self._processor:
            return self._processor.transcribe_audio(audio_path)
        return None

    def write_srt(self, result, output_path):
        if self._processor:
            return self._processor.write_srt(result, output_path)
        return False

def generate_subtitles(
    video_path: str,
    output_path: Optional[str] = None,
    model_name: str = 'base.en',
    device: str = 'cuda',
    force: bool = False
) -> bool:
    """
    Tạo phụ đề cho video sử dụng Whisper
    
    Args:
        video_path: Đường dẫn đến file video
        output_path: Đường dẫn để lưu file phụ đề (mặc định là cùng thư mục với video)
        model_name: Tên model Whisper (tiny.en, base.en, small.en)
        device: Thiết bị chạy model (cuda/cpu)
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
        logger.info(f"Using model: {model_name}")
        logger.info(f"Device: {device}")
        
        manager = WhisperManager.get_instance(model_name, device)
        result = manager.transcribe(str(video_path))
        if result is None:
            logger.error("Subtitle generation failed")
            return False
            
        # Ghi kết quả ra file SRT
        return manager.write_srt(result, output_path)
        
    except Exception as e:
        logger.error(f"Error generating subtitles: {str(e)}")
        return False

if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='Generate subtitles for video files')
    parser.add_argument('video_path', help='Path to input video file')
    parser.add_argument('--output', '-o', help='Path to output SRT file')
    parser.add_argument('--model', '-m', help='Whisper model name')
    parser.add_argument('--device', '-d', help='Device to run on (cuda/cpu)')
    parser.add_argument('--force', '-f', action='store_true', help='Force regenerate subtitles even if they exist')
    
    args = parser.parse_args()
    
    success = generate_subtitles(
        args.video_path,
        output_path=args.output,
        model_name=args.model,
        device=args.device,
        force=args.force
    )
    
    if not success:
        exit(1) 