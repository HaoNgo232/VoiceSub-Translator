@echo off

REM Kích hoạt môi trường ảo
call ..\venv\Scripts\activate

REM Cài đặt dependencies
pip install -r requirements.txt

REM Chạy tests
python -m pytest test_api_handler.py -v 