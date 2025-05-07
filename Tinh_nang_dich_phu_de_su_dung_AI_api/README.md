# API Handler cho Dịch Phụ Đề

Module xử lý API cho việc dịch phụ đề sử dụng Groq API.

## Cài đặt

1. Tạo môi trường ảo:

```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# hoặc
.\venv\Scripts\activate  # Windows
```

2. Cài đặt dependencies:

```bash
pip install -r requirements.txt
```

## Chạy Tests

1. Chạy tất cả tests:

```bash
./run_tests.sh  # Linux/Mac
# hoặc
run_tests.bat  # Windows
```

2. Chạy test cụ thể:

```bash
python -m pytest test_api_handler.py -v
```

## Các Test Case

1. `test_translate_text_success`: Test dịch văn bản thành công
2. `test_translate_text_empty_input`: Test với input rỗng
3. `test_translate_text_invalid_blocks`: Test với block markers không hợp lệ
4. `test_rate_limit_handling`: Test xử lý rate limit
5. `test_model_switching`: Test chuyển đổi model
6. `test_rate_limiter`: Test rate limiter
7. `test_model_stats_update`: Test cập nhật thống kê model
8. `test_multiple_models_usage`: Test sử dụng nhiều model

## Cấu trúc Code

- `api_handler.py`: Class chính xử lý API
- `test_api_handler.py`: File chứa các test case
- `conftest.py`: Cấu hình pytest
- `requirements.txt`: Danh sách dependencies
- `run_tests.sh`: Script chạy test (Linux/Mac)
- `run_tests.bat`: Script chạy test (Windows)
