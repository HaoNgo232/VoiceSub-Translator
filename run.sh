#!/bin/bash
# VoiceSub-Translator Run Script

cd "$(dirname "$0")"

if [ ! -d "venv" ]; then
    echo "❌ Virtual environment không tìm thấy. Vui lòng chạy setup.sh trước."
    exit 1
fi

echo "🚀 Khởi động VoiceSub-Translator..."
source venv/bin/activate

# Function to show user-friendly display setup instructions
show_display_instructions() {
    echo ""
    echo "============================================================"
    echo "🖥️  ỨNG DỤNG GUI - CẦN THIẾT LẬP DISPLAY"
    echo "============================================================"
    echo ""
    echo "Ứng dụng này cần display server để chạy giao diện đồ họa."
    echo ""
    echo "📋 HƯỚNG DẪN THIẾT LẬP:"
    echo ""
    echo "1️⃣  Cài đặt Xvfb (Virtual Display):"
    echo "   sudo apt-get update"
    echo "   sudo apt-get install -y xvfb"
    echo ""
    echo "2️⃣  Chạy ứng dụng với virtual display:"
    echo "   xvfb-run -a ./run.sh"
    echo ""
    echo "3️⃣  Hoặc thiết lập DISPLAY thủ công:"
    echo "   export DISPLAY=:99"
    echo "   Xvfb :99 -screen 0 1024x768x24 &"
    echo "   ./run.sh"
    echo ""
    echo "4️⃣  Để xem giao diện từ xa (nếu cần):"
    echo "   - Cài đặt VNC server"
    echo "   - Hoặc sử dụng X11 forwarding qua SSH"
    echo ""
    echo "💡 LƯU Ý:"
    echo "   - Ứng dụng này được thiết kế để chạy trên desktop"
    echo "   - Trong môi trường server, bạn có thể cần CLI alternative"
    echo ""
    echo "============================================================"
    echo ""
}

# Check if DISPLAY is available for GUI
if [ -z "$DISPLAY" ]; then
    echo "⚠️  DISPLAY không được thiết lập."
    show_display_instructions
    echo "Thử chạy ứng dụng anyway..."
    echo ""
fi

python run.py "$@"