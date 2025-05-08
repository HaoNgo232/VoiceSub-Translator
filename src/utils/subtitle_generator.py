import os
import torch
import whisper
import logging
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)

def generate_subtitles(video_path: str, output_path: str, model_name: str = "base") -> None:
    """
    Tạo phụ đề cho video sử dụng Whisper
    
    Args:
        video_path: Đường dẫn đến file video
        output_path: Đường dẫn để lưu file phụ đề
        model_name: Tên model Whisper (tiny, base, small, medium, large)
    """
    try:
        # Kiểm tra GPU
        device = "cuda" if torch.cuda.is_available() else "cpu"
        logger.info(f"Sử dụng device: {device}")
        
        # Load model
        logger.info(f"Đang tải model Whisper {model_name}...")
        model = whisper.load_model(model_name, device=device)
        
        # Tạo phụ đề
        logger.info(f"Đang tạo phụ đề cho {video_path}...")
        result = model.transcribe(video_path)
        
        # Lưu phụ đề
        logger.info(f"Đang lưu phụ đề vào {output_path}...")
        _save_srt(result["segments"], output_path)
        
        logger.info("Hoàn thành!")
        
    except Exception as e:
        logger.error(f"Lỗi khi tạo phụ đề: {str(e)}")
        raise

def _save_srt(segments: list, output_path: str) -> None:
    """
    Lưu phụ đề dạng SRT
    
    Args:
        segments: Danh sách các đoạn phụ đề
        output_path: Đường dẫn để lưu file
    """
    with open(output_path, "w", encoding="utf-8") as f:
        for i, segment in enumerate(segments, 1):
            # Chuyển đổi thời gian
            start = _format_timestamp(segment["start"])
            end = _format_timestamp(segment["end"])
            
            # Ghi phụ đề
            f.write(f"{i}\n")
            f.write(f"{start} --> {end}\n")
            f.write(f"{segment['text'].strip()}\n\n")

def _format_timestamp(seconds: float) -> str:
    """
    Chuyển đổi số giây thành định dạng SRT (HH:MM:SS,mmm)
    
    Args:
        seconds: Số giây
        
    Returns:
        Chuỗi thời gian theo định dạng SRT
    """
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    seconds = seconds % 60
    milliseconds = int((seconds - int(seconds)) * 1000)
    
    return f"{hours:02d}:{minutes:02d}:{int(seconds):02d},{milliseconds:03d}" 