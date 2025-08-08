import importlib.util
import time
from pathlib import Path

spec = importlib.util.spec_from_file_location(
    "thread_manager", Path(__file__).resolve().parents[1] / "src/utils/thread_manager.py"
)
thread_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(thread_module)
ThreadManager = thread_module.ThreadManager


def test_active_task_count_and_idempotent_completion():
    manager = ThreadManager(max_workers=2)

    def task():
        time.sleep(0.05)
        return 'done'

    results = manager.run_tasks([task, task], show_progress=False)
    assert results == ['done', 'done']
    assert manager.active_task_count() == 0

    manager._task_completed(0)
    assert manager.active_task_count() == 0

    manager.shutdown()

