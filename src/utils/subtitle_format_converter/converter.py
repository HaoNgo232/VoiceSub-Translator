#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Module chính xử lý chuyển đổi định dạng phụ đề
"""

import os
import logging
from pathlib import Path
from abc import ABC, abstractmethod
from typing import Dict, List, Type, Optional

# Import các provider
from .providers import get_all_providers

# Cấu hình logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SubtitleFormatConverter(ABC):
    """
    Lớp trừu tượng cho các converter định dạng phụ đề
    """
    
    # Phần mở rộng của định dạng phụ đề (sẽ được ghi đè bởi lớp con)
    extension = ""
    
    @abstractmethod
    def convert_to_srt(self, content: str) -> str:
        """
        Chuyển đổi nội dung phụ đề sang định dạng SRT
        
        Args:
            content: Nội dung phụ đề cần chuyển đổi
            
        Returns:
            Nội dung phụ đề ở định dạng SRT
        """
        pass
    
    @abstractmethod
    def detect_format(self, content: str) -> bool:
        """
        Kiểm tra xem nội dung có phải định dạng phụ đề này không
        
        Args:
            content: Nội dung phụ đề cần kiểm tra
            
        Returns:
            True nếu đúng định dạng, False nếu không
        """
        pass
    
    @classmethod
    def get_extension(cls) -> str:
        """
        Trả về phần mở rộng của định dạng phụ đề
        
        Returns:
            Phần mở rộng của định dạng phụ đề (bao gồm dấu chấm)
        """
        return cls.extension


def convert_to_srt(input_file: str, output_file: Optional[str] = None) -> bool:
    """
    Chuyển đổi file phụ đề sang định dạng SRT
    
    Args:
        input_file: Đường dẫn đến file phụ đề cần chuyển đổi
        output_file: Đường dẫn file SRT đầu ra (mặc định là cùng tên với đuôi .srt)
        
    Returns:
        bool: True nếu thành công, False nếu thất bại
    """
    input_path = Path(input_file)
    
    if not input_path.exists():
        logger.error(f"Không tìm thấy file: {input_file}")
        return False
    
    # Tạo đường dẫn output nếu không được chỉ định
    if output_file is None:
        output_file = str(input_path.with_suffix('.srt'))
    
    try:
        # Đọc nội dung file
        with open(input_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Lấy danh sách tất cả các provider
        providers = get_all_providers()
        
        # Tìm provider phù hợp với định dạng file
        converter = None
        for provider_class in providers:
            if input_path.suffix.lower() == provider_class.get_extension():
                converter = provider_class()
                if converter.detect_format(content):
                    break
                converter = None
        
        if not converter:
            logger.error(f"Không hỗ trợ định dạng file: {input_file}")
            return False
        
        # Chuyển đổi nội dung
        srt_content = converter.convert_to_srt(content)
        
        # Ghi file mới
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(srt_content)
        
        logger.info(f"Đã chuyển đổi thành công: {output_file}")
        return True
        
    except Exception as e:
        logger.error(f"Lỗi khi chuyển đổi file: {str(e)}")
        return False


def batch_convert_to_srt(input_dir: str) -> None:
    """
    Chuyển đổi hàng loạt file phụ đề trong thư mục sang định dạng SRT
    
    Args:
        input_dir: Đường dẫn thư mục chứa các file phụ đề cần chuyển đổi
    """
    input_dir = Path(input_dir)
    providers = get_all_providers()
    
    # Lấy danh sách tất cả các định dạng được hỗ trợ
    supported_extensions = [provider.get_extension() for provider in providers]
    subtitle_files = []
    
    for ext in supported_extensions:
        subtitle_files.extend(list(input_dir.glob(f'**/*{ext}')))
    
    if not subtitle_files:
        extensions_str = ', '.join(supported_extensions)
        logger.warning(f"Không tìm thấy file phụ đề nào ({extensions_str}) trong {input_dir}")
        return
    
    success_count = 0
    for subtitle_file in subtitle_files:
        if convert_to_srt(str(subtitle_file)):
            success_count += 1
    
    logger.info(f"Đã chuyển đổi thành công {success_count}/{len(subtitle_files)} file")