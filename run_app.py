#!/usr/bin/env python3
"""
VoiceSub-Translator App Runner
Script Python đơn giản để chạy ứng dụng
"""

import os
import sys
import subprocess
import importlib.util

def check_venv():
    """Kiểm tra môi trường ảo"""
    if not hasattr(sys, 'real_prefix') and not (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
        print("❌ Vui lòng kích hoạt môi trường ảo trước!")
        print("   source venv/bin/activate")
        return False
    return True

def check_dependencies():
    """Kiểm tra thư viện phụ thuộc"""
    required_modules = ['torch', 'whisper', 'customtkinter']
    missing_modules = []
    
    for module in required_modules:
        if importlib.util.find_spec(module) is None:
            missing_modules.append(module)
    
    if missing_modules:
        print(f"❌ Thiếu thư viện: {', '.join(missing_modules)}")
        print("   Vui lòng chạy: ./smart_install.sh")
        return False
    
    print("✅ Tất cả thư viện đã sẵn sàng")
    return True

def find_gui_app():
    """Tìm ứng dụng GUI có sẵn"""
    gui_options = [
        ("run_modern_gui.py", "Giao diện hiện đại"),
        ("src/gui/modern_app.py", "Giao diện hiện đại"),
        ("src/gui/app.py", "Giao diện cổ điển"),
        ("simple_test.py", "Test đơn giản")
    ]
    
    for file_path, description in gui_options:
        if os.path.exists(file_path):
            return file_path, description
    
    return None, None

def run_app():
    """Chạy ứng dụng"""
    print("🚀 VoiceSub-Translator App Runner")
    print("==================================")
    
    # Kiểm tra môi trường
    if not check_venv():
        return
    
    if not check_dependencies():
        return
    
    # Tìm ứng dụng GUI
    app_path, app_desc = find_gui_app()
    if not app_path:
        print("❌ Không tìm thấy ứng dụng GUI nào!")
        return
    
    print(f"🔍 Tìm thấy: {app_desc} ({app_path})")
    
    # Chạy ứng dụng
    try:
        print(f"🚀 Khởi chạy {app_desc}...")
        subprocess.run([sys.executable, app_path], check=True)
    except subprocess.CalledProcessError as e:
        print(f"❌ Lỗi khi chạy ứng dụng: {e}")
    except KeyboardInterrupt:
        print("\n👋 Đã dừng ứng dụng")

if __name__ == "__main__":
    run_app()