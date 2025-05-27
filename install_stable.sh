#!/bin/bash

# Script cài đặt tự động - CUDA Whisper Environment
# Đã test thành công với Ubuntu/Linux

set -e  # Dừng nếu có lỗi

echo "=================================================="
echo "CUDA WHISPER ENVIRONMENT SETUP"
echo "=================================================="

# Kiểm tra Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 không tìm thấy. Vui lòng cài đặt Python3 trước."
    exit 1
fi

echo "✅ Python3 found: $(python3 --version)"

# Tạo virtual environment nếu chưa có
if [ ! -d ".venv" ]; then
    echo "📦 Tạo virtual environment..."
    python3 -m venv .venv
fi

# Kích hoạt virtual environment
echo "🔄 Kích hoạt virtual environment..."
source .venv/bin/activate

# Upgrade pip
echo "⬆️  Upgrade pip..."
pip install --upgrade pip

# Bước 1: Core dependencies
echo "📋 [1/6] Cài đặt core dependencies..."
pip install numpy==1.26.4 filelock==3.18.0 typing-extensions==4.13.2 fsspec==2025.5.1

# Bước 2: PyTorch with CUDA
echo "🔥 [2/6] Cài đặt PyTorch với CUDA support..."
pip install torch==2.1.0 torchvision==0.16.0 torchaudio==2.1.0 --index-url https://download.pytorch.org/whl/cu118

# Bước 3: Triton (sau PyTorch)
echo "⚡ [3/6] Cài đặt Triton..."
pip install triton==2.1.0

# Bước 4: Whisper
echo "🎤 [4/6] Cài đặt Whisper models..."
pip install openai-whisper==20231117 faster-whisper==1.1.1

# Bước 5: Audio/Video processing
echo "🎵 [5/6] Cài đặt audio/video dependencies..."
pip install ffmpeg-python==0.2.0 audioread==3.0.1

# Bước 6: GUI và các thư viện khác
echo "🖥️  [6/6] Cài đặt GUI và utilities..."
pip install Pillow==11.2.1 anthropic==0.52.0 google-generativeai==0.8.5 groq==0.25.0 requests==2.32.3 python-dotenv coloredlogs==15.0.1

echo "=================================================="
echo "🧪 TESTING INSTALLATION..."
echo "=================================================="

# Test CUDA
echo "🔍 Testing CUDA availability..."
python3 -c "
import torch
print(f'✅ PyTorch version: {torch.__version__}')
print(f'✅ CUDA available: {torch.cuda.is_available()}')
if torch.cuda.is_available():
    print(f'✅ CUDA device: {torch.cuda.get_device_name(0)}')
    print(f'✅ CUDA device count: {torch.cuda.device_count()}')
else:
    print('⚠️  CUDA not available - will use CPU')
"

# Test Whisper
echo "🔍 Testing Whisper..."
python3 -c "
import whisper
print('✅ OpenAI Whisper import successful')
try:
    model = whisper.load_model('base.en', device='cuda' if __import__('torch').cuda.is_available() else 'cpu')
    print('✅ Whisper model loaded successfully')
except Exception as e:
    print(f'⚠️  Whisper model load warning: {e}')
"

# Test Faster Whisper
echo "🔍 Testing Faster Whisper..."
python3 -c "
try:
    import faster_whisper
    print('✅ Faster Whisper import successful')
except Exception as e:
    print(f'⚠️  Faster Whisper warning: {e}')
"

echo "=================================================="
echo "🎉 INSTALLATION COMPLETED!"
echo "=================================================="
echo ""
echo "📝 Versions installed:"
echo "   - PyTorch: 2.1.0+cu118"
echo "   - Triton: 2.1.0" 
echo "   - NumPy: 1.26.4"
echo "   - OpenAI Whisper: 20231117"
echo "   - Faster Whisper: 1.1.1"
echo ""
echo "🚀 To activate environment in future:"
echo "   source .venv/bin/activate"
echo ""
echo "🎯 To test your app:"
echo "   python3 src/gui/app.py"
echo ""
echo "=================================================="
