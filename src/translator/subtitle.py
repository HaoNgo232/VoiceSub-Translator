import os
import logging
from typing import List, Optional, Dict
from pathlib import Path
from ..api.handler import APIHandler

# Cấu hình logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SubtitleProcessor:
    def __init__(self, api_handler: Optional[APIHandler] = None):
        """Khởi tạo SubtitleProcessor."""
        self.api_handler = api_handler or APIHandler()
        
    def process_subtitle_file(self, input_file: str, output_file: str, target_lang: str = 'vi', service: str = 'google') -> bool:
        """Xử lý file phụ đề và tạo bản dịch."""
        try:
            # Đọc file phụ đề
            with open(input_file, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # Tách thành các block
            blocks = self._split_into_blocks(content)
            
            # Dịch từng block
            translated_blocks = []
            for block in blocks:
                translated_block = self._translate_block(block, target_lang, service)
                if translated_block:
                    translated_blocks.append(translated_block)
                else:
                    logger.error(f"Không thể dịch block: {block}")
                    return False
                    
            # Ghép các block đã dịch
            translated_content = '\n\n'.join(translated_blocks)
            
            # Lưu file kết quả
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(translated_content)
                
            return True
            
        except Exception as e:
            logger.error(f"Lỗi khi xử lý file phụ đề: {str(e)}")
            return False
            
    def _split_into_blocks(self, content: str) -> List[str]:
        """Tách nội dung thành các block phụ đề."""
        blocks = []
        current_block = []
        
        for line in content.split('\n'):
            line = line.strip()
            if not line:
                if current_block:
                    blocks.append('\n'.join(current_block))
                    current_block = []
            else:
                current_block.append(line)
                
        if current_block:
            blocks.append('\n'.join(current_block))
            
        return blocks
        
    def _translate_block(self, block: str, target_lang: str, service: str) -> Optional[str]:
        """Dịch một block phụ đề."""
        try:
            # Tách số thứ tự và timestamp
            lines = block.split('\n')
            if len(lines) < 3:
                return None
                
            number = lines[0]
            timestamp = lines[1]
            text = '\n'.join(lines[2:])
            
            # Dịch text
            translated_text = self.api_handler.translate_text(text, target_lang, service)
            if not translated_text:
                return None
                
            # Ghép lại thành block
            return f"{number}\n{timestamp}\n{translated_text}"
            
        except Exception as e:
            logger.error(f"Lỗi khi dịch block: {str(e)}")
            return None
            
    def process_directory(self, input_dir: str, output_dir: str, target_lang: str = 'vi', service: str = 'google') -> Dict[str, int]:
        """Xử lý tất cả các file phụ đề trong thư mục."""
        results = {
            'total': 0,
            'success': 0,
            'failed': 0
        }
        
        try:
            # Tạo thư mục output nếu chưa tồn tại
            os.makedirs(output_dir, exist_ok=True)
            
            # Xử lý từng file
            for file in os.listdir(input_dir):
                if file.endswith('.srt'):
                    results['total'] += 1
                    
                    input_path = os.path.join(input_dir, file)
                    output_path = os.path.join(output_dir, file)
                    
                    if self.process_subtitle_file(input_path, output_path, target_lang, service):
                        results['success'] += 1
                    else:
                        results['failed'] += 1
                        
            return results
            
        except Exception as e:
            logger.error(f"Lỗi khi xử lý thư mục: {str(e)}")
            return results 