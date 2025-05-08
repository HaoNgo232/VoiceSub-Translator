import pytest
import time
import os
import json
import threading
import psutil
from datetime import datetime, timedelta
from src.utils.cache_manager import CacheManager
from src.utils.thread_manager import ThreadManager
from src.utils.progress_manager import ProgressManager
from src.utils.memory_manager import MemoryManager
from src.utils.log_manager import LogManager

# Test CacheManager
class TestCacheManager:
    @pytest.fixture
    def cache(self):
        cache = CacheManager(cache_dir="test_cache")
        yield cache
        # Cleanup sau mỗi test
        if os.path.exists("test_cache"):
            for file in os.listdir("test_cache"):
                os.remove(os.path.join("test_cache", file))
            os.rmdir("test_cache")
            
    def test_cache_basic_operations(self, cache):
        # Test set và get
        cache.set("test1", "novita", "model1", "result1")
        assert cache.get("test1", "novita", "model1") == "result1"
        
        # Test cache không tồn tại
        assert cache.get("test2", "novita", "model1") is None
        
    def test_cache_expiry(self, cache):
        # Test cache hết hạn
        cache.set("test3", "novita", "model1", "result3")
        # Giả lập thời gian hết hạn
        cache.cache_expiry = timedelta(seconds=1)
        time.sleep(2)
        assert cache.get("test3", "novita", "model1") is None
        
    def test_cache_concurrent_access(self, cache):
        def write_cache():
            for i in range(10):
                cache.set(f"test{i}", "novita", "model1", f"result{i}")
                
        def read_cache():
            for i in range(10):
                cache.get(f"test{i}", "novita", "model1")
                
        # Test concurrent access
        threads = []
        for _ in range(5):
            threads.append(threading.Thread(target=write_cache))
            threads.append(threading.Thread(target=read_cache))
            
        for t in threads:
            t.start()
        for t in threads:
            t.join()
            
        # Verify results
        for i in range(10):
            assert cache.get(f"test{i}", "novita", "model1") == f"result{i}"

# Test ThreadManager
class TestThreadManager:
    @pytest.fixture
    def thread_mgr(self):
        thread_mgr = ThreadManager(max_workers=4)
        yield thread_mgr
        thread_mgr.shutdown()
        
    def test_thread_basic_operations(self, thread_mgr):
        def task1():
            time.sleep(0.1)
            return "task1"
            
        def task2():
            time.sleep(0.1)
            return "task2"
            
        results = thread_mgr.run_tasks(
            [task1, task2],
            task_names=["Task 1", "Task 2"],
            show_progress=False
        )
        assert results == ["task1", "task2"]
        
    def test_thread_error_handling(self, thread_mgr):
        def error_task():
            raise ValueError("Test error")
            
        results = thread_mgr.run_tasks(
            [error_task],
            task_names=["Error Task"],
            show_progress=False
        )
        assert results == [None]
        
    def test_thread_concurrent_tasks(self, thread_mgr):
        def long_task():
            time.sleep(0.5)
            return "long_task"
            
        def short_task():
            time.sleep(0.1)
            return "short_task"
            
        tasks = [long_task, short_task] * 5
        results = thread_mgr.run_tasks(tasks, show_progress=False)
        assert len(results) == 10
        assert results.count("long_task") == 5
        assert results.count("short_task") == 5

# Test ProgressManager
class TestProgressManager:
    @pytest.fixture
    def progress_mgr(self):
        return ProgressManager()
        
    def test_progress_basic_operations(self, progress_mgr):
        pbar = progress_mgr.create_progress(100, "Test Progress")
        assert pbar.total == 100
        
        progress_mgr.update_progress(10)
        assert pbar.n == 10
        
        progress_mgr.close_progress()
        assert progress_mgr._current_progress is None
        
    def test_progress_context_manager(self, progress_mgr):
        with progress_mgr.create_progress(100) as pbar:
            progress_mgr.update_progress(20)
            assert pbar.n == 20
            
    def test_progress_wrapper(self, progress_mgr):
        def test_func():
            return "test"
            
        wrapped_func = progress_mgr.wrap_with_progress(
            test_func,
            total=1,
            desc="Test Wrapper"
        )
        assert wrapped_func() == "test"

# Test MemoryManager
class TestMemoryManager:
    @pytest.fixture
    def memory_mgr(self):
        return MemoryManager(
            memory_threshold=0.9,
            check_interval=1
        )
        
    def test_memory_basic_operations(self, memory_mgr):
        usage = memory_mgr.get_memory_usage()
        assert 0 <= usage <= 1
        
        assert not memory_mgr.is_memory_critical()
        
    def test_memory_monitoring(self, memory_mgr):
        memory_mgr.start_monitoring()
        time.sleep(2)
        memory_mgr.stop_monitoring()
        
    def test_memory_wrapper(self, memory_mgr):
        def test_func():
            return "test"
            
        wrapped_func = memory_mgr.wrap_with_memory_management(test_func)
        assert wrapped_func() == "test"

# Test LogManager
class TestLogManager:
    @pytest.fixture
    def log_mgr(self):
        log_mgr = LogManager(log_dir="test_logs")
        yield log_mgr
        # Cleanup
        if os.path.exists("test_logs"):
            for file in os.listdir("test_logs"):
                os.remove(os.path.join("test_logs", file))
            os.rmdir("test_logs")
            
    def test_log_basic_operations(self, log_mgr):
        # Test error logging
        try:
            raise ValueError("Test error")
        except Exception as e:
            log_mgr.log_error(e, {"test": "context"})
            
        # Test API call logging
        log_mgr.log_api_call(
            provider="novita",
            model="test-model",
            success=True,
            duration=0.5
        )
        
        # Test error API call
        log_mgr.log_api_call(
            provider="novita",
            model="test-model",
            success=False,
            duration=0.5,
            error=ValueError("API error")
        )
        
    def test_log_rotation(self, log_mgr):
        # Test log rotation
        for i in range(15):  # Tạo nhiều file log
            log_mgr.log_error(ValueError(f"Test error {i}"))
            
        log_files = [f for f in os.listdir("test_logs") if f.startswith("app_")]
        assert len(log_files) <= log_mgr.max_log_files
        
    def test_log_concurrent_access(self, log_mgr):
        def write_logs():
            for i in range(10):
                log_mgr.log_error(ValueError(f"Test error {i}"))
                
        threads = []
        for _ in range(5):
            threads.append(threading.Thread(target=write_logs))
            
        for t in threads:
            t.start()
        for t in threads:
            t.join()
            
        # Verify log files exist
        assert os.path.exists("test_logs")
        log_files = [f for f in os.listdir("test_logs") if f.startswith("app_")]
        assert len(log_files) > 0 