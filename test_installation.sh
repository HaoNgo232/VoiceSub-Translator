#!/bin/bash
# Test installation script
cd "$(dirname "$0")"
source venv/bin/activate
python test_local.py
