import tkinter as tk
from src.gui.components.main_app import SubtitleApp
import shutil
import os
import messagebox

def main():
    """Chạy ứng dụng chính"""
    root = tk.Tk()
    SubtitleApp(root)
    root.mainloop()
    
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
    count = 0
    for root, _, files in os.walk(input_folder):
        for file in files:
            if file.lower().endswith(".srt"):
                rel_path = os.path.relpath(os.path.join(root, file), input_folder)
                dest_path = os.path.join(output_folder, rel_path)
                os.makedirs(os.path.dirname(dest_path), exist_ok=True)
                shutil.copy2(os.path.join(root, file), dest_path)
                count += 1
    messagebox.showinfo("Thành công", f"Đã sao chép {count} file phụ đề .srt sang thư mục output!")

if __name__ == "__main__":
    main() 