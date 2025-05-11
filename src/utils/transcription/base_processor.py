from abc import ABC, abstractmethod
from typing import Optional, Dict, Any, List

class BaseTranscriptionProcessor(ABC):
    """
    Interface cơ sở cho các processor tạo phụ đề từ audio
    """
    
    @abstractmethod
    def load_model(self) -> None:
        """
        Load model transcription vào bộ nhớ
        """
        pass
        
    @abstractmethod
    def transcribe_audio(self, audio_path: str) -> Optional[Dict[str, Any]]:
        """
        Chuyển đổi audio thành văn bản
        
        Args:
            audio_path: Đường dẫn đến file audio
            
        Returns:
            Dict chứa kết quả chuyển đổi hoặc None nếu có lỗi
        """
        pass
        
    @abstractmethod
    def write_srt(self, result: Dict[str, Any], output_path: str) -> bool:
        """
        Ghi kết quả chuyển đổi ra file SRT
        
        Args:
            result: Kết quả từ transcribe_audio
            output_path: Đường dẫn file SRT đầu ra
            
        Returns:
            bool: True nếu thành công, False nếu thất bại
        """
        pass 