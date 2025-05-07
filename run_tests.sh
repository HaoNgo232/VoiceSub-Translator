#!/bin/bash

# Kích hoạt môi trường ảo
source venv/bin/activate

# Chạy tests với coverage
pytest tests/ -v --cov=src --cov-report=term-missing --cov-report=html

# Hiển thị kết quả coverage
echo "Coverage report đã được tạo trong thư mục htmlcov/" 