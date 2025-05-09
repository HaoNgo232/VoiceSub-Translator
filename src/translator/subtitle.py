import os
import logging
import time
import json
from typing import List, Optional, Dict, Tuple
from pathlib import Path
from ..api.handler import APIHandler
import concurrent.futures
import hashlib

# Cấu hình logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SubtitleTranslator:
    def __init__(self, api_handler: Optional[APIHandler] = None, cache_dir: str = None):
        """Khởi tạo SubtitleTranslator."""
        self.api_handler = api_handler or APIHandler()
        
        # Cấu hình cache
        self.use_cache = True
        self.cache_dir = cache_dir or os.path.join(os.path.expanduser("~"), ".subtitle_translator_cache")
        os.makedirs(self.cache_dir, exist_ok=True)
        logger.info(f"Sử dụng cache tại: {self.cache_dir}")
        
        # Số lần thử lại khi gặp lỗi do văn bản quá dài
        self.max_retries = 3
        # Hệ số chia văn bản (nếu gặp lỗi do văn bản quá dài)
        self.split_factor = 2
        
    def process_subtitle_file(self, input_file: str, output_file: str, target_lang: str = 'vi', service: str = 'novita', max_workers: int = 4) -> bool:
        """Xử lý file phụ đề và tạo bản dịch (song song nhiều block)."""
        start_time = time.time()
        try:
            # Đọc và chuẩn bị dữ liệu
            blocks, stats = self._prepare_subtitle_data(input_file)
            
            # Dịch các block
            translated_blocks, errors = self._translate_blocks(blocks, target_lang, service, max_workers, stats)
            
            # Xử lý và lưu kết quả
            success = self._process_and_save_results(translated_blocks, errors, blocks, output_file, service)
            
            # Log kết quả
            elapsed_time = time.time() - start_time
            logger.info(f"Đã dịch xong file {input_file} trong {elapsed_time:.2f}s: "
                       f"{stats['successful']}/{stats['total_blocks']} block thành công, "
                       f"{stats['cache_hits']} từ cache")
            return success
            
        except Exception as e:
            logger.error(f"Lỗi khi xử lý file phụ đề: {str(e)}")
            return False
            
    def _prepare_subtitle_data(self, input_file: str) -> Tuple[List[str], Dict]:
        """Đọc file phụ đề và chuẩn bị dữ liệu."""
        with open(input_file, 'r', encoding='utf-8') as f:
            content = f.read()
        blocks = self._split_into_blocks(content)
        logger.info(f"Đọc {len(blocks)} block từ file {input_file}")
        
        # Khởi tạo stats
        stats = {
            'total_blocks': len(blocks),
            'successful': 0,
            'failed': 0,
            'fallback_used': False,
            'cache_hits': 0
        }
        
        return blocks, stats
        
    def _translate_blocks(self, blocks: List[str], target_lang: str, service: str, max_workers: int, stats: Dict) -> Tuple[List[Optional[str]], List[Optional[str]]]:
        """Dịch các block phụ đề."""
        translated_blocks = [None] * len(blocks)
        errors = [None] * len(blocks)
        
        def translate_block_wrapper(idx, block):
            return self._translate_single_block(idx, block, target_lang, service, errors, stats)
            
        with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_idx = {executor.submit(translate_block_wrapper, i, block): i for i, block in enumerate(blocks)}
            for future in concurrent.futures.as_completed(future_to_idx):
                idx = future_to_idx[future]
                try:
                    translated_blocks[idx] = future.result()
                except Exception as e:
                    errors[idx] = f"Block {idx+1} lỗi: {str(e)}"
                    stats['failed'] += 1
                    
        return translated_blocks, errors
                
    def _translate_single_block(self, idx: int, block: str, target_lang: str, service: str, errors: List[Optional[str]], stats: Dict) -> Optional[str]:
        """Dịch một block phụ đề và cập nhật thống kê."""
        try:
            # Tách dữ liệu và tạo khóa cache
            block_lines = block.split('\n')
            if len(block_lines) < 3:
                errors[idx] = f"Block {idx+1} không đủ 3 dòng"
                return None
                
            number = block_lines[0]
            timestamp = block_lines[1]
            text = '\n'.join(block_lines[2:])
            
            # Kiểm tra cache trước khi dịch
            cache_key = self._generate_cache_key(text, target_lang, service)
            cached_result = self._get_from_cache(cache_key)
            
            if cached_result:
                stats['cache_hits'] += 1
                stats['successful'] += 1
                return f"{number}\n{timestamp}\n{cached_result}"
            
            # Dịch với retry nếu cần
            translated_text = self._translate_with_retry(text, target_lang, service)
            
            if not translated_text:
                errors[idx] = f"Block {idx+1} dịch lỗi hoặc rỗng"
                return None
                
            # Lưu kết quả vào cache
            self._save_to_cache(cache_key, translated_text)
            
            stats['successful'] += 1
            return f"{number}\n{timestamp}\n{translated_text}"
        except Exception as e:
            errors[idx] = f"Block {idx+1} lỗi: {str(e)}"
            stats['failed'] += 1
            return None
            
    def _process_and_save_results(self, translated_blocks: List[Optional[str]], errors: List[Optional[str]], blocks: List[str], output_file: str, service: str) -> bool:
        """Xử lý kết quả dịch và lưu vào file."""
        # Kiểm tra lỗi
        failed_blocks = [i for i, b in enumerate(translated_blocks) if b is None]
        if failed_blocks:
            logger.error(f"{len(failed_blocks)}/{len(blocks)} block dịch lỗi với provider {service}")
            # Nếu tất cả đều lỗi
            if len(failed_blocks) == len(blocks):
                logger.error(f"Tất cả block đều dịch lỗi với provider {service}")
                return False
            
            # Nếu một số block dịch thành công, vẫn lưu file kết quả
            # nhưng đánh dấu các block lỗi
            for i in failed_blocks:
                translated_blocks[i] = f"{i+1}\n00:00:00,000 --> 00:00:01,000\n[TRANSLATION ERROR FOR BLOCK {i+1}]"
            logger.warning(f"Lưu file với {len(failed_blocks)} block lỗi đã được đánh dấu")
            
        # Lưu kết quả
        translated_content = '\n\n'.join(filter(None, translated_blocks))
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(translated_content)
            
        return True
    
    def _generate_cache_key(self, text: str, target_lang: str, service: str) -> str:
        """Tạo khóa cache từ văn bản, ngôn ngữ đích và dịch vụ."""
        # Tạo hash từ text để rút ngắn key
        text_hash = hashlib.md5(text.encode('utf-8')).hexdigest()
        return f"{text_hash}_{target_lang}_{service}"
        
    def _get_cache_path(self, cache_key: str) -> str:
        """Tạo đường dẫn cache từ cache key."""
        return os.path.join(self.cache_dir, f"{cache_key}.json")
        
    def _get_from_cache(self, cache_key: str) -> Optional[str]:
        """Lấy kết quả dịch từ cache."""
        if not self.use_cache:
            return None
            
        cache_path = self._get_cache_path(cache_key)
        if os.path.exists(cache_path):
            try:
                with open(cache_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    return data.get('translation')
            except Exception as e:
                logger.warning(f"Lỗi khi đọc cache: {str(e)}")
        return None
        
    def _save_to_cache(self, cache_key: str, translation: str) -> bool:
        """Lưu kết quả dịch vào cache."""
        if not self.use_cache:
            return False
            
        cache_path = self._get_cache_path(cache_key)
        try:
            with open(cache_path, 'w', encoding='utf-8') as f:
                json.dump({'translation': translation}, f, ensure_ascii=False)
            return True
        except Exception as e:
            logger.warning(f"Lỗi khi lưu cache: {str(e)}")
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
        
    def _translate_with_retry(self, text: str, target_lang: str, service: str) -> Optional[str]:
        """Dịch văn bản với cơ chế thử lại khi gặp lỗi do văn bản quá dài."""
        retries = 0
        current_text = text
        
        while retries < self.max_retries:
            translated_text = self._try_translate(current_text, target_lang, service)
            if translated_text:
                return translated_text
                
            # Nếu không có lỗi cụ thể nhưng dịch thất bại
            if len(current_text) > 1000 and retries < self.max_retries - 1:
                result = self._translate_long_text(current_text, target_lang, service)
                if result:
                    return result
                    
            retries += 1
                
        return None
        
    def _try_translate(self, text: str, target_lang: str, service: str) -> Optional[str]:
        """Thử dịch văn bản và xử lý các ngoại lệ."""
        try:
            return self.api_handler.translate_text(text, target_lang, service)
            
        except Exception as e:
            # Kiểm tra lỗi do văn bản quá dài
            err_msg = str(e).lower()
            is_size_error = any(kw in err_msg for kw in ['too long', 'too many tokens', 'maximum context', 'too large'])
            
            if is_size_error and len(text) > 500:
                # Xử lý lỗi văn bản quá dài
                return self._handle_text_too_long(text, target_lang, service, e)
            else:
                # Lỗi khác, không thử lại
                logger.error(f"Lỗi khi dịch văn bản: {str(e)}")
                return None
                
    def _handle_text_too_long(self, text: str, target_lang: str, service: str, error: Exception) -> Optional[str]:
        """Xử lý trường hợp văn bản quá dài."""
        logger.info(f"Văn bản quá dài ({len(text)} ký tự), chia nhỏ và thử lại")
        parts = self._split_text(text, self.split_factor)
        
        return self._translate_text_parts(parts, target_lang, service)
        
    def _translate_text_parts(self, parts: List[str], target_lang: str, service: str) -> Optional[str]:
        """Dịch từng phần văn bản và kết hợp kết quả."""
        translated_parts = []
        
        for part in parts:
            try:
                part_translation = self.api_handler.translate_text(part, target_lang, service)
                if not part_translation:
                    logger.warning(f"Không thể dịch phần văn bản: {part[:50]}...")
                    return None
                translated_parts.append(part_translation)
            except Exception as part_error:
                logger.warning(f"Lỗi khi dịch phần văn bản: {str(part_error)}")
                return None
        
        if translated_parts:
            return ' '.join(translated_parts)
        return None
        
    def _translate_long_text(self, text: str, target_lang: str, service: str) -> Optional[str]:
        """Xử lý dịch văn bản dài bằng cách chia nhỏ chủ động."""
        parts = self._split_text(text, self.split_factor)
        translated_parts = []
        
        for part in parts:
            part_translation = self.api_handler.translate_text(part, target_lang, service)
            if not part_translation:
                return None
            translated_parts.append(part_translation)
            
        return ' '.join(translated_parts)
        
    def _split_text(self, text: str, split_factor: int) -> List[str]:
        """Chia văn bản thành các phần nhỏ hơn."""
        if split_factor <= 1:
            return [text]
            
        # Tìm vị trí tốt để chia (sau dấu chấm câu hoặc dấu xuống dòng)
        lines = text.split('\n')
        
        if len(lines) >= split_factor:
            return self._split_by_lines(lines, split_factor)
        else:
            return self._split_by_chars(text, split_factor)
    
    def _split_by_lines(self, lines: List[str], split_factor: int) -> List[str]:
        """Chia văn bản theo dòng."""
        chunk_size = len(lines) // split_factor
        return ['\n'.join(lines[i:i+chunk_size]) for i in range(0, len(lines), chunk_size)]
        
    def _split_by_chars(self, text: str, split_factor: int) -> List[str]:
        """Chia văn bản theo ký tự, cố gắng cắt tại vị trí hợp lý."""
        chunk_size = len(text) // split_factor
        parts = []
        
        for i in range(0, len(text), chunk_size):
            end = min(i + chunk_size, len(text))
            
            if end < len(text):
                best_pos = self._find_best_split_position(text, i, end, chunk_size)
                part = text[i:best_pos]
            else:
                part = text[i:end]
                
            parts.append(part)
            
        return parts
        
    def _find_best_split_position(self, text: str, start: int, end: int, chunk_size: int) -> int:
        """Tìm vị trí tốt nhất để cắt văn bản."""
        break_chars = ['. ', '! ', '? ', '; ', '\n']
        best_pos = end
        
        # Tìm vị trí tốt trong khoảng ±20% chunk_size
        search_start = max(start + chunk_size - int(0.2 * chunk_size), start)
        search_end = min(start + chunk_size + int(0.2 * chunk_size), len(text))
        
        for pos in range(search_start, search_end):
            for char in break_chars:
                if pos + len(char) <= len(text) and text[pos:pos+len(char)] == char:
                    return pos + len(char)
                    
        return best_pos
        
    def _translate_block(self, block: str, target_lang: str, service: str) -> Optional[str]:
        """Dịch một block phụ đề."""
        try:
            # Tách số thứ tự và timestamp
            lines = block.split('\n')
            if len(lines) < 3:
                logger.warning(f"Block không đủ 3 dòng, bỏ qua: {block}")
                return None
                
            number = lines[0]
            timestamp = lines[1]
            text = '\n'.join(lines[2:])
            
            # Dịch text với backup providers nếu cần
            translated_text = self._translate_with_retry(text, target_lang, service)
            if not translated_text:
                logger.error(f"Không thể dịch block với provider {service}")
                return None
                
            # Ghép lại thành block
            return f"{number}\n{timestamp}\n{translated_text}"
            
        except Exception as e:
            logger.error(f"Lỗi khi dịch block: {str(e)}")
            return None
            
    def process_directory(self, input_dir: str, output_dir: str, target_lang: str = 'vi', service: str = 'google', max_workers: int = 4) -> Dict[str, int]:
        """Xử lý tất cả các file phụ đề trong thư mục (song song nhiều file)."""
        start_time = time.time()
        results = {
            'total': 0,
            'success': 0,
            'failed': 0
        }
        try:
            os.makedirs(output_dir, exist_ok=True)
            srt_files = [f for f in os.listdir(input_dir) if f.endswith('.srt')]
            results['total'] = len(srt_files)
            
            logger.info(f"Bắt đầu xử lý {len(srt_files)} file phụ đề với {max_workers} luồng")
            
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
                        
            elapsed_time = time.time() - start_time
            logger.info(f"Hoàn thành xử lý {results['total']} file trong {elapsed_time:.2f}s: "
                      f"{results['success']} thành công, {results['failed']} thất bại")
            return results
        except Exception as e:
            logger.error(f"Lỗi khi xử lý thư mục: {str(e)}")
            return results 