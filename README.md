# Tạo Phụ Đề Bằng AI

Ứng dụng tự động tạo và dịch phụ đề sử dụng các API AI.

## Tính Năng

- Tự động nhận diện giọng nói và tạo phụ đề
- Dịch phụ đề sang nhiều ngôn ngữ khác nhau
- Hỗ trợ nhiều định dạng video và phụ đề
- Giao diện người dùng thân thiện
- Xử lý hàng loạt nhiều file
- Tối ưu hóa hiệu suất với đa luồng
- Cache kết quả để tái sử dụng

## Cài Đặt

1. Clone repository:

```bash
git clone https://github.com/yourusername/tao_phu_de_bang_ai.git
cd tao_phu_de_bang_ai
```

2. Tạo môi trường ảo:

```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# hoặc
.\venv\Scripts\activate  # Windows
```

3. Cài đặt dependencies:

```bash
pip install -r requirements.txt
```

4. Tạo file .env từ mẫu:

```bash
cp .env.example .env
```

5. Cập nhật API keys trong file .env

## Sử Dụng

### Utility Classes

#### CacheManager

Quản lý cache để lưu trữ và tái sử dụng kết quả:

```python
from src.utils.cache_manager import CacheManager

cache = CacheManager()
# Lưu kết quả
cache.set("text", "provider", "model", "result")
# Lấy kết quả
result = cache.get("text", "provider", "model")
```

#### ThreadManager

Quản lý xử lý đa luồng:

```python
from src.utils.thread_manager import ThreadManager

thread_mgr = ThreadManager(max_workers=4)
results = thread_mgr.run_tasks(
    tasks=[task1, task2],
    task_names=["Task 1", "Task 2"],
    show_progress=True
)
```

#### ProgressManager

Hiển thị tiến trình xử lý:

```python
from src.utils.progress_manager import ProgressManager

progress = ProgressManager()
with progress.create_progress(100, "Processing") as pbar:
    # Xử lý công việc
    progress.update_progress(1)
```

#### MemoryManager

Quản lý và tối ưu bộ nhớ:

```python
from src.utils.memory_manager import MemoryManager

memory_mgr = MemoryManager()
with memory_mgr:
    # Xử lý công việc nặng
    pass
```

#### LogManager

Quản lý logs:

```python
from src.utils.log_manager import LogManager

log_mgr = LogManager()
# Log lỗi
log_mgr.log_error(error, context={"task": "translation"})
# Log API call
log_mgr.log_api_call(
    provider="novita",
    model="test-model",
    success=True,
    duration=0.5
)
```

## Testing

Chạy tests:

```bash
./run_tests.sh
```

Hoặc chạy riêng từng module:

```bash
pytest tests/test_utils_comprehensive.py -v
```

## Cấu Trúc Project

```
.
├── src/
│   ├── api/              # API handlers và providers
│   ├── gui/              # Giao diện người dùng
│   ├── translator/       # Xử lý dịch thuật
│   └── utils/            # Các utility classes
├── tests/                # Tests
├── requirements.txt      # Dependencies
└── README.md            # Tài liệu
```

## Contributing

1. Fork repository
2. Tạo branch mới (`git checkout -b feature/AmazingFeature`)
3. Commit thay đổi (`git commit -m 'Add some AmazingFeature'`)
4. Push lên branch (`git push origin feature/AmazingFeature`)
5. Tạo Pull Request

## License

Distributed under the MIT License. See `LICENSE` for more information.
