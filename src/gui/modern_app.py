import sys
import os
import json
import threading
from pathlib import Path
from typing import Dict, Optional
import shutil

# Thêm thư mục gốc vào đường dẫn Python
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

def check_display_available():
    """Kiểm tra xem có display server nào khả dụng không"""
    try:
        # Kiểm tra biến môi trường DISPLAY
        if 'DISPLAY' not in os.environ:
            return False
        
        # Thử import và tạo một tkinter widget đơn giản
        import tkinter as tk
        test_root = tk.Tk()
        test_root.withdraw()  # Ẩn cửa sổ
        test_root.destroy()   # Xóa cửa sổ
        return True
    except Exception:
        return False

def setup_virtual_display():
    """Hướng dẫn thiết lập virtual display"""
    print("\n" + "="*60)
    print("🖥️  ỨNG DỤNG GUI - CẦN THIẾT LẬP DISPLAY")
    print("="*60)
    print("\nỨng dụng này cần display server để chạy giao diện đồ họa.")
    print("\n📋 HƯỚNG DẪN THIẾT LẬP:")
    print("\n1️⃣  Cài đặt Xvfb (Virtual Display):")
    print("   sudo apt-get update")
    print("   sudo apt-get install -y xvfb")
    print("\n2️⃣  Chạy ứng dụng với virtual display:")
    print("   xvfb-run -a python run.py")
    print("\n3️⃣  Hoặc thiết lập DISPLAY thủ công:")
    print("   export DISPLAY=:99")
    print("   Xvfb :99 -screen 0 1024x768x24 &")
    print("   python run.py")
    print("\n4️⃣  Để xem giao diện từ xa (nếu cần):")
    print("   - Cài đặt VNC server")
    print("   - Hoặc sử dụng X11 forwarding qua SSH")
    print("\n💡 LƯU Ý:")
    print("   - Ứng dụng này được thiết kế để chạy trên desktop")
    print("   - Trong môi trường server, bạn có thể cần CLI alternative")
    print("\n" + "="*60 + "\n")

# Kiểm tra display availability trước khi import GUI
if not check_display_available():
    # Nếu không có display, import minimal components để tránh lỗi
    print("⚠️  Không phát hiện display server")
else:
    try:
        import customtkinter as ctk
        from tkinter import filedialog, messagebox
        from src.gui.subtitle_processor import SubtitleProcessor
        from src.gui.components.progress_window import ProgressWindow
        from src.gui.components.modern_error_handler import ModernErrorHandler, show_success_notification, show_warning_dialog
        from src.utils.subtitle_management import backup_original_subtitles, restore_original_subtitles
        from src.utils.transcription import ENGINE_OPENAI_WHISPER, ENGINE_FASTER_WHISPER

        # Cấu hình CustomTkinter
        ctk.set_appearance_mode("dark")  # Chế độ: "dark", "light", "system"
        ctk.set_default_color_theme("blue")  # Chủ đề: "blue", "green", "dark-blue"
    except Exception as e:
        print(f"⚠️  Lỗi import GUI components: {e}")
        # Fallback - treat as no display available
        check_display_available = lambda: False

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
        
        # Setup keyboard shortcuts
        self.setup_keyboard_shortcuts()
        
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
        # Configure main window grid for two-column layout
        self.root.grid_columnconfigure(0, weight=3)  # Main content
        self.root.grid_columnconfigure(1, weight=1)  # Sidebar
        self.root.grid_rowconfigure(0, weight=1)
        
        # Main content frame with scrollbar
        main_frame = ctk.CTkScrollableFrame(self.root, fg_color="transparent")
        main_frame.grid(row=0, column=0, sticky="nsew", padx=(20, 10), pady=20)
        main_frame.grid_columnconfigure(0, weight=1)
        
        # Tiêu đề ứng dụng
        title_label = ctk.CTkLabel(
            main_frame, 
            text="🎬 Công cụ xử lý phụ đề", 
            font=ctk.CTkFont(size=28, weight="bold"),
            text_color="#4CAF50"
        )
        title_label.grid(row=0, column=0, pady=(0, 30), sticky="ew")
        
        # Phần chọn thư mục với drag-and-drop
        from src.gui.components.modern_file_selection import ModernFileSelectionPanel
        self.file_selection = ModernFileSelectionPanel(main_frame)
        self.file_selection.grid(row=1, column=0, sticky="ew", pady=(0, 20))
        
        # Link variables for backward compatibility
        self.input_folder_var = self.file_selection.input_folder_var
        self.output_folder_var = self.file_selection.output_folder_var
        self.save_same_folder_var = self.file_selection.save_same_folder_var
        
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
        generate_btn = ctk.CTkButton(
            button_frame, 
            text="🎬 Tạo phụ đề", 
            command=self.generate_subtitles,
            height=45,
            width=180,
            fg_color="#4CAF50",
            hover_color="#45A049",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        generate_btn.pack(side="left", padx=10)
        
        translate_btn = ctk.CTkButton(
            button_frame, 
            text="🌐 Dịch phụ đề", 
            command=self.translate_subtitles,
            height=45,
            width=180,
            fg_color="#2196F3",
            hover_color="#1976D2",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        translate_btn.pack(side="left", padx=10)
        
        clone_btn = ctk.CTkButton(
            button_frame, 
            text="📋 Sao chép phụ đề", 
            command=self.clone_subtitles,
            height=45,
            width=180,
            fg_color="#FF9800",
            hover_color="#F57C00",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        clone_btn.pack(side="left", padx=10)
        
        # Frame chứa các nút phụ
        button_frame2 = ctk.CTkFrame(control_frame, fg_color="transparent")
        button_frame2.grid(row=2, column=0, pady=(0, 15))
        
        manage_btn = ctk.CTkButton(
            button_frame2, 
            text="💾 Quản lý phụ đề gốc", 
            command=self.manage_original_subtitles,
            height=40,
            width=180,
            fg_color="#9C27B0",
            hover_color="#7B1FA2",
            font=ctk.CTkFont(size=14)
        )
        manage_btn.pack(side="left", padx=10)
        
        convert_btn = ctk.CTkButton(
            button_frame2, 
            text="🔄 Chuyển đổi phụ đề", 
            command=self.convert_subtitles,
            height=40,
            width=180,
            fg_color="#607D8B",
            hover_color="#455A64",
            font=ctk.CTkFont(size=14)
        )
        convert_btn.pack(side="left", padx=10)
        
        settings_btn = ctk.CTkButton(
            button_frame2, 
            text="⚙️ Cài đặt", 
            command=self.open_settings,
            height=40,
            width=180,
            fg_color="#795548",
            hover_color="#5D4037",
            font=ctk.CTkFont(size=14)
        )
        settings_btn.pack(side="left", padx=10)
        
        # Add tooltips after creating sidebar
        self.root.after(100, lambda: self.add_tooltips(generate_btn, translate_btn, clone_btn, manage_btn, convert_btn, settings_btn))
        
        # Status bar
        self.status_label = ctk.CTkLabel(
            main_frame, 
            text="✅ Sẵn sàng sử dụng", 
            font=ctk.CTkFont(size=12),
            text_color="#4CAF50"
        )
        self.status_label.grid(row=6, column=0, pady=(20, 0), sticky="ew")
        
        # Add subtitle preview panel on the right
        self.add_sidebar_preview()
        
    def on_engine_selected(self, value):
        """Xử lý khi chọn engine"""
        if value == ENGINE_FASTER_WHISPER:
            self.compute_type_var.set("float32")
            
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

    def generate_subtitles(self):
        """Tạo phụ đề cho video với error handling hiện đại"""
        input_folder = self.input_folder_var.get()
        save_same_folder = self.save_same_folder_var.get()
        output_folder = self.output_folder_var.get()
        
        # Validation with modern error handling
        if not input_folder:
            show_warning_dialog(
                self.root,
                "Thiếu thông tin",
                "Vui lòng chọn thư mục chứa video trước khi tạo phụ đề.",
                ["Nhấn vào khu vực 'Kéo thả thư mục vào đây'", "Hoặc nhấn nút 'Chọn thư mục'"]
            )
            return
            
        if not save_same_folder and not output_folder:
            show_warning_dialog(
                self.root,
                "Thiếu thư mục đầu ra",
                "Vui lòng chọn thư mục đầu ra hoặc chọn 'Lưu phụ đề cùng vị trí với video'.",
                ["Bật tùy chọn 'Lưu phụ đề cùng vị trí với video'", "Hoặc chọn thư mục đầu ra cụ thể"]
            )
            return
            
        # Check if input folder exists
        if not os.path.exists(input_folder):
            show_warning_dialog(
                self.root,
                "Thư mục không tồn tại",
                f"Thư mục '{input_folder}' không tồn tại hoặc đã bị di chuyển.",
                ["Chọn lại thư mục đầu vào", "Kiểm tra đường dẫn thư mục"]
            )
            return
            
        # Xác định model dựa vào engine
        engine = self.engine_var.get()
        model_name = self.whisper_model_var.get() if engine == ENGINE_OPENAI_WHISPER else self.faster_model_var.get()
        
        self.status_label.configure(text="🔄 Đang tạo phụ đề...", text_color="#FF9800")
        
        # Tạo progress window
        progress_window = ProgressWindow(self.root)
        processor = SubtitleProcessor(progress_window.update)
        
        # Chạy xử lý trong thread riêng với error handling
        def process():
            def execute_generation():
                output_path = None if save_same_folder else output_folder
                return processor.process_videos(
                    input_folder,
                    output_path,
                    generate=True,
                    translate=False,
                    engine=engine,
                    model_name=model_name,
                    device=self.device_var.get(),
                    compute_type=self.compute_type_var.get()
                )
            
            def on_success(result):
                progress_window.close()
                show_success_notification(
                    self.root,
                    "Tạo phụ đề thành công",
                    "Đã tạo phụ đề cho tất cả video!"
                )
                self.status_label.configure(text="✅ Đã tạo phụ đề thành công!", text_color="#4CAF50")
                
            def on_error(error):
                progress_window.close()
                self.status_label.configure(text="❌ Lỗi khi tạo phụ đề", text_color="#F44336")
            
            ModernErrorHandler.safe_execute(
                self.root,
                execute_generation,
                context="Đang tạo phụ đề từ video",
                success_callback=on_success,
                error_callback=on_error
            )
        
        threading.Thread(target=process, daemon=True).start()
        
    def translate_subtitles(self):
        """Mở dialog dịch phụ đề hiện đại"""
        input_folder = self.input_folder_var.get()
        save_same_folder = self.save_same_folder_var.get()
        output_folder = self.output_folder_var.get()
        
        # Validation with modern error handling
        if not input_folder:
            show_warning_dialog(
                self.root,
                "Thiếu thông tin",
                "Vui lòng chọn thư mục chứa phụ đề trước khi dịch.",
                ["Nhấn vào khu vực 'Kéo thả thư mục vào đây'", "Hoặc nhấn nút 'Chọn thư mục'"]
            )
            return
            
        if not save_same_folder and not output_folder:
            show_warning_dialog(
                self.root,
                "Thiếu thư mục đầu ra",
                "Vui lòng chọn thư mục đầu ra hoặc chọn 'Lưu phụ đề cùng vị trí với video'.",
                ["Bật tùy chọn 'Lưu phụ đề cùng vị trí với video'", "Hoặc chọn thư mục đầu ra cụ thể"]
            )
            return
            
        # Check if input folder exists
        if not os.path.exists(input_folder):
            show_warning_dialog(
                self.root,
                "Thư mục không tồn tại",
                f"Thư mục '{input_folder}' không tồn tại hoặc đã bị di chuyển.",
                ["Chọn lại thư mục đầu vào", "Kiểm tra đường dẫn thư mục"]
            )
            return

        # Import the modern translation dialog
        from src.gui.components.modern_translation_dialog import ModernTranslationDialog
        
        # Create status update callback
        def update_status(text: str, color: str):
            self.status_label.configure(text=text, text_color=color)
        
        # Open the modern translation dialog
        ModernTranslationDialog(
            self.root, 
            input_folder, 
            output_folder, 
            save_same_folder,
            status_callback=update_status
        )

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
        
    def add_sidebar_preview(self):
        """Add subtitle preview sidebar"""
        # Import and create preview panel
        from src.gui.components.subtitle_preview import SubtitlePreviewPanel
        
        # Create sidebar frame
        sidebar_frame = ctk.CTkFrame(self.root, fg_color="#1A1A1A")
        sidebar_frame.grid(row=0, column=1, sticky="nsew", padx=(10, 20), pady=20)
        sidebar_frame.grid_columnconfigure(0, weight=1)
        sidebar_frame.grid_rowconfigure(0, weight=1)
        
        # Add preview panel
        self.preview_panel = SubtitlePreviewPanel(sidebar_frame, height=600)
        self.preview_panel.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
        
    def setup_keyboard_shortcuts(self):
        """Setup keyboard shortcuts for better UX"""
        # Bind keyboard shortcuts
        self.root.bind('<Control-g>', lambda e: self.generate_subtitles())  # Ctrl+G for Generate
        self.root.bind('<Control-t>', lambda e: self.translate_subtitles())  # Ctrl+T for Translate
        self.root.bind('<Control-o>', lambda e: self.file_selection.input_drag_frame.browse_folder())  # Ctrl+O for Open
        self.root.bind('<Control-s>', lambda e: self.open_settings())  # Ctrl+S for Settings
        self.root.bind('<Control-p>', lambda e: self.preview_panel.select_subtitle_file())  # Ctrl+P for Preview
        self.root.bind('<F1>', lambda e: self.show_help())  # F1 for Help
        self.root.bind('<F5>', lambda e: self.refresh_interface())  # F5 for Refresh
        
        # Focus the root window to capture keyboard events
        self.root.focus_set()
        
    def open_settings(self):
        """Open modern settings dialog"""
        from src.gui.components.modern_settings_dialog import ModernSettingsDialog
        ModernSettingsDialog(self.root)
        
    def show_help(self):
        """Show help dialog with keyboard shortcuts"""
        help_dialog = ctk.CTkToplevel(self.root)
        help_dialog.title("📖 Trợ giúp")
        help_dialog.geometry("500x400")
        help_dialog.transient(self.root)
        help_dialog.grab_set()
        
        # Center dialog
        help_dialog.update_idletasks()
        width = help_dialog.winfo_width()
        height = help_dialog.winfo_height()
        x = (help_dialog.winfo_screenwidth() // 2) - (width // 2)
        y = (help_dialog.winfo_screenheight() // 2) - (height // 2)
        help_dialog.geometry(f"{width}x{height}+{x}+{y}")
        
        main_frame = ctk.CTkScrollableFrame(help_dialog, fg_color="#1A1A1A")
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Title
        ctk.CTkLabel(
            main_frame,
            text="📖 Hướng dẫn sử dụng",
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color="#4CAF50"
        ).pack(pady=(0, 20))
        
        # Keyboard shortcuts
        shortcuts_frame = ctk.CTkFrame(main_frame, fg_color="#2B2B2B")
        shortcuts_frame.pack(fill="x", pady=(0, 20))
        
        ctk.CTkLabel(
            shortcuts_frame,
            text="⌨️ Phím tắt",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color="#FF9800"
        ).pack(pady=(15, 10))
        
        shortcuts = [
            ("Ctrl + G", "Tạo phụ đề"),
            ("Ctrl + T", "Dịch phụ đề"),
            ("Ctrl + O", "Chọn thư mục đầu vào"),
            ("Ctrl + S", "Mở cài đặt"),
            ("Ctrl + P", "Chọn file xem trước"),
            ("F1", "Hiện trợ giúp"),
            ("F5", "Làm mới giao diện")
        ]
        
        for shortcut, description in shortcuts:
            shortcut_frame = ctk.CTkFrame(shortcuts_frame, fg_color="transparent")
            shortcut_frame.pack(fill="x", padx=15, pady=2)
            
            ctk.CTkLabel(
                shortcut_frame,
                text=shortcut,
                font=ctk.CTkFont(size=12, weight="bold"),
                text_color="#2196F3",
                width=80
            ).pack(side="left")
            
            ctk.CTkLabel(
                shortcut_frame,
                text=description,
                font=ctk.CTkFont(size=12),
                text_color="#E0E0E0"
            ).pack(side="left", padx=(10, 0))
            
        ctk.CTkLabel(shortcuts_frame, text="", height=10).pack()
        
        # Usage tips
        tips_frame = ctk.CTkFrame(main_frame, fg_color="#2B2B2B")
        tips_frame.pack(fill="x", pady=(0, 20))
        
        ctk.CTkLabel(
            tips_frame,
            text="💡 Mẹo sử dụng",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color="#4CAF50"
        ).pack(pady=(15, 10))
        
        tips = [
            "• Kéo thả thư mục trực tiếp vào khu vực chọn file",
            "• Sử dụng panel xem trước để kiểm tra phụ đề",
            "• Tùy chỉnh cài đặt mặc định để tiết kiệm thời gian",
            "• Dùng dịch vụ AI khác nhau cho kết quả tốt nhất",
            "• Backup prompt quan trọng để tái sử dụng"
        ]
        
        for tip in tips:
            ctk.CTkLabel(
                tips_frame,
                text=tip,
                font=ctk.CTkFont(size=11),
                text_color="#E0E0E0",
                wraplength=400,
                justify="left"
            ).pack(anchor="w", padx=15, pady=2)
            
        ctk.CTkLabel(tips_frame, text="", height=10).pack()
        
        # Close button
        ctk.CTkButton(
            main_frame,
            text="✅ Đóng",
            command=help_dialog.destroy,
            height=40,
            fg_color="#4CAF50",
            hover_color="#45A049"
        ).pack(pady=20)
        
    def refresh_interface(self):
        """Refresh the interface"""
        # Update preview panel if exists
        if hasattr(self, 'preview_panel'):
            self.preview_panel.refresh_preview()
            
        # Update status
        self.status_label.configure(text="🔄 Đã làm mới giao diện", text_color="#4CAF50")
        
        # Reset status after 2 seconds
        self.root.after(2000, lambda: self.status_label.configure(
            text="✅ Sẵn sàng sử dụng", text_color="#4CAF50"
        ))
        
    def add_tooltips(self, generate_btn, translate_btn, clone_btn, manage_btn, convert_btn, settings_btn):
        """Add tooltips to buttons for better UX"""
        from src.gui.components.modern_tooltip import ModernButtonTooltip
        
        # Add tooltips with keyboard shortcuts
        ModernButtonTooltip(
            generate_btn,
            "Tạo phụ đề từ video bằng AI\nHỗ trợ nhiều định dạng video phổ biến",
            "Ctrl+G"
        )
        
        ModernButtonTooltip(
            translate_btn,
            "Dịch phụ đề sang ngôn ngữ khác\nSử dụng AI translation với nhiều dịch vụ",
            "Ctrl+T"
        )
        
        ModernButtonTooltip(
            clone_btn,
            "Sao chép tất cả file phụ đề .srt\nGiữ nguyên cấu trúc thư mục"
        )
        
        ModernButtonTooltip(
            manage_btn,
            "Quản lý phụ đề gốc\nBackup và khôi phục phụ đề"
        )
        
        ModernButtonTooltip(
            convert_btn,
            "Chuyển đổi định dạng phụ đề\nHỗ trợ VTT, ASS sang SRT"
        )
        
        ModernButtonTooltip(
            settings_btn,
            "Mở cài đặt ứng dụng\nTùy chỉnh các giá trị mặc định",
            "Ctrl+S"
        )
        
    def convert_subtitles(self):
        """Mở cửa sổ chuyển đổi định dạng phụ đề"""
        from src.gui.components.modern_convert_dialog import ModernConvertDialog
        ModernConvertDialog(self.root)
        
    def run(self):
        """Chạy ứng dụng"""
        self.root.mainloop()

def main():
    """Chạy ứng dụng chính"""
    if not check_display_available():
        setup_virtual_display()
        return
        
    try:
        app = ModernSubtitleApp()
        app.run()
    except Exception as e:
        print(f"❌ Lỗi khởi động ứng dụng: {str(e)}")
        print("\n🔧 Có thể thử các giải pháp sau:")
        print("1. Kiểm tra lại display server")
        print("2. Chạy với xvfb-run: xvfb-run -a python run.py") 
        print("3. Thiết lập biến môi trường DISPLAY")
        setup_virtual_display()

if __name__ == "__main__":
    main()