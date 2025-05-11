"""
Các thành phần xử lý phụ đề
"""

import logging
from typing import List, Dict, Tuple, Optional
import os

logger = logging.getLogger(__name__)

class SubtitleProcessor:
    """Lớp xử lý phụ đề"""
    
    def __init__(self):
        """Khởi tạo SubtitleProcessor"""
        pass
    
    def read_subtitle_file(self, file_path: str) -> str:
        """Đọc file phụ đề từ đường dẫn
        
        Args:
            file_path: Đường dẫn đến file phụ đề
            
        Returns:
            Nội dung file phụ đề
            
        Raises:
            FileNotFoundError: Nếu file không tồn tại
            UnicodeDecodeError: Nếu file không đúng định dạng
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
        except UnicodeDecodeError:
            # Thử mã hóa khác nếu utf-8 không hoạt động
            encodings = ['latin-1', 'cp1252', 'iso-8859-1']
            for encoding in encodings:
                try:
                    with open(file_path, 'r', encoding=encoding) as f:
                        content = f.read()
                    logger.info(f"Đọc file phụ đề với mã hóa {encoding}")
                    return content
                except UnicodeDecodeError:
                    continue
            # Nếu tất cả các mã hóa đều thất bại
            raise UnicodeDecodeError("Không thể đọc file phụ đề với các mã hóa đã thử")
            
    def write_subtitle_file(self, file_path: str, content: str) -> bool:
        """Ghi nội dung phụ đề vào file
        
        Args:
            file_path: Đường dẫn đến file phụ đề
            content: Nội dung cần ghi
            
        Returns:
            True nếu ghi thành công, False nếu thất bại
        """
        try:
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            return True
        except Exception as e:
            logger.error(f"Lỗi khi ghi file phụ đề: {str(e)}")
            return False
            
    def split_into_blocks(self, content: str) -> List[str]:
        """Tách nội dung phụ đề thành các block
        
        Args:
            content: Nội dung phụ đề
            
        Returns:
            Danh sách các block phụ đề
        """
        blocks = []
        current_block = []
        
        for line in content.split('\n'):
            line = line.rstrip()
            
            if not line and current_block:
                # Kết thúc block hiện tại
                blocks.append('\n'.join(current_block))
                current_block = []
            elif line or current_block:
                # Thêm dòng vào block hiện tại
                # (chỉ bắt đầu thêm khi đã có nội dung hoặc dòng hiện tại không rỗng)
                current_block.append(line)
                
        # Thêm block cuối cùng nếu có
        if current_block:
            blocks.append('\n'.join(current_block))
            
        return blocks
        
    def parse_subtitle_block(self, block: str) -> Tuple[str, str, str]:
        """Phân tách block phụ đề thành các thành phần
        
        Args:
            block: Block phụ đề
            
        Returns:
            Tuple (số thứ tự, timestamp, văn bản)
            
        Raises:
            ValueError: Nếu block không đúng định dạng
        """
        lines = block.split('\n')
        
        if len(lines) < 3:
            raise ValueError(f"Block phụ đề không đúng định dạng (ít hơn 3 dòng)")
            
        number = lines[0].strip()
        timestamp = lines[1].strip()
        text = '\n'.join(lines[2:])
        
        return number, timestamp, text
        
    def create_subtitle_block(self, number: str, timestamp: str, text: str) -> str:
        """Tạo block phụ đề từ các thành phần
        
        Args:
            number: Số thứ tự
            timestamp: Timestamp
            text: Văn bản phụ đề
            
        Returns:
            Block phụ đề hoàn chỉnh
        """
        return f"{number}\n{timestamp}\n{text}"
        
    def process_subtitle_blocks(self, blocks: List[str], processor_func) -> Tuple[List[Optional[str]], Dict]:
        """Xử lý các block phụ đề
        
        Args:
            blocks: Danh sách các block phụ đề
            processor_func: Hàm xử lý mỗi block, nhận block và trả về block đã xử lý
            
        Returns:
            Tuple (danh sách block đã xử lý, thống kê)
        """
        processed_blocks = [None] * len(blocks)
        stats = {
            'total_blocks': len(blocks),
            'successful': 0,
            'failed': 0
        }
        
        for i, block in enumerate(blocks):
            try:
                processed_block = processor_func(i, block)
                processed_blocks[i] = processed_block
                if processed_block is not None:
                    stats['successful'] += 1
                else:
                    stats['failed'] += 1
            except Exception as e:
                logger.error(f"Lỗi khi xử lý block {i+1}: {str(e)}")
                stats['failed'] += 1
                
        return processed_blocks, stats
        
    def validate_subtitle_format(self, content: str) -> bool:
        """Kiểm tra nội dung phụ đề có đúng định dạng không
        
        Args:
            content: Nội dung phụ đề
            
        Returns:
            True nếu đúng định dạng, False nếu không
        """
        blocks = self.split_into_blocks(content)
        
        if not blocks:
            logger.error("Không tìm thấy block phụ đề nào")
            return False
            
        for i, block in enumerate(blocks):
            try:
                number, timestamp, text = self.parse_subtitle_block(block)
                
                # Kiểm tra timestamp
                if '-->' not in timestamp:
                    logger.error(f"Block {i+1}: Timestamp không đúng định dạng")
                    return False
                    
                # Kiểm tra thứ tự
                try:
                    block_num = int(number)
                    if block_num != i+1:
                        logger.warning(f"Block {i+1}: Số thứ tự không liên tục (tìm thấy {block_num})")
                except ValueError:
                    logger.error(f"Block {i+1}: Số thứ tự không phải số nguyên")
                    return False
                    
            except ValueError as e:
                logger.error(f"Block {i+1}: {str(e)}")
                return False
                
        return True
        
    def merge_subtitle_blocks(self, blocks: List[str]) -> str:
        """Ghép các block phụ đề thành một chuỗi hoàn chỉnh
        
        Args:
            blocks: Danh sách các block phụ đề
            
        Returns:
            Chuỗi phụ đề hoàn chỉnh
        """
        # Lọc các block None
        valid_blocks = [b for b in blocks if b is not None]
        
        # Ghép với dòng trống ở giữa
        return '\n\n'.join(valid_blocks)
        
    def renumber_subtitle_blocks(self, blocks: List[str]) -> List[str]:
        """Đánh số lại các block phụ đề
        
        Args:
            blocks: Danh sách các block phụ đề
            
        Returns:
            Danh sách đã được đánh số lại
        """
        renumbered_blocks = []
        
        for i, block in enumerate(blocks):
            if block is None:
                continue
                
            try:
                number, timestamp, text = self.parse_subtitle_block(block)
                renumbered_block = self.create_subtitle_block(str(i+1), timestamp, text)
                renumbered_blocks.append(renumbered_block)
            except ValueError:
                # Nếu không thể phân tích block, giữ nguyên
                renumbered_blocks.append(block)
                
        return renumbered_blocks 