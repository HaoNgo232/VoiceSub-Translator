import customtkinter as ctk
from tkinter import messagebox
import threading
from typing import Dict, Optional, Callable

from src.gui.subtitle_processor import SubtitleProcessor
from src.gui.components.progress_window import ProgressWindow


class ModernTranslationDialog:
    """Modern translation dialog with enhanced UX"""
    
    # Available languages with their names and codes
    LANGUAGES = {
        "🇻🇳 Tiếng Việt": "vi",
        "🇺🇸 English": "en", 
        "🇯🇵 日本語": "ja",
        "🇰🇷 한국어": "ko",
        "🇨🇳 中文": "zh",
        "🇫🇷 Français": "fr",
        "🇩🇪 Deutsch": "de",
        "🇪🇸 Español": "es",
        "🇷🇺 Русский": "ru",
        "🇹🇭 ไทย": "th"
    }
    
    # Available translation services
    SERVICES = {
        "🚀 Novita AI": "novita",
        "🔍 Google Translate": "google", 
        "🧠 Mistral AI": "mistral",
        "⚡ Groq": "groq",
        "🌐 OpenRouter": "openrouter",
        "🧮 Cerebras": "cerebras"
    }
    
    def __init__(self, parent, input_folder: str, output_folder: Optional[str], 
                 save_same_folder: bool, status_callback: Optional[Callable] = None):
        self.input_folder = input_folder
        self.output_folder = output_folder  
        self.save_same_folder = save_same_folder
        self.status_callback = status_callback
        
        # Create dialog
        self.dialog = ctk.CTkToplevel(parent)
        self.dialog.title("🌐 Cấu hình dịch phụ đề")
        self.dialog.geometry("800x600")
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # Center the dialog
        self.dialog.after(100, self._center_dialog)
        
        # Configure grid
        self.dialog.grid_columnconfigure(0, weight=1)
        self.dialog.grid_rowconfigure(0, weight=1)
        
        # Create main frame
        self.main_frame = ctk.CTkScrollableFrame(self.dialog, fg_color="transparent")
        self.main_frame.grid(row=0, column=0, sticky="nsew", padx=20, pady=20)
        self.main_frame.grid_columnconfigure(0, weight=1)
        
        # Variables
        self.target_lang_var = ctk.StringVar(value="🇻🇳 Tiếng Việt")
        self.source_lang_var = ctk.StringVar(value="🔍 Tự động phát hiện")
        self.service_var = ctk.StringVar(value="🚀 Novita AI")
        self.use_context_var = ctk.BooleanVar(value=True)
        self.batch_size_var = ctk.IntVar(value=5)
        
        # Create widgets
        self.create_widgets()
        
    def _center_dialog(self):
        """Center the dialog on screen"""
        self.dialog.update_idletasks()
        width = self.dialog.winfo_width()
        height = self.dialog.winfo_height()
        x = (self.dialog.winfo_screenwidth() // 2) - (width // 2)
        y = (self.dialog.winfo_screenheight() // 2) - (height // 2)
        self.dialog.geometry(f"{width}x{height}+{x}+{y}")
        
    def create_widgets(self):
        """Create all widgets for the dialog"""
        
        # Title
        title_label = ctk.CTkLabel(
            self.main_frame,
            text="🌐 Cấu hình dịch phụ đề",
            font=ctk.CTkFont(size=28, weight="bold"),
            text_color="#2196F3"
        )
        title_label.grid(row=0, column=0, pady=(0, 30), sticky="ew")
        
        # Language selection section
        self.create_language_section()
        
        # Service selection section  
        self.create_service_section()
        
        # Advanced options section
        self.create_advanced_section()
        
        # Preview section
        self.create_preview_section()
        
        # Control buttons
        self.create_control_buttons()
        
    def create_language_section(self):
        """Create language selection section"""
        lang_frame = ctk.CTkFrame(self.main_frame, fg_color="#2B2B2B")
        lang_frame.grid(row=1, column=0, sticky="ew", pady=(0, 20))
        lang_frame.grid_columnconfigure(1, weight=1)
        lang_frame.grid_columnconfigure(3, weight=1)
        
        # Section title
        lang_title = ctk.CTkLabel(
            lang_frame,
            text="🗣️ Cấu hình ngôn ngữ",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color="#4CAF50"
        )
        lang_title.grid(row=0, column=0, columnspan=4, pady=(15, 20), sticky="ew")
        
        # Source language
        ctk.CTkLabel(lang_frame, text="Ngôn ngữ nguồn:", font=ctk.CTkFont(size=14)).grid(
            row=1, column=0, sticky="w", padx=15, pady=10
        )
        
        source_langs = ["🔍 Tự động phát hiện"] + list(self.LANGUAGES.keys())
        source_combo = ctk.CTkOptionMenu(
            lang_frame,
            variable=self.source_lang_var,
            values=source_langs,
            height=35,
            font=ctk.CTkFont(size=12)
        )
        source_combo.grid(row=1, column=1, sticky="ew", padx=15, pady=10)
        
        # Target language  
        ctk.CTkLabel(lang_frame, text="Ngôn ngữ đích:", font=ctk.CTkFont(size=14)).grid(
            row=1, column=2, sticky="w", padx=15, pady=10
        )
        
        target_combo = ctk.CTkOptionMenu(
            lang_frame,
            variable=self.target_lang_var,
            values=list(self.LANGUAGES.keys()),
            height=35,
            font=ctk.CTkFont(size=12)
        )
        target_combo.grid(row=1, column=3, sticky="ew", padx=15, pady=10)
        
    def create_service_section(self):
        """Create service selection section"""
        service_frame = ctk.CTkFrame(self.main_frame, fg_color="#2B2B2B")
        service_frame.grid(row=2, column=0, sticky="ew", pady=(0, 20))
        service_frame.grid_columnconfigure(1, weight=1)
        
        # Section title
        service_title = ctk.CTkLabel(
            service_frame,
            text="🤖 Dịch vụ AI",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color="#FF9800"
        )
        service_title.grid(row=0, column=0, columnspan=2, pady=(15, 20), sticky="ew")
        
        # Service selection
        ctk.CTkLabel(service_frame, text="Chọn dịch vụ:", font=ctk.CTkFont(size=14)).grid(
            row=1, column=0, sticky="w", padx=15, pady=10
        )
        
        service_combo = ctk.CTkOptionMenu(
            service_frame,
            variable=self.service_var,
            values=list(self.SERVICES.keys()),
            height=35,
            font=ctk.CTkFont(size=12),
            command=self.on_service_changed
        )
        service_combo.grid(row=1, column=1, sticky="ew", padx=15, pady=10)
        
        # Service description
        self.service_desc_label = ctk.CTkLabel(
            service_frame,
            text=self.get_service_description("novita"),
            font=ctk.CTkFont(size=11),
            text_color="#BDBDBD",
            wraplength=600,
            justify="left"
        )
        self.service_desc_label.grid(row=2, column=0, columnspan=2, sticky="ew", padx=15, pady=(0, 15))
        
    def create_advanced_section(self):
        """Create advanced options section"""
        advanced_frame = ctk.CTkFrame(self.main_frame, fg_color="#2B2B2B")
        advanced_frame.grid(row=3, column=0, sticky="ew", pady=(0, 20))
        advanced_frame.grid_columnconfigure(1, weight=1)
        
        # Section title
        advanced_title = ctk.CTkLabel(
            advanced_frame,
            text="⚙️ Tùy chọn nâng cao",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color="#9C27B0"
        )
        advanced_title.grid(row=0, column=0, columnspan=2, pady=(15, 20), sticky="ew")
        
        # Context-aware translation
        self.context_cb = ctk.CTkCheckBox(
            advanced_frame,
            text="🧠 Sử dụng dịch thông minh (Context-aware)",
            variable=self.use_context_var,
            text_color="#E0E0E0",
            checkbox_width=20,
            checkbox_height=20
        )
        self.context_cb.grid(row=1, column=0, columnspan=2, sticky="w", padx=15, pady=10)
        
        # Batch size
        ctk.CTkLabel(advanced_frame, text="Số lượng xử lý đồng thời:", font=ctk.CTkFont(size=14)).grid(
            row=2, column=0, sticky="w", padx=15, pady=10
        )
        
        batch_slider = ctk.CTkSlider(
            advanced_frame,
            from_=1,
            to=10,
            number_of_steps=9,
            variable=self.batch_size_var,
            height=20
        )
        batch_slider.grid(row=2, column=1, sticky="ew", padx=15, pady=10)
        
        # Batch size value label
        self.batch_value_label = ctk.CTkLabel(
            advanced_frame,
            text=f"{self.batch_size_var.get()} files",
            font=ctk.CTkFont(size=12),
            text_color="#BDBDBD"
        )
        self.batch_value_label.grid(row=3, column=1, sticky="w", padx=15, pady=(0, 15))
        
        # Update batch size label when slider changes
        batch_slider.configure(command=self.update_batch_label)
        
    def create_preview_section(self):
        """Create preview section"""
        preview_frame = ctk.CTkFrame(self.main_frame, fg_color="#2B2B2B")
        preview_frame.grid(row=4, column=0, sticky="ew", pady=(0, 20))
        
        # Section title
        preview_title = ctk.CTkLabel(
            preview_frame,
            text="👁️ Xem trước cấu hình",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color="#607D8B"
        )
        preview_title.grid(row=0, column=0, pady=(15, 20), sticky="ew")
        
        # Preview text
        self.preview_text = ctk.CTkTextbox(
            preview_frame,
            height=100,
            font=ctk.CTkFont(size=11),
            wrap="word"
        )
        self.preview_text.grid(row=1, column=0, sticky="ew", padx=15, pady=(0, 15))
        
        # Update preview
        self.update_preview()
        
        # Bind variables to update preview
        self.target_lang_var.trace('w', lambda *args: self.update_preview())
        self.source_lang_var.trace('w', lambda *args: self.update_preview())
        self.service_var.trace('w', lambda *args: self.update_preview())
        self.use_context_var.trace('w', lambda *args: self.update_preview())
        
    def create_control_buttons(self):
        """Create control buttons"""
        button_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        button_frame.grid(row=5, column=0, pady=20)
        
        # Start translation button
        start_btn = ctk.CTkButton(
            button_frame,
            text="🚀 Bắt đầu dịch",
            command=self.start_translation,
            height=50,
            width=200,
            fg_color="#4CAF50",
            hover_color="#45A049",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        start_btn.pack(side="left", padx=10)
        
        # Cancel button
        cancel_btn = ctk.CTkButton(
            button_frame,
            text="❌ Hủy",
            command=self.dialog.destroy,
            height=50,
            width=150,
            fg_color="#F44336",
            hover_color="#D32F2F",
            font=ctk.CTkFont(size=16)
        )
        cancel_btn.pack(side="left", padx=10)
        
    def get_service_description(self, service_code: str) -> str:
        """Get description for service"""
        descriptions = {
            "novita": "⚡ Dịch vụ AI tốc độ cao với chất lượng tốt, hỗ trợ nhiều ngôn ngữ",
            "google": "🔍 Google Translate - Độ chính xác cao, miễn phí, hỗ trợ rất nhiều ngôn ngữ",
            "mistral": "🧠 Mistral AI - AI tiên tiến với khả năng hiểu ngữ cảnh tốt",
            "groq": "⚡ Groq - Tốc độ xử lý cực nhanh với chip AI chuyên dụng",
            "openrouter": "🌐 OpenRouter - Truy cập nhiều mô hình AI khác nhau",
            "cerebras": "🧮 Cerebras - Chip AI siêu nhanh cho xử lý ngôn ngữ"
        }
        return descriptions.get(service_code, "Mô tả không có sẵn")
        
    def on_service_changed(self, service_name: str):
        """Handle service selection change"""
        service_code = self.SERVICES.get(service_name, "novita")
        self.service_desc_label.configure(text=self.get_service_description(service_code))
        
    def update_batch_label(self, value):
        """Update batch size label"""
        self.batch_value_label.configure(text=f"{int(value)} files")
        
    def update_preview(self):
        """Update configuration preview"""
        source_lang = self.source_lang_var.get()
        target_lang = self.target_lang_var.get()
        service = self.service_var.get()
        context_aware = "Có" if self.use_context_var.get() else "Không"
        batch_size = self.batch_size_var.get()
        
        preview_text = f"""
📋 CẤU HÌNH DỊCH PHỤ ĐỀ

🗣️ Ngôn ngữ:
   • Từ: {source_lang}
   • Sang: {target_lang}

🤖 Dịch vụ: {service}

⚙️ Tùy chọn:
   • Dịch thông minh: {context_aware}
   • Xử lý đồng thời: {batch_size} files

📁 Thư mục:
   • Đầu vào: {self.input_folder}
   • Đầu ra: {"Cùng với video" if self.save_same_folder else self.output_folder}
        """
        
        self.preview_text.delete("1.0", "end")
        self.preview_text.insert("1.0", preview_text.strip())
        
    def start_translation(self):
        """Start translation process"""
        # Get selected values
        target_lang_code = self.LANGUAGES.get(self.target_lang_var.get(), "vi")
        service_code = self.SERVICES.get(self.service_var.get(), "novita")
        
        # Close dialog
        self.dialog.destroy()
        
        # Update status if callback provided
        if self.status_callback:
            self.status_callback("🔄 Đang dịch phụ đề...", "#FF9800")
            
        # Create progress window - this will be handled by the parent
        # For now, we'll create a simple info dialog
        result_dialog = ctk.CTkToplevel()
        result_dialog.title("🚀 Đang dịch...")
        result_dialog.geometry("400x200")
        result_dialog.grab_set()
        
        # Center dialog
        result_dialog.update_idletasks()
        width = result_dialog.winfo_width()
        height = result_dialog.winfo_height()
        x = (result_dialog.winfo_screenwidth() // 2) - (width // 2)
        y = (result_dialog.winfo_screenheight() // 2) - (height // 2)
        result_dialog.geometry(f"{width}x{height}+{x}+{y}")
        
        main_frame = ctk.CTkFrame(result_dialog)
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        ctk.CTkLabel(
            main_frame,
            text="🚀 Bắt đầu quá trình dịch",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color="#4CAF50"
        ).pack(pady=20)
        
        ctk.CTkLabel(
            main_frame,
            text=f"Dịch sang: {self.target_lang_var.get()}\nDịch vụ: {self.service_var.get()}",
            font=ctk.CTkFont(size=12)
        ).pack(pady=10)
        
        # Start actual translation in background
        def process():
            try:
                progress_window = ProgressWindow(result_dialog)
                processor = SubtitleProcessor(progress_window.update)
                
                processor.process_videos(
                    self.input_folder,
                    self.output_folder,
                    generate=False,
                    translate=True,
                    target_lang=target_lang_code,
                    service=service_code
                )
                
                progress_window.close()
                result_dialog.after(0, lambda: messagebox.showinfo("Thành công", "Đã dịch xong phụ đề!"))
                result_dialog.after(0, result_dialog.destroy)
                
                if self.status_callback:
                    self.status_callback("✅ Đã dịch phụ đề thành công!", "#4CAF50")
                    
            except Exception as e:
                progress_window.close()
                result_dialog.after(0, lambda: messagebox.showerror("Lỗi", str(e)))
                result_dialog.after(0, result_dialog.destroy)
                
                if self.status_callback:
                    self.status_callback("❌ Lỗi khi dịch phụ đề", "#F44336")
                    
        threading.Thread(target=process, daemon=True).start()
        
        # Close button
        ctk.CTkButton(
            main_frame,
            text="Đóng",
            command=result_dialog.destroy,
            fg_color="#F44336",
            hover_color="#D32F2F"
        ).pack(pady=20)