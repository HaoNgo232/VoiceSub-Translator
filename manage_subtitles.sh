#!/bin/bash

# Script để quản lý phụ đề gốc
# Sử dụng:
#   ./manage_subtitles.sh -i /đường/dẫn/đến/thư/mục/video [options]

# Chuyển đến thư mục gốc của dự án
cd "$(dirname "$0")"

# Kích hoạt môi trường ảo nếu tồn tại
if [ -d "venv" ]; then
    source venv/bin/activate
fi

# Chạy script Python với các tham số được chuyển tiếp
python -m src.scripts.manage_subtitles "$@"

# Hiển thị hướng dẫn nếu không có tham số
if [ $# -eq 0 ]; then
    echo "Cách sử dụng:"
    echo "  ./manage_subtitles.sh -i /đường/dẫn/thư/mục/video [options]"
    echo ""
    echo "Các tùy chọn:"
    echo "  -i, --input    Thư mục đầu vào chứa video và phụ đề (bắt buộc)"
    echo "  -b, --backup   Thư mục backup (mặc định: '<input_folder>/backup_subtitles')"
    echo "  -l, --lang     Ngôn ngữ đích của bản dịch (mặc định: 'vi')"
    echo "  -r, --restore  Khôi phục phụ đề gốc từ thư mục backup"
    echo ""
    echo "Ví dụ:"
    echo "  ./manage_subtitles.sh -i Videos -b Subtitles_Backup -l vi"
    echo "  ./manage_subtitles.sh -i Videos -r"
fi 