import logging
from typing import Optional, Dict, Any

from .base_processor import BaseTranscriptionProcessor
from .whisper_processor import WhisperProcessor
from .faster_whisper_processor import FasterWhisperProcessor

logger = logging.getLogger(__name__)

# Engine Constants
ENGINE_OPENAI_WHISPER = "openai_whisper"
ENGINE_FASTER_WHISPER = "faster_whisper"

SUPPORTED_ENGINES = [ENGINE_OPENAI_WHISPER, ENGINE_FASTER_WHISPER]

class TranscriptionProcessorFactory:
    """
    Factory để tạo ra các transcription processor
    """
    
    @staticmethod
    def create_processor(engine: str, model_name: str, device: str = 'cuda', **kwargs) -> Optional[BaseTranscriptionProcessor]:
        """
        Tạo processor dựa trên engine được chọn
        
        Args:
            engine: Loại engine (openai_whisper, faster_whisper)
            model_name: Tên model
            device: Thiết bị (cuda, cpu)
            **kwargs: Tham số bổ sung cho processor cụ thể
            
        Returns:
            BaseTranscriptionProcessor hoặc None nếu không hỗ trợ
        """
        if engine not in SUPPORTED_ENGINES:
            logger.error(f"Engine {engine} không được hỗ trợ. Sử dụng {ENGINE_OPENAI_WHISPER}")
            engine = ENGINE_OPENAI_WHISPER
            
        logger.info(f"Creating {engine} processor with model {model_name} on {device}")
        
        if engine == ENGINE_OPENAI_WHISPER:
            return WhisperProcessor(model_name=model_name, device=device)
        elif engine == ENGINE_FASTER_WHISPER:
            # Extract compute_type for FasterWhisperProcessor if provided
            compute_type = kwargs.get('compute_type', 'float16')
            return FasterWhisperProcessor(model_name=model_name, device=device, compute_type=compute_type)
        
        return None 