import logging
from typing import List, Optional, Dict, Any
from threading import Lock
from datetime import datetime, timedelta

from .base import BaseAPIHandler
from .config import APIConfig, ProviderConfig
from .exceptions import NoAvailableProvidersError, TranslationError
from .utils.monitoring import log_api_call, metrics

class APIManager:
    """Manager class to handle multiple translation API providers."""
    
    def __init__(self, config: Optional[APIConfig] = None):
        """
        Initialize API manager.
        
        Args:
            config: Optional API configuration, creates new if not provided
        """
        self.config = config or APIConfig()
        self.providers: Dict[str, BaseAPIHandler] = {}
        self.provider_lock = Lock()
        self.provider_stats: Dict[str, Dict[str, Any]] = {}
        self._initialize_providers()

    def _initialize_providers(self) -> None:
        """Initialize configured providers."""
        available_providers = self.config.get_available_providers()
        
        for name, config in available_providers.items():
            try:
                # Import provider dynamically
                module = __import__(f'api.providers.{name}', fromlist=[''])
                handler_class = getattr(module, f'{name.capitalize()}APIHandler')
                
                # Initialize provider
                provider = handler_class(config)
                self.providers[name] = provider
                
                # Initialize stats
                self.provider_stats[name] = {
                    "last_success": None,
                    "last_error": None,
                    "error_count": 0,
                    "consecutive_errors": 0,
                    "cooldown_until": None
                }
                
                logging.info(f"Initialized provider: {name}")
            except Exception as e:
                logging.error(f"Failed to initialize provider {name}: {str(e)}")

    def _get_available_provider(self) -> Optional[BaseAPIHandler]:
        """
        Get the next available provider based on priority and status.
        
        Returns:
            Available provider if any, None otherwise
        """
        with self.provider_lock:
            # Sort providers by priority
            sorted_providers = sorted(
                self.providers.items(),
                key=lambda x: x[1].get_priority()
            )
            
            current_time = datetime.now()
            
            for name, provider in sorted_providers:
                stats = self.provider_stats[name]
                
                # Skip if provider is in cooldown
                if stats["cooldown_until"] and current_time < stats["cooldown_until"]:
                    continue
                
                # Skip if provider has too many consecutive errors
                if stats["consecutive_errors"] >= provider.max_retries:
                    continue
                
                # Check if provider is available
                if provider.is_available():
                    return provider
            
            return None

    def _handle_provider_error(self, provider_name: str, error: Exception) -> None:
        """
        Update provider stats after an error.
        
        Args:
            provider_name: Name of the provider
            error: Error that occurred
        """
        with self.provider_lock:
            stats = self.provider_stats[provider_name]
            stats["last_error"] = datetime.now()
            stats["error_count"] += 1
            stats["consecutive_errors"] += 1
            
            # Apply cooldown if too many consecutive errors
            if stats["consecutive_errors"] >= self.providers[provider_name].max_retries:
                stats["cooldown_until"] = datetime.now() + timedelta(minutes=5)
                logging.warning(
                    f"Provider {provider_name} placed in cooldown until "
                    f"{stats['cooldown_until'].strftime('%Y-%m-%d %H:%M:%S')}"
                )

    def _handle_provider_success(self, provider_name: str) -> None:
        """
        Update provider stats after a successful operation.
        
        Args:
            provider_name: Name of the provider
        """
        with self.provider_lock:
            stats = self.provider_stats[provider_name]
            stats["last_success"] = datetime.now()
            stats["consecutive_errors"] = 0
            stats["cooldown_until"] = None

    @log_api_call
    def translate(self, text: str, target_language: str = "Vietnamese") -> str:
        """
        Translate text using available providers.
        
        Args:
            text: Text to translate
            target_language: Target language for translation
            
        Returns:
            Translated text
            
        Raises:
            NoAvailableProvidersError: If no providers are available
            TranslationError: If translation fails
        """
        errors = []
        
        while True:
            provider = self._get_available_provider()
            if not provider:
                if not errors:
                    raise NoAvailableProvidersError("No translation providers available")
                raise TranslationError(
                    "all_providers",
                    f"All providers failed: {'; '.join(str(e) for e in errors)}"
                )
            
            try:
                translation = provider.translate_text(text, target_language)
                if translation:
                    # Use provider name from config
                    provider_name = provider.config.name
                    self._handle_provider_success(provider_name)
                    return translation
                    
                # If translation is None but no exception was raised,
                # treat it as an error and try next provider
                raise TranslationError(
                    provider.__class__.__name__,
                    "Provider returned empty translation"
                )
                
            except Exception as e:
                # Use provider name from config
                provider_name = provider.config.name 
                self._handle_provider_error(provider_name, e)
                errors.append(f"{provider_name}: {str(e)}")
                logging.error(f"Translation failed with provider {provider_name}: {str(e)}")
                continue

    def get_provider_stats(self) -> Dict[str, Any]:
        """
        Get current statistics for all providers.
        
        Returns:
            Dictionary containing provider statistics
        """
        with self.provider_lock:
            stats = {}
            for name, provider in self.providers.items():
                provider_stats = self.provider_stats[name].copy()
                provider_stats.update({
                    "priority": provider.get_priority(),
                    "available": provider.is_available(),
                    "metrics": metrics.get_metrics()["providers"].get(name, {})
                })
                stats[name] = provider_stats
            return stats

    def reset_provider_stats(self, provider_name: Optional[str] = None) -> None:
        """
        Reset statistics for one or all providers.
        
        Args:
            provider_name: Name of provider to reset, or None for all
        """
        with self.provider_lock:
            if provider_name:
                if provider_name in self.provider_stats:
                    self.provider_stats[provider_name] = {
                        "last_success": None,
                        "last_error": None,
                        "error_count": 0,
                        "consecutive_errors": 0,
                        "cooldown_until": None
                    }
            else:
                for name in self.provider_stats:
                    self.reset_provider_stats(name)
