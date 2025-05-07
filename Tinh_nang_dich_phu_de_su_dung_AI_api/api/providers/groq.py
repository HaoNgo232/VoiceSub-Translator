import os
import time
import logging
import httpx
from typing import Optional, Dict, Any
from datetime import datetime

from groq import Groq
from groq import RateLimitError
from ..base import BaseAPIHandler
from ..exceptions import (
    AuthenticationError,
    ConfigurationError,
    ConnectionError,
    RateLimitError as APIRateLimitError,
    TranslationError,
    ValidationError
)
from ..config import ProviderConfig

class GroqAPIHandler(BaseAPIHandler):
    """Handler for Groq translation API."""

    def __init__(self, config: ProviderConfig):
        """
        Initialize Groq API handler.
        
        Args:
            config: Provider configuration
        """
        super().__init__(
            max_retries=config.max_retries,
            timeout=config.timeout
        )
        self.config = config
        self.models = {
            model: {
                "errors": 0,
                "consecutive_errors": 0,
                "last_error": None,
                "retry_after": 0,
                "total_requests": 0,
                "successful_requests": 0
            }
            for model in config.extra_config.get("models", [])
        }
        self.current_model_index = 0
        self._initialize_api()

    def _initialize_api(self):
        """Initialize Groq API client."""
        try:
            if not self.config.api_key:
                raise ConfigurationError("API key not configured")
            self.client = Groq(api_key=self.config.api_key)
            self._test_connection()
        except Exception as e:
            raise ConfigurationError(f"Failed to initialize Groq API: {str(e)}")

    def _test_connection(self):
        """Test API connection with minimal request."""
        try:
            test_model = list(self.models.keys())[0]
            self.client.chat.completions.create(
                messages=[{"role": "user", "content": "test"}],
                model=test_model,
                max_tokens=1
            )
            logging.info("Successfully connected to Groq API")
        except Exception as e:
            raise ConnectionError(f"Failed to connect to Groq API: {str(e)}")

    def _get_next_model(self) -> Optional[str]:
        """
        Get next available model.
        
        Returns:
            Model name if available, None otherwise
        """
        current_time = time.time()
        tried_models = set()
        model_names = list(self.models.keys())
        
        while len(tried_models) < len(model_names):
            model = model_names[self.current_model_index]
            self.current_model_index = (self.current_model_index + 1) % len(model_names)
            
            model_info = self.models[model]
            
            # Skip if model is in cooldown
            if model_info["retry_after"] > current_time:
                tried_models.add(model)
                continue
                
            # Skip if model has too many errors
            if model_info["consecutive_errors"] >= self.max_retries:
                tried_models.add(model)
                continue
                
            return model
            
        # If no models available, reset error counters and try again
        if not tried_models:
            return None
            
        logging.warning("Resetting all models' error counts")
        for model in self.models:
            self.models[model]["errors"] = 0
            self.models[model]["consecutive_errors"] = 0
            self.models[model]["retry_after"] = 0
            
        return model_names[0]

    def translate_text(self, text: str, target_language: str = "Vietnamese") -> Optional[str]:
        """
        Translate text using Groq API.
        
        Args:
            text: Text to translate
            target_language: Target language
            
        Returns:
            Translated text
            
        Raises:
            Various exceptions based on error type
        """
        if not text or not text.strip():
            raise ValidationError("Empty input text")

        current_model = self._get_next_model()
        if not current_model:
            raise TranslationError("groq", "No available models")

        try:
            # Prepare prompt
            system_prompt = f"""Translate the following English text to {target_language}.
IMPORTANT: 
1. Maintain the exact structure of the input text
2. Keep all block markers (---BLOCK X--- and ---END BLOCK X---)
3. Only translate the content between block markers
4. Return the complete structure with translations
5. Do not add any additional text or explanations
"""
            # Call API
            chat_completion = self.client.chat.completions.create(
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": text}
                ],
                model=current_model,
                timeout=self.timeout
            )

            # Get and validate result
            translated_text = chat_completion.choices[0].message.content.strip()
            if not self._validate_translation(text, translated_text):
                raise ValidationError("Invalid translation structure")

            # Update model stats
            model_info = self.models[current_model]
            model_info["errors"] = 0
            model_info["consecutive_errors"] = 0
            model_info["successful_requests"] += 1

            # Update tokens if available
            if hasattr(chat_completion, 'usage') and chat_completion.usage:
                self._update_stats(True, chat_completion.usage.total_tokens)
            else:
                self._update_stats(True)

            return translated_text

        except httpx.HTTPStatusError as e:
            if e.response.status_code == 429:  # Rate limit
                retry_after = int(e.response.headers.get('retry-after', 60))
                self.models[current_model]["retry_after"] = time.time() + retry_after
                raise APIRateLimitError(retry_after)
            elif e.response.status_code in [401, 403]:
                raise AuthenticationError("Invalid API credentials")
            else:
                raise TranslationError("groq", f"HTTP error {e.response.status_code}")

        except RateLimitError as e:
            retry_after = int(getattr(e.response.headers, 'retry-after', 60))
            self.models[current_model]["retry_after"] = time.time() + retry_after
            raise APIRateLimitError(retry_after)

        except Exception as e:
            # Update error stats
            model_info = self.models[current_model]
            model_info["errors"] += 1
            model_info["consecutive_errors"] += 1
            model_info["last_error"] = str(e)
            self._update_stats(False)
            
            raise TranslationError("groq", str(e))

    def is_available(self) -> bool:
        """Check if any models are available."""
        return self._get_next_model() is not None

    def get_priority(self) -> int:
        """Get provider priority."""
        return self.config.priority

    def get_model_stats(self) -> Dict[str, Any]:
        """Get current model statistics."""
        return {
            name: {
                **info,
                "available": info["retry_after"] <= time.time() and
                           info["consecutive_errors"] < self.max_retries
            }
            for name, info in self.models.items()
        }
