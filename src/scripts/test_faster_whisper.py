#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import argparse
import logging
from pathlib import Path

# Thêm thư mục gốc vào PATH để import các module từ src
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from src.utils import (
    generate_subtitles,
    ENGINE_OPENAI_WHISPER,
    ENGINE_FASTER_WHISPER
)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def main():
    parser = argparse.ArgumentParser(description='Test Faster-Whisper Subtitle Generation')
    parser.add_argument('video_path', help='Path to input video file')
    parser.add_argument('--model', '-m', default='base', 
                      help='Model name for Faster-Whisper (tiny, base, small, medium, large-v3, distil-large-v3)')
    parser.add_argument('--compute_type', '-c', choices=['float16', 'float32', 'int8', 'int8_float16'],
                      default='float16', help='Compute type')
    parser.add_argument('--device', '-d', default='cuda', choices=['cuda', 'cpu'],
                      help='Device to run on (cuda/cpu)')
    parser.add_argument('--output', '-o', help='Path to output SRT file')
    parser.add_argument('--force', '-f', action='store_true', help='Force regenerate subtitles')
    
    args = parser.parse_args()
    
    # Tạo đường dẫn output nếu không được chỉ định
    if not args.output:
        video_path = Path(args.video_path)
        args.output = str(video_path.with_suffix('.srt'))
    
    logger.info("Testing Faster-Whisper subtitle generation")
    logger.info(f"Video: {args.video_path}")
    logger.info(f"Model: {args.model}")
    logger.info(f"Device: {args.device}")
    logger.info(f"Compute type: {args.compute_type}")
    
    success = generate_subtitles(
        video_path=args.video_path,
        output_path=args.output,
        model_name=args.model,
        device=args.device,
        engine=ENGINE_FASTER_WHISPER,
        compute_type=args.compute_type,
        force=args.force
    )
    
    if success:
        logger.info(f"Faster-Whisper subtitle generation completed successfully!")
        logger.info(f"Output saved to: {args.output}")
    else:
        logger.error("Faster-Whisper subtitle generation failed")
        sys.exit(1)

if __name__ == "__main__":
    main() 