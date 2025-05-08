import logging
import os
from datetime import datetime
from typing import Optional
import json
from pathlib import Path

class LogManager:
    def __init__(self, 
                 log_dir: str = "logs",
                 log_level: int = logging.INFO,
                 max_log_files: int = 10):
        self.log_dir = log_dir
        self.log_level = log_level
        self.max_log_files = max_log_files
        self._setup_logging()
        
    def _setup_logging(self) -> None:
        """Thiết lập logging"""
        # Tạo thư mục logs nếu chưa tồn tại
        os.makedirs(self.log_dir, exist_ok=True)
        
        # Tạo tên file log dựa trên thời gian
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        log_file = os.path.join(self.log_dir, f"app_{timestamp}.log")
        
        # Cấu hình logging
        logging.basicConfig(
            level=self.log_level,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file, encoding='utf-8'),
                logging.StreamHandler()
            ]
        )
        
        # Xóa các file log cũ nếu vượt quá giới hạn
        self._cleanup_old_logs()
        
    def _cleanup_old_logs(self) -> None:
        """Xóa các file log cũ"""
        log_files = sorted(
            [f for f in os.listdir(self.log_dir) if f.startswith("app_") and f.endswith(".log")],
            key=lambda x: os.path.getmtime(os.path.join(self.log_dir, x))
        )
        
        # Xóa các file cũ nếu vượt quá giới hạn
        while len(log_files) > self.max_log_files:
            old_file = log_files.pop(0)
            try:
                os.remove(os.path.join(self.log_dir, old_file))
            except Exception as e:
                print(f"Error deleting old log file {old_file}: {e}")
                
    def log_error(self, 
                  error: Exception,
                  context: Optional[dict] = None) -> None:
        """Log lỗi với context"""
        error_info = {
            'error_type': type(error).__name__,
            'error_message': str(error),
            'timestamp': datetime.now().isoformat(),
            'context': context or {}
        }
        
        # Log dưới dạng JSON để dễ parse
        logging.error(json.dumps(error_info, ensure_ascii=False))
        
    def log_api_call(self,
                    provider: str,
                    model: str,
                    success: bool,
                    duration: float,
                    error: Optional[Exception] = None) -> None:
        """Log thông tin API call"""
        api_info = {
            'provider': provider,
            'model': model,
            'success': success,
            'duration': duration,
            'timestamp': datetime.now().isoformat(),
            'error': str(error) if error else None
        }
        
        if success:
            logging.info(json.dumps(api_info, ensure_ascii=False))
        else:
            logging.error(json.dumps(api_info, ensure_ascii=False))
            
    def get_logger(self, name: str) -> logging.Logger:
        """Lấy logger với tên cụ thể"""
        return logging.getLogger(name) 