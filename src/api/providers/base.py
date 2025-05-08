from abc import ABC, abstractmethod
import logging

logger = logging.getLogger(__name__)

class BaseProvider(ABC):
    def __init__(self, api_key: str):
        self.api_key = api_key
        
    @abstractmethod
    def translate(self, text: str, target_lang: str) -> str:
        """Dịch văn bản sang ngôn ngữ đích"""
        pass
        
    def get_system_prompt(self, target_lang: str) -> str:
        """Lấy prompt hệ thống cho việc dịch"""
        return f"""Translate the following text to {target_lang}. 
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
10. Keep all numbers and timestamps exactly as they are
11. Keep all special characters and formatting exactly as they are
12. Keep all line breaks and spacing exactly as they are""" 