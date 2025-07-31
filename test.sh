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
