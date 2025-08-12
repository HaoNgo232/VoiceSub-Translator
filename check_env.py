#!/usr/bin/env python3
"""
Environment Checker for VoiceSub-Translator
Kiểm tra môi trường và dependencies
"""

import os
import sys
import importlib.util
import subprocess

def print_header(title):
    """In tiêu đề với định dạng đẹp"""
    print(f"\n{'='*50}")
    print(f"  {title}")
    print(f"{'='*50}")

def print_status(message, status):
    """In trạng thái với emoji"""
    emoji = "✅" if status else "❌"
    print(f"{emoji} {message}")

def check_python_version():
    """Kiểm tra phiên bản Python"""
    print_header("Kiểm tra Python")
    
    version = sys.version_info
    print(f"Phiên bản hiện tại: {version.major}.{version.minor}.{version.micro}")
    
    is_compatible = version.major >= 3 and version.minor >= 8
    print_status("Phiên bản Python phù hợp", is_compatible)
    
    if not is_compatible:
        print("⚠️  Khuyến nghị: Python 3.8+")
    
    return is_compatible

def check_venv():
    """Kiểm tra môi trường ảo"""
    print_header("Kiểm tra môi trường ảo")
    
    # Kiểm tra xem có đang trong venv không
    in_venv = hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix)
    print_status("Đang trong môi trường ảo", in_venv)
    
    if in_venv:
        print(f"   Môi trường: {sys.prefix}")
    
    # Kiểm tra thư mục venv
    venv_exists = os.path.exists("venv")
    print_status("Thư mục venv tồn tại", venv_exists)
    
    return in_venv and venv_exists

def check_dependencies():
    """Kiểm tra dependencies"""
    print_header("Kiểm tra thư viện phụ thuộc")
    
    dependencies = {
        'torch': 'PyTorch (AI framework)',
        'whisper': 'OpenAI Whisper (Speech recognition)',
        'customtkinter': 'CustomTkinter (Modern GUI)',
        'PIL': 'Pillow (Image processing)',
        'numpy': 'NumPy (Numerical computing)',
        'requests': 'Requests (HTTP library)',
        'openai': 'OpenAI API client',
        'google.generativeai': 'Google Gemini API',
        'mistralai': 'Mistral AI API'
    }
    
    missing = []
    installed = []
    
    for module, description in dependencies.items():
        if importlib.util.find_spec(module) is None:
            missing.append(module)
        else:
            installed.append(module)
            # Lấy phiên bản nếu có thể
            try:
                mod = importlib.import_module(module)
                if hasattr(mod, '__version__'):
                    print(f"   {module}: {mod.__version__} - {description}")
                else:
                    print(f"   {module}: ✓ - {description}")
            except:
                print(f"   {module}: ✓ - {description}")
    
    print_status(f"Đã cài đặt {len(installed)}/{len(dependencies)} thư viện", len(missing) == 0)
    
    if missing:
        print(f"\n❌ Thiếu: {', '.join(missing)}")
        print("   Chạy: ./smart_install.sh để cài đặt")
    
    return len(missing) == 0

def check_system_deps():
    """Kiểm tra system dependencies"""
    print_header("Kiểm tra system dependencies")
    
    system_deps = {
        'ffmpeg': 'FFmpeg (Audio/video processing)',
        'python3': 'Python 3',
        'pip': 'Pip (Package manager)'
    }
    
    all_available = True
    
    for cmd, description in system_deps.items():
        try:
            result = subprocess.run([cmd, '--version'], capture_output=True, text=True)
            if result.returncode == 0:
                version = result.stdout.split('\n')[0]
                print(f"   {cmd}: {version} - {description}")
            else:
                print(f"   {cmd}: ❌ - {description}")
                all_available = False
        except FileNotFoundError:
            print(f"   {cmd}: ❌ - {description}")
            all_available = False
    
    print_status("System dependencies", all_available)
    return all_available

def check_gui_apps():
    """Kiểm tra các ứng dụng GUI có sẵn"""
    print_header("Kiểm tra ứng dụng GUI")
    
    gui_apps = [
        ("run_modern_gui.py", "Giao diện hiện đại"),
        ("src/gui/modern_app.py", "Giao diện hiện đại"),
        ("src/gui/app.py", "Giao diện cổ điển"),
        ("simple_test.py", "Test đơn giản")
    ]
    
    available = []
    for app_path, description in gui_apps:
        if os.path.exists(app_path):
            available.append(f"{app_path} ({description})")
            print(f"   ✓ {app_path} - {description}")
        else:
            print(f"   ❌ {app_path} - {description}")
    
    print_status(f"Tìm thấy {len(available)} ứng dụng GUI", len(available) > 0)
    return len(available) > 0

def generate_report():
    """Tạo báo cáo tổng quan"""
    print_header("BÁO CÁO TỔNG QUAN")
    
    checks = [
        ("Python version", check_python_version()),
        ("Virtual environment", check_venv()),
        ("Dependencies", check_dependencies()),
        ("System dependencies", check_system_deps()),
        ("GUI applications", check_gui_apps())
    ]
    
    passed = sum(1 for _, status in checks if status)
    total = len(checks)
    
    print(f"\n📊 Kết quả: {passed}/{total} kiểm tra thành công")
    
    if passed == total:
        print("🎉 Môi trường đã sẵn sàng! Chạy: python run_app.py")
    else:
        print("⚠️  Có vấn đề với môi trường. Vui lòng khắc phục trước khi chạy ứng dụng.")
        print("💡 Gợi ý: Chạy ./smart_install.sh để thiết lập môi trường")

def main():
    print("🔍 VoiceSub-Translator Environment Checker")
    print("Kiểm tra môi trường và dependencies")
    
    generate_report()

if __name__ == "__main__":
    main()