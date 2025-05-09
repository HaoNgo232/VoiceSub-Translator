import os
import time
import logging
from typing import Optional, List, Dict
import backoff
from dotenv import load_dotenv
import threading

from .providers import (
    NovitaProvider,
    GoogleProvider,
    MistralProvider,
    GroqProvider,
    OpenRouterProvider,
    CerebrasProvider
)
from .error_handler import RateLimitHandler

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
        
        # Khởi tạo RateLimitHandler
        self.rate_limit_handler = RateLimitHandler()
        
        # Ghi nhớ các provider thất bại liên tục để tạm thời bỏ qua
        self.provider_failures = {name: 0 for name in self.provider_priority}
        self.failure_threshold = 5  # Sau 5 lần thất bại liên tục
        self.disabled_providers = {}  # {provider: thời_gian_hết_timeout}
        
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
        
    def get_rate_limit(self, provider, paid=False):
        # Novita: chỉ rate limit nếu trả phí
        if provider == "novita":
            return 0.3 if paid else 0
        # OpenRouter free: 3s/lần, trả phí: 0.9s/lần
        elif provider == "openrouter":
            return 3 if not paid else 0.9
        # Groq free: 2s/lần, trả phí: 0.9s/lần
        elif provider == "groq":
            return 2 if not paid else 0.9
        # Gemini free: 6s/lần, trả phí: 0.9s/lần
        elif provider == "google":
            return 6 if not paid else 0.9
        # Cerebras: mặc định 1s/lần
        elif provider == "cerebras":
            return 1
        # Mistral: mặc định 1s/lần
        elif provider == "mistral":
            return 1
        else:
            return 0.9

    # Biến lưu thời điểm gọi cuối cùng cho từng provider
    _last_call_time = {}
    _lock = threading.Lock()

    def rate_limited(self, provider, paid=False):
        def decorator(func):
            def wrapper(*args, **kwargs):
                interval = self.get_rate_limit(provider, paid)
                if interval > 0:
                    with self._lock:
                        last = self._last_call_time.get(provider, 0)
                        now = time.time()
                        wait = interval - (now - last)
                        if wait > 0:
                            time.sleep(wait)
                        self._last_call_time[provider] = time.time()
                return func(*args, **kwargs)
            return wrapper
        return decorator

    @backoff.on_exception(
        backoff.expo,
        Exception,
        max_tries=3,
        max_time=30
    )
    def translate(self, text: str, target_lang: str = None, provider_name: Optional[str] = None) -> Optional[str]:
        """Dịch văn bản sử dụng provider được chỉ định, hoặc thử lần lượt các provider nếu bị lỗi."""
        target_lang = target_lang or self.default_target_lang
        provider_list = self._get_provider_list(provider_name)
        
        if not provider_list:
            logger.error("Không tìm thấy provider khả dụng")
            return None
        
        return self._try_translate_with_providers(text, target_lang, provider_list)

    def _get_provider_list(self, provider_name: Optional[str] = None) -> List[str]:
        """Xác định danh sách providers để thử dịch."""
        tried_providers = set()
        provider_list = []
        
        # Lọc ra các provider tạm thời bị vô hiệu hóa do lỗi liên tục
        current_time = time.time()
        for provider, disable_until in list(self.disabled_providers.items()):
            if current_time > disable_until:
                logger.info(f"Re-enabling provider {provider} after timeout")
                del self.disabled_providers[provider]
        
        # Nếu chỉ định provider, thử provider đó trước
        if provider_name:
            # Nếu provider không bị disable
            if provider_name not in self.disabled_providers:
                provider_list.append(provider_name)
                tried_providers.add(provider_name)
        
        # Sau đó thử các provider còn lại theo thứ tự ưu tiên
        for name in self.provider_priority:
            if name not in tried_providers and self.providers.get(name) is not None:
                # Nếu provider không bị disable
                if name not in self.disabled_providers:
                    provider_list.append(name)
            
        return provider_list

    def _translate_text_in_chunks(self, text: str, target_lang: str, do_translate) -> Optional[str]:
        """Chia văn bản thành các phần nhỏ để dịch nếu cần."""
        chunks = [text[i:i + self.translation_chunk_size] for i in range(0, len(text), self.translation_chunk_size)]
        translated_chunks = []
        
        for chunk in chunks:
            translated_chunk = do_translate(chunk, target_lang)
            if not translated_chunk:
                return None
            translated_chunks.append(translated_chunk)
            
        return " ".join(translated_chunks)

    def _try_translate_with_providers(self, text: str, target_lang: str, provider_list: List[str]) -> Optional[str]:
        """Thử dịch văn bản với danh sách các providers cho trước."""
        error_info = {}
        
        for provider_key in provider_list:
            provider = self.providers.get(provider_key)
            if not provider:
                logger.error(f"Provider {provider_key} không tồn tại, bỏ qua")
                continue
            
            # Kiểm tra rate limit tổng thể (nếu áp dụng) trước khi thử gọi API
            if not self.rate_limit_handler.check_rate_limit(provider_key):
                logger.warning(f"Bỏ qua provider {provider_key} do đạt giới hạn tổng thể RPM")
                error_info[provider_key] = "Đạt giới hạn RPM tổng thể"
                continue
            
            # Xác định loại tài khoản (free/paid)
            is_paid = provider_key == "novita"  # Giả sử Novita luôn trả phí, có thể mở rộng
            
            # Bọc hàm dịch với rate limit
            @self.rate_limited(provider_key, is_paid)
            def do_translate(text, target_lang):
                return provider.translate(text, target_lang)
            
            try:
                # Dịch toàn bộ văn bản hoặc theo từng chunk
                if len(text) > self.translation_chunk_size:
                    result = self._translate_text_in_chunks(text, target_lang, do_translate)
                else:
                    result = do_translate(text, target_lang)
                
                if result:
                    logger.info(f"Đã dịch thành công với provider: {provider_key}")
                    # Reset số lần thất bại vì đã thành công
                    self.provider_failures[provider_key] = 0
                    return result
                else:
                    logger.warning(f"Provider {provider_key} trả về kết quả rỗng. Thử provider tiếp theo...")
                    error_info[provider_key] = "Kết quả dịch rỗng"
                    self.provider_failures[provider_key] += 1
            except Exception as e:
                logger.warning(f"Lỗi khi dịch với provider {provider_key}: {str(e)}. Thử provider tiếp theo...")
                error_info[provider_key] = str(e)
                
                # Tăng số lần thất bại
                self.provider_failures[provider_key] += 1
                
                # Nếu provider thất bại quá nhiều lần liên tiếp, tạm thời vô hiệu hóa
                if self.provider_failures[provider_key] >= self.failure_threshold:
                    # Vô hiệu hóa provider trong 5 phút
                    self.disabled_providers[provider_key] = time.time() + 180
                    logger.warning(f"Tạm thời vô hiệu hóa provider {provider_key} trong 3 phút do lỗi liên tục")
        
        # Nếu tất cả providers đều thất bại
        logger.error(f"Tất cả providers đều thất bại. Chi tiết lỗi: {error_info}")
        return None

    def test_connection(self) -> bool:
        """Test kết nối đến API."""
        try:
            # Đợi để tuân thủ rate limit
            self._wait_for_rate_limit()
            
            # Gọi API với prompt đơn giản
            self.client.chat.completions.create(
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

    def translate_text(self, text, target_lang='vi', provider_name=None):
        """
        Dịch văn bản sử dụng provider được chỉ định hoặc provider đầu tiên khả dụng.
        Wrapper cho hàm translate để tương thích với các module khác.
        """
        return self.translate(text, target_lang, provider_name) 