import customtkinter as ctk
from tkinter import filedialog, messagebox
import json
import os
from pathlib import Path
from typing import Dict, Any


class ModernSettingsDialog:
    """Modern settings dialog with comprehensive configuration options"""
    
    def __init__(self, parent):
        # Create dialog
        self.dialog = ctk.CTkToplevel(parent)
        self.dialog.title("⚙️ Cài đặt ứng dụng")
        self.dialog.geometry("700x600")
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # Center dialog
        self.dialog.after(100, self._center_dialog)
        
        # Configure grid
        self.dialog.grid_columnconfigure(0, weight=1)
        self.dialog.grid_rowconfigure(0, weight=1)
        
        # Load settings
        self.settings = self.load_settings()
        
        # Variables
        self.init_variables()
        
        # Create widgets
        self.create_widgets()
        
    def _center_dialog(self):
        """Center dialog on screen"""
        self.dialog.update_idletasks()
        width = self.dialog.winfo_width()
        height = self.dialog.winfo_height()
        x = (self.dialog.winfo_screenwidth() // 2) - (width // 2)
        y = (self.dialog.winfo_screenheight() // 2) - (height // 2)
        self.dialog.geometry(f"{width}x{height}+{x}+{y}")
        
    def load_settings(self) -> Dict[str, Any]:
        """Load settings from file"""
        settings_file = Path("config/app_settings.json")
        
        default_settings = {
            "theme": "dark",
            "default_input_folder": "",
            "default_output_folder": "",
            "save_same_folder": True,
            "default_engine": "faster-whisper",
            "default_model": "base",
            "default_device": "cuda",
            "default_compute_type": "float16",
            "default_target_lang": "vi",
            "default_service": "novita",
            "auto_check_updates": True,
            "show_notifications": True,
            "max_concurrent_files": 5,
            "auto_backup_prompts": True,
            "preview_panel_enabled": True,
            "advanced_mode": False
        }
        
        if settings_file.exists():
            try:
                with open(settings_file, 'r', encoding='utf-8') as f:
                    loaded_settings = json.load(f)
                    default_settings.update(loaded_settings)
            except Exception:
                pass
                
        return default_settings
        
    def save_settings(self):
        """Save settings to file"""
        settings_file = Path("config/app_settings.json")
        settings_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Update settings from UI
        self.settings.update({
            "theme": self.theme_var.get(),
            "default_input_folder": self.default_input_var.get(),
            "default_output_folder": self.default_output_var.get(),
            "save_same_folder": self.save_same_folder_var.get(),
            "default_engine": self.default_engine_var.get(),
            "default_model": self.default_model_var.get(),
            "default_device": self.default_device_var.get(),
            "default_compute_type": self.default_compute_type_var.get(),
            "default_target_lang": self.default_target_lang_var.get(),
            "default_service": self.default_service_var.get(),
            "auto_check_updates": self.auto_check_updates_var.get(),
            "show_notifications": self.show_notifications_var.get(),
            "max_concurrent_files": self.max_concurrent_var.get(),
            "auto_backup_prompts": self.auto_backup_prompts_var.get(),
            "preview_panel_enabled": self.preview_panel_var.get(),
            "advanced_mode": self.advanced_mode_var.get()
        })
        
        try:
            with open(settings_file, 'w', encoding='utf-8') as f:
                json.dump(self.settings, f, indent=4, ensure_ascii=False)
            return True
        except Exception as e:
            messagebox.showerror("Lỗi", f"Không thể lưu cài đặt: {str(e)}")
            return False
            
    def init_variables(self):
        """Initialize UI variables from settings"""
        self.theme_var = ctk.StringVar(value=self.settings.get("theme", "dark"))
        self.default_input_var = ctk.StringVar(value=self.settings.get("default_input_folder", ""))
        self.default_output_var = ctk.StringVar(value=self.settings.get("default_output_folder", ""))
        self.save_same_folder_var = ctk.BooleanVar(value=self.settings.get("save_same_folder", True))
        self.default_engine_var = ctk.StringVar(value=self.settings.get("default_engine", "faster-whisper"))
        self.default_model_var = ctk.StringVar(value=self.settings.get("default_model", "base"))
        self.default_device_var = ctk.StringVar(value=self.settings.get("default_device", "cuda"))
        self.default_compute_type_var = ctk.StringVar(value=self.settings.get("default_compute_type", "float16"))
        self.default_target_lang_var = ctk.StringVar(value=self.settings.get("default_target_lang", "vi"))
        self.default_service_var = ctk.StringVar(value=self.settings.get("default_service", "novita"))
        self.auto_check_updates_var = ctk.BooleanVar(value=self.settings.get("auto_check_updates", True))
        self.show_notifications_var = ctk.BooleanVar(value=self.settings.get("show_notifications", True))
        self.max_concurrent_var = ctk.IntVar(value=self.settings.get("max_concurrent_files", 5))
        self.auto_backup_prompts_var = ctk.BooleanVar(value=self.settings.get("auto_backup_prompts", True))
        self.preview_panel_var = ctk.BooleanVar(value=self.settings.get("preview_panel_enabled", True))
        self.advanced_mode_var = ctk.BooleanVar(value=self.settings.get("advanced_mode", False))
        
    def create_widgets(self):
        """Create all settings widgets"""
        # Main frame with tabs
        main_frame = ctk.CTkScrollableFrame(self.dialog, fg_color="transparent")
        main_frame.grid(row=0, column=0, sticky="nsew", padx=20, pady=20)
        main_frame.grid_columnconfigure(0, weight=1)
        
        # Title
        title_label = ctk.CTkLabel(
            main_frame,
            text="⚙️ Cài đặt ứng dụng",
            font=ctk.CTkFont(size=24, weight="bold"),
            text_color="#2196F3"
        )
        title_label.grid(row=0, column=0, pady=(0, 20), sticky="ew")
        
        # Create sections
        row = 1
        row = self.create_appearance_section(main_frame, row)
        row = self.create_defaults_section(main_frame, row)
        row = self.create_processing_section(main_frame, row)
        row = self.create_advanced_section(main_frame, row)
        row = self.create_button_section(main_frame, row)
        
    def create_appearance_section(self, parent, start_row):
        """Create appearance settings section"""
        section_frame = ctk.CTkFrame(parent, fg_color="#2B2B2B")
        section_frame.grid(row=start_row, column=0, sticky="ew", pady=(0, 15))
        section_frame.grid_columnconfigure(1, weight=1)
        
        # Section title
        ctk.CTkLabel(
            section_frame,
            text="🎨 Giao diện",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color="#4CAF50"
        ).grid(row=0, column=0, columnspan=2, pady=(15, 20), sticky="ew")
        
        # Theme selection
        ctk.CTkLabel(section_frame, text="Chủ đề:", font=ctk.CTkFont(size=14)).grid(
            row=1, column=0, sticky="w", padx=15, pady=10
        )
        
        theme_combo = ctk.CTkOptionMenu(
            section_frame,
            variable=self.theme_var,
            values=["dark", "light", "system"],
            height=35
        )
        theme_combo.grid(row=1, column=1, sticky="ew", padx=15, pady=10)
        
        # Preview panel
        ctk.CTkCheckBox(
            section_frame,
            text="🔍 Hiện panel xem trước phụ đề",
            variable=self.preview_panel_var,
            text_color="#E0E0E0"
        ).grid(row=2, column=0, columnspan=2, sticky="w", padx=15, pady=10)
        
        # Show notifications
        ctk.CTkCheckBox(
            section_frame,
            text="🔔 Hiện thông báo thành công",
            variable=self.show_notifications_var,
            text_color="#E0E0E0"
        ).grid(row=3, column=0, columnspan=2, sticky="w", padx=15, pady=(10, 15))
        
        return start_row + 1
        
    def create_defaults_section(self, parent, start_row):
        """Create default settings section"""
        section_frame = ctk.CTkFrame(parent, fg_color="#2B2B2B")
        section_frame.grid(row=start_row, column=0, sticky="ew", pady=(0, 15))
        section_frame.grid_columnconfigure(1, weight=1)
        section_frame.grid_columnconfigure(3, weight=1)
        
        # Section title
        ctk.CTkLabel(
            section_frame,
            text="📂 Mặc định",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color="#FF9800"
        ).grid(row=0, column=0, columnspan=4, pady=(15, 20), sticky="ew")
        
        # Default folders
        ctk.CTkLabel(section_frame, text="Thư mục đầu vào:", font=ctk.CTkFont(size=14)).grid(
            row=1, column=0, sticky="w", padx=15, pady=10
        )
        
        input_entry = ctk.CTkEntry(
            section_frame,
            textvariable=self.default_input_var,
            placeholder_text="Thư mục mặc định cho video...",
            height=35
        )
        input_entry.grid(row=1, column=1, sticky="ew", padx=15, pady=10)
        
        ctk.CTkButton(
            section_frame,
            text="📁",
            command=lambda: self.browse_folder(self.default_input_var),
            width=40,
            height=35
        ).grid(row=1, column=2, padx=(0, 15), pady=10)
        
        # Save same folder
        ctk.CTkCheckBox(
            section_frame,
            text="💾 Mặc định lưu cùng vị trí với video",
            variable=self.save_same_folder_var,
            text_color="#E0E0E0"
        ).grid(row=2, column=0, columnspan=4, sticky="w", padx=15, pady=10)
        
        # Default language and service
        ctk.CTkLabel(section_frame, text="Ngôn ngữ đích:", font=ctk.CTkFont(size=14)).grid(
            row=3, column=0, sticky="w", padx=15, pady=10
        )
        
        lang_combo = ctk.CTkOptionMenu(
            section_frame,
            variable=self.default_target_lang_var,
            values=["vi", "en", "ja", "ko", "zh", "fr", "de", "es", "ru", "th"],
            height=35
        )
        lang_combo.grid(row=3, column=1, sticky="ew", padx=15, pady=10)
        
        ctk.CTkLabel(section_frame, text="Dịch vụ:", font=ctk.CTkFont(size=14)).grid(
            row=3, column=2, sticky="w", padx=15, pady=10
        )
        
        service_combo = ctk.CTkOptionMenu(
            section_frame,
            variable=self.default_service_var,
            values=["novita", "google", "mistral", "groq", "openrouter", "cerebras"],
            height=35
        )
        service_combo.grid(row=3, column=3, sticky="ew", padx=15, pady=(10, 15))
        
        return start_row + 1
        
    def create_processing_section(self, parent, start_row):
        """Create processing settings section"""
        section_frame = ctk.CTkFrame(parent, fg_color="#2B2B2B")
        section_frame.grid(row=start_row, column=0, sticky="ew", pady=(0, 15))
        section_frame.grid_columnconfigure(1, weight=1)
        section_frame.grid_columnconfigure(3, weight=1)
        
        # Section title
        ctk.CTkLabel(
            section_frame,
            text="⚡ Xử lý",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color="#9C27B0"
        ).grid(row=0, column=0, columnspan=4, pady=(15, 20), sticky="ew")
        
        # Engine and model
        ctk.CTkLabel(section_frame, text="Engine:", font=ctk.CTkFont(size=14)).grid(
            row=1, column=0, sticky="w", padx=15, pady=10
        )
        
        engine_combo = ctk.CTkOptionMenu(
            section_frame,
            variable=self.default_engine_var,
            values=["openai-whisper", "faster-whisper"],
            height=35
        )
        engine_combo.grid(row=1, column=1, sticky="ew", padx=15, pady=10)
        
        ctk.CTkLabel(section_frame, text="Model:", font=ctk.CTkFont(size=14)).grid(
            row=1, column=2, sticky="w", padx=15, pady=10
        )
        
        model_combo = ctk.CTkOptionMenu(
            section_frame,
            variable=self.default_model_var,
            values=["tiny", "base", "small", "medium", "large-v3"],
            height=35
        )
        model_combo.grid(row=1, column=3, sticky="ew", padx=15, pady=10)
        
        # Device and compute type
        ctk.CTkLabel(section_frame, text="Device:", font=ctk.CTkFont(size=14)).grid(
            row=2, column=0, sticky="w", padx=15, pady=10
        )
        
        device_combo = ctk.CTkOptionMenu(
            section_frame,
            variable=self.default_device_var,
            values=["cuda", "cpu"],
            height=35
        )
        device_combo.grid(row=2, column=1, sticky="ew", padx=15, pady=10)
        
        ctk.CTkLabel(section_frame, text="Precision:", font=ctk.CTkFont(size=14)).grid(
            row=2, column=2, sticky="w", padx=15, pady=10
        )
        
        compute_combo = ctk.CTkOptionMenu(
            section_frame,
            variable=self.default_compute_type_var,
            values=["float16", "float32", "int8", "int8_float16"],
            height=35
        )
        compute_combo.grid(row=2, column=3, sticky="ew", padx=15, pady=10)
        
        # Concurrent files
        ctk.CTkLabel(section_frame, text="Số file xử lý đồng thời:", font=ctk.CTkFont(size=14)).grid(
            row=3, column=0, sticky="w", padx=15, pady=10
        )
        
        concurrent_slider = ctk.CTkSlider(
            section_frame,
            from_=1,
            to=10,
            number_of_steps=9,
            variable=self.max_concurrent_var,
            height=20
        )
        concurrent_slider.grid(row=3, column=1, sticky="ew", padx=15, pady=10)
        
        self.concurrent_label = ctk.CTkLabel(
            section_frame,
            text=f"{self.max_concurrent_var.get()} files",
            font=ctk.CTkFont(size=12),
            text_color="#BDBDBD"
        )
        self.concurrent_label.grid(row=3, column=2, sticky="w", padx=15, pady=(10, 15))
        
        # Update label when slider changes
        concurrent_slider.configure(command=self.update_concurrent_label)
        
        return start_row + 1
        
    def create_advanced_section(self, parent, start_row):
        """Create advanced settings section"""
        section_frame = ctk.CTkFrame(parent, fg_color="#2B2B2B")
        section_frame.grid(row=start_row, column=0, sticky="ew", pady=(0, 15))
        section_frame.grid_columnconfigure(0, weight=1)
        
        # Section title
        ctk.CTkLabel(
            section_frame,
            text="🔧 Nâng cao",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color="#F44336"
        ).grid(row=0, column=0, pady=(15, 20), sticky="ew")
        
        # Advanced options
        ctk.CTkCheckBox(
            section_frame,
            text="🔄 Tự động kiểm tra cập nhật",
            variable=self.auto_check_updates_var,
            text_color="#E0E0E0"
        ).grid(row=1, column=0, sticky="w", padx=15, pady=5)
        
        ctk.CTkCheckBox(
            section_frame,
            text="💾 Tự động backup prompts",
            variable=self.auto_backup_prompts_var,
            text_color="#E0E0E0"
        ).grid(row=2, column=0, sticky="w", padx=15, pady=5)
        
        ctk.CTkCheckBox(
            section_frame,
            text="🧪 Chế độ nâng cao (hiện thêm tùy chọn)",
            variable=self.advanced_mode_var,
            text_color="#E0E0E0"
        ).grid(row=3, column=0, sticky="w", padx=15, pady=(5, 15))
        
        return start_row + 1
        
    def create_button_section(self, parent, start_row):
        """Create control buttons"""
        button_frame = ctk.CTkFrame(parent, fg_color="transparent")
        button_frame.grid(row=start_row, column=0, pady=20)
        
        # Reset to defaults
        ctk.CTkButton(
            button_frame,
            text="🔄 Khôi phục mặc định",
            command=self.reset_defaults,
            height=40,
            fg_color="#607D8B",
            hover_color="#455A64"
        ).pack(side="left", padx=10)
        
        # Save settings
        ctk.CTkButton(
            button_frame,
            text="💾 Lưu cài đặt",
            command=self.save_and_close,
            height=40,
            fg_color="#4CAF50",
            hover_color="#45A049"
        ).pack(side="left", padx=10)
        
        # Cancel
        ctk.CTkButton(
            button_frame,
            text="❌ Hủy",
            command=self.dialog.destroy,
            height=40,
            fg_color="#F44336",
            hover_color="#D32F2F"
        ).pack(side="left", padx=10)
        
        return start_row + 1
        
    def browse_folder(self, var: ctk.StringVar):
        """Browse for folder"""
        folder = filedialog.askdirectory()
        if folder:
            var.set(folder)
            
    def update_concurrent_label(self, value):
        """Update concurrent files label"""
        self.concurrent_label.configure(text=f"{int(value)} files")
        
    def reset_defaults(self):
        """Reset all settings to defaults"""
        if messagebox.askyesno("Xác nhận", "Bạn có chắc muốn khôi phục tất cả cài đặt về mặc định?"):
            # Reset all variables to defaults
            self.theme_var.set("dark")
            self.default_input_var.set("")
            self.default_output_var.set("")
            self.save_same_folder_var.set(True)
            self.default_engine_var.set("faster-whisper")
            self.default_model_var.set("base")
            self.default_device_var.set("cuda")
            self.default_compute_type_var.set("float16")
            self.default_target_lang_var.set("vi")
            self.default_service_var.set("novita")
            self.auto_check_updates_var.set(True)
            self.show_notifications_var.set(True)
            self.max_concurrent_var.set(5)
            self.auto_backup_prompts_var.set(True)
            self.preview_panel_var.set(True)
            self.advanced_mode_var.set(False)
            
    def save_and_close(self):
        """Save settings and close dialog"""
        if self.save_settings():
            messagebox.showinfo("Thành công", "Đã lưu cài đặt thành công!")
            self.dialog.destroy()