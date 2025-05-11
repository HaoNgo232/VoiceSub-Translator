"""
Package chính cho ứng dụng tạo và dịch phụ đề.
"""

# Thứ tự import quan trọng để tránh vòng lặp:
# 1. Các module cơ sở utils và api
# 2. Các module phụ thuộc vào cơ sở (processor, translator)
# 3. Giao diện người dùng (gui) - phụ thuộc vào tất cả các thành phần khác

# Import API và Utils trước
from src.api import APIHandler
from src.utils import generate_subtitles
from src.utils.cache_manager import CacheManager, TranslationCacheManager

# Import các module trung gian
from src.translator import (
    SubtitleTranslator,
    SubtitleProcessor as TranslatorSubtitleProcessor,
    TranslatorService, 
    APITranslatorService
)

# Cuối cùng import GUI
from src.gui import SubtitleApp, SubtitleProcessor, ProgressWindow, main

__all__ = [
    # API
    'APIHandler',
    
    # Utils
    'generate_subtitles',
    'CacheManager',
    'TranslationCacheManager',
    
    # Translator
    'SubtitleTranslator',
    'TranslatorSubtitleProcessor',
    'TranslatorService',
    'APITranslatorService',
    
    # GUI
    'SubtitleApp',
    'SubtitleProcessor',
    'ProgressWindow',
    'main'
] 