#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import argparse
import tempfile
from pathlib import Path
import logging
from dotenv import load_dotenv
from .transcription import WhisperProcessor
from typing import Optional

# Load biến môi trường
load_dotenv()

# Enable PyTorch CUDA logging with adjusted memory block size
os.environ["PYTORCH_CUDA_ALLOC_CONF"] = "max_split_size_mb:24"

# Cấu hình logging
logging.basicConfig(
    level=os.getenv('LOG_LEVEL', 'INFO'),
    format=os.getenv('LOG_FORMAT', '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
)
logger = logging.getLogger(__name__)

def transcribe_video(
    video_path: str,
    output_path: Optional[str] = None,
    model_name: str = 'base.en',
    device: str = 'cuda'
) -> bool:
    """
    Chuyển đổi video thành văn bản sử dụng Whisper
    
    Args:
        video_path: Đường dẫn đến file video
        output_path: Đường dẫn để lưu file văn bản (mặc định là cùng thư mục với video)
        model_name: Tên model Whisper (tiny.en, base.en, small.en)
        device: Thiết bị chạy model (cuda/cpu)
        
    Returns:
        bool: True nếu thành công, False nếu thất bại
    """
    try:
        # Tạo đường dẫn output nếu không được chỉ định
        if output_path is None:
            video_path = Path(video_path)
            output_path = str(video_path.with_suffix('.txt'))
            
        logger.info(f"Starting transcription for: {video_path}")
        logger.info(f"Using model: {model_name}")
        logger.info(f"Device: {device}")
        
        # Khởi tạo WhisperProcessor
        processor = WhisperProcessor(model_name=model_name, device=device)
        
        # Thực hiện chuyển đổi
        result = processor.transcribe_audio(str(video_path))
        if result is None:
            logger.error("Transcription failed")
            return False
            
        # Ghi kết quả ra file text
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(result['text'])
            
        logger.info(f"Transcription saved to: {output_path}")
        return True
        
    except Exception as e:
        logger.error(f"Error during transcription: {str(e)}")
        return False

def main():
    parser = argparse.ArgumentParser(description='Transcribe audio/video using Whisper')
    parser.add_argument('input_path', help='Path to input audio/video file')
    parser.add_argument('--output', '-o', help='Path to output SRT file')
    parser.add_argument('--model', '-m', help='Whisper model name')
    parser.add_argument('--language', '-l', help='Language code')
    parser.add_argument('--device', '-d', help='Device to run on (cuda/cpu)')
    
    args = parser.parse_args()
    
    # Lấy cấu hình từ biến môi trường nếu không được chỉ định
    model_name = args.model or os.getenv('WHISPER_MODEL', 'base.en')
    language = args.language or os.getenv('WHISPER_LANGUAGE', 'en')  # Mặc định là tiếng Anh
    device = args.device or os.getenv('WHISPER_DEVICE', 'cuda')
    
    # Tạo tên file output nếu không được chỉ định
    if not args.output:
        base_name = os.path.splitext(args.input_path)[0]
        args.output = f"{base_name}.srt"
    
    logger.info(f"Starting transcription with model: {model_name}")
    logger.info(f"Language: {language}")
    logger.info(f"Device: {device}")
    
    success = transcribe_video(
        args.input_path,
        args.output,
        model_name=model_name,
        device=device
    )
    
    if success:
        logger.info(f"Transcription completed successfully. Output saved to: {args.output}")
    else:
        logger.error("Transcription failed")
        exit(1)

if __name__ == '__main__':
    main()
