import customtkinter as ctk
from tkinter import filedialog, messagebox
import threading
import os
from pathlib import Path

from src.utils.subtitle_format_converter import batch_convert_to_srt
from src.gui.components.progress_window import ProgressWindow

class ModernConvertDialog:
    """Dialog chuyển đổi định dạng phụ đề hiện đại"""
    
    def __init__(self, parent):
        # Tạo dialog
        self.dialog = ctk.CTkToplevel(parent)
        self.dialog.title("Chuyển đổi định dạng phụ đề")
        self.dialog.geometry("700x500")
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # Cấu hình grid
        self.dialog.grid_columnconfigure(0, weight=1)
        self.dialog.grid_rowconfigure(0, weight=1)
        
        # Tạo các widget
        main_frame = ctk.CTkFrame(self.dialog)
        main_frame.grid(row=0, column=0, sticky="nsew", padx=20, pady=20)
        main_frame.grid_columnconfigure(0, weight=1)
        
        # Tiêu đề
        title_label = ctk.CTkLabel(
            main_frame, 
            text="🔄 Chuyển đổi định dạng phụ đề", 
            font=ctk.CTkFont(size=24, weight="bold"),
            text_color="#607D8B"
        )
        title_label.grid(row=0, column=0, pady=(0, 30), sticky="ew")
        
        # Phần chọn thư mục
        folder_frame = ctk.CTkFrame(main_frame, fg_color="#2B2B2B")
        folder_frame.grid(row=1, column=0, sticky="ew", pady=(0, 20))
        folder_frame.grid_columnconfigure(1, weight=1)
        
        # Tiêu đề section
        folder_title = ctk.CTkLabel(
            folder_frame, 
            text="📁 Chọn thư mục", 
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color="#2196F3"
        )
        folder_title.grid(row=0, column=0, columnspan=3, pady=(15, 20), sticky="ew")
        
        ctk.CTkLabel(folder_frame, text="Thư mục chứa phụ đề:", font=ctk.CTkFont(size=14)).grid(
            row=1, column=0, sticky="w", padx=15, pady=10
        )
        
        self.folder_var = ctk.StringVar()
        folder_entry = ctk.CTkEntry(
            folder_frame, 
            textvariable=self.folder_var, 
            placeholder_text="Chọn thư mục chứa phụ đề...",
            height=35
        )
        folder_entry.grid(row=1, column=1, sticky="ew", padx=15, pady=10)
        
        def browse_folder():
            folder = filedialog.askdirectory()
            if folder:
                self.folder_var.set(folder)
                
        ctk.CTkButton(
            folder_frame, 
            text="Chọn thư mục", 
            command=browse_folder,
            height=35,
            fg_color="#4CAF50",
            hover_color="#45A049"
        ).grid(row=1, column=2, padx=15, pady=10)
        
        # Cài đặt tìm kiếm đệ quy
        self.recursive_var = ctk.BooleanVar(value=True)
        ctk.CTkCheckBox(
            folder_frame, 
            text="🔍 Tìm kiếm trong các thư mục con", 
            variable=self.recursive_var,
            text_color="#E0E0E0",
            checkbox_width=20,
            checkbox_height=20
        ).grid(row=2, column=0, columnspan=3, sticky="w", padx=15, pady=10)
        
        # Thông tin các định dạng được hỗ trợ
        info_frame = ctk.CTkFrame(main_frame, fg_color="#2B2B2B")
        info_frame.grid(row=2, column=0, sticky="ew", pady=(0, 20))
        
        # Tiêu đề section
        info_title = ctk.CTkLabel(
            info_frame, 
            text="ℹ️ Thông tin hỗ trợ", 
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color="#FF9800"
        )
        info_title.grid(row=0, column=0, pady=(15, 20), sticky="ew")
        
        info_text = """
Chức năng này sẽ tìm kiếm và chuyển đổi tất cả các file phụ đề không phải SRT sang định dạng SRT.

Các định dạng được hỗ trợ hiện tại:
• VTT (WebVTT)

Kết quả sẽ là file SRT cùng tên và cùng thư mục với file gốc.
        """
        
        info_label = ctk.CTkLabel(
            info_frame, 
            text=info_text, 
            justify="left", 
            wraplength=600,
            font=ctk.CTkFont(size=12),
            text_color="#E0E0E0"
        )
        info_label.grid(row=1, column=0, padx=15, pady=(0, 15), sticky="ew")
        
        # Nút điều khiển
        button_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        button_frame.grid(row=3, column=0, pady=20)
        
        ctk.CTkButton(
            button_frame, 
            text="🔄 Bắt đầu chuyển đổi", 
            command=self.convert,
            height=45,
            width=200,
            fg_color="#607D8B",
            hover_color="#455A64",
            font=ctk.CTkFont(size=16, weight="bold")
        ).pack(side="left", padx=10)
        
        ctk.CTkButton(
            button_frame, 
            text="❌ Đóng", 
            command=self.dialog.destroy,
            height=45,
            width=150,
            fg_color="#F44336",
            hover_color="#D32F2F",
            font=ctk.CTkFont(size=16)
        ).pack(side="left", padx=10)
        
    def convert(self):
        """Thực hiện chuyển đổi phụ đề"""
        folder = self.folder_var.get()
        
        if not folder:
            messagebox.showerror("Lỗi", "Vui lòng chọn thư mục chứa phụ đề")
            return
            
        if not os.path.exists(folder):
            messagebox.showerror("Lỗi", f"Thư mục '{folder}' không tồn tại")
            return
            
        # Tạo cửa sổ tiến trình
        progress_window = ProgressWindow(self.dialog)
        
        def process():
            try:
                # Thực hiện chuyển đổi
                batch_convert_to_srt(folder)
                
                # Đóng cửa sổ tiến trình và hiển thị thông báo
                progress_window.close()
                self.dialog.after(0, lambda: messagebox.showinfo("Thành công", "Đã chuyển đổi xong các file phụ đề"))
                
            except Exception as e:
                progress_window.close()
                self.dialog.after(0, lambda: messagebox.showerror("Lỗi", str(e)))
                
        # Chạy trong thread riêng
        threading.Thread(target=process, daemon=True).start()