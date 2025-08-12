#!/bin/bash

# VoiceSub-Translator Smart Installer
# Giải quyết vấn đề conflict thư viện và đơn giản hóa quá trình cài đặt

set -e  # Exit on any error

# Colors for better output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
PYTHON_VERSION="3.9"
VENV_NAME="venv"
PROJECT_NAME="VoiceSub-Translator"

# Function to print colored output
print_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_header() {
    echo -e "\n${BLUE}========================================${NC}"
    echo -e "${BLUE}  $1${NC}"
    echo -e "${BLUE}========================================${NC}"
}

# Function to check if command exists
command_exists() {
    command -v "$1" &> /dev/null
}

# Function to check Python version
check_python_version() {
    print_header "Kiểm tra phiên bản Python"
    
    if ! command_exists python3; then
        print_error "Python3 không được tìm thấy. Vui lòng cài đặt Python3 trước."
        exit 1
    fi
    
    PYTHON_VER=$(python3 -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
    print_info "Tìm thấy Python $PYTHON_VER"
    
    if [[ $(echo "$PYTHON_VER >= $PYTHON_VERSION" | bc -l) -eq 1 ]]; then
        print_success "Phiên bản Python $PYTHON_VER phù hợp"
    else
        print_warning "Phiên bản Python $PYTHON_VER có thể gây vấn đề. Khuyến nghị Python $PYTHON_VERSION+"
        if ! confirm "Tiếp tục với phiên bản hiện tại?"; then
            exit 1
        fi
    fi
}

# Function to get user confirmation
confirm() {
    read -p "$1 (y/n): " -n 1 -r
    echo
    [[ $REPLY =~ ^[Yy]$ ]]
}

# Function to clean existing environment
clean_environment() {
    print_header "Dọn dẹp môi trường cũ"
    
    if [ -d "$VENV_NAME" ]; then
        if confirm "Tìm thấy môi trường ảo cũ. Xóa và tạo mới?"; then
            print_info "Xóa môi trường ảo cũ..."
            rm -rf "$VENV_NAME"
            print_success "Đã xóa môi trường ảo cũ"
        else
            print_info "Giữ lại môi trường ảo cũ"
            return
        fi
    fi
    
    # Clean pip cache to avoid conflicts
    print_info "Dọn dẹp cache pip..."
    pip3 cache purge 2>/dev/null || true
    print_success "Đã dọn dẹp cache pip"
}

# Function to create virtual environment
create_venv() {
    print_header "Tạo môi trường ảo mới"
    
    print_info "Tạo môi trường ảo với Python $PYTHON_VERSION..."
    python3 -m venv "$VENV_NAME" || {
        print_error "Không thể tạo môi trường ảo"
        exit 1
    }
    
    print_success "Môi trường ảo đã được tạo"
}

# Function to activate virtual environment
activate_venv() {
    print_header "Kích hoạt môi trường ảo"
    
    print_info "Kích hoạt môi trường ảo..."
    source "$VENV_NAME/bin/activate" || {
        print_error "Không thể kích hoạt môi trường ảo"
        exit 1
    }
    
    # Upgrade pip to latest version
    print_info "Nâng cấp pip..."
    pip install --upgrade pip setuptools wheel || {
        print_warning "Không thể nâng cấp pip, tiếp tục với phiên bản hiện tại"
    }
    
    print_success "Môi trường ảo đã được kích hoạt"
}

# Function to install dependencies with conflict resolution
install_dependencies() {
    print_header "Cài đặt thư viện phụ thuộc"
    
    # Check if requirements.txt exists
    if [ ! -f "requirements.txt" ]; then
        print_error "Không tìm thấy file requirements.txt"
        exit 1
    fi
    
    print_info "Cài đặt các thư viện cơ bản trước..."
    
    # Install core dependencies first to avoid conflicts
    pip install torch==2.0.1 torchaudio==2.0.2 torchvision==0.15.2 --index-url https://download.pytorch.org/whl/cpu || {
        print_warning "Không thể cài đặt PyTorch với CUDA, thử cài đặt CPU version"
        pip install torch==2.0.1 torchaudio==2.0.2 torchvision==0.15.2 || {
            print_error "Không thể cài đặt PyTorch"
            exit 1
        }
    }
    
    print_success "PyTorch đã được cài đặt"
    
    # Install other dependencies
    print_info "Cài đặt các thư viện khác..."
    pip install -r requirements.txt || {
        print_error "Có lỗi khi cài đặt thư viện. Kiểm tra log để biết chi tiết."
        exit 1
    }
    
    print_success "Tất cả thư viện đã được cài đặt thành công"
}

# Function to verify installation
verify_installation() {
    print_header "Kiểm tra cài đặt"
    
    print_info "Kiểm tra các thư viện chính..."
    
    # Test core libraries
    python -c "
import torch
import whisper
import customtkinter
import PIL
print(f'✓ PyTorch: {torch.__version__}')
print(f'✓ Whisper: {whisper.__version__}')
print(f'✓ CustomTkinter: {customtkinter.__version__}')
print(f'✓ Pillow: {PIL.__version__}')
" || {
        print_error "Có vấn đề với một số thư viện"
        exit 1
    }
    
    print_success "Tất cả thư viện đã được cài đặt và hoạt động bình thường"
}

# Function to create launcher script
create_launcher() {
    print_header "Tạo script khởi chạy"
    
    cat > run_app.sh << 'EOF'
#!/bin/bash

# VoiceSub-Translator Launcher
# Script tự động kích hoạt môi trường và chạy ứng dụng

set -e

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${GREEN}🎬 VoiceSub-Translator${NC}"
echo "=================================="

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo -e "${RED}❌ Môi trường ảo không tồn tại. Vui chạy smart_install.sh trước.${NC}"
    exit 1
fi

# Activate virtual environment
echo "🔧 Kích hoạt môi trường ảo..."
source venv/bin/activate

# Check if dependencies are installed
if ! python -c "import torch, whisper, customtkinter" 2>/dev/null; then
    echo -e "${RED}❌ Thư viện chưa được cài đặt. Vui chạy smart_install.sh trước.${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Môi trường đã sẵn sàng${NC}"

# Choose which GUI to run
echo ""
echo "Chọn giao diện để chạy:"
echo "1. Giao diện hiện đại (CustomTkinter)"
echo "2. Giao diện cổ điển (Tkinter)"
echo "3. Chạy test đơn giản"
read -p "Nhập lựa chọn (1-3): " choice

case $choice in
    1)
        echo "🚀 Khởi chạy giao diện hiện đại..."
        python run_modern_gui.py
        ;;
    2)
        echo "🚀 Khởi chạy giao diện cổ điển..."
        python src/gui/app.py
        ;;
    3)
        echo "🧪 Chạy test đơn giản..."
        python simple_test.py
        ;;
    *)
        echo "❌ Lựa chọn không hợp lệ"
        exit 1
        ;;
esac
EOF
    
    chmod +x run_app.sh
    print_success "Script khởi chạy đã được tạo: run_app.sh"
}

# Function to show usage instructions
show_instructions() {
    print_header "Hướng dẫn sử dụng"
    
    echo -e "${GREEN}🎉 Cài đặt hoàn tất!${NC}"
    echo ""
    echo "Để chạy ứng dụng, sử dụng một trong các cách sau:"
    echo ""
    echo "1. ${YELLOW}Script tự động:${NC}"
    echo "   ./run_app.sh"
    echo ""
    echo "2. ${YELLOW}Thủ công:${NC}"
    echo "   source venv/bin/activate"
    echo "   python run_modern_gui.py  # Giao diện hiện đại"
    echo "   python src/gui/app.py     # Giao diện cổ điển"
    echo ""
    echo "3. ${YELLOW}Test nhanh:${NC}"
    echo "   source venv/bin/activate"
    echo "   python simple_test.py"
    echo ""
    echo "${BLUE}Lưu ý:${NC} Luôn kích hoạt môi trường ảo trước khi chạy ứng dụng!"
}

# Main installation function
main() {
    print_header "Bắt đầu cài đặt $PROJECT_NAME"
    
    check_python_version
    clean_environment
    create_venv
    activate_venv
    install_dependencies
    verify_installation
    create_launcher
    show_instructions
    
    print_header "Cài đặt hoàn tất!"
    echo -e "${GREEN}Bạn có thể chạy ./run_app.sh để khởi chạy ứng dụng${NC}"
}

# Run main function
main "$@"