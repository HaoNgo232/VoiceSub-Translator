#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import shutil
from pathlib import Path
import logging
from typing import Dict, List, Tuple

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def backup_original_subtitles(input_folder: str, backup_folder: str = None, target_lang: str = "vi") -> Dict[str, int]:
    """
    Sao lưu phụ đề gốc sang thư mục backup và xóa chúng nếu đã có bản dịch.
    
    Args:
        input_folder: Thư mục chứa các video và phụ đề
        backup_folder: Thư mục để sao lưu phụ đề gốc (mặc định là "backup_subtitles" trong input_folder)
        target_lang: Ngôn ngữ đích (mặc định là "vi")
        
    Returns:
        Dict[str, int]: Thống kê kết quả (số file được sao lưu, số file bị bỏ qua)
    """
    input_path = Path(input_folder)
    
    # Nếu không chỉ định backup_folder, mặc định là input_folder/backup_subtitles
    if backup_folder is None:
        backup_path = input_path / "backup_subtitles"
    else:
        backup_path = Path(backup_folder)
    
    # Tạo thư mục backup nếu chưa tồn tại
    backup_path.mkdir(parents=True, exist_ok=True)
    
    stats = {
        "total": 0,         # Tổng số phụ đề gốc
        "backed_up": 0,     # Số phụ đề đã sao lưu và xóa
        "skipped": 0,       # Số phụ đề bỏ qua (không có bản dịch)
        "no_subtitle": 0,   # Số video không có phụ đề
    }
    
    # Tìm tất cả các file video
    video_extensions = {'.mp4', '.avi', '.mkv', '.mov', '.wmv'}
    video_files = [f for f in input_path.glob('**/*') if f.suffix.lower() in video_extensions]
    
    logger.info(f"Tìm thấy {len(video_files)} file video trong thư mục {input_folder}")
    
    for video_file in video_files:
        # Tìm phụ đề gốc
        original_subtitle = video_file.with_suffix('.srt')
        
        if not original_subtitle.exists():
            logger.info(f"Video {video_file.name} không có phụ đề gốc")
            stats["no_subtitle"] += 1
            continue
            
        # Tìm phụ đề đã dịch
        translated_subtitle = original_subtitle.parent / f"{original_subtitle.stem}_{target_lang}.srt"
        
        if not translated_subtitle.exists():
            logger.info(f"Video {video_file.name} chưa có bản dịch {target_lang}")
            stats["skipped"] += 1
            continue
            
        stats["total"] += 1
        
        # Tạo đường dẫn trong thư mục backup
        relative_path = original_subtitle.relative_to(input_path)
        backup_file = backup_path / relative_path
        
        # Tạo thư mục cha cho file backup
        backup_file.parent.mkdir(parents=True, exist_ok=True)
        
        try:
            # Sao chép file gốc vào thư mục backup
            shutil.copy2(original_subtitle, backup_file)
            
            # Xóa file gốc
            original_subtitle.unlink()
            
            logger.info(f"Đã sao lưu và xóa phụ đề gốc: {original_subtitle.name}")
            stats["backed_up"] += 1
        except Exception as e:
            logger.error(f"Lỗi khi xử lý file {original_subtitle}: {str(e)}")
    
    # Log thống kê
    logger.info(f"Kết quả xử lý:")
    logger.info(f"- Tổng số phụ đề gốc: {stats['total']}")
    logger.info(f"- Số phụ đề đã sao lưu và xóa: {stats['backed_up']}")
    logger.info(f"- Số phụ đề bỏ qua (không có bản dịch): {stats['skipped']}")
    logger.info(f"- Số video không có phụ đề: {stats['no_subtitle']}")
    
    return stats

def restore_original_subtitles(input_folder: str, backup_folder: str = None) -> Dict[str, int]:
    """
    Khôi phục phụ đề gốc từ thư mục backup.
    
    Args:
        input_folder: Thư mục chứa các video
        backup_folder: Thư mục chứa phụ đề gốc đã sao lưu (mặc định là "backup_subtitles" trong input_folder)
        
    Returns:
        Dict[str, int]: Thống kê kết quả
    """
    input_path = Path(input_folder)
    
    # Nếu không chỉ định backup_folder, mặc định là input_folder/backup_subtitles
    if backup_folder is None:
        backup_path = input_path / "backup_subtitles"
    else:
        backup_path = Path(backup_folder)
    
    if not backup_path.exists():
        logger.error(f"Thư mục backup {backup_path} không tồn tại")
        return {"restored": 0, "failed": 0}
    
    stats = {
        "restored": 0,  # Số phụ đề đã khôi phục
        "failed": 0     # Số khôi phục thất bại
    }
    
    # Tìm tất cả file phụ đề trong thư mục backup
    backed_up_subtitles = list(backup_path.glob('**/*.srt'))
    
    logger.info(f"Tìm thấy {len(backed_up_subtitles)} phụ đề trong thư mục backup")
    
    for backup_file in backed_up_subtitles:
        try:
            # Tính đường dẫn tương đối
            relative_path = backup_file.relative_to(backup_path)
            
            # Tính đường dẫn đích
            target_file = input_path / relative_path
            
            # Tạo thư mục cha cho file đích nếu chưa tồn tại
            target_file.parent.mkdir(parents=True, exist_ok=True)
            
            # Khôi phục file
            shutil.copy2(backup_file, target_file)
            
            logger.info(f"Đã khôi phục phụ đề: {target_file}")
            stats["restored"] += 1
        except Exception as e:
            logger.error(f"Lỗi khi khôi phục file {backup_file}: {str(e)}")
            stats["failed"] += 1
    
    # Log thống kê
    logger.info(f"Kết quả khôi phục:")
    logger.info(f"- Số phụ đề đã khôi phục: {stats['restored']}")
    logger.info(f"- Số khôi phục thất bại: {stats['failed']}")
    
    return stats

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Quản lý phụ đề gốc")
    parser.add_argument("--input", "-i", required=True, help="Thư mục chứa video và phụ đề")
    parser.add_argument("--backup", "-b", default=None, help="Thư mục backup (mặc định: '<input_folder>/backup_subtitles')")
    parser.add_argument("--lang", "-l", default="vi", help="Ngôn ngữ đích (mặc định: 'vi')")
    parser.add_argument("--restore", "-r", action="store_true", help="Khôi phục phụ đề gốc từ backup")
    
    args = parser.parse_args()
    
    if args.restore:
        restore_original_subtitles(args.input, args.backup)
    else:
        backup_original_subtitles(args.input, args.backup, args.lang) 