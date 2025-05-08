#!/bin/bash

# Màu sắc cho output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${GREEN}Bắt đầu quá trình cài đặt...${NC}"

# Kiểm tra Python version
echo -e "\n${YELLOW}Kiểm tra Python version...${NC}"
python_version=$(python3 --version 2>&1)
if [[ $python_version == *"Python 3"* ]]; then
    echo -e "${GREEN}✓ Python đã được cài đặt: $python_version${NC}"
else
    echo -e "${RED}✗ Python 3 chưa được cài đặt. Vui lòng cài đặt Python 3.8 trở lên.${NC}"
    exit 1
fi

# Kiểm tra pip
echo -e "\n${YELLOW}Kiểm tra pip...${NC}"
if command -v pip3 &> /dev/null; then
    echo -e "${GREEN}✓ pip đã được cài đặt${NC}"
else
    echo -e "${RED}✗ pip chưa được cài đặt. Vui lòng cài đặt pip.${NC}"
    exit 1
fi

# Kiểm tra FFmpeg
echo -e "\n${YELLOW}Kiểm tra FFmpeg...${NC}"
if command -v ffmpeg &> /dev/null; then
    echo -e "${GREEN}✓ FFmpeg đã được cài đặt${NC}"
else
    echo -e "${RED}✗ FFmpeg chưa được cài đặt. Vui lòng cài đặt FFmpeg.${NC}"
    exit 1
fi

# Kiểm tra CUDA
echo -e "\n${YELLOW}Kiểm tra CUDA...${NC}"
if command -v nvcc &> /dev/null; then
    echo -e "${GREEN}✓ CUDA đã được cài đặt${NC}"
    nvidia-smi
else
    echo -e "${YELLOW}! CUDA chưa được cài đặt. Ứng dụng sẽ chạy trên CPU (chậm hơn).${NC}"
fi

# Tạo môi trường ảo
echo -e "\n${YELLOW}Tạo môi trường ảo...${NC}"
if [ ! -d "venv" ]; then
    python3 -m venv venv
    echo -e "${GREEN}✓ Đã tạo môi trường ảo${NC}"
else
    echo -e "${GREEN}✓ Môi trường ảo đã tồn tại${NC}"
fi

# Kích hoạt môi trường ảo
source venv/bin/activate

# Cài đặt dependencies
echo -e "\n${YELLOW}Cài đặt dependencies...${NC}"
pip install --upgrade pip
pip install -r requirements.txt

# Tạo thư mục cần thiết
echo -e "\n${YELLOW}Tạo thư mục cần thiết...${NC}"
mkdir -p cache logs

# Kiểm tra file .env
echo -e "\n${YELLOW}Kiểm tra file .env...${NC}"
if [ ! -f ".env" ]; then
    if [ -f ".env.example" ]; then
        cp .env.example .env
        echo -e "${GREEN}✓ Đã tạo file .env từ mẫu${NC}"
        echo -e "${YELLOW}! Vui lòng cập nhật các API keys trong file .env${NC}"
    else
        echo -e "${RED}✗ Không tìm thấy file .env.example${NC}"
        exit 1
    fi
else
    echo -e "${GREEN}✓ File .env đã tồn tại${NC}"
fi

# Kiểm tra quyền thực thi
echo -e "\n${YELLOW}Cấp quyền thực thi cho scripts...${NC}"
chmod +x run_tests.sh
chmod +x setup.sh

echo -e "\n${GREEN}Cài đặt hoàn tất!${NC}"
echo -e "${YELLOW}Lưu ý:${NC}"
echo "1. Vui lòng kiểm tra và cập nhật các API keys trong file .env"
echo "2. Chạy tests để kiểm tra cài đặt: ./run_tests.sh"
echo "3. Để chạy ứng dụng: python src/main.py" 