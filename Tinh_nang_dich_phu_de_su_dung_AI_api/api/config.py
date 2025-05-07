import os
from typing import Dict, Any, Optional
from dataclasses import dataclass
from dotenv import load_dotenv

@dataclass
class ProviderConfig:
    """Configuration for a single API provider."""
    name: str
    api_key: str
    priority: int
    timeout: int = 30
    max_retries: int = 3
    batch_size: Optional[int] = None
    rate_limits: Optional[Dict[str, int]] = None
    extra_config: Optional[Dict[str, Any]] = None

class APIConfig:
    """Configuration manager for translation API providers."""
    
    def __init__(self):
        """Initialize configuration manager."""
        load_dotenv()
        self.providers: Dict[str, ProviderConfig] = {}
        self._load_configs()

    def _load_configs(self):
        """Load provider configurations from environment variables."""
        # Groq configuration
        groq_api_key = os.getenv('GROQ_API_KEY')
        if groq_api_key:
            self.providers['groq'] = ProviderConfig(
                name='groq',
                api_key=groq_api_key,
                priority=1,
                rate_limits={
                    'rpm': 30,
                    'tpm': {
                        'gemma2-9b-it': 15000,
                        'llama-3.3-70b-versatile': 6000,
                        'llama3-70b-8192': 6000,
                        'llama3-8b-8192': 6000,
                    }
                },
                extra_config={
                    'models': [
                        'gemma2-9b-it',
                        'llama-3.3-70b-versatile',
                        'llama3-70b-8192',
                        'llama3-8b-8192',
                    ]
                }
            )

        # OpenRouter configuration
        openrouter_api_key = os.getenv('OPENROUTER_API_KEY')
        if openrouter_api_key:
            self.providers['openrouter'] = ProviderConfig(
                name='openrouter',
                api_key=openrouter_api_key,
                priority=2,  # Lower priority than Groq
                rate_limits={
                    'daily': 200,  # 200 requests per model per day
                    'minute': 20,  # 20 requests per model per minute
                },
                extra_config={
                    'models': [
                        'google/gemma-3-12b-it:free',
                        'google/gemma-2-9b-it:free',
                        'qwen/qwen2.5-vl-32b-instruct:free',
                        'featherless/qwerky-72b:free',
                        'google/gemma-3-27b-it:free',
                        'cognitivecomputations/dolphin3.0-r1-mistral-24b:free',
                        'qwen/qwen2.5-vl-72b-instruct:free',
                        'qwen/qwq-32b-preview:free',
                        'mistralai/mistral-7b-instruct:free'
                    ]
                }
            )

    def get_provider_config(self, provider_name: str) -> Optional[ProviderConfig]:
        """
        Get configuration for a specific provider.
        
        Args:
            provider_name: Name of the provider
            
        Returns:
            Provider configuration if exists, None otherwise
        """
        return self.providers.get(provider_name)

    def get_available_providers(self) -> Dict[str, ProviderConfig]:
        """
        Get all configured providers.
        
        Returns:
            Dictionary of provider configurations
        """
        return self.providers.copy()

    def add_provider(self, name: str, config: ProviderConfig) -> None:
        """
        Add or update a provider configuration.
        
        Args:
            name: Provider name
            config: Provider configuration
        """
        self.providers[name] = config

    def remove_provider(self, name: str) -> None:
        """
        Remove a provider configuration.
        
        Args:
            name: Provider name
        """
        if name in self.providers:
            del self.providers[name]

    def get_default_provider(self) -> Optional[ProviderConfig]:
        """
        Get the provider with highest priority (lowest priority number).
        
        Returns:
            Provider configuration if any exists, None otherwise
        """
        if not self.providers:
            return None
            
        return min(self.providers.values(), key=lambda x: x.priority)

    @staticmethod
    def validate_config(config: ProviderConfig) -> bool:
        """
        Validate provider configuration.
        
        Args:
            config: Provider configuration to validate
            
        Returns:
            True if configuration is valid, False otherwise
        """
        try:
            if not config.name or not config.api_key:
                return False
                
            if config.priority < 0:
                return False
                
            if config.timeout <= 0 or config.max_retries < 0:
                return False
                
            return True
        except Exception:
            return False
