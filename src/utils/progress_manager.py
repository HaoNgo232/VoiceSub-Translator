from typing import Optional, Callable
from tqdm import tqdm
import logging

logger = logging.getLogger(__name__)

class ProgressManager:
    def __init__(self):
        self._current_progress: Optional[tqdm] = None
        
    def create_progress(self, 
                       total: int, 
                       desc: str = "Processing",
                       unit: str = "items") -> tqdm:
        """Tạo progress bar mới"""
        if self._current_progress is not None:
            self._current_progress.close()
            
        self._current_progress = tqdm(
            total=total,
            desc=desc,
            unit=unit,
            ncols=100,
            bar_format='{l_bar}{bar}| {n_fmt}/{total_fmt} [{elapsed}<{remaining}]'
        )
        return self._current_progress
        
    def update_progress(self, n: int = 1) -> None:
        """Cập nhật progress bar"""
        if self._current_progress is not None:
            self._current_progress.update(n)
            
    def close_progress(self) -> None:
        """Đóng progress bar hiện tại"""
        if self._current_progress is not None:
            self._current_progress.close()
            self._current_progress = None
            
    def __enter__(self):
        return self
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close_progress()
        
    def wrap_with_progress(self, 
                          func: Callable,
                          total: int,
                          desc: str = "Processing",
                          unit: str = "items") -> Callable:
        """Wrapper cho hàm với progress bar"""
        def wrapper(*args, **kwargs):
            with self.create_progress(total, desc, unit) as pbar:
                def update_progress(*args, **kwargs):
                    pbar.update(1)
                    return func(*args, **kwargs)
                return update_progress(*args, **kwargs)
        return wrapper 