import logging
from typing import List

from .rate_limit_handler import RateLimitHandler
from .error_tracker import ErrorTracker

logger = logging.getLogger(__name__)

class APIErrorHandler:
    """Lớp xử lý tất cả các loại lỗi từ API"""
    
    def __init__(self):
        """Khởi tạo APIErrorHandler"""
        self.rate_limit_handler = RateLimitHandler()
        self.error_tracker = ErrorTracker()
        
    def handle_error(self, error: Exception, provider: str, **kwargs) -> bool:
        """Xử lý lỗi từ provider
        
        Args:
            error: Lỗi gặp phải
            provider: Tên provider
            
        Returns:
            True nếu lỗi đã được xử lý, False nếu không
        """
        # Kiểm tra lỗi rate limit trước
        if self.rate_limit_handler.handle_error(error, provider, **kwargs):
            return True
            
        # Ghi nhận lỗi
        self.error_tracker.record_failure(provider)
        
        return False
        
    def record_success(self, provider: str) -> None:
        """Ghi nhận thành công từ provider
        
        Args:
            provider: Tên provider
        """
        self.error_tracker.record_success(provider)
        
    def get_available_providers(self, all_providers: List[str]) -> List[str]:
        """Lấy danh sách các provider có thể sử dụng
        
        Args:
            all_providers: Danh sách tất cả provider
            
        Returns:
            Danh sách các provider có thể sử dụng
        """
        # Lọc bỏ các provider bị vô hiệu hóa
        active_providers = self.error_tracker.get_available_providers(all_providers)
        
        # Lọc bỏ các provider bị rate limit
        return self.rate_limit_handler.get_available_providers(active_providers)
        
    def reset_provider(self, provider: str) -> None:
        """Đặt lại trạng thái cho provider
        
        Args:
            provider: Tên provider
        """
        self.rate_limit_handler.reset_provider(provider)
        self.error_tracker.reset_provider(provider) 