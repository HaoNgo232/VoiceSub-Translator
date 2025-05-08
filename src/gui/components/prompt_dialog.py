import tkinter as tk
from tkinter import ttk

class PromptDialog:
    """Dialog hiển thị form nhập/sửa prompt"""
    
    def __init__(self, parent, title, name="", content=""):
        self.result = None
        
        # Tạo dialog
        self.dialog = tk.Toplevel(parent)
        self.dialog.title(title)
        self.dialog.geometry("500x400")
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # Tạo form
        ttk.Label(self.dialog, text="Tên prompt:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        self.name_var = tk.StringVar(value=name)
        name_entry = ttk.Entry(self.dialog, textvariable=self.name_var, width=40)
        name_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=5, pady=5)
        
        ttk.Label(self.dialog, text="Nội dung:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        self.content_text = tk.Text(self.dialog, height=15, width=50)
        self.content_text.grid(row=2, column=0, columnspan=2, padx=5, pady=5)
        
        if content:
            self.content_text.insert("1.0", content)
            
        # Nút điều khiển
        button_frame = ttk.Frame(self.dialog)
        button_frame.grid(row=3, column=0, columnspan=2, pady=10)
        
        ttk.Button(button_frame, text="OK", command=self.on_ok).grid(row=0, column=0, padx=5)
        ttk.Button(button_frame, text="Hủy", command=self.on_cancel).grid(row=0, column=1, padx=5)
        
        # Focus vào trường đầu tiên
        name_entry.focus_set()
        
        # Đợi dialog đóng
        parent.wait_window(self.dialog)
        
    def on_ok(self):
        """Xử lý khi nhấn OK"""
        name = self.name_var.get().strip()
        content = self.content_text.get("1.0", tk.END).strip()
        
        if name and content:
            self.result = (name, content)
            self.dialog.destroy()
        
    def on_cancel(self):
        """Xử lý khi nhấn Cancel"""
        self.dialog.destroy() 