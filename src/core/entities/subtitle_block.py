"""
Domain entities - Pure business objects
Following Domain-Driven Design principles
"""

from dataclasses import dataclass
from typing import Optional, Dict, Any
import re


@dataclass
class SubtitleBlock:
    """
    Core domain entity representing a subtitle block
    
    Principle: Single Responsibility Principle
    - Chỉ chứa data và business logic liên quan đến subtitle block
    """
    
    number: int
    start_time: str  # Format: "HH:MM:SS,mmm"
    end_time: str    # Format: "HH:MM:SS,mmm" 
    text: str
    translated_text: Optional[str] = None
    
    def __post_init__(self):
        """Validate subtitle block data"""
        if not self.is_valid_timestamp(self.start_time):
            raise ValueError(f"Invalid start_time format: {self.start_time}")
        if not self.is_valid_timestamp(self.end_time):
            raise ValueError(f"Invalid end_time format: {self.end_time}")
        if self.number <= 0:
            raise ValueError(f"Invalid block number: {self.number}")
    
    @staticmethod
    def is_valid_timestamp(timestamp: str) -> bool:
        """
        Kiểm tra format timestamp SRT
        
        Args:
            timestamp: Timestamp string
            
        Returns:
            True nếu format đúng (HH:MM:SS,mmm)
        """
        pattern = r'^\d{2}:\d{2}:\d{2},\d{3}$'
        return bool(re.match(pattern, timestamp))
    
    @property
    def timestamp(self) -> str:
        """Trả về timestamp range string"""
        return f"{self.start_time} --> {self.end_time}"
    
    @property
    def duration_seconds(self) -> float:
        """Tính thời lượng của subtitle block (giây)"""
        start_seconds = self._timestamp_to_seconds(self.start_time)
        end_seconds = self._timestamp_to_seconds(self.end_time)
        return end_seconds - start_seconds
    
    def _timestamp_to_seconds(self, timestamp: str) -> float:
        """Chuyển timestamp thành giây"""
        time_part, ms_part = timestamp.split(',')
        h, m, s = map(int, time_part.split(':'))
        ms = int(ms_part)
        return h * 3600 + m * 60 + s + ms / 1000
    
    def to_srt_format(self, use_translated: bool = False) -> str:
        """
        Chuyển đổi thành format SRT
        
        Args:
            use_translated: Sử dụng translated_text thay vì text gốc
            
        Returns:
            String format SRT
        """
        display_text = self.translated_text if (use_translated and self.translated_text) else self.text
        return f"{self.number}\n{self.timestamp}\n{display_text}\n"
    
    @classmethod
    def from_srt_block(cls, srt_text: str) -> 'SubtitleBlock':
        """
        Tạo SubtitleBlock từ SRT text block
        
        Args:
            srt_text: Text block từ file SRT
            
        Returns:
            SubtitleBlock instance
            
        Raises:
            ValueError: Nếu format SRT không đúng
        """
        lines = srt_text.strip().split('\n')
        
        if len(lines) < 3:
            raise ValueError(f"Invalid SRT block format: {srt_text}")
        
        try:
            number = int(lines[0])
            timestamp_line = lines[1]
            text = '\n'.join(lines[2:])
            
            # Parse timestamp
            if '-->' not in timestamp_line:
                raise ValueError(f"Invalid timestamp format: {timestamp_line}")
            
            start_time, end_time = timestamp_line.split(' --> ')
            start_time = start_time.strip()
            end_time = end_time.strip()
            
            return cls(
                number=number,
                start_time=start_time,
                end_time=end_time,
                text=text
            )
            
        except (ValueError, IndexError) as e:
            raise ValueError(f"Failed to parse SRT block: {srt_text}. Error: {str(e)}")
    
    def is_empty(self) -> bool:
        """Kiểm tra xem subtitle block có rỗng không"""
        return not self.text.strip()
    
    def get_word_count(self) -> int:
        """Đếm số từ trong text"""
        return len(self.text.split())
    
    def clone(self) -> 'SubtitleBlock':
        """Tạo bản copy của subtitle block"""
        return SubtitleBlock(
            number=self.number,
            start_time=self.start_time,
            end_time=self.end_time,
            text=self.text,
            translated_text=self.translated_text
        )
    
    @classmethod
    def parse_srt_content(cls, srt_content: str) -> list['SubtitleBlock']:
        """
        Parse toàn bộ file SRT thành list SubtitleBlock
        
        Args:
            srt_content: Nội dung file SRT
            
        Returns:
            List SubtitleBlock instances
        """
        blocks = []
        
        # Split bằng double newlines để tách các blocks
        srt_blocks = re.split(r'\n\s*\n', srt_content.strip())
        
        for block_text in srt_blocks:
            if block_text.strip():
                try:
                    block = cls.from_srt_block(block_text)
                    blocks.append(block)
                except ValueError as e:
                    # Log warning but continue parsing
                    import logging
                    logging.warning(f"Skipped invalid SRT block: {e}")
                    continue
        
        return blocks
    
    @classmethod
    def to_srt_content(cls, blocks: list['SubtitleBlock'], use_translated: bool = False) -> str:
        """
        Chuyển list SubtitleBlock thành SRT content
        
        Args:
            blocks: List SubtitleBlock
            use_translated: Sử dụng translated_text thay vì text gốc
            
        Returns:
            SRT content string
        """
        srt_parts = []
        
        for block in blocks:
            srt_parts.append(block.to_srt_format(use_translated=use_translated))
        
        return '\n'.join(srt_parts)
