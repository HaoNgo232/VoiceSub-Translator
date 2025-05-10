#!/bin/bash

# Colors for better readability
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}===========================================================${NC}"
echo -e "${BLUE}   VoiceSub-Translator Automated Setup Script              ${NC}"
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

# Function to detect the Linux distribution
detect_distro() {
    print_section "Detecting Linux Distribution"
    
    if [ -f /etc/os-release ]; then
        . /etc/os-release
        OS=$NAME
        VERSION=$VERSION_ID
        print_success "Detected: $OS $VERSION"
    elif command_exists lsb_release; then
        OS=$(lsb_release -si)
        VERSION=$(lsb_release -sr)
        print_success "Detected: $OS $VERSION"
    elif [ -f /etc/lsb-release ]; then
        . /etc/lsb-release
        OS=$DISTRIB_ID
        VERSION=$DISTRIB_RELEASE
        print_success "Detected: $OS $VERSION"
    else
        OS="Unknown"
        print_warning "Could not detect Linux distribution. Assuming Debian/Ubuntu compatible."
    fi
}

# Function to check and install system dependencies
install_system_deps() {
    print_section "Installing System Dependencies"
    
    if command_exists apt-get; then
        echo "Updating system package lists..."
        sudo apt-get update -qq || print_error "Failed to update package lists"
        
        echo "Installing required system packages..."
        sudo apt-get install -y software-properties-common build-essential \
            curl wget git ffmpeg python3-pip python3-dev || print_error "Failed to install system packages"
        print_success "System dependencies installed"
    else
        print_error "Unsupported package manager. This script requires apt-get."
    fi
}

# Function to install Python 3.9.9
install_python() {
    print_section "Setting up Python 3.9.9"
    
    if command_exists python3.9 && python3.9 --version | grep -q "3.9.9"; then
        print_success "Python 3.9.9 is already installed"
    else
        echo "Installing Python 3.9.9..."
        sudo add-apt-repository -y ppa:deadsnakes/ppa || print_error "Failed to add deadsnakes PPA"
        sudo apt-get update -qq
        sudo apt-get install -y python3.9 python3.9-venv python3.9-dev || print_error "Failed to install Python 3.9.9"
        print_success "Python 3.9.9 installed successfully"
    fi
}

# Function to set up virtual environment
setup_venv() {
    print_section "Setting up Virtual Environment"
    
    if [ -d "venv" ]; then
        if confirm "Virtual environment 'venv' already exists. Do you want to recreate it?"; then
            echo "Removing existing virtual environment..."
            rm -rf venv
        else
            print_success "Using existing virtual environment"
            return
        fi
    fi
    
    echo "Creating virtual environment with Python 3.9.9..."
    python3.9 -m venv venv || print_error "Failed to create virtual environment"
    print_success "Virtual environment created successfully"
}

# Function to activate virtual environment
activate_venv() {
    echo "Activating virtual environment..."
    source venv/bin/activate || print_error "Failed to activate virtual environment"
    print_success "Virtual environment activated"
}

# Function to check CUDA availability
check_cuda() {
    print_section "Checking CUDA Availability"
    
    if command_exists nvidia-smi; then
        echo "NVIDIA GPU detected. Checking CUDA installation..."
        if command_exists nvcc; then
            CUDA_VERSION=$(nvcc --version | grep "release" | awk '{print $6}' | cut -c2-)
            print_success "CUDA $CUDA_VERSION is installed"
            return 0
        else
            print_warning "NVIDIA GPU detected but CUDA is not installed or not in PATH."
            if confirm "Would you like to see instructions for installing CUDA?"; then
                echo -e "\nTo install CUDA, visit: https://developer.nvidia.com/cuda-11-8-0-download-archive"
                echo "Follow the instructions for your specific OS version."
            fi
            return 1
        fi
    else
        print_warning "No NVIDIA GPU detected. Whisper will run in CPU mode (very slow)."
        if confirm "Continue without GPU acceleration?"; then
            return 1
        else
            print_error "Setup aborted. Please install an NVIDIA GPU or configure CUDA before running this script again."
        fi
    fi
}

# Function to install PyTorch with CUDA support
install_pytorch() {
    print_section "Installing PyTorch with CUDA Support"
    
    echo "Upgrading pip, setuptools, and wheel..."
    pip install --upgrade pip setuptools wheel || print_error "Failed to upgrade pip"
    
    if check_cuda; then
        echo "Installing PyTorch with CUDA support..."
        pip install torch==2.0.1 torchaudio==2.0.2 torchvision==0.15.2 --index-url https://download.pytorch.org/whl/cu118 || print_error "Failed to install PyTorch"
    else
        echo "Installing PyTorch without CUDA support..."
        pip install torch==2.0.1 torchaudio==2.0.2 torchvision==0.15.2 || print_error "Failed to install PyTorch"
    fi
    
    print_success "PyTorch installed successfully"
}

# Function to install project dependencies
install_project_deps() {
    print_section "Installing Project Dependencies"
    
    echo "Installing requirements from requirements.txt..."
    pip install -r requirements.txt || print_error "Failed to install dependencies from requirements.txt"
    
    echo "Installing project in development mode..."
    pip install -e . || print_error "Failed to install project in development mode"
    
    print_success "Project dependencies installed successfully"
}

# Function to verify installation
verify_installation() {
    print_section "Verifying Installation"
    
    echo "Checking Whisper installation..."
    if python -c "import whisper; print(f'Whisper {whisper.__version__} successfully installed')"; then
        print_success "Whisper installation verified"
    else
        print_error "Whisper installation verification failed"
    fi
    
    echo "Checking CUDA availability for PyTorch..."
    if python -c "import torch; print(f'CUDA available: {torch.cuda.is_available()}'); print(f'Device: {torch.cuda.get_device_name(0) if torch.cuda.is_available() else \"CPU\"}')"; then
        print_success "PyTorch installation verified"
    else
        print_error "PyTorch installation verification failed"
    fi
}

# Function to display API setup instructions
show_api_instructions() {
    print_section "API Setup Instructions"
    
    echo -e "To use the translation features, you need to set up API keys."
    echo -e "Create a file named '.env' in the project root with the following content:"
    echo -e "\n# API Keys for Translation Providers"
    echo -e "OPENAI_API_KEY=your_openai_key_here"
    echo -e "GOOGLE_API_KEY=your_google_gemini_key_here"
    echo -e "MISTRAL_API_KEY=your_mistral_key_here"
    echo -e "GROQ_API_KEY=your_groq_key_here"
    echo -e "OPENROUTER_API_KEY=your_openrouter_key_here"
    echo -e "CEREBRAS_API_KEY=your_cerebras_key_here"
    echo -e "NOVITA_API_KEY=your_novita_key_here"
    echo -e "\n# Optional: Set default providers"
    echo -e "DEFAULT_TRANSLATION_PROVIDER=google  # Options: novita, google, mistral, groq, openrouter, cerebras"
    
    echo -e "\nRefer to the README.md file for more information on obtaining API keys."
}

# Main script execution
main() {
    detect_distro
    install_system_deps
    install_python
    setup_venv
    activate_venv
    install_pytorch
    install_project_deps
    verify_installation
    show_api_instructions
    
    echo -e "\n${GREEN}===========================================================${NC}"
    echo -e "${GREEN}   VoiceSub-Translator setup completed successfully!        ${NC}"
    echo -e "${GREEN}===========================================================${NC}"
    echo -e "\nTo start the application, run: ${YELLOW}source venv/bin/activate && python src/gui/app.py${NC}"
    echo -e "\nThank you for using VoiceSub-Translator!"
}

# Execute main function
main