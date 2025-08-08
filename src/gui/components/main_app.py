import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import json
import os
from pathlib import Path
from typing import Dict, Optional
import threading
import shutil
from concurrent.futures import ThreadPoolExecutor

from src.gui.subtitle_processor import SubtitleProcessor
from src.gui.components.progress_window import ProgressWindow
from src.gui.components.prompt_dialog import PromptDialog
from src.utils.subtitle_management import backup_original_subtitles, restore_original_subtitles
from src.utils.transcription import ENGINE_OPENAI_WHISPER, ENGINE_FASTER_WHISPER

class SubtitleApp:
    """Ứng dụng chính xử lý phụ đề"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("Công cụ xử lý phụ đề")
        self.root.geometry("800x650")  # Tăng chiều cao cho widget mới
        
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
        
        # Checkbox lưu cùng vị trí video
        self.save_same_folder_var = tk.BooleanVar(value=True)
        self.save_same_folder_cb = ttk.Checkbutton(folder_frame, text="Lưu phụ đề cùng vị trí với video", variable=self.save_same_folder_var, command=self.toggle_output_folder)
        self.save_same_folder_cb.grid(row=1, column=0, sticky=tk.W, pady=2)
        
        # Output folder
        ttk.Label(folder_frame, text="Thư mục đầu ra:").grid(row=2, column=0, sticky=tk.W)
        self.output_folder_var = tk.StringVar()
        self.output_folder_entry = ttk.Entry(folder_frame, textvariable=self.output_folder_var, width=50, state='disabled')
        self.output_folder_entry.grid(row=2, column=1, padx=5)
        self.output_folder_btn = ttk.Button(folder_frame, text="Chọn", command=self.select_output_folder, state='disabled')
        self.output_folder_btn.grid(row=2, column=2)
        
        # Phần cấu hình transcription
        transcription_frame = ttk.LabelFrame(main_frame, text="Cấu hình tạo phụ đề", padding="5")
        transcription_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        
        # Engine
        ttk.Label(transcription_frame, text="Engine:").grid(row=0, column=0, sticky=tk.W)
        self.engine_var = tk.StringVar(value=ENGINE_OPENAI_WHISPER)
        engine_combo = ttk.Combobox(transcription_frame, textvariable=self.engine_var, 
                                   values=[ENGINE_OPENAI_WHISPER, ENGINE_FASTER_WHISPER],
                                   width=15)
        engine_combo.grid(row=0, column=1, sticky=tk.W, padx=5)
        engine_combo.bind("<<ComboboxSelected>>", self.on_engine_selected)
        
        # Model cho OpenAI Whisper
        ttk.Label(transcription_frame, text="OpenAI Model:").grid(row=0, column=2, sticky=tk.W, padx=(10, 0))
        self.whisper_model_var = tk.StringVar(value="base.en")
        whisper_model_combo = ttk.Combobox(transcription_frame, textvariable=self.whisper_model_var, 
                                          values=["tiny.en", "base.en", "small.en"],
                                          width=10)
        whisper_model_combo.grid(row=0, column=3, sticky=tk.W, padx=5)
        
        # Model cho Faster Whisper
        ttk.Label(transcription_frame, text="Faster-Whisper Model:").grid(row=1, column=0, sticky=tk.W)
        self.faster_model_var = tk.StringVar(value="base")
        faster_model_combo = ttk.Combobox(transcription_frame, textvariable=self.faster_model_var, 
                                         values=["tiny", "base", "small", "medium", "large-v3", "distil-large-v3"],
                                         width=15)
        faster_model_combo.grid(row=1, column=1, sticky=tk.W, padx=5)
        
        # Compute Type
        ttk.Label(transcription_frame, text="Precision:").grid(row=1, column=2, sticky=tk.W, padx=(10, 0))
        self.compute_type_var = tk.StringVar(value="float16")
        compute_type_combo = ttk.Combobox(transcription_frame, textvariable=self.compute_type_var, 
                                         values=["float16", "float32", "int8", "int8_float16"],
                                         width=10)
        compute_type_combo.grid(row=1, column=3, sticky=tk.W, padx=5)
        
        # Device
        ttk.Label(transcription_frame, text="Device:").grid(row=2, column=0, sticky=tk.W)
        self.device_var = tk.StringVar(value="cuda")
        device_combo = ttk.Combobox(transcription_frame, textvariable=self.device_var, 
                                   values=["cuda", "cpu"],
                                   width=10)
        device_combo.grid(row=2, column=1, sticky=tk.W, padx=5)
        
        # Phần quản lý prompts
        prompt_frame = ttk.LabelFrame(main_frame, text="Quản lý Prompts", padding="5")
        prompt_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=5)
        
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
        control_frame.grid(row=3, column=0, columnspan=2, pady=10)
        
        ttk.Button(control_frame, text="Sao chép phụ đề", command=self.clone_subtitles).grid(row=0, column=2, padx=5)
        ttk.Button(control_frame, text="Tạo phụ đề", command=self.generate_subtitles).grid(row=0, column=0, padx=5)
        ttk.Button(control_frame, text="Dịch phụ đề", command=self.translate_subtitles).grid(row=0, column=1, padx=5)
        
        # Thêm nút quản lý phụ đề gốc
        ttk.Button(control_frame, text="Quản lý phụ đề gốc", command=self.manage_original_subtitles).grid(row=0, column=3, padx=5)
        
    def on_engine_selected(self, event):
        """Xử lý khi chọn engine"""
        engine = self.engine_var.get()
        # Cập nhật UI dựa trên engine được chọn
        if engine == ENGINE_OPENAI_WHISPER:
            # Hiển thị model cho OpenAI Whisper
            pass  # Không cần thay đổi gì vì đã hiển thị sẵn
        elif engine == ENGINE_FASTER_WHISPER:
            # Đặt giá trị mặc định cho compute_type là float32
            self.compute_type_var.set("float32")
            
        
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
                
    def toggle_output_folder(self):
        """Bật/tắt trường chọn output folder theo checkbox"""
        if self.save_same_folder_var.get():
            self.output_folder_entry.config(state='disabled')
            self.output_folder_btn.config(state='disabled')
        else:
            self.output_folder_entry.config(state='normal')
            self.output_folder_btn.config(state='normal')

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
                messagebox.showinfo("Thành công", "Đã tạo phụ đề cho tất cả video!")
            except Exception as e:
                progress_window.close()
                self.root.after(0, lambda: messagebox.showerror("Lỗi", str(e)))
        threading.Thread(target=process, daemon=True).start()
        
    def translate_subtitles(self):
        """Dịch phụ đề"""
        # Kiểm tra logic đúng với lựa chọn lưu cùng vị trí
        if not self.input_folder_var.get():
            messagebox.showerror("Lỗi", "Vui lòng chọn thư mục đầu vào")
            return
        if not self.save_same_folder_var.get() and not self.output_folder_var.get():
            messagebox.showerror("Lỗi", "Vui lòng chọn thư mục đầu ra hoặc chọn lưu cùng vị trí với video")
            return

        # Lấy giá trị input/output folder
        input_folder = self.input_folder_var.get()
        output_folder = None if self.save_same_folder_var.get() else self.output_folder_var.get()

        # Tạo cửa sổ tiến trình
        progress_window = ProgressWindow(self.root)
        processor = SubtitleProcessor(progress_window.update)

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
            except Exception as e:
                self.root.after(0, lambda: messagebox.showerror("Lỗi", str(e)))
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

        input_folder = Path(self.input_folder_var.get())
        output_folder = Path(self.output_folder_var.get())

        def copy_file(src: Path) -> None:
            rel_path = src.relative_to(input_folder)
            dest_path = output_folder / rel_path
            dest_path.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, dest_path)

        subtitles = list(input_folder.rglob("*.srt"))
        with ThreadPoolExecutor() as executor:
            list(executor.map(copy_file, subtitles))

        messagebox.showinfo(
            "Thành công",
            f"Đã sao chép {len(subtitles)} file phụ đề .srt sang thư mục output!",
        )
        
    def manage_original_subtitles(self):
        """Mở cửa sổ quản lý phụ đề gốc"""
        if not self.input_folder_var.get():
            messagebox.showerror("Lỗi", "Vui lòng chọn thư mục đầu vào")
            return
            
        # Tạo cửa sổ dialog
        dialog = tk.Toplevel(self.root)
        dialog.title("Quản lý phụ đề gốc")
        dialog.geometry("500x300")
        dialog.transient(self.root)
        dialog.grab_set()
        
        # Tạo các widget
        frame = ttk.Frame(dialog, padding="10")
        frame.pack(fill=tk.BOTH, expand=True)
        
        # Tự động tạo đường dẫn backup mặc định từ thư mục đầu vào
        default_backup = os.path.join(self.input_folder_var.get(), "backup_subtitles")
        
        # Thư mục backup
        ttk.Label(frame, text="Thư mục backup:").grid(row=0, column=0, sticky=tk.W, pady=5)
        backup_folder_var = tk.StringVar(value=default_backup)
        backup_entry = ttk.Entry(frame, textvariable=backup_folder_var, width=40)
        backup_entry.grid(row=0, column=1, padx=5, pady=5, sticky=(tk.W, tk.E))
        
        def select_backup_folder():
            folder = filedialog.askdirectory()
            if folder:
                backup_folder_var.set(folder)
                
        ttk.Button(frame, text="Chọn", command=select_backup_folder).grid(row=0, column=2, padx=5, pady=5)
        
        # Ngôn ngữ đích
        ttk.Label(frame, text="Ngôn ngữ đích:").grid(row=1, column=0, sticky=tk.W, pady=5)
        target_lang_var = tk.StringVar(value="vi")
        lang_entry = ttk.Entry(frame, textvariable=target_lang_var, width=10)
        lang_entry.grid(row=1, column=1, padx=5, pady=5, sticky=tk.W)
        
        # Mô tả
        description = """
        Chức năng này sẽ xóa các phụ đề gốc của video đã có phụ đề dịch và sao lưu chúng vào thư mục backup.
        Điều này giúp giảm sự thừa thãi khi bạn chỉ cần sử dụng phụ đề đã dịch.
        
        Bạn có thể khôi phục phụ đề gốc từ thư mục backup bất kỳ lúc nào.
        """
        desc_label = ttk.Label(frame, text=description, wraplength=480, justify="left")
        desc_label.grid(row=2, column=0, columnspan=3, pady=10, sticky=(tk.W, tk.E))
        
        # Frame chứa các nút
        button_frame = ttk.Frame(frame)
        button_frame.grid(row=3, column=0, columnspan=3, pady=10)
        
        def backup_subtitles():
            input_folder = self.input_folder_var.get()
            backup_folder = backup_folder_var.get()
            target_lang = target_lang_var.get()
            
            # Tạo cửa sổ tiến trình
            progress_window = ProgressWindow(dialog)
            
            def process():
                try:
                    # Thực hiện backup
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
            
            # Kiểm tra thư mục backup có tồn tại không
            if not os.path.exists(backup_folder):
                messagebox.showerror("Lỗi", f"Thư mục backup '{backup_folder}' không tồn tại")
                return
                
            # Tạo cửa sổ tiến trình
            progress_window = ProgressWindow(dialog)
            
            def process():
                try:
                    # Thực hiện khôi phục
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
            
        ttk.Button(button_frame, text="Sao lưu và xóa phụ đề gốc", command=backup_subtitles).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Khôi phục phụ đề gốc", command=restore_subtitles).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Đóng", command=dialog.destroy).pack(side=tk.LEFT, padx=5) 