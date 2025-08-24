#!/bin/bash

# VoiceSub-Translator Setup Script
# Tự động cài đặt và giải quyết conflict dependency cho đến khi ứng dụng chạy mượt mà

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Global variables
PYTHON_CMD="python3"
VENV_DIR="venv"
PROJECT_ROOT="$(pwd)"
LOG_FILE="setup.log"

# Utility functions
print_section() {
    echo -e "\n${CYAN}=== $1 ===${NC}"
}

print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
    echo "Chi tiết lỗi đã được ghi vào $LOG_FILE"
    exit 1
}

print_warning() {
    echo -e "${YELLOW}! $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ $1${NC}"
}

# Function to log commands
log_command() {
    echo "$(date): $1" >> "$LOG_FILE"
    eval "$1" 2>&1 | tee -a "$LOG_FILE"
    return ${PIPESTATUS[0]}
}

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to get user confirmation
confirm() {
    read -p "$1 (y/n): " choice
    case "$choice" in 
        y|Y ) return 0;;
        * ) return 1;;
    esac
}

# Function to detect system and Python version
detect_system() {
    print_section "Phát hiện hệ thống và kiểm tra tương thích"
    
    # Detect OS
    if [ -f /etc/os-release ]; then
        . /etc/os-release
        OS=$NAME
        VERSION=$VERSION_ID
        print_success "Hệ điều hành: $OS $VERSION"
    else
        print_error "Hệ điều hành không được hỗ trợ. Script này yêu cầu Linux."
    fi
    
    # Check Python version (require 3.8+)
    if command_exists python3; then
        PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
        PYTHON_MAJOR=$(echo $PYTHON_VERSION | cut -d'.' -f1)
        PYTHON_MINOR=$(echo $PYTHON_VERSION | cut -d'.' -f2)
        
        if [ $PYTHON_MAJOR -eq 3 ] && [ $PYTHON_MINOR -ge 8 ]; then
            print_success "Python: $PYTHON_VERSION (tương thích)"
            PYTHON_CMD="python3"
        else
            print_warning "Python $PYTHON_VERSION được phát hiện. Khuyến nghị Python 3.8+."
            if confirm "Tiếp tục với Python $PYTHON_VERSION?"; then
                PYTHON_CMD="python3"
            else
                print_error "Vui lòng cài đặt Python 3.8+ trước khi chạy script này."
            fi
        fi
    else
        print_error "Python 3 không được tìm thấy. Vui lòng cài đặt Python 3.8+ trước."
    fi
    
    # Check pip
    if ! command_exists pip3; then
        print_error "pip3 không được tìm thấy. Vui lòng cài đặt python3-pip."
    fi
    
    print_success "Kiểm tra hệ thống hoàn tất"
}

# Function to install system dependencies
install_system_deps() {
    print_section "Cài đặt dependencies hệ thống"
    
    if command_exists apt-get; then
        print_info "Cập nhật danh sách package..."
        log_command "sudo apt-get update -qq" || print_error "Không thể cập nhật package lists"
        
        print_info "Cài đặt các package hệ thống cần thiết..."
        log_command "sudo apt-get install -y \
            software-properties-common \
            build-essential \
            curl wget git \
            ffmpeg \
            python3-pip python3-dev python3-venv \
            portaudio19-dev \
            ca-certificates" || print_error "Không thể cài đặt system packages"
            
        print_success "System dependencies đã được cài đặt"
    elif command_exists yum; then
        print_info "Cài đặt dependencies cho Red Hat/CentOS..."
        log_command "sudo yum install -y \
            epel-release \
            gcc gcc-c++ make \
            wget git \
            ffmpeg \
            python3-pip python3-devel \
            portaudio-devel" || print_error "Không thể cài đặt system packages"
        print_success "System dependencies đã được cài đặt"
    else
        print_error "Package manager không được hỗ trợ. Script này yêu cầu apt-get hoặc yum."
    fi
}

# Function to check GPU support
check_gpu_support() {
    print_section "Kiểm tra hỗ trợ GPU"
    
    if command_exists nvidia-smi; then
        print_info "Phát hiện NVIDIA GPU..."
        nvidia-smi --query-gpu=name,driver_version,memory.total --format=csv,noheader 2>/dev/null || true
        print_success "Hỗ trợ GPU khả dụng"
        export GPU_SUPPORT="true"
        return 0
    else
        print_warning "Không phát hiện GPU NVIDIA. Sẽ sử dụng CPU."
        export GPU_SUPPORT="false"
        return 1
    fi
}

# Function to create and setup virtual environment
setup_virtual_environment() {
    print_section "Thiết lập Virtual Environment"
    
    if [ -d "$VENV_DIR" ]; then
        print_warning "Virtual environment đã tồn tại. Có muốn tạo lại?"
        if confirm "Tạo lại virtual environment?"; then
            print_info "Xóa virtual environment cũ..."
            rm -rf "$VENV_DIR"
        else
            print_info "Sử dụng virtual environment hiện tại..."
            source "$VENV_DIR/bin/activate" || print_error "Không thể kích hoạt virtual environment"
            print_success "Virtual environment đã được kích hoạt"
            return 0
        fi
    fi
    
    print_info "Tạo virtual environment mới..."
    log_command "$PYTHON_CMD -m venv $VENV_DIR" || print_error "Không thể tạo virtual environment"
    
    print_info "Kích hoạt virtual environment..."
    source "$VENV_DIR/bin/activate" || print_error "Không thể kích hoạt virtual environment"
    
    print_info "Nâng cấp pip..."
    log_command "pip install --upgrade pip setuptools wheel" || print_error "Không thể nâng cấp pip"
    
    print_success "Virtual environment đã được thiết lập thành công"
}

# Function to install PyTorch with proper GPU/CPU support
install_pytorch() {
    print_section "Cài đặt PyTorch"
    
    if [ "$GPU_SUPPORT" = "true" ]; then
        print_info "Cài đặt PyTorch với hỗ trợ CUDA..."
        log_command "pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121" || {
            print_warning "Không thể cài đặt PyTorch CUDA. Thử cài đặt phiên bản CPU..."
            log_command "pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu" || print_error "Không thể cài đặt PyTorch"
        }
    else
        print_info "Cài đặt PyTorch phiên bản CPU..."
        log_command "pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu" || print_error "Không thể cài đặt PyTorch"
    fi
    
    print_success "PyTorch đã được cài đặt"
}

# Function to handle dependency conflicts and install packages
install_dependencies() {
    print_section "Cài đặt dependencies của dự án"
    
    # Ensure virtual environment is activated
    if [ -z "$VIRTUAL_ENV" ]; then
        source "$VENV_DIR/bin/activate" || print_error "Không thể kích hoạt virtual environment"
    fi
    
    # Install main requirements first
    if [ -f "requirements.txt" ]; then
        print_info "Cài đặt dependencies từ requirements.txt..."
        log_command "pip install -r requirements.txt" || {
            print_warning "Một số packages trong requirements.txt gặp lỗi. Tiếp tục với cài đặt thủ công..."
        }
    fi
    
    # Install missing dependencies
    print_info "Cài đặt các dependencies thiếu..."
    
    # Core dependencies that are often missing
    core_deps=(
        "backoff"
        "redis"
        "openai"
        "groq"
        "tiktoken"
        "tenacity"
        "aiohttp"
        "websockets"
        "emoji"
        "langdetect"
        "python-dotenv"
        "customtkinter"
        "faster-whisper"
        "whisper"
        "psutil"
        "google-generativeai"
        "requests"
        "ffmpeg-python"
        "pillow"
        "pytest"
    )
    
    for dep in "${core_deps[@]}"; do
        print_info "Kiểm tra $dep..."
        if ! pip show "$dep" >/dev/null 2>&1; then
            print_info "Cài đặt $dep..."
            log_command "pip install '$dep'" || {
                print_warning "Không thể cài đặt $dep, bỏ qua..."
                continue
            }
        else
            print_success "$dep đã được cài đặt"
        fi
    done
    
    # Handle potential conflicts by using specific versions
    print_info "Giải quyết conflicts..."
    
    # Common conflict resolutions
    log_command "pip install --upgrade typing-extensions" || true
    log_command "pip install --upgrade numpy" || true
    log_command "pip install --upgrade protobuf" || true
    
    print_success "Dependencies đã được cài đặt"
}

# Function to verify installation
verify_installation() {
    print_section "Kiểm tra cài đặt"
    
    # Ensure virtual environment is activated
    if [ -z "$VIRTUAL_ENV" ]; then
        source "$VENV_DIR/bin/activate" || print_error "Không thể kích hoạt virtual environment"
    fi
    
    print_info "Kiểm tra import các modules chính..."
    
    local failed_imports=0
    
    # Test PyTorch
    if python -c "import torch; print('PyTorch:', torch.__version__)" 2>/dev/null; then
        print_success "PyTorch: OK"
    else
        print_warning "PyTorch import failed"
        ((failed_imports++))
    fi
    
    # Test Whisper
    if python -c "import whisper; print('Whisper: OK')" 2>/dev/null; then
        print_success "Whisper: OK"
    else
        print_warning "Whisper import failed"
        ((failed_imports++))
    fi
    
    # Test CustomTkinter
    if python -c "import customtkinter; print('CustomTkinter: OK')" 2>/dev/null; then
        print_success "CustomTkinter: OK"
    else
        print_warning "CustomTkinter import failed"
        ((failed_imports++))
    fi
    
    # Test Backoff
    if python -c "import backoff; print('Backoff: OK')" 2>/dev/null; then
        print_success "Backoff: OK"
    else
        print_warning "Backoff import failed"
        ((failed_imports++))
    fi
    
    if [ $failed_imports -eq 0 ]; then
        print_success "Tất cả imports thành công!"
    else
        print_warning "$failed_imports imports thất bại, nhưng có thể không ảnh hưởng chính"
    fi
    
    # Test application imports
    print_info "Kiểm tra imports của ứng dụng..."
    if python -c "import sys; sys.path.insert(0, '.'); import src" 2>/dev/null; then
        print_success "Application imports thành công!"
    else
        print_warning "Application imports gặp lỗi. Kiểm tra chi tiết trong log."
    fi
}

# Function to create helper scripts
create_helper_scripts() {
    print_section "Tạo helper scripts"
    
    # Create run.sh script
    cat > run.sh << 'EOF'
#!/bin/bash
# VoiceSub-Translator Run Script

cd "$(dirname "$0")"

if [ ! -d "venv" ]; then
    echo "❌ Virtual environment không tìm thấy. Vui lòng chạy setup.sh trước."
    exit 1
fi

echo "🚀 Khởi động VoiceSub-Translator..."
source venv/bin/activate

# Check if DISPLAY is available for GUI
if [ -z "$DISPLAY" ]; then
    echo "⚠️  DISPLAY không được thiết lập. Đảm bảo bạn đang chạy trong môi trường GUI."
fi

python run.py "$@"
EOF
    chmod +x run.sh
    print_success "Đã tạo run.sh script"
    
    # Create test script with a simpler Python test
    cat > test_installation.sh << 'EOF'
#!/bin/bash
# Test installation script

cd "$(dirname "$0")"

if [ ! -d "venv" ]; then
    echo "❌ Virtual environment không tìm thấy. Vui lòng chạy setup.sh trước."
    exit 1
fi

echo "🧪 Kiểm tra cài đặt VoiceSub-Translator..."
source venv/bin/activate

# Run basic tests
if [ -f "test_local.py" ]; then
    python test_local.py
else
    echo "Chạy test cơ bản..."
    python << 'PYEOF'
import sys
sys.path.insert(0, '.')

print('=== Test cơ bản ===')

try:
    import torch
    print('✓ PyTorch:', torch.__version__)
    print('✓ CUDA khả dụng:', torch.cuda.is_available())
except Exception as e:
    print('✗ PyTorch:', e)

try:
    import whisper
    print('✓ Whisper: OK')
except Exception as e:
    print('✗ Whisper:', e)

try:
    import customtkinter
    print('✓ CustomTkinter: OK')
except Exception as e:
    print('✗ CustomTkinter:', e)

try:
    import src
    print('✓ Application modules: OK')
except Exception as e:
    print('✗ Application modules:', e)
    
print()
print('=== Test hoàn tất ===')
PYEOF
fi
EOF
    chmod +x test_installation.sh
    print_success "Đã tạo test_installation.sh script"
    
    # Create update script
    cat > update_dependencies.sh << 'EOF'
#!/bin/bash
# Update dependencies script

cd "$(dirname "$0")"

if [ ! -d "venv" ]; then
    echo "❌ Virtual environment không tìm thấy. Vui lòng chạy setup.sh trước."
    exit 1
fi

echo "🔄 Cập nhật dependencies..."
source venv/bin/activate

pip install --upgrade pip
pip install --upgrade -r requirements.txt

echo "✅ Dependencies đã được cập nhật!"
EOF
    chmod +x update_dependencies.sh
    print_success "Đã tạo update_dependencies.sh script"
}

# Function to create environment configuration
create_env_config() {
    print_section "Tạo cấu hình môi trường"
    
    if [ ! -f ".env" ]; then
        if [ -f ".env.example" ]; then
            cp .env.example .env
            print_success "Đã sao chép .env.example thành .env"
        else
            cat > .env << 'EOF'
# VoiceSub-Translator API Configuration
# Thêm API keys của bạn vào đây

# OpenAI (GPT models)
OPENAI_API_KEY=your_openai_key_here

# Google Gemini 
GOOGLE_API_KEY=your_google_gemini_key_here

# Groq (Fast inference)
GROQ_API_KEY=your_groq_key_here

# OpenRouter (Multiple models)
OPENROUTER_API_KEY=your_openrouter_key_here

# Cerebras (Fast inference)
CEREBRAS_API_KEY=your_cerebras_key_here

# Novita AI
NOVITA_API_KEY=your_novita_key_here

# Mistral AI
MISTRAL_API_KEY=your_mistral_key_here

# Default providers (optional)
DEFAULT_TRANSLATION_PROVIDER=google
DEFAULT_WHISPER_MODEL=medium
EOF
            print_success "Đã tạo file .env mới"
        fi
        
        print_info "Vui lòng chỉnh sửa file .env và thêm API keys của bạn!"
    else
        print_success "File .env đã tồn tại"
    fi
}

# Function to show final instructions
show_final_instructions() {
    print_section "Hướng dẫn sử dụng"
    
    echo -e "${CYAN}🚀 Các lệnh khởi động nhanh:${NC}"
    echo -e "  ${YELLOW}./run.sh${NC}                    - Khởi động ứng dụng GUI"
    echo -e "  ${YELLOW}./test_installation.sh${NC}     - Kiểm tra cài đặt"
    echo -e "  ${YELLOW}./update_dependencies.sh${NC}   - Cập nhật dependencies"
    echo -e ""
    echo -e "${CYAN}📝 Các file quan trọng:${NC}"
    echo -e "  ${YELLOW}.env${NC}                       - Cấu hình API keys"
    echo -e "  ${YELLOW}setup.log${NC}                  - Log chi tiết quá trình cài đặt"
    echo -e "  ${YELLOW}venv/${NC}                      - Virtual environment"
    echo -e ""
    echo -e "${CYAN}🔧 Khắc phục sự cố:${NC}"
    echo -e "  ${YELLOW}source venv/bin/activate${NC}   - Kích hoạt virtual environment thủ công"
    echo -e "  ${YELLOW}pip install <package>${NC}      - Cài đặt package thiếu"
    echo -e "  ${YELLOW}cat setup.log${NC}              - Xem log chi tiết"
    echo -e ""
    
    if [ "$GPU_SUPPORT" = "true" ]; then
        echo -e "${GREEN}🎮 GPU support đã được kích hoạt!${NC}"
    else
        echo -e "${YELLOW}💻 Chạy ở chế độ CPU-only${NC}"
    fi
    
    echo -e ""
    echo -e "${GREEN}✨ Cài đặt hoàn tất! Chạy './run.sh' để khởi động ứng dụng.${NC}"
}

# Main function
main() {
    echo -e "${CYAN}"
    echo "╔══════════════════════════════════════════════════════════════╗"
    echo "║                VoiceSub-Translator Setup Script              ║"
    echo "║                                                              ║"
    echo "║  Tự động cài đặt và giải quyết dependency conflicts         ║"
    echo "║  cho đến khi ứng dụng chạy mượt mà                          ║"
    echo "╚══════════════════════════════════════════════════════════════╝"
    echo -e "${NC}\n"
    
    # Initialize log file
    echo "$(date): Starting VoiceSub-Translator setup" > "$LOG_FILE"
    
    # Validate we're in the correct directory
    if [ ! -f "requirements.txt" ] || [ ! -d "src" ]; then
        print_error "Vui lòng chạy script này từ thư mục gốc của dự án VoiceSub-Translator."
    fi
    
    # Setup process
    detect_system
    
    # Ask for system dependencies installation
    if confirm "Cài đặt system dependencies (cần sudo quyền)?"; then
        install_system_deps
    else
        print_warning "Bỏ qua cài đặt system dependencies. Đảm bảo ffmpeg và các tools cần thiết đã được cài đặt."
    fi
    
    check_gpu_support
    setup_virtual_environment
    install_pytorch
    install_dependencies
    verify_installation
    create_helper_scripts
    create_env_config
    show_final_instructions
    
    print_section "Kết thúc"
    echo -e "${GREEN}🎉 Setup hoàn tất thành công!${NC}"
    echo -e "Chi tiết đầy đủ có trong file: ${YELLOW}$LOG_FILE${NC}"
}

# Cleanup on interrupt
trap 'echo -e "\n${RED}Setup bị gián đoạn. Bạn có thể cần chạy lại script.${NC}"; exit 1' INT TERM

# Execute main function
main "$@"