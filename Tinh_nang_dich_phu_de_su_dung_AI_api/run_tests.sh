#!/bin/bash

# Kích hoạt môi trường ảo
source ../venv/bin/activate

# Cài đặt dependencies
pip install -r requirements.txt

# Chạy tests
python -m pytest test_api_handler.py -v 