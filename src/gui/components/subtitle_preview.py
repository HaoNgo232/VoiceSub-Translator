import customtkinter as ctk
import tkinter as tk
from tkinter import filedialog
import os
from typing import Optional, List, Dict
import threading
import subprocess


class SubtitlePreviewPanel(ctk.CTkFrame):
    """Real-time subtitle preview panel"""
    
    def __init__(self, parent, **kwargs):
        super().__init__(parent, fg_color="#1A1A1A", **kwargs)
        
        # Configure grid
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        
        # Variables
        self.current_file = None
        self.subtitles = []
        
        # Create widgets
        self.create_widgets()
        
    def create_widgets(self):
        """Create preview widgets"""
        
        # Header
        header_frame = ctk.CTkFrame(self, fg_color="#2B2B2B")
        header_frame.grid(row=0, column=0, sticky="ew", padx=10, pady=(10, 5))
        header_frame.grid_columnconfigure(1, weight=1)
        
        # Title
        ctk.CTkLabel(
            header_frame,
            text="👁️ Xem trước phụ đề",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color="#4CAF50"
        ).grid(row=0, column=0, sticky="w", padx=15, pady=10)
        
        # File selection button
        self.select_btn = ctk.CTkButton(
            header_frame,
            text="📄 Chọn file phụ đề",
            command=self.select_subtitle_file,
            height=30,
            fg_color="#2196F3",
            hover_color="#1976D2"
        )
        self.select_btn.grid(row=0, column=1, sticky="e", padx=15, pady=10)
        
        # File info
        self.file_info_label = ctk.CTkLabel(
            header_frame,
            text="Chưa chọn file",
            font=ctk.CTkFont(size=11),
            text_color="#BDBDBD"
        )
        self.file_info_label.grid(row=1, column=0, columnspan=2, sticky="ew", padx=15, pady=(0, 10))
        
        # Preview area
        preview_frame = ctk.CTkFrame(self, fg_color="#0F0F0F")
        preview_frame.grid(row=1, column=0, sticky="nsew", padx=10, pady=(5, 10))
        preview_frame.grid_columnconfigure(0, weight=1)
        preview_frame.grid_rowconfigure(0, weight=1)
        
        # Subtitle list with scrollbar
        self.subtitle_list = ctk.CTkScrollableFrame(preview_frame, fg_color="#1A1A1A")
        self.subtitle_list.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        self.subtitle_list.grid_columnconfigure(0, weight=1)
        
        # Default message
        self.show_default_message()
        
    def show_default_message(self):
        """Show default message when no file selected"""
        # Clear existing content
        for widget in self.subtitle_list.winfo_children():
            widget.destroy()
            
        default_frame = ctk.CTkFrame(self.subtitle_list, fg_color="transparent")
        default_frame.grid(row=0, column=0, sticky="ew", pady=50)
        
        ctk.CTkLabel(
            default_frame,
            text="📄",
            font=ctk.CTkFont(size=48),
            text_color="#4CAF50"
        ).pack(pady=10)
        
        ctk.CTkLabel(
            default_frame,
            text="Chọn file phụ đề để xem trước",
            font=ctk.CTkFont(size=14),
            text_color="#BDBDBD"
        ).pack()
        
        ctk.CTkLabel(
            default_frame,
            text="Hỗ trợ định dạng: .srt, .vtt, .ass",
            font=ctk.CTkFont(size=11),
            text_color="#757575"
        ).pack(pady=(5, 0))
        
    def select_subtitle_file(self):
        """Select subtitle file to preview"""
        file_path = filedialog.askopenfilename(
            title="Chọn file phụ đề",
            filetypes=[
                ("Subtitle files", "*.srt *.vtt *.ass"),
                ("SRT files", "*.srt"),
                ("VTT files", "*.vtt"), 
                ("ASS files", "*.ass"),
                ("All files", "*.*")
            ]
        )
        
        if file_path and os.path.exists(file_path):
            self.load_subtitle_file(file_path)
            
    def load_subtitle_file(self, file_path: str):
        """Load and display subtitle file"""
        self.current_file = file_path
        
        # Update file info
        file_name = os.path.basename(file_path)
        file_size = os.path.getsize(file_path)
        size_str = self.format_file_size(file_size)
        self.file_info_label.configure(text=f"📄 {file_name} ({size_str})")
        
        # Load subtitles in background
        threading.Thread(target=self._load_subtitles_background, daemon=True).start()
        
    def _load_subtitles_background(self):
        """Load subtitles in background thread"""
        try:
            subtitles = self.parse_subtitle_file(self.current_file)
            # Update UI in main thread
            self.after(0, lambda: self.display_subtitles(subtitles))
        except Exception as e:
            self.after(0, lambda: self.show_error(str(e)))
            
    def parse_subtitle_file(self, file_path: str) -> List[Dict]:
        """Parse subtitle file and return subtitle entries"""
        subtitles = []
        
        if file_path.lower().endswith('.srt'):
            subtitles = self.parse_srt(file_path)
        elif file_path.lower().endswith('.vtt'):
            subtitles = self.parse_vtt(file_path)
        elif file_path.lower().endswith('.ass'):
            subtitles = self.parse_ass(file_path)
            
        return subtitles
        
    def parse_srt(self, file_path: str) -> List[Dict]:
        """Parse SRT file"""
        subtitles = []
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
        except UnicodeDecodeError:
            # Try different encodings
            for encoding in ['latin-1', 'cp1252', 'iso-8859-1']:
                try:
                    with open(file_path, 'r', encoding=encoding) as f:
                        content = f.read()
                    break
                except UnicodeDecodeError:
                    continue
            else:
                raise Exception("Không thể đọc file với encoding phù hợp")
                
        # Parse SRT format
        entries = content.strip().split('\n\n')
        
        for entry in entries:
            lines = entry.strip().split('\n')
            if len(lines) >= 3:
                try:
                    index = int(lines[0])
                    time_range = lines[1]
                    text = '\n'.join(lines[2:])
                    
                    # Parse time range
                    if ' --> ' in time_range:
                        start_time, end_time = time_range.split(' --> ')
                        
                        subtitles.append({
                            'index': index,
                            'start_time': start_time.strip(),
                            'end_time': end_time.strip(),
                            'text': text.strip()
                        })
                except ValueError:
                    continue
                    
        return subtitles
        
    def parse_vtt(self, file_path: str) -> List[Dict]:
        """Parse VTT file"""
        subtitles = []
        
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            
        current_entry = {}
        index = 0
        
        for line in lines:
            line = line.strip()
            
            if '-->' in line:
                # Time line
                if ' --> ' in line:
                    start_time, end_time = line.split(' --> ')
                    current_entry = {
                        'index': index,
                        'start_time': start_time.strip(),
                        'end_time': end_time.strip(),
                        'text': ''
                    }
                    index += 1
                    
            elif line and 'WEBVTT' not in line and current_entry:
                # Text line
                if current_entry.get('text'):
                    current_entry['text'] += '\n' + line
                else:
                    current_entry['text'] = line
                    
            elif not line and current_entry:
                # Empty line - end of entry
                if current_entry.get('text'):
                    subtitles.append(current_entry)
                current_entry = {}
                
        # Add last entry if exists
        if current_entry and current_entry.get('text'):
            subtitles.append(current_entry)
            
        return subtitles
        
    def parse_ass(self, file_path: str) -> List[Dict]:
        """Parse ASS file (basic parsing)"""
        subtitles = []
        
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            
        index = 0
        
        for line in lines:
            line = line.strip()
            
            if line.startswith('Dialogue:'):
                # Parse dialogue line
                parts = line.split(',', 9)
                if len(parts) >= 10:
                    start_time = parts[1].strip()
                    end_time = parts[2].strip()
                    text = parts[9].strip()
                    
                    # Clean up ASS formatting
                    text = self.clean_ass_text(text)
                    
                    subtitles.append({
                        'index': index,
                        'start_time': start_time,
                        'end_time': end_time,
                        'text': text
                    })
                    index += 1
                    
        return subtitles
        
    def clean_ass_text(self, text: str) -> str:
        """Clean ASS formatting from text"""
        import re
        
        # Remove ASS tags
        text = re.sub(r'\{[^}]*\}', '', text)
        # Remove \N line breaks
        text = text.replace('\\N', '\n')
        
        return text.strip()
        
    def display_subtitles(self, subtitles: List[Dict]):
        """Display subtitles in the preview area"""
        # Clear existing content
        for widget in self.subtitle_list.winfo_children():
            widget.destroy()
            
        self.subtitles = subtitles
        
        if not subtitles:
            self.show_empty_message()
            return
            
        # Display subtitle count
        count_frame = ctk.CTkFrame(self.subtitle_list, fg_color="#2B2B2B")
        count_frame.grid(row=0, column=0, sticky="ew", pady=(0, 10))
        
        ctk.CTkLabel(
            count_frame,
            text=f"📊 Tổng số phụ đề: {len(subtitles)}",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color="#4CAF50"
        ).pack(pady=10)
        
        # Display subtitles
        for i, subtitle in enumerate(subtitles):
            self.create_subtitle_widget(i + 1, subtitle)
            
    def create_subtitle_widget(self, row: int, subtitle: Dict):
        """Create widget for single subtitle entry"""
        subtitle_frame = ctk.CTkFrame(self.subtitle_list, fg_color="#2B2B2B")
        subtitle_frame.grid(row=row, column=0, sticky="ew", pady=2, padx=5)
        subtitle_frame.grid_columnconfigure(1, weight=1)
        
        # Index
        ctk.CTkLabel(
            subtitle_frame,
            text=f"#{subtitle['index']}",
            font=ctk.CTkFont(size=10, weight="bold"),
            text_color="#FF9800",
            width=40
        ).grid(row=0, column=0, sticky="nw", padx=10, pady=5)
        
        # Content frame
        content_frame = ctk.CTkFrame(subtitle_frame, fg_color="transparent")
        content_frame.grid(row=0, column=1, sticky="ew", padx=5, pady=5)
        content_frame.grid_columnconfigure(0, weight=1)
        
        # Time range
        time_text = f"⏰ {subtitle['start_time']} → {subtitle['end_time']}"
        ctk.CTkLabel(
            content_frame,
            text=time_text,
            font=ctk.CTkFont(size=9),
            text_color="#BDBDBD"
        ).grid(row=0, column=0, sticky="w", pady=(0, 2))
        
        # Subtitle text
        text_widget = ctk.CTkLabel(
            content_frame,
            text=subtitle['text'],
            font=ctk.CTkFont(size=11),
            text_color="#E0E0E0",
            wraplength=300,
            justify="left"
        )
        text_widget.grid(row=1, column=0, sticky="ew")
        
    def show_empty_message(self):
        """Show message when no subtitles found"""
        empty_frame = ctk.CTkFrame(self.subtitle_list, fg_color="transparent")
        empty_frame.grid(row=0, column=0, sticky="ew", pady=50)
        
        ctk.CTkLabel(
            empty_frame,
            text="📭",
            font=ctk.CTkFont(size=48),
            text_color="#FF9800"
        ).pack(pady=10)
        
        ctk.CTkLabel(
            empty_frame,
            text="Không tìm thấy phụ đề trong file",
            font=ctk.CTkFont(size=14),
            text_color="#BDBDBD"
        ).pack()
        
    def show_error(self, error_msg: str):
        """Show error message"""
        # Clear existing content
        for widget in self.subtitle_list.winfo_children():
            widget.destroy()
            
        error_frame = ctk.CTkFrame(self.subtitle_list, fg_color="transparent")
        error_frame.grid(row=0, column=0, sticky="ew", pady=50)
        
        ctk.CTkLabel(
            error_frame,
            text="❌",
            font=ctk.CTkFont(size=48),
            text_color="#F44336"
        ).pack(pady=10)
        
        ctk.CTkLabel(
            error_frame,
            text="Lỗi khi đọc file phụ đề",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color="#F44336"
        ).pack()
        
        ctk.CTkLabel(
            error_frame,
            text=error_msg,
            font=ctk.CTkFont(size=11),
            text_color="#BDBDBD",
            wraplength=300
        ).pack(pady=5)
        
    def format_file_size(self, size_bytes: int) -> str:
        """Format file size in human readable format"""
        if size_bytes < 1024:
            return f"{size_bytes} B"
        elif size_bytes < 1024 * 1024:
            return f"{size_bytes / 1024:.1f} KB"
        else:
            return f"{size_bytes / (1024 * 1024):.1f} MB"
            
    def refresh_preview(self):
        """Refresh current preview"""
        if self.current_file and os.path.exists(self.current_file):
            self.load_subtitle_file(self.current_file)