import tkinter as tk
from tkinter import messagebox
import sys
import os

# Thêm thư mục gốc vào đường dẫn Python
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

def main():
    """Chạy ứng dụng chính"""
    # Import trong hàm để tránh vòng lặp
    from src.gui.components.main_app import SubtitleApp
    
    root = tk.Tk()
    try:
        SubtitleApp(root)
        root.mainloop()
    except Exception as e:
        messagebox.showerror("Lỗi khởi động", f"Không thể khởi động ứng dụng: {str(e)}")
        root.destroy()
    
if __name__ == "__main__":
    main()