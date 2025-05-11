import os
import time
import logging
import backoff
from typing import Optional, List, Dict
from dotenv import load_dotenv

from .providers import (
    NovitaProvider,
    GoogleProvider,
    MistralProvider,
    GroqProvider,
    OpenRouterProvider,
    CerebrasProvider
)
from .error_handler import RateLimitHandler, APIErrorHandler
from .translation_service import TranslationService

# Load biến môi trường
load_dotenv()

# Cấu hình logging
logging.basicConfig(
    level=getattr(logging, os.getenv('LOG_LEVEL', 'INFO')),
    format=os.getenv('LOG_FORMAT', '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
)
logger = logging.getLogger(__name__)

class APIHandler:
    """Lớp xử lý các cuộc gọi API đến các provider"""
    
    def __init__(self):
        # Load API keys từ biến môi trường
        self.novita_key = os.getenv('NOVITA_API_KEY')
        self.google_key = os.getenv('GOOGLE_API_KEY')
        self.mistral_key = os.getenv('MISTRAL_API_KEY')
        self.groq_key = os.getenv('GROQ_API_KEY')
        self.openrouter_key = os.getenv('OPENROUTER_API_KEY')
        self.cerebras_key = os.getenv('CEREBRAS_API_KEY')
        
        # Cấu hình provider
        self.provider_priority = os.getenv('PROVIDER_PRIORITY', 'novita,google,mistral,groq,openrouter,cerebras').split(',')
        
        # Khởi tạo Rate Limit Handler
        self.rate_limit_handler = RateLimitHandler()
        
        # Khởi tạo API Error Handler
        self.error_handler = APIErrorHandler()
        
        # Khởi tạo các providers
        self.providers = {
            'novita': NovitaProvider(self.novita_key) if self.novita_key else None,
            'google': GoogleProvider(self.google_key) if self.google_key else None,
            'mistral': MistralProvider(self.mistral_key) if self.mistral_key else None,
            'groq': GroqProvider(self.groq_key) if self.groq_key else None,
            'openrouter': OpenRouterProvider(self.openrouter_key) if self.openrouter_key else None,
            'cerebras': CerebrasProvider(self.cerebras_key) if self.cerebras_key else None
        }
        
        # Khởi tạo TranslationService
        self.translation_service = TranslationService(
            providers=self.providers,
            rate_limit_handler=self.rate_limit_handler,
            provider_priorities=self.provider_priority
        )
        
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
        """Dịch văn bản sử dụng provider được chỉ định, hoặc thử lần lượt các provider nếu bị lỗi."""
        # Sử dụng TranslationService đã tách riêng
        return self.translation_service.translate(text, target_lang, provider_name)

    def translate_text(self, text, target_lang='vi', provider_name=None):
        """
        Dịch văn bản sử dụng provider được chỉ định hoặc provider đầu tiên khả dụng.
        Wrapper cho hàm translate để tương thích với các module khác.
        """
        return self.translate(text, target_lang, provider_name) 