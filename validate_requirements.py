#!/usr/bin/env python3
"""
Validate Requirements.txt
Kiểm tra cú pháp và format của file requirements.txt
"""

import re
import os

def validate_package_line(line: str, line_num: int) -> tuple[bool, str]:
    """Validate một dòng package trong requirements.txt"""
    line = line.strip()
    
    # Bỏ qua comment và dòng trống
    if not line or line.startswith('#'):
        return True, ""
    
    # Pattern cho package name và version spec
    # Ví dụ: package>=1.0.0, package==1.0.0, package
    pattern = r'^([a-zA-Z0-9_-]+)([<>=!~]+[0-9a-zA-Z._-]+)?$'
    
    match = re.match(pattern, line)
    if not match:
        return False, f"Dòng {line_num}: Format không hợp lệ - '{line}'"
    
    package_name = match.group(1)
    version_spec = match.group(2) if match.group(2) else ""
    
    # Kiểm tra package name
    if not package_name or len(package_name) < 1:
        return False, f"Dòng {line_num}: Tên package không hợp lệ - '{package_name}'"
    
    # Kiểm tra version spec nếu có
    if version_spec:
        version_pattern = r'^[<>=!~]+[0-9a-zA-Z._-]+$'
        if not re.match(version_pattern, version_spec):
            return False, f"Dòng {line_num}: Version spec không hợp lệ - '{version_spec}'"
    
    return True, ""

def validate_requirements_file(file_path: str = "requirements.txt") -> tuple[bool, list[str]]:
    """Validate toàn bộ file requirements.txt"""
    errors = []
    
    if not os.path.exists(file_path):
        errors.append(f"File {file_path} không tồn tại")
        return False, errors
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        print(f"📋 Đang validate {len(lines)} dòng trong {file_path}...")
        
        for i, line in enumerate(lines, 1):
            is_valid, error_msg = validate_package_line(line, i)
            if not is_valid:
                errors.append(error_msg)
        
        return len(errors) == 0, errors
        
    except Exception as e:
        errors.append(f"Lỗi khi đọc file: {e}")
        return False, errors

def analyze_requirements(file_path: str = "requirements.txt"):
    """Phân tích file requirements.txt"""
    if not os.path.exists(file_path):
        print(f"❌ File {file_path} không tồn tại")
        return
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        lines = content.split('\n')
        
        # Thống kê
        total_lines = len(lines)
        comment_lines = sum(1 for line in lines if line.strip().startswith('#'))
        empty_lines = sum(1 for line in lines if not line.strip())
        package_lines = total_lines - comment_lines - empty_lines
        
        print(f"📊 Thống kê file {file_path}:")
        print(f"   Tổng số dòng: {total_lines}")
        print(f"   Dòng comment: {comment_lines}")
        print(f"   Dòng trống: {empty_lines}")
        print(f"   Dòng package: {package_lines}")
        
        # Phân loại packages
        packages = []
        for line in lines:
            line = line.strip()
            if line and not line.startswith('#'):
                package_name = line.split('>=')[0].split('==')[0].split('<=')[0].split('!=')[0].split('~=')[0].strip()
                packages.append(package_name)
        
        print(f"\n📦 Danh sách packages ({len(packages)}):")
        for i, package in enumerate(packages, 1):
            print(f"   {i:2d}. {package}")
        
        return packages
        
    except Exception as e:
        print(f"❌ Lỗi khi phân tích file: {e}")
        return []

def main():
    """Hàm chính"""
    print("🔍 Validate Requirements.txt")
    print("=" * 40)
    
    # Validate file
    is_valid, errors = validate_requirements_file()
    
    if is_valid:
        print("✅ File requirements.txt hợp lệ!")
    else:
        print("❌ File requirements.txt có lỗi:")
        for error in errors:
            print(f"   {error}")
    
    print()
    
    # Phân tích file
    packages = analyze_requirements()
    
    print()
    if is_valid:
        print("🎉 Validation hoàn tất thành công!")
        print(f"📦 Tổng cộng {len(packages)} packages đã được định nghĩa")
    else:
        print("⚠️  Vui lòng sửa các lỗi trước khi sử dụng")

if __name__ == "__main__":
    main()