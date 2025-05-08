import requests
from .base import BaseProvider, logger

class CerebrasProvider(BaseProvider):
    def translate(self, text: str, target_lang: str) -> str:
        """Dịch văn bản sử dụng Cerebras API."""
        url = "https://api.cerebras.ai/v1/chat/completions"
        headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json'
        }
        data = {
            'model': 'cerebras-1',
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
            logger.error("Cerebras API timeout")
            raise
        except requests.exceptions.RequestException as e:
            logger.error(f"Cerebras API error: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error with Cerebras API: {str(e)}")
            raise 