import os
import time
import logging
from typing import Optional, List
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
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class APIHandler:
    def __init__(self):
        # Load API keys từ biến môi trường
        self.novita_keys = [
            os.getenv('NOVITA_API_KEY')
        ]
        self.google_key = os.getenv('GOOGLE_AI_STUDIO_KEY_1')
        self.mistral_key = os.getenv('MISTRAL_API_KEY')
        self.groq_key = os.getenv('GROQ_API_KEY')
        self.openrouter_keys = [
            os.getenv('OPENROUTER_API_KEY_1'),
            os.getenv('OPENROUTER_API_KEY_2'),
            os.getenv('OPENROUTER_API_KEY_3')
        ]
        self.cerebras_key = os.getenv('CEREBRAS_API_KEY')
        
        # Rate limiting
        self.rate_limits = {
            'novita': {'calls': 0, 'last_reset': time.time(), 'limit': 100, 'window': 3600},
            'google': {'calls': 0, 'last_reset': time.time(), 'limit': 1000, 'window': 3600},
            'mistral': {'calls': 0, 'last_reset': time.time(), 'limit': 100, 'window': 3600},
            'groq': {'calls': 0, 'last_reset': time.time(), 'limit': 100, 'window': 3600},
            'openrouter': {'calls': 0, 'last_reset': time.time(), 'limit': 100, 'window': 3600},
            'cerebras': {'calls': 0, 'last_reset': time.time(), 'limit': 100, 'window': 3600}
        }
        
        # Current key indices
        self.current_keys = {
            'novita': 0,
            'google': 0,
            'openrouter': 0
        }
        
        # Thứ tự ưu tiên các providers
        self.provider_priority = ['novita', 'google', 'mistral', 'groq', 'openrouter', 'cerebras']

    def _check_rate_limit(self, service: str) -> bool:
        """Kiểm tra rate limit cho một service."""
        now = time.time()
        limit_info = self.rate_limits[service]
        
        # Reset counter nếu đã qua window
        if now - limit_info['last_reset'] > limit_info['window']:
            limit_info['calls'] = 0
            limit_info['last_reset'] = now
            
        # Kiểm tra limit
        if limit_info['calls'] >= limit_info['limit']:
            return False
            
        limit_info['calls'] += 1
        return True

    def _get_api_key(self, service: str) -> Optional[str]:
        """Lấy API key cho service, với rotation nếu có nhiều key."""
        if service == 'novita':
            key = self.novita_keys[self.current_keys['novita']]
            self.current_keys['novita'] = (self.current_keys['novita'] + 1) % len(self.novita_keys)
            return key
        elif service == 'google':
            return self.google_key
        elif service == 'openrouter':
            key = self.openrouter_keys[self.current_keys['openrouter']]
            self.current_keys['openrouter'] = (self.current_keys['openrouter'] + 1) % len(self.openrouter_keys)
            return key
        elif service == 'mistral':
            return self.mistral_key
        elif service == 'groq':
            return self.groq_key
        elif service == 'cerebras':
            return self.cerebras_key
        return None

    def _get_provider(self, service: str) -> Optional[object]:
        """Tạo provider instance cho service."""
        api_key = self._get_api_key(service)
        if not api_key:
            return None
            
        if service == 'novita':
            return NovitaProvider(api_key)
        elif service == 'google':
            return GoogleProvider(api_key)
        elif service == 'mistral':
            return MistralProvider(api_key)
        elif service == 'groq':
            return GroqProvider(api_key)
        elif service == 'openrouter':
            return OpenRouterProvider(api_key)
        elif service == 'cerebras':
            return CerebrasProvider(api_key)
        return None

    @backoff.on_exception(backoff.expo, 
                         Exception,
                         max_tries=3)
    def translate_text(self, text: str, target_lang: str = 'vi', service: str = 'novita') -> Optional[str]:
        """Dịch văn bản sử dụng service được chọn với cơ chế retry và fallback."""
        # Thử với provider được chọn trước
        if self._check_rate_limit(service):
            provider = self._get_provider(service)
            if provider:
                try:
                    return provider.translate(text, target_lang)
                except Exception as e:
                    logger.error(f"Error with {service}: {str(e)}")
            
        # Nếu thất bại, thử với các providers khác theo thứ tự ưu tiên
        for provider_name in self.provider_priority:
            if provider_name != service and self._check_rate_limit(provider_name):
                logger.info(f"Thử lại với provider {provider_name}")
                provider = self._get_provider(provider_name)
                if provider:
                    try:
                        return provider.translate(text, target_lang)
                    except Exception as e:
                        logger.error(f"Error with {provider_name}: {str(e)}")
                        
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