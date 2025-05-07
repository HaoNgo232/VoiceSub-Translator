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
        logging.FileHandler('feature_test.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def test_single_video():
    """Test tạo phụ đề cho một video."""
    logger.info("=== Test tạo phụ đề cho một video ===")
    
    # Tạo video test
    subprocess.run(["python3", "generate_fake_data.py"], check=True)
    
    # Lấy file video đầu tiên
    video_file = next(Path("fake_data").glob("*.mp4"))
    
    # Test với các model khác nhau
    models = ["tiny.en", "base.en", "small.en"]
    results = []
    
    for model in models:
        logger.info(f"\nTesting model: {model}")
        output_file = f"output/test_{video_file.stem}_{model}.srt"
        
        try:
            # Chạy lệnh transcribe
            command = [
                "python3", "openai_whisper_transcribe.py",
                str(video_file),
                "--output", output_file,
                "--model", model,
                "--language", "en"
            ]
            
            start_time = time.time()
            result = subprocess.run(command, capture_output=True, text=True, check=True)
            duration = time.time() - start_time
            
            # Kiểm tra kết quả
            success = Path(output_file).exists() and Path(output_file).stat().st_size > 0
            
            results.append({
                "model": model,
                "success": success,
                "duration": duration,
                "output": result.stdout
            })
            
            logger.info(f"Model {model}: {'Success' if success else 'Failed'} in {duration:.2f}s")
            
        except Exception as e:
            logger.error(f"Error with model {model}: {str(e)}")
            results.append({
                "model": model,
                "success": False,
                "error": str(e)
            })
    
    return results

def test_batch_processing():
    """Test xử lý hàng loạt video."""
    logger.info("\n=== Test xử lý hàng loạt video ===")
    
    try:
        # Chạy batch processing
        command = [
            "python3", "test_batch.py",
            "--input", "fake_data",
            "--output", "output",
            "--model", "tiny.en",
            "--language", "en"
        ]
        
        start_time = time.time()
        result = subprocess.run(command, capture_output=True, text=True, check=True)
        duration = time.time() - start_time
        
        # Kiểm tra kết quả
        summary_file = Path("output/batch_summary.json")
        success = summary_file.exists()
        
        if success:
            with open(summary_file, 'r', encoding='utf-8') as f:
                summary = json.load(f)
            logger.info(f"Batch processing completed in {duration:.2f}s")
            logger.info(f"Total files: {summary['total_files']}")
            logger.info(f"Successful: {summary['successful']}")
            logger.info(f"Failed: {summary['failed']}")
        else:
            logger.error("Batch processing failed - no summary file found")
            
        return {
            "success": success,
            "duration": duration,
            "output": result.stdout
        }
        
    except Exception as e:
        logger.error(f"Error in batch processing: {str(e)}")
        return {
            "success": False,
            "error": str(e)
        }

def run_all_tests():
    """Chạy tất cả các test."""
    logger.info("Starting feature tests...")
    
    # Tạo thư mục output nếu chưa tồn tại
    os.makedirs("output", exist_ok=True)
    
    # Test single video
    single_results = test_single_video()
    
    # Test batch processing
    batch_result = test_batch_processing()
    
    # Tổng kết
    logger.info("\n=== Test Summary ===")
    logger.info("Single Video Tests:")
    for result in single_results:
        logger.info(f"Model {result['model']}: {'Success' if result['success'] else 'Failed'}")
    
    logger.info("\nBatch Processing Test:")
    logger.info(f"Status: {'Success' if batch_result['success'] else 'Failed'}")
    
    # Lưu kết quả
    summary = {
        "single_video_tests": single_results,
        "batch_processing_test": batch_result
    }
    
    with open("output/test_summary.json", "w", encoding="utf-8") as f:
        json.dump(summary, f, ensure_ascii=False, indent=2)
    
    logger.info("\nTest results have been saved to output/test_summary.json")

if __name__ == "__main__":
    run_all_tests() 