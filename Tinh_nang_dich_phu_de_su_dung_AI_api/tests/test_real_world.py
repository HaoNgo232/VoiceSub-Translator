import os
import time
import logging
import unittest
from typing import List
from datetime import datetime

from api.providers.groq import GroqAPIHandler
from api.providers.openrouter import OpenrouterAPIHandler # Sửa tên class
from api.config import APIConfig
from api.manager import APIManager
from api.exceptions import TranslationError

# Cấu hình logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

class TestRealWorld(unittest.TestCase):
    """Test với file subtitle thực tế."""
    
    @classmethod
    def setUpClass(cls):
        """Khởi tạo test environment."""
        cls.config = APIConfig()
        cls.manager = APIManager(cls.config)
        
        # Tạo thư mục test_data nếu chưa tồn tại
        cls.test_data_dir = "tests/test_data"
        os.makedirs(cls.test_data_dir, exist_ok=True)

    def setUp(self):
        """Chuẩn bị data cho mỗi test."""
        # Tạo file test nhỏ
        self.create_test_file("small.srt", 5)
        # Tạo file test vừa
        self.create_test_file("medium.srt", 20)
        # Tạo file test lớn
        self.create_test_file("large.srt", 50)

    def create_test_file(self, filename: str, num_blocks: int):
        """Tạo file test với số lượng block cho trước."""
        file_path = os.path.join(self.test_data_dir, filename)
        
        with open(file_path, 'w', encoding='utf-8') as f:
            for i in range(num_blocks):
                block = f"{i+1}\n"
                block += f"00:0{i//60}:{i%60},000 --> 00:0{i//60}:{i%60+1},000\n"
                block += f"""---BLOCK {i+1}---
This is test subtitle block number {i+1}.
It includes some technical terms like API, model, and configuration.
---END BLOCK {i+1}---\n\n"""
                f.write(block)

    def test_small_file(self):
        """Test với file nhỏ (~5 blocks)."""
        print("\nTesting small file translation...")
        file_path = os.path.join(self.test_data_dir, "small.srt")
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Dịch từng block
            blocks = content.split('\n\n')
            translated_blocks = []
            
            for block in blocks:
                if not block.strip():
                    continue
                    
                try:
                    result = self.manager.translate(block)
                    translated_blocks.append(result)
                    print(f"Translated block successfully")
                except Exception as e:
                    print(f"Error translating block: {str(e)}")
                    translated_blocks.append(block)  # Giữ nguyên block gốc
                
                time.sleep(0.1)  # Tránh hit rate limit
            
            # Lưu kết quả
            output_path = os.path.join(self.test_data_dir, "small_translated.srt")
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write('\n\n'.join(translated_blocks))
                
            print(f"Small file translated and saved to {output_path}")
            
        except Exception as e:
            self.fail(f"Small file test failed: {str(e)}")

    def test_medium_file(self):
        """Test với file vừa (~20 blocks)."""
        print("\nTesting medium file translation...")
        file_path = os.path.join(self.test_data_dir, "medium.srt")
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            blocks = content.split('\n\n')
            translated_blocks = []
            errors = []
            
            for i, block in enumerate(blocks):
                if not block.strip():
                    continue
                    
                try:
                    result = self.manager.translate(block)
                    translated_blocks.append(result)
                    print(f"Translated block {i+1}/{len(blocks)}")
                except Exception as e:
                    print(f"Error translating block {i+1}: {str(e)}")
                    errors.append(f"Block {i+1}: {str(e)}")
                    translated_blocks.append(block)
                
                time.sleep(0.1)
            
            # Lưu kết quả và log lỗi
            output_path = os.path.join(self.test_data_dir, "medium_translated.srt")
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write('\n\n'.join(translated_blocks))
            
            if errors:
                error_log = os.path.join(self.test_data_dir, "medium_errors.log")
                with open(error_log, 'w', encoding='utf-8') as f:
                    f.write('\n'.join(errors))
                print(f"Errors logged to {error_log}")
                
            print(f"Medium file translated with {len(errors)} errors")
            
        except Exception as e:
            self.fail(f"Medium file test failed: {str(e)}")

    def test_large_file(self):
        """Test với file lớn (~50 blocks)."""
        print("\nTesting large file translation...")
        file_path = os.path.join(self.test_data_dir, "large.srt")
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            blocks = content.split('\n\n')
            translated_blocks = []
            errors = []
            stats = {
                'total': len(blocks),
                'success': 0,
                'error': 0,
                'start_time': datetime.now()
            }
            
            for i, block in enumerate(blocks):
                if not block.strip():
                    continue
                    
                try:
                    result = self.manager.translate(block)
                    translated_blocks.append(result)
                    stats['success'] += 1
                    print(f"Translated block {i+1}/{stats['total']}")
                except Exception as e:
                    print(f"Error translating block {i+1}: {str(e)}")
                    errors.append(f"Block {i+1}: {str(e)}")
                    translated_blocks.append(block)
                    stats['error'] += 1
                
                time.sleep(0.1)
            
            # Tính thống kê
            stats['end_time'] = datetime.now()
            stats['duration'] = (stats['end_time'] - stats['start_time']).total_seconds()
            
            # Lưu kết quả và thống kê
            output_path = os.path.join(self.test_data_dir, "large_translated.srt")
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write('\n\n'.join(translated_blocks))
            
            if errors:
                error_log = os.path.join(self.test_data_dir, "large_errors.log")
                with open(error_log, 'w', encoding='utf-8') as f:
                    f.write('\n'.join(errors))
                
            stats_log = os.path.join(self.test_data_dir, "large_stats.log")
            with open(stats_log, 'w', encoding='utf-8') as f:
                f.write(f"Translation Statistics:\n")
                f.write(f"Total blocks: {stats['total']}\n")
                f.write(f"Successful: {stats['success']}\n")
                f.write(f"Failed: {stats['error']}\n")
                f.write(f"Duration: {stats['duration']:.2f} seconds\n")
                f.write(f"Average time per block: {stats['duration']/stats['total']:.2f} seconds\n")
                
            print(f"Large file translated with {stats['error']} errors")
            print(f"Statistics saved to {stats_log}")
            
        except Exception as e:
            self.fail(f"Large file test failed: {str(e)}")

    def test_concurrent_files(self):
        """Test xử lý nhiều file cùng lúc."""
        print("\nTesting concurrent file translation...")
        files = ["small.srt", "medium.srt"]
        results = []
        
        for filename in files:
            file_path = os.path.join(self.test_data_dir, filename)
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                blocks = content.split('\n\n')
                translated_blocks = []
                
                for block in blocks:
                    if not block.strip():
                        continue
                        
                    try:
                        result = self.manager.translate(block)
                        translated_blocks.append(result)
                    except Exception as e:
                        print(f"Error in {filename}, block: {str(e)}")
                        translated_blocks.append(block)
                    
                    time.sleep(0.1)
                
                # Lưu kết quả
                output_path = os.path.join(self.test_data_dir, f"{filename}_concurrent.srt")
                with open(output_path, 'w', encoding='utf-8') as f:
                    f.write('\n\n'.join(translated_blocks))
                
                results.append(f"Translated {filename}")
                
            except Exception as e:
                results.append(f"Failed {filename}: {str(e)}")
        
        print("\nConcurrent translation results:")
        for result in results:
            print(result)

    def tearDown(self):
        """Dọn dẹp sau mỗi test."""
        # Có thể xóa các file test nếu cần
        pass

    @classmethod
    def tearDownClass(cls):
        """Dọn dẹp sau khi test xong."""
        # Giữ lại các file để kiểm tra kết quả
        pass

if __name__ == '__main__':
    unittest.main(verbosity=2)
