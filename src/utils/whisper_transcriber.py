#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import argparse
import tempfile
from pathlib import Path
import logging

from src.utils.transcription import (
    extract_audio, 
    transcribe_audio
)

# Enable PyTorch CUDA logging with adjusted memory block size
os.environ["PYTORCH_CUDA_ALLOC_CONF"] = "max_split_size_mb:24"

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def main():
    parser = argparse.ArgumentParser(description="Transcribe audio/video using OpenAI's Whisper models")
    parser.add_argument("input_path", help="Path to input audio or video file")
    parser.add_argument("--output", "-o", help="Path to output SRT file (default: input_name_model.srt)")
    parser.add_argument("--model", "-m", default="tiny.en", 
                       choices=["tiny.en", "base.en", "small.en", "medium.en", "tiny", "base", "small", "medium", "large"],
                       help="Whisper model to use (default: tiny.en)")
    parser.add_argument("--language", "-l", help="Language code (e.g., 'en', 'vi'). Auto-detect if not specified.")
    parser.add_argument("--device", "-d", choices=["cuda", "cpu"], 
                       help="Device to run on (default: cuda if available, otherwise cpu)")
    
    args = parser.parse_args()
    
    # Set default output path if not specified
    if not args.output:
        input_path = Path(args.input_path)
        base_name = input_path.stem
        args.output = f"{base_name}_{args.model.replace('.', '_')}.srt"
    
    # Determine if input is audio or video
    input_ext = Path(args.input_path).suffix.lower()
    is_video = input_ext in ['.mp4', '.mkv', '.avi', '.mov', '.webm', '.flv']
    
    # Create a temporary directory for audio extraction if needed
    with tempfile.TemporaryDirectory() as temp_dir:
        audio_path = args.input_path
        
        # If input is video, extract audio first
        if is_video:
            logger.info("Input is a video file. Extracting audio...")
            audio_path = os.path.join(temp_dir, "extracted_audio.wav")
            if not extract_audio(args.input_path, audio_path):
                logger.error("Failed to extract audio. Exiting.")
                return
        
        # Transcribe the audio
        logger.info(f"Transcribing with model: {args.model}, Language: {args.language or 'auto-detect'}")
        success = transcribe_audio(
            audio_path, 
            args.output, 
            model_name=args.model, 
            language=args.language,
            device=args.device
        )
        
        if success:
            logger.info(f"Transcription completed successfully. Subtitles saved to: {args.output}")
        else:
            logger.error("Transcription failed or produced empty results.")

if __name__ == "__main__":
    main()
