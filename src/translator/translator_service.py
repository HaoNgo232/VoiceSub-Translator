"""
Các giao diện và triển khai cho dịch vụ dịch thuật
"""

from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any
import logging

from ..api.handler import APIHandler
from ..utils.cache_manager import CacheManager, TranslationCacheManager

logger = logging.getLogger(__name__)

class TranslatorService(ABC):
    """Giao diện cho dịch vụ dịch thuật"""
    
    @abstractmethod
    def translate_text(self, text: str, target_lang: str, service: str) -> Optional[str]:
        """Dịch một đoạn văn bản"""
        pass
        
    @abstractmethod
    def translate_batch(self, texts: List[str], target_lang: str, service: str) -> List[Optional[str]]:
        """Dịch hàng loạt nhiều đoạn văn bản"""
        pass

class APITranslatorService(TranslatorService):
    """Triển khai dịch vụ dịch thuật sử dụng API"""
    
    def __init__(self, api_handler: Optional[APIHandler] = None, cache_manager: Optional[CacheManager] = None):
        """Khởi tạo dịch vụ dịch thuật
        
        Args:
            api_handler: Trình xử lý API
            cache_manager: Trình quản lý cache
        """
        self.api_handler = api_handler or APIHandler()
        self.cache_manager = cache_manager or TranslationCacheManager()
        
        # Cấu hình dịch thuật
        self.max_retries = 3
        self.split_factor = 2

    def translate_text(self, text: str, target_lang: str, service: str) -> Optional[str]:
        """Dịch một đoạn văn bản
        
        Args:
            text: Văn bản cần dịch
            target_lang: Ngôn ngữ đích
            service: Tên dịch vụ API
            
        Returns:
            Văn bản đã dịch hoặc None nếu có lỗi
        """
        # Kiểm tra cache trước
        cache_key = self.cache_manager.generate_key(text, target_lang=target_lang, service=service)
        cached_result = self.cache_manager.get(cache_key)
        
        if cached_result:
            logger.debug(f"Sử dụng kết quả từ cache cho dịch vụ {service}")
            return cached_result
            
        # Nếu không có trong cache, dịch với retry nếu cần
        translated_text = self._translate_with_retry(text, target_lang, service)
        
        # Lưu kết quả vào cache nếu thành công
        if translated_text:
            self.cache_manager.set(cache_key, translated_text)
            
        return translated_text
    
    def translate_batch(self, texts: List[str], target_lang: str, service: str) -> List[Optional[str]]:
        """Dịch hàng loạt nhiều đoạn văn bản
        
        Args:
            texts: Danh sách văn bản cần dịch
            target_lang: Ngôn ngữ đích
            service: Tên dịch vụ API
            
        Returns:
            Danh sách các văn bản đã dịch (None cho các mục lỗi)
        """
        results = []
        
        for text in texts:
            result = self.translate_text(text, target_lang, service)
            results.append(result)
            
        return results
            
    def _translate_with_retry(self, text: str, target_lang: str, service: str) -> Optional[str]:
        """Thử dịch văn bản với số lần thử lại
        
        Args:
            text: Văn bản cần dịch
            target_lang: Ngôn ngữ đích
            service: Tên dịch vụ API
            
        Returns:
            Văn bản đã dịch hoặc None nếu thất bại
        """
        for attempt in range(self.max_retries):
            try:
                return self._try_translate(text, target_lang, service)
            except Exception as e:
                error_msg = str(e).lower()
                
                # Xử lý trường hợp văn bản quá dài
                if "too long" in error_msg or "maximum context" in error_msg or "token limit" in error_msg:
                    logger.warning(f"Văn bản quá dài, thử chia nhỏ (lần {attempt+1}/{self.max_retries})")
                    result = self._handle_text_too_long(text, target_lang, service, e)
                    if result:
                        return result
                else:
                    logger.warning(f"Lỗi khi dịch (lần {attempt+1}/{self.max_retries}): {str(e)}")
                    
                # Nếu đây là lần thử cuối cùng
                if attempt == self.max_retries - 1:
                    logger.error(f"Đã thử {self.max_retries} lần và thất bại")
                    return None
                    
        return None
                
    def _try_translate(self, text: str, target_lang: str, service: str) -> Optional[str]:
        """Thực hiện dịch thuật không có retry
        
        Args:
            text: Văn bản cần dịch
            target_lang: Ngôn ngữ đích 
            service: Tên dịch vụ
            
        Returns:
            Văn bản đã dịch
            
        Raises:
            Exception: Nếu có lỗi từ API
        """
        if not text.strip():
            return ""
            
        result = self.api_handler.translate(text, target_lang, service)
        if not result:
            raise Exception(f"Kết quả dịch rỗng từ dịch vụ {service}")
            
        return result
            
    def _handle_text_too_long(self, text: str, target_lang: str, service: str, error: Exception) -> Optional[str]:
        """Xử lý trường hợp văn bản quá dài
        
        Args:
            text: Văn bản gốc
            target_lang: Ngôn ngữ đích
            service: Tên dịch vụ
            error: Lỗi gốc
            
        Returns:
            Văn bản đã dịch hoặc None nếu thất bại
        """
        # Thử chia văn bản
        return self._translate_long_text(text, target_lang, service)
            
    def _translate_long_text(self, text: str, target_lang: str, service: str) -> Optional[str]:
        """Dịch văn bản dài bằng cách chia nhỏ
        
        Args:
            text: Văn bản dài
            target_lang: Ngôn ngữ đích
            service: Tên dịch vụ
            
        Returns:
            Văn bản đã dịch hoặc None nếu thất bại
        """
        parts = self._split_text(text, self.split_factor)
        logger.info(f"Chia văn bản thành {len(parts)} phần")
        
        return self._translate_text_parts(parts, target_lang, service)
    
    def _translate_text_parts(self, parts: List[str], target_lang: str, service: str) -> Optional[str]:
        """Dịch và ghép các phần của văn bản
        
        Args:
            parts: Các phần văn bản
            target_lang: Ngôn ngữ đích
            service: Tên dịch vụ
            
        Returns:
            Văn bản đã dịch hoặc None nếu thất bại
        """
        translated_parts = []
        
        for i, part in enumerate(parts):
            try:
                logger.info(f"Đang dịch phần {i+1}/{len(parts)}")
                translated = self._try_translate(part, target_lang, service)
                if translated:
                    translated_parts.append(translated)
                else:
                    logger.error(f"Phần {i+1} dịch thất bại")
                    return None
            except Exception as e:
                logger.error(f"Lỗi khi dịch phần {i+1}: {str(e)}")
                return None
                
        return "\n".join(translated_parts)
    
    def _split_text(self, text: str, split_factor: int) -> List[str]:
        """Chia văn bản thành các phần nhỏ hơn
        
        Args:
            text: Văn bản cần chia
            split_factor: Hệ số chia
            
        Returns:
            Danh sách các phần văn bản
        """
        # Chia theo dòng
        lines = text.split('\n')
        
        if len(lines) > 1:
            return self._split_by_lines(lines, split_factor)
        else:
            # Nếu chỉ có 1 dòng, chia theo ký tự
            return self._split_by_chars(text, split_factor)
            
    def _split_by_lines(self, lines: List[str], split_factor: int) -> List[str]:
        """Chia văn bản theo dòng
        
        Args:
            lines: Danh sách dòng
            split_factor: Hệ số chia
            
        Returns:
            Danh sách các phần văn bản
        """
        parts_count = split_factor
        lines_per_part = max(1, len(lines) // parts_count)
        
        parts = []
        for i in range(0, len(lines), lines_per_part):
            parts.append('\n'.join(lines[i:i+lines_per_part]))
            
        return parts
            
    def _split_by_chars(self, text: str, split_factor: int) -> List[str]:
        """Chia văn bản theo ký tự
        
        Args:
            text: Văn bản cần chia
            split_factor: Hệ số chia
            
        Returns:
            Danh sách các phần văn bản
        """
        parts_count = split_factor
        chars_per_part = max(10, len(text) // parts_count)
        
        parts = []
        current_pos = 0
        
        while current_pos < len(text):
            # Tìm vị trí tốt nhất để cắt
            if current_pos + chars_per_part >= len(text):
                # Phần cuối cùng
                end_pos = len(text)
            else:
                end_pos = self._find_best_split_position(text, current_pos, current_pos + chars_per_part, chars_per_part)
                
            parts.append(text[current_pos:end_pos])
            current_pos = end_pos
            
        return parts
    
    def _find_best_split_position(self, text: str, start: int, end: int, chunk_size: int) -> int:
        """Tìm vị trí tốt nhất để chia văn bản
        
        Args:
            text: Văn bản gốc
            start: Vị trí bắt đầu
            end: Vị trí kết thúc dự kiến
            chunk_size: Kích thước mỗi phần
            
        Returns:
            Vị trí tốt nhất để cắt
        """
        # Ưu tiên cắt ở các dấu câu hoặc khoảng trắng
        priority_chars = ['.', '!', '?', '\n', ';', ',', ' ']
        
        # Tìm trong khoảng ±10% của end
        search_start = max(start + int(chunk_size * 0.9), start)
        search_end = min(end + int(chunk_size * 0.1), len(text))
        
        for char in priority_chars:
            pos = text.rfind(char, search_start, search_end)
            if pos != -1:
                return pos + 1  # Vị trí sau dấu
                
        # Nếu không tìm thấy vị trí lý tưởng, trả về end
        return end 