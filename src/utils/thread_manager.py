import threading
import asyncio
from concurrent.futures import ThreadPoolExecutor, as_completed, ProcessPoolExecutor
from typing import List, Callable, Any, Dict, Union, Optional
import logging
from tqdm import tqdm
import time
import queue
from contextlib import contextmanager

logger = logging.getLogger(__name__)

class ThreadManager:
    def __init__(self, max_workers: int = None, use_process_pool: bool = False):
        # Tự động xác định số worker tối ưu
        if max_workers is None:
            import multiprocessing
            max_workers = min(multiprocessing.cpu_count() * 2, 8)
        
        self.max_workers = max_workers
        self.use_process_pool = use_process_pool
        
        # Sử dụng ProcessPoolExecutor cho CPU-intensive tasks
        if use_process_pool:
            self.executor = ProcessPoolExecutor(max_workers=max_workers)
        else:
            self.executor = ThreadPoolExecutor(max_workers=max_workers)
            
        self._lock = threading.Lock()
        self._active_tasks: Dict[int, bool] = {}
        self._task_queue = queue.Queue()
        self._results_cache = {}
        self._cache_ttl = 300  # 5 phút cache
        
        # Background thread để xử lý queue
        self._queue_worker = threading.Thread(target=self._process_queue, daemon=True)
        self._queue_worker.start()
        
    def _get_task_id(self) -> int:
        """Lấy ID cho task mới"""
        with self._lock:
            task_id = len(self._active_tasks)
            self._active_tasks[task_id] = True
            return task_id
            
    def _task_completed(self, task_id: int) -> None:
        """Đánh dấu task đã hoàn thành"""
        with self._lock:
            self._active_tasks[task_id] = False
            
    def _process_queue(self):
        """Background thread để xử lý task queue"""
        while True:
            try:
                task_data = self._task_queue.get(timeout=1)
                if task_data is None:  # Shutdown signal
                    break
                    
                task_id, task, task_name = task_data
                try:
                    result = task()
                    self._results_cache[task_id] = {
                        'result': result,
                        'timestamp': time.time()
                    }
                except Exception as e:
                    logger.error(f"Error in queued task {task_name}: {e}")
                    self._results_cache[task_id] = {
                        'error': str(e),
                        'timestamp': time.time()
                    }
                finally:
                    self._task_completed(task_id)
                    self._task_queue.task_done()
                    
            except queue.Empty:
                continue
            except Exception as e:
                logger.error(f"Error in queue worker: {e}")
                
    def run_tasks(self, 
                 tasks: List[Callable], 
                 task_names: List[str] = None,
                 show_progress: bool = True,
                 max_concurrent: int = None) -> List[Any]:
        """Chạy nhiều task song song với progress bar và giới hạn concurrent"""
        if task_names is None:
            task_names = [f"Task {i+1}" for i in range(len(tasks))]
            
        if max_concurrent is None:
            max_concurrent = self.max_workers
            
        results = []
        futures = []
        semaphore = threading.Semaphore(max_concurrent)
        
        def limited_task(task):
            with semaphore:
                return task()
        
        # Submit tasks với semaphore
        for task, name in zip(tasks, task_names):
            task_id = self._get_task_id()
            future = self.executor.submit(self._wrap_task, limited_task, task_id, name)
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
        
    async def run_tasks_async(self, 
                            tasks: List[Callable], 
                            task_names: List[str] = None,
                            max_concurrent: int = None) -> List[Any]:
        """Chạy tasks bất đồng bộ với asyncio"""
        if max_concurrent is None:
            max_concurrent = self.max_workers
            
        semaphore = asyncio.Semaphore(max_concurrent)
        
        async def limited_task(task):
            async with semaphore:
                loop = asyncio.get_event_loop()
                return await loop.run_in_executor(self.executor, task)
        
        # Chạy tất cả tasks
        if task_names is None:
            task_names = [f"Task {i+1}" for i in range(len(tasks))]
            
        async def run_single_task(task, name):
            try:
                logger.info(f"Starting async task: {name}")
                result = await limited_task(task)
                logger.info(f"Completed async task: {name}")
                return result
            except Exception as e:
                logger.error(f"Error in async task {name}: {e}")
                return None
        
        # Chạy tasks song song
        task_coroutines = [run_single_task(task, name) for task, name in zip(tasks, task_names)]
        results = await asyncio.gather(*task_coroutines, return_exceptions=True)
        
        # Xử lý exceptions
        processed_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                logger.error(f"Task {task_names[i]} failed with exception: {result}")
                processed_results.append(None)
            else:
                processed_results.append(result)
                
        return processed_results
        
    def run_tasks_with_priority(self, 
                              tasks: List[Callable], 
                              priorities: List[int],
                              task_names: List[str] = None) -> List[Any]:
        """Chạy tasks với priority queue"""
        if task_names is None:
            task_names = [f"Task {i+1}" for i in range(len(tasks))]
            
        # Tạo priority queue
        import heapq
        priority_queue = []
        for i, (task, priority, name) in enumerate(zip(tasks, priorities, task_names)):
            heapq.heappush(priority_queue, (priority, i, task, name))
            
        results = [None] * len(tasks)
        futures = []
        
        # Submit tasks theo priority
        while priority_queue:
            _, task_idx, task, name = heapq.heappop(priority_queue)
            task_id = self._get_task_id()
            future = self.executor.submit(self._wrap_task, task, task_id, name)
            futures.append((future, task_idx))
            
        # Xử lý kết quả
        for future, task_idx in futures:
            try:
                result = future.result()
                results[task_idx] = result
            except Exception as e:
                logger.error(f"Priority task failed: {e}")
                results[task_idx] = None
                
        return results
        
    def _wrap_task(self, task: Callable, task_id: int, task_name: str) -> Any:
        """Wrapper cho task để xử lý lỗi và cleanup"""
        try:
            logger.info(f"Starting task: {task_name}")
            start_time = time.time()
            result = task()
            execution_time = time.time() - start_time
            logger.info(f"Completed task: {task_name} in {execution_time:.2f}s")
            return result
        except Exception as e:
            logger.error(f"Error in task {task_name}: {e}")
            raise
        finally:
            self._task_completed(task_id)
            
    @contextmanager
    def get_executor(self):
        """Context manager để sử dụng executor"""
        try:
            yield self.executor
        finally:
            pass
            
    def submit_task(self, task: Callable, task_name: str = None) -> Any:
        """Submit một task đơn lẻ"""
        if task_name is None:
            task_name = f"Task_{id(task)}"
            
        task_id = self._get_task_id()
        future = self.executor.submit(self._wrap_task, task, task_id, task_name)
        return future
        
    def get_task_result(self, task_id: int, timeout: float = None) -> Optional[Any]:
        """Lấy kết quả của task từ cache"""
        if task_id in self._results_cache:
            cache_entry = self._results_cache[task_id]
            if time.time() - cache_entry['timestamp'] < self._cache_ttl:
                return cache_entry.get('result')
            else:
                # Cache expired
                del self._results_cache[task_id]
        return None
        
    def clear_cache(self) -> None:
        """Xóa cache"""
        self._results_cache.clear()
        
    def get_stats(self) -> Dict[str, Any]:
        """Lấy thống kê về thread manager"""
        with self._lock:
            active_tasks = sum(1 for active in self._active_tasks.values() if active)
            
        return {
            'max_workers': self.max_workers,
            'active_tasks': active_tasks,
            'cache_size': len(self._results_cache),
            'use_process_pool': self.use_process_pool
        }
            
    def shutdown(self) -> None:
        """Đóng thread pool và cleanup"""
        # Gửi shutdown signal đến queue worker
        self._task_queue.put(None)
        
        # Đợi queue worker kết thúc
        if self._queue_worker.is_alive():
            self._queue_worker.join(timeout=5)
            
        # Đóng executor
        self.executor.shutdown(wait=True)
        
        # Clear cache
        self.clear_cache()
        
        logger.info("ThreadManager shutdown completed") 