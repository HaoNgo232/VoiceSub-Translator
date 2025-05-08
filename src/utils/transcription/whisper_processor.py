import os
import torch
import whisper
import logging
import time

from .gpu_utils import get_gpu_info, clear_gpu_memory

# Cấu hình logging
logger = logging.getLogger(__name__)

def format_timestamp(seconds):
    """Convert seconds to SRT timestamp format (HH:MM:SS,mmm)"""
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    seconds_remainder = seconds % 60
    milliseconds = int((seconds_remainder % 1) * 1000)
    return f"{hours:02d}:{minutes:02d}:{int(seconds_remainder):02d},{milliseconds:03d}"

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