import os
import logging
import unittest
from datetime import datetime, timezone
from api.providers.groq import GroqAPIHandler
from api.providers.openrouter import OpenrouterAPIHandler # Sửa tên class
from api.config import APIConfig, ProviderConfig

# Cấu hình logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

class TestProviders(unittest.TestCase):
    """Test các provider dịch."""
    
    @classmethod
    def setUpClass(cls):
        """Khởi tạo các provider trước khi test."""
        cls.config = APIConfig()
        
        # Khởi tạo Groq provider
        cls.groq_config = cls.config.get_provider_config('groq')
        if not cls.groq_config:
            raise ValueError("Groq configuration not found. Check .env file.")
        cls.groq = GroqAPIHandler(cls.groq_config)
        
        # Khởi tạo OpenRouter provider
        cls.openrouter_config = cls.config.get_provider_config('openrouter')
        if not cls.openrouter_config:
            raise ValueError("OpenRouter configuration not found. Check .env file.")
        cls.openrouter = OpenrouterAPIHandler(cls.openrouter_config) # Sửa tên class
        
        # Test text với các độ phức tạp khác nhau
        cls.simple_text = """---BLOCK 1---
Hello world! How are you?
---END BLOCK 1---"""

        cls.medium_text = """---BLOCK 1---
Hello world! How are you?
---END BLOCK 1---
---BLOCK 2---
This is a test message with some technical terms.
---END BLOCK 2---
---BLOCK 3---
We need to ensure that all blocks are translated correctly.
---END BLOCK 3---"""

        cls.complex_text = """---BLOCK 1---
This is a more complex text with technical terminology.
---END BLOCK 1---
---BLOCK 2---
It includes words like "API", "rate limiting", and "configuration".
---END BLOCK 2---
---BLOCK 3---
Let's see how well the translation handles these terms.
---END BLOCK 3---
---BLOCK 4---
We also need to verify Unicode characters: ©®™
---END BLOCK 4---
---BLOCK 5---
And some numbers: 123,456.78 and dates: 2025-04-02
---END BLOCK 5---"""

    def test_groq_connection(self):
        """Test kết nối với Groq API."""
        try:
            self.groq._test_connection()
            self.assertTrue(True)  # Nếu không raise exception
        except Exception as e:
            self.fail(f"Groq connection failed: {str(e)}")

    def test_openrouter_connection(self):
        """Test kết nối với OpenRouter API."""
        try:
            self.openrouter._test_connection()
            self.assertTrue(True)  # Nếu không raise exception
        except Exception as e:
            self.fail(f"OpenRouter connection failed: {str(e)}")

    def test_groq_simple_translation(self):
        """Test dịch đơn giản với Groq."""
        result = self.groq.translate_text(self.simple_text)
        self.assertIsNotNone(result)
        self.assertTrue(self.groq._validate_translation(self.simple_text, result))
        print("\nGroq simple translation:")
        print(result)

    def test_openrouter_simple_translation(self):
        """Test dịch đơn giản với OpenRouter."""
        result = self.openrouter.translate_text(self.simple_text)
        self.assertIsNotNone(result)
        self.assertTrue(self.openrouter._validate_translation(self.simple_text, result))
        print("\nOpenRouter simple translation:")
        print(result)

    def test_groq_medium_translation(self):
        """Test dịch văn bản trung bình với Groq."""
        result = self.groq.translate_text(self.medium_text)
        self.assertIsNotNone(result)
        self.assertTrue(self.groq._validate_translation(self.medium_text, result))
        print("\nGroq medium translation:")
        print(result)

    def test_openrouter_medium_translation(self):
        """Test dịch văn bản trung bình với OpenRouter."""
        result = self.openrouter.translate_text(self.medium_text)
        self.assertIsNotNone(result)
        self.assertTrue(self.openrouter._validate_translation(self.medium_text, result))
        print("\nOpenRouter medium translation:")
        print(result)

    def test_groq_complex_translation(self):
        """Test dịch văn bản phức tạp với Groq."""
        result = self.groq.translate_text(self.complex_text)
        self.assertIsNotNone(result)
        self.assertTrue(self.groq._validate_translation(self.complex_text, result))
        print("\nGroq complex translation:")
        print(result)

    def test_openrouter_complex_translation(self):
        """Test dịch văn bản phức tạp với OpenRouter."""
        result = self.openrouter.translate_text(self.complex_text)
        self.assertIsNotNone(result)
        self.assertTrue(self.openrouter._validate_translation(self.complex_text, result))
        print("\nOpenRouter complex translation:")
        print(result)

    def test_validate_translation_structure(self):
        """Test validate cấu trúc bản dịch."""
        # Test với text không hợp lệ
        invalid_text = "This is not a valid block structure"
        valid_text = """---BLOCK 1---
This is a valid block.
---END BLOCK 1---"""
        
        # Test Groq validation
        self.assertFalse(self.groq._validate_translation(valid_text, invalid_text))
        self.assertTrue(self.groq._validate_translation(valid_text, valid_text))
        
        # Test OpenRouter validation
        self.assertFalse(self.openrouter._validate_translation(valid_text, invalid_text))
        self.assertTrue(self.openrouter._validate_translation(valid_text, valid_text))

    def test_providers_available(self):
        """Test tính khả dụng của các provider."""
        self.assertTrue(self.groq.is_available())
        self.assertTrue(self.openrouter.is_available())

    def test_provider_priorities(self):
        """Test độ ưu tiên của các provider."""
        self.assertEqual(self.groq.get_priority(), 1)  # Groq có priority cao nhất
        self.assertEqual(self.openrouter.get_priority(), 2)  # OpenRouter là fallback

    def test_validation_error(self):
        """Test xử lý lỗi validation đầu vào."""
        from api.exceptions import TranslationError # Sửa exception mong đợi
        invalid_text = "This is not a valid block structure"
        
        # Test Groq
        with self.assertRaises(TranslationError): # Sửa exception mong đợi
            self.groq.translate_text(invalid_text)
            
        # Test OpenRouter
        with self.assertRaises(TranslationError): # Sửa exception mong đợi
            self.openrouter.translate_text(invalid_text)

if __name__ == '__main__':
    unittest.main(verbosity=2)
