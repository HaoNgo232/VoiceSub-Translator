import requests
from .base import BaseProvider, logger

class OpenRouterProvider(BaseProvider):
    def translate(self, text: str, target_lang: str) -> str:
        """Dịch văn bản sử dụng OpenRouter API."""
        url = "https://openrouter.ai/api/v1/chat/completions"
        headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json'
        }
        data = {
            'model': 'anthropic/claude-3-opus',
            'messages': [
                {'role': 'system', 'content': self.get_system_prompt(target_lang)},
                {'role': 'user', 'content': text}
            ]
        }
        try:
            response = requests.post(url, headers=headers, json=data, timeout=30)
            response.raise_for_status()
            return response.json()['choices'][0]['message']['content']
        except requests.exceptions.Timeout:
            logger.error("OpenRouter API timeout")
            raise
        except requests.exceptions.RequestException as e:
            logger.error(f"OpenRouter API error: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error with OpenRouter API: {str(e)}")
            raise 