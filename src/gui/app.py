import tkinter as tk
from src.gui.components.main_app import SubtitleApp

def main():
    """Chạy ứng dụng chính"""
    root = tk.Tk()
    SubtitleApp(root)
    root.mainloop()
    
if __name__ == "__main__":
    main() 