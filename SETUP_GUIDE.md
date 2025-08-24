# VoiceSub-Translator Setup Guide

## Cài đặt tự động với setup.sh

Script `setup.sh` sẽ tự động cài đặt và giải quyết tất cả dependency conflicts cho đến khi ứng dụng chạy mượt mà.

### Cách sử dụng

```bash
# Tải về hoặc clone repository
git clone https://github.com/HaoNgo232/VoiceSub-Translator.git
cd VoiceSub-Translator

# Chạy script setup tự động
./setup.sh
```

### Tính năng của setup.sh

- ✅ **Tự động phát hiện hệ thống** và kiểm tra tương thích Python 3.8+
- ✅ **Cài đặt system dependencies** (ffmpeg, build tools, etc.)
- ✅ **Phát hiện GPU** và cài đặt PyTorch phù hợp (CUDA/CPU)
- ✅ **Tạo virtual environment** để tránh conflicts
- ✅ **Giải quyết dependency conflicts** tự động
- ✅ **Cài đặt missing dependencies** (backoff, redis, etc.)
- ✅ **Tạo helper scripts** (run.sh, test_installation.sh)
- ✅ **Cấu hình môi trường** (.env file)
- ✅ **Kiểm tra cài đặt** và verify imports

### Dependencies được giải quyết

Script tự động cài đặt các packages thiếu:

```
backoff              # Retry logic với exponential backoff
redis                # Redis client
openai               # OpenAI API
groq                 # Groq API  
tiktoken             # Tokenizer cho OpenAI
tenacity             # Retry utilities
aiohttp              # Async HTTP client
websockets           # WebSocket support
emoji                # Emoji support
langdetect           # Language detection
python-dotenv        # Environment variables
customtkinter        # Modern GUI
faster-whisper       # Fast speech recognition
whisper              # OpenAI Whisper
psutil               # System utilities
google-generativeai  # Google Gemini API
requests             # HTTP client
ffmpeg-python        # FFmpeg wrapper
pillow               # Image processing
pytest               # Testing framework
```

### Helper Scripts được tạo

Sau khi chạy setup.sh, bạn sẽ có các scripts tiện ích:

```bash
# Khởi động ứng dụng
./run.sh

# Kiểm tra cài đặt
./test_installation.sh

# Cập nhật dependencies
./update_dependencies.sh
```

### Cấu trúc sau khi setup

```
VoiceSub-Translator/
├── venv/                    # Virtual environment
├── setup.sh                # Setup script
├── run.sh                  # Run script
├── test_installation.sh    # Test script
├── update_dependencies.sh  # Update script
├── .env                    # Environment config
├── setup.log              # Setup log
└── ...
```

### Khắc phục sự cố

#### Lỗi permissions
```bash
chmod +x setup.sh
sudo ./setup.sh
```

#### Lỗi network timeout
```bash
# Thử lại với timeout lớn hơn
pip install --timeout 1000 -r requirements.txt
```

#### Lỗi missing system packages
```bash
# Ubuntu/Debian
sudo apt-get update
sudo apt-get install ffmpeg python3-dev build-essential

# CentOS/RHEL  
sudo yum install epel-release
sudo yum install ffmpeg python3-devel gcc
```

#### Manual activation
```bash
source venv/bin/activate
pip install -r requirements.txt
python run.py
```

### Logs và debugging

- Xem log chi tiết: `cat setup.log`
- Test imports: `./test_installation.sh`
- Activate environment: `source venv/bin/activate`

### GPU Support

Script tự động phát hiện GPU và cài đặt:
- **NVIDIA GPU**: PyTorch với CUDA support
- **No GPU**: PyTorch CPU-only version

### Môi trường được hỗ trợ

- **OS**: Ubuntu/Debian, CentOS/RHEL
- **Python**: 3.8+ (recommended 3.10+)
- **GPU**: NVIDIA CUDA (optional)
- **RAM**: Minimum 4GB (8GB+ recommended)
- **Storage**: 5GB+ free space

---

## Cài đặt thủ công (nếu cần)

Nếu script tự động gặp vấn đề, bạn có thể cài đặt thủ công:

```bash
# 1. Tạo virtual environment
python3 -m venv venv
source venv/bin/activate

# 2. Upgrade pip
pip install --upgrade pip setuptools wheel

# 3. Cài đặt PyTorch
pip install torch torchvision torchaudio

# 4. Cài đặt dependencies
pip install -r requirements.txt

# 5. Cài đặt missing packages
pip install backoff redis openai groq

# 6. Test installation
python -c "import src; print('✓ Application ready')"

# 7. Run application
python run.py
```

### API Keys Configuration

Sau khi cài đặt, cấu hình API keys trong file `.env`:

```bash
# Copy example config
cp .env.example .env

# Edit với API keys của bạn
nano .env
```

Required API keys:
- `OPENAI_API_KEY` - For GPT models
- `GOOGLE_API_KEY` - For Gemini models  
- `GROQ_API_KEY` - For fast inference
- `OPENROUTER_API_KEY` - For multiple models

---

## Chạy ứng dụng

```bash
# Sử dụng helper script (khuyến nghị)
./run.sh

# Hoặc manual
source venv/bin/activate
python run.py

# Hoặc GUI mode
python src/gui/app.py
```

### Testing

```bash
# Test cài đặt
./test_installation.sh

# Chạy tests
pytest tests/

# Test manual  
python -c "import torch; print('PyTorch:', torch.__version__)"
```

Setup script đảm bảo ứng dụng chạy mượt mà mà không cần can thiệp thủ công!