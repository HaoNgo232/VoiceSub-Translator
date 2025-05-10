# VoiceSub-Translator

A powerful tool for generating, translating, and editing subtitles using AI models. This application leverages OpenAI's Whisper for speech recognition and various AI providers for translation.

## Features

- Generate subtitles from video files using Whisper
- Translate subtitles between languages using multiple AI providers
- Edit subtitles with a user-friendly GUI
- GPU acceleration with CUDA support

## Installation

### Prerequisites

- Python 3.9.9
- CUDA Toolkit (recommended: CUDA 11.8) for GPU acceleration
- ffmpeg

### Step 1: Install Python 3.9.9

On Linux Mint/Ubuntu:

```bash
sudo add-apt-repository ppa:deadsnakes/ppa
sudo apt update
sudo apt install python3.9 python3.9-venv python3.9-dev
```

### Step 2: Create a Virtual Environment

```bash
python3.9 -m venv venv
source venv/bin/activate
```

### Step 3: Install CUDA and cuDNN

Ensure CUDA is installed for GPU acceleration:

```bash
# Check if CUDA is already installed
nvcc --version

# If not installed, download and install CUDA 11.8 from NVIDIA's website
# https://developer.nvidia.com/cuda-11-8-0-download-archive
```

### Step 4: Install PyTorch with CUDA Support

```bash
pip install --upgrade pip setuptools wheel
pip install torch==2.0.1 torchaudio==2.0.2 torchvision==0.15.2 --index-url https://download.pytorch.org/whl/cu118
```

### Step 5: Install Project Dependencies

```bash
pip install -r requirements.txt
pip install -e . # Nếu gặp lôi module src not found
```

### Step 6: Install ffmpeg

```bash
sudo apt update
sudo apt install ffmpeg
```

### Step 7: Verify Installation

```bash
# Check Whisper version
python -c "import whisper; print(whisper.__version__)"

# Check CUDA availability
python -c "import torch; print('CUDA available:', torch.cuda.is_available()); print('Device name:', torch.cuda.get_device_name(0) if torch.cuda.is_available() else 'No GPU')"
```

## API Provider Setup

VoiceSub-Translator supports multiple AI providers for translation services. Configure your API keys in a `.env` file in the project root:

```
# API Keys for Translation Providers
OPENAI_API_KEY=your_openai_key_here
GOOGLE_API_KEY=your_google_gemini_key_here
MISTRAL_API_KEY=your_mistral_key_here
GROQ_API_KEY=your_groq_key_here
OPENROUTER_API_KEY=your_openrouter_key_here
CEREBRAS_API_KEY=your_cerebras_key_here
NOVITA_API_KEY=your_novita_key_here

# Optional: Set default providers
DEFAULT_TRANSLATION_PROVIDER=google  # Options: novita, google, mistral, groq, openrouter, cerebras
```

### Obtaining API Keys

1. **OpenAI API (including Novita)**: Sign up at [OpenAI Platform](https://platform.openai.com/)
2. **Google Gemini**: Get API key at [Google AI Studio](https://makersuite.google.com/app/apikey)
3. **Mistral AI**: Register at [Mistral AI Platform](https://console.mistral.ai/)
4. **Groq**: Get API key from [Groq Cloud](https://console.groq.com/)
5. **OpenRouter**: Sign up at [OpenRouter](https://openrouter.ai/)
6. **Cerebras**: Register at [Cerebras](https://www.cerebras.net/)

## Usage

### Starting the Application

```bash
python src/gui/app.py
```

### Generating Subtitles

1. Open a video file using the "Open File" button
2. Click "Generate Subtitles" to create subtitles using Whisper
3. Adjust settings as needed in the configuration panel

### Translating Subtitles

1. Load a video with subtitles or generate them first
2. Select the target language from the dropdown
3. Click "Translate" to create translated subtitles

## Troubleshooting

1. **Module Not Found Errors**: Ensure you've installed the project in development mode:

   ```bash
   pip install -e .
   ```

2. **GPU/CUDA Issues**: If encountering Triton-related errors:

   ```bash
   pip uninstall -y triton
   pip install triton==2.2.0
   ```

3. **API Provider Issues**: Check that your API keys are correctly set in the `.env` file and that you have an active subscription with the provider.

## License

[Your License Information]
