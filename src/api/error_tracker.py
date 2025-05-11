import time
import logging
from typing import List, Tuple, Optional

logger = logging.getLogger(__name__)

class ErrorTracker:
    """Lớp theo dõi lỗi liên tục từ các provider"""
    
    def __init__(self, failure_threshold: int = 5, cooldown_period: int = 300):
        """Khởi tạo ErrorTracker
        
        Args:
            failure_threshold: Số lần lỗi liên tiếp trước khi vô hiệu hóa provider
            cooldown_period: Thời gian chờ (giây) trước khi cho phép thử lại
        """
        # Đếm số lần lỗi liên tiếp
        self.failure_counts = {}
        
        # Thời điểm vô hiệu hóa
        self.disabled_providers = {}
        
        # Cấu hình
        self.failure_threshold = failure_threshold
        self.cooldown_period = cooldown_period
        
    def record_failure(self, provider: str) -> Tuple[bool, int]:
        """Ghi nhận lỗi từ provider
        
        Args:
            provider: Tên provider
            
        Returns:
            Tuple (đã bị vô hiệu hóa, số lỗi hiện tại)
        """
        # Tăng số lần lỗi
        self.failure_counts[provider] = self.failure_counts.get(provider, 0) + 1
        current_failures = self.failure_counts[provider]
        
        # Kiểm tra ngưỡng
        if current_failures >= self.failure_threshold:
            # Vô hiệu hóa provider
            self.disabled_providers[provider] = time.time() + self.cooldown_period
            logger.warning(f"Provider {provider} đã bị vô hiệu hóa sau {current_failures} lần lỗi liên tiếp, sẽ thử lại sau {self.cooldown_period}s")
            return True, current_failures
            
        return False, current_failures
        
    def record_success(self, provider: str) -> None:
        """Ghi nhận thành công từ provider
        
        Args:
            provider: Tên provider
        """
        # Reset số lần lỗi
        if provider in self.failure_counts:
            del self.failure_counts[provider]
            
    def is_disabled(self, provider: str) -> bool:
        """Kiểm tra xem provider có bị vô hiệu hóa không
        
        Args:
            provider: Tên provider
            
        Returns:
            True nếu provider đang bị vô hiệu hóa, False nếu không
        """
        if provider not in self.disabled_providers:
            return False
            
        disabled_until = self.disabled_providers[provider]
        current_time = time.time()
        
        # Nếu đã hết thời gian vô hiệu hóa
        if current_time > disabled_until:
            del self.disabled_providers[provider]
            return False
            
        return True
        
    def get_available_providers(self, all_providers: List[str]) -> List[str]:
        """Lọc danh sách các provider chưa bị vô hiệu hóa
        
        Args:
            all_providers: Danh sách tất cả provider
            
        Returns:
            Danh sách các provider chưa bị vô hiệu hóa
        """
        return [p for p in all_providers if not self.is_disabled(p)]
        
    def reset_provider(self, provider: str) -> None:
        """Đặt lại trạng thái cho provider
        
        Args:
            provider: Tên provider
        """
        if provider in self.failure_counts:
            del self.failure_counts[provider]
            
        if provider in self.disabled_providers:
            del self.disabled_providers[provider]
            
        logger.info(f"Đã reset trạng thái lỗi cho provider {provider}") 