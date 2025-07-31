"""
Main Translation Service - Application Layer Orchestrator
Coordinates between strategies, providers, and caching
"""

import logging
from typing import List, Optional, Dict, Type
from ...core import (
    SubtitleBlock, 
    TranslationContext, 
    TranslationMode,
    TranslationStrategy,
    ProviderService,
    CacheService
)
from ..strategies import SimpleTranslationStrategy, ContextAwareTranslationStrategy

logger = logging.getLogger(__name__)


class TranslationService:
    """
    Main translation orchestrator
    
    Principle: Facade Pattern + Strategy Pattern + Dependency Injection
    - Provides simple interface for complex translation operations
    - Manages strategy selection and execution
    - Handles caching and provider coordination
    """
    
    def __init__(
        self, 
        provider_service: ProviderService,
        cache_service: Optional[CacheService] = None
    ):
        """
        Initialize translation service
        
        Args:
            provider_service: Service for calling translation providers
            cache_service: Optional cache service for performance
        """
        self.provider_service = provider_service
        self.cache_service = cache_service
        
        # Register available strategies
        self._strategies: Dict[str, Type[TranslationStrategy]] = {
            TranslationMode.SIMPLE.value: SimpleTranslationStrategy,
            TranslationMode.CONTEXT_AWARE.value: ContextAwareTranslationStrategy,
        }
        
        # Strategy instances cache
        self._strategy_instances: Dict[str, TranslationStrategy] = {}
        
        logger.info(f"Translation service initialized with strategies: {list(self._strategies.keys())}")
    
    def translate_subtitle_file(
        self, 
        subtitle_blocks: List[SubtitleBlock],
        context: TranslationContext
    ) -> List[Optional[SubtitleBlock]]:
        """
        Main entry point for translating subtitle files
        
        Args:
            subtitle_blocks: List of subtitle blocks to translate
            context: Translation context with all parameters
            
        Returns:
            List of translated blocks (None for failed translations)
        """
        logger.info(f"Starting translation of {len(subtitle_blocks)} blocks")
        logger.info(f"Mode: {context.mode.value}, Target: {context.target_language}")
        
        if not subtitle_blocks:
            logger.warning("No subtitle blocks provided")
            return []
        
        # Check cache first if enabled
        if context.use_cache and self.cache_service:
            cached_results = self._check_cache_for_blocks(subtitle_blocks, context)
            if cached_results:
                logger.info("Found cached translations")
                return cached_results
        
        # Select and execute strategy
        strategy = self._get_strategy(context.mode)
        translated_blocks = strategy.translate_blocks(
            subtitle_blocks, context, self.provider_service
        )
        
        # Cache results if enabled
        if context.use_cache and self.cache_service:
            self._cache_translation_results(subtitle_blocks, translated_blocks, context)
        
        # Log summary
        successful = sum(1 for block in translated_blocks if block is not None)
        logger.info(f"Translation completed: {successful}/{len(subtitle_blocks)} successful")
        
        return translated_blocks
    
    def translate_single_block(
        self, 
        block: SubtitleBlock,
        context: TranslationContext
    ) -> Optional[SubtitleBlock]:
        """
        Translate a single subtitle block
        
        Args:
            block: Single subtitle block
            context: Translation context
            
        Returns:
            Translated block or None if failed
        """
        logger.debug(f"Translating single block {block.number}")
        
        # Check cache first
        if context.use_cache and self.cache_service:
            cached_result = self._check_cache_for_single_block(block, context)
            if cached_result:
                return cached_result
        
        # Use simple strategy for single block (no context available)
        simple_context = context.clone(mode=TranslationMode.SIMPLE)
        strategy = self._get_strategy(TranslationMode.SIMPLE)
        
        results = strategy.translate_blocks([block], simple_context, self.provider_service)
        translated_block = results[0] if results else None
        
        # Cache result
        if translated_block and context.use_cache and self.cache_service:
            self._cache_single_block(block, translated_block, context)
        
        return translated_block
    
    def get_available_strategies(self) -> List[str]:
        """Get list of available translation strategies"""
        return list(self._strategies.keys())
    
    def add_strategy(self, mode: str, strategy_class: Type[TranslationStrategy]):
        """
        Add custom translation strategy
        
        Args:
            mode: Strategy mode name
            strategy_class: Strategy class implementing TranslationStrategy
        """
        self._strategies[mode] = strategy_class
        logger.info(f"Added custom strategy: {mode}")
    
    def _get_strategy(self, mode: TranslationMode) -> TranslationStrategy:
        """
        Get strategy instance for given mode
        
        Args:
            mode: Translation mode
            
        Returns:
            Strategy instance
            
        Raises:
            ValueError: If strategy not found
        """
        mode_str = mode.value
        
        # Check if strategy exists
        if mode_str not in self._strategies:
            logger.warning(f"Strategy {mode_str} not found, falling back to simple")
            mode_str = TranslationMode.SIMPLE.value
        
        # Get or create strategy instance
        if mode_str not in self._strategy_instances:
            strategy_class = self._strategies[mode_str]
            self._strategy_instances[mode_str] = strategy_class()
            logger.debug(f"Created strategy instance: {mode_str}")
        
        return self._strategy_instances[mode_str]
    
    def _check_cache_for_blocks(
        self, 
        blocks: List[SubtitleBlock],
        context: TranslationContext
    ) -> Optional[List[Optional[SubtitleBlock]]]:
        """Check cache for all blocks"""
        if not self.cache_service:
            return None
        
        # Generate cache key for the entire file
        file_cache_key = self._generate_file_cache_key(blocks, context)
        
        cached_file = self.cache_service.get(file_cache_key)
        if cached_file:
            logger.info("Found complete file in cache")
            # Deserialize cached blocks (implementation depends on cache format)
            return self._deserialize_cached_blocks(cached_file)
        
        # Check individual blocks
        cached_blocks = []
        cache_hits = 0
        
        for block in blocks:
            cached_block = self._check_cache_for_single_block(block, context)
            cached_blocks.append(cached_block)
            if cached_block:
                cache_hits += 1
        
        # Only use cache if we have significant coverage
        cache_coverage = cache_hits / len(blocks) if blocks else 0
        if cache_coverage >= 0.8:  # 80% cache hit rate
            logger.info(f"Using cached results: {cache_hits}/{len(blocks)} blocks")
            return cached_blocks
        
        return None
    
    def _check_cache_for_single_block(
        self, 
        block: SubtitleBlock,
        context: TranslationContext
    ) -> Optional[SubtitleBlock]:
        """Check cache for single block"""
        if not self.cache_service:
            return None
        
        cache_key = self._generate_block_cache_key(block, context)
        cached_translation = self.cache_service.get(cache_key)
        
        if cached_translation:
            cached_block = block.clone()
            cached_block.translated_text = cached_translation
            return cached_block
        
        return None
    
    def _cache_translation_results(
        self, 
        original_blocks: List[SubtitleBlock],
        translated_blocks: List[Optional[SubtitleBlock]],
        context: TranslationContext
    ):
        """Cache translation results"""
        if not self.cache_service:
            return
        
        # Cache individual successful translations
        for orig_block, trans_block in zip(original_blocks, translated_blocks):
            if trans_block and trans_block.translated_text:
                self._cache_single_block(orig_block, trans_block, context)
        
        # Cache entire file if all blocks successful
        if all(block is not None for block in translated_blocks):
            file_cache_key = self._generate_file_cache_key(original_blocks, context)
            serialized_blocks = self._serialize_blocks_for_cache(translated_blocks)
            self.cache_service.set(file_cache_key, serialized_blocks)
            logger.debug("Cached complete file translation")
    
    def _cache_single_block(
        self, 
        original_block: SubtitleBlock,
        translated_block: SubtitleBlock,
        context: TranslationContext
    ):
        """Cache single block translation"""
        if not self.cache_service or not translated_block.translated_text:
            return
        
        cache_key = self._generate_block_cache_key(original_block, context)
        self.cache_service.set(cache_key, translated_block.translated_text)
    
    def _generate_block_cache_key(self, block: SubtitleBlock, context: TranslationContext) -> str:
        """Generate cache key for single block"""
        if not self.cache_service:
            return ""
        
        key_components = context.get_cache_key_components()
        key_components['text'] = block.text
        key_components['block_number'] = str(block.number)
        
        return self.cache_service.generate_key(**key_components)
    
    def _generate_file_cache_key(self, blocks: List[SubtitleBlock], context: TranslationContext) -> str:
        """Generate cache key for entire file"""
        if not self.cache_service:
            return ""
        
        import hashlib
        
        # Create hash of all block texts
        all_text = '|'.join(block.text for block in blocks)
        text_hash = hashlib.md5(all_text.encode()).hexdigest()[:8]
        
        key_components = context.get_cache_key_components()
        key_components['file_hash'] = text_hash
        key_components['block_count'] = str(len(blocks))
        
        return self.cache_service.generate_key(**key_components)
    
    def _serialize_blocks_for_cache(self, blocks: List[Optional[SubtitleBlock]]) -> str:
        """Serialize blocks for caching"""
        import json
        
        serialized = []
        for block in blocks:
            if block:
                serialized.append({
                    'number': block.number,
                    'start_time': block.start_time,
                    'end_time': block.end_time,
                    'text': block.text,
                    'translated_text': block.translated_text
                })
            else:
                serialized.append(None)
        
        return json.dumps(serialized)
    
    def _deserialize_cached_blocks(self, cached_data: str) -> List[Optional[SubtitleBlock]]:
        """Deserialize blocks from cache"""
        import json
        
        try:
            data = json.loads(cached_data)
            blocks = []
            
            for item in data:
                if item:
                    block = SubtitleBlock(
                        number=item['number'],
                        start_time=item['start_time'],
                        end_time=item['end_time'],
                        text=item['text'],
                        translated_text=item.get('translated_text')
                    )
                    blocks.append(block)
                else:
                    blocks.append(None)
            
            return blocks
            
        except (json.JSONDecodeError, KeyError) as e:
            logger.error(f"Failed to deserialize cached blocks: {e}")
            return []
        except ValueError as e:
            logger.error(f"Failed to create SubtitleBlock from cached data: {e}")
            return []
