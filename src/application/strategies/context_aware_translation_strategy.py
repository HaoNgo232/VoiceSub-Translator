"""
Context-Aware Translation Strategy - Application Layer
Implements intelligent translation using surrounding context
"""

import logging
from typing import List, Dict, Any, Optional
from ...core import TranslationStrategy, ProviderService, CacheService, SubtitleBlock, TranslationContext

logger = logging.getLogger(__name__)


class ContextAwareTranslationStrategy(TranslationStrategy):
    """
    Context-aware translation strategy - uses surrounding context for better translations
    
    Principle: Strategy Pattern implementation with enhanced intelligence
    - Single Responsibility: Handles context-aware translation logic
    - Open/Closed: Extensible for different context strategies
    """
    
    def __init__(self, provider_service: ProviderService, cache_service: CacheService):
        """
        Initialize context-aware translation strategy
        
        Args:
            provider_service: Service for calling translation providers
            cache_service: Service for caching translations
        """
        self.provider_service = provider_service
        self.cache_service = cache_service
        logger.info("Context-aware translation strategy initialized")
    
    def get_strategy_name(self) -> str:
        """Return strategy name"""
        return "context_aware"
    
    def translate_blocks(
        self, 
        blocks: List[SubtitleBlock], 
        context: TranslationContext,
        provider_service: ProviderService
    ) -> List[Optional[SubtitleBlock]]:
        """
        Translate subtitle blocks using context-aware strategy
        
        Args:
            blocks: List of subtitle blocks
            context: Translation context
            provider_service: Provider service to use
            
        Returns:
            List of translated subtitle blocks
        """
        translated_blocks = []
        previous_segments = []
        
        for i, block in enumerate(blocks):
            if block.is_empty():
                # Keep empty blocks as-is
                translated_blocks.append(block.clone())
                continue
            
            # Build context window
            context_segments = self._build_subtitle_context(
                blocks, i, context.context_window_size
            )
            
            # Create enhanced context for this block
            enhanced_context = context.clone()
            enhanced_context.previous_segments = previous_segments + context_segments
            
            # Create a copy of the block
            translated_block = block.clone()
            
            # Translate with context
            translated_text = self._translate_with_context(
                block.text, enhanced_context, provider_service
            )
            
            if translated_text:
                translated_block.translated_text = translated_text
                translated_blocks.append(translated_block)
                
                # Update previous segments for next iteration
                previous_segments.append(f"[{block.start_time}] {block.text} -> {translated_text}")
                if len(previous_segments) > context.context_window_size * 2:
                    previous_segments = previous_segments[-context.context_window_size:]
            else:
                # Translation failed
                translated_blocks.append(None)
            
            logger.debug(f"Context-aware translation for block {block.number}: {block.text[:30]}...")
        
        successful_count = len([b for b in translated_blocks if b])
        logger.info(f"Translated {successful_count} of {len(blocks)} blocks using context-aware strategy")
        return translated_blocks
    
    def _translate_with_context(
        self, 
        text: str, 
        context: TranslationContext, 
        provider_service: ProviderService
    ) -> Optional[str]:
        """
        Translate text with context using provider service
        
        Args:
            text: Text to translate
            context: Enhanced translation context
            provider_service: Provider service
            
        Returns:
            Translated text or None if failed
        """
        try:
            # Build enhanced prompt with context
            enhanced_text = self._build_context_enhanced_prompt(text, context)
            
            translated = provider_service.translate_text(
                text=enhanced_text,
                target_lang=context.target_language,
                provider_name=getattr(context, 'provider_name', None)
            )
            
            if translated:
                # Extract clean translation from response
                cleaned_translation = self._extract_translation_from_response(translated, text)
                return cleaned_translation
            
            return None
            
        except Exception as e:
            logger.error(f"Context-aware translation failed: {e}")
            return None
    
    def translate(self, text: str, context: TranslationContext, provider: str) -> str:
        """
        Translate text using context-aware approach
        
        Args:
            text: Text to translate
            context: Translation context with surrounding information
            provider: Provider name to use
            
        Returns:
            Translated text
        """
        if not text or not text.strip():
            return text
        
        # Generate cache key (includes context)
        cache_key = self._generate_cache_key(text, context, provider)
        
        # Check cache first
        if context.use_cache:
            cached_result = self.cache_service.get(cache_key)
            if cached_result:
                logger.debug(f"Cache hit for context-aware translation: {text[:50]}...")
                return cached_result
        
        # Build enhanced prompt with context
        enhanced_text = self._build_context_enhanced_prompt(text, context)
        
        # Perform translation
        try:
            translated = self.provider_service.translate(
                text=enhanced_text,
                target_language=context.target_language,
                source_language=context.source_language or "auto",
                provider=provider
            )
            
            # Extract just the translated text (remove context parts)
            cleaned_translation = self._extract_translation_from_response(translated, text)
            
            # Cache the result
            if context.use_cache and cleaned_translation:
                self.cache_service.set(cache_key, cleaned_translation)
            
            logger.debug(f"Context-aware translation: {text[:30]}... -> {cleaned_translation[:30]}...")
            return cleaned_translation
            
        except Exception as e:
            logger.error(f"Context-aware translation failed for text: {text[:50]}..., error: {e}")
            
            # Fallback to simple translation
            try:
                simple_result = self.provider_service.translate(
                    text=text,
                    target_language=context.target_language,
                    source_language=context.source_language or "auto",
                    provider=provider
                )
                logger.info("Fallback to simple translation successful")
                return simple_result
            except Exception as fallback_error:
                logger.error(f"Fallback translation also failed: {fallback_error}")
                return text
    
    def translate_batch(self, texts: List[str], context: TranslationContext, provider: str) -> List[str]:
        """
        Translate multiple texts with shared context
        
        Args:
            texts: List of texts to translate
            context: Translation context
            provider: Provider name
            
        Returns:
            List of translated texts
        """
        results = []
        
        # Build cumulative context as we translate
        previous_segments = context.previous_segments.copy() if hasattr(context, 'previous_segments') else []
        
        for i, text in enumerate(texts):
            # Update context with previous translations
            current_context = context.clone()
            if hasattr(current_context, 'previous_segments'):
                current_context.previous_segments = previous_segments[-context.context_window_size:]
            
            translated = self.translate(text, current_context, provider)
            results.append(translated)
            
            # Add to context for next iteration
            previous_segments.append(f"Original: {text} | Translated: {translated}")
        
        return results
    
    def translate_subtitle_blocks(
        self, 
        subtitle_blocks: List[SubtitleBlock], 
        context: TranslationContext, 
        provider: str
    ) -> List[SubtitleBlock]:
        """
        Translate subtitle blocks using context-aware strategy
        
        Args:
            subtitle_blocks: List of subtitle blocks
            context: Translation context
            provider: Provider name
            
        Returns:
            List of subtitle blocks with context-aware translations
        """
        translated_blocks = []
        previous_segments = []
        
        for i, block in enumerate(subtitle_blocks):
            if block.is_empty():
                # Keep empty blocks as-is
                translated_blocks.append(block.clone())
                continue
            
            # Build context window
            context_segments = self._build_subtitle_context(
                subtitle_blocks, i, context.context_window_size
            )
            
            # Create enhanced context for this block
            enhanced_context = context.clone()
            if hasattr(enhanced_context, 'previous_segments'):
                enhanced_context.previous_segments = previous_segments + context_segments
            else:
                # Add previous_segments attribute if it doesn't exist
                enhanced_context.previous_segments = previous_segments + context_segments
            
            # Create a copy of the block
            translated_block = block.clone()
            
            # Translate with context
            translated_text = self.translate(block.text, enhanced_context, provider)
            translated_block.translated_text = translated_text
            
            translated_blocks.append(translated_block)
            
            # Update previous segments for next iteration
            previous_segments.append(f"[{block.start_time}] {block.text} -> {translated_text}")
            if len(previous_segments) > context.context_window_size * 2:
                previous_segments = previous_segments[-context.context_window_size:]
            
            logger.debug(f"Context-aware translation for block {block.number}: {block.text[:30]}...")
        
        logger.info(f"Translated {len(translated_blocks)} subtitle blocks using context-aware strategy")
        return translated_blocks
    
    def _build_context_enhanced_prompt(self, text: str, context: TranslationContext) -> str:
        """
        Build enhanced prompt with context information
        
        Args:
            text: Original text to translate
            context: Translation context
            
        Returns:
            Enhanced prompt string
        """
        prompt_template = context.get_prompt_template()
        
        # Build context string
        context_parts = []
        
        # Add previous segments
        if hasattr(context, 'previous_segments') and context.previous_segments:
            recent_segments = context.previous_segments[-3:]  # Last 3 segments
            context_parts.append("Previous translations:")
            for segment in recent_segments:
                context_parts.append(f"- {segment}")
        
        # Add video metadata
        if hasattr(context, 'video_metadata') and context.video_metadata:
            metadata = context.video_metadata
            if metadata.get('title'):
                context_parts.append(f"Video title: {metadata['title']}")
            if metadata.get('genre'):
                context_parts.append(f"Genre: {metadata['genre']}")
        
        # Add custom instructions
        if hasattr(context, 'custom_instructions') and context.custom_instructions:
            context_parts.append(f"Special instructions: {context.custom_instructions}")
        
        context_string = "\n".join(context_parts) if context_parts else "No additional context"
        
        # Format the prompt
        try:
            return prompt_template.format(
                text=text,
                context=context_string
            )
        except KeyError:
            # Fallback if template doesn't have context placeholder
            return prompt_template.format(text=text)
    
    def _extract_translation_from_response(self, response: str, original_text: str) -> str:
        """
        Extract clean translation from provider response
        
        Args:
            response: Provider response
            original_text: Original text
            
        Returns:
            Cleaned translation
        """
        # Simple extraction - just return the response
        # Could be enhanced to parse structured responses
        return response.strip()
    
    def _build_subtitle_context(self, blocks: List[SubtitleBlock], current_index: int, window_size: int) -> List[str]:
        """
        Build context from surrounding subtitle blocks
        
        Args:
            blocks: All subtitle blocks
            current_index: Index of current block
            window_size: Number of surrounding blocks to include
            
        Returns:
            List of context strings
        """
        context_segments = []
        
        # Add previous blocks
        start_index = max(0, current_index - window_size)
        for i in range(start_index, current_index):
            block = blocks[i]
            context_segments.append(f"[{block.start_time}] {block.text}")
        
        # Add next blocks (if available)
        end_index = min(len(blocks), current_index + window_size + 1)
        for i in range(current_index + 1, end_index):
            block = blocks[i]
            context_segments.append(f"[{block.start_time}] {block.text}")
        
        return context_segments
    
    def _generate_cache_key(self, text: str, context: TranslationContext, provider: str) -> str:
        """
        Generate cache key for context-aware translation
        
        Args:
            text: Text being translated
            context: Translation context
            provider: Provider name
            
        Returns:
            Cache key string
        """
        key_components = context.get_cache_key_components()
        
        # Add context-specific components
        context_hash = ""
        if hasattr(context, 'previous_segments') and context.previous_segments:
            # Hash recent context for cache key
            import hashlib
            recent_context = "|".join(context.previous_segments[-2:])  # Last 2 segments
            context_hash = hashlib.md5(recent_context.encode()).hexdigest()[:8]
        
        key_components.update({
            'text': text,
            'provider': provider,
            'strategy': 'context_aware',
            'context_hash': context_hash
        })
        
        return self.cache_service.generate_key(**key_components)
