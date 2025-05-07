@echo off

REM Kích hoạt môi trường ảo
call venv\Scripts\activate.bat

REM Chạy tests với coverage
pytest tests/ -v --cov=src --cov-report=term-missing --cov-report=html

REM Hiển thị kết quả coverage
echo Coverage report đã được tạo trong thư mục htmlcov/ 