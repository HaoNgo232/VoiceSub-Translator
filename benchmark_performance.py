#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Script benchmark để kiểm tra hiệu năng của VoiceSub Translator
Sau khi áp dụng các cải tiến
"""

import time
import os
import sys
import logging
import json
from pathlib import Path
from typing import Dict, Any, List
import psutil
import gc

# Thêm src vào path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from utils.performance_monitor import PerformanceMonitor, PerformanceOptimizer, monitor_performance
from utils.thread_manager import ThreadManager
from utils.cache_manager import TranslationCacheManager, MemoryCacheManager
from utils.memory_manager import MemoryManager

# Cấu hình logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class PerformanceBenchmark:
    """Class để benchmark hiệu năng ứng dụng"""
    
    def __init__(self):
        self.results = {}
        self.benchmark_data = []
        
    def run_memory_benchmark(self) -> Dict[str, Any]:
        """Benchmark memory management"""
        logger.info("Running memory management benchmark...")
        
        results = {
            'test_name': 'Memory Management',
            'timestamp': time.time(),
            'tests': {}
        }
        
        # Test 1: Memory allocation và cleanup
        start_time = time.time()
        memory_manager = MemoryManager(enable_profiling=True)
        
        # Allocate memory
        large_objects = []
        for i in range(1000):
            large_objects.append([f"test_data_{j}" for j in range(100)])
            
        allocation_time = time.time() - start_time
        memory_after_allocation = psutil.Process().memory_info().rss
        
        # Cleanup
        start_cleanup = time.time()
        del large_objects
        gc.collect()
        cleanup_time = time.time() - start_cleanup
        memory_after_cleanup = psutil.Process().memory_info().rss
        
        results['tests']['memory_allocation'] = {
            'allocation_time': allocation_time,
            'memory_after_allocation_mb': memory_after_allocation / (1024 * 1024),
            'cleanup_time': cleanup_time,
            'memory_after_cleanup_mb': memory_after_cleanup / (1024 * 1024),
            'memory_freed_mb': (memory_after_allocation - memory_after_cleanup) / (1024 * 1024)
        }
        
        # Test 2: Memory monitoring
        memory_manager.start_monitoring()
        time.sleep(2)
        memory_profile = memory_manager.get_memory_profile()
        memory_manager.stop_monitoring()
        
        results['tests']['memory_monitoring'] = {
            'profile_enabled': memory_profile.get('enabled', False),
            'data_points': memory_profile.get('data_points', 0),
            'cleanup_count': memory_profile.get('cleanup_stats', {}).get('total_cleanups', 0)
        }
        
        return results
        
    def run_cache_benchmark(self) -> Dict[str, Any]:
        """Benchmark cache performance"""
        logger.info("Running cache performance benchmark...")
        
        results = {
            'test_name': 'Cache Performance',
            'timestamp': time.time(),
            'tests': {}
        }
        
        # Test 1: Memory cache performance
        memory_cache = MemoryCacheManager(max_size=1000)
        
        # Write performance
        start_time = time.time()
        for i in range(1000):
            memory_cache.set(f"key_{i}", f"value_{i}" * 100)
        write_time = time.time() - start_time
        
        # Read performance
        start_time = time.time()
        for i in range(1000):
            value = memory_cache.get(f"key_{i}")
        read_time = time.time() - start_time
        
        results['tests']['memory_cache'] = {
            'write_1000_items_time': write_time,
            'read_1000_items_time': read_time,
            'write_rate_items_per_sec': 1000 / write_time if write_time > 0 else 0,
            'read_rate_items_per_sec': 1000 / read_time if read_time > 0 else 0
        }
        
        # Test 2: File cache performance
        file_cache = TranslationCacheManager(cache_type='file')
        
        # Write performance
        start_time = time.time()
        for i in range(100):
            file_cache.set(f"file_key_{i}", f"file_value_{i}" * 100)
        file_write_time = time.time() - start_time
        
        # Read performance
        start_time = time.time()
        for i in range(100):
            value = file_cache.get(f"file_key_{i}")
        file_read_time = time.time() - start_time
        
        results['tests']['file_cache'] = {
            'write_100_items_time': file_write_time,
            'read_100_items_time': file_read_time,
            'write_rate_items_per_sec': 100 / file_write_time if file_write_time > 0 else 0,
            'read_rate_items_per_sec': 100 / file_read_time if file_read_time > 0 else 0
        }
        
        # Cleanup file cache
        file_cache.clear()
        
        return results
        
    def run_threading_benchmark(self) -> Dict[str, Any]:
        """Benchmark threading performance"""
        logger.info("Running threading performance benchmark...")
        
        results = {
            'test_name': 'Threading Performance',
            'timestamp': time.time(),
            'tests': {}
        }
        
        # Test 1: Thread pool performance
        thread_manager = ThreadManager(max_workers=4)
        
        def cpu_intensive_task(n):
            """Task tính toán CPU-intensive"""
            result = 0
            for i in range(n):
                result += i ** 2
            return result
            
        # Single thread performance
        start_time = time.time()
        for i in range(10):
            cpu_intensive_task(100000)
        single_thread_time = time.time() - start_time
        
        # Multi-thread performance
        tasks = [lambda: cpu_intensive_task(100000) for _ in range(10)]
        start_time = time.time()
        thread_manager.run_tasks(tasks, show_progress=False)
        multi_thread_time = time.time() - start_time
        
        results['tests']['thread_pool'] = {
            'single_thread_time': single_thread_time,
            'multi_thread_time': multi_thread_time,
            'speedup': single_thread_time / multi_thread_time if multi_thread_time > 0 else 0,
            'efficiency': (single_thread_time / multi_thread_time) / 4 if multi_thread_time > 0 else 0  # 4 workers
        }
        
        # Test 2: Async performance
        async def async_task(n):
            """Async task"""
            import asyncio
            await asyncio.sleep(0.1)  # Simulate async work
            return cpu_intensive_task(n)
            
        async def run_async_benchmark():
            import asyncio
            tasks = [async_task(10000) for _ in range(10)]
            start_time = time.time()
            await asyncio.gather(*tasks)
            return time.time() - start_time
            
        # Run async benchmark
        try:
            import asyncio
            async_time = asyncio.run(run_async_benchmark())
            results['tests']['async_performance'] = {
                'async_time': async_time,
                'vs_single_thread': single_thread_time / async_time if async_time > 0 else 0
            }
        except Exception as e:
            results['tests']['async_performance'] = {'error': str(e)}
            
        thread_manager.shutdown()
        return results
        
    def run_performance_monitoring_benchmark(self) -> Dict[str, Any]:
        """Benchmark performance monitoring"""
        logger.info("Running performance monitoring benchmark...")
        
        results = {
            'test_name': 'Performance Monitoring',
            'timestamp': time.time(),
            'tests': {}
        }
        
        # Test 1: Function timing overhead
        monitor = PerformanceMonitor(enable_monitoring=True)
        
        def test_function():
            time.sleep(0.1)
            return "test"
            
        # Without monitoring
        start_time = time.time()
        for _ in range(100):
            test_function()
        without_monitoring_time = time.time() - start_time
        
        # With monitoring
        monitored_function = monitor.time_function("test_function")(test_function)
        start_time = time.time()
        for _ in range(100):
            monitored_function()
        with_monitoring_time = time.time() - start_time
        
        results['tests']['monitoring_overhead'] = {
            'without_monitoring_time': without_monitoring_time,
            'with_monitoring_time': with_monitoring_time,
            'overhead_percentage': ((with_monitoring_time - without_monitoring_time) / without_monitoring_time) * 100 if without_monitoring_time > 0 else 0
        }
        
        # Test 2: Performance report generation
        start_time = time.time()
        performance_report = monitor.get_performance_report()
        report_generation_time = time.time() - start_time
        
        results['tests']['report_generation'] = {
            'report_generation_time': report_generation_time,
            'report_size_bytes': len(json.dumps(performance_report))
        }
        
        # Test 3: Optimization
        optimizer = PerformanceOptimizer(monitor)
        start_time = time.time()
        optimization_report = optimizer.generate_optimization_report()
        optimization_time = time.time() - start_time
        
        results['tests']['optimization'] = {
            'optimization_time': optimization_time,
            'optimization_report_size': len(json.dumps(optimization_report))
        }
        
        monitor.stop_monitoring()
        return results
        
    @monitor_performance("run_all_benchmarks")
    def run_all_benchmarks(self) -> Dict[str, Any]:
        """Chạy tất cả benchmarks"""
        logger.info("Starting comprehensive performance benchmark...")
        
        start_time = time.time()
        
        # Run individual benchmarks
        benchmarks = [
            self.run_memory_benchmark,
            self.run_cache_benchmark,
            self.run_threading_benchmark,
            self.run_performance_monitoring_benchmark
        ]
        
        all_results = []
        for benchmark in benchmarks:
            try:
                result = benchmark()
                all_results.append(result)
                logger.info(f"Completed {result['test_name']} benchmark")
            except Exception as e:
                logger.error(f"Benchmark failed: {e}")
                all_results.append({
                    'test_name': benchmark.__name__,
                    'error': str(e),
                    'timestamp': time.time()
                })
                
        total_time = time.time() - start_time
        
        # Compile final results
        final_results = {
            'benchmark_summary': {
                'total_benchmarks': len(benchmarks),
                'successful_benchmarks': len([r for r in all_results if 'error' not in r]),
                'failed_benchmarks': len([r for r in all_results if 'error' in r]),
                'total_execution_time': total_time
            },
            'benchmark_results': all_results,
            'system_info': self._get_system_info(),
            'timestamp': time.time()
        }
        
        self.results = final_results
        return final_results
        
    def _get_system_info(self) -> Dict[str, Any]:
        """Lấy thông tin hệ thống"""
        try:
            return {
                'python_version': sys.version,
                'platform': sys.platform,
                'cpu_count': psutil.cpu_count(),
                'memory_total_gb': psutil.virtual_memory().total / (1024**3),
                'disk_usage': psutil.disk_usage('/').percent if os.path.exists('/') else 0
            }
        except Exception as e:
            return {'error': str(e)}
            
    def save_results(self, filename: str = None) -> str:
        """Lưu kết quả benchmark vào file"""
        if not self.results:
            logger.warning("No benchmark results to save")
            return ""
            
        if filename is None:
            timestamp = time.strftime("%Y%m%d_%H%M%S")
            filename = f"benchmark_results_{timestamp}.json"
            
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(self.results, f, indent=2, ensure_ascii=False)
                
            logger.info(f"Benchmark results saved to {filename}")
            return filename
            
        except Exception as e:
            logger.error(f"Error saving benchmark results: {e}")
            return ""
            
    def print_summary(self):
        """In summary của benchmark results"""
        if not self.results:
            logger.warning("No benchmark results to display")
            return
            
        summary = self.results['benchmark_summary']
        print("\n" + "="*60)
        print("PERFORMANCE BENCHMARK SUMMARY")
        print("="*60)
        print(f"Total Benchmarks: {summary['total_benchmarks']}")
        print(f"Successful: {summary['successful_benchmarks']}")
        print(f"Failed: {summary['failed_benchmarks']}")
        print(f"Total Execution Time: {summary['total_execution_time']:.2f}s")
        print("="*60)
        
        # Print individual benchmark results
        for result in self.results['benchmark_results']:
            if 'error' in result:
                print(f"❌ {result['test_name']}: FAILED - {result['error']}")
            else:
                print(f"✅ {result['test_name']}: COMPLETED")
                
        print("="*60)
        
        # Print system info
        system_info = self.results.get('system_info', {})
        if 'error' not in system_info:
            print(f"System: Python {system_info.get('python_version', 'Unknown')}")
            print(f"CPU Cores: {system_info.get('cpu_count', 'Unknown')}")
            print(f"Memory: {system_info.get('memory_total_gb', 0):.1f} GB")
            print(f"Platform: {system_info.get('platform', 'Unknown')}")

def main():
    """Main function để chạy benchmark"""
    logger.info("Starting VoiceSub Translator Performance Benchmark")
    
    try:
        # Tạo benchmark instance
        benchmark = PerformanceBenchmark()
        
        # Chạy tất cả benchmarks
        results = benchmark.run_all_benchmarks()
        
        # In summary
        benchmark.print_summary()
        
        # Lưu results
        filename = benchmark.save_results()
        if filename:
            print(f"\nDetailed results saved to: {filename}")
            
        # Performance optimization
        print("\nRunning performance optimization...")
        optimizer = PerformanceOptimizer()
        optimization_report = optimizer.generate_optimization_report()
        
        print("Optimization completed!")
        print(f"Memory freed: {optimization_report['memory_optimization'].get('memory_freed', 0)} bytes")
        
        return 0
        
    except Exception as e:
        logger.error(f"Benchmark failed: {e}")
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)