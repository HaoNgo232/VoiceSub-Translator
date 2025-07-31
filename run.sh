#!/bin/bash
# VoiceSub-Translator Quick Run Script
cd "$(dirname "$0")"
source venv/bin/activate
python src/gui/app.py "$@"
