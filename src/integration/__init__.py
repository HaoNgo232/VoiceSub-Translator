"""
Integration Layer - Bridges Clean Architecture with Legacy GUI
Provides facade pattern for smooth migration
"""

import logging
from typing import Optional, Dict, Any, List
from pathlib import Path

from ..core import (
    TranslationStrategy, 
    ProviderService, 
    CacheService,
    SubtitleBlock,
    TranslationContext,
    TranslationMode
)
from ..application import (
    TranslationService,
    SimpleTranslationStrategy,
    ContextAwareTranslationStrategy
)
from ..infrastructure import (
    ConcreteProviderService,
    FileCacheService
)

logger = logging.getLogger(__name__)


class TranslationFacade:
    """
    Facade Pattern - Simplifies interaction with Clean Architecture
    
    Purpose: 
    - Hide complexity of new architecture from existing GUI
    - Provide backward compatibility
    - Enable gradual migration
    """
    
    def __init__(
        self,
        cache_dir: Optional[str] = None,
        use_context_aware: bool = True,
        default_strategy: str = "context_aware"
    ):
        """
        Initialize translation facade
        
        Args:
            cache_dir: Cache directory path
            use_context_aware: Enable context-aware translation
            default_strategy: Default translation strategy
        """
        # Initialize infrastructure services
        self.cache_service = FileCacheService(cache_dir)
        self.provider_service = ConcreteProviderService()
        
        # Initialize translation strategies
        self.strategies = {
            'simple': SimpleTranslationStrategy(
                provider_service=self.provider_service,
                cache_service=self.cache_service
            ),
            'context_aware': ContextAwareTranslationStrategy(
                provider_service=self.provider_service,
                cache_service=self.cache_service
            )
        }
        
        # Initialize main translation service
        self.translation_service = TranslationService(
            provider_service=self.provider_service,
            cache_service=self.cache_service
        )
        
        self.use_context_aware = use_context_aware
        logger.info(f"Translation facade initialized with strategy: {default_strategy}")
    
    def translate_text(
        self,
        text: str,
        target_language: str,
        source_language: str = "auto",
        provider: str = "groq",
        context: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Translate text - Legacy API compatibility
        
        Args:
            text: Text to translate
            target_language: Target language code
            source_language: Source language code
            provider: Provider name
            context: Additional context
            
        Returns:
            Translated text
        """
        try:
            # Create translation context
            translation_context = TranslationContext(
                source_language=source_language,
                target_language=target_language,
                mode=TranslationMode.CONTEXT_AWARE if self.use_context_aware else TranslationMode.SIMPLE,
                previous_segments=context.get('previous_segments', []) if context else [],
                video_metadata=context.get('video_metadata', {}) if context else {},
                custom_instructions=context.get('custom_instructions') if context else None
            )
            
            # Switch strategy if needed
            strategy_name = 'context_aware' if self.use_context_aware else 'simple'
            if self.translation_service.strategy != self.strategies[strategy_name]:
                self.translation_service.set_strategy(self.strategies[strategy_name])
            
            # Perform translation
            result = self.translation_service.translate(
                text=text,
                context=translation_context,
                provider=provider
            )
            
            return result
            
        except Exception as e:
            logger.error(f"Translation failed: {e}")
            # Fallback to simple translation
            return text  # Return original text as fallback
    
    def translate_subtitle_file(
        self,
        file_path: str,
        target_language: str,
        source_language: str = "auto",
        provider: str = "groq",
        output_path: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Translate subtitle file - Enhanced with context awareness
        
        Args:
            file_path: Path to subtitle file
            target_language: Target language code
            source_language: Source language code
            provider: Provider name
            output_path: Output file path
            context: Additional context
            
        Returns:
            Path to translated file
        """
        try:
            input_path = Path(file_path)
            
            if not input_path.exists():
                raise FileNotFoundError(f"Subtitle file not found: {file_path}")
            
            # Read subtitle file
            with open(input_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Parse subtitle blocks
            subtitle_blocks = SubtitleBlock.parse_srt_content(content)
            
            if not subtitle_blocks:
                raise ValueError("No subtitle blocks found in file")
            
            # Create translation context with video metadata
            video_metadata = context.get('video_metadata', {}) if context else {}
            if not video_metadata and input_path.stem:
                # Extract basic metadata from filename
                video_metadata = {
                    'title': input_path.stem,
                    'duration': len(subtitle_blocks) * 3  # Rough estimate
                }
            
            translation_context = TranslationContext(
                source_language=source_language,
                target_language=target_language,
                mode=TranslationMode.CONTEXT_AWARE if self.use_context_aware else TranslationMode.SIMPLE,
                previous_segments=[],  # Will be populated during translation
                video_metadata=video_metadata,
                custom_instructions=context.get('custom_instructions') if context else None
            )
            
            # Switch to appropriate strategy
            strategy_name = 'context_aware' if self.use_context_aware else 'simple'
            if self.translation_service.strategy != self.strategies[strategy_name]:
                self.translation_service.set_strategy(self.strategies[strategy_name])
            
            # Translate subtitle blocks
            translated_blocks = self.translation_service.translate_subtitle_blocks(
                subtitle_blocks=subtitle_blocks,
                context=translation_context,
                provider=provider
            )
            
            # Generate output content
            output_content = SubtitleBlock.to_srt_content(translated_blocks)
            
            # Determine output path
            if not output_path:
                output_path = str(input_path.parent / f"{input_path.stem}_{target_language}.srt")
            
            # Write translated file
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(output_content)
            
            logger.info(f"Translated subtitle file saved: {output_path}")
            return output_path
            
        except Exception as e:
            logger.error(f"Subtitle translation failed: {e}")
            raise
    
    def set_translation_mode(self, mode: str) -> None:
        """
        Set translation mode
        
        Args:
            mode: 'simple' or 'context_aware'
        """
        if mode not in self.strategies:
            raise ValueError(f"Unknown translation mode: {mode}")
        
        self.use_context_aware = (mode == 'context_aware')
        self.translation_service.set_strategy(self.strategies[mode])
        logger.info(f"Translation mode set to: {mode}")
    
    def get_available_providers(self) -> List[str]:
        """Get list of available providers"""
        return self.provider_service.get_available_providers()
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        return self.cache_service.get_cache_stats()
    
    def clear_cache(self) -> None:
        """Clear translation cache"""
        self.cache_service.clear_all()
        logger.info("Translation cache cleared")
    
    def validate_provider_config(self, provider: str) -> bool:
        """
        Validate provider configuration
        
        Args:
            provider: Provider name
            
        Returns:
            True if provider is configured properly
        """
        try:
            available_providers = self.get_available_providers()
            return provider in available_providers
        except Exception as e:
            logger.error(f"Provider validation failed: {e}")
            return False


class LegacyTranslatorAdapter:
    """
    Adapter Pattern - Provides exact legacy API compatibility
    
    Purpose: Drop-in replacement for existing translator classes
    """
    
    def __init__(self, **kwargs):
        """Initialize with legacy parameters"""
        self.facade = TranslationFacade(**kwargs)
        
        # Legacy attribute compatibility
        self.provider = "groq"
        self.source_lang = "auto"
        self.target_lang = "vi"
    
    def translate(self, text: str, **kwargs) -> str:
        """Legacy translate method"""
        provider = kwargs.get('provider', self.provider)
        source_lang = kwargs.get('source_lang', self.source_lang)
        target_lang = kwargs.get('target_lang', self.target_lang)
        
        return self.facade.translate_text(
            text=text,
            target_language=target_lang,
            source_language=source_lang,
            provider=provider
        )
    
    def translate_file(self, file_path: str, **kwargs) -> str:
        """Legacy translate file method"""
        provider = kwargs.get('provider', self.provider)
        source_lang = kwargs.get('source_lang', self.source_lang)
        target_lang = kwargs.get('target_lang', self.target_lang)
        output_path = kwargs.get('output_path')
        
        return self.facade.translate_subtitle_file(
            file_path=file_path,
            target_language=target_lang,
            source_language=source_lang,
            provider=provider,
            output_path=output_path
        )
    
    def set_provider(self, provider: str) -> None:
        """Legacy set provider method"""
        self.provider = provider
    
    def set_languages(self, source: str, target: str) -> None:
        """Legacy set languages method"""
        self.source_lang = source
        self.target_lang = target
