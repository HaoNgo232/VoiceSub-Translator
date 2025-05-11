"""
Các thành phần xử lý phụ đề sử dụng Whisper và Faster-Whisper
"""

from .gpu_utils import get_gpu_info, clear_gpu_memory
from .audio_utils import extract_audio
from .base_processor import BaseTranscriptionProcessor
from .whisper_processor import WhisperProcessor, format_timestamp
from .faster_whisper_processor import FasterWhisperProcessor
from .processor_factory import (
    TranscriptionProcessorFactory, 
    ENGINE_OPENAI_WHISPER,
    ENGINE_FASTER_WHISPER,
    SUPPORTED_ENGINES
)

__all__ = [
    # Processors
    'BaseTranscriptionProcessor',
    'WhisperProcessor',
    'FasterWhisperProcessor',
    'TranscriptionProcessorFactory',
    
    # Constants
    'ENGINE_OPENAI_WHISPER',
    'ENGINE_FASTER_WHISPER',
    'SUPPORTED_ENGINES',
    
    # Utilities
    'format_timestamp',
    'get_gpu_info',
    'clear_gpu_memory',
    'extract_audio'
] 