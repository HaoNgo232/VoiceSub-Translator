import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import threading
import os
from pathlib import Path

from src.utils.subtitle_format_converter import batch_convert_to_srt
from src.gui.components.progress_window import ProgressWindow

class ConvertDialog:
    """Dialog chuyển đổi định dạng phụ đề"""
    
    def __init__(self, parent):
        # Tạo dialog
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Chuyển đổi định dạng phụ đề")
        self.dialog.geometry("650x400")
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # Tạo các widget
        main_frame = ttk.Frame(self.dialog, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Phần chọn thư mục
        folder_frame = ttk.LabelFrame(main_frame, text="Thư mục", padding="5")
        folder_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(folder_frame, text="Thư mục chứa phụ đề:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.folder_var = tk.StringVar()
        folder_entry = ttk.Entry(folder_frame, textvariable=self.folder_var, width=40)
        folder_entry.grid(row=0, column=1, padx=5, pady=5, sticky=(tk.W, tk.E))
        
        def browse_folder():
            folder = filedialog.askdirectory()
            if folder:
                self.folder_var.set(folder)
                
        ttk.Button(folder_frame, text="Chọn", command=browse_folder).grid(row=0, column=2, padx=5, pady=5)
        
        # Cài đặt tìm kiếm đệ quy
        self.recursive_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(folder_frame, text="Tìm kiếm trong các thư mục con", variable=self.recursive_var).grid(row=1, column=0, columnspan=3, sticky=tk.W, pady=5)
        
        # Thông tin các định dạng được hỗ trợ
        info_frame = ttk.LabelFrame(main_frame, text="Thông tin", padding="5")
        info_frame.pack(fill=tk.X, padx=5, pady=5)
        
        info_text = """
Chức năng này sẽ tìm kiếm và chuyển đổi tất cả các file phụ đề không phải SRT sang định dạng SRT.

Các định dạng được hỗ trợ hiện tại:
- VTT (WebVTT)

Kết quả sẽ là file SRT cùng tên và cùng thư mục với file gốc.
        """
        
        info_label = ttk.Label(info_frame, text=info_text, justify="left", wraplength=480)
        info_label.pack(padx=5, pady=5)
        
        # Nút điều khiển
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(pady=10)
        
        ttk.Button(button_frame, text="Chuyển đổi", command=self.convert).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Đóng", command=self.dialog.destroy).pack(side=tk.LEFT, padx=5)
        
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