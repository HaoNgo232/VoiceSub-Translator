import os
from pathlib import Path
from typing import List, Optional
import logging
from concurrent.futures import ThreadPoolExecutor
import tkinter as tk
from tkinter import ttk

from src.api.handler import APIHandler
from src.translator.subtitle import SubtitleTranslator
from src.utils.subtitle_generator import generate_subtitles

logger = logging.getLogger(__name__)

class SubtitleProcessor:
    def __init__(self, progress_callback=None):
        self.api_handler = APIHandler()
        self.translator = SubtitleTranslator(self.api_handler)
        self.progress_callback = progress_callback
        
    def process_videos(self, input_folder: str, output_folder: Optional[str] = None, 
                      generate: bool = True, translate: bool = False,
                      target_lang: str = "vi", service: str = "novita") -> None:
        """Xử lý tất cả video trong thư mục đầu vào"""
        video_files = self._get_video_files(input_folder)
        if not video_files:
            raise ValueError("Không tìm thấy file video nào trong thư mục đầu vào")
        total_files = len(video_files)
        for i, video_file in enumerate(video_files, 1):
            try:
                self._update_progress(i, total_files, f"Đang xử lý {video_file.name}")
                subtitle_file = self._handle_subtitle(video_file, output_folder, generate, input_folder)
                if self._should_skip_translation(subtitle_file, target_lang):
                    continue
                if translate and subtitle_file:
                    self._translate_subtitle(subtitle_file, target_lang, service)
            except Exception as e:
                logger.error(f"Lỗi khi xử lý file {video_file}: {str(e)}")
                self._update_progress(i, total_files, f"Lỗi: {str(e)}")

    def _update_progress(self, i, total, status):
        if self.progress_callback:
            self.progress_callback(i, total, status)

    def _handle_subtitle(self, video_file, output_folder, generate, input_folder):
        if generate:
            return self._generate_subtitle(video_file, output_folder, input_folder)
        return self._get_subtitle_file(video_file, output_folder)

    def _should_skip_translation(self, subtitle_file, target_lang):
        if subtitle_file:
            vi_subtitle = subtitle_file.parent / f"{subtitle_file.stem}_{target_lang}.srt"
            if vi_subtitle.exists():
                logger.info(f"Bỏ qua {subtitle_file.name} - đã có bản dịch")
                return True
        return False

    def _get_video_files(self, folder: str) -> List[Path]:
        """Lấy danh sách file video trong thư mục"""
        folder_path = Path(folder)
        video_extensions = {'.mp4', '.avi', '.mkv', '.mov', '.wmv'}
        return [f for f in folder_path.glob('**/*') 
                if f.suffix.lower() in video_extensions 
                and not f.stem.endswith('_vi')]  # Bỏ qua các file đã có đuôi _vi
        
    def _get_subtitle_file(self, video_file: Path, output_folder: Optional[str]) -> Optional[Path]:
        """Lấy đường dẫn file phụ đề tương ứng với video"""
        if output_folder:
            rel_path = video_file.relative_to(Path(input_folder))
            subtitle_file = Path(output_folder) / rel_path.with_suffix('.srt')
        else:
            subtitle_file = video_file.with_suffix('.srt')
        return subtitle_file if subtitle_file.exists() else None
        
    def _generate_subtitle(self, video_file: Path, output_folder: Optional[str], input_folder: str) -> Path:
        if output_folder:
            rel_path = video_file.relative_to(Path(input_folder))
            subtitle_path = Path(output_folder) / rel_path.with_suffix('.srt')
            subtitle_path.parent.mkdir(parents=True, exist_ok=True)
        else:
            subtitle_path = video_file.with_suffix('.srt')
        generate_subtitles(str(video_file), str(subtitle_path))
        return subtitle_path
        
    def _translate_subtitle(self, subtitle_file: Path, target_lang: str, service: str) -> None:
        """Dịch phụ đề"""
        output_file = subtitle_file.parent / f"{subtitle_file.stem}_{target_lang}.srt"
        self.translator.process_subtitle_file(str(subtitle_file), str(output_file), target_lang, service)

class ProgressWindow:
    def __init__(self, parent):
        self.window = tk.Toplevel(parent)
        self.window.title("Tiến trình xử lý")
        self.window.geometry("400x150")
        self.window.transient(parent)
        self.window.grab_set()
        
        # Progress bar
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(
            self.window, 
            variable=self.progress_var,
            maximum=100
        )
        self.progress_bar.grid(row=0, column=0, padx=10, pady=10, sticky=(tk.W, tk.E))
        
        # Status label
        self.status_var = tk.StringVar()
        self.status_label = ttk.Label(
            self.window,
            textvariable=self.status_var,
            wraplength=380
        )
        self.status_label.grid(row=1, column=0, padx=10, pady=5)
        
        # Cancel button
        self.cancel_button = ttk.Button(
            self.window,
            text="Hủy",
            command=self.cancel
        )
        self.cancel_button.grid(row=2, column=0, pady=10)
        
        self.cancelled = False
        
    def update(self, current: int, total: int, status: str):
        """Cập nhật tiến trình"""
        if self.cancelled:
            return
            
        progress = (current / total) * 100
        self.progress_var.set(progress)
        self.status_var.set(status)
        self.window.update()
        
    def cancel(self):
        """Hủy xử lý"""
        self.cancelled = True
        self.window.destroy()
        
    def close(self):
        """Đóng cửa sổ"""
        self.window.destroy() 