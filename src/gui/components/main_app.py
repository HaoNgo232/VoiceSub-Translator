import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import json
import os
from pathlib import Path
from typing import Dict, Optional
import threading

from src.gui.subtitle_processor import SubtitleProcessor
from src.gui.components.progress_window import ProgressWindow
from src.gui.components.prompt_dialog import PromptDialog

class SubtitleApp:
    """Ứng dụng chính xử lý phụ đề"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("Công cụ xử lý phụ đề")
        self.root.geometry("800x600")
        
        # Biến lưu trữ
        self.prompts: Dict[str, str] = {}
        self.current_prompt: Optional[str] = None
        self.input_folder: Optional[str] = None
        self.output_folder: Optional[str] = None
        
        # Tải prompts từ file
        self.load_prompts()
        
        # Tạo giao diện
        self.create_widgets()
        
    def load_prompts(self):
        """Tải prompts từ file config"""
        config_path = Path("config/prompts.json")
        if config_path.exists():
            with open(config_path, "r", encoding="utf-8") as f:
                self.prompts = json.load(f)
        else:
            # Prompt mặc định
            self.prompts = {
                "default": """Translate the following text to {target_lang}. 
IMPORTANT INSTRUCTIONS:
1. Only return the translated text, without any explanations or notes
2. Keep the original format and timing information
3. Keep technical terms and IT concepts in English (e.g. API, CPU, RAM, etc.)
4. Keep certification names in English (e.g. CISP, CISM, etc.)
5. Keep company names in English
6. Keep product names in English
7. Keep programming languages and frameworks in English
8. Keep file extensions in English
9. Keep commands and code snippets in English

Text to translate:
{text}"""
            }
            # Tạo thư mục config nếu chưa tồn tại
            config_path.parent.mkdir(parents=True, exist_ok=True)
            # Lưu prompts mặc định
            with open(config_path, "w", encoding="utf-8") as f:
                json.dump(self.prompts, f, indent=4, ensure_ascii=False)
        
        self.current_prompt = "default"
        
    def save_prompts(self):
        """Lưu prompts vào file config"""
        config_path = Path("config/prompts.json")
        with open(config_path, "w", encoding="utf-8") as f:
            json.dump(self.prompts, f, indent=4, ensure_ascii=False)
            
    def create_widgets(self):
        """Tạo các widget cho giao diện"""
        # Frame chính
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Phần chọn thư mục
        folder_frame = ttk.LabelFrame(main_frame, text="Thư mục", padding="5")
        folder_frame.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        
        # Input folder
        ttk.Label(folder_frame, text="Thư mục đầu vào:").grid(row=0, column=0, sticky=tk.W)
        self.input_folder_var = tk.StringVar()
        ttk.Entry(folder_frame, textvariable=self.input_folder_var, width=50).grid(row=0, column=1, padx=5)
        ttk.Button(folder_frame, text="Chọn", command=self.select_input_folder).grid(row=0, column=2)
        
        # Output folder
        ttk.Label(folder_frame, text="Thư mục đầu ra:").grid(row=1, column=0, sticky=tk.W)
        self.output_folder_var = tk.StringVar()
        ttk.Entry(folder_frame, textvariable=self.output_folder_var, width=50).grid(row=1, column=1, padx=5)
        ttk.Button(folder_frame, text="Chọn", command=self.select_output_folder).grid(row=1, column=2)
        
        # Phần quản lý prompts
        prompt_frame = ttk.LabelFrame(main_frame, text="Quản lý Prompts", padding="5")
        prompt_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=5)
        
        # Chọn prompt
        ttk.Label(prompt_frame, text="Chọn prompt:").grid(row=0, column=0, sticky=tk.W)
        self.prompt_var = tk.StringVar(value=self.current_prompt)
        prompt_combo = ttk.Combobox(prompt_frame, textvariable=self.prompt_var, values=list(self.prompts.keys()))
        prompt_combo.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=5)
        prompt_combo.bind("<<ComboboxSelected>>", self.on_prompt_selected)
        
        # Nút thêm/sửa/xóa prompt
        ttk.Button(prompt_frame, text="Thêm mới", command=self.add_prompt).grid(row=0, column=2, padx=2)
        ttk.Button(prompt_frame, text="Sửa", command=self.edit_prompt).grid(row=0, column=3, padx=2)
        ttk.Button(prompt_frame, text="Xóa", command=self.delete_prompt).grid(row=0, column=4, padx=2)
        
        # Hiển thị nội dung prompt
        ttk.Label(prompt_frame, text="Nội dung prompt:").grid(row=1, column=0, sticky=tk.W)
        self.prompt_text = tk.Text(prompt_frame, height=10, width=70)
        self.prompt_text.grid(row=2, column=0, columnspan=5, sticky=(tk.W, tk.E))
        self.prompt_text.insert("1.0", self.prompts[self.current_prompt])
        
        # Phần nút điều khiển
        control_frame = ttk.Frame(main_frame)
        control_frame.grid(row=2, column=0, columnspan=2, pady=10)
        
        ttk.Button(control_frame, text="Tạo phụ đề", command=self.generate_subtitles).grid(row=0, column=0, padx=5)
        ttk.Button(control_frame, text="Dịch phụ đề", command=self.translate_subtitles).grid(row=0, column=1, padx=5)
        
    def select_input_folder(self):
        """Chọn thư mục đầu vào"""
        folder = filedialog.askdirectory()
        if folder:
            self.input_folder = folder
            self.input_folder_var.set(folder)
            
    def select_output_folder(self):
        """Chọn thư mục đầu ra"""
        folder = filedialog.askdirectory()
        if folder:
            self.output_folder = folder
            self.output_folder_var.set(folder)
            
    def on_prompt_selected(self, event):
        """Xử lý khi chọn prompt từ combobox"""
        prompt_name = self.prompt_var.get()
        if prompt_name in self.prompts:
            self.current_prompt = prompt_name
            self.prompt_text.delete("1.0", tk.END)
            self.prompt_text.insert("1.0", self.prompts[prompt_name])
            
    def add_prompt(self):
        """Thêm prompt mới"""
        dialog = PromptDialog(self.root, "Thêm prompt mới")
        if dialog.result:
            name, content = dialog.result
            if name and content:
                self.prompts[name] = content
                self.prompt_var.set(name)
                self.current_prompt = name
                self.prompt_text.delete("1.0", tk.END)
                self.prompt_text.insert("1.0", content)
                self.save_prompts()
                
    def edit_prompt(self):
        """Sửa prompt hiện tại"""
        name = self.prompt_var.get()
        if name in self.prompts:
            content = self.prompt_text.get("1.0", tk.END).strip()
            dialog = PromptDialog(self.root, "Sửa prompt", name, content)
            if dialog.result:
                new_name, new_content = dialog.result
                if new_name and new_content:
                    if new_name != name:
                        del self.prompts[name]
                    self.prompts[new_name] = new_content
                    self.prompt_var.set(new_name)
                    self.current_prompt = new_name
                    self.prompt_text.delete("1.0", tk.END)
                    self.prompt_text.insert("1.0", new_content)
                    self.save_prompts()
                    
    def delete_prompt(self):
        """Xóa prompt hiện tại"""
        name = self.prompt_var.get()
        if name != "default" and name in self.prompts:
            if messagebox.askyesno("Xác nhận", f"Bạn có chắc muốn xóa prompt '{name}'?"):
                del self.prompts[name]
                self.prompt_var.set("default")
                self.current_prompt = "default"
                self.prompt_text.delete("1.0", tk.END)
                self.prompt_text.insert("1.0", self.prompts["default"])
                self.save_prompts()
                
    def generate_subtitles(self):
        """Tạo phụ đề cho video"""
        if not self.input_folder or not self.output_folder:
            messagebox.showerror("Lỗi", "Vui lòng chọn thư mục đầu vào và đầu ra")
            return
            
        # Tạo cửa sổ tiến trình
        progress_window = ProgressWindow(self.root)
        
        # Tạo processor
        processor = SubtitleProcessor(progress_window.update)
        
        # Chạy xử lý trong thread riêng
        def process():
            try:
                processor.process_videos(
                    self.input_folder,
                    self.output_folder,
                    self.prompts[self.current_prompt],
                    generate=True,
                    translate=False,
                    target_lang="vi",
                    service="novita"
                )
                self.root.after(0, lambda: messagebox.showinfo("Thành công", "Đã tạo và dịch xong phụ đề"))
            except Exception as e:
                self.root.after(0, lambda: messagebox.showerror("Lỗi", str(e)))
            finally:
                self.root.after(0, progress_window.close)
                
        threading.Thread(target=process, daemon=True).start()
        
    def translate_subtitles(self):
        """Dịch phụ đề"""
        if not self.input_folder or not self.output_folder:
            messagebox.showerror("Lỗi", "Vui lòng chọn thư mục đầu vào và đầu ra")
            return
            
        # Tạo cửa sổ tiến trình
        progress_window = ProgressWindow(self.root)
        
        # Tạo processor
        processor = SubtitleProcessor(progress_window.update)
        
        # Chạy xử lý trong thread riêng
        def process():
            try:
                processor.process_videos(
                    self.input_folder,
                    self.output_folder,
                    self.prompts[self.current_prompt],
                    generate=False,
                    translate=True,
                    target_lang="vi",
                    service="novita"
                )
                self.root.after(0, lambda: messagebox.showinfo("Thành công", "Đã dịch xong phụ đề"))
            except Exception as e:
                self.root.after(0, lambda: messagebox.showerror("Lỗi", str(e)))
            finally:
                self.root.after(0, progress_window.close)
                
        threading.Thread(target=process, daemon=True).start() 