#!/usr/bin/env python3
"""
Test script để kiểm tra requirements.txt
"""

import os
import sys

def test_requirements_file():
    """Kiểm tra file requirements.txt"""
    print("🔍 Kiểm tra file requirements.txt...")
    
    if not os.path.exists("requirements.txt"):
        print("❌ File requirements.txt không tồn tại")
        return False
    
    print("✅ File requirements.txt tồn tại")
    
    # Đọc và hiển thị nội dung
    with open("requirements.txt", "r", encoding="utf-8") as f:
        content = f.read()
    
    print(f"\n📋 Nội dung requirements.txt:")
    print("=" * 50)
    print(content)
    print("=" * 50)
    
    # Đếm số packages
    lines = [line.strip() for line in content.split('\n') if line.strip() and not line.startswith('#')]
    print(f"\n📊 Tổng số packages: {len(lines)}")
    
    return True

def test_pip_install():
    """Test lệnh pip install"""
    print("\n🔧 Test lệnh pip install...")
    
    try:
        import subprocess
        result = subprocess.run([
            sys.executable, "-m", "pip", "install", "--dry-run", "-r", "requirements.txt"
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ Lệnh pip install hoạt động bình thường")
            return True
        else:
            print("❌ Lệnh pip install có vấn đề")
            print(f"Lỗi: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ Không thể test pip install: {e}")
        return False

def main():
    """Hàm chính"""
    print("🧪 Test Requirements.txt")
    print("=" * 30)
    
    # Test file requirements.txt
    if not test_requirements_file():
        return
    
    # Test pip install
    if not test_pip_install():
        return
    
    print("\n🎉 Tất cả tests đã pass!")
    print("File requirements.txt hoạt động bình thường")

if __name__ == "__main__":
    main()