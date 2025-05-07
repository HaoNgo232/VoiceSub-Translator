#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import argparse
import torch
import gc
import whisper
import logging
import time
import tempfile
import subprocess
from pathlib import Path

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Enable PyTorch CUDA logging with adjusted memory block size
os.environ["PYTORCH_CUDA_ALLOC_CONF"] = "max_split_size_mb:24"

def get_gpu_info():
    """Get GPU memory information."""
    if torch.cuda.is_available():
        try:
            t = torch.cuda.get_device_properties(0).total_memory
            r = torch.cuda.memory_reserved(0)
            a = torch.cuda.memory_allocated(0)
            f = r - a  # Free memory within the reserved block
            return f"Total: {t/1e9:.1f}GB, Reserved: {r/1e9:.1f}GB, Allocated: {a/1e9:.1f}GB, Free in Reserved: {f/1e9:.1f}GB"
        except Exception as e:
            logger.error(f"Could not get GPU info: {e}")
            return "Error getting GPU info"
    return "CUDA not available"

def clear_gpu_memory():
    """Clear GPU memory cache."""
    logger.info("Attempting to clear GPU memory...")
    gc.collect()
    if torch.cuda.is_available():
        try:
            torch.cuda.empty_cache()
            logger.info("torch.cuda.empty_cache() called.")
        except Exception as e:
            logger.error(f"Error calling torch.cuda.empty_cache(): {e}")
    else:
        logger.info("CUDA not available, skipping torch.cuda.empty_cache().")

def extract_audio(video_path, audio_path):
    """Extract audio from video file using ffmpeg."""
    try:
        # Construct ffmpeg command
        command = [
            'ffmpeg',
            '-i', video_path,  # Input video
            '-vn',  # Disable video
            '-acodec', 'pcm_s16le',  # Audio codec
            '-ar', '16000',  # Sample rate
            '-ac', '1',  # Mono audio
            '-y',  # Overwrite output file
            audio_path
        ]
        
        # Execute ffmpeg command
        logger.info(f"Running ffmpeg command: {' '.join(command)}")
        result = subprocess.run(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=False  # Don't raise exception on non-zero exit
        )
        
        # Check if command was successful
        if result.returncode != 0:
            logger.error(f"FFmpeg error (code {result.returncode}): {result.stderr}")
            return False
            
        logger.info(f"Successfully extracted audio to: {audio_path}")
        return True
        
    except Exception as e:
        logger.error(f"Error extracting audio: {str(e)}")
        return False

def transcribe_audio(audio_path, output_path, model_name="tiny.en", language=None, device=None):
    """
    Transcribe audio using OpenAI's Whisper model.
    
    Args:
        audio_path: Path to the audio file
        output_path: Path to save the SRT file
        model_name: Whisper model name (tiny.en, base.en, etc.)
        language: Language code (e.g., 'en', 'vi')
        device: Device to run on ('cuda', 'cpu', or None for auto-detection)
    
    Returns:
        bool: True if successful, False otherwise
    """
    model = None
    try:
        # Determine device if not specified
        if device is None:
            device = "cuda" if torch.cuda.is_available() else "cpu"
        
        # Clear GPU memory before loading model if using CUDA
        if device == "cuda":
            clear_gpu_memory()
            logger.info(f"GPU status before loading model: {get_gpu_info()}")
        
        # Load the Whisper model
        logger.info(f"Loading Whisper model: {model_name} on {device}")
        model = whisper.load_model(model_name, device=device)
        logger.info(f"Model {model_name} loaded successfully")
        
        if device == "cuda":
            logger.info(f"GPU status after loading model: {get_gpu_info()}")
        
        # Set transcription options
        transcribe_options = {
            "temperature": (0.0, 0.2, 0.4, 0.6, 0.8, 1.0),  # Temperature for sampling
            "compression_ratio_threshold": 2.4,
            "logprob_threshold": -1.0,
            "no_speech_threshold": 0.6,
            "condition_on_previous_text": True,
            "word_timestamps": True,  # Enable word-level timestamps
            "initial_prompt": None
        }
        
        # Add language if specified
        if language:
            transcribe_options["language"] = language
        
        # Transcribe the audio
        logger.info(f"Starting transcription with model {model_name}")
        start_time = time.time()
        result = model.transcribe(audio_path, **transcribe_options)
        end_time = time.time()
        logger.info(f"Transcription completed in {end_time - start_time:.2f} seconds")
        
        if device == "cuda":
            logger.info(f"GPU status after transcription: {get_gpu_info()}")
        
        # Convert result to SRT format
        logger.info(f"Writing subtitles to: {output_path}")
        with open(output_path, "w", encoding="utf-8") as f:
            for i, segment in enumerate(result["segments"], 1):
                # Format timestamps as SRT format (HH:MM:SS,mmm)
                start = format_timestamp(segment["start"])
                end = format_timestamp(segment["end"])
                
                # Write SRT entry
                f.write(f"{i}\n")
                f.write(f"{start} --> {end}\n")
                f.write(f"{segment['text'].strip()}\n\n")
        
        # Verify the output file
        if os.path.exists(output_path) and os.path.getsize(output_path) > 0:
            logger.info("Subtitle generation completed successfully!")
            return True
        else:
            logger.error(f"Subtitle file is empty or not created: {output_path}")
            return False
            
    except Exception as e:
        logger.error(f"Error during transcription: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        return False
    finally:
        # Clean up resources
        if model is not None:
            del model
        if device == "cuda":
            clear_gpu_memory()
            logger.info(f"GPU status after cleanup: {get_gpu_info()}")

def format_timestamp(seconds):
    """Convert seconds to SRT timestamp format (HH:MM:SS,mmm)"""
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    seconds_remainder = seconds % 60
    milliseconds = int((seconds_remainder % 1) * 1000)
    return f"{hours:02d}:{minutes:02d}:{int(seconds_remainder):02d},{milliseconds:03d}"

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
