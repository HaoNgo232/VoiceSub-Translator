"""
Provider Service Implementation - Infrastructure Layer
Implements ProviderService interface for the application layer
"""

import logging
from typing import List, Optional, Dict
from ...core import ProviderService
from .base import BaseProvider

logger = logging.getLogger(__name__)


class ConcreteProviderService(ProviderService):
    """
    Concrete implementation of ProviderService interface
    
    Principle: Dependency Inversion + Adapter Pattern
    - Adapts existing provider infrastructure to new interface
    - Isolates application layer from infrastructure details
    """
    
    def __init__(self, providers: Optional[Dict[str, BaseProvider]] = None, provider_priorities: Optional[List[str]] = None):
        """
        Initialize provider service
        
        Args:
            providers: Dictionary of provider instances (None for auto-discovery)
            provider_priorities: List of provider names in priority order (None for defaults)
        """
        if providers is None:
            # Auto-discover providers (implement basic discovery)
            self.providers = self._discover_providers()
        else:
            self.providers = providers
        
        if provider_priorities is None:
            # Use default priorities
            self.provider_priorities = ['groq', 'google', 'openrouter', 'novita']
        else:
            self.provider_priorities = provider_priorities
        
        # Filter out None providers
        self.active_providers = {
            name: provider for name, provider in self.providers.items() 
            if provider is not None
        }
        
        logger.info(f"Provider service initialized with {len(self.active_providers)} providers")
        logger.info(f"Active providers: {list(self.active_providers.keys())}")
    
    def _discover_providers(self) -> Dict[str, BaseProvider]:
        """
        Auto-discover available providers
        
        Returns:
            Dictionary of discovered providers
        """
        # For now, return empty dict - could be enhanced to auto-discover
        # from existing provider infrastructure
        logger.info("Auto-discovering providers...")
        return {}
    
    def translate_text(
        self, 
        text: str, 
        target_lang: str, 
        provider_name: Optional[str] = None
    ) -> Optional[str]:
        """
        Translate text using specified or best available provider
        
        Args:
            text: Text to translate
            target_lang: Target language
            provider_name: Specific provider to use (None for auto-select)
            
        Returns:
            Translated text or None if failed
        """
        if not text.strip():
            return ""
        
        # Determine providers to try
        providers_to_try = self._get_providers_to_try(provider_name)
        
        if not providers_to_try:
            logger.error("No available providers")
            return None
        
        # Try providers in order
        last_error = None
        for provider_name in providers_to_try:
            provider = self.active_providers.get(provider_name)
            if not provider:
                continue
                
            try:
                logger.debug(f"Trying provider: {provider_name}")
                result = provider.translate(text, target_lang)
                
                if result and result.strip():
                    logger.debug(f"Successfully translated with provider: {provider_name}")
                    return result.strip()
                else:
                    logger.warning(f"Provider {provider_name} returned empty result")
                    
            except Exception as e:
                logger.warning(f"Provider {provider_name} failed: {str(e)}")
                last_error = e
                continue
        
        logger.error(f"All providers failed. Last error: {last_error}")
        return None
    
    def get_available_providers(self) -> List[str]:
        """Get list of available provider names"""
        return list(self.active_providers.keys())
    
    def _get_providers_to_try(self, preferred_provider: Optional[str]) -> List[str]:
        """
        Get ordered list of providers to try
        
        Args:
            preferred_provider: Preferred provider name
            
        Returns:
            List of provider names in try order
        """
        providers_to_try = []
        
        # Add preferred provider first if specified and available
        if preferred_provider and preferred_provider in self.active_providers:
            providers_to_try.append(preferred_provider)
        
        # Add other providers in priority order
        for provider_name in self.provider_priorities:
            if (provider_name in self.active_providers and 
                provider_name not in providers_to_try):
                providers_to_try.append(provider_name)
        
        return providers_to_try
    
    def get_provider_status(self) -> Dict[str, Dict[str, any]]:
        """
        Get status information for all providers
        
        Returns:
            Dictionary with provider status info
        """
        status = {}
        
        for name, provider in self.active_providers.items():
            try:
                # Test provider with simple text
                test_result = provider.translate("Hello", "vi")
                status[name] = {
                    'available': True,
                    'test_successful': bool(test_result),
                    'last_error': None
                }
            except Exception as e:
                status[name] = {
                    'available': False,
                    'test_successful': False,
                    'last_error': str(e)
                }
        
        return status
