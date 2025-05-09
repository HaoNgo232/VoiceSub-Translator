#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import argparse
import logging
from pathlib import Path
import sys

# Thêm thư mục gốc vào sys.path để import các module
sys.path.append(str(Path(__file__).parent.parent.parent))

from src.utils.subtitle_management import backup_original_subtitles, restore_original_subtitles

# Thiết lập logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('subtitle_management.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def parse_args():
    """Xử lý tham số dòng lệnh"""
    parser = argparse.ArgumentParser(
        description="Công cụ xóa phụ đề gốc sau khi đã có bản dịch",
        formatter_class=argparse.RawTextHelpFormatter
    )
    
    parser.add_argument(
        "-i", "--input", 
        required=True,
        help="Thư mục đầu vào chứa video và phụ đề"
    )
    
    parser.add_argument(
        "-b", "--backup",
        default=None,
        help="Thư mục backup (mặc định: '<input_folder>/backup_subtitles')"
    )
    
    parser.add_argument(
        "-l", "--lang",
        default="vi",
        help="Ngôn ngữ đích của bản dịch (mặc định: 'vi')"
    )
    
    parser.add_argument(
        "-r", "--restore",
        action="store_true",
        help="Khôi phục phụ đề gốc từ thư mục backup"
    )
    
    return parser.parse_args()

def print_stats(stats, restore=False):
    """In thống kê kết quả"""
    if restore:
        print("\n--- KẾT QUẢ KHÔI PHỤC ---")
        print(f"Số phụ đề đã khôi phục: {stats['restored']}")
        print(f"Số khôi phục thất bại: {stats['failed']}")
    else:
        print("\n--- KẾT QUẢ XỬ LÝ ---")
        print(f"Tổng số phụ đề gốc: {stats['total']}")
        print(f"Số phụ đề đã sao lưu và xóa: {stats['backed_up']}")
        print(f"Số phụ đề bỏ qua (không có bản dịch): {stats['skipped']}")
        print(f"Số video không có phụ đề: {stats['no_subtitle']}")

def main():
    """Hàm chính"""
    args = parse_args()
    
    if not os.path.exists(args.input):
        logger.error(f"Thư mục đầu vào '{args.input}' không tồn tại")
        return 1
    
    try:
        # Tính toán đường dẫn backup mặc định nếu không được chỉ định
        backup_folder = args.backup
        if backup_folder is None:
            backup_folder = os.path.join(args.input, "backup_subtitles")
            
        if args.restore:
            if not os.path.exists(backup_folder):
                logger.error(f"Thư mục backup '{backup_folder}' không tồn tại")
                return 1
                
            print(f"Đang khôi phục phụ đề gốc từ '{backup_folder}' vào '{args.input}'...")
            stats = restore_original_subtitles(args.input, args.backup)
            print_stats(stats, restore=True)
        else:
            print(f"Đang xóa phụ đề gốc và sao lưu vào '{backup_folder}'...")
            stats = backup_original_subtitles(args.input, args.backup, args.lang)
            print_stats(stats)
            
        return 0
    except Exception as e:
        logger.error(f"Lỗi: {str(e)}")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 