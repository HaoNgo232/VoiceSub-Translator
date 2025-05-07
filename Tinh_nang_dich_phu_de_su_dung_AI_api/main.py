import os
import sys
import logging
import argparse
from pathlib import Path
from api_handler import GroqAPIHandler
from typing import Optional, List, Dict, Any

# Cấu hình logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('translation.log'),
        logging.StreamHandler(sys.stdout)
    ]
)

class SubtitleTranslator:
    def __init__(self):
        """Khởi tạo translator với API handler."""
        self.api_handler = GroqAPIHandler()
        
    def scan_directory(self, directory: str) -> List[str]:
        """Quét thư mục tìm các file .srt."""
        srt_files = []
        for root, _, files in os.walk(directory):
            for file in files:
                if file.endswith('.srt'):
                    srt_files.append(os.path.join(root, file))
        return srt_files
    
    def read_subtitle_file(self, file_path: str) -> Optional[str]:
        """Đọc nội dung file phụ đề."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
        except UnicodeDecodeError:
            try:
                with open(file_path, 'r', encoding='latin-1') as f:
                    return f.read()
            except Exception as e:
                logging.error(f"Không thể đọc file {file_path}: {str(e)}")
                return None
        except Exception as e:
            logging.error(f"Lỗi khi đọc file {file_path}: {str(e)}")
            return None
    
    def save_translation(self, file_path: str, translated_text: str) -> bool:
        """Lưu bản dịch vào file."""
        try:
            # Tạo tên file mới với hậu tố _vi
            base_name = os.path.splitext(file_path)[0]
            new_path = f"{base_name}_vi.srt"
            
            with open(new_path, 'w', encoding='utf-8') as f:
                f.write(translated_text)
            
            logging.info(f"Đã lưu bản dịch vào {new_path}")
            return True
        except Exception as e:
            logging.error(f"Lỗi khi lưu file {new_path}: {str(e)}")
            return False
    
    def process_file(self, file_path: str) -> bool:
        """Xử lý một file phụ đề."""
        logging.info(f"Đang xử lý file: {file_path}")
        
        # Đọc file
        content = self.read_subtitle_file(file_path)
        if not content:
            return False
        
        # Kiểm tra xem đã có bản dịch chưa
        base_name = os.path.splitext(file_path)[0]
        vi_path = f"{base_name}_vi.srt"
        if os.path.exists(vi_path):
            logging.info(f"File {vi_path} đã tồn tại, bỏ qua")
            return True
        
        # Dịch nội dung
        translated = self.api_handler.translate_text(content)
        if not translated:
            logging.error(f"Không thể dịch file {file_path}")
            return False
        
        # Lưu bản dịch
        return self.save_translation(file_path, translated)
    
    def process_directory(self, directory: str) -> Dict[str, Any]:
        """Xử lý tất cả file phụ đề trong thư mục."""
        results = {
            "total": 0,
            "success": 0,
            "failed": 0,
            "skipped": 0
        }
        
        # Quét thư mục
        srt_files = self.scan_directory(directory)
        results["total"] = len(srt_files)
        
        # Xử lý từng file
        for file_path in srt_files:
            if self.process_file(file_path):
                results["success"] += 1
            else:
                results["failed"] += 1
        
        return results

def main():
    """Hàm chính của chương trình."""
    parser = argparse.ArgumentParser(description='Dịch phụ đề sử dụng Groq API')
    parser.add_argument('--dir', type=str, help='Thư mục chứa file phụ đề')
    parser.add_argument('--file', type=str, help='Đường dẫn đến file phụ đề cần dịch')
    parser.add_argument('--test', action='store_true', help='Chạy tests')
    
    args = parser.parse_args()
    
    if args.test:
        # Chạy tests
        import pytest
        pytest.main(['test_api_handler.py', '-v'])
        return
    
    translator = SubtitleTranslator()
    
    if args.file:
        # Xử lý một file
        if translator.process_file(args.file):
            logging.info("Dịch file thành công")
        else:
            logging.error("Dịch file thất bại")
    
    elif args.dir:
        # Xử lý thư mục
        results = translator.process_directory(args.dir)
        logging.info(f"""
Kết quả xử lý:
- Tổng số file: {results['total']}
- Thành công: {results['success']}
- Thất bại: {results['failed']}
- Đã bỏ qua: {results['skipped']}
        """)
    
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
