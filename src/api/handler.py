import os
import time
import logging
from typing import Optional, List, Dict
import backoff
from dotenv import load_dotenv

from .providers import (
    NovitaProvider,
    GoogleProvider,
    MistralProvider,
    GroqProvider,
    OpenRouterProvider,
    CerebrasProvider
)

# Load biến môi trường
load_dotenv()

# Cấu hình logging
logging.basicConfig(
    level=getattr(logging, os.getenv('LOG_LEVEL', 'INFO')),
    format=os.getenv('LOG_FORMAT', '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
)
logger = logging.getLogger(__name__)

class APIHandler:
    def __init__(self):
        # Load API keys từ biến môi trường
        self.novita_key = os.getenv('NOVITA_API_KEY')
        self.google_key = os.getenv('GOOGLE_API_KEY')
        self.mistral_key = os.getenv('MISTRAL_API_KEY')
        self.groq_key = os.getenv('GROQ_API_KEY')
        self.openrouter_key = os.getenv('OPENROUTER_API_KEY')
        self.cerebras_key = os.getenv('CEREBRAS_API_KEY')
        
        # Rate limiting configuration
        self.rate_limits = {
            'novita': {
                'calls': 0,
                'last_reset': time.time(),
                'limit': int(os.getenv('RATE_LIMIT_REQUESTS_PER_HOUR', '1000')),
                'window': int(os.getenv('RATE_LIMIT_WINDOW', '3600'))
            },
            'google': {
                'calls': 0,
                'last_reset': time.time(),
                'limit': int(os.getenv('RATE_LIMIT_REQUESTS_PER_HOUR', '1000')),
                'window': int(os.getenv('RATE_LIMIT_WINDOW', '3600'))
            },
            'mistral': {
                'calls': 0,
                'last_reset': time.time(),
                'limit': int(os.getenv('RATE_LIMIT_REQUESTS_PER_HOUR', '1000')),
                'window': int(os.getenv('RATE_LIMIT_WINDOW', '3600'))
            },
            'groq': {
                'calls': 0,
                'last_reset': time.time(),
                'limit': int(os.getenv('RATE_LIMIT_REQUESTS_PER_HOUR', '1000')),
                'window': int(os.getenv('RATE_LIMIT_WINDOW', '3600'))
            },
            'openrouter': {
                'calls': 0,
                'last_reset': time.time(),
                'limit': int(os.getenv('RATE_LIMIT_REQUESTS_PER_HOUR', '1000')),
                'window': int(os.getenv('RATE_LIMIT_WINDOW', '3600'))
            },
            'cerebras': {
                'calls': 0,
                'last_reset': time.time(),
                'limit': int(os.getenv('RATE_LIMIT_REQUESTS_PER_HOUR', '1000')),
                'window': int(os.getenv('RATE_LIMIT_WINDOW', '3600'))
            }
        }
        
        # Provider configuration
        self.provider_priority = os.getenv('PROVIDER_PRIORITY', 'novita,google,mistral,groq,openrouter,cerebras').split(',')
        
        # Translation configuration
        self.default_target_lang = os.getenv('DEFAULT_TARGET_LANG', 'vi')
        self.translation_chunk_size = int(os.getenv('TRANSLATION_CHUNK_SIZE', '1000'))
        self.translation_max_length = int(os.getenv('TRANSLATION_MAX_LENGTH', '4000'))
        
        # Khởi tạo các providers
        self.providers = {
            'novita': NovitaProvider(self.novita_key) if self.novita_key else None,
            'google': GoogleProvider(self.google_key) if self.google_key else None,
            'mistral': MistralProvider(self.mistral_key) if self.mistral_key else None,
            'groq': GroqProvider(self.groq_key) if self.groq_key else None,
            'openrouter': OpenRouterProvider(self.openrouter_key) if self.openrouter_key else None,
            'cerebras': CerebrasProvider(self.cerebras_key) if self.cerebras_key else None
        }
        
        # Log các providers đã được khởi tạo
        active_providers = [name for name, provider in self.providers.items() if provider is not None]
        logger.info(f"Đã khởi tạo các providers: {', '.join(active_providers)}")
        
    def get_provider(self, provider_name: Optional[str] = None) -> Optional[object]:
        """Lấy provider theo tên hoặc provider đầu tiên khả dụng"""
        if provider_name:
            return self.providers.get(provider_name)
            
        # Tìm provider đầu tiên khả dụng theo thứ tự ưu tiên
        for name in self.provider_priority:
            provider = self.providers.get(name)
            if provider is not None:
                return provider
                
        return None
        
    @backoff.on_exception(
        backoff.expo,
        Exception,
        max_tries=3,
        max_time=30
    )
    def translate(self, text: str, target_lang: str = None, provider_name: Optional[str] = None) -> Optional[str]:
        """Dịch văn bản sử dụng provider được chỉ định hoặc provider đầu tiên khả dụng"""
        provider = self.get_provider(provider_name)
        if not provider:
            logger.error("Không tìm thấy provider khả dụng")
            return None
            
        target_lang = target_lang or self.default_target_lang
        
        # Chia văn bản thành các chunks nếu cần
        if len(text) > self.translation_chunk_size:
            chunks = [text[i:i + self.translation_chunk_size] for i in range(0, len(text), self.translation_chunk_size)]
            translated_chunks = []
            
            for chunk in chunks:
                try:
                    translated_chunk = provider.translate(chunk, target_lang)
                    if translated_chunk:
                        translated_chunks.append(translated_chunk)
                    else:
                        logger.error(f"Không thể dịch chunk: {chunk[:100]}...")
                        return None
                except Exception as e:
                    logger.error(f"Lỗi khi dịch chunk: {str(e)}")
                    return None
                    
            return " ".join(translated_chunks)
        else:
            try:
                return provider.translate(text, target_lang)
            except Exception as e:
                logger.error(f"Lỗi khi dịch văn bản: {str(e)}")
                return None

    def test_connection(self) -> bool:
        """Test kết nối đến API."""
        try:
            # Đợi để tuân thủ rate limit
            self._wait_for_rate_limit()
            
            # Gọi API với prompt đơn giản
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "user", "content": "Hello"}
                ],
                max_tokens=10
            )
            
            return True
            
        except Exception as e:
            logging.error(f"Lỗi khi test kết nối: {str(e)}")
            return False 