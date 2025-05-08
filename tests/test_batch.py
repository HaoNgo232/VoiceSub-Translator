#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import subprocess
import logging
from pathlib import Path
import time
import json

# Thiết lập logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('batch_test.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def run_transcription(input_file, output_dir, model="tiny.en", language="vi"):
    """Chạy script transcribe cho một file."""
    try:
        # Tạo tên file output
        input_path = Path(input_file)
        output_file = output_dir / f"{input_path.stem}_{model.replace('.', '_')}.srt"
        
        # Chạy lệnh transcribe
        command = [
            "python3",
            "openai_whisper_transcribe.py",
            str(input_file),
            "--output", str(output_file),
            "--model", model,
            "--language", language
        ]
        
        logger.info(f"Đang xử lý file: {input_file}")
        start_time = time.time()
        
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            check=True
        )
        
        end_time = time.time()
        duration = end_time - start_time
        
        # Kiểm tra kết quả
        success = output_file.exists() and output_file.stat().st_size > 0
        
        return {
            "file": str(input_file),
            "success": success,
            "duration": duration,
            "output": str(output_file),
            "log": result.stdout
        }
        
    except subprocess.CalledProcessError as e:
        logger.error(f"Lỗi khi xử lý file {input_file}: {e.stderr}")
        return {
            "file": str(input_file),
            "success": False,
            "error": e.stderr
        }
    except Exception as e:
        logger.error(f"Lỗi không xác định với file {input_file}: {str(e)}")
        return {
            "file": str(input_file),
            "success": False,
            "error": str(e)
        }

def batch_process(input_dir, output_dir, model="tiny.en", language="vi"):
    """Xử lý batch các file video trong thư mục."""
    # Tạo thư mục output nếu chưa tồn tại
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Lấy danh sách file video
    input_dir = Path(input_dir)
    video_files = list(input_dir.glob("*.mp4"))
    
    if not video_files:
        logger.warning(f"Không tìm thấy file video nào trong {input_dir}")
        return
    
    logger.info(f"Bắt đầu xử lý {len(video_files)} file video")
    
    # Xử lý từng file
    results = []
    for video_file in video_files:
        result = run_transcription(video_file, output_dir, model, language)
        results.append(result)
        
        if result["success"]:
            logger.info(f"Hoàn thành: {video_file.name} trong {result['duration']:.2f} giây")
        else:
            logger.error(f"Thất bại: {video_file.name}")
    
    # Lưu kết quả
    summary = {
        "total_files": len(video_files),
        "successful": sum(1 for r in results if r["success"]),
        "failed": sum(1 for r in results if not r["success"]),
        "results": results
    }
    
    # Lưu summary vào file JSON
    with open(output_dir / "batch_summary.json", "w", encoding="utf-8") as f:
        json.dump(summary, f, ensure_ascii=False, indent=2)
    
    # In thống kê
    logger.info("\n=== Thống kê ===")
    logger.info(f"Tổng số file: {summary['total_files']}")
    logger.info(f"Thành công: {summary['successful']}")
    logger.info(f"Thất bại: {summary['failed']}")
    logger.info(f"Chi tiết kết quả đã được lưu vào: {output_dir}/batch_summary.json")

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Test batch processing cho script transcribe")
    parser.add_argument("--input", "-i", default="fake_data",
                      help="Thư mục chứa file video cần xử lý")
    parser.add_argument("--output", "-o", default="output",
                      help="Thư mục chứa kết quả")
    parser.add_argument("--model", "-m", default="tiny.en",
                      help="Model Whisper sử dụng")
    parser.add_argument("--language", "-l", default="vi",
                      help="Ngôn ngữ của video")
    
    args = parser.parse_args()
    
    batch_process(args.input, args.output, args.model, args.language) 