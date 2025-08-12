#!/usr/bin/env python3
"""
Launcher cho giao diện hiện đại của ứng dụng xử lý phụ đề
Sử dụng CustomTkinter thay vì Tkinter cũ
"""

import sys
import os

# Thêm thư mục gốc vào đường dẫn Python
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

def check_dependencies():
    """Kiểm tra và cài đặt dependencies cần thiết"""
    try:
        import customtkinter
        print("✅ CustomTkinter đã được cài đặt")
        return True
    except ImportError:
        print("❌ CustomTkinter chưa được cài đặt")
        print("Đang cài đặt CustomTkinter...")
        
        try:
            import subprocess
            subprocess.check_call([sys.executable, "-m", "pip", "install", "customtkinter>=5.2.0"])
            print("✅ Đã cài đặt CustomTkinter thành công")
            return True
        except Exception as e:
            print(f"❌ Không thể cài đặt CustomTkinter: {e}")
            print("Vui lòng cài đặt thủ công bằng lệnh:")
            print("pip install customtkinter>=5.2.0")
            return False

def main():
    """Hàm chính"""
    print("🎬 Khởi động ứng dụng xử lý phụ đề - Phiên bản hiện đại")
    print("=" * 60)
    
    # Kiểm tra dependencies
    if not check_dependencies():
        print("❌ Không thể khởi động ứng dụng do thiếu dependencies")
        return
    
    try:
        # Import và chạy ứng dụng hiện đại
        from src.gui.modern_app import ModernSubtitleApp
        
        print("✅ Khởi động giao diện hiện đại...")
        app = ModernSubtitleApp()
        app.run()
        
    except Exception as e:
        print(f"❌ Lỗi khi khởi động ứng dụng: {e}")
        print("Vui lòng kiểm tra lại cài đặt và thử lại")

if __name__ == "__main__":
    main()