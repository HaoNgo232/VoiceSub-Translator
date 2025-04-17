#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import subprocess
import argparse
import torch
import gc
from faster_whisper import WhisperModel
import logging
import shutil

# Set up logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Enable PyTorch CUDA logging
import os
os.environ["PYTORCH_CUDA_ALLOC_CONF"] = "max_split_size_mb:32"

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
            text=True
        )
        
        # Check if command was successful
        if result.returncode != 0:
            logger.error(f"FFmpeg error: {result.stderr}")
            return False
            
        logger.info(f"Successfully extracted audio to: {audio_path}")
        return True
        
    except Exception as e:
        logger.error(f"Error extracting audio: {str(e)}")
        return False

def get_gpu_info():
    """Get GPU memory information."""
    if torch.cuda.is_available():
        t = torch.cuda.get_device_properties(0).total_memory
        c = torch.cuda.memory_cached(0)
        a = torch.cuda.memory_allocated(0)
        f = t - (c + a)  # free inside cache
        return f"Total: {t/1e9:.1f}GB, Cached: {c/1e9:.1f}GB, Allocated: {a/1e9:.1f}GB, Free: {f/1e9:.1f}GB"
    retu rn "CUDA not available"

def clear_gpu_memory():
    """Clear GPU memory cache and model files."""
    logger.info("Clearing GPU memory...")
    gc.collect()
    torch.cuda.empty_cache()
    
    # Clear model cache
    cache_dir = os.path.expanduser("~/.cache/huggingface")
    if os.path.exists(cache_dir):
        logger.info(f"Clearing model cache: {cache_dir}")
        shutil.rmtree(cache_dir, ignore_errors=True)

def generate_subtitles(audio_path, output_path, model_size="tiny", language=None):
    """Generate subtitles from audio using Faster Whisper."""
    try:
        # Show GPU info before loading
        logger.info(f"GPU status before loading: {get_gpu_info()}")
        clear_gpu_memory()
        logger.info(f"GPU status after clearing: {get_gpu_info()}")
        
        # Load the model with specific GPU settings
        logger.info(f"Loading Whisper model: {model_size} with compute_type=int8_float16")
        # Configure model settings
        model = WhisperModel(
            model_size,
            device="cuda",
            compute_type="int8",
            device_index=0,
            cpu_threads=1,
            num_workers=1,
            download_root=None
        )
        
        # Transcribe the audio
        logger.info("Transcribing audio...")
        segments, _ = model.transcribe(
            audio_path,
            beam_size=1,
            best_of=1,
            temperature=0,
            language=language,
            no_speech_threshold=0.5,
            condition_on_previous_text=False,
            vad_filter=False,
            compression_ratio_threshold=2.4,
            initial_prompt="This is a programming tutorial about NestJS, a popular Node.js framework. The speaker is explaining concepts clearly in English."
        )
        
        # Write subtitles in SRT format
        logger.info(f"Writing subtitles to: {output_path}")
        with open(output_path, "w", encoding="utf-8") as f:
            for i, segment in enumerate(segments, 1):
                # Convert time to SRT format (HH:MM:SS,mmm)
                start = f"{int(segment.start // 3600):02d}:{int(segment.start % 3600 // 60):02d}:{int(segment.start % 60):02d},{int(segment.start * 1000 % 1000):03d}"
                end = f"{int(segment.end // 3600):02d}:{int(segment.end % 3600 // 60):02d}:{int(segment.end % 60):02d},{int(segment.end * 1000 % 1000):03d}"
                
                # Write SRT block
                f.write(f"{i}\n")
                f.write(f"{start} --> {end}\n")
                f.write(f"{segment.text.strip()}\n\n")
                
        logger.info("Subtitle generation completed successfully!")
        return True
        
    except Exception as e:
        logger.error(f"Error generating subtitles: {str(e)}")
        return False

def main():
    # Set up argument parser
    parser = argparse.ArgumentParser(description="Generate subtitles for a video file using Faster Whisper")
    parser.add_argument("video_path", help="Path to input video file")
    parser.add_argument("--output", "-o", help="Path to output SRT file (default: input_video_subs.srt)")
    parser.add_argument("--model", "-m", default="base", help="Whisper model size (tiny, base, small, medium, large)")
    parser.add_argument("--language", "-l", help="Language code (optional, auto-detect if not specified)")
    
    args = parser.parse_args()
    
    # Verify input video exists
    if not os.path.exists(args.video_path):
        logger.error(f"Input video file does not exist: {args.video_path}")
        exit(1)
    
    # Set default output path if not specified
    if not args.output:
        output_name = os.path.splitext(os.path.basename(args.video_path))[0] + "_subs.srt"
        args.output = output_name
    
    # Temporary audio file path
    audio_path = "temp_audio.wav"
    
    try:
        # Extract audio
        logger.info("Extracting audio from video...")
        if not extract_audio(args.video_path, audio_path):
            raise Exception("Audio extraction failed")
            
        # Generate subtitles
        if not generate_subtitles(audio_path, args.output, args.model, args.language):
            raise Exception("Subtitle generation failed")
            
        # Clean up temp audio file
        if os.path.exists(audio_path):
            os.remove(audio_path)
            
    except Exception as e:
        logger.error(f"Error processing video: {e}")
        if os.path.exists(audio_path):
            os.remove(audio_path)
        exit(1)

if __name__ == "__main__":
    print("""
CUDA/cuDNN Installation Guide:
1. Install NVIDIA drivers:
   - Visit https://www.nvidia.com/download/index.aspx
   - Select your GPU model and download appropriate driver

2. Install CUDA Toolkit 11.8:
   - Download from https://developer.nvidia.com/cuda-11-8-0-download-archive
   - Follow installation instructions for your OS

3. Install cuDNN v9.1.0 for CUDA 11.x:
   - Visit https://developer.nvidia.com/cudnn
   - Download cuDNN v9.1.0 for CUDA 11.x
   - Follow installation guide: https://docs.nvidia.com/deeplearning/cudnn/install-guide/
   
If you don't have GPU/CUDA support, the script will automatically run on CPU (slower).
    """)
    main()
