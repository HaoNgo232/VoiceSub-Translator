"""
Các components cho giao diện
"""

# Import các thành phần độc lập trước
from .prompt_dialog import PromptDialog
from .progress_window import ProgressWindow

# Chỉ export tên class mà không import trực tiếp để tránh circular import
__all__ = [
    'PromptDialog',
    'ProgressWindow', 
    'SubtitleApp'  # Vẫn xuất tên nhưng không import trực tiếp
]

# Người dùng có thể import như sau:
# from src.gui.components import SubtitleApp
# Khi đó mới thực sự import:
from .main_app import SubtitleApp 