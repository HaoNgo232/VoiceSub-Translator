"""Utilities for managing cached translations.

Cache files are stored as JSON with the following structure::

    {
        "translation": "<translated text>",
        "timestamp": "<ISO 8601 datetime>"
    }

The ``timestamp`` field records when the cache entry was created and is
ignored by :meth:`get` but used by :meth:`clear_expired` to remove old
entries.
"""

from abc import ABC, abstractmethod
import os
import json
import logging
import hashlib
from typing import Optional, Dict, Any
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class CacheManager(ABC):
    """Giao diện quản lý cache cho các dịch vụ của ứng dụng"""
    
    @abstractmethod
    def get(self, key: str) -> Optional[Any]:
        """Lấy giá trị từ cache theo key"""
        pass
        
    @abstractmethod
    def set(self, key: str, value: Any) -> bool:
        """Lưu giá trị vào cache"""
        pass
        
    @abstractmethod
    def generate_key(self, data: Any, **kwargs) -> str:
        """Tạo khóa cache từ dữ liệu"""
        pass
        
    @abstractmethod
    def clear(self, pattern: Optional[str] = None) -> bool:
        """Xóa cache (theo pattern nếu có)"""
        pass

class TranslationCacheManager(CacheManager):
    """Triển khai cụ thể của CacheManager cho việc lưu cache bản dịch"""
    
    def __init__(self, cache_dir: Optional[str] = None, use_cache: bool = True):
        """Khởi tạo TranslationCacheManager
        
        Args:
            cache_dir: Thư mục lưu cache
            use_cache: Bật/tắt sử dụng cache
        """
        self.use_cache = use_cache
        self.cache_dir = cache_dir or os.path.join(os.path.expanduser("~"), ".subtitle_translator_cache")
        self.cache_expiry = timedelta(days=7)  # Cache hết hạn sau 7 ngày
        os.makedirs(self.cache_dir, exist_ok=True)
        logger.info(f"Sử dụng cache tại: {self.cache_dir}")
        
    def get(self, key: str) -> Optional[str]:
        """Lấy bản dịch từ cache
        
        Args:
            key: Khóa cache
            
        Returns:
            Nội dung bản dịch hoặc None nếu không tìm thấy
        """
        if not self.use_cache:
            return None
            
        cache_path = self._get_cache_path(key)
        if os.path.exists(cache_path):
            try:
                with open(cache_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    _ = data.get('timestamp')  # timestamp is ignored during retrieval
                    return data.get('translation')
            except Exception as e:
                logger.warning(f"Lỗi khi đọc cache: {str(e)}")
        return None
        
    def set(self, key: str, value: str) -> bool:
        """Lưu bản dịch vào cache
        
        Args:
            key: Khóa cache
            value: Nội dung bản dịch
            
        Returns:
            True nếu lưu thành công, False nếu thất bại
        """
        if not self.use_cache:
            return False
            
        cache_path = self._get_cache_path(key)
        try:
            with open(cache_path, 'w', encoding='utf-8') as f:
                json.dump({
                    'translation': value,
                    'timestamp': datetime.now().isoformat()
                }, f, ensure_ascii=False)
            return True
        except Exception as e:
            logger.warning(f"Lỗi khi lưu cache: {str(e)}")
            return False
    
    def generate_key(self, text: str, **kwargs) -> str:
        """Tạo khóa cache từ văn bản, ngôn ngữ đích và dịch vụ
        
        Args:
            text: Văn bản cần dịch
            **kwargs: Các tham số khác (target_lang, service)
            
        Returns:
            Chuỗi đại diện cho khóa cache
        """
        # Tạo hash từ text để rút ngắn key
        text_hash = hashlib.md5(text.encode('utf-8')).hexdigest()
        target_lang = kwargs.get('target_lang', 'unknown')
        service = kwargs.get('service', 'unknown')
        return f"{text_hash}_{target_lang}_{service}"
    
    def clear(self, pattern: Optional[str] = None) -> bool:
        """Xóa cache (theo pattern nếu có)
        
        Args:
            pattern: Mẫu tên file để xóa có chọn lọc
            
        Returns:
            True nếu xóa thành công, False nếu có lỗi
        """
        try:
            if pattern:
                import glob
                files = glob.glob(os.path.join(self.cache_dir, f"*{pattern}*"))
                for file in files:
                    os.remove(file)
            else:
                import shutil
                shutil.rmtree(self.cache_dir)
                os.makedirs(self.cache_dir, exist_ok=True)
            return True
        except Exception as e:
            logger.error(f"Lỗi khi xóa cache: {str(e)}")
            return False
            
    def _get_cache_path(self, cache_key: str) -> str:
        """Tạo đường dẫn cache từ cache key
        
        Args:
            cache_key: Khóa cache
            
        Returns:
            Đường dẫn đầy đủ đến file cache
        """
        return os.path.join(self.cache_dir, f"{cache_key}.json")

    def clear_expired(self) -> None:
        """Xóa các cache đã hết hạn"""
        try:
            for filename in os.listdir(self.cache_dir):
                if not filename.endswith('.json'):
                    continue
                    
                file_path = os.path.join(self.cache_dir, filename)
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        cache_data = json.load(f)
                    timestamp_str = cache_data.get('timestamp')
                    if not timestamp_str:
                        os.remove(file_path)
                        continue
                    try:
                        cache_time = datetime.fromisoformat(timestamp_str)
                    except (ValueError, TypeError):
                        os.remove(file_path)
                        continue
                    if datetime.now() - cache_time > self.cache_expiry:
                        os.remove(file_path)

                except Exception:
                    # Nếu file bị lỗi, xóa luôn
                    os.remove(file_path)
                    
        except Exception as e:
            logger.error(f"Error clearing expired cache: {e}") 