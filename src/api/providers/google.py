from google import genai
from .base import BaseProvider, logger

class GoogleProvider(BaseProvider):
    def __init__(self, api_key: str):
        super().__init__(api_key)
        self.client = genai.Client(api_key=api_key)
        
    def translate(self, text: str, target_lang: str) -> str:
        """Dịch văn bản sử dụng Gemini API."""
        try:
            prompt = f"{self.get_system_prompt(target_lang)}\n\nText to translate:\n{text}"
            response = self.client.models.generate_content(
                model="gemini-2.0-flash",
                contents=prompt
            )
            return response.text.strip()
        except Exception as e:
            logger.error(f"Error translating with Gemini: {str(e)}")
            raise 