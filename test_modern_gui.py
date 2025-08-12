#!/usr/bin/env python3
"""
Test script cho giao diện hiện đại
Kiểm tra các chức năng cơ bản
"""

import sys
import os

# Thêm thư mục gốc vào đường dẫn Python
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

def test_imports():
    """Kiểm tra các import cần thiết"""
    print("🔍 Kiểm tra imports...")
    
    try:
        import customtkinter as ctk
        print(f"✅ CustomTkinter: {ctk.__version__}")
    except ImportError as e:
        print(f"❌ CustomTkinter: {e}")
        return False
    
    try:
        from src.gui.modern_app import ModernSubtitleApp
        print("✅ ModernSubtitleApp import thành công")
    except ImportError as e:
        print(f"❌ ModernSubtitleApp: {e}")
        return False
    
    try:
        from src.gui.components.modern_convert_dialog import ModernConvertDialog
        print("✅ ModernConvertDialog import thành công")
    except ImportError as e:
        print(f"❌ ModernConvertDialog: {e}")
        return False
    
    return True

def test_basic_functionality():
    """Kiểm tra chức năng cơ bản"""
    print("\n🔍 Kiểm tra chức năng cơ bản...")
    
    try:
        # Test tạo app instance
        from src.gui.modern_app import ModernSubtitleApp
        
        # Tạo app (không chạy mainloop)
        app = ModernSubtitleApp()
        print("✅ Tạo ModernSubtitleApp instance thành công")
        
        # Kiểm tra các thuộc tính cơ bản
        assert hasattr(app, 'root'), "App phải có thuộc tính root"
        assert hasattr(app, 'prompts'), "App phải có thuộc tính prompts"
        assert hasattr(app, 'input_folder'), "App phải có thuộc tính input_folder"
        print("✅ Các thuộc tính cơ bản đã được kiểm tra")
        
        # Đóng app
        app.root.destroy()
        print("✅ App đã được đóng thành công")
        
        return True
        
    except Exception as e:
        print(f"❌ Lỗi khi test chức năng cơ bản: {e}")
        return False

def test_dialog_imports():
    """Kiểm tra các dialog imports"""
    print("\n🔍 Kiểm tra dialog imports...")
    
    try:
        # Test các components
        from src.gui.components.progress_window import ProgressWindow
        print("✅ ProgressWindow import thành công")
        
        from src.gui.components.prompt_dialog import PromptDialog
        print("✅ PromptDialog import thành công")
        
        return True
        
    except ImportError as e:
        print(f"❌ Lỗi import components: {e}")
        return False

def main():
    """Hàm chính test"""
    print("🧪 Test giao diện hiện đại")
    print("=" * 50)
    
    # Test 1: Kiểm tra imports
    if not test_imports():
        print("\n❌ Test imports thất bại")
        return False
    
    # Test 2: Kiểm tra chức năng cơ bản
    if not test_basic_functionality():
        print("\n❌ Test chức năng cơ bản thất bại")
        return False
    
    # Test 3: Kiểm tra dialog imports
    if not test_dialog_imports():
        print("\n❌ Test dialog imports thất bại")
        return False
    
    print("\n🎉 Tất cả tests đã pass!")
    print("✅ Giao diện hiện đại đã sẵn sàng sử dụng")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)