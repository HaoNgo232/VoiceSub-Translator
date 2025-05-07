#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import re
from pathlib import Path
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def srt_to_vtt(srt_content):
    """Chuyển đổi nội dung SRT sang VTT."""
    # Thay thế dấu phẩy bằng dấu chấm trong timestamp
    vtt_content = re.sub(r'(\d{2}:\d{2}:\d{2}),(\d{3})', r'\1.\2', srt_content)
    
    # Thêm header VTT
    vtt_content = 'WEBVTT\n\n' + vtt_content
    
    return vtt_content

def convert_subtitle(input_file, output_format='vtt'):
    """Chuyển đổi file phụ đề sang định dạng khác."""
    input_path = Path(input_file)
    
    if not input_path.exists():
        logger.error(f"Không tìm thấy file: {input_file}")
        return False
        
    try:
        # Đọc nội dung file
        with open(input_file, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # Chuyển đổi nội dung
        if output_format.lower() == 'vtt':
            converted_content = srt_to_vtt(content)
            output_file = input_path.with_suffix('.vtt')
        else:
            logger.error(f"Định dạng không được hỗ trợ: {output_format}")
            return False
            
        # Ghi file mới
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(converted_content)
            
        logger.info(f"Đã chuyển đổi thành công: {output_file}")
        return True
        
    except Exception as e:
        logger.error(f"Lỗi khi chuyển đổi file: {str(e)}")
        return False

def batch_convert(input_dir, output_format='vtt'):
    """Chuyển đổi hàng loạt file phụ đề."""
    input_dir = Path(input_dir)
    srt_files = list(input_dir.glob('*.srt'))
    
    if not srt_files:
        logger.warning(f"Không tìm thấy file SRT nào trong {input_dir}")
        return
        
    success_count = 0
    for srt_file in srt_files:
        if convert_subtitle(srt_file, output_format):
            success_count += 1
            
    logger.info(f"Đã chuyển đổi thành công {success_count}/{len(srt_files)} file")

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Chuyển đổi định dạng phụ đề")
    parser.add_argument("input", help="File hoặc thư mục cần chuyển đổi")
    parser.add_argument("--format", "-f", default="vtt", choices=["vtt"],
                      help="Định dạng đầu ra (hiện tại chỉ hỗ trợ VTT)")
    
    args = parser.parse_args()
    
    input_path = Path(args.input)
    if input_path.is_file():
        convert_subtitle(input_path, args.format)
    else:
        batch_convert(input_path, args.format) 