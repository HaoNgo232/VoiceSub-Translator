import os
import time
import logging
from typing import Optional, List
import groq
from dotenv import load_dotenv
import requests
from google import genai

# Load biến môi trường
load_dotenv()

# Cấu hình logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class APIHandler:
    def __init__(self):
        # Load API keys từ biến môi trường
        self.novita_keys = [
            os.getenv('NOVITA_API_KEY_1'),
            os.getenv('NOVITA_API_KEY_2')
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
        
        # Khởi tạo Gemini client
        if self.google_key:
            self.gemini_client = genai.Client(api_key=self.google_key)

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

    def translate_text(self, text: str, target_lang: str = 'vi', service: str = 'google') -> Optional[str]:
        """Dịch văn bản sử dụng service được chọn."""
        if not self._check_rate_limit(service):
            logger.warning(f"Rate limit exceeded for {service}")
            return None
            
        api_key = self._get_api_key(service)
        if not api_key:
            logger.error(f"No API key available for {service}")
            return None
            
        try:
            if service == 'google':
                return self._translate_google(text, target_lang)
            elif service == 'novita':
                return self._translate_novita(text, target_lang, api_key)
            elif service == 'mistral':
                return self._translate_mistral(text, target_lang, api_key)
            elif service == 'groq':
                return self._translate_groq(text, target_lang, api_key)
            elif service == 'openrouter':
                return self._translate_openrouter(text, target_lang, api_key)
            elif service == 'cerebras':
                return self._translate_cerebras(text, target_lang, api_key)
            else:
                logger.error(f"Unsupported translation service: {service}")
                return None
        except Exception as e:
            logger.error(f"Translation error with {service}: {str(e)}")
            return None

    def _translate_google(self, text: str, target_lang: str) -> str:
        """Dịch văn bản sử dụng Gemini API."""
        try:
            prompt = f"""Translate the following text to {target_lang}. 
IMPORTANT INSTRUCTIONS:
1. Only return the translated text, without any explanations or notes
2. Keep the original format and timing information
3. Keep technical terms and IT concepts in English (e.g. API, CPU, RAM, etc.)
4. Keep certification names in English (e.g. CISP, CISM, etc.)
5. Keep company names in English
6. Keep product names in English
7. Keep programming languages and frameworks in English
8. Keep file extensions in English
9. Keep commands and code snippets in English

Text to translate:
{text}"""
            response = self.gemini_client.models.generate_content(
                model="gemini-2.0-flash",
                contents=prompt
            )
            return response.text.strip()
        except Exception as e:
            logger.error(f"Error translating with Gemini: {str(e)}")
            return None

    def _translate_novita(self, text: str, target_lang: str, api_key: str) -> str:
        """Dịch văn bản sử dụng Novita API."""
        url = "https://api.novita.ai/v1/translate"
        headers = {
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json'
        }
        data = {
            'text': text,
            'target_language': target_lang
        }
        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status()
        return response.json()['translated_text']

    def _translate_mistral(self, text: str, target_lang: str, api_key: str) -> str:
        """Dịch văn bản sử dụng Mistral AI API."""
        url = "https://api.mistral.ai/v1/chat/completions"
        headers = {
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json'
        }
        data = {
            'model': 'mistral-large-latest',
            'messages': [
                {'role': 'system', 'content': f'Translate the following text to {target_lang}:'},
                {'role': 'user', 'content': text}
            ]
        }
        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status()
        return response.json()['choices'][0]['message']['content']

    def _translate_groq(self, text: str, target_lang: str, api_key: str) -> str:
        """Dịch văn bản sử dụng Groq API."""
        url = "https://api.groq.com/v1/chat/completions"
        headers = {
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json'
        }
        data = {
            'model': 'mixtral-8x7b-32768',
            'messages': [
                {'role': 'system', 'content': f'Translate the following text to {target_lang}:'},
                {'role': 'user', 'content': text}
            ]
        }
        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status()
        return response.json()['choices'][0]['message']['content']

    def _translate_openrouter(self, text: str, target_lang: str, api_key: str) -> str:
        """Dịch văn bản sử dụng OpenRouter API."""
        url = "https://openrouter.ai/api/v1/chat/completions"
        headers = {
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json'
        }
        data = {
            'model': 'anthropic/claude-3-opus',
            'messages': [
                {'role': 'system', 'content': f'Translate the following text to {target_lang}:'},
                {'role': 'user', 'content': text}
            ]
        }
        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status()
        return response.json()['choices'][0]['message']['content']

    def _translate_cerebras(self, text: str, target_lang: str, api_key: str) -> str:
        """Dịch văn bản sử dụng Cerebras API."""
        url = "https://api.cerebras.ai/v1/chat/completions"
        headers = {
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json'
        }
        data = {
            'model': 'cerebras-1',
            'messages': [
                {'role': 'system', 'content': f'Translate the following text to {target_lang}:'},
                {'role': 'user', 'content': text}
            ]
        }
        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status()
        return response.json()['choices'][0]['message']['content']

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