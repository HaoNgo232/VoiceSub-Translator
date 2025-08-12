#!/usr/bin/env python3
"""
Dependency Updater for VoiceSub-Translator
Cập nhật dependencies một cách an toàn
"""

import os
import sys
import subprocess
import importlib.util
import time

def print_header(title):
    """In tiêu đề với định dạng đẹp"""
    print(f"\n{'='*50}")
    print(f"  {title}")
    print(f"{'='*50}")

def check_venv():
    """Kiểm tra môi trường ảo"""
    if not hasattr(sys, 'real_prefix') and not (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
        print("❌ Vui lòng kích hoạt môi trường ảo trước!")
        print("   source venv/bin/activate")
        return False
    return True

def backup_requirements():
    """Sao lưu requirements hiện tại"""
    if os.path.exists("requirements.txt"):
        import shutil
        backup_name = f"requirements_backup_{int(time.time())}.txt"
        shutil.copy("requirements.txt", backup_name)
        print(f"✅ Đã sao lưu requirements.txt thành {backup_name}")
        return backup_name
    return None

def get_current_versions():
    """Lấy phiên bản hiện tại của các packages"""
    packages = {}
    
    # Danh sách packages cần kiểm tra
    check_packages = [
        'torch', 'torchaudio', 'torchvision',
        'whisper', 'customtkinter', 'PIL',
        'numpy', 'scipy', 'requests'
    ]
    
    for package in check_packages:
        try:
            mod = importlib.import_module(package)
            if hasattr(mod, '__version__'):
                packages[package] = mod.__version__
        except ImportError:
            packages[package] = "Not installed"
    
    return packages

def update_pip():
    """Cập nhật pip"""
    print("🔧 Cập nhật pip...")
    try:
        subprocess.run([sys.executable, "-m", "pip", "install", "--upgrade", "pip"], check=True)
        print("✅ Pip đã được cập nhật")
        return True
    except subprocess.CalledProcessError:
        print("❌ Không thể cập nhật pip")
        return False

def update_package(package):
    """Cập nhật một package cụ thể"""
    print(f"🔧 Cập nhật {package}...")
    try:
        subprocess.run([sys.executable, "-m", "pip", "install", "--upgrade", package], check=True)
        print(f"✅ {package} đã được cập nhật")
        return True
    except subprocess.CalledProcessError:
        print(f"❌ Không thể cập nhật {package}")
        return False

def update_all_packages():
    """Cập nhật tất cả packages"""
    print("🔧 Cập nhật tất cả packages...")
    try:
        subprocess.run([sys.executable, "-m", "pip", "install", "--upgrade", "-r", "requirements.txt"], check=True)
        print("✅ Tất cả packages đã được cập nhật")
        return True
    except subprocess.CalledProcessError:
        print("❌ Không thể cập nhật tất cả packages")
        return False

def show_update_menu():
    """Hiển thị menu cập nhật"""
    print_header("MENU CẬP NHẬT")
    print("1. Cập nhật pip")
    print("2. Cập nhật tất cả packages")
    print("3. Cập nhật package cụ thể")
    print("4. Kiểm tra phiên bản hiện tại")
    print("5. Thoát")
    
    choice = input("\nChọn tùy chọn (1-5): ").strip()
    return choice

def main():
    print("🔄 VoiceSub-Translator Dependency Updater")
    print("Cập nhật dependencies một cách an toàn")
    
    if not check_venv():
        return
    
    while True:
        choice = show_update_menu()
        
        if choice == "1":
            update_pip()
        
        elif choice == "2":
            update_all_packages()
        
        elif choice == "3":
            package = input("Nhập tên package cần cập nhật: ").strip()
            if package:
                update_package(package)
            else:
                print("❌ Tên package không hợp lệ")
        
        elif choice == "4":
            print_header("PHIÊN BẢN HIỆN TẠI")
            current_versions = get_current_versions()
            for package, version in current_versions.items():
                print(f"   {package}: {version}")
        
        elif choice == "5":
            print("👋 Tạm biệt!")
            break
        
        else:
            print("❌ Lựa chọn không hợp lệ")
        
        input("\nNhấn Enter để tiếp tục...")

if __name__ == "__main__":
    main()