import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List, Callable, Any, Dict
import logging
from tqdm import tqdm

logger = logging.getLogger(__name__)

class ThreadManager:
    def __init__(self, max_workers: int = 4):
        self.max_workers = max_workers
        self.executor = ThreadPoolExecutor(max_workers=max_workers)
        self._lock = threading.Lock()
        self._active_tasks: Dict[int, bool] = {}
        
    def _get_task_id(self) -> int:
        """Lấy ID cho task mới"""
        with self._lock:
            task_id = len(self._active_tasks)
            self._active_tasks[task_id] = True
            return task_id
            
    def _task_completed(self, task_id: int) -> None:
        """Đánh dấu task đã hoàn thành"""
        with self._lock:
            if task_id in self._active_tasks:
                del self._active_tasks[task_id]

    def active_task_count(self) -> int:
        """Trả về số lượng task đang chạy"""
        with self._lock:
            return len(self._active_tasks)
            
    def run_tasks(self, 
                 tasks: List[Callable], 
                 task_names: List[str] = None,
                 show_progress: bool = True) -> List[Any]:
        """Chạy nhiều task song song với progress bar"""
        if task_names is None:
            task_names = [f"Task {i+1}" for i in range(len(tasks))]
            
        results = []
        futures = []
        
        # Submit tasks
        for task, name in zip(tasks, task_names):
            task_id = self._get_task_id()
            future = self.executor.submit(self._wrap_task, task, task_id, name)
            futures.append(future)
            
        # Xử lý kết quả với progress bar
        if show_progress:
            with tqdm(total=len(tasks), desc="Processing tasks") as pbar:
                for future in as_completed(futures):
                    try:
                        result = future.result()
                        results.append(result)
                    except Exception as e:
                        logger.error(f"Task failed: {e}")
                        results.append(None)
                    finally:
                        pbar.update(1)
        else:
            for future in as_completed(futures):
                try:
                    result = future.result()
                    results.append(result)
                except Exception as e:
                    logger.error(f"Task failed: {e}")
                    results.append(None)
                    
        return results
        
    def _wrap_task(self, task: Callable, task_id: int, task_name: str) -> Any:
        """Wrapper cho task để xử lý lỗi và cleanup"""
        try:
            logger.info(f"Starting task: {task_name}")
            result = task()
            logger.info(f"Completed task: {task_name}")
            return result
        except Exception as e:
            logger.error(f"Error in task {task_name}: {e}")
            raise
        finally:
            self._task_completed(task_id)
            
    def shutdown(self) -> None:
        """Đóng thread pool"""
        self.executor.shutdown(wait=True)
