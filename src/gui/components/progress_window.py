import tkinter as tk
from tkinter import ttk

class ProgressWindow:
    """Cửa sổ hiển thị tiến trình xử lý"""
    
    def __init__(self, parent):
        # Tạo dialog
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Đang xử lý...")
        self.dialog.geometry("400x150")
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # Tạo các thành phần
        main_frame = ttk.Frame(self.dialog, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Trạng thái
        self.status_var = tk.StringVar(value="Đang chuẩn bị...")
        ttk.Label(main_frame, textvariable=self.status_var).pack(pady=(0, 10))
        
        # Tiến trình
        self.progress = ttk.Progressbar(main_frame, mode="determinate", length=350)
        self.progress.pack(pady=(0, 10))
        
        # Thông tin tiến trình
        self.progress_var = tk.StringVar(value="0/0")
        ttk.Label(main_frame, textvariable=self.progress_var).pack()
        
        # Ngăn đóng cửa sổ
        self.dialog.protocol("WM_DELETE_WINDOW", lambda: None)
        
        # Cập nhật giao diện
        self.dialog.update()

    def update(self, current: int, total: int, status: str = ""):
        """Cập nhật trạng thái tiến trình"""

        def _update():
            if status:
                self.status_var.set(status)
            self.progress_var.set(f"{current}/{total}")
            self.progress["value"] = (current / total) * 100

        self.dialog.after(0, _update)

    def close(self):
        """Đóng cửa sổ tiến trình"""

        # Sử dụng after để đảm bảo gọi hủy cửa sổ trong main thread
        self.dialog.after(0, self.dialog.destroy)

    # Hỗ trợ sử dụng ProgressWindow như một context manager
    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
        # Không chặn ngoại lệ (để xử lý bên ngoài nếu cần)
        return False

