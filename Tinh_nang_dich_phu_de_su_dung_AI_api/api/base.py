from abc import ABC, abstractmethod
from typing import Optional, Dict, Any, List
import logging
import time
from datetime import datetime

class BaseAPIHandler(ABC):
    """Base class for all API handlers."""
    
    def __init__(self, max_retries: int = 3, timeout: int = 30):
        """
        Initialize base API handler.
        
        Args:
            max_retries: Maximum number of retries for failed requests
            timeout: Request timeout in seconds
        """
        self.max_retries = max_retries
        self.timeout = timeout
        self.stats = {
            "total_requests": 0,
            "successful_requests": 0,
            "failed_requests": 0,
            "total_tokens": 0,
            "last_request": None,
            "errors": []
        }

    @abstractmethod
    def translate_text(self, text: str, target_language: str = "Vietnamese") -> Optional[str]:
        """
        Translate text using the API provider.
        
        Args:
            text: Text to translate
            target_language: Target language for translation
            
        Returns:
            Translated text if successful, None otherwise
        """
        pass

    @abstractmethod
    def _initialize_api(self):
        """Initialize API client and validate configuration."""
        pass

    def _validate_translation(self, source_text: str, translated_text: str) -> bool:
        """
        Validate translation structure and content.
        
        Args:
            source_text: Original text
            translated_text: Translated text
            
        Returns:
            True if translation is valid, False otherwise
        """
        try:
            if not translated_text or not isinstance(translated_text, str):
                return False
                
            # Count block markers
            source_blocks = source_text.count('---BLOCK')
            translated_blocks = translated_text.count('---BLOCK')
            
            if source_blocks != translated_blocks:
                logging.error(f"Block count mismatch: source={source_blocks}, translated={translated_blocks}")
                return False
                
            return True
        except Exception as e:
            logging.error(f"Translation validation error: {str(e)}")
            return False

    def _handle_rate_limit(self, retry_after: int) -> None:
        """
        Handle rate limit by updating stats and sleeping.
        
        Args:
            retry_after: Number of seconds to wait
        """
        self.stats["errors"].append({
            "type": "rate_limit",
            "timestamp": datetime.now().isoformat(),
            "retry_after": retry_after
        })
        time.sleep(retry_after)

    def _update_stats(self, success: bool, tokens: Optional[int] = None) -> None:
        """
        Update handler statistics.
        
        Args:
            success: Whether the request was successful
            tokens: Number of tokens used (if available)
        """
        self.stats["total_requests"] += 1
        self.stats["last_request"] = datetime.now().isoformat()
        
        if success:
            self.stats["successful_requests"] += 1
        else:
            self.stats["failed_requests"] += 1
            
        if tokens:
            self.stats["total_tokens"] += tokens

    def get_stats(self) -> Dict[str, Any]:
        """
        Get current handler statistics.
        
        Returns:
            Dictionary containing handler stats
        """
        return self.stats.copy()

    def reset_stats(self) -> None:
        """Reset handler statistics."""
        self.stats = {
            "total_requests": 0,
            "successful_requests": 0,
            "failed_requests": 0,
            "total_tokens": 0,
            "last_request": None,
            "errors": []
        }

    @abstractmethod
    def is_available(self) -> bool:
        """
        Check if the handler is currently available.
        
        Returns:
            True if handler can process requests, False otherwise
        """
        pass

    @abstractmethod
    def get_priority(self) -> int:
        """
        Get handler priority.
        
        Returns:
            Priority value (lower is higher priority)
        """
        pass
