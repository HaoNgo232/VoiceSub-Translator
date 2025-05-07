@echo off
setlocal enabledelayedexpansion

:: Lưu thông tin hệ thống
echo === Thông tin hệ thống === > system_info.txt
echo OS: %OS% >> system_info.txt
echo Python version: >> system_info.txt
python --version >> system_info.txt 2>&1

:: Kiểm tra NVIDIA GPU và CUDA
echo CUDA version: >> system_info.txt
nvidia-smi | findstr "CUDA Version" >> system_info.txt 2>&1
echo GPU: >> system_info.txt
nvidia-smi --query-gpu=name --format=csv,noheader >> system_info.txt 2>&1
echo VRAM: >> system_info.txt
nvidia-smi --query-gpu=memory.total --format=csv,noheader >> system_info.txt 2>&1
echo ========================= >> system_info.txt

REM Kiểm tra Python
python --version >nul 2>&1
if errorlevel 1 (
    echo Python chưa được cài đặt. Vui lòng cài đặt Python trước.
    exit /b 1
)

REM Kiểm tra ffmpeg
ffmpeg -version >nul 2>&1
if errorlevel 1 (
    echo ffmpeg chưa được cài đặt. Vui lòng cài đặt ffmpeg trước.
    exit /b 1
)

:: Tạo và kích hoạt môi trường ảo
echo Tạo môi trường ảo Python...
python -m venv venv
call venv\Scripts\activate.bat

:: Cài đặt các thư viện
echo Cài đặt các thư viện cần thiết...
python -m pip install --upgrade pip
pip install -r requirements.txt

:: Kiểm tra cài đặt
echo Kiểm tra cài đặt...
python -c "import torch; print('PyTorch version:', torch.__version__); print('CUDA available:', torch.cuda.is_available()); print('GPU device:', torch.cuda.get_device_name(0) if torch.cuda.is_available() else 'None')" >> system_info.txt

REM Tạo thư mục output
if not exist output mkdir output

REM Tạo file .env
if not exist .env (
    echo GROQ_API_KEY=your_api_key_here > .env
    echo Đã tạo file .env. Vui lòng cập nhật API key của bạn.
)

echo Cài đặt hoàn tất! Kiểm tra file system_info.txt để xem thông tin chi tiết.
echo Để kích hoạt môi trường ảo, chạy: venv\Scripts\activate.bat
pause 