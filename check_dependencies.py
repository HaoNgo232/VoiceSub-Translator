#!/usr/bin/env python3
"""
Dependency Checker for VoiceSub-Translator
Kiểm tra và báo cáo trạng thái của tất cả dependencies
"""

import os
import sys
import importlib.util
import subprocess
from typing import Dict, List, Tuple

def print_header(title: str):
    """In tiêu đề với định dạng đẹp"""
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}")

def check_package_import(package_name: str) -> Tuple[bool, str]:
    """Kiểm tra xem package có thể import được không"""
    try:
        # Xử lý các trường hợp đặc biệt
        if package_name == 'PIL':
            import PIL
            return True, PIL.__version__
        elif package_name == 'ffmpeg':
            # Kiểm tra ffmpeg command line tool
            result = subprocess.run(['ffmpeg', '-version'], 
                                 capture_output=True, text=True)
            if result.returncode == 0:
                version_line = result.stdout.split('\n')[0]
                return True, version_line
            else:
                return False, "Not found"
        else:
            mod = importlib.import_module(package_name)
            if hasattr(mod, '__version__'):
                return True, mod.__version__
            else:
                return True, "Installed (no version info)"
    except ImportError:
        return False, "Not installed"
    except Exception as e:
        return False, f"Error: {str(e)}"

def get_requirements_packages() -> List[str]:
    """Đọc danh sách packages từ requirements.txt"""
    packages = []
    if os.path.exists("requirements.txt"):
        with open("requirements.txt", "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and not line.startswith("torch-cuda"):
                    # Lấy tên package từ dòng (loại bỏ version spec)
                    package = line.split(">=")[0].split("==")[0].split("<=")[0].strip()
                    if package:
                        packages.append(package)
    return packages

def check_all_dependencies():
    """Kiểm tra tất cả dependencies"""
    print_header("KIỂM TRA DEPENDENCIES")
    
    # Lấy danh sách packages từ requirements.txt
    required_packages = get_requirements_packages()
    
    if not required_packages:
        print("❌ Không thể đọc requirements.txt")
        return
    
    print(f"📋 Tìm thấy {len(required_packages)} packages cần kiểm tra")
    print()
    
    # Kiểm tra từng package
    results = []
    for package in required_packages:
        status, version = check_package_import(package)
        results.append((package, status, version))
        
        status_icon = "✅" if status else "❌"
        print(f"{status_icon} {package:<20} : {version}")
    
    # Tóm tắt
    print()
    print_header("TÓM TẮT")
    installed = sum(1 for _, status, _ in results if status)
    total = len(results)
    
    print(f"📊 Tổng số packages: {total}")
    print(f"✅ Đã cài đặt: {installed}")
    print(f"❌ Chưa cài đặt: {total - installed}")
    
    if total - installed > 0:
        print(f"\n🔧 Để cài đặt tất cả dependencies, chạy:")
        print(f"   pip install -r requirements.txt")
        
        print(f"\n📦 Các packages cần cài đặt:")
        for package, status, _ in results:
            if not status:
                print(f"   - {package}")
    
    return results

def check_python_version():
    """Kiểm tra phiên bản Python"""
    print_header("THÔNG TIN PYTHON")
    print(f"🐍 Python version: {sys.version}")
    print(f"📍 Python executable: {sys.executable}")
    print(f"📁 Working directory: {os.getcwd()}")

def check_virtual_environment():
    """Kiểm tra môi trường ảo"""
    print_header("MÔI TRƯỜNG ẢO")
    if hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
        print("✅ Đang chạy trong môi trường ảo")
        print(f"   Base prefix: {sys.base_prefix}")
        print(f"   Current prefix: {sys.prefix}")
    else:
        print("❌ Không chạy trong môi trường ảo")
        print("   Khuyến nghị: Kích hoạt môi trường ảo trước khi cài đặt dependencies")

def main():
    """Hàm chính"""
    print("🔍 VoiceSub-Translator Dependency Checker")
    print("Kiểm tra trạng thái của tất cả dependencies")
    
    # Kiểm tra thông tin cơ bản
    check_python_version()
    check_virtual_environment()
    
    # Kiểm tra dependencies
    results = check_all_dependencies()
    
    # Kết luận
    print_header("KẾT LUẬN")
    if results:
        installed = sum(1 for _, status, _ in results if status)
        total = len(results)
        
        if installed == total:
            print("🎉 Tất cả dependencies đã được cài đặt thành công!")
            print("   Bạn có thể chạy ứng dụng ngay bây giờ.")
        else:
            print("⚠️  Một số dependencies chưa được cài đặt.")
            print("   Vui lòng cài đặt trước khi chạy ứng dụng.")
    else:
        print("❌ Không thể kiểm tra dependencies.")
        print("   Vui lòng kiểm tra file requirements.txt")

if __name__ == "__main__":
    main()