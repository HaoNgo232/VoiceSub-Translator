"""GUI package."""

# Cấu trúc import để tránh vòng lặp
# Import các components trước
from .components.main_app import SubtitleApp
from .subtitle_processor import SubtitleProcessor
from .components.progress_window import ProgressWindow
# Cuối cùng mới import main từ app
from .app import main

__all__ = [
    'SubtitleApp',
    'main',
    'SubtitleProcessor',
    'ProgressWindow'
]