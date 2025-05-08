#!/bin/bash

# Tạo môi trường ảo nếu chưa tồn tại
if [ ! -d "venv" ]; then
    python3 -m venv venv
fi

# Kích hoạt môi trường ảo
source venv/bin/activate

# Cài đặt các dependencies
pip install -r requirements.txt
pip install pytest pytest-cov

# Chạy tests với coverage
pytest tests/ -v --cov=src --cov-report=term-missing

# Tắt môi trường ảo
deactivate

# Kiểm tra kết quả
if [ $? -eq 0 ]; then
    echo "All tests passed successfully!"
else
    echo "Some tests failed!"
    exit 1
fi

# Hiển thị kết quả coverage
echo "Coverage report đã được tạo trong thư mục htmlcov/" 