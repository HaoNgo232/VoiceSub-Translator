#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import subprocess
from gtts import gTTS
from PIL import Image, ImageDraw, ImageFont
import numpy as np

def create_test_image(output_path, text="Test Video", size=(1280, 720)):
    """Tạo ảnh test với text."""
    # Tạo ảnh màu đen
    image = Image.new('RGB', size, color='black')
    draw = ImageDraw.Draw(image)
    
    # Thêm text vào ảnh
    try:
        font = ImageFont.truetype("arial.ttf", 60)
    except:
        font = ImageFont.load_default()
        
    text_width = draw.textlength(text, font=font)
    text_height = 60
    
    position = ((size[0] - text_width) // 2, (size[1] - text_height) // 2)
    draw.text(position, text, font=font, fill='white')
    
    image.save(output_path)
    return output_path

def create_test_audio(output_path, text, lang='en'):
    """Tạo file audio test bằng gTTS."""
    tts = gTTS(text=text, lang=lang)
    tts.save(output_path)
    return output_path

def create_test_video(image_path, audio_path, output_path, duration=10):
    """Tạo video test từ ảnh và audio."""
    command = [
        'ffmpeg',
        '-loop', '1',
        '-i', image_path,
        '-i', audio_path,
        '-c:v', 'libx264',
        '-c:a', 'aac',
        '-strict', 'experimental',
        '-b:a', '192k',
        '-shortest',
        '-t', str(duration),
        '-y',
        output_path
    ]
    
    subprocess.run(command, check=True)
    return output_path

def generate_test_data():
    """Tạo dữ liệu test."""
    # Tạo thư mục nếu chưa tồn tại
    os.makedirs('fake_data', exist_ok=True)
    
    # Danh sách các đoạn text test tiếng Anh
    test_texts = [
        "Welcome to this Python programming course.",
        "Today we will learn about basic data structures.",
        "First, let's understand lists and tuples in Python.",
        "Next, we will explore dictionaries and sets.",
        "Finally, we will practice with some exercises."
    ]
    
    # Tạo các file test
    for i, text in enumerate(test_texts, 1):
        # Tạo ảnh
        image_path = f'fake_data/test_image_{i}.jpg'
        create_test_image(image_path, f"Test Video {i}")
        
        # Tạo audio
        audio_path = f'fake_data/test_audio_{i}.wav'
        create_test_audio(audio_path, text, lang='en')
        
        # Tạo video
        video_path = f'fake_data/test_video_{i}.mp4'
        create_test_video(image_path, audio_path, video_path)
        
        print(f"Created test data {i}: {video_path}")

if __name__ == "__main__":
    generate_test_data() 