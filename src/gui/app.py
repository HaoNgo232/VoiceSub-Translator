import tkinter as tk
from tkinter import messagebox
import sys
import os
import shutil
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor


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

if __name__ == "__main__":
    main()
