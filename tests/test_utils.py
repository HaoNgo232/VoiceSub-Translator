import pytest
import time
import os
import json
from src.utils.cache_manager import CacheManager
from src.utils.thread_manager import ThreadManager
from src.utils.progress_manager import ProgressManager
from src.utils.memory_manager import MemoryManager
from src.utils.log_manager import LogManager

def test_cache_manager():
    cache = CacheManager(cache_dir="test_cache")
    
    # Test set và get
    cache.set("test", "novita", "model1", "result1")
    assert cache.get("test", "novita", "model1") == "result1"
    
    # Test cache không tồn tại
    assert cache.get("test2", "novita", "model1") is None
    
    # Test clear expired
    cache.clear_expired()
    
    # Cleanup
    if os.path.exists("test_cache"):
        for file in os.listdir("test_cache"):
            os.remove(os.path.join("test_cache", file))
        os.rmdir("test_cache")

def test_thread_manager():
    thread_mgr = ThreadManager(max_workers=2)
    
    def task1():
        time.sleep(0.1)
        return "task1"
        
    def task2():
        time.sleep(0.1)
        return "task2"
        
    # Test run tasks
    results = thread_mgr.run_tasks(
        [task1, task2],
        task_names=["Task 1", "Task 2"],
        show_progress=False
    )
    assert results == ["task1", "task2"]
    
    # Test error handling
    def error_task():
        raise Exception("Test error")
        
    results = thread_mgr.run_tasks(
        [error_task],
        task_names=["Error Task"],
        show_progress=False
    )
    assert results == [None]
    
    thread_mgr.shutdown()

def test_progress_manager():
    progress_mgr = ProgressManager()
    
    # Test create progress
    pbar = progress_mgr.create_progress(100, "Test Progress")
    assert pbar.total == 100
    
    # Test update
    progress_mgr.update_progress(10)
    assert pbar.n == 10
    
    # Test close
    progress_mgr.close_progress()
    assert progress_mgr._current_progress is None
    
    # Test context manager
    with progress_mgr.create_progress(100) as pbar:
        progress_mgr.update_progress(20)
        assert pbar.n == 20

def test_memory_manager():
    memory_mgr = MemoryManager(
        memory_threshold=0.9,  # Set high to avoid false positives
        check_interval=1
    )
    
    # Test memory usage
    usage = memory_mgr.get_memory_usage()
    assert 0 <= usage <= 1
    
    # Test memory critical
    assert not memory_mgr.is_memory_critical()
    
    # Test cleanup
    memory_mgr.cleanup_memory()
    
    # Test monitoring
    memory_mgr.start_monitoring()
    time.sleep(2)
    memory_mgr.stop_monitoring()

def test_log_manager():
    log_mgr = LogManager(log_dir="test_logs")
    
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
    
    # Test get logger
    logger = log_mgr.get_logger("test")
    assert isinstance(logger, logging.Logger)
    
    # Cleanup
    if os.path.exists("test_logs"):
        for file in os.listdir("test_logs"):
            os.remove(os.path.join("test_logs", file))
        os.rmdir("test_logs") 