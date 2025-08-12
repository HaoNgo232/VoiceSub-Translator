#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Performance monitoring và optimization utilities cho VoiceSub Translator
"""

import time
import logging
import threading
import psutil
import gc
from typing import Dict, Any, List, Optional, Callable
from functools import wraps
from collections import defaultdict, deque
import json
import os
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class PerformanceMonitor:
    """Monitor hiệu năng tổng thể của ứng dụng"""
    
    def __init__(self, enable_monitoring: bool = True, save_metrics: bool = True):
        self.enable_monitoring = enable_monitoring
        self.save_metrics = save_metrics
        
        # Performance metrics
        self._function_timings = defaultdict(list)
        self._memory_usage = deque(maxlen=1000)
        self._cpu_usage = deque(maxlen=1000)
        self._disk_io = deque(maxlen=1000)
        self._network_io = deque(maxlen=1000)
        
        # System metrics
        self._system_metrics = {}
        self._last_system_check = 0
        self._system_check_interval = 30  # 30 giây
        
        # Performance alerts
        self._performance_alerts = deque(maxlen=100)
        self._alert_thresholds = {
            'memory_usage': 0.85,  # 85%
            'cpu_usage': 0.90,     # 90%
            'function_time': 5.0,   # 5 giây
            'disk_io': 1000000,    # 1MB/s
        }
        
        # Monitoring thread
        self._monitor_thread = None
        self._stop_monitoring = threading.Event()
        self._lock = threading.RLock()
        
        if self.enable_monitoring:
            self.start_monitoring()
            
    def start_monitoring(self):
        """Bắt đầu monitoring performance"""
        if self._monitor_thread is not None:
            return
            
        self._stop_monitoring.clear()
        self._monitor_thread = threading.Thread(target=self._monitor_performance)
        self._monitor_thread.daemon = True
        self._monitor_thread.start()
        logger.info("Performance monitoring started")
        
    def stop_monitoring(self):
        """Dừng monitoring performance"""
        if self._monitor_thread is None:
            return
            
        self._stop_monitoring.set()
        if self._monitor_thread.is_alive():
            self._monitor_thread.join(timeout=5)
        self._monitor_thread = None
        logger.info("Performance monitoring stopped")
        
    def _monitor_performance(self):
        """Thread monitoring performance"""
        while not self._stop_monitoring.is_set():
            try:
                self._collect_system_metrics()
                self._check_performance_alerts()
                time.sleep(10)  # Check every 10 seconds
            except Exception as e:
                logger.error(f"Error in performance monitoring: {e}")
                time.sleep(10)
                
    def _collect_system_metrics(self):
        """Thu thập metrics hệ thống"""
        current_time = time.time()
        
        # CPU usage
        try:
            cpu_percent = psutil.cpu_percent(interval=1)
            self._cpu_usage.append({
                'timestamp': current_time,
                'usage': cpu_percent / 100.0
            })
        except Exception as e:
            logger.debug(f"Error collecting CPU metrics: {e}")
            
        # Memory usage
        try:
            memory = psutil.virtual_memory()
            self._memory_usage.append({
                'timestamp': current_time,
                'usage': memory.percent / 100.0,
                'available': memory.available,
                'total': memory.total
            })
        except Exception as e:
            logger.debug(f"Error collecting memory metrics: {e}")
            
        # Disk I/O
        try:
            disk_io = psutil.disk_io_counters()
            if disk_io:
                self._disk_io.append({
                    'timestamp': current_time,
                    'read_bytes': disk_io.read_bytes,
                    'write_bytes': disk_io.write_bytes,
                    'read_count': disk_io.read_count,
                    'write_count': disk_io.write_count
                })
        except Exception as e:
            logger.debug(f"Error collecting disk I/O metrics: {e}")
            
        # Network I/O
        try:
            net_io = psutil.net_io_counters()
            if net_io:
                self._network_io.append({
                    'timestamp': current_time,
                    'bytes_sent': net_io.bytes_sent,
                    'bytes_recv': net_io.bytes_recv,
                    'packets_sent': net_io.packets_sent,
                    'packets_recv': net_io.packets_recv
                })
        except Exception as e:
            logger.debug(f"Error collecting network I/O metrics: {e}")
            
        self._last_system_check = current_time
        
    def _check_performance_alerts(self):
        """Kiểm tra và tạo performance alerts"""
        current_time = time.time()
        
        # Check memory usage
        if self._memory_usage:
            latest_memory = self._memory_usage[-1]
            if latest_memory['usage'] > self._alert_thresholds['memory_usage']:
                self._add_alert('memory_high', f"Memory usage is high: {latest_memory['usage']:.1%}")
                
        # Check CPU usage
        if self._cpu_usage:
            latest_cpu = self._cpu_usage[-1]
            if latest_cpu['usage'] > self._alert_thresholds['cpu_usage']:
                self._add_alert('cpu_high', f"CPU usage is high: {latest_cpu['usage']:.1%}")
                
        # Check function timings
        for func_name, timings in self._function_timings.items():
            if timings:
                avg_time = sum(timings) / len(timings)
                if avg_time > self._alert_thresholds['function_time']:
                    self._add_alert('function_slow', f"Function {func_name} is slow: {avg_time:.2f}s average")
                    
    def _add_alert(self, alert_type: str, message: str):
        """Thêm performance alert"""
        alert = {
            'timestamp': time.time(),
            'type': alert_type,
            'message': message,
            'severity': 'warning'
        }
        
        self._performance_alerts.append(alert)
        logger.warning(f"Performance alert: {message}")
        
    def time_function(self, func_name: str = None):
        """Decorator để đo thời gian thực thi function"""
        def decorator(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                if not self.enable_monitoring:
                    return func(*args, **kwargs)
                    
                start_time = time.time()
                try:
                    result = func(*args, **kwargs)
                    execution_time = time.time() - start_time
                    
                    # Lưu timing
                    name = func_name or func.__name__
                    with self._lock:
                        self._function_timings[name].append(execution_time)
                        
                        # Giới hạn số timing records
                        if len(self._function_timings[name]) > 1000:
                            self._function_timings[name] = self._function_timings[name][-500:]
                            
                    return result
                except Exception as e:
                    execution_time = time.time() - start_time
                    logger.error(f"Function {func.__name__} failed after {execution_time:.2f}s: {e}")
                    raise
                    
            return wrapper
        return decorator
        
    def get_performance_report(self) -> Dict[str, Any]:
        """Lấy báo cáo hiệu năng tổng thể"""
        if not self.enable_monitoring:
            return {'monitoring_disabled': True}
            
        try:
            report = {
                'timestamp': time.time(),
                'system_metrics': self._get_system_summary(),
                'function_metrics': self._get_function_summary(),
                'alerts': list(self._performance_alerts)[-10:],  # Last 10 alerts
                'recommendations': self._generate_recommendations()
            }
            
            return report
            
        except Exception as e:
            logger.error(f"Error generating performance report: {e}")
            return {'error': str(e)}
            
    def _get_system_summary(self) -> Dict[str, Any]:
        """Lấy summary của system metrics"""
        summary = {}
        
        # Memory summary
        if self._memory_usage:
            memory_data = list(self._memory_usage)
            summary['memory'] = {
                'current_usage': memory_data[-1]['usage'],
                'avg_usage': sum(m['usage'] for m in memory_data) / len(memory_data),
                'max_usage': max(m['usage'] for m in memory_data),
                'min_usage': min(m['usage'] for m in memory_data)
            }
            
        # CPU summary
        if self._cpu_usage:
            cpu_data = list(self._cpu_usage)
            summary['cpu'] = {
                'current_usage': cpu_data[-1]['usage'],
                'avg_usage': sum(c['usage'] for c in cpu_data) / len(cpu_data),
                'max_usage': max(c['usage'] for c in cpu_data),
                'min_usage': min(c['usage'] for c in cpu_data)
            }
            
        # Disk I/O summary
        if self._disk_io:
            disk_data = list(self._disk_io)
            if len(disk_data) > 1:
                # Calculate I/O rate
                time_diff = disk_data[-1]['timestamp'] - disk_data[0]['timestamp']
                if time_diff > 0:
                    total_read = disk_data[-1]['read_bytes'] - disk_data[0]['read_bytes']
                    total_write = disk_data[-1]['write_bytes'] - disk_data[0]['write_bytes']
                    
                    summary['disk_io'] = {
                        'read_rate_mbps': (total_read / time_diff) / (1024 * 1024),
                        'write_rate_mbps': (total_write / time_diff) / (1024 * 1024)
                    }
                    
        return summary
        
    def _get_function_summary(self) -> Dict[str, Any]:
        """Lấy summary của function timings"""
        summary = {}
        
        for func_name, timings in self._function_timings.items():
            if timings:
                summary[func_name] = {
                    'call_count': len(timings),
                    'avg_time': sum(timings) / len(timings),
                    'max_time': max(timings),
                    'min_time': min(timings),
                    'total_time': sum(timings)
                }
                
        return summary
        
    def _generate_recommendations(self) -> List[str]:
        """Tạo recommendations dựa trên performance metrics"""
        recommendations = []
        
        # Memory recommendations
        if self._memory_usage:
            current_memory = self._memory_usage[-1]['usage']
            if current_memory > 0.8:
                recommendations.append("Memory usage is high. Consider reducing memory footprint or increasing available memory.")
            elif current_memory > 0.6:
                recommendations.append("Memory usage is moderate. Monitor for potential memory leaks.")
                
        # CPU recommendations
        if self._cpu_usage:
            current_cpu = self._cpu_usage[-1]['usage']
            if current_cpu > 0.8:
                recommendations.append("CPU usage is high. Consider optimizing CPU-intensive operations or using more cores.")
                
        # Function performance recommendations
        for func_name, timings in self._function_timings.items():
            if timings:
                avg_time = sum(timings) / len(timings)
                if avg_time > 2.0:
                    recommendations.append(f"Function '{func_name}' is slow ({avg_time:.2f}s average). Consider optimization.")
                    
        if not recommendations:
            recommendations.append("Performance is within acceptable ranges.")
            
        return recommendations
        
    def save_metrics_to_file(self, filename: str = None):
        """Lưu metrics vào file"""
        if not self.save_metrics:
            return
            
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"performance_metrics_{timestamp}.json"
            
        try:
            metrics = {
                'timestamp': datetime.now().isoformat(),
                'function_timings': dict(self._function_timings),
                'system_metrics': {
                    'memory_usage': list(self._memory_usage),
                    'cpu_usage': list(self._cpu_usage),
                    'disk_io': list(self._disk_io),
                    'network_io': list(self._network_io)
                },
                'alerts': list(self._performance_alerts)
            }
            
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(metrics, f, indent=2, ensure_ascii=False)
                
            logger.info(f"Performance metrics saved to {filename}")
            
        except Exception as e:
            logger.error(f"Error saving performance metrics: {e}")
            
    def clear_metrics(self):
        """Xóa tất cả metrics"""
        with self._lock:
            self._function_timings.clear()
            self._memory_usage.clear()
            self._cpu_usage.clear()
            self._disk_io.clear()
            self._network_io.clear()
            self._performance_alerts.clear()
            
        logger.info("All performance metrics cleared")
        
    def __enter__(self):
        return self
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.stop_monitoring()

class PerformanceOptimizer:
    """Class để tối ưu hóa hiệu năng ứng dụng"""
    
    def __init__(self, monitor: PerformanceMonitor = None):
        self.monitor = monitor or PerformanceMonitor()
        self._optimizations_applied = []
        
    def optimize_memory_usage(self) -> Dict[str, Any]:
        """Tối ưu hóa memory usage"""
        optimization_results = {
            'memory_freed': 0,
            'optimizations_applied': []
        }
        
        try:
            # Force garbage collection
            collected = gc.collect()
            optimization_results['optimizations_applied'].append(f"Garbage collection: {collected} objects collected")
            
            # Clear Python caches
            import builtins
            if hasattr(builtins, '__dict__'):
                # Clear some builtin caches
                pass
                
            # Clear monitor caches if they're too large
            if self.monitor and len(self.monitor._function_timings) > 500:
                for func_name in list(self.monitor._function_timings.keys()):
                    if len(self.monitor._function_timings[func_name]) > 200:
                        self.monitor._function_timings[func_name] = self.monitor._function_timings[func_name][-100:]
                optimization_results['optimizations_applied'].append("Reduced function timing cache size")
                
            # Memory cleanup
            if hasattr(psutil, 'Process'):
                process = psutil.Process()
                memory_before = process.memory_info().rss
                
                # Force memory release
                gc.collect()
                
                memory_after = process.memory_info().rss
                optimization_results['memory_freed'] = memory_before - memory_after
                
        except Exception as e:
            logger.error(f"Error during memory optimization: {e}")
            optimization_results['error'] = str(e)
            
        return optimization_results
        
    def optimize_cpu_usage(self) -> Dict[str, Any]:
        """Tối ưu hóa CPU usage"""
        optimization_results = {
            'optimizations_applied': []
        }
        
        try:
            # Check for CPU-intensive operations
            if self.monitor:
                slow_functions = []
                for func_name, timings in self.monitor._function_timings.items():
                    if timings:
                        avg_time = sum(timings) / len(timings)
                        if avg_time > 1.0:  # >1 second
                            slow_functions.append((func_name, avg_time))
                            
                if slow_functions:
                    # Sort by average time
                    slow_functions.sort(key=lambda x: x[1], reverse=True)
                    optimization_results['slow_functions'] = slow_functions
                    optimization_results['optimizations_applied'].append(f"Identified {len(slow_functions)} slow functions")
                    
        except Exception as e:
            logger.error(f"Error during CPU optimization: {e}")
            optimization_results['error'] = str(e)
            
        return optimization_results
        
    def generate_optimization_report(self) -> Dict[str, Any]:
        """Tạo báo cáo tối ưu hóa"""
        report = {
            'timestamp': datetime.now().isoformat(),
            'memory_optimization': self.optimize_memory_usage(),
            'cpu_optimization': self.optimize_cpu_usage(),
            'recommendations': []
        }
        
        # Generate recommendations
        if self.monitor:
            performance_report = self.monitor.get_performance_report()
            if 'recommendations' in performance_report:
                report['recommendations'].extend(performance_report['recommendations'])
                
        return report

# Global performance monitor instance
_performance_monitor = None

def get_performance_monitor() -> PerformanceMonitor:
    """Lấy global performance monitor instance"""
    global _performance_monitor
    if _performance_monitor is None:
        _performance_monitor = PerformanceMonitor()
    return _performance_monitor

def monitor_performance(func_name: str = None):
    """Decorator để monitor performance của function"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            monitor = get_performance_monitor()
            return monitor.time_function(func_name)(func)(*args, **kwargs)
        return wrapper
    return decorator

def optimize_performance():
    """Function để tối ưu hóa hiệu năng tổng thể"""
    monitor = get_performance_monitor()
    optimizer = PerformanceOptimizer(monitor)
    
    # Generate optimization report
    report = optimizer.generate_optimization_report()
    
    # Save metrics
    if monitor.save_metrics:
        monitor.save_metrics_to_file()
        
    return report