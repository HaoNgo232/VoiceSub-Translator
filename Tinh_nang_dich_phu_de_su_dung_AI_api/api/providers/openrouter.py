import os
import time
import json
import logging
from datetime import datetime, timezone, timedelta
from typing import Optional, Dict, Any
import requests
from threading import Lock

from ..base import BaseAPIHandler
from ..exceptions import (
    AuthenticationError,
    ConfigurationError, 
    ConnectionError,
    RateLimitError,
    TranslationError,
    ValidationError,
    NoAvailableModelsError
)
from ..config import ProviderConfig
from ..utils.rate_limit import RateLimitManager

class OpenrouterAPIHandler(BaseAPIHandler):
    """Handler for OpenRouter API with free models."""
    
    MODELS = [
        "google/gemma-3-12b-it:free",
        "google/gemma-2-9b-it:free",
        "qwen/qwen2.5-vl-32b-instruct:free",
        "featherless/qwerky-72b:free",
        "google/gemma-3-27b-it:free",
        "cognitivecomputations/dolphin3.0-r1-mistral-24b:free",
        "qwen/qwen2.5-vl-72b-instruct:free",
        "qwen/qwq-32b-preview:free", 
        "mistralai/mistral-7b-instruct:free"
    ]
    
    BASE_URL = "https://openrouter.ai/api/v1"
    
    def __init__(self, config: ProviderConfig):
        """Initialize OpenRouter API handler."""
        super().__init__(
            max_retries=config.max_retries,
            timeout=config.timeout
        )
        self.config = config
        self.rate_limiter = RateLimitManager()
        self._initialize_api()
        
    def _initialize_api(self):
        """Initialize API configuration."""
        try:
            self.api_key = os.getenv('OPENROUTER_API_KEY')
            if not self.api_key:
                raise ConfigurationError("OPENROUTER_API_KEY not configured")
                
            # Khởi tạo rate limits cho tất cả models
            for model in self.MODELS:
                self.rate_limiter.initialize_model("openrouter", model)
                
            # Test connection with smallest model
            self._test_connection()
            
        except Exception as e:
            raise ConfigurationError(f"Failed to initialize OpenRouter API: {str(e)}")
            
    def _test_connection(self):
        """Test API connection with minimal request."""
        try:
            test_model = self.MODELS[-1]  # Use smallest model for test
            self._call_api(
                model=test_model,
                messages=[{"role": "user", "content": "test"}],
                max_tokens=1
            )
            logging.info("Successfully connected to OpenRouter API")
        except Exception as e:
            raise ConnectionError(f"Failed to connect to OpenRouter API: {str(e)}")

    def _call_api(self, 
                  model: str, 
                  messages: list,
                  temperature: float = 0.7,
                  max_tokens: Optional[int] = None) -> Dict:
        """Make request to OpenRouter API."""
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": os.getenv('SITE_URL', 'http://localhost'),  # Required by OpenRouter
            "X-Title": os.getenv('SITE_NAME', 'Local Development')  # Required by OpenRouter
        }

        data = {
            "model": model,
            "messages": messages,
            "temperature": temperature
        }
        if max_tokens:
            data["max_tokens"] = max_tokens

        try:
            response = requests.post(
                f"{self.BASE_URL}/chat/completions",
                headers=headers,
                json=data,
                timeout=self.timeout
            )
            
            response.raise_for_status()
            return response.json()
            
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 429:
                raise RateLimitError(
                    retry_after=int(e.response.headers.get('retry-after', 60))
                )
            elif e.response.status_code in [401, 403]:
                raise AuthenticationError("Invalid API credentials")
            else:
                raise TranslationError(
                    "openrouter",
                    f"HTTP error {e.response.status_code}"
                )
                
        except requests.exceptions.Timeout:
            raise TranslationError("openrouter", "Request timeout")
            
        except requests.exceptions.RequestException as e:
            raise ConnectionError(f"Request failed: {str(e)}")
            
        except Exception as e:
            raise TranslationError("openrouter", str(e))

    def translate_text(self, text: str, target_language: str = "Vietnamese") -> Optional[str]:
        """Translate text using available models."""
        # Get available model from rate limiter
        model = self.rate_limiter.get_available_model("openrouter", self.MODELS)
        if not model:
            raise NoAvailableModelsError("No models available within rate limits")

        try:
            # Prepare messages
            system_prompt = f"""Translate the following English text to {target_language}.
IMPORTANT: 
1. Maintain the exact structure of the input text
2. Keep all block markers (---BLOCK X--- and ---END BLOCK X---)
3. Only translate the content between block markers
4. Return the complete structure with translations
5. Do not add any additional text or explanations
"""
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": text}
            ]

            # Call API
            response = self._call_api(model, messages)
            translated_text = response["choices"][0]["message"]["content"].strip()

            # Validate translation
            if not self._validate_translation(text, translated_text):
                raise ValidationError("Invalid translation structure")

            # Update successful stats
            self.rate_limiter.increment_usage("openrouter", model)
            self._update_stats(True)

            return translated_text

        except Exception as e:
            # Log error and update stats
            logging.error(f"Translation failed with model {model}: {str(e)}")
            self._update_stats(False)
            
            # Re-raise exception to try with next model
            raise TranslationError("openrouter", str(e))

    def is_available(self) -> bool:
        """Check if any models are available within rate limits."""
        return self.rate_limiter.get_available_model("openrouter", self.MODELS) is not None

    def get_priority(self) -> int:
        """Get provider priority (lower is higher priority)."""
        return self.config.priority  # Should be higher than Groq
