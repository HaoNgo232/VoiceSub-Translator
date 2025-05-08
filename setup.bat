@echo off
setlocal enabledelayedexpansion

echo Bắt đầu quá trình cài đặt...

:: Kiểm tra Python version
echo.
echo Kiểm tra Python version...
python --version 2>NUL
if %ERRORLEVEL% EQU 0 (
    echo ✓ Python đã được cài đặt
) else (
    echo ✗ Python 3 chưa được cài đặt. Vui lòng cài đặt Python 3.8 trở lên.
    exit /b 1
)

:: Kiểm tra pip
echo.
echo Kiểm tra pip...
pip --version 2>NUL
if %ERRORLEVEL% EQU 0 (
    echo ✓ pip đã được cài đặt
) else (
    echo ✗ pip chưa được cài đặt. Vui lòng cài đặt pip.
    exit /b 1
)

:: Kiểm tra FFmpeg
echo.
echo Kiểm tra FFmpeg...
ffmpeg -version 2>NUL
if %ERRORLEVEL% EQU 0 (
    echo ✓ FFmpeg đã được cài đặt
) else (
    echo ✗ FFmpeg chưa được cài đặt. Vui lòng cài đặt FFmpeg.
    exit /b 1
)

:: Kiểm tra CUDA
echo.
echo Kiểm tra CUDA...
nvidia-smi 2>NUL
if %ERRORLEVEL% EQU 0 (
    echo ✓ CUDA đã được cài đặt
) else (
    echo ! CUDA chưa được cài đặt. Ứng dụng sẽ chạy trên CPU (chậm hơn).
)

:: Tạo môi trường ảo
echo.
echo Tạo môi trường ảo...
if not exist venv (
    python -m venv venv
    echo ✓ Đã tạo môi trường ảo
) else (
    echo ✓ Môi trường ảo đã tồn tại
)

:: Kích hoạt môi trường ảo
call venv\Scripts\activate.bat

:: Cài đặt dependencies
echo.
echo Cài đặt dependencies...
python -m pip install --upgrade pip
pip install -r requirements.txt

:: Tạo thư mục cần thiết
echo.
echo Tạo thư mục cần thiết...
if not exist cache mkdir cache
if not exist logs mkdir logs

:: Kiểm tra file .env
echo.
echo Kiểm tra file .env...
if not exist .env (
    if exist .env.example (
        copy .env.example .env
        echo ✓ Đã tạo file .env từ mẫu
        echo ! Vui lòng cập nhật các API keys trong file .env
    ) else (
        echo ✗ Không tìm thấy file .env.example
        exit /b 1
    )
) else (
    echo ✓ File .env đã tồn tại
)

echo.
echo Cài đặt hoàn tất!
echo Lưu ý:
echo 1. Vui lòng kiểm tra và cập nhật các API keys trong file .env
echo 2. Chạy tests để kiểm tra cài đặt: run_tests.bat
echo 3. Để chạy ứng dụng: python src/main.py

pause 