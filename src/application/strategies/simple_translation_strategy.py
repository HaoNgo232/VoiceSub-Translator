"""
Simple Translation Strategy - Application Layer
Implements basic one-by-one translation without context
"""

import logging
from typing import List, Optional
from ...core import TranslationStrategy, ProviderService, CacheService, SubtitleBlock, TranslationContext

logger = logging.getLogger(__name__)


class SimpleTranslationStrategy(TranslationStrategy):
    """
    Simple translation strategy - translates each text independently
    
    Principle: Strategy Pattern implementation
    - Single Responsibility: Only handles simple translation logic
    - Open/Closed: Can be extended without modification
    """
    
    def __init__(self, provider_service: ProviderService, cache_service: CacheService):
        """
        Initialize simple translation strategy
        
        Args:
            provider_service: Service for calling translation providers
            cache_service: Service for caching translations
        """
        self.provider_service = provider_service
        self.cache_service = cache_service
        logger.info("Simple translation strategy initialized")
    
    def get_strategy_name(self) -> str:
        """Return strategy name"""
        return "simple"
    
    def translate_blocks(
        self, 
        blocks: List[SubtitleBlock], 
        context: TranslationContext,
        provider_service: ProviderService
    ) -> List[Optional[SubtitleBlock]]:
        """
        Translate subtitle blocks using simple approach
        
        Args:
            blocks: List of subtitle blocks
            context: Translation context
            provider_service: Provider service to use
            
        Returns:
            List of translated subtitle blocks
        """
        translated_blocks = []
        
        for block in blocks:
            if block.is_empty():
                # Keep empty blocks as-is
                translated_blocks.append(block.clone())
                continue
            
            # Create a copy of the block
            translated_block = block.clone()
            
            # Translate the text
            translated_text = self._translate_single_text(
                block.text, context, provider_service
            )
            
            if translated_text:
                translated_block.translated_text = translated_text
                translated_blocks.append(translated_block)
            else:
                # Translation failed, append None
                translated_blocks.append(None)
            
            logger.debug(f"Translated block {block.number}: {block.text[:30]}...")
        
        logger.info(f"Translated {len([b for b in translated_blocks if b])} of {len(blocks)} blocks using simple strategy")
        return translated_blocks
    
    def translate(self, text: str, context: TranslationContext, provider: str) -> str:
        """
        Translate text using simple approach
        
        Args:
            text: Text to translate
            context: Translation context (minimal usage in simple strategy)
            provider: Provider name to use
            
        Returns:
            Translated text
        """
        if not text or not text.strip():
            return text
        
        # Generate cache key
        cache_key = self._generate_cache_key(text, context, provider)
        
        # Check cache first
        if context.use_cache:
            cached_result = self.cache_service.get(cache_key)
            if cached_result:
                logger.debug(f"Cache hit for text: {text[:50]}...")
                return cached_result
        
        # Perform translation
        try:
            translated = self.provider_service.translate_text(
                text=text,
                target_lang=context.target_language,
                provider_name=provider
            )
            
            if not translated:
                logger.warning(f"Translation returned empty result for: {text[:50]}...")
                return text
            
            # Cache the result
            if context.use_cache and translated:
                self.cache_service.set(cache_key, translated)
            
            logger.debug(f"Translated: {text[:30]}... -> {translated[:30]}...")
            return translated
            
        except Exception as e:
            logger.error(f"Translation failed for text: {text[:50]}..., error: {e}")
            
            if context.retry_failed:
                # Could implement retry logic here
                pass
            
            # Return original text as fallback
            return text
    
    def _translate_single_text(
        self, 
        text: str, 
        context: TranslationContext, 
        provider_service: ProviderService
    ) -> Optional[str]:
        """
        Translate single text using provider service
        
        Args:
            text: Text to translate
            context: Translation context
            provider_service: Provider service
            
        Returns:
            Translated text or None if failed
        """
        try:
            translated = provider_service.translate_text(
                text=text,
                target_lang=context.target_language,
                provider_name=getattr(context, 'provider_name', None)
            )
            return translated
        except Exception as e:
            logger.error(f"Single text translation failed: {e}")
            return None
    
    def translate_batch(self, texts: List[str], context: TranslationContext, provider: str) -> List[str]:
        """
        Translate multiple texts
        
        Args:
            texts: List of texts to translate
            context: Translation context
            provider: Provider name
            
        Returns:
            List of translated texts
        """
        results = []
        
        for text in texts:
            translated = self.translate(text, context, provider)
            results.append(translated)
        
        return results
    
    def translate_subtitle_blocks(
        self, 
        subtitle_blocks: List[SubtitleBlock], 
        context: TranslationContext, 
        provider: str
    ) -> List[SubtitleBlock]:
        """
        Translate subtitle blocks using simple strategy
        
        Args:
            subtitle_blocks: List of subtitle blocks
            context: Translation context
            provider: Provider name
            
        Returns:
            List of subtitle blocks with translations
        """
        translated_blocks = []
        
        for block in subtitle_blocks:
            if block.is_empty():
                # Keep empty blocks as-is
                translated_blocks.append(block.clone())
                continue
            
            # Create a copy of the block
            translated_block = block.clone()
            
            # Translate the text
            translated_text = self.translate(block.text, context, provider)
            translated_block.translated_text = translated_text
            
            translated_blocks.append(translated_block)
            
            logger.debug(f"Translated block {block.number}: {block.text[:30]}...")
        
        logger.info(f"Translated {len(translated_blocks)} subtitle blocks using simple strategy")
        return translated_blocks
    
    def _generate_cache_key(self, text: str, context: TranslationContext, provider: str) -> str:
        """
        Generate cache key for simple translation
        
        Args:
            text: Text being translated
            context: Translation context
            provider: Provider name
            
        Returns:
            Cache key string
        """
        key_components = context.get_cache_key_components()
        key_components.update({
            'text': text,
            'provider': provider,
            'strategy': 'simple'
        })
        
        return self.cache_service.generate_key(**key_components)
