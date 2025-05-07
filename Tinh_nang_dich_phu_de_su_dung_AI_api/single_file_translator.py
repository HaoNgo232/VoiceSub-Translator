import os
import logging
from typing import List
from subtitle_processor import SubtitleProcessor
from api_handler import GroqAPIHandler

class SingleFileTranslator(SubtitleProcessor):
    def __init__(self, api_handler: GroqAPIHandler):
        super().__init__(api_handler)

    def translate_single_file(self, file_path: str) -> str:
        """Dịch một file phụ đề duy nhất."""
        logging.info(f"Bắt đầu dịch file: {file_path}")
        
        # Kiểm tra file tồn tại
        if not os.path.exists(file_path):
            error_msg = f"Lỗi: Không tìm thấy file {file_path}"
            logging.error(error_msg)
            return error_msg

        # Kiểm tra đuôi file
        if not file_path.lower().endswith('.srt'):
            error_msg = f"Lỗi: File {file_path} không phải là file .srt"
            logging.error(error_msg)
            return error_msg

        try:
            count = self.process_subtitle_file(file_path)
            if count > 0:
                return f"Đã dịch thành công {count} đoạn trong file."
            elif count == 0:
                return "File đã được dịch hoàn toàn hoặc không có gì để dịch."
            else:  # count == -1
                return "Có lỗi xảy ra trong quá trình dịch file."
        except Exception as e:
            error_msg = f"Lỗi không mong đợi khi xử lý file: {str(e)}"
            logging.error(error_msg)
            return error_msg
