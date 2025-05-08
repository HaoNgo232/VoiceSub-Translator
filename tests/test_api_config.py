import os
import pytest
from src.api.handler import APIHandler

@pytest.fixture
def mock_env_vars(monkeypatch):
    """Thiết lập các biến môi trường giả lập cho testing"""
    env_vars = {
        'NOVITA_API_KEY': 'test_novita_key',
        'GOOGLE_API_KEY': 'test_google_key',
        'MISTRAL_API_KEY': 'test_mistral_key',
        'GROQ_API_KEY': 'test_groq_key',
        'OPENROUTER_API_KEY': 'test_openrouter_key',
        'CEREBRAS_API_KEY': 'test_cerebras_key',
        'PROVIDER_PRIORITY': 'novita,google,mistral,groq,openrouter,cerebras',
        'DEFAULT_TARGET_LANG': 'vi',
        'TRANSLATION_CHUNK_SIZE': '1000',
        'TRANSLATION_MAX_LENGTH': '4000',
        'RATE_LIMIT_REQUESTS_PER_HOUR': '1000',
        'RATE_LIMIT_WINDOW': '3600',
        'LOG_LEVEL': 'INFO',
        'LOG_FORMAT': '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        'LOG_DIR': 'logs',
        'MAX_LOG_FILES': '10',
        'CACHE_DIR': 'cache',
        'CACHE_EXPIRY_DAYS': '7',
        'MAX_WORKERS': '4',
        'MEMORY_THRESHOLD': '0.8',
        'MEMORY_CHECK_INTERVAL': '5'
    }
    for key, value in env_vars.items():
        monkeypatch.setenv(key, value)

def test_api_handler_initialization(mock_env_vars):
    """Test khởi tạo APIHandler với các biến môi trường"""
    handler = APIHandler()
    
    # Kiểm tra API keys
    assert handler.novita_key == 'test_novita_key'
    assert handler.google_key == 'test_google_key'
    assert handler.mistral_key == 'test_mistral_key'
    assert handler.groq_key == 'test_groq_key'
    assert handler.openrouter_key == 'test_openrouter_key'
    assert handler.cerebras_key == 'test_cerebras_key'
    
    # Kiểm tra cấu hình providers
    assert handler.provider_priority == ['novita', 'google', 'mistral', 'groq', 'openrouter', 'cerebras']
    
    # Kiểm tra cấu hình translation
    assert handler.default_target_lang == 'vi'
    assert handler.translation_chunk_size == 1000
    assert handler.translation_max_length == 4000

def test_provider_initialization(mock_env_vars):
    """Test khởi tạo các providers"""
    handler = APIHandler()
    
    # Kiểm tra tất cả các providers đã được khởi tạo
    assert handler.providers['novita'] is not None
    assert handler.providers['google'] is not None
    assert handler.providers['mistral'] is not None
    assert handler.providers['groq'] is not None
    assert handler.providers['openrouter'] is not None
    assert handler.providers['cerebras'] is not None
    
    # Kiểm tra loại của các providers
    assert handler.providers['novita'].__class__.__name__ == 'NovitaProvider'
    assert handler.providers['google'].__class__.__name__ == 'GoogleProvider'
    assert handler.providers['mistral'].__class__.__name__ == 'MistralProvider'
    assert handler.providers['groq'].__class__.__name__ == 'GroqProvider'
    assert handler.providers['openrouter'].__class__.__name__ == 'OpenRouterProvider'
    assert handler.providers['cerebras'].__class__.__name__ == 'CerebrasProvider'

def test_get_provider(mock_env_vars):
    """Test lấy provider theo tên hoặc provider đầu tiên khả dụng"""
    handler = APIHandler()
    
    # Test lấy provider theo tên
    provider = handler.get_provider('novita')
    assert provider is not None
    assert provider.__class__.__name__ == 'NovitaProvider'
    
    # Test lấy provider đầu tiên khả dụng
    provider = handler.get_provider()
    assert provider is not None
    assert provider.__class__.__name__ == 'NovitaProvider'  # Novita là provider đầu tiên trong danh sách ưu tiên

def test_provider_priority(mock_env_vars, monkeypatch):
    """Test thứ tự ưu tiên của các providers"""
    # Xóa Novita API key để kiểm tra fallback
    monkeypatch.delenv('NOVITA_API_KEY')
    
    handler = APIHandler()
    
    # Kiểm tra provider đầu tiên khả dụng là Google (vì Novita không có API key)
    provider = handler.get_provider()
    assert provider is not None
    assert provider.__class__.__name__ == 'GoogleProvider'

def test_translation_with_chunks(mock_env_vars):
    """Test dịch văn bản dài được chia thành các chunks"""
    handler = APIHandler()
    
    # Tạo văn bản dài hơn translation_chunk_size
    long_text = "Hello world! " * 200  # 2400 ký tự
    
    # Dịch văn bản
    translated_text = handler.translate(long_text)
    
    # Kiểm tra kết quả
    assert translated_text is not None  # Đảm bảo có kết quả trả về
    assert len(translated_text) > 0  # Đảm bảo kết quả không rỗng 