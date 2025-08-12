#!/bin/bash

# Script cài đặt giao diện hiện đại cho ứng dụng xử lý phụ đề
# Sử dụng CustomTkinter thay vì Tkinter cũ

echo "🎬 Cài đặt giao diện hiện đại cho ứng dụng xử lý phụ đề"
echo "=================================================="

# Kiểm tra Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 không được tìm thấy. Vui lòng cài đặt Python3 trước."
    exit 1
fi

echo "✅ Python3 đã được tìm thấy: $(python3 --version)"

# Kiểm tra pip
if ! command -v pip3 &> /dev/null; then
    echo "❌ pip3 không được tìm thấy. Vui lòng cài đặt pip3 trước."
    exit 1
fi

echo "✅ pip3 đã được tìm thấy: $(pip3 --version)"

# Cài đặt CustomTkinter
echo "📦 Đang cài đặt CustomTkinter..."
if pip3 install customtkinter>=5.2.0; then
    echo "✅ CustomTkinter đã được cài đặt thành công"
else
    echo "❌ Không thể cài đặt CustomTkinter. Vui lòng thử cài đặt thủ công:"
    echo "   pip3 install customtkinter>=5.2.0"
    exit 1
fi

# Cài đặt Pillow (nếu chưa có)
echo "📦 Đang cài đặt Pillow..."
if pip3 install pillow>=9.0.0; then
    echo "✅ Pillow đã được cài đặt thành công"
else
    echo "⚠️  Không thể cài đặt Pillow. Có thể đã được cài đặt sẵn."
fi

# Kiểm tra cài đặt
echo "🔍 Kiểm tra cài đặt..."
if python3 -c "import customtkinter; print('CustomTkinter version:', customtkinter.__version__)"; then
    echo "✅ CustomTkinter đã được cài đặt và hoạt động bình thường"
else
    echo "❌ Có vấn đề với cài đặt CustomTkinter"
    exit 1
fi

# Tạo file launcher có thể thực thi
echo "🔧 Tạo file launcher..."
chmod +x run_modern_gui.py

echo ""
echo "🎉 Cài đặt hoàn tất!"
echo "=================================================="
echo "Để chạy giao diện hiện đại, sử dụng một trong các cách sau:"
echo ""
echo "1. Sử dụng launcher tự động:"
echo "   python3 run_modern_gui.py"
echo ""
echo "2. Chạy trực tiếp:"
echo "   python3 src/gui/modern_app.py"
echo ""
echo "3. Chạy giao diện cũ (nếu cần):"
echo "   python3 src/gui/app.py"
echo ""
echo "📚 Xem hướng dẫn chi tiết trong file: MODERN_GUI_README.md"
echo ""
echo "🚀 Chúc bạn có trải nghiệm sử dụng tuyệt vời!"