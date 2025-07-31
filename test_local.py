#!/usr/bin/env python3
"""
Test script cho VoiceSub-Translator local environment
"""

import sys
import os

# Add project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_imports():
    """Test basic imports"""
    print("=== Testing Basic Imports ===")
    
    try:
        import torch
        print(f"✅ PyTorch: {torch.__version__}")
        print(f"✅ CUDA available: {torch.cuda.is_available()}")
        if torch.cuda.is_available():
            print(f"✅ GPU device: {torch.cuda.get_device_name()}")
            print(f"✅ GPU count: {torch.cuda.device_count()}")
    except Exception as e:
        print(f"❌ PyTorch error: {e}")
    
    try:
        import whisper
        print(f"✅ OpenAI Whisper imported")
    except Exception as e:
        print(f"❌ Whisper error: {e}")
    
    try:
        from faster_whisper import WhisperModel
        print(f"✅ Faster Whisper imported")
    except Exception as e:
        print(f"❌ Faster Whisper error: {e}")
    
    try:
        import openai
        print(f"✅ OpenAI: {openai.__version__}")
    except Exception as e:
        print(f"❌ OpenAI error: {e}")

def test_project_structure():
    """Test project structure"""
    print("\n=== Testing Project Structure ===")
    
    required_dirs = ['src', 'src/gui', 'src/api', 'src/processor', 'src/translator']
    for dir_path in required_dirs:
        if os.path.exists(dir_path):
            print(f"✅ {dir_path}")
        else:
            print(f"❌ {dir_path} - missing")

def test_gpu_functionality():
    """Test GPU functionality with simple tensor operation"""
    print("\n=== Testing GPU Functionality ===")
    
    try:
        import torch
        if torch.cuda.is_available():
            # Create tensors on GPU
            device = torch.device('cuda')
            x = torch.randn(100, 100).to(device)
            y = torch.randn(100, 100).to(device)
            z = torch.matmul(x, y)
            print(f"✅ GPU tensor operations successful")
            print(f"✅ Result tensor shape: {z.shape}")
            print(f"✅ GPU memory used: {torch.cuda.memory_allocated() / 1024**2:.2f} MB")
        else:
            print("❌ CUDA not available")
    except Exception as e:
        print(f"❌ GPU test error: {e}")

def main():
    """Main test function"""
    print("🧪 VoiceSub-Translator Local Environment Test")
    print("=" * 50)
    
    test_imports()
    test_project_structure() 
    test_gpu_functionality()
    
    print("\n" + "=" * 50)
    print("✨ Test completed!")

if __name__ == "__main__":
    main()
