import sys
import os
import json
import threading
from pathlib import Path
from typing import Dict, Optional
import customtkinter as ctk
from tkinter import filedialog, messagebox
import shutil

# Thêm thư mục gốc vào đường dẫn Python
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from src.gui.subtitle_processor import SubtitleProcessor
from src.gui.components.progress_window import ProgressWindow
from src.utils.subtitle_management import backup_original_subtitles, restore_original_subtitles
from src.utils.transcription import ENGINE_OPENAI_WHISPER, ENGINE_FASTER_WHISPER

# Cấu hình CustomTkinter
ctk.set_appearance_mode("dark")  # Chế độ: "dark", "light", "system"
ctk.set_default_color_theme("blue")  # Chủ đề: "blue", "green", "dark-blue"

class ModernSubtitleApp:
    """Ứng dụng xử lý phụ đề với giao diện hiện đại"""
    
    def __init__(self):
        self.root = ctk.CTk()
        self.root.title("Công cụ xử lý phụ đề - Phiên bản hiện đại")
        self.root.geometry("1200x800")
        self.root.minsize(1000, 700)
        
        # Biến lưu trữ
        self.prompts: Dict[str, str] = {}
        self.current_prompt: Optional[str] = None
        self.input_folder: Optional[str] = None
        self.output_folder: Optional[str] = None
        
        # Tải prompts từ file
        self.load_prompts()
        
        # Tạo giao diện
        self.create_widgets()
        
        # Cấu hình grid
        self.root.grid_columnconfigure(0, weight=1)
        self.root.grid_rowconfigure(0, weight=1)
        
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
        # Frame chính với scrollbar
        main_frame = ctk.CTkScrollableFrame(self.root, fg_color="transparent")
        main_frame.grid(row=0, column=0, sticky="nsew", padx=20, pady=20)
        main_frame.grid_columnconfigure(0, weight=1)
        
        # Tiêu đề ứng dụng
        title_label = ctk.CTkLabel(
            main_frame, 
            text="🎬 Công cụ xử lý phụ đề", 
            font=ctk.CTkFont(size=28, weight="bold"),
            text_color="#4CAF50"
        )
        title_label.grid(row=0, column=0, pady=(0, 30), sticky="ew")
        
        # Phần chọn thư mục
        folder_frame = ctk.CTkFrame(main_frame, fg_color="#2B2B2B")
        folder_frame.grid(row=1, column=0, sticky="ew", pady=(0, 20))
        folder_frame.grid_columnconfigure(1, weight=1)
        
        # Tiêu đề section
        folder_title = ctk.CTkLabel(
            folder_frame, 
            text="📁 Quản lý thư mục", 
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color="#2196F3"
        )
        folder_title.grid(row=0, column=0, columnspan=3, pady=(15, 20), sticky="ew")
        
        # Input folder
        ctk.CTkLabel(folder_frame, text="Thư mục đầu vào:", font=ctk.CTkFont(size=14)).grid(
            row=1, column=0, sticky="w", padx=15, pady=10
        )
        self.input_folder_var = ctk.StringVar()
        input_entry = ctk.CTkEntry(
            folder_frame, 
            textvariable=self.input_folder_var, 
            placeholder_text="Chọn thư mục chứa video...",
            height=35
        )
        input_entry.grid(row=1, column=1, sticky="ew", padx=15, pady=10)
        
        input_btn = ctk.CTkButton(
            folder_frame, 
            text="Chọn thư mục", 
            command=self.select_input_folder,
            height=35,
            fg_color="#4CAF50",
            hover_color="#45A049"
        )
        input_btn.grid(row=1, column=2, padx=15, pady=10)
        
        # Checkbox lưu cùng vị trí video
        self.save_same_folder_var = ctk.BooleanVar(value=True)
        self.save_same_folder_cb = ctk.CTkCheckBox(
            folder_frame, 
            text="💾 Lưu phụ đề cùng vị trí với video", 
            variable=self.save_same_folder_var, 
            command=self.toggle_output_folder,
            text_color="#E0E0E0",
            checkbox_width=20,
            checkbox_height=20
        )
        self.save_same_folder_cb.grid(row=2, column=0, columnspan=3, sticky="w", padx=15, pady=10)
        
        # Output folder
        ctk.CTkLabel(folder_frame, text="Thư mục đầu ra:", font=ctk.CTkFont(size=14)).grid(
            row=3, column=0, sticky="w", padx=15, pady=10
        )
        self.output_folder_var = ctk.StringVar()
        self.output_folder_entry = ctk.CTkEntry(
            folder_frame, 
            textvariable=self.output_folder_var, 
            placeholder_text="Chọn thư mục lưu phụ đề...",
            height=35,
            state="disabled"
        )
        self.output_folder_entry.grid(row=3, column=1, sticky="ew", padx=15, pady=10)
        
        self.output_folder_btn = ctk.CTkButton(
            folder_frame, 
            text="Chọn thư mục", 
            command=self.select_output_folder,
            height=35,
            fg_color="#FF9800",
            hover_color="#F57C00",
            state="disabled"
        )
        self.output_folder_btn.grid(row=3, column=2, padx=15, pady=10)
        
        # Phần cấu hình transcription
        transcription_frame = ctk.CTkFrame(main_frame, fg_color="#2B2B2B")
        transcription_frame.grid(row=2, column=0, sticky="ew", pady=(0, 20))
        transcription_frame.grid_columnconfigure(1, weight=1)
        transcription_frame.grid_columnconfigure(3, weight=1)
        
        # Tiêu đề section
        transcription_title = ctk.CTkLabel(
            transcription_frame, 
            text="⚙️ Cấu hình tạo phụ đề", 
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color="#FF9800"
        )
        transcription_title.grid(row=0, column=0, columnspan=4, pady=(15, 20), sticky="ew")
        
        # Engine
        ctk.CTkLabel(transcription_frame, text="Engine:", font=ctk.CTkFont(size=14)).grid(
            row=1, column=0, sticky="w", padx=15, pady=10
        )
        self.engine_var = ctk.StringVar(value=ENGINE_OPENAI_WHISPER)
        engine_combo = ctk.CTkOptionMenu(
            transcription_frame, 
            variable=self.engine_var,
            values=[ENGINE_OPENAI_WHISPER, ENGINE_FASTER_WHISPER],
            height=35,
            command=self.on_engine_selected
        )
        engine_combo.grid(row=1, column=1, sticky="ew", padx=15, pady=10)
        
        # Model cho OpenAI Whisper
        ctk.CTkLabel(transcription_frame, text="OpenAI Model:", font=ctk.CTkFont(size=14)).grid(
            row=1, column=2, sticky="w", padx=15, pady=10
        )
        self.whisper_model_var = ctk.StringVar(value="base.en")
        whisper_model_combo = ctk.CTkOptionMenu(
            transcription_frame, 
            variable=self.whisper_model_var,
            values=["tiny.en", "base.en", "small.en"],
            height=35
        )
        whisper_model_combo.grid(row=1, column=3, sticky="ew", padx=15, pady=10)
        
        # Model cho Faster Whisper
        ctk.CTkLabel(transcription_frame, text="Faster-Whisper Model:", font=ctk.CTkFont(size=14)).grid(
            row=2, column=0, sticky="w", padx=15, pady=10
        )
        self.faster_model_var = ctk.StringVar(value="base")
        faster_model_combo = ctk.CTkOptionMenu(
            transcription_frame, 
            variable=self.faster_model_var,
            values=["tiny", "base", "small", "medium", "large-v3", "distil-large-v3"],
            height=35
        )
        faster_model_combo.grid(row=2, column=1, sticky="ew", padx=15, pady=10)
        
        # Compute Type
        ctk.CTkLabel(transcription_frame, text="Precision:", font=ctk.CTkFont(size=14)).grid(
            row=2, column=2, sticky="w", padx=15, pady=10
        )
        self.compute_type_var = ctk.StringVar(value="float16")
        compute_type_combo = ctk.CTkOptionMenu(
            transcription_frame, 
            variable=self.compute_type_var,
            values=["float16", "float32", "int8", "int8_float16"],
            height=35
        )
        compute_type_combo.grid(row=2, column=3, sticky="ew", padx=15, pady=10)
        
        # Device
        ctk.CTkLabel(transcription_frame, text="Device:", font=ctk.CTkFont(size=14)).grid(
            row=3, column=0, sticky="w", padx=15, pady=10
        )
        self.device_var = ctk.StringVar(value="cuda")
        device_combo = ctk.CTkOptionMenu(
            transcription_frame, 
            variable=self.device_var,
            values=["cuda", "cpu"],
            height=35
        )
        device_combo.grid(row=3, column=1, sticky="ew", padx=15, pady=10)
        
        # Phần quản lý prompts
        prompt_frame = ctk.CTkFrame(main_frame, fg_color="#2B2B2B")
        prompt_frame.grid(row=3, column=0, sticky="ew", pady=(0, 20))
        prompt_frame.grid_columnconfigure(1, weight=1)
        
        # Tiêu đề section
        prompt_title = ctk.CTkLabel(
            prompt_frame, 
            text="✍️ Quản lý Prompts", 
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color="#9C27B0"
        )
        prompt_title.grid(row=0, column=0, columnspan=5, pady=(15, 20), sticky="ew")
        
        # Chọn prompt
        ctk.CTkLabel(prompt_frame, text="Chọn prompt:", font=ctk.CTkFont(size=14)).grid(
            row=1, column=0, sticky="w", padx=15, pady=10
        )
        self.prompt_var = ctk.StringVar(value=self.current_prompt)
        prompt_combo = ctk.CTkOptionMenu(
            prompt_frame, 
            variable=self.prompt_var,
            values=list(self.prompts.keys()),
            height=35,
            command=self.on_prompt_selected
        )
        prompt_combo.grid(row=1, column=1, sticky="ew", padx=15, pady=10)
        
        # Nút thêm/sửa/xóa prompt
        ctk.CTkButton(
            prompt_frame, 
            text="➕ Thêm mới", 
            command=self.add_prompt,
            height=35,
            fg_color="#4CAF50",
            hover_color="#45A049"
        ).grid(row=1, column=2, padx=5, pady=10)
        
        ctk.CTkButton(
            prompt_frame, 
            text="✏️ Sửa", 
            command=self.edit_prompt,
            height=35,
            fg_color="#2196F3",
            hover_color="#1976D2"
        ).grid(row=1, column=3, padx=5, pady=10)
        
        ctk.CTkButton(
            prompt_frame, 
            text="🗑️ Xóa", 
            command=self.delete_prompt,
            height=35,
            fg_color="#F44336",
            hover_color="#D32F2F"
        ).grid(row=1, column=4, padx=5, pady=10)
        
        # Hiển thị nội dung prompt
        ctk.CTkLabel(prompt_frame, text="Nội dung prompt:", font=ctk.CTkFont(size=14)).grid(
            row=2, column=0, sticky="w", padx=15, pady=(20, 10)
        )
        self.prompt_text = ctk.CTkTextbox(
            prompt_frame, 
            height=120, 
            width=70,
            font=ctk.CTkFont(size=12)
        )
        self.prompt_text.grid(row=3, column=0, columnspan=5, sticky="ew", padx=15, pady=(0, 15))
        self.prompt_text.insert("1.0", self.prompts[self.current_prompt])
        
        # Phần nút điều khiển chính
        control_frame = ctk.CTkFrame(main_frame, fg_color="#2B2B2B")
        control_frame.grid(row=4, column=0, sticky="ew", pady=(0, 20))
        control_frame.grid_columnconfigure(0, weight=1)
        
        # Tiêu đề section
        control_title = ctk.CTkLabel(
            control_frame, 
            text="🎯 Thao tác chính", 
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color="#FF5722"
        )
        control_title.grid(row=0, column=0, columnspan=5, pady=(15, 20), sticky="ew")
        
        # Frame chứa các nút
        button_frame = ctk.CTkFrame(control_frame, fg_color="transparent")
        button_frame.grid(row=1, column=0, pady=(0, 15))
        
        # Các nút chính
        ctk.CTkButton(
            button_frame, 
            text="🎬 Tạo phụ đề", 
            command=self.generate_subtitles,
            height=45,
            width=180,
            fg_color="#4CAF50",
            hover_color="#45A049",
            font=ctk.CTkFont(size=16, weight="bold")
        ).pack(side="left", padx=10)
        
        ctk.CTkButton(
            button_frame, 
            text="🌐 Dịch phụ đề", 
            command=self.translate_subtitles,
            height=45,
            width=180,
            fg_color="#2196F3",
            hover_color="#1976D2",
            font=ctk.CTkFont(size=16, weight="bold")
        ).pack(side="left", padx=10)
        
        ctk.CTkButton(
            button_frame, 
            text="📋 Sao chép phụ đề", 
            command=self.clone_subtitles,
            height=45,
            width=180,
            fg_color="#FF9800",
            hover_color="#F57C00",
            font=ctk.CTkFont(size=16, weight="bold")
        ).pack(side="left", padx=10)
        
        # Frame chứa các nút phụ
        button_frame2 = ctk.CTkFrame(control_frame, fg_color="transparent")
        button_frame2.grid(row=2, column=0, pady=(0, 15))
        
        ctk.CTkButton(
            button_frame2, 
            text="💾 Quản lý phụ đề gốc", 
            command=self.manage_original_subtitles,
            height=40,
            width=180,
            fg_color="#9C27B0",
            hover_color="#7B1FA2",
            font=ctk.CTkFont(size=14)
        ).pack(side="left", padx=10)
        
        ctk.CTkButton(
            button_frame2, 
            text="🔄 Chuyển đổi phụ đề", 
            command=self.convert_subtitles,
            height=40,
            width=180,
            fg_color="#607D8B",
            hover_color="#455A64",
            font=ctk.CTkFont(size=14)
        ).pack(side="left", padx=10)
        
        # Status bar
        self.status_label = ctk.CTkLabel(
            main_frame, 
            text="✅ Sẵn sàng sử dụng", 
            font=ctk.CTkFont(size=12),
            text_color="#4CAF50"
        )
        self.status_label.grid(row=5, column=0, pady=(20, 0), sticky="ew")
        
    def on_engine_selected(self, value):
        """Xử lý khi chọn engine"""
        if value == ENGINE_FASTER_WHISPER:
            self.compute_type_var.set("float32")
            
    def select_input_folder(self):
        """Chọn thư mục đầu vào"""
        folder = filedialog.askdirectory()
        if folder:
            self.input_folder = folder
            self.input_folder_var.set(folder)
            self.status_label.configure(text=f"📁 Đã chọn thư mục đầu vào: {os.path.basename(folder)}")
            
    def select_output_folder(self):
        """Chọn thư mục đầu ra"""
        folder = filedialog.askdirectory()
        if folder:
            self.output_folder = folder
            self.output_folder_var.set(folder)
            self.status_label.configure(text=f"📁 Đã chọn thư mục đầu ra: {os.path.basename(folder)}")
            
    def on_prompt_selected(self, value):
        """Xử lý khi chọn prompt từ combobox"""
        if value in self.prompts:
            self.current_prompt = value
            self.prompt_text.delete("1.0", "end")
            self.prompt_text.insert("1.0", self.prompts[value])
            
    def add_prompt(self):
        """Thêm prompt mới"""
        # Tạo dialog đơn giản
        dialog = ctk.CTkToplevel(self.root)
        dialog.title("Thêm prompt mới")
        dialog.geometry("500x400")
        dialog.transient(self.root)
        dialog.grab_set()
        
        # Widgets
        ctk.CTkLabel(dialog, text="Tên prompt:", font=ctk.CTkFont(size=14)).pack(pady=10)
        name_entry = ctk.CTkEntry(dialog, width=400, height=35)
        name_entry.pack(pady=5)
        
        ctk.CTkLabel(dialog, text="Nội dung prompt:", font=ctk.CTkFont(size=14)).pack(pady=10)
        content_text = ctk.CTkTextbox(dialog, width=400, height=200)
        content_text.pack(pady=5)
        
        def save_prompt():
            name = name_entry.get().strip()
            content = content_text.get("1.0", "end").strip()
            if name and content:
                self.prompts[name] = content
                self.prompt_var.set(name)
                self.current_prompt = name
                self.prompt_text.delete("1.0", "end")
                self.prompt_text.insert("1.0", content)
                self.save_prompts()
                dialog.destroy()
                self.status_label.configure(text=f"✅ Đã thêm prompt: {name}")
            else:
                messagebox.showerror("Lỗi", "Vui lòng nhập đầy đủ thông tin")
                
        ctk.CTkButton(
            dialog, 
            text="Lưu", 
            command=save_prompt,
            fg_color="#4CAF50",
            hover_color="#45A049"
        ).pack(pady=20)
                
    def edit_prompt(self):
        """Sửa prompt hiện tại"""
        name = self.prompt_var.get()
        if name in self.prompts:
            content = self.prompt_text.get("1.0", "end").strip()
            
            # Tạo dialog tương tự add_prompt
            dialog = ctk.CTkToplevel(self.root)
            dialog.title("Sửa prompt")
            dialog.geometry("500x400")
            dialog.transient(self.root)
            dialog.grab_set()
            
            # Widgets
            ctk.CTkLabel(dialog, text="Tên prompt:", font=ctk.CTkFont(size=14)).pack(pady=10)
            name_entry = ctk.CTkEntry(dialog, width=400, height=35)
            name_entry.insert(0, name)
            name_entry.pack(pady=5)
            
            ctk.CTkLabel(dialog, text="Nội dung prompt:", font=ctk.CTkFont(size=14)).pack(pady=10)
            content_text = ctk.CTkTextbox(dialog, width=400, height=200)
            content_text.insert("1.0", content)
            content_text.pack(pady=5)
            
            def save_changes():
                new_name = name_entry.get().strip()
                new_content = content_text.get("1.0", "end").strip()
                if new_name and new_content:
                    if new_name != name:
                        del self.prompts[name]
                    self.prompts[new_name] = new_content
                    self.prompt_var.set(new_name)
                    self.current_prompt = new_name
                    self.prompt_text.delete("1.0", "end")
                    self.prompt_text.insert("1.0", new_content)
                    self.save_prompts()
                    dialog.destroy()
                    self.status_label.configure(text=f"✅ Đã cập nhật prompt: {new_name}")
                else:
                    messagebox.showerror("Lỗi", "Vui lòng nhập đầy đủ thông tin")
                    
            ctk.CTkButton(
                dialog, 
                text="Lưu thay đổi", 
                command=save_changes,
                fg_color="#4CAF50",
                hover_color="#45A049"
            ).pack(pady=20)
                    
    def delete_prompt(self):
        """Xóa prompt hiện tại"""
        name = self.prompt_var.get()
        if name != "default" and name in self.prompts:
            if messagebox.askyesno("Xác nhận", f"Bạn có chắc muốn xóa prompt '{name}'?"):
                del self.prompts[name]
                self.prompt_var.set("default")
                self.current_prompt = "default"
                self.prompt_text.delete("1.0", "end")
                self.prompt_text.insert("1.0", self.prompts["default"])
                self.save_prompts()
                self.status_label.configure(text=f"🗑️ Đã xóa prompt: {name}")
                
    def toggle_output_folder(self):
        """Bật/tắt trường chọn output folder theo checkbox"""
        if self.save_same_folder_var.get():
            self.output_folder_entry.configure(state="disabled")
            self.output_folder_btn.configure(state="disabled")
        else:
            self.output_folder_entry.configure(state="normal")
            self.output_folder_btn.configure(state="normal")

    def generate_subtitles(self):
        """Tạo phụ đề cho video"""
        if not self.input_folder_var.get():
            messagebox.showerror("Lỗi", "Vui lòng chọn thư mục đầu vào")
            return
        if not self.save_same_folder_var.get() and not self.output_folder_var.get():
            messagebox.showerror("Lỗi", "Vui lòng chọn thư mục đầu ra hoặc chọn lưu cùng vị trí với video")
            return
            
        # Xác định model dựa vào engine
        engine = self.engine_var.get()
        model_name = self.whisper_model_var.get() if engine == ENGINE_OPENAI_WHISPER else self.faster_model_var.get()
            
        # Tạo cửa sổ tiến trình
        progress_window = ProgressWindow(self.root)
        # Tạo processor
        processor = SubtitleProcessor(progress_window.update)
        
        self.status_label.configure(text="🔄 Đang tạo phụ đề...", text_color="#FF9800")
        
        # Chạy xử lý trong thread riêng
        def process():
            try:
                output_folder = None if self.save_same_folder_var.get() else self.output_folder_var.get()
                processor.process_videos(
                    self.input_folder_var.get(),
                    output_folder,
                    generate=True,
                    translate=False,
                    engine=engine,
                    model_name=model_name,
                    device=self.device_var.get(),
                    compute_type=self.compute_type_var.get()
                )
                progress_window.close()
                self.root.after(0, lambda: messagebox.showinfo("Thành công", "Đã tạo phụ đề cho tất cả video!"))
                self.root.after(0, lambda: self.status_label.configure(text="✅ Đã tạo phụ đề thành công!", text_color="#4CAF50"))
            except Exception as e:
                progress_window.close()
                self.root.after(0, lambda: messagebox.showerror("Lỗi", str(e)))
                self.root.after(0, lambda: self.status_label.configure(text="❌ Lỗi khi tạo phụ đề", text_color="#F44336"))
        threading.Thread(target=process, daemon=True).start()
        
    def translate_subtitles(self):
        """Dịch phụ đề"""
        if not self.input_folder_var.get():
            messagebox.showerror("Lỗi", "Vui lòng chọn thư mục đầu vào")
            return
        if not self.save_same_folder_var.get() and not self.output_folder_var.get():
            messagebox.showerror("Lỗi", "Vui lòng chọn thư mục đầu ra hoặc chọn lưu cùng vị trí với video")
            return

        input_folder = self.input_folder_var.get()
        output_folder = None if self.save_same_folder_var.get() else self.output_folder_var.get()

        progress_window = ProgressWindow(self.root)
        processor = SubtitleProcessor(progress_window.update)
        
        self.status_label.configure(text="🔄 Đang dịch phụ đề...", text_color="#FF9800")

        def process():
            try:
                processor.process_videos(
                    input_folder,
                    output_folder,
                    generate=False,
                    translate=True,
                    target_lang="vi",
                    service="novita"
                )
                self.root.after(0, lambda: messagebox.showinfo("Thành công", "Đã dịch xong phụ đề"))
                self.root.after(0, lambda: self.status_label.configure(text="✅ Đã dịch phụ đề thành công!", text_color="#4CAF50"))
            except Exception as e:
                self.root.after(0, lambda: messagebox.showerror("Lỗi", str(e)))
                self.root.after(0, lambda: self.status_label.configure(text="❌ Lỗi khi dịch phụ đề", text_color="#F44336"))
            finally:
                self.root.after(0, progress_window.close)

        threading.Thread(target=process, daemon=True).start()

    def clone_subtitles(self):
        """Sao chép toàn bộ file .srt từ input sang output, giữ nguyên cấu trúc thư mục"""
        if not self.input_folder_var.get():
            messagebox.showerror("Lỗi", "Vui lòng chọn thư mục đầu vào")
            return
        if not self.output_folder_var.get():
            messagebox.showerror("Lỗi", "Vui lòng chọn thư mục đầu ra")
            return

        input_folder = self.input_folder_var.get()
        output_folder = self.output_folder_var.get()
        
        self.status_label.configure(text="🔄 Đang sao chép phụ đề...", text_color="#FF9800")
        
        def process():
            try:
                count = 0
                for root, _, files in os.walk(input_folder):
                    for file in files:
                        if file.lower().endswith(".srt"):
                            rel_path = os.path.relpath(os.path.join(root, file), input_folder)
                            dest_path = os.path.join(output_folder, rel_path)
                            os.makedirs(os.path.dirname(dest_path), exist_ok=True)
                            shutil.copy2(os.path.join(root, file), dest_path)
                            count += 1
                
                self.root.after(0, lambda: messagebox.showinfo("Thành công", f"Đã sao chép {count} file phụ đề .srt sang thư mục output!"))
                self.root.after(0, lambda: self.status_label.configure(text=f"✅ Đã sao chép {count} file phụ đề", text_color="#4CAF50"))
            except Exception as e:
                self.root.after(0, lambda: messagebox.showerror("Lỗi", str(e)))
                self.root.after(0, lambda: self.status_label.configure(text="❌ Lỗi khi sao chép phụ đề", text_color="#F44336"))
                
        threading.Thread(target=process, daemon=True).start()
        
    def manage_original_subtitles(self):
        """Mở cửa sổ quản lý phụ đề gốc"""
        if not self.input_folder_var.get():
            messagebox.showerror("Lỗi", "Vui lòng chọn thư mục đầu vào")
            return
            
        # Tạo cửa sổ dialog hiện đại
        dialog = ctk.CTkToplevel(self.root)
        dialog.title("Quản lý phụ đề gốc")
        dialog.geometry("600x400")
        dialog.transient(self.root)
        dialog.grab_set()
        
        # Tạo các widget
        main_frame = ctk.CTkFrame(dialog)
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Tiêu đề
        ctk.CTkLabel(
            main_frame, 
            text="💾 Quản lý phụ đề gốc", 
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color="#9C27B0"
        ).pack(pady=(0, 20))
        
        # Tự động tạo đường dẫn backup mặc định từ thư mục đầu vào
        default_backup = os.path.join(self.input_folder_var.get(), "backup_subtitles")
        
        # Thư mục backup
        backup_frame = ctk.CTkFrame(main_frame)
        backup_frame.pack(fill="x", pady=10)
        
        ctk.CTkLabel(backup_frame, text="Thư mục backup:", font=ctk.CTkFont(size=14)).pack(anchor="w", padx=15, pady=5)
        
        backup_folder_var = ctk.StringVar(value=default_backup)
        backup_entry = ctk.CTkEntry(backup_frame, textvariable=backup_folder_var, width=400, height=35)
        backup_entry.pack(side="left", padx=15, pady=10)
        
        def select_backup_folder():
            folder = filedialog.askdirectory()
            if folder:
                backup_folder_var.set(folder)
                
        ctk.CTkButton(
            backup_frame, 
            text="Chọn", 
            command=select_backup_folder,
            height=35,
            fg_color="#4CAF50",
            hover_color="#45A049"
        ).pack(side="right", padx=15, pady=10)
        
        # Ngôn ngữ đích
        lang_frame = ctk.CTkFrame(main_frame)
        lang_frame.pack(fill="x", pady=10)
        
        ctk.CTkLabel(lang_frame, text="Ngôn ngữ đích:", font=ctk.CTkFont(size=14)).pack(anchor="w", padx=15, pady=5)
        
        target_lang_var = ctk.StringVar(value="vi")
        lang_entry = ctk.CTkEntry(lang_frame, textvariable=target_lang_var, width=100, height=35)
        lang_entry.pack(side="left", padx=15, pady=10)
        
        # Mô tả
        desc_frame = ctk.CTkFrame(main_frame)
        desc_frame.pack(fill="x", pady=10)
        
        description = """
Chức năng này sẽ xóa các phụ đề gốc của video đã có phụ đề dịch và sao lưu chúng vào thư mục backup.
Điều này giúp giảm sự thừa thãi khi bạn chỉ cần sử dụng phụ đề đã dịch.

Bạn có thể khôi phục phụ đề gốc từ thư mục backup bất kỳ lúc nào.
        """
        
        desc_label = ctk.CTkLabel(
            desc_frame, 
            text=description, 
            justify="left", 
            wraplength=550,
            font=ctk.CTkFont(size=12)
        )
        desc_label.pack(padx=15, pady=15)
        
        # Frame chứa các nút
        button_frame = ctk.CTkFrame(main_frame)
        button_frame.pack(pady=20)
        
        def backup_subtitles():
            input_folder = self.input_folder_var.get()
            backup_folder = backup_folder_var.get()
            target_lang = target_lang_var.get()
            
            progress_window = ProgressWindow(dialog)
            
            def process():
                try:
                    stats = backup_original_subtitles(input_folder, backup_folder, target_lang)
                    
                    msg = f"""Kết quả xử lý:
- Tổng số phụ đề gốc: {stats['total']}
- Số phụ đề đã sao lưu và xóa: {stats['backed_up']}
- Số phụ đề bỏ qua (không có bản dịch): {stats['skipped']}
- Số video không có phụ đề: {stats['no_subtitle']}
                    """
                    
                    progress_window.close()
                    dialog.after(0, lambda: messagebox.showinfo("Thành công", msg))
                except Exception as e:
                    progress_window.close()
                    dialog.after(0, lambda: messagebox.showerror("Lỗi", str(e)))
                    
            threading.Thread(target=process, daemon=True).start()
            
        def restore_subtitles():
            input_folder = self.input_folder_var.get()
            backup_folder = backup_folder_var.get()
            
            if not os.path.exists(backup_folder):
                messagebox.showerror("Lỗi", f"Thư mục backup '{backup_folder}' không tồn tại")
                return
                
            progress_window = ProgressWindow(dialog)
            
            def process():
                try:
                    stats = restore_original_subtitles(input_folder, backup_folder)
                    
                    msg = f"""Kết quả khôi phục:
- Số phụ đề đã khôi phục: {stats['restored']}
- Số khôi phục thất bại: {stats['failed']}
                    """
                    
                    progress_window.close()
                    dialog.after(0, lambda: messagebox.showinfo("Thành công", msg))
                except Exception as e:
                    progress_window.close()
                    dialog.after(0, lambda: messagebox.showerror("Lỗi", str(e)))
                    
            threading.Thread(target=process, daemon=True).start()
            
        ctk.CTkButton(
            button_frame, 
            text="💾 Sao lưu và xóa phụ đề gốc", 
            command=backup_subtitles,
            height=40,
            fg_color="#9C27B0",
            hover_color="#7B1FA2"
        ).pack(side="left", padx=10)
        
        ctk.CTkButton(
            button_frame, 
            text="🔄 Khôi phục phụ đề gốc", 
            command=restore_subtitles,
            height=40,
            fg_color="#607D8B",
            hover_color="#455A64"
        ).pack(side="left", padx=10)
        
        ctk.CTkButton(
            button_frame, 
            text="❌ Đóng", 
            command=dialog.destroy,
            height=40,
            fg_color="#F44336",
            hover_color="#D32F2F"
        ).pack(side="left", padx=10)
        
    def convert_subtitles(self):
        """Mở cửa sổ chuyển đổi định dạng phụ đề"""
        from src.gui.components.modern_convert_dialog import ModernConvertDialog
        ModernConvertDialog(self.root)
        
    def run(self):
        """Chạy ứng dụng"""
        self.root.mainloop()

def main():
    """Chạy ứng dụng chính"""
    try:
        app = ModernSubtitleApp()
        app.run()
    except Exception as e:
        messagebox.showerror("Lỗi khởi động", f"Không thể khởi động ứng dụng: {str(e)}")

if __name__ == "__main__":
    main()