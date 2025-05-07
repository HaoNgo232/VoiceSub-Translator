import os
import pytest
from src.api.handler import GroqAPIHandler

def test_api_handler_init(mock_env_vars):
    """Test khởi tạo API handler."""
    handler = GroqAPIHandler()
    assert handler.api_key == "test_api_key"
    assert handler.client is not None
    assert handler.model == "mixtral-8x7b-32768"
    assert handler.max_tokens == 4096
    assert handler.temperature == 0.7

def test_wait_for_rate_limit(mock_env_vars):
    """Test rate limiting."""
    handler = GroqAPIHandler()
    
    # Gọi lần đầu
    handler._wait_for_rate_limit()
    first_time = handler.last_request_time
    
    # Gọi lần thứ hai ngay lập tức
    handler._wait_for_rate_limit()
    second_time = handler.last_request_time
    
    # Kiểm tra khoảng thời gian
    time_diff = second_time - first_time
    assert time_diff >= handler.min_request_interval

def test_translate_text(mock_env_vars):
    """Test dịch văn bản."""
    handler = GroqAPIHandler()
    
    # Test với văn bản đơn giản
    text = "Hello, world!"
    translated = handler.translate_text(text)
    
    assert translated is not None
    assert isinstance(translated, str)
    assert len(translated) > 0

def test_translate_srt(mock_env_vars):
    """Test dịch file SRT."""
    handler = GroqAPIHandler()
    
    # Test với nội dung SRT
    srt_content = """1
00:00:01,000 --> 00:00:04,000
This is a test subtitle file.

2
00:00:05,000 --> 00:00:08,000
It contains multiple subtitle blocks."""
    
    translated = handler.translate_text(srt_content)
    
    assert translated is not None
    assert isinstance(translated, str)
    assert len(translated) > 0
    assert "--> 00:00:04,000" in translated  # Giữ nguyên timestamp

def test_test_connection(mock_env_vars):
    """Test kết nối đến API."""
    handler = GroqAPIHandler()
    assert handler.test_connection() 