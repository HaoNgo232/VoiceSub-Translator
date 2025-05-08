import psutil
import gc
import logging
from typing import Optional, Callable
import threading
import time

logger = logging.getLogger(__name__)

class MemoryManager:
    def __init__(self, 
                 memory_threshold: float = 0.8,  # 80% memory usage
                 check_interval: int = 5):  # Check every 5 seconds
        self.memory_threshold = memory_threshold
        self.check_interval = check_interval
        self._monitor_thread: Optional[threading.Thread] = None
        self._stop_monitoring = threading.Event()
        
    def get_memory_usage(self) -> float:
        """Lấy tỷ lệ sử dụng memory"""
        return psutil.Process().memory_percent() / 100.0
        
    def is_memory_critical(self) -> bool:
        """Kiểm tra xem memory có đang ở mức nguy hiểm không"""
        return self.get_memory_usage() > self.memory_threshold
        
    def cleanup_memory(self) -> None:
        """Dọn dẹp memory"""
        gc.collect()
        
    def start_monitoring(self) -> None:
        """Bắt đầu monitoring memory"""
        if self._monitor_thread is not None:
            return
            
        self._stop_monitoring.clear()
        self._monitor_thread = threading.Thread(target=self._monitor_memory)
        self._monitor_thread.daemon = True
        self._monitor_thread.start()
        
    def stop_monitoring(self) -> None:
        """Dừng monitoring memory"""
        if self._monitor_thread is None:
            return
            
        self._stop_monitoring.set()
        self._monitor_thread.join()
        self._monitor_thread = None
        
    def _monitor_memory(self) -> None:
        """Thread monitoring memory"""
        while not self._stop_monitoring.is_set():
            if self.is_memory_critical():
                logger.warning("Memory usage is critical, cleaning up...")
                self.cleanup_memory()
            time.sleep(self.check_interval)
            
    def wrap_with_memory_management(self, func: Callable) -> Callable:
        """Wrapper cho hàm với memory management"""
        def wrapper(*args, **kwargs):
            if self.is_memory_critical():
                logger.warning("Memory usage is critical before function call, cleaning up...")
                self.cleanup_memory()
                
            result = func(*args, **kwargs)
            
            if self.is_memory_critical():
                logger.warning("Memory usage is critical after function call, cleaning up...")
                self.cleanup_memory()
                
            return result
        return wrapper
        
    def __enter__(self):
        self.start_monitoring()
        return self
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.stop_monitoring() 