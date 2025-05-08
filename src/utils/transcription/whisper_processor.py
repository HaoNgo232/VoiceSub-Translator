import os
import torch
import whisper
import logging
import time
from dotenv import load_dotenv
from typing import Optional, Dict, Any
from pathlib import Path

from .gpu_utils import get_gpu_info, clear_gpu_memory

# Load biến môi trường
load_dotenv()

# Cấu hình logging
logger = logging.getLogger(__name__)

# Danh sách các model tiếng Anh được hỗ trợ
BASE_EN = 'base.en'
SUPPORTED_EN_MODELS = ['tiny.en', BASE_EN, 'small.en']

def validate_model_name(model_name: str) -> str:
    """Kiểm tra và xác thực tên model"""
    if model_name not in SUPPORTED_EN_MODELS:
        logger.warning(f"Model {model_name} không được hỗ trợ. Sử dụng {BASE_EN}")
        return BASE_EN
    return model_name

def format_timestamp(seconds):
    """Convert seconds to SRT timestamp format (HH:MM:SS,mmm)"""
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    seconds_remainder = seconds % 60
    milliseconds = int((seconds_remainder % 1) * 1000)
    return f"{hours:02d}:{minutes:02d}:{int(seconds_remainder):02d},{milliseconds:03d}"

class WhisperProcessor:
    def __init__(self, model_name: str = 'base.en', device: str = 'cuda'):
        """
        Khởi tạo WhisperProcessor
        
        Args:
            model_name: Tên model Whisper (tiny.en, base.en, small.en)
            device: Thiết bị chạy model (cuda/cpu)
        """
        self.model_name = validate_model_name(model_name)
        self.device = device if torch.cuda.is_available() else 'cpu'
        self.model = None
        
    def load_model(self) -> None:
        """Load model Whisper"""
        try:
            # Xóa bộ nhớ GPU trước khi load model
            if self.device == 'cuda':
                clear_gpu_memory()
                gpu_info = get_gpu_info()
                logger.info(f"GPU status before loading model: {gpu_info}")
            
            logger.info(f"Loading Whisper model: {self.model_name} on {self.device}")
            self.model = whisper.load_model(self.model_name, device=self.device)
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
                "language": "en",  # Luôn sử dụng tiếng Anh cho model .en
                "fp16": self.device == 'cuda',
                "verbose": False,
                "word_timestamps": True,  # Bật timestamp cho từng từ
                "condition_on_previous_text": True,  # Sử dụng ngữ cảnh từ đoạn trước
                "temperature": 0.0,  # Không sử dụng sampling
                "compression_ratio_threshold": 2.4,
                "logprob_threshold": -1.0,
                "no_speech_threshold": 0.6
            }
            
            # Thực hiện chuyển đổi
            result = self.model.transcribe(audio_path, **transcribe_options)
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