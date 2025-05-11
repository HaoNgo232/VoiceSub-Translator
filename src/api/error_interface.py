from abc import ABC, abstractmethod

class ErrorHandler(ABC):
    """Giao diện cơ sở cho các lớp xử lý lỗi"""
    
    @abstractmethod
    def handle_error(self, error: Exception, provider: str, **kwargs) -> bool:
        """Xử lý lỗi từ provider
        
        Args:
            error: Lỗi gặp phải
            provider: Tên provider
            
        Returns:
            True nếu lỗi đã được xử lý, False nếu không
        """
        pass 