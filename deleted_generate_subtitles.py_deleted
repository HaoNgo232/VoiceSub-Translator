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
import time

# Set up logging
logging.basicConfig(
    level=logging.INFO,  
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Enable PyTorch CUDA logging with adjusted memory block size
os.environ["PYTORCH_CUDA_ALLOC_CONF"] = "max_split_size_mb:24"

def choose_optimal_config(model_size, mode=None):
    """Choose optimal device and compute_type based on model size and mode preference."""
    if mode == "speed":
        return "tiny", "cuda", "int8"
    elif mode == "accuracy":
        return "base", "cpu", "int8"
    else:
        # Auto-select best config based on model size
        if model_size == "tiny":
            return model_size, "cuda", "int8"  # tiny works well on GPU
        else:
            return model_size, "cpu", "int8"  # base/small better on CPU

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

def generate_subtitles(audio_path, output_path, model_size="tiny", language=None, device="cuda", compute_type="int8"):
    """Generate subtitles from audio using Faster Whisper."""
    model = None
    try:
        # Validate compute_type based on device
        if device == "cpu" and compute_type not in ["int8", "float32", "default"]:
            logger.warning(f"Compute type {compute_type} not optimal for CPU. Using 'int8' instead.")
            compute_type = "int8"  # Force int8 for CPU as safest option
        if device == "cuda" and compute_type not in ["int8", "float16", "auto", "int8_float16"]:
            logger.warning(f"Compute type {compute_type} not typical for CUDA. Using 'auto' instead.")
            compute_type = "auto"  # Let the library choose for CUDA

        # Clear memory *before* attempting to load
        if device == "cuda":
            clear_gpu_memory()
            logger.info(f"GPU status before loading: {get_gpu_info()}")
        else:
            logger.info("Targeting CPU, skipping GPU memory clear.")

        # Load the model
        logger.info(f"Attempting to load Whisper model: {model_size} on {device} with compute_type={compute_type}")
        try:
            # Fix parameter names to match CTranslate2 expectations
            model = WhisperModel(
                model_size,
                device=device,
                compute_type=compute_type,
                # Fix parameter names for CPU/CUDA
                device_index=0 if device == "cuda" else None,
                cpu_threads=4 if device == "cpu" else 2,  # CPU threads
                num_workers=2,  # Applies to both CPU and CUDA
                download_root="model_cache"
            )
            logger.info(f"Model {model_size} loaded successfully on {device}.")
            if device == "cuda":
                logger.info(f"GPU status after loading: {get_gpu_info()}")

        except RuntimeError as e:
            logger.error(f"Failed to load model {model_size} on {device}. Error: {str(e)}")
            if "CUDA out of memory" in str(e) and device == "cuda":
                logger.warning("CUDA OOM detected. Suggest trying CPU or smaller model/compute_type.")
            if model is not None: del model; model = None
            if device == "cuda": clear_gpu_memory()
            return False
        except Exception as load_e:
            logger.error(f"An unexpected error occurred during model loading: {str(load_e)}")
            logger.info("Trying different parameter structure for CTranslate2...")
            
            # Second attempt with simpler parameters to match CTranslate2 expectations
            try:
                model = WhisperModel(
                    model_size,
                    device=device,
                    compute_type=compute_type,
                    download_root="model_cache"
                )
                logger.info(f"Model {model_size} loaded successfully on second attempt.")
            except Exception as retry_e:
                logger.error(f"Second attempt also failed: {str(retry_e)}")
                if model is not None: del model; model = None
                if device == "cuda": clear_gpu_memory()
                return False

        if model is None:
            logger.error(f"Model object is None after loading attempts. Cannot proceed.")
            return False

        # Adjustments based on model and device
        beam_size = 5 if device == "cpu" or model_size == "tiny" else 1
        best_of = 5 if device == "cpu" or model_size == "tiny" else 1
        
        # Transcribe the audio with optimized parameters based on device and model
        logger.info(f"Starting transcription with model {model_size} on {device}")
        logger.info(f"Using beam_size={beam_size}, best_of={best_of}")
        
        segments, info = model.transcribe(
            audio_path,
            language=language,
            beam_size=beam_size,
            temperature=0,
            best_of=best_of,
            vad_filter=True,
            vad_parameters=dict(
                threshold=0.5,
                min_silence_duration_ms=500,
                speech_pad_ms=100
            ),
            condition_on_previous_text=True,
            initial_prompt="This is a tutorial video." if model_size != "tiny" else None,
            no_speech_threshold=0.6,
            word_timestamps=False
        )

        logger.info(f"Transcription finished. Detected language: {info.language}")
        if device == "cuda":
            logger.info(f"GPU status after transcription: {get_gpu_info()}")

        segment_list = list(segments)  # Materialize the generator
        logger.info(f"Extracted {len(segment_list)} segments")

        logger.info(f"Writing subtitles to: {output_path}")
        with open(output_path, "w", encoding="utf-8") as f:
            if not segment_list:
                logger.warning("No segments were transcribed!")
            for i, segment in enumerate(segment_list, 1):
                logger.debug(f"Segment {i}: '{segment.text[:50]}...' [{segment.start:.1f}s - {segment.end:.1f}s]")  # Use debug level
                start = f"{int(segment.start // 3600):02d}:{int(segment.start % 3600 // 60):02d}:{int(segment.start % 60):02d},{int(segment.start * 1000 % 1000):03d}"
                end = f"{int(segment.end // 3600):02d}:{int(segment.end % 3600 // 60):02d}:{int(segment.end % 60):02d},{int(segment.end * 1000 % 1000):03d}"
                f.write(f"{i}\n")
                f.write(f"{start} --> {end}\n")
                f.write(f"{segment.text.strip()}\n\n")

        # Verify file has content
        if os.path.exists(output_path) and os.path.getsize(output_path) > 0:
            with open(output_path, "r", encoding="utf-8") as f_check:
                content = f_check.read()
                lines = [line.strip() for line in content.split('\n') if line.strip()]
                if len(lines) > len(segment_list) * 2 and len(segment_list) > 0:
                    logger.info("Subtitle generation completed successfully!")
                    return True
                elif len(segment_list) == 0 and len(lines) == 0:
                    logger.warning("Transcription resulted in 0 segments. Output file is empty.")
                    return False
                else:
                    logger.error(f"Subtitle file generated but seems empty or only contains timestamps: {output_path}")
                    return False
        elif not segment_list:
            logger.warning(f"Subtitle generation finished, but no segments were transcribed. Output file '{output_path}' might be empty or not created.")
            return False
        else:
            logger.error(f"Subtitle file is empty or not created: {output_path}")
            return False

    except Exception as e:
        logger.error(f"An error occurred in generate_subtitles: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        return False
    finally:
        if model is not None:
            logger.info(f"Cleaning up model {model_size}...")
            del model
            model = None
        if device == "cuda":
            clear_gpu_memory()
            logger.info(f"GPU status after final cleanup: {get_gpu_info()}")

def main():
    parser = argparse.ArgumentParser(description="Generate subtitles for a video file using Faster Whisper")
    parser.add_argument("video_path", help="Path to input video file")
    parser.add_argument("--output", "-o", help="Path to output SRT file (default: video_name_model_lang.srt)")
    parser.add_argument("--model", "-m", default="tiny", choices=["tiny", "base", "small", "medium", "large-v2", "large-v3"], help="Whisper model size (default: base)")
    parser.add_argument("--language", "-l", default="en", help="Language code (e.g., 'en', 'vi'). Auto-detect if None.")
    parser.add_argument("--device", "-d", default="cuda", choices=["cuda", "cpu"], help="Device to run on (default: cuda)")
    parser.add_argument("--compute_type", "-ct", default="int8", 
                       choices=["int8", "float16", "float32", "auto", "int8_float16"], 
                       help="Compute type (default: int8)")
    parser.add_argument("--mode", default=None, choices=["speed", "accuracy"], 
                       help="Optimization mode: 'speed' (tiny on GPU) or 'accuracy' (base on CPU)")

    args = parser.parse_args()
    
    # Apply optimization mode if specified (overrides other settings)
    if args.mode:
        original_model = args.model
        args.model, args.device, args.compute_type = choose_optimal_config(args.model, args.mode)
        logger.info(f"Mode '{args.mode}' selected: Changed from '{original_model}' to model='{args.model}', device='{args.device}', compute_type='{args.compute_type}'")

    # Validate compute_type based on device in main as well
    if args.device == "cpu" and args.compute_type in ["float16", "auto", "int8_float16"]:
        logger.warning(f"Compute type '{args.compute_type}' might not be ideal for CPU. Suggesting 'int8' or 'float32'.")
    if args.device == "cuda" and args.compute_type == "float32":
        logger.warning("Compute type 'float32' is generally inefficient on GPU compared to 'float16' or 'int8'.")

    # Set default output path if not specified
    if not args.output:
        base_name = os.path.splitext(os.path.basename(args.video_path))[0]
        lang_suffix = f"_{args.language}" if args.language else "_auto"
        device_suffix = f"_{args.device}"
        ct_suffix = f"_{args.compute_type}"
        args.output = f"{base_name}_{args.model}{lang_suffix}{device_suffix}{ct_suffix}.srt"

    # Temporary audio file path
    temp_dir = "temp_audio_dir"
    os.makedirs(temp_dir, exist_ok=True)
    audio_path = os.path.join(temp_dir, "temp_audio.wav")

    try:
        logger.info(f"Processing video: {args.video_path}")
        logger.info(f"Model: {args.model}, Language: {args.language or 'auto'}, Device: {args.device}, Compute Type: {args.compute_type}")
        logger.info(f"Output file: {args.output}")

        # 1. Extract Audio
        logger.info("Step 1: Extracting audio...")
        if not extract_audio(args.video_path, audio_path):
            logger.error("Failed to extract audio. Exiting.")
            if os.path.exists(temp_dir):
                shutil.rmtree(temp_dir)
            return
        logger.info("Audio extraction successful.")

        # 2. Generate Subtitles
        logger.info(f"Step 2: Generating subtitles...")
        start_time = time.time()
        success = generate_subtitles(audio_path, args.output, args.model, args.language, args.device, args.compute_type)
        end_time = time.time()
        logger.info(f"Subtitle generation step took {end_time - start_time:.2f} seconds.")

        # 3. Cleanup audio file/dir
        if os.path.exists(temp_dir):
            logger.info(f"Cleaning up temporary audio directory: {temp_dir}")
            shutil.rmtree(temp_dir)

        if success:
            logger.info(f"Process finished successfully. Subtitles saved to: {args.output}")
        else:
            logger.error("Process failed during subtitle generation or produced empty results.")

    except Exception as e:
        logger.error(f"An error occurred in main process: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        if os.path.exists(temp_dir):
            logger.info(f"Cleaning up temporary audio directory after error: {temp_dir}")
            shutil.rmtree(temp_dir)

if __name__ == "__main__":
    main()
