import os
import logging
from typing import List, Optional, Dict
from pathlib import Path
from ..api.handler import APIHandler
import concurrent.futures

# Cấu hình logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SubtitleTranslator:
    def __init__(self, api_handler: Optional[APIHandler] = None):
        """Khởi tạo SubtitleTranslator."""
        self.api_handler = api_handler or APIHandler()
        
    def process_subtitle_file(self, input_file: str, output_file: str, target_lang: str = 'vi', service: str = 'novita', max_workers: int = 4) -> bool:
        """Xử lý file phụ đề và tạo bản dịch (song song nhiều block)."""
        try:
            with open(input_file, 'r', encoding='utf-8') as f:
                content = f.read()
            blocks = self._split_into_blocks(content)
            translated_blocks = [None] * len(blocks)
            errors = [None] * len(blocks)
            def translate_block_wrapper(idx, block):
                try:
                    result = self._translate_block(block, target_lang, service)
                    if result is None:
                        errors[idx] = f"Block {idx+1} dịch lỗi hoặc rỗng"
                    return result
                except Exception as e:
                    errors[idx] = f"Block {idx+1} lỗi: {str(e)}"
                    return None
            with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
                future_to_idx = {executor.submit(translate_block_wrapper, i, block): i for i, block in enumerate(blocks)}
                for future in concurrent.futures.as_completed(future_to_idx):
                    idx = future_to_idx[future]
                    try:
                        translated_blocks[idx] = future.result()
                    except Exception as e:
                        errors[idx] = f"Block {idx+1} lỗi: {str(e)}"
            # Kiểm tra lỗi
            if any(b is None for b in translated_blocks):
                logger.error(f"Một số block dịch lỗi: {errors}")
                return False
            translated_content = '\n\n'.join(translated_blocks)
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
            
    def process_directory(self, input_dir: str, output_dir: str, target_lang: str = 'vi', service: str = 'google', max_workers: int = 4) -> Dict[str, int]:
        """Xử lý tất cả các file phụ đề trong thư mục (song song nhiều file)."""
        results = {
            'total': 0,
            'success': 0,
            'failed': 0
        }
        try:
            os.makedirs(output_dir, exist_ok=True)
            srt_files = [f for f in os.listdir(input_dir) if f.endswith('.srt')]
            results['total'] = len(srt_files)
            def process_one_file(file):
                input_path = os.path.join(input_dir, file)
                output_path = os.path.join(output_dir, file)
                ok = self.process_subtitle_file(input_path, output_path, target_lang, service, max_workers=max_workers)
                return (file, ok)
            with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
                future_to_file = {executor.submit(process_one_file, file): file for file in srt_files}
                for future in concurrent.futures.as_completed(future_to_file):
                    file = future_to_file[future]
                    try:
                        _, ok = future.result()
                        if ok:
                            results['success'] += 1
                        else:
                            results['failed'] += 1
                    except Exception as e:
                        logger.error(f"Lỗi khi dịch file {file}: {str(e)}")
                        results['failed'] += 1
            return results
        except Exception as e:
            logger.error(f"Lỗi khi xử lý thư mục: {str(e)}")
            return results 