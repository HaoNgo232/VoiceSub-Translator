import os
import json
import hashlib
from typing import Optional, Any
import logging
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class CacheManager:
    def __init__(self, cache_dir: str = "cache"):
        self.cache_dir = cache_dir
        self.cache_expiry = timedelta(days=7)  # Cache hết hạn sau 7 ngày
        os.makedirs(cache_dir, exist_ok=True)
        
    def _get_cache_key(self, text: str, provider: str, model: str) -> str:
        """Tạo cache key từ text và provider"""
        key_string = f"{text}:{provider}:{model}"
        return hashlib.md5(key_string.encode()).hexdigest()
        
    def _get_cache_path(self, cache_key: str) -> str:
        """Lấy đường dẫn file cache"""
        return os.path.join(self.cache_dir, f"{cache_key}.json")
        
    def get(self, text: str, provider: str, model: str) -> Optional[str]:
        """Lấy kết quả từ cache nếu có"""
        cache_key = self._get_cache_key(text, provider, model)
        cache_path = self._get_cache_path(cache_key)
        
        if not os.path.exists(cache_path):
            return None
            
        try:
            with open(cache_path, 'r', encoding='utf-8') as f:
                cache_data = json.load(f)
                
            # Kiểm tra hết hạn
            cache_time = datetime.fromisoformat(cache_data['timestamp'])
            if datetime.now() - cache_time > self.cache_expiry:
                os.remove(cache_path)
                return None
                
            return cache_data['result']
            
        except Exception as e:
            logger.error(f"Error reading cache: {e}")
            return None
            
    def set(self, text: str, provider: str, model: str, result: str) -> None:
        """Lưu kết quả vào cache"""
        cache_key = self._get_cache_key(text, provider, model)
        cache_path = self._get_cache_path(cache_key)
        
        try:
            cache_data = {
                'timestamp': datetime.now().isoformat(),
                'result': result
            }
            
            with open(cache_path, 'w', encoding='utf-8') as f:
                json.dump(cache_data, f, ensure_ascii=False)
                
        except Exception as e:
            logger.error(f"Error writing to cache: {e}")
            
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
                        
                    cache_time = datetime.fromisoformat(cache_data['timestamp'])
                    if datetime.now() - cache_time > self.cache_expiry:
                        os.remove(file_path)
                        
                except Exception:
                    # Nếu file bị lỗi, xóa luôn
                    os.remove(file_path)
                    
        except Exception as e:
            logger.error(f"Error clearing expired cache: {e}") 