import os
import time
import logging
import unittest
import requests
import httpx
from unittest.mock import patch, Mock
from datetime import datetime, timezone

from api.providers.groq import GroqAPIHandler
from api.providers.openrouter import OpenrouterAPIHandler as OpenRouterAPIHandler
from api.manager import APIManager
from api.config import APIConfig
from api.exceptions import (
    TranslationError,
    AuthenticationError,
    ConnectionError,
    RateLimitError,
    ValidationError,
    ConfigurationError,
    NoAvailableProvidersError
)

# Cấu hình logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

class TestErrorHandling(unittest.TestCase):
    """Test xử lý lỗi và fallback."""
    
    def setUp(self):
        """Khởi tạo test environment."""
        # Mock config để không cần API keys thật
        self.config = Mock(spec=APIConfig)
        self.config.get_provider_config.return_value = {
            'api_key': 'fake_key',
            'model': 'test-model'
        }
        self.config.get_available_providers.return_value = {
            'groq': {
                'api_key': 'fake_groq_key',
                'model': 'test-model'
            },
            'openrouter': {
                'api_key': 'fake_openrouter_key',
                'model': 'test-model'
            }
        }
        
        # Tạo mock handlers với phương thức get_priority()
        # Tạo mock handlers với phương thức get_priority() và thuộc tính max_retries
        self.groq_handler = Mock(spec=GroqAPIHandler)
        self.groq_handler.get_priority.return_value = 1
        self.groq_handler.name = 'groq'
        self.groq_handler.max_retries = 3 # Thêm max_retries
        self.groq_handler.config = Mock() 
        self.groq_handler.config.name = 'groq' 
        
        self.openrouter_handler = Mock(spec=OpenRouterAPIHandler)
        self.openrouter_handler.get_priority.return_value = 2
        self.openrouter_handler.name = 'openrouter'
        self.openrouter_handler.max_retries = 3 # Thêm max_retries
        self.openrouter_handler.config = Mock() 
        self.openrouter_handler.config.name = 'openrouter' 
        
        # Patch các provider class để trả về mock handlers
        # Patch các provider class để trả về mock handlers đã cấu hình
        # Không cần mock __init__ phức tạp nữa, chỉ cần return_value
        self.groq_patcher = patch('api.providers.groq.GroqAPIHandler', return_value=self.groq_handler)
        self.openrouter_patcher = patch('api.providers.openrouter.OpenrouterAPIHandler', return_value=self.openrouter_handler)
        
        # Start patches
        self.mock_groq_class = self.groq_patcher.start()
        self.mock_openrouter_class = self.openrouter_patcher.start()
        
        # Khởi tạo manager
        self.manager = APIManager(self.config)
        
        # Text mẫu để test
        self.test_text = """---BLOCK 1---
This is a test message.
---END BLOCK 1---"""

    def test_invalid_auth(self):
        """Test xử lý lỗi xác thực."""
        # Cấu hình mock handlers để ném AuthenticationError
        self.groq_handler.translate_text.side_effect = AuthenticationError("Invalid Groq API key")
        self.openrouter_handler.translate_text.side_effect = AuthenticationError("Invalid OpenRouter API key")
        
        # Kiểm tra manager xử lý lỗi xác thực
        with self.assertRaisesRegex(TranslationError, "All providers failed"):
            self.manager.translate(self.test_text)

    def test_connection_error(self):
        """Test xử lý lỗi kết nối."""
        # Cấu hình mock handlers để ném ConnectionError
        self.groq_handler.translate_text.side_effect = ConnectionError("Connection failed")
        self.openrouter_handler.translate_text.side_effect = ConnectionError("Connection failed")
        
        # Test với APIManager
        with self.assertRaisesRegex(TranslationError, "All providers failed"):
            self.manager.translate(self.test_text)

    def test_provider_fallback(self):
        """Test fallback giữa các provider."""
        # Giả lập Groq thất bại
        self.groq_handler.translate_text.side_effect = TranslationError("groq", "API error")
        # Giả lập OpenRouter thành công
        self.openrouter_handler.translate_text.return_value = "---BLOCK 1---\nTranslated by OpenRouter.\n---END BLOCK 1---"
        
        try:
            # Nên fallback sang OpenRouter
            result = self.manager.translate(self.test_text)
            self.assertIsNotNone(result)
            print("\nFallback successful, used OpenRouter")
        except Exception as e:
            self.fail(f"Fallback failed: {str(e)}")

    def test_error_recovery(self):
        """Test khôi phục sau lỗi."""
        print("\nTesting error recovery...")
        
        # Chuỗi các response mô phỏng lỗi rồi phục hồi
        self.groq_handler.translate_text.side_effect = [
            AuthenticationError("Invalid API key"),
            "---BLOCK 1---\nTranslated content\n---END BLOCK 1---"
        ]
        
        # Lần đầu sẽ thất bại
        try:
            result = self.groq_handler.translate_text(self.test_text)
            self.fail("Should have raised AuthenticationError")
        except AuthenticationError:
            print("Authentication error occurred as expected")
            
        # Lần hai sẽ thành công
        result = self.groq_handler.translate_text(self.test_text)
        self.assertIsNotNone(result)
        print("Successfully recovered after error")

    def test_rate_limit_error_handling(self):
        """Test xử lý rate limit error."""
        print("\nTesting rate limit error handling...")
        
        # Cấu hình mock handlers để ném RateLimitError
        self.groq_handler.translate_text.side_effect = RateLimitError(60, "Rate limit exceeded")
        self.openrouter_handler.translate_text.side_effect = RateLimitError(30, "Rate limit exceeded")
        
        # Kiểm tra manager xử lý rate limit
        with self.assertRaisesRegex(TranslationError, "All providers failed"):
            self.manager.translate(self.test_text)

    def test_manager_error_handling(self):
        """Test xử lý lỗi của APIManager."""
        print("\nTesting APIManager error handling...")
        
        # Giả lập tất cả provider đều lỗi
        self.groq_handler.translate_text.side_effect = TranslationError("groq", "API error")
        self.openrouter_handler.translate_text.side_effect = TranslationError("openrouter", "API error")
                
        with self.assertRaisesRegex(TranslationError, "All providers failed"):
            self.manager.translate(self.test_text)
                    
        print("Successfully handled all providers failing")

    def tearDown(self):
        """Dọn dẹp sau mỗi test."""
        # Reset mock handlers
        self.groq_handler.reset_mock()
        self.openrouter_handler.reset_mock()
        
        # Stop patches
        self.groq_patcher.stop()
        self.openrouter_patcher.stop()

if __name__ == '__main__':
    unittest.main(verbosity=2)
