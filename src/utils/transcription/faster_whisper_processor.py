import os
import torch
import logging
import time
from dotenv import load_dotenv
from typing import Optional, Dict, Any, List
from pathlib import Path

# Import faster-whisper
from faster_whisper import WhisperModel

from .gpu_utils import get_gpu_info, clear_gpu_memory
from .base_processor import BaseTranscriptionProcessor

# Load biến môi trường
load_dotenv()

# Cấu hình logging
logger = logging.getLogger(__name__)

# Danh sách các model được hỗ trợ
MODEL_TINY = 'tiny'
MODEL_BASE = 'base'
MODEL_SMALL = 'small'
MODEL_MEDIUM = 'medium'
MODEL_LARGE = 'large-v3'
MODEL_DISTIL_LARGE = 'distil-large-v3'

SUPPORTED_MODELS = [
    MODEL_TINY, MODEL_BASE, MODEL_SMALL, 
    MODEL_MEDIUM, MODEL_LARGE, MODEL_DISTIL_LARGE
]

def validate_model_name(model_name: str) -> str:
    """Kiểm tra và xác thực tên model"""
    if model_name not in SUPPORTED_MODELS:
        logger.warning(f"Model {model_name} không được hỗ trợ. Sử dụng {MODEL_BASE}")
        return MODEL_BASE
    return model_name

def format_timestamp(seconds):
    """Convert seconds to SRT timestamp format (HH:MM:SS,mmm)"""
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    seconds_remainder = seconds % 60
    milliseconds = int((seconds_remainder % 1) * 1000)
    return f"{hours:02d}:{minutes:02d}:{int(seconds_remainder):02d},{milliseconds:03d}"

class FasterWhisperProcessor(BaseTranscriptionProcessor):
    def __init__(self, model_name: str = MODEL_BASE, device: str = 'cuda', compute_type: str = 'float16'):
        """
        Khởi tạo FasterWhisperProcessor
        
        Args:
            model_name: Tên model Whisper (tiny, base, small, medium, large-v3, distil-large-v3)
            device: Thiết bị chạy model (cuda/cpu)
            compute_type: Loại tính toán (float16, float32, int8, int8_float16)
        """
        self.model_name = validate_model_name(model_name)
        
        # Kiểm tra CUDA và điều chỉnh thiết bị nếu cần
        self.device = device
        if device == 'cuda' and not torch.cuda.is_available():
            logger.warning("CUDA không khả dụng, sử dụng CPU thay thế")
            self.device = 'cpu'
            
        # Điều chỉnh compute_type tùy theo thiết bị
        self.compute_type = compute_type
        if self.device == 'cpu' and compute_type == 'float16':
            logger.warning("float16 không được hỗ trợ trên CPU, sử dụng float32 thay thế")
            self.compute_type = 'float32'
            
        self.model = None
        
    def load_model(self) -> None:
        """Load model Faster Whisper"""
        try:
            # Xóa bộ nhớ GPU trước khi load model
            if self.device == 'cuda':
                clear_gpu_memory()
                gpu_info = get_gpu_info()
                logger.info(f"GPU status before loading model: {gpu_info}")
            
            logger.info(f"Loading Faster Whisper model: {self.model_name} on {self.device} with {self.compute_type}")
            self.model = WhisperModel(self.model_name, device=self.device, compute_type=self.compute_type)
            logger.info(f"Model {self.model_name} loaded successfully")
            
            if self.device == 'cuda':
                gpu_info = get_gpu_info()
                logger.info(f"GPU status after loading model: {gpu_info}")
                
        except Exception as e:
            logger.error(f"Error loading model: {str(e)}")
            raise
            
    def transcribe_audio(self, audio_path: str) -> Optional[Dict[str, Any]]:
        """
        Chuyển đổi audio thành văn bản
        
        Args:
            audio_path: Đường dẫn đến file audio
            
        Returns:
            Dict chứa kết quả chuyển đổi hoặc None nếu có lỗi
        """
        if not self.model:
            self.load_model()
            
        try:
            logger.info(f"Starting transcription with model {self.model_name}")
            
            # Cấu hình cho transcribe
            transcribe_options = {
                "language": "en",  # Mặc định là tiếng Anh
                "beam_size": 5,
                "word_timestamps": True,  # Bật timestamp cho từng từ
                "condition_on_previous_text": True,  # Sử dụng ngữ cảnh từ đoạn trước
                "temperature": 0.0,  # Không sử dụng sampling
                "compression_ratio_threshold": 2.4,
                "no_speech_threshold": 0.6,
                "vad_filter": True,  # Bật VAD filter
                "vad_parameters": {"min_silence_duration_ms": 500}
            }
            
            # Thực hiện chuyển đổi
            segments, info = self.model.transcribe(audio_path, **transcribe_options)
            
            # Convert generator to list for easier handling
            segments_list = list(segments)
            
            # Format kết quả tương tự như whisper
            result = {
                "segments": [],
                "language": info.language
            }
            
            for segment in segments_list:
                words = []
                if hasattr(segment, 'words') and segment.words:
                    for word in segment.words:
                        words.append({
                            "start": word.start,
                            "end": word.end,
                            "word": word.word
                        })
                
                result["segments"].append({
                    "id": segment.id,
                    "start": segment.start,
                    "end": segment.end,
                    "text": segment.text,
                    "words": words
                })
                
            return result
            
        except Exception as e:
            logger.error(f"Error during transcription: {str(e)}")
            logger.error("Traceback:", exc_info=True)
            return None
            
        finally:
            # Dọn dẹp bộ nhớ GPU sau khi xử lý
            if self.device == 'cuda':
                clear_gpu_memory()
                gpu_info = get_gpu_info()
                logger.info(f"GPU status after cleanup: {gpu_info}")
                
    def write_srt(self, result: Dict[str, Any], output_path: str) -> bool:
        """
        Ghi kết quả chuyển đổi ra file SRT
        
        Args:
            result: Kết quả từ transcribe_audio
            output_path: Đường dẫn file SRT đầu ra
            
        Returns:
            bool: True nếu thành công, False nếu thất bại
        """
        try:
            logger.info(f"Writing subtitles to: {output_path}")
            with open(output_path, "w", encoding="utf-8") as f:
                for i, segment in enumerate(result["segments"], 1):
                    # Format timestamps as SRT format (HH:MM:SS,mmm)
                    start = format_timestamp(segment["start"])
                    end = format_timestamp(segment["end"])
                    
                    # Write SRT entry
                    f.write(f"{i}\n")
                    f.write(f"{start} --> {end}\n")
                    f.write(f"{segment['text'].strip()}\n\n")
            
            # Verify the output file
            if os.path.exists(output_path) and os.path.getsize(output_path) > 0:
                logger.info("Subtitle generation completed successfully!")
                return True
            else:
                logger.error(f"Subtitle file is empty or not created: {output_path}")
                return False
                
        except Exception as e:
            logger.error(f"Error writing SRT file: {str(e)}")
            return False 