import os
import time
import logging
from typing import Dict, Optional, List
from .error_interface import ErrorHandler

logger = logging.getLogger(__name__)

class RateLimitHandler(ErrorHandler):
    """Lớp xử lý lỗi giới hạn tốc độ (rate limit)"""
    
    def __init__(self):
        """Khởi tạo RateLimitHandler"""
        # Theo dõi trạng thái rate limit của các provider
        self.rate_limited_providers = {}
        self.reset_times = {}
        
        # Cấu hình từ biến môi trường hoặc giá trị mặc định
        self.default_reset_time = int(os.getenv('RATE_LIMIT_RESET_TIME', '60'))  # 60 giây
        
        # Thiết lập giới hạn cho các provider
        self.provider_limits = {
            'novita': {'rpm': int(os.getenv('NOVITA_RPM', '1000')), 'current': 0, 'last_reset': time.time()},
            'google': {'rpm': int(os.getenv('GOOGLE_RPM', '1000')), 'current': 0, 'last_reset': time.time()},
            'mistral': {'rpm': int(os.getenv('MISTRAL_RPM', '1000')), 'current': 0, 'last_reset': time.time()},
            'groq': {'rpm': int(os.getenv('GROQ_RPM', '1000')), 'current': 0, 'last_reset': time.time()},
            'openrouter': {'rpm': int(os.getenv('OPENROUTER_RPM', '1000')), 'current': 0, 'last_reset': time.time()},
            'cerebras': {'rpm': int(os.getenv('CEREBRAS_RPM', '1000')), 'current': 0, 'last_reset': time.time()}
        }
        
        # Từ khóa để phát hiện lỗi rate limit
        self.rate_limit_keywords = [
            'rate limit',
            'ratelimit',
            'too many requests',
            'quota exceeded',
            'try again later',
            'limit exceeded',
            'too frequent',
            'throttled',
            'slow down'
        ]
    
    def check_rate_limit(self, provider: str) -> bool:
        """Kiểm tra xem provider có vượt quá giới hạn RPM không
        
        Args:
            provider: Tên provider
            
        Returns:
            True nếu provider còn trong giới hạn, False nếu đã vượt quá
        """
        # Nếu provider không được theo dõi, cho phép sử dụng
        if provider not in self.provider_limits:
            return True
            
        limit_info = self.provider_limits[provider]
        current_time = time.time()
        
        # Nếu đã qua 1 phút kể từ lần reset cuối, reset counter
        if current_time - limit_info['last_reset'] > 60:
            limit_info['current'] = 0
            limit_info['last_reset'] = current_time
            
        # Nếu đã đạt giới hạn, không cho phép sử dụng
        if limit_info['current'] >= limit_info['rpm']:
            return False
            
        # Tăng counter và cho phép sử dụng
        limit_info['current'] += 1
        return True
    
    def is_rate_limited(self, provider: str) -> bool:
        """Kiểm tra xem provider có đang bị giới hạn tốc độ không
        
        Args:
            provider: Tên provider
            
        Returns:
            True nếu provider đang bị giới hạn tốc độ, False nếu không
        """
        if provider not in self.rate_limited_providers:
            return False
            
        limit_time = self.rate_limited_providers[provider]
        current_time = time.time()
        reset_time = self.reset_times.get(provider, self.default_reset_time)
        
        # Nếu đã qua thời gian reset, xóa khỏi danh sách bị limit
        if current_time - limit_time > reset_time:
            del self.rate_limited_providers[provider]
            return False
            
        return True
        
    def mark_rate_limited(self, provider: str, reset_time: Optional[int] = None) -> None:
        """Đánh dấu provider đã bị giới hạn tốc độ
        
        Args:
            provider: Tên provider
            reset_time: Thời gian reset (giây), nếu None sẽ sử dụng giá trị mặc định
        """
        self.rate_limited_providers[provider] = time.time()
        if reset_time is not None:
            self.reset_times[provider] = reset_time
            
    def handle_error(self, error: Exception, provider: str, **kwargs) -> bool:
        """Xử lý lỗi từ provider, phát hiện và xử lý lỗi rate limit
        
        Args:
            error: Lỗi gặp phải
            provider: Tên provider
            
        Returns:
            True nếu lỗi là do rate limit, False nếu không
        """
        error_msg = str(error).lower()
        
        # Kiểm tra xem lỗi có phải do rate limit không
        if any(keyword in error_msg for keyword in self.rate_limit_keywords):
            # Lấy thời gian reset từ kwargs hoặc sử dụng mặc định
            reset_time = kwargs.get('reset_time', self.default_reset_time)
            
            # Đánh dấu provider đã bị rate limit
            self.mark_rate_limited(provider, reset_time)
            
            logger.warning(f"Provider {provider} đã bị rate limit, sẽ tạm ngưng trong {reset_time}s")
            return True
            
        return False
        
    def get_available_providers(self, all_providers: List[str]) -> List[str]:
        """Lọc danh sách các provider chưa bị giới hạn tốc độ
        
        Args:
            all_providers: Danh sách tất cả provider
            
        Returns:
            Danh sách các provider chưa bị giới hạn tốc độ
        """
        return [p for p in all_providers if not self.is_rate_limited(p)]
        
    def get_oldest_limited_provider(self) -> Optional[str]:
        """Lấy provider bị giới hạn tốc độ lâu nhất
        
        Returns:
            Tên provider hoặc None nếu không có provider nào bị giới hạn
        """
        if not self.rate_limited_providers:
            return None
            
        return min(self.rate_limited_providers.items(), key=lambda x: x[1])[0]
        
    def reset_provider(self, provider: str) -> None:
        """Đặt lại trạng thái giới hạn tốc độ cho provider
        
        Args:
            provider: Tên provider
        """
        if provider in self.rate_limited_providers:
            del self.rate_limited_providers[provider]
            logger.info(f"Đã reset trạng thái rate limit cho provider {provider}") 