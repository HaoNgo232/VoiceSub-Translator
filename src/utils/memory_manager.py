import psutil
import gc
import logging
from typing import Optional, Callable, Dict, Any, List
import threading
import time
import os
import sys
from collections import deque
import weakref

logger = logging.getLogger(__name__)

class MemoryManager:
    def __init__(self, 
                 memory_threshold: float = 0.8,  # 80% memory usage
                 check_interval: int = 5,  # Check every 5 seconds
                 adaptive_monitoring: bool = True,
                 enable_profiling: bool = False):
        self.memory_threshold = memory_threshold
        self.check_interval = check_interval
        self.adaptive_monitoring = adaptive_monitoring
        self.enable_profiling = enable_profiling
        
        self._monitor_thread: Optional[threading.Thread] = None
        self._stop_monitoring = threading.Event()
        self._lock = threading.RLock()
        
        # Adaptive monitoring
        self._memory_history = deque(maxlen=100)
        self._cleanup_history = deque(maxlen=50)
        self._threshold_adjustments = []
        
        # Memory profiling
        self._memory_snapshots = []
        self._object_tracker = weakref.WeakSet()
        
        # Performance metrics
        self._cleanup_count = 0
        self._total_cleanup_time = 0
        self._last_cleanup_time = 0
        
    def get_memory_usage(self) -> float:
        """Lấy tỷ lệ sử dụng memory"""
        try:
            process = psutil.Process()
            memory_info = process.memory_info()
            memory_percent = process.memory_percent()
            
            # Lưu vào history cho adaptive monitoring
            if self.adaptive_monitoring:
                self._memory_history.append({
                    'timestamp': time.time(),
                    'percent': memory_percent / 100.0,
                    'rss': memory_info.rss,
                    'vms': memory_info.vms
                })
            
            return memory_percent / 100.0
        except Exception as e:
            logger.error(f"Error getting memory usage: {e}")
            return 0.0
        
    def get_memory_info(self) -> Dict[str, Any]:
        """Lấy thông tin chi tiết về memory"""
        try:
            process = psutil.Process()
            memory_info = process.memory_info()
            memory_percent = process.memory_percent()
            
            # System memory info
            system_memory = psutil.virtual_memory()
            
            return {
                'process': {
                    'rss': memory_info.rss,  # Resident Set Size
                    'vms': memory_info.vms,  # Virtual Memory Size
                    'percent': memory_percent,
                    'percent_normalized': memory_percent / 100.0
                },
                'system': {
                    'total': system_memory.total,
                    'available': system_memory.available,
                    'percent': system_memory.percent,
                    'percent_normalized': system_memory.percent / 100.0
                }
            }
        except Exception as e:
            logger.error(f"Error getting memory info: {e}")
            return {}
        
    def is_memory_critical(self) -> bool:
        """Kiểm tra xem memory có đang ở mức nguy hiểm không"""
        current_usage = self.get_memory_usage()
        
        # Adaptive threshold adjustment
        if self.adaptive_monitoring and len(self._memory_history) > 10:
            adjusted_threshold = self._calculate_adaptive_threshold()
            return current_usage > adjusted_threshold
        
        return current_usage > self.memory_threshold
        
    def _calculate_adaptive_threshold(self) -> float:
        """Tính toán threshold động dựa trên memory usage pattern"""
        if len(self._memory_history) < 10:
            return self.memory_threshold
            
        # Tính toán trend
        recent_usage = [entry['percent'] for entry in list(self._memory_history)[-10:]]
        if len(recent_usage) < 2:
            return self.memory_threshold
            
        # Nếu memory usage đang tăng nhanh, giảm threshold
        trend = (recent_usage[-1] - recent_usage[0]) / len(recent_usage)
        
        if trend > 0.01:  # Tăng >1% mỗi lần check
            adjusted_threshold = max(0.6, self.memory_threshold - 0.1)
        elif trend < -0.01:  # Giảm >1% mỗi lần check
            adjusted_threshold = min(0.9, self.memory_threshold + 0.05)
        else:
            adjusted_threshold = self.memory_threshold
            
        # Lưu adjustment để theo dõi
        self._threshold_adjustments.append({
            'timestamp': time.time(),
            'original': self.memory_threshold,
            'adjusted': adjusted_threshold,
            'trend': trend
        })
        
        return adjusted_threshold
        
    def cleanup_memory(self, aggressive: bool = False) -> Dict[str, Any]:
        """Dọn dẹp memory với các strategy khác nhau"""
        start_time = time.time()
        cleanup_stats = {
            'objects_collected': 0,
            'memory_freed': 0,
            'cleanup_time': 0,
            'strategy': 'normal'
        }
        
        try:
            # Lấy memory usage trước khi cleanup
            memory_before = self.get_memory_info()
            
            if aggressive:
                cleanup_stats['strategy'] = 'aggressive'
                # Aggressive cleanup
                self._aggressive_cleanup()
            else:
                # Normal cleanup
                self._normal_cleanup()
                
            # Lấy memory usage sau khi cleanup
            memory_after = self.get_memory_info()
            
            # Tính toán kết quả
            if memory_before and memory_after:
                process_before = memory_before['process']
                process_after = memory_after['process']
                
                cleanup_stats['memory_freed'] = process_before['rss'] - process_after['rss']
                cleanup_stats['objects_collected'] = gc.collect()[0]
                
            cleanup_stats['cleanup_time'] = time.time() - start_time
            
            # Cập nhật statistics
            self._cleanup_count += 1
            self._total_cleanup_time += cleanup_stats['cleanup_time']
            self._last_cleanup_time = time.time()
            
            # Lưu vào history
            self._cleanup_history.append({
                'timestamp': time.time(),
                'strategy': cleanup_stats['strategy'],
                'memory_freed': cleanup_stats['memory_freed'],
                'cleanup_time': cleanup_stats['cleanup_time']
            })
            
            logger.info(f"Memory cleanup completed: {cleanup_stats['memory_freed']} bytes freed in {cleanup_stats['cleanup_time']:.2f}s")
            
        except Exception as e:
            logger.error(f"Error during memory cleanup: {e}")
            cleanup_stats['error'] = str(e)
            
        return cleanup_stats
        
    def _normal_cleanup(self):
        """Normal memory cleanup"""
        # Garbage collection
        collected = gc.collect()
        
        # Clear Python cache
        if hasattr(sys, 'getrefcount'):
            # Clear some Python internal caches
            import builtins
            if hasattr(builtins, '__dict__'):
                # Clear some builtin caches
                pass
                
        # Clear memory history if too long
        if len(self._memory_history) > 200:
            self._memory_history.clear()
            
        if len(self._cleanup_history) > 100:
            self._cleanup_history.clear()
            
    def _aggressive_cleanup(self):
        """Aggressive memory cleanup"""
        # Multiple garbage collection cycles
        for _ in range(3):
            gc.collect()
            
        # Clear all history
        self._memory_history.clear()
        self._cleanup_history.clear()
        self._threshold_adjustments.clear()
        
        # Clear memory snapshots
        self._memory_snapshots.clear()
        
        # Force Python to release memory
        if hasattr(sys, 'intern'):
            # Clear string intern cache
            pass
            
    def start_monitoring(self) -> None:
        """Bắt đầu monitoring memory"""
        if self._monitor_thread is not None:
            return
            
        self._stop_monitoring.clear()
        self._monitor_thread = threading.Thread(target=self._monitor_memory)
        self._monitor_thread.daemon = True
        self._monitor_thread.start()
        logger.info("Memory monitoring started")
        
    def stop_monitoring(self) -> None:
        """Dừng monitoring memory"""
        if self._monitor_thread is None:
            return
            
        self._stop_monitoring.set()
        if self._monitor_thread.is_alive():
            self._monitor_thread.join(timeout=5)
        self._monitor_thread = None
        logger.info("Memory monitoring stopped")
        
    def _monitor_memory(self) -> None:
        """Thread monitoring memory với adaptive logic"""
        while not self._stop_monitoring.is_set():
            try:
                if self.is_memory_critical():
                    logger.warning("Memory usage is critical, cleaning up...")
                    
                    # Chọn strategy cleanup dựa trên memory usage
                    memory_usage = self.get_memory_usage()
                    if memory_usage > 0.9:  # >90%
                        self.cleanup_memory(aggressive=True)
                    else:
                        self.cleanup_memory(aggressive=False)
                        
                    # Adaptive interval adjustment
                    if self.adaptive_monitoring:
                        self._adjust_monitoring_interval()
                        
                # Memory profiling
                if self.enable_profiling:
                    self._take_memory_snapshot()
                    
                time.sleep(self.check_interval)
                
            except Exception as e:
                logger.error(f"Error in memory monitoring: {e}")
                time.sleep(self.check_interval)
                
    def _adjust_monitoring_interval(self):
        """Điều chỉnh interval monitoring dựa trên memory pattern"""
        if len(self._cleanup_history) < 5:
            return
            
        # Nếu cleanup xảy ra thường xuyên, giảm interval
        recent_cleanups = [entry for entry in list(self._cleanup_history)[-5:] 
                          if time.time() - entry['timestamp'] < 60]  # Trong 1 phút
        
        if len(recent_cleanups) >= 3:
            # Tăng frequency monitoring
            new_interval = max(1, self.check_interval // 2)
            if new_interval != self.check_interval:
                self.check_interval = new_interval
                logger.info(f"Adjusted monitoring interval to {new_interval}s")
        elif len(recent_cleanups) == 0:
            # Giảm frequency monitoring
            new_interval = min(30, self.check_interval * 2)
            if new_interval != self.check_interval:
                self.check_interval = new_interval
                logger.info(f"Adjusted monitoring interval to {new_interval}s")
                
    def _take_memory_snapshot(self):
        """Chụp snapshot memory cho profiling"""
        try:
            snapshot = {
                'timestamp': time.time(),
                'memory_info': self.get_memory_info(),
                'gc_stats': gc.get_stats() if hasattr(gc, 'get_stats') else {},
                'object_count': len(self._object_tracker)
            }
            
            self._memory_snapshots.append(snapshot)
            
            # Giới hạn số snapshot
            if len(self._memory_snapshots) > 1000:
                self._memory_snapshots = self._memory_snapshots[-500:]
                
        except Exception as e:
            logger.debug(f"Error taking memory snapshot: {e}")
            
    def track_object(self, obj: Any) -> None:
        """Theo dõi object để memory profiling"""
        if self.enable_profiling:
            self._object_tracker.add(obj)
            
    def get_memory_profile(self) -> Dict[str, Any]:
        """Lấy memory profile"""
        if not self.enable_profiling:
            return {'enabled': False}
            
        try:
            # Analyze snapshots
            if len(self._memory_snapshots) < 2:
                return {'enabled': True, 'data_points': len(self._memory_snapshots)}
                
            # Tính toán trends
            recent_snapshots = self._memory_snapshots[-10:]
            memory_trends = []
            
            for i in range(1, len(recent_snapshots)):
                prev = recent_snapshots[i-1]
                curr = recent_snapshots[i]
                
                if 'memory_info' in prev and 'memory_info' in curr:
                    prev_rss = prev['memory_info'].get('process', {}).get('rss', 0)
                    curr_rss = curr['memory_info'].get('process', {}).get('rss', 0)
                    
                    if prev_rss > 0:
                        growth_rate = (curr_rss - prev_rss) / prev_rss
                        memory_trends.append(growth_rate)
                        
            avg_growth_rate = sum(memory_trends) / len(memory_trends) if memory_trends else 0
            
            return {
                'enabled': True,
                'data_points': len(self._memory_snapshots),
                'avg_growth_rate': avg_growth_rate,
                'cleanup_stats': {
                    'total_cleanups': self._cleanup_count,
                    'avg_cleanup_time': self._total_cleanup_time / self._cleanup_count if self._cleanup_count > 0 else 0,
                    'last_cleanup': self._last_cleanup_time
                },
                'threshold_adjustments': len(self._threshold_adjustments)
            }
            
        except Exception as e:
            logger.error(f"Error generating memory profile: {e}")
            return {'enabled': True, 'error': str(e)}
        
    def wrap_with_memory_management(self, func: Callable) -> Callable:
        """Wrapper cho hàm với memory management"""
        def wrapper(*args, **kwargs):
            # Track function call
            if self.enable_profiling:
                self.track_object(func)
                
            # Check memory before
            if self.is_memory_critical():
                logger.warning("Memory usage is critical before function call, cleaning up...")
                self.cleanup_memory()
                
            # Execute function
            result = func(*args, **kwargs)
            
            # Check memory after
            if self.is_memory_critical():
                logger.warning("Memory usage is critical after function call, cleaning up...")
                self.cleanup_memory()
                
            return result
        return wrapper
        
    def get_stats(self) -> Dict[str, Any]:
        """Lấy thống kê về memory manager"""
        return {
            'memory_threshold': self.memory_threshold,
            'check_interval': self.check_interval,
            'adaptive_monitoring': self.adaptive_monitoring,
            'enable_profiling': self.enable_profiling,
            'monitoring_active': self._monitor_thread is not None,
            'memory_history_size': len(self._memory_history),
            'cleanup_history_size': len(self._cleanup_history),
            'cleanup_count': self._cleanup_count,
            'avg_cleanup_time': self._total_cleanup_time / self._cleanup_count if self._cleanup_count > 0 else 0,
            'last_cleanup': self._last_cleanup_time
        }
        
    def __enter__(self):
        self.start_monitoring()
        return self
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.stop_monitoring() 