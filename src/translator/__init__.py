"""Translator package.

Module này chứa các lớp và hàm liên quan đến việc dịch phụ đề.
"""

# Thứ tự import quan trọng để tránh vòng lặp:
# 1. Các lớp khởi tạo đầu tiên
# 2. Các lớp phụ thuộc vào các lớp khởi tạo

# Import các lớp cơ sở trước
from .subtitle_processor import SubtitleProcessor
from .translator_service import TranslatorService, APITranslatorService

# Sau đó import các lớp phụ thuộc
from .subtitle import SubtitleTranslator

__all__ = [
    'SubtitleTranslator',
    'SubtitleProcessor',
    'TranslatorService',
    'APITranslatorService'
] 