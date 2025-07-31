#!/bin/bash

# VoiceSub-Translator Setup Script v2.0
# Updated for Python 3.10+ with GPU support and modern dependencies
# Follows SOLID principles with separated concerns

# Colors for better readability
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
PURPLE='\033[0;35m'
NC='\033[0m' # No Color

echo -e "${BLUE}===========================================================${NC}"
echo -e "${BLUE}   VoiceSub-Translator Setup Script v2.0                   ${NC}"
echo -e "${BLUE}   Updated with GPU Support & Modern Dependencies          ${NC}"
echo -e "${BLUE}===========================================================${NC}"

# Function to check if a command exists
command_exists() {
    command -v "$1" &> /dev/null
}

# Function to print section headers
print_section() {
    echo -e "\n${YELLOW}[$1]${NC}"
}

# Function to print success message
print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

# Function to print error message and exit
print_error() {
    echo -e "${RED}✗ $1${NC}"
    exit 1
}

# Function to print warning
print_warning() {
    echo -e "${YELLOW}! $1${NC}"
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
    print_section "System Detection & Compatibility Check"
    
    # Detect OS
    if [ -f /etc/os-release ]; then
        . /etc/os-release
        OS=$NAME
        VERSION=$VERSION_ID
        print_success "OS: $OS $VERSION"
    else
        print_error "Unsupported operating system. This script requires Linux with systemd."
    fi
    
    # Check Python version (require 3.10+)
    if command_exists python3; then
        PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
        PYTHON_MAJOR=$(echo $PYTHON_VERSION | cut -d'.' -f1)
        PYTHON_MINOR=$(echo $PYTHON_VERSION | cut -d'.' -f2)
        
        if [ $PYTHON_MAJOR -eq 3 ] && [ $PYTHON_MINOR -ge 10 ]; then
            print_success "Python: $PYTHON_VERSION (compatible)"
            PYTHON_CMD="python3"
        else
            print_warning "Python $PYTHON_VERSION detected. Python 3.10+ recommended."
            if confirm "Continue with Python $PYTHON_VERSION?"; then
                PYTHON_CMD="python3"
            else
                print_error "Please install Python 3.10+ before running this script."
            fi
        fi
    else
        print_error "Python 3 not found. Please install Python 3.10+ first."
    fi
}

# Function to install system dependencies (Simplified)
install_system_deps() {
    print_section "Installing System Dependencies"
    
    if command_exists apt-get; then
        echo "Updating system package lists..."
        sudo apt-get update -qq || print_error "Failed to update package lists"
        
        echo "Installing core system packages..."
        sudo apt-get install -y \
            software-properties-common \
            build-essential \
            curl wget git \
            ffmpeg \
            python3-pip python3-dev python3-venv \
            alsa-utils pulseaudio \
            ca-certificates || print_error "Failed to install system packages"
            
        print_success "System dependencies installed"
    else
        print_error "Unsupported package manager. This script requires apt-get (Ubuntu/Debian)."
    fi
}

# Function to check GPU support (Simplified)
check_gpu_support() {
    print_section "GPU Support Detection"
    
    if command_exists nvidia-smi; then
        echo "NVIDIA GPU detected..."
        nvidia-smi --query-gpu=name,driver_version,memory.total --format=csv,noheader
        
        print_success "GPU support available"
        export GPU_SUPPORT="true"
        return 0
    else
        print_warning "No NVIDIA GPU detected. Whisper will run in CPU mode (slower)."
        if confirm "Continue without GPU acceleration?"; then
            export GPU_SUPPORT="false"
            return 1
        else
            print_error "Setup aborted. Install NVIDIA drivers first."
        fi
    fi
}

# Function to set up virtual environment (Consistent naming)
setup_venv() {
    print_section "Setting up Virtual Environment"
    
    VENV_DIR="venv"  # Consistent with our successful setup
    
    if [ -d "$VENV_DIR" ]; then
        if confirm "Virtual environment '$VENV_DIR' already exists. Recreate it?"; then
            echo "Removing existing virtual environment..."
            rm -rf "$VENV_DIR"
        else
            print_success "Using existing virtual environment"
            return 0
        fi
    fi
    
    echo "Creating virtual environment with $PYTHON_CMD..."
    $PYTHON_CMD -m venv "$VENV_DIR" || print_error "Failed to create virtual environment"
    print_success "Virtual environment created successfully"
    
    # Activate and upgrade core tools
    echo "Activating virtual environment and upgrading core tools..."
    source "$VENV_DIR/bin/activate" || print_error "Failed to activate virtual environment"
    pip install --upgrade pip setuptools wheel || print_error "Failed to upgrade core tools"
    print_success "Virtual environment ready"
}

# Function to install PyTorch with optimal CUDA support
install_pytorch() {
    print_section "Installing PyTorch with CUDA Support"
    
    echo "Activating virtual environment..."
    source venv/bin/activate || print_error "Failed to activate virtual environment"
    
    # Check if GPU support was detected earlier
    if [ "$GPU_SUPPORT" = "true" ]; then
        echo "Installing PyTorch 2.3.1 with CUDA 12.1 support..."
        # Using index-url that worked in our testing
        pip install torch==2.3.1 torchvision==0.18.1 torchaudio==2.3.1 --index-url https://download.pytorch.org/whl/cu121 || print_error "Failed to install PyTorch with CUDA"
        print_success "PyTorch with CUDA support installed"
    else
        echo "Installing PyTorch CPU-only version..."
        pip install torch==2.3.1 torchvision==0.18.1 torchaudio==2.3.1 --index-url https://download.pytorch.org/whl/cpu || print_error "Failed to install PyTorch CPU"
        print_success "PyTorch CPU version installed"
    fi
}

# Function to install project dependencies (Dependency Inversion)
install_project_deps() {
    print_section "Installing Project Dependencies"
    
    echo "Activating virtual environment..."
    source venv/bin/activate || print_error "Failed to activate virtual environment"
    
    if [ ! -f "requirements.txt" ]; then
        print_error "requirements.txt not found. Please ensure you're in the project root directory."
    fi
    
    echo "Installing project dependencies from requirements.txt..."
    pip install -r requirements.txt || print_error "Failed to install dependencies from requirements.txt"
    
    print_success "Project dependencies installed successfully"
}

# Function to verify installation (Interface Segregation)
verify_installation() {
    print_section "Verifying Installation"
    
    echo "Activating virtual environment for verification..."
    source venv/bin/activate || print_error "Failed to activate virtual environment"
    
    # Test imports
    echo "Testing core imports..."
    if python -c "
import sys
print(f'Python version: {sys.version}')

import torch
print(f'PyTorch version: {torch.__version__}')
print(f'CUDA available: {torch.cuda.is_available()}')
if torch.cuda.is_available():
    print(f'GPU device: {torch.cuda.get_device_name()}')
    print(f'GPU count: {torch.cuda.device_count()}')

import whisper
print('OpenAI Whisper: ✓')

from faster_whisper import WhisperModel
print('Faster Whisper: ✓')

import openai
print(f'OpenAI client: {openai.__version__}')

print('🎉 All core components verified successfully!')
"; then
        print_success "Installation verification passed"
    else
        print_error "Installation verification failed"
    fi
    
    # Test GPU functionality if available
    echo "Testing GPU functionality..."
    if python -c "
import torch
if torch.cuda.is_available():
    device = torch.device('cuda')
    x = torch.randn(100, 100).to(device)
    y = torch.randn(100, 100).to(device)
    z = torch.matmul(x, y)
    print(f'✓ GPU tensor operations successful')
    print(f'✓ GPU memory used: {torch.cuda.memory_allocated() / 1024**2:.2f} MB')
else:
    print('⚠ GPU not available, will use CPU')
"; then
        print_success "GPU functionality test passed"
    else
        print_warning "GPU functionality test failed, but CPU mode will work"
    fi
}

# Function to create convenient run scripts
create_run_scripts() {
    print_section "Creating Convenience Scripts"
    
    # Create run.sh script
    cat > run.sh << 'EOF'
#!/bin/bash
# VoiceSub-Translator Quick Run Script
cd "$(dirname "$0")"

if [ ! -d "venv" ]; then
    echo "❌ Virtual environment not found. Please run setup.sh first."
    echo "   ./setup.sh"
    exit 1
fi

echo "🚀 Starting VoiceSub-Translator..."
source venv/bin/activate
python src/gui/app.py "$@"
EOF
    chmod +x run.sh
    print_success "Created run.sh script"
    
    # Create test script
    cat > test_installation.sh << 'EOF'
#!/bin/bash
# Test installation script
cd "$(dirname "$0")"

if [ ! -d "venv" ]; then
    echo "❌ Virtual environment not found. Please run setup.sh first."
    exit 1
fi

echo "🧪 Testing VoiceSub-Translator installation..."
source venv/bin/activate
python test_local.py
EOF
    chmod +x test_installation.sh
    print_success "Created test_installation.sh script"
}

# Function to display usage instructions (Simplified)
show_usage_instructions() {
    print_section "Usage Instructions"
    
    echo -e "${CYAN}🚀 Quick Start Commands:${NC}"
    echo -e "  ${YELLOW}./run.sh${NC}                    - Start the GUI application"
    echo -e "  ${YELLOW}./test_installation.sh${NC}      - Test the installation"
    echo -e "  ${YELLOW}source venv/bin/activate${NC}    - Activate virtual environment manually"
    echo -e ""
    echo -e "${CYAN} Project Structure:${NC}"
    echo -e "  ${YELLOW}src/gui/app.py${NC}              - Main GUI application"
    echo -e "  ${YELLOW}src/api/${NC}                    - API integration modules"
    echo -e "  ${YELLOW}src/processor/${NC}              - Audio/video processing"
    echo -e "  ${YELLOW}src/translator/${NC}             - Translation services"
    echo -e "  ${YELLOW}venv/${NC}                       - Virtual environment (isolated)"
}

# Function to display API setup instructions (Enhanced)
show_api_instructions() {
    print_section "API Configuration"
    
    echo -e "${CYAN}📝 API Keys Setup:${NC}"
    echo -e "Create a ${YELLOW}.env${NC} file in the project root with your API keys:"
    echo -e ""
    cat > .env.example << 'EOF'
# VoiceSub-Translator API Configuration
# Copy this file to .env and add your actual API keys

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
    
    print_success "Created .env.example template"
    echo -e "${YELLOW}Copy .env.example to .env and add your actual API keys${NC}"
    echo -e ""
    echo -e "${CYAN}📚 API Documentation:${NC}"
    echo -e "  Check the ${YELLOW}Providers API Docs/${NC} folder for detailed setup instructions"
}

# Main script execution (Simplified for Virtual Environment focus)
main() {
    echo -e "${PURPLE}Starting VoiceSub-Translator setup process...${NC}\n"
    
    # Phase 1: System Detection & Validation
    detect_system
    
    # Phase 2: GPU Detection (before any virtual environment setup)
    check_gpu_support
    
    # Phase 3: System Dependencies
    install_system_deps
    
    # Phase 4: Virtual Environment Setup (isolated from system)
    setup_venv
    
    # Phase 5: PyTorch Installation (Core ML Framework)
    install_pytorch
    
    # Phase 6: Project Dependencies
    install_project_deps
    
    # Phase 7: Verification
    verify_installation
    
    # Phase 8: Convenience & Documentation
    create_run_scripts
    show_api_instructions
    show_usage_instructions
    
    echo -e "\n${GREEN}===========================================================${NC}"
    echo -e "${GREEN}   🎉 VoiceSub-Translator setup completed successfully!  ${NC}"
    echo -e "${GREEN}===========================================================${NC}"
    echo -e "${CYAN}📋 Summary:${NC}"
    echo -e "  ✅ Python environment: $(python3 --version)"
    echo -e "  ✅ Virtual environment: venv/ (isolated)"
    echo -e "  ✅ GPU support: $(nvidia-smi &>/dev/null && echo "NVIDIA GPU detected" || echo "CPU only")"
    echo -e "  ✅ Dependencies: Installed in virtual environment"
    echo -e "  ✅ Scripts: run.sh, test_installation.sh"
    echo -e ""
    echo -e "${YELLOW}🚀 Quick start: ./run.sh${NC}"
    echo -e "${YELLOW}🧪 Test setup: ./test_installation.sh${NC}"
    echo -e ""
    echo -e "Thank you for using VoiceSub-Translator! 🎬🗣️→📝"
}

# Error handling and cleanup
trap 'echo -e "\n${RED}Setup interrupted. You may need to run the script again.${NC}"; exit 1' INT TERM

# Validate we're in the correct directory
if [ ! -f "requirements.txt" ] || [ ! -d "src" ]; then
    print_error "Please run this script from the VoiceSub-Translator project root directory."
fi

# Execute main function
main "$@"