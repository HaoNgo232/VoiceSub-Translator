@echo off
rem Script để quản lý phụ đề gốc trên Windows
rem Sử dụng:
rem   manage_subtitles.bat -i C:\đường\dẫn\đến\thư\mục\video [options]

rem Chuyển đến thư mục gốc của dự án
cd /d "%~dp0"

rem Kích hoạt môi trường ảo nếu tồn tại
if exist venv\Scripts\activate.bat (
    call venv\Scripts\activate.bat
)

rem Chạy script Python với các tham số được chuyển tiếp
python -m src.scripts.manage_subtitles %*

rem Hiển thị hướng dẫn nếu không có tham số
if "%~1"=="" (
    echo Cách sử dụng:
    echo   manage_subtitles.bat -i C:\đường\dẫn\thư\mục\video [options]
    echo.
    echo Các tùy chọn:
    echo   -i, --input    Thư mục đầu vào chứa video và phụ đề (bắt buộc^)
    echo   -b, --backup   Thư mục backup (mặc định: '<input_folder>/backup_subtitles'^)
    echo   -l, --lang     Ngôn ngữ đích của bản dịch (mặc định: 'vi'^)
    echo   -r, --restore  Khôi phục phụ đề gốc từ thư mục backup
    echo.
    echo Ví dụ:
    echo   manage_subtitles.bat -i Videos -b Subtitles_Backup -l vi
    echo   manage_subtitles.bat -i Videos -r
) 