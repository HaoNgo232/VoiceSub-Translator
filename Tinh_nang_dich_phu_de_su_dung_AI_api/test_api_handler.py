import os
import logging
from api_handler import GroqAPIHandler
from unittest.mock import patch, MagicMock
import pytest
import time

# Cấu hình logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# Dữ liệu test
TEST_SUBTITLES = """1
00:00:01,000 --> 00:00:04,000
---BLOCK 1---
Welcome to this course!
---END BLOCK 1---

2
00:00:05,000 --> 00:00:08,000
---BLOCK 2---
In this video, we will learn about Python programming.
---END BLOCK 2---

3
00:00:09,000 --> 00:00:12,000
---BLOCK 3---
Let's get started with some basic concepts.
---END BLOCK 3---"""

# Mock response cho API
MOCK_RESPONSE = """1
00:00:01,000 --> 00:00:04,000
---BLOCK 1---
Chào mừng đến với khóa học này!
---END BLOCK 1---

2
00:00:05,000 --> 00:00:08,000
---BLOCK 2---
Trong video này, chúng ta sẽ học về lập trình Python.
---END BLOCK 2---

3
00:00:09,000 --> 00:00:12,000
---BLOCK 3---
Hãy bắt đầu với một số khái niệm cơ bản.
---END BLOCK 3---"""

@pytest.fixture
def mock_groq_client():
    """Tạo mock cho Groq client."""
    with patch('groq.Groq') as mock:
        # Tạo mock cho chat completion
        mock_completion = MagicMock()
        mock_completion.choices = [MagicMock()]
        mock_completion.choices[0].message.content = MOCK_RESPONSE
        
        # Tạo mock cho response
        mock_response = MagicMock()
        mock_response.headers = {
            'x-ratelimit-limit-requests': '100',
            'x-ratelimit-remaining-requests': '95',
            'x-ratelimit-reset-requests': '3600',
            'x-ratelimit-limit-tokens': '1000000',
            'x-ratelimit-remaining-tokens': '950000',
            'x-ratelimit-reset-tokens': '3600'
        }
        mock_completion.response = mock_response
        
        # Cấu hình mock client
        mock_client = MagicMock()
        mock_client.chat.completions.create.return_value = mock_completion
        mock.return_value = mock_client
        
        yield mock

def test_translate_text_success(mock_groq_client):
    """Test dịch văn bản thành công."""
    # Tạo API handler với mock client
    handler = GroqAPIHandler()
    
    # Test dịch
    result = handler.translate_text(TEST_SUBTITLES)
    
    # Kiểm tra kết quả
    assert result is not None
    assert "Chào mừng đến với khóa học này" in result
    assert "---BLOCK 1---" in result
    assert "---END BLOCK 1---" in result
    
    # Kiểm tra số lượng block
    assert result.count("---BLOCK") == 3
    assert result.count("---END BLOCK") == 3

def test_translate_text_empty_input():
    """Test với input rỗng."""
    handler = GroqAPIHandler()
    result = handler.translate_text("")
    assert result is None

def test_translate_text_invalid_blocks(mock_groq_client):
    """Test với block markers không hợp lệ."""
    # Tạo response không hợp lệ
    mock_groq_client.return_value.chat.completions.create.return_value.choices[0].message.content = """
    1
    00:00:01,000 --> 00:00:04,000
    ---BLOCK 1---
    Chào mừng!
    ---END BLOCK 2---
    """
    
    handler = GroqAPIHandler()
    result = handler.translate_text(TEST_SUBTITLES)
    assert result is None

def test_rate_limit_handling(mock_groq_client):
    """Test xử lý rate limit."""
    # Giả lập rate limit error
    mock_groq_client.return_value.chat.completions.create.side_effect = [
        Exception("Rate limit exceeded"),
        MagicMock(choices=[MagicMock(message=MagicMock(content=MOCK_RESPONSE))])
    ]
    
    handler = GroqAPIHandler()
    result = handler.translate_text(TEST_SUBTITLES)
    
    # Kiểm tra đã retry và thành công
    assert result is not None
    assert mock_groq_client.return_value.chat.completions.create.call_count == 2

def test_model_switching(mock_groq_client):
    """Test chuyển đổi model khi gặp lỗi."""
    # Giả lập lỗi với model đầu tiên
    mock_groq_client.return_value.chat.completions.create.side_effect = [
        Exception("Model error"),
        MagicMock(choices=[MagicMock(message=MagicMock(content=MOCK_RESPONSE))])
    ]
    
    handler = GroqAPIHandler()
    result = handler.translate_text(TEST_SUBTITLES)
    
    # Kiểm tra đã chuyển model và thành công
    assert result is not None
    assert mock_groq_client.return_value.chat.completions.create.call_count == 2

def test_rate_limiter():
    """Test rate limiter."""
    handler = GroqAPIHandler()
    start_time = time.time()
    
    # Gọi API 3 lần liên tiếp
    for _ in range(3):
        handler.rate_limiter.wait()
    
    end_time = time.time()
    elapsed = end_time - start_time
    
    # Kiểm tra thời gian chờ tối thiểu
    assert elapsed >= 1.8  # 0.9s * 2 lần chờ

def test_model_stats_update(mock_groq_client):
    """Test cập nhật thống kê model."""
    handler = GroqAPIHandler()
    result = handler.translate_text(TEST_SUBTITLES)
    
    # Kiểm tra thống kê đã được cập nhật
    model = handler.model_queue[0]
    assert handler.models[model]["successful_requests"] > 0
    assert handler.models[model]["last_success_time"] > 0

def test_multiple_models_usage(mock_groq_client):
    """Test sử dụng nhiều model."""
    # Giả lập lỗi với tất cả model trừ model cuối
    errors = [Exception("Model error")] * (len(handler.models) - 1)
    errors.append(MagicMock(choices=[MagicMock(message=MagicMock(content=MOCK_RESPONSE))]))
    mock_groq_client.return_value.chat.completions.create.side_effect = errors
    
    handler = GroqAPIHandler()
    result = handler.translate_text(TEST_SUBTITLES)
    
    # Kiểm tra đã thử qua tất cả model
    assert result is not None
    assert mock_groq_client.return_value.chat.completions.create.call_count == len(handler.models)

if __name__ == "__main__":
    # Chạy tests
    pytest.main([__file__, "-v"]) 