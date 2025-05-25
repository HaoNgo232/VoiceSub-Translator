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
        
        # Tách thành các chunk
        chunks = re.split(r'\n\s*\n', content.strip())
        result = []
        subtitle_index = 1
        
        for chunk in chunks:
            # Bỏ qua các dòng chỉ có NOTE hoặc rỗng
            if chunk.strip().startswith("NOTE") or not chunk.strip():
                continue
                
            # Xử lý các dòng trong chunk
            lines = chunk.strip().split('\n')
            timestamp_line = None
            text_lines = []
            
            for line in lines:
                line = line.strip()
                if '-->' in line:
                    timestamp_line = line
                elif line and not re.match(r'^\d+$', line):  # Bỏ qua dòng chỉ có số (số thứ tự cũ)
                    # Loại bỏ các thẻ HTML/VTT như <v ->, <v Speaker>, etc.
                    line = re.sub(r'<v[^>]*>', '', line)  # Loại bỏ thẻ mở <v ...>
                    line = re.sub(r'</v>', '', line)      # Loại bỏ thẻ đóng </v>
                    line = re.sub(r'<[^>]+>', '', line)   # Loại bỏ các thẻ HTML khác
                    line = line.strip()
                    if line:  # Chỉ thêm nếu dòng không rỗng sau khi loại bỏ thẻ
                        text_lines.append(line)
            
            if timestamp_line and text_lines:
                joined_text = '\n'.join(text_lines)
                result.append(f"{subtitle_index}\n{timestamp_line}\n{joined_text}")
                subtitle_index += 1
        
        return '\n\n'.join(result)