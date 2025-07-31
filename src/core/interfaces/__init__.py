"""
Core domain interfaces - Độc lập với implementation details
Following Dependency Inversion Principle (SOLID)
"""

from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any
from ..entities.subtitle_block import SubtitleBlock
from ..entities.translation_context import TranslationContext


class TranslationStrategy(ABC):
    """
    Interface cho các chiến lược dịch thuật khác nhau
    
    Principle: Strategy Pattern + Open/Closed Principle
    - Open for extension (thêm strategy mới)
    - Closed for modification (không thay đổi interface)
    """
    
    @abstractmethod
    def translate_blocks(
        self, 
        blocks: List[SubtitleBlock], 
        context: TranslationContext,
        provider_service: 'ProviderService'
    ) -> List[Optional[SubtitleBlock]]:
        """
        Dịch danh sách subtitle blocks với strategy cụ thể
        
        Args:
            blocks: Danh sách subtitle blocks cần dịch
            context: Context chứa thông tin dịch thuật (target_lang, service, etc.)
            provider_service: Service để gọi API providers
            
        Returns:
            List các subtitle blocks đã dịch (None nếu dịch thất bại)
        """
        pass
    
    @abstractmethod
    def get_strategy_name(self) -> str:
        """Trả về tên của strategy"""
        pass


class ProviderService(ABC):
    """
    Interface cho việc quản lý và gọi các translation providers
    
    Principle: Interface Segregation Principle
    - Chỉ expose những methods cần thiết cho translation strategies
    """
    
    @abstractmethod
    def translate_text(
        self, 
        text: str, 
        target_lang: str, 
        provider_name: Optional[str] = None
    ) -> Optional[str]:
        """
        Dịch một đoạn văn bản
        
        Args:
            text: Văn bản cần dịch
            target_lang: Ngôn ngữ đích
            provider_name: Provider cụ thể (None = auto select)
            
        Returns:
            Văn bản đã dịch hoặc None nếu thất bại
        """
        pass
    
    @abstractmethod
    def get_available_providers(self) -> List[str]:
        """Lấy danh sách providers khả dụng"""
        pass


class CacheService(ABC):
    """
    Interface cho cache management
    
    Principle: Single Responsibility Principle
    - Chỉ chịu trách nhiệm cache operations
    """
    
    @abstractmethod
    def get(self, key: str) -> Optional[str]:
        """Lấy giá trị từ cache"""
        pass
    
    @abstractmethod
    def set(self, key: str, value: str, ttl: Optional[int] = None) -> None:
        """Lưu giá trị vào cache"""
        pass
    
    @abstractmethod
    def generate_key(self, **kwargs) -> str:
        """Tạo cache key từ parameters"""
        pass


class TranscriptionService(ABC):
    """
    Interface cho transcription services (Whisper, etc.)
    
    Principle: Dependency Inversion Principle
    - High-level modules don't depend on low-level modules
    """
    
    @abstractmethod
    def transcribe_audio(self, audio_path: str) -> Optional[Dict[str, Any]]:
        """
        Chuyển đổi audio thành text với timestamps
        
        Args:
            audio_path: Đường dẫn file audio
            
        Returns:
            Dict chứa segments với timestamps hoặc None nếu thất bại
        """
        pass
    
    @abstractmethod
    def write_srt(self, transcription_result: Dict[str, Any], output_path: str) -> bool:
        """
        Ghi transcription result ra file SRT
        
        Args:
            transcription_result: Kết quả từ transcribe_audio
            output_path: Đường dẫn file SRT output
            
        Returns:
            True nếu thành công, False nếu thất bại
        """
        pass
