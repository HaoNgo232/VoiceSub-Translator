#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Provider chuyển đổi từ định dạng VTT sang SRT
"""

import re
from ..converter import SubtitleFormatConverter

class VttProvider(SubtitleFormatConverter):
    """
    Provider chuyển đổi từ định dạng VTT sang SRT
    """
    
    # Phần mở rộng của định dạng VTT
    extension = ".vtt"
    
    def detect_format(self, content: str) -> bool:
        """
        Kiểm tra nội dung có phải định dạng VTT không
        
        Args:
            content: Nội dung cần kiểm tra
            
        Returns:
            True nếu đúng định dạng VTT, False nếu không
        """
        return content.strip().startswith("WEBVTT")
    
    def convert_to_srt(self, content: str) -> str:
        """
        Chuyển đổi nội dung VTT sang SRT
        
        Args:
            content: Nội dung VTT cần chuyển đổi
            
        Returns:
            Nội dung ở định dạng SRT
        """
        # Loại bỏ header WEBVTT
        content = re.sub(r'^WEBVTT\s*\n', '', content)
        
        # Chuyển đổi timestamp từ dạng dấu chấm sang dấu phẩy
        content = re.sub(r'(\d{2}:\d{2}:\d{2})\.(\d{3})', r'\1,\2', content)
        
        # Thêm số thứ tự cho mỗi đoạn phụ đề
        chunks = re.split(r'\n\s*\n', content.strip())
        result = []
        
        for i, chunk in enumerate(chunks, 1):
            # Bỏ qua các dòng chỉ có NOTE
            if chunk.strip().startswith("NOTE") or not chunk.strip():
                continue
                
            # Xử lý các dòng có timestamp
            lines = chunk.strip().split('\n')
            timestamp_line = None
            text_lines = []
            
            for line in lines:
                if '-->' in line:
                    timestamp_line = line.strip()
                elif line.strip():
                    text_lines.append(line.strip())
            
            if timestamp_line and text_lines:
                joined_text = '\n'.join(text_lines)
                result.append(f"{i}\n{timestamp_line}\n{joined_text}")
        
        return '\n\n'.join(result)