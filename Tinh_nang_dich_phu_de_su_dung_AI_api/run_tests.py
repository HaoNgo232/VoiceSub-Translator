import os
import sys
import time
import unittest
import logging
from datetime import datetime
from typing import List, Dict, Any

# Cấu hình logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def run_test_suite(test_module: str) -> Dict[str, Any]:
    """Chạy một test suite và trả về kết quả."""
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromName(test_module)
    runner = unittest.TextTestRunner(verbosity=2)
    
    start_time = time.time()
    result = runner.run(suite)
    end_time = time.time()
    
    return {
        'module': test_module,
        'total': result.testsRun,
        'failures': len(result.failures),
        'errors': len(result.errors),
        'skipped': len(result.skipped),
        'success': result.wasSuccessful(),
        'duration': end_time - start_time
    }

def create_report(results: List[Dict[str, Any]], output_dir: str = "test_reports"):
    """Tạo báo cáo test."""
    os.makedirs(output_dir, exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_file = os.path.join(output_dir, f"test_report_{timestamp}.txt")
    
    total_tests = sum(r['total'] for r in results)
    total_failures = sum(r['failures'] for r in results)
    total_errors = sum(r['errors'] for r in results)
    total_skipped = sum(r['skipped'] for r in results)
    total_duration = sum(r['duration'] for r in results)
    
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write("=== Test Execution Report ===\n\n")
        f.write(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"Total Duration: {total_duration:.2f} seconds\n\n")
        
        f.write("Summary:\n")
        f.write(f"Total Tests: {total_tests}\n")
        f.write(f"Passed: {total_tests - total_failures - total_errors - total_skipped}\n")
        f.write(f"Failed: {total_failures}\n")
        f.write(f"Errors: {total_errors}\n")
        f.write(f"Skipped: {total_skipped}\n\n")
        
        f.write("Detailed Results:\n")
        for result in results:
            f.write(f"\n{result['module']}:\n")
            f.write(f"  Tests Run: {result['total']}\n")
            f.write(f"  Failures: {result['failures']}\n")
            f.write(f"  Errors: {result['errors']}\n")
            f.write(f"  Skipped: {result['skipped']}\n")
            f.write(f"  Success: {'Yes' if result['success'] else 'No'}\n")
            f.write(f"  Duration: {result['duration']:.2f} seconds\n")
    
    print(f"\nTest report saved to: {report_file}")
    return report_file

def main():
    """Chạy tất cả các test và tạo báo cáo."""
    # Danh sách các test module
    test_modules = [
        'tests.test_providers',
        'tests.test_rate_limits',
        'tests.test_error_handling',
        'tests.test_real_world'
    ]
    
    print("=== Starting Test Suite ===\n")
    results = []
    
    for module in test_modules:
        print(f"\nRunning {module}...")
        try:
            result = run_test_suite(module)
            results.append(result)
        except Exception as e:
            print(f"Error running {module}: {str(e)}")
            results.append({
                'module': module,
                'total': 0,
                'failures': 0,
                'errors': 1,
                'skipped': 0,
                'success': False,
                'duration': 0
            })
    
    # Tạo báo cáo
    report_file = create_report(results)
    
    # Kiểm tra kết quả tổng thể
    total_failures = sum(r['failures'] for r in results)
    total_errors = sum(r['errors'] for r in results)
    
    if total_failures > 0 or total_errors > 0:
        print("\n❌ Some tests failed! Check the report for details.")
        sys.exit(1)
    else:
        print("\n✅ All tests passed successfully!")
        sys.exit(0)

if __name__ == '__main__':
    main()
