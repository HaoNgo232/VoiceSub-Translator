#!/bin/bash

# VoiceSub-Translator Quick Runner
# Script chạy ứng dụng nhanh chóng

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${GREEN}🚀 VoiceSub-Translator Quick Runner${NC}"
echo "======================================"

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo -e "${RED}❌ Môi trường ảo không tồn tại!${NC}"
    echo ""
    echo "Vui lòng chạy cài đặt trước:"
    echo "   ./smart_install.sh"
    exit 1
fi

# Activate virtual environment
echo "🔧 Kích hoạt môi trường ảo..."
source venv/bin/activate

# Check if dependencies are installed
echo "🔍 Kiểm tra thư viện..."
if ! python -c "import torch, whisper, customtkinter" 2>/dev/null; then
    echo -e "${RED}❌ Thư viện chưa được cài đặt!${NC}"
    echo ""
    echo "Vui lòng chạy cài đặt trước:"
    echo "   ./smart_install.sh"
    exit 1
fi

echo -e "${GREEN}✅ Môi trường đã sẵn sàng${NC}"

# Auto-detect and run the best available GUI
echo ""
echo "🔍 Tự động phát hiện giao diện tốt nhất..."

if [ -f "run_modern_gui.py" ]; then
    echo "🚀 Khởi chạy giao diện hiện đại..."
    python run_modern_gui.py
elif [ -f "src/gui/modern_app.py" ]; then
    echo "🚀 Khởi chạy giao diện hiện đại..."
    python src/gui/modern_app.py
elif [ -f "src/gui/app.py" ]; then
    echo "🚀 Khởi chạy giao diện cổ điển..."
    python src/gui/app.py
else
    echo -e "${YELLOW}⚠️  Không tìm thấy giao diện chính, chạy test...${NC}"
    python simple_test.py
fi
