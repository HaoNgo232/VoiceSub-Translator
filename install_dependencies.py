#!/usr/bin/env python3
"""
Automatic Dependency Installer for VoiceSub-Translator
Cài đặt tất cả dependencies một cách tự động và an toàn
"""

import os
import sys
import subprocess
import time
import shutil
from pathlib import Path

def print_header(title: str):
    """In tiêu đề với định dạng đẹp"""
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}")

def print_step(step: str, message: str):
    """In bước thực hiện"""
    print(f"\n🔧 {step}")
    print(f"   {message}")

def check_python_version():
    """Kiểm tra phiên bản Python"""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print("❌ Python 3.8+ là bắt buộc")
        print(f"   Hiện tại: Python {version.major}.{version.minor}")
        return False
    print(f"✅ Python version: {version.major}.{version.minor}.{version.micro}")
    return True

def check_virtual_environment():
    """Kiểm tra môi trường ảo"""
    if hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
        print("✅ Đang chạy trong môi trường ảo")
        return True
    else:
        print("⚠️  Không chạy trong môi trường ảo")
        print("   Khuyến nghị: Kích hoạt môi trường ảo trước khi cài đặt")
        response = input("   Bạn có muốn tiếp tục không? (y/N): ").strip().lower()
        return response in ['y', 'yes']

def backup_requirements():
    """Sao lưu requirements.txt nếu tồn tại"""
    if os.path.exists("requirements.txt"):
        backup_name = f"requirements_backup_{int(time.time())}.txt"
        shutil.copy("requirements.txt", backup_name)
        print(f"✅ Đã sao lưu requirements.txt thành {backup_name}")
        return backup_name
    return None

def upgrade_pip():
    """Nâng cấp pip"""
    print_step("Nâng cấp pip", "Đảm bảo pip có phiên bản mới nhất")
    try:
        result = subprocess.run([
            sys.executable, "-m", "pip", "install", "--upgrade", "pip"
        ], capture_output=True, text=True, check=True)
        print("✅ Pip đã được nâng cấp")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Không thể nâng cấp pip: {e}")
        return False

def install_package(package: str, retries: int = 2):
    """Cài đặt một package cụ thể"""
    for attempt in range(retries + 1):
        try:
            print(f"   📦 Cài đặt {package}... (lần thử {attempt + 1})")
            result = subprocess.run([
                sys.executable, "-m", "pip", "install", package
            ], capture_output=True, text=True, check=True)
            print(f"   ✅ {package} đã được cài đặt thành công")
            return True
        except subprocess.CalledProcessError as e:
            if attempt < retries:
                print(f"   ⚠️  Lần thử {attempt + 1} thất bại, thử lại...")
                time.sleep(2)
            else:
                print(f"   ❌ Không thể cài đặt {package}: {e}")
                return False

def install_core_dependencies():
    """Cài đặt các dependencies cốt lõi trước"""
    print_step("Cài đặt dependencies cốt lõi", "Cài đặt các packages cơ bản trước")
    
    core_packages = [
        "numpy>=1.21.0",
        "requests>=2.25.0",
        "Pillow>=9.0.0"
    ]
    
    for package in core_packages:
        if not install_package(package):
            print(f"❌ Không thể cài đặt {package}")
            return False
    
    print("✅ Tất cả dependencies cốt lõi đã được cài đặt")
    return True

def install_ai_dependencies():
    """Cài đặt các dependencies AI"""
    print_step("Cài đặt dependencies AI", "Cài đặt PyTorch và Whisper")
    
    # Cài đặt PyTorch (CPU version để tránh xung đột)
    print("   📦 Cài đặt PyTorch (CPU version)...")
    try:
        result = subprocess.run([
            sys.executable, "-m", "pip", "install", 
            "torch", "torchaudio", "torchvision", "--index-url", "https://download.pytorch.org/whl/cpu"
        ], capture_output=True, text=True, check=True)
        print("   ✅ PyTorch đã được cài đặt")
    except subprocess.CalledProcessError as e:
        print(f"   ❌ Không thể cài đặt PyTorch: {e}")
        return False
    
    # Cài đặt Whisper
    ai_packages = [
        "openai-whisper>=20231117",
        "faster-whisper>=0.9.0"
    ]
    
    for package in ai_packages:
        if not install_package(package):
            print(f"❌ Không thể cài đặt {package}")
            return False
    
    print("✅ Tất cả dependencies AI đã được cài đặt")
    return True

def install_gui_dependencies():
    """Cài đặt các dependencies GUI"""
    print_step("Cài đặt dependencies GUI", "Cài đặt CustomTkinter và các packages liên quan")
    
    gui_packages = [
        "customtkinter>=5.2.0"
    ]
    
    for package in gui_packages:
        if not install_package(package):
            print(f"❌ Không thể cài đặt {package}")
            return False
    
    print("✅ Tất cả dependencies GUI đã được cài đặt")
    return True

def install_remaining_dependencies():
    """Cài đặt các dependencies còn lại"""
    print_step("Cài đặt dependencies còn lại", "Cài đặt các packages bổ sung")
    
    remaining_packages = [
        "scipy>=1.7.0",
        "pandas>=1.3.0",
        "openai>=1.0.0",
        "ffmpeg-python>=0.2.0",
        "pydub>=0.25.0",
        "pathlib2>=2.3.0",
        "typing-extensions>=4.0.0",
        "psutil>=5.8.0"
    ]
    
    for package in remaining_packages:
        if not install_package(package):
            print(f"⚠️  Không thể cài đặt {package}, bỏ qua...")
            continue
    
    print("✅ Các dependencies còn lại đã được cài đặt")
    return True

def install_dev_dependencies():
    """Cài đặt các dependencies phát triển"""
    print_step("Cài đặt dependencies phát triển", "Cài đặt các tools phát triển (tùy chọn)")
    
    response = input("   Bạn có muốn cài đặt các tools phát triển không? (y/N): ").strip().lower()
    if response not in ['y', 'yes']:
        print("   ⏭️  Bỏ qua dependencies phát triển")
        return True
    
    dev_packages = [
        "pytest>=7.0.0",
        "pytest-cov>=4.0.0",
        "black>=22.0.0",
        "flake8>=5.0.0"
    ]
    
    for package in dev_packages:
        if not install_package(package):
            print(f"⚠️  Không thể cài đặt {package}, bỏ qua...")
            continue
    
    print("✅ Các dependencies phát triển đã được cài đặt")
    return True

def verify_installation():
    """Xác minh cài đặt"""
    print_step("Xác minh cài đặt", "Kiểm tra xem tất cả dependencies đã được cài đặt đúng chưa")
    
    try:
        # Import các packages chính
        import numpy
        import torch
        import customtkinter
        import whisper
        print("✅ Các packages chính có thể import được")
        
        # Kiểm tra phiên bản
        print(f"   📊 Numpy: {numpy.__version__}")
        print(f"   📊 PyTorch: {torch.__version__}")
        print(f"   📊 CustomTkinter: {customtkinter.__version__}")
        
        return True
    except ImportError as e:
        print(f"❌ Lỗi khi import packages: {e}")
        return False

def main():
    """Hàm chính"""
    print_header("AUTOMATIC DEPENDENCY INSTALLER")
    print("Cài đặt tất cả dependencies cho VoiceSub-Translator")
    
    # Kiểm tra điều kiện tiên quyết
    if not check_python_version():
        return
    
    if not check_virtual_environment():
        return
    
    # Sao lưu requirements.txt nếu cần
    backup_file = backup_requirements()
    
    try:
        # Nâng cấp pip
        if not upgrade_pip():
            print("❌ Không thể nâng cấp pip, dừng cài đặt")
            return
        
        # Cài đặt từng nhóm dependencies
        if not install_core_dependencies():
            print("❌ Không thể cài đặt dependencies cốt lõi")
            return
        
        if not install_ai_dependencies():
            print("❌ Không thể cài đặt dependencies AI")
            return
        
        if not install_gui_dependencies():
            print("❌ Không thể cài đặt dependencies GUI")
            return
        
        if not install_remaining_dependencies():
            print("⚠️  Một số dependencies không thể cài đặt")
        
        install_dev_dependencies()
        
        # Xác minh cài đặt
        if verify_installation():
            print_header("🎉 CÀI ĐẶT HOÀN TẤT")
            print("Tất cả dependencies đã được cài đặt thành công!")
            print("Bạn có thể chạy ứng dụng ngay bây giờ.")
        else:
            print_header("⚠️  CÀI ĐẶT KHÔNG HOÀN TẤT")
            print("Một số dependencies có thể chưa được cài đặt đúng.")
            print("Vui lòng kiểm tra lại và cài đặt thủ công nếu cần.")
    
    except KeyboardInterrupt:
        print("\n\n⚠️  Cài đặt bị gián đoạn bởi người dùng")
        print("Các packages đã cài đặt vẫn còn nguyên")
    
    except Exception as e:
        print(f"\n❌ Lỗi không mong muốn: {e}")
        print("Vui lòng kiểm tra lại và thử lại")
    
    finally:
        if backup_file:
            print(f"\n💾 File backup: {backup_file}")

if __name__ == "__main__":
    main()