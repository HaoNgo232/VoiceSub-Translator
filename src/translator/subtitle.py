import os
import logging
import time
import json
from typing import List, Optional, Dict, Tuple
from pathlib import Path
import concurrent.futures
import hashlib

# Import động tránh vòng lặp import
# Sử dụng typing.TYPE_CHECKING cho type annotation

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SubtitleTranslator:
    def __init__(
        self, 
        api_handler=None, 
        cache_manager=None,
        translator_service=None,
        subtitle_processor=None,
        cache_dir: str = None
    ):
        """Khởi tạo SubtitleTranslator.
        
        Args:
            api_handler: Đối tượng xử lý API
            cache_manager: Đối tượng quản lý cache
            translator_service: Dịch vụ dịch thuật
            subtitle_processor: Đối tượng xử lý phụ đề
            cache_dir: Thư mục lưu cache
        """
        # Import động để tránh vòng lặp import
        # Import khi cần thiết
        if api_handler is None:
            from ..api.handler import APIHandler
            api_handler = APIHandler()

        if cache_manager is None:
            from ..utils.cache_manager import TranslationCacheManager
            cache_manager = TranslationCacheManager(cache_dir)

        if translator_service is None:
            from .translator_service import APITranslatorService
            translator_service = APITranslatorService(api_handler, cache_manager)

        if subtitle_processor is None:
            from .subtitle_processor import SubtitleProcessor
            subtitle_processor = SubtitleProcessor()
            
        # Lưu các dependencies
        self.api_handler = api_handler
        self.cache_manager = cache_manager
        self.translator_service = translator_service
        self.subtitle_processor = subtitle_processor
        
    def process_subtitle_file(self, input_file: str, output_file: str, target_lang: str = 'vi', service: str = 'novita', max_workers: int = 10) -> bool:
        """Xử lý file phụ đề và tạo bản dịch (song song nhiều block).
        
        Args:
            input_file: Đường dẫn file phụ đề đầu vào
            output_file: Đường dẫn file phụ đề đầu ra
            target_lang: Ngôn ngữ đích (mặc định: vi)
            service: Dịch vụ dịch thuật sử dụng
            max_workers: Số luồng xử lý tối đa
            
        Returns:
            True nếu thành công, False nếu thất bại
        """
        start_time = time.time()
        try:
            # Đọc nội dung file phụ đề
            content = self.subtitle_processor.read_subtitle_file(input_file)
            
            # Tách thành các block
            blocks = self.subtitle_processor.split_into_blocks(content)
            
            # Khởi tạo thống kê
            stats = {
                'total_blocks': len(blocks),
                'successful': 0,
                'failed': 0,
                'cache_hits': 0
            }
            
            # Dịch các block song song
            translated_blocks, errors = self._translate_blocks_parallel(
                blocks, target_lang, service, max_workers, stats
            )
            
            # Xử lý và lưu kết quả
            success = self._process_and_save_results(
                translated_blocks, errors, blocks, output_file
            )
            
            # Log kết quả
            elapsed_time = time.time() - start_time
            logger.info(f"Đã dịch xong file {input_file} trong {elapsed_time:.2f}s: "
                       f"{stats['successful']}/{stats['total_blocks']} block thành công, "
                       f"{stats['cache_hits']} từ cache")
            return success
            
        except Exception as e:
            logger.error(f"Lỗi khi xử lý file phụ đề: {str(e)}")
            return False
    
    def _translate_blocks_parallel(
        self, 
        blocks: List[str], 
        target_lang: str, 
        service: str, 
        max_workers: int,
        stats: Dict
    ) -> Tuple[List[Optional[str]], List[Optional[str]]]:
        """Dịch các block phụ đề song song.
        
        Args:
            blocks: Danh sách các block phụ đề
            target_lang: Ngôn ngữ đích
            service: Dịch vụ dịch thuật
            max_workers: Số luồng tối đa
            stats: Từ điển lưu thông tin thống kê
            
        Returns:
            Tuple (danh sách block đã dịch, danh sách lỗi)
        """
        translated_blocks = [None] * len(blocks)
        errors = [None] * len(blocks)
        
        def translate_block_wrapper(idx, block):
            try:
                # Phân tách block
                number, timestamp, text = self.subtitle_processor.parse_subtitle_block(block)
                
                # Kiểm tra cache
                cache_key = self.cache_manager.generate_key(text, target_lang=target_lang, service=service)
                cached_result = self.cache_manager.get(cache_key)
                
                if cached_result:
                    stats['cache_hits'] += 1
                    stats['successful'] += 1
                    return self.subtitle_processor.create_subtitle_block(number, timestamp, cached_result)
                
                # Dịch văn bản
                translated_text = self.translator_service.translate_text(text, target_lang, service)
                
                if not translated_text:
                    errors[idx] = f"Block {idx+1} dịch lỗi hoặc rỗng"
                    return None
                    
                # Lưu kết quả vào cache
                self.cache_manager.set(cache_key, translated_text)
                
                stats['successful'] += 1
                return self.subtitle_processor.create_subtitle_block(number, timestamp, translated_text)
                
            except Exception as e:
                errors[idx] = f"Block {idx+1} lỗi: {str(e)}"
                stats['failed'] += 1
                return None
        
        # Sử dụng ThreadPoolExecutor để dịch song song
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
                
    def _process_and_save_results(
        self, 
        translated_blocks: List[Optional[str]], 
        errors: List[Optional[str]], 
        original_blocks: List[str], 
        output_file: str
    ) -> bool:
        """Xử lý kết quả dịch và lưu vào file.
        
        Args:
            translated_blocks: Danh sách các block đã dịch
            errors: Danh sách lỗi
            original_blocks: Danh sách các block gốc
            output_file: Đường dẫn file đầu ra
            
        Returns:
            True nếu thành công, False nếu thất bại
        """
        # Kiểm tra lỗi
        failed_blocks = [i for i, b in enumerate(translated_blocks) if b is None]
        
        if failed_blocks:
            logger.error(f"{len(failed_blocks)}/{len(original_blocks)} block dịch lỗi")
            
            # Nếu tất cả đều lỗi
            if len(failed_blocks) == len(original_blocks):
                logger.error("Tất cả block đều dịch lỗi")
                return False
            
            # Nếu một số block dịch thành công, vẫn lưu file kết quả
            # nhưng đánh dấu các block lỗi
            for i in failed_blocks:
                number = str(i+1)
                translated_blocks[i] = self.subtitle_processor.create_subtitle_block(
                    number, 
                    "00:00:00,000 --> 00:00:01,000", 
                    f"[TRANSLATION ERROR FOR BLOCK {i+1}]"
                )
            logger.warning(f"Lưu file với {len(failed_blocks)} block lỗi đã được đánh dấu")
            
        # Đánh số lại các block và ghép lại
        renumbered_blocks = self.subtitle_processor.renumber_subtitle_blocks(translated_blocks)
        translated_content = self.subtitle_processor.merge_subtitle_blocks(renumbered_blocks)
        
        # Ghi ra file
        if self.subtitle_processor.write_subtitle_file(output_file, translated_content):
            logger.info(f"Đã lưu phụ đề dịch vào: {output_file}")
            return True
        else:
            logger.error(f"Lỗi khi lưu file {output_file}")
            return False
            
    def process_directory(self, input_dir: str, output_dir: str, target_lang: str = 'vi', service: str = 'novita', max_workers: int = 4) -> Dict[str, int]:
        """Xử lý toàn bộ thư mục chứa file phụ đề.
        
        Args:
            input_dir: Thư mục đầu vào
            output_dir: Thư mục đầu ra
            target_lang: Ngôn ngữ đích
            service: Dịch vụ dịch thuật
            max_workers: Số luồng xử lý tối đa cho mỗi file
            
        Returns:
            Từ điển thống kê kết quả
        """
        os.makedirs(output_dir, exist_ok=True)
        
        # Tìm tất cả file .srt trong thư mục
        input_files = list(Path(input_dir).glob('**/*.srt'))
        
        stats = {
            'total_files': len(input_files),
            'successful': 0,
            'failed': 0,
            'skipped': 0
        }
        
        # Xử lý từng file
        for input_file in input_files:
            # Tạo đường dẫn output tương ứng
            rel_path = input_file.relative_to(input_dir)
            output_file = Path(output_dir) / rel_path
            os.makedirs(output_file.parent, exist_ok=True)
            
            logger.info(f"Đang xử lý: {input_file}")
            
            # Kiểm tra file đã tồn tại
            if output_file.exists():
                logger.info(f"File {output_file} đã tồn tại, bỏ qua")
                stats['skipped'] += 1
                continue
                
            # Xử lý file
            success = self.process_subtitle_file(
                str(input_file), 
                str(output_file), 
                target_lang, 
                service, 
                max_workers
            )
            
            if success:
                stats['successful'] += 1
            else:
                stats['failed'] += 1
                
        logger.info(f"Kết quả xử lý thư mục: {stats['successful']}/{stats['total_files']} file thành công")
        return stats 