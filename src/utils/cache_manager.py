from abc import ABC, abstractmethod
import os
import json
import logging
import hashlib
import pickle
import gzip
import time
from typing import Optional, Dict, Any, Union
from datetime import datetime, timedelta
import threading
from functools import wraps

logger = logging.getLogger(__name__)

class CacheManager(ABC):
    """Giao diện quản lý cache cho các dịch vụ của ứng dụng"""
    
    @abstractmethod
    def get(self, key: str) -> Optional[Any]:
        """Lấy giá trị từ cache theo key"""
        pass
        
    @abstractmethod
    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """Lưu giá trị vào cache với TTL tùy chọn"""
        pass
        
    @abstractmethod
    def generate_key(self, data: Any, **kwargs) -> str:
        """Tạo khóa cache từ dữ liệu"""
        pass
        
    @abstractmethod
    def clear(self, pattern: Optional[str] = None) -> bool:
        """Xóa cache (theo pattern nếu có)"""
        pass
        
    @abstractmethod
    def exists(self, key: str) -> bool:
        """Kiểm tra xem key có tồn tại trong cache không"""
        pass
        
    @abstractmethod
    def get_stats(self) -> Dict[str, Any]:
        """Lấy thống kê về cache"""
        pass

class MemoryCacheManager(CacheManager):
    """In-memory cache manager với LRU và TTL support"""
    
    def __init__(self, max_size: int = 1000, default_ttl: int = 3600):
        self.max_size = max_size
        self.default_ttl = default_ttl
        self._cache = {}
        self._access_times = {}
        self._lock = threading.RLock()
        self._hits = 0
        self._misses = 0
        
    def get(self, key: str) -> Optional[Any]:
        """Lấy giá trị từ cache với LRU logic"""
        with self._lock:
            if key in self._cache:
                entry = self._cache[key]
                if time.time() < entry['expiry']:
                    self._access_times[key] = time.time()
                    self._hits += 1
                    return entry['value']
                else:
                    # Expired, remove
                    del self._cache[key]
                    del self._access_times[key]
                    
            self._misses += 1
            return None
            
    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """Lưu giá trị vào cache với TTL"""
        if ttl is None:
            ttl = self.default_ttl
            
        with self._lock:
            # Check if we need to evict
            if len(self._cache) >= self.max_size:
                self._evict_lru()
                
            self._cache[key] = {
                'value': value,
                'expiry': time.time() + ttl,
                'created': time.time()
            }
            self._access_times[key] = time.time()
            return True
            
    def _evict_lru(self):
        """Xóa item ít được sử dụng nhất"""
        if not self._access_times:
            return
            
        oldest_key = min(self._access_times.keys(), key=lambda k: self._access_times[k])
        del self._cache[oldest_key]
        del self._access_times[oldest_key]
        
    def generate_key(self, data: Any, **kwargs) -> str:
        """Tạo khóa cache từ dữ liệu"""
        if isinstance(data, str):
            content = data
        else:
            content = str(data)
            
        # Thêm kwargs vào content
        if kwargs:
            content += str(sorted(kwargs.items()))
            
        return hashlib.md5(content.encode('utf-8')).hexdigest()
        
    def clear(self, pattern: Optional[str] = None) -> bool:
        """Xóa cache theo pattern hoặc toàn bộ"""
        with self._lock:
            if pattern is None:
                self._cache.clear()
                self._access_times.clear()
            else:
                keys_to_remove = [k for k in self._cache.keys() if pattern in k]
                for k in keys_to_remove:
                    del self._cache[k]
                    del self._access_times[k]
            return True
            
    def exists(self, key: str) -> bool:
        """Kiểm tra xem key có tồn tại và chưa hết hạn không"""
        with self._lock:
            if key in self._cache:
                return time.time() < self._cache[key]['expiry']
            return False
            
    def get_stats(self) -> Dict[str, Any]:
        """Lấy thống kê về cache"""
        with self._lock:
            total_requests = self._hits + self._misses
            hit_rate = self._hits / total_requests if total_requests > 0 else 0
            
            # Clean expired entries
            current_time = time.time()
            expired_keys = [k for k, v in self._cache.items() if current_time >= v['expiry']]
            for k in expired_keys:
                del self._cache[k]
                del self._access_times[k]
                
            return {
                'size': len(self._cache),
                'max_size': self.max_size,
                'hits': self._hits,
                'misses': self._misses,
                'hit_rate': hit_rate,
                'total_requests': total_requests
            }

class RedisCacheManager(CacheManager):
    """Redis cache manager với compression và connection pooling"""
    
    def __init__(self, redis_url: str = "redis://localhost:6379", 
                 default_ttl: int = 3600, use_compression: bool = True):
        self.redis_url = redis_url
        self.default_ttl = default_ttl
        self.use_compression = use_compression
        self._redis_client = None
        self._connection_pool = None
        self._lock = threading.Lock()
        
        try:
            import redis
            self._redis_client = redis.from_url(redis_url)
            # Test connection
            self._redis_client.ping()
            logger.info(f"Connected to Redis at {redis_url}")
        except ImportError:
            logger.warning("Redis package not installed, falling back to memory cache")
            self._redis_client = None
        except Exception as e:
            logger.error(f"Failed to connect to Redis: {e}")
            self._redis_client = None
            
    def _get_redis(self):
        """Lấy Redis client với connection pooling"""
        if self._redis_client is None:
            return None
            
        try:
            # Test connection
            self._redis_client.ping()
            return self._redis_client
        except Exception as e:
            logger.warning(f"Redis connection failed: {e}")
            return None
            
    def _compress_data(self, data: bytes) -> bytes:
        """Nén dữ liệu với gzip"""
        if not self.use_compression:
            return data
        return gzip.compress(data)
        
    def _decompress_data(self, data: bytes) -> bytes:
        """Giải nén dữ liệu"""
        if not self.use_compression:
            return data
        try:
            return gzip.decompress(data)
        except Exception:
            return data
            
    def get(self, key: str) -> Optional[Any]:
        """Lấy giá trị từ Redis cache"""
        redis_client = self._get_redis()
        if redis_client is None:
            return None
            
        try:
            data = redis_client.get(key)
            if data is None:
                return None
                
            # Decompress if needed
            decompressed_data = self._decompress_data(data)
            
            # Try to deserialize
            try:
                return pickle.loads(decompressed_data)
            except Exception:
                # Fallback to JSON
                return json.loads(decompressed_data.decode('utf-8'))
                
        except Exception as e:
            logger.error(f"Error getting from Redis cache: {e}")
            return None
            
    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """Lưu giá trị vào Redis cache"""
        redis_client = self._get_redis()
        if redis_client is None:
            return False
            
        try:
            if ttl is None:
                ttl = self.default_ttl
                
            # Serialize data
            try:
                serialized_data = pickle.dumps(value)
            except Exception:
                serialized_data = json.dumps(value, ensure_ascii=False).encode('utf-8')
                
            # Compress if enabled
            compressed_data = self._compress_data(serialized_data)
            
            # Store in Redis
            return redis_client.setex(key, ttl, compressed_data)
            
        except Exception as e:
            logger.error(f"Error setting Redis cache: {e}")
            return False
            
    def generate_key(self, data: Any, **kwargs) -> str:
        """Tạo khóa cache từ dữ liệu"""
        if isinstance(data, str):
            content = data
        else:
            content = str(data)
            
        # Thêm kwargs vào content
        if kwargs:
            content += str(sorted(kwargs.items()))
            
        return hashlib.md5(content.encode('utf-8')).hexdigest()
        
    def clear(self, pattern: Optional[str] = None) -> bool:
        """Xóa cache theo pattern hoặc toàn bộ"""
        redis_client = self._get_redis()
        if redis_client is None:
            return False
            
        try:
            if pattern is None:
                redis_client.flushdb()
            else:
                keys = redis_client.keys(pattern)
                if keys:
                    redis_client.delete(*keys)
            return True
        except Exception as e:
            logger.error(f"Error clearing Redis cache: {e}")
            return False
            
    def exists(self, key: str) -> bool:
        """Kiểm tra xem key có tồn tại trong cache không"""
        redis_client = self._get_redis()
        if redis_client is None:
            return False
            
        try:
            return redis_client.exists(key) > 0
        except Exception as e:
            logger.error(f"Error checking Redis cache: {e}")
            return False
            
    def get_stats(self) -> Dict[str, Any]:
        """Lấy thống kê về Redis cache"""
        redis_client = self._get_redis()
        if redis_client is None:
            return {'status': 'disconnected'}
            
        try:
            info = redis_client.info()
            return {
                'status': 'connected',
                'redis_version': info.get('redis_version'),
                'used_memory_human': info.get('used_memory_human'),
                'connected_clients': info.get('connected_clients'),
                'total_commands_processed': info.get('total_commands_processed'),
                'keyspace_hits': info.get('keyspace_hits'),
                'keyspace_misses': info.get('keyspace_misses')
            }
        except Exception as e:
            logger.error(f"Error getting Redis stats: {e}")
            return {'status': 'error', 'error': str(e)}

class TranslationCacheManager(CacheManager):
    """Triển khai cụ thể của CacheManager cho việc lưu cache bản dịch"""
    
    def __init__(self, cache_dir: Optional[str] = None, use_cache: bool = True,
                 cache_type: str = 'memory', redis_url: str = None):
        """Khởi tạo TranslationCacheManager
        
        Args:
            cache_dir: Thư mục lưu cache (cho file-based cache)
            use_cache: Bật/tắt sử dụng cache
            cache_type: Loại cache ('memory', 'file', 'redis')
            redis_url: URL Redis nếu sử dụng Redis cache
        """
        self.use_cache = use_cache
        self.cache_type = cache_type
        
        if cache_type == 'redis' and redis_url:
            self._cache_manager = RedisCacheManager(redis_url)
        elif cache_type == 'memory':
            self._cache_manager = MemoryCacheManager()
        else:
            # File-based cache
            self.cache_dir = cache_dir or os.path.join(os.path.expanduser("~"), ".subtitle_translator_cache")
            self.cache_expiry = timedelta(days=7)  # Cache hết hạn sau 7 ngày
            os.makedirs(self.cache_dir, exist_ok=True)
            self._cache_manager = None
            logger.info(f"Sử dụng file cache tại: {self.cache_dir}")
        
    def get(self, key: str) -> Optional[str]:
        """Lấy bản dịch từ cache"""
        if not self.use_cache:
            return None
            
        if self._cache_manager:
            return self._cache_manager.get(key)
            
        # File-based cache
        cache_path = self._get_cache_path(key)
        if os.path.exists(cache_path):
            try:
                with open(cache_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    # Check expiry
                    if 'expiry' in data and datetime.now().isoformat() > data['expiry']:
                        os.remove(cache_path)
                        return None
                    return data.get('translation')
            except Exception as e:
                logger.warning(f"Lỗi khi đọc cache: {str(e)}")
        return None
        
    def set(self, key: str, value: str, ttl: Optional[int] = None) -> bool:
        """Lưu bản dịch vào cache"""
        if not self.use_cache:
            return False
            
        if self._cache_manager:
            return self._cache_manager.set(key, value, ttl)
            
        # File-based cache
        cache_path = self._get_cache_path(key)
        try:
            expiry = (datetime.now() + timedelta(seconds=ttl or 604800)).isoformat()
            with open(cache_path, 'w', encoding='utf-8') as f:
                json.dump({
                    'translation': value,
                    'expiry': expiry,
                    'created': datetime.now().isoformat()
                }, f, ensure_ascii=False)
            return True
        except Exception as e:
            logger.warning(f"Lỗi khi lưu cache: {str(e)}")
            return False
    
    def generate_key(self, text: str, **kwargs) -> str:
        """Tạo khóa cache từ văn bản, ngôn ngữ đích và dịch vụ"""
        # Tạo content string từ text và kwargs
        content = text.lower().strip()
        
        # Thêm các tham số khác
        if 'target_lang' in kwargs:
            content += f":{kwargs['target_lang']}"
        if 'service' in kwargs:
            content += f":{kwargs['service']}"
        if 'source_lang' in kwargs:
            content += f":{kwargs['source_lang']}"
            
        # Tạo hash
        return hashlib.md5(content.encode('utf-8')).hexdigest()
        
    def clear(self, pattern: Optional[str] = None) -> bool:
        """Xóa cache theo pattern hoặc toàn bộ"""
        if self._cache_manager:
            return self._cache_manager.clear(pattern)
            
        # File-based cache
        try:
            if pattern is None:
                # Xóa toàn bộ cache
                for file in os.listdir(self.cache_dir):
                    if file.endswith('.cache'):
                        os.remove(os.path.join(self.cache_dir, file))
            else:
                # Xóa theo pattern
                for file in os.listdir(self.cache_dir):
                    if pattern in file and file.endswith('.cache'):
                        os.remove(os.path.join(self.cache_dir, file))
            return True
        except Exception as e:
            logger.error(f"Lỗi khi xóa cache: {str(e)}")
            return False
            
    def exists(self, key: str) -> bool:
        """Kiểm tra xem key có tồn tại trong cache không"""
        if self._cache_manager:
            return self._cache_manager.exists(key)
            
        # File-based cache
        cache_path = self._get_cache_path(key)
        if os.path.exists(cache_path):
            try:
                with open(cache_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    return 'expiry' not in data or datetime.now().isoformat() <= data['expiry']
            except Exception:
                return False
        return False
        
    def get_stats(self) -> Dict[str, Any]:
        """Lấy thống kê về cache"""
        if self._cache_manager:
            return self._cache_manager.get_stats()
            
        # File-based cache stats
        try:
            cache_files = [f for f in os.listdir(self.cache_dir) if f.endswith('.cache')]
            total_size = sum(os.path.getsize(os.path.join(self.cache_dir, f)) for f in cache_files)
            
            return {
                'type': 'file',
                'cache_dir': self.cache_dir,
                'file_count': len(cache_files),
                'total_size_bytes': total_size,
                'total_size_mb': total_size / (1024 * 1024)
            }
        except Exception as e:
            return {'type': 'file', 'error': str(e)}
        
    def _get_cache_path(self, key: str) -> str:
        """Lấy đường dẫn file cache"""
        return os.path.join(self.cache_dir, f"{key}.cache")

def cache_result(ttl: int = 3600, cache_type: str = 'memory'):
    """Decorator để cache kết quả của function"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Tạo cache key từ function name và arguments
            cache_key = f"{func.__name__}:{hash(str(args) + str(sorted(kwargs.items()))}"
            
            # Tạo cache manager
            cache_manager = TranslationCacheManager(cache_type=cache_type)
            
            # Kiểm tra cache
            cached_result = cache_manager.get(cache_key)
            if cached_result is not None:
                return cached_result
                
            # Thực thi function
            result = func(*args, **kwargs)
            
            # Lưu vào cache
            cache_manager.set(cache_key, result, ttl)
            
            return result
        return wrapper
    return decorator 