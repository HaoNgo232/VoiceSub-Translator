"""
Simple Translation Strategy - Current block-by-block approach
Implements Strategy Pattern for translation methods
"""

import logging
import concurrent.futures
from typing import List, Optional, Dict
from ...core import SubtitleBlock, TranslationContext, TranslationStrategy, ProviderService

logger = logging.getLogger(__name__)


class SimpleTranslationStrategy(TranslationStrategy):
    """
    Strategy for simple block-by-block translation
    
    Principle: Strategy Pattern + Single Responsibility Principle
    - Focuses solely on simple translation logic
    - No context awareness, each block translated independently
    """
    
    def get_strategy_name(self) -> str:
        return "simple"
    
    def translate_blocks(
        self, 
        blocks: List[SubtitleBlock], 
        context: TranslationContext,
        provider_service: ProviderService
    ) -> List[Optional[SubtitleBlock]]:
        """
        Dịch từng block riêng lẻ không có context
        
        Args:
            blocks: Danh sách subtitle blocks
            context: Translation context
            provider_service: Service để gọi providers
            
        Returns:
            List các blocks đã dịch
        """
        logger.info(f"Starting simple translation for {len(blocks)} blocks")
        
        if not context.enable_parallel or context.max_workers == 1:
            return self._translate_sequential(blocks, context, provider_service)
        else:
            return self._translate_parallel(blocks, context, provider_service)
    
    def _translate_sequential(
        self, 
        blocks: List[SubtitleBlock], 
        context: TranslationContext,
        provider_service: ProviderService
    ) -> List[Optional[SubtitleBlock]]:
        """Dịch tuần tự từng block"""
        translated_blocks = []
        
        for i, block in enumerate(blocks):
            logger.info(f"Translating block {i+1}/{len(blocks)}")
            
            translated_block = self._translate_single_block(
                block, context, provider_service
            )
            translated_blocks.append(translated_block)
        
        return translated_blocks
    
    def _translate_parallel(
        self, 
        blocks: List[SubtitleBlock], 
        context: TranslationContext,
        provider_service: ProviderService
    ) -> List[Optional[SubtitleBlock]]:
        """
        Dịch parallel với ThreadPoolExecutor
        
        Principle: Concurrent processing for better performance
        """
        translated_blocks = [None] * len(blocks)
        
        def translate_block_wrapper(index: int, block: SubtitleBlock):
            """Wrapper function for parallel execution"""
            try:
                return index, self._translate_single_block(block, context, provider_service)
            except Exception as e:
                logger.error(f"Error translating block {index + 1}: {str(e)}")
                return index, None
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=context.max_workers) as executor:
            # Submit all translation tasks
            future_to_index = {
                executor.submit(translate_block_wrapper, i, block): i 
                for i, block in enumerate(blocks)
            }
            
            # Collect results as they complete
            for future in concurrent.futures.as_completed(future_to_index):
                try:
                    index, translated_block = future.result()
                    translated_blocks[index] = translated_block
                    
                    # Log progress
                    completed = sum(1 for b in translated_blocks if b is not None)
                    logger.info(f"Completed {completed}/{len(blocks)} blocks")
                    
                except Exception as e:
                    index = future_to_index[future]
                    logger.error(f"Exception in translation task {index}: {str(e)}")
                    translated_blocks[index] = None
        
        return translated_blocks
    
    def _translate_single_block(
        self, 
        block: SubtitleBlock, 
        context: TranslationContext,
        provider_service: ProviderService
    ) -> Optional[SubtitleBlock]:
        """
        Dịch một block riêng lẻ
        
        Args:
            block: Subtitle block cần dịch
            context: Translation context
            provider_service: Provider service
            
        Returns:
            Block đã dịch hoặc None nếu thất bại
        """
        if block.is_empty():
            # Return empty block as-is
            translated_block = block.clone()
            translated_block.translated_text = ""
            return translated_block
        
        try:
            # Translate text using provider service
            translated_text = provider_service.translate_text(
                text=block.text,
                target_lang=context.target_language,
                provider_name=context.provider_name
            )
            
            if translated_text:
                translated_block = block.clone()
                translated_block.translated_text = translated_text
                return translated_block
            else:
                logger.warning(f"Failed to translate block {block.number}")
                return None
                
        except Exception as e:
            logger.error(f"Error translating block {block.number}: {str(e)}")
            
            if context.retry_failed:
                logger.info(f"Retrying block {block.number}")
                return self._retry_translation(block, context, provider_service)
            
            return None
    
    def _retry_translation(
        self, 
        block: SubtitleBlock, 
        context: TranslationContext,
        provider_service: ProviderService
    ) -> Optional[SubtitleBlock]:
        """
        Retry translation với exponential backoff
        
        Args:
            block: Block cần retry
            context: Translation context
            provider_service: Provider service
            
        Returns:
            Block đã dịch hoặc None nếu thất bại
        """
        import time
        
        for attempt in range(context.max_retries):
            try:
                logger.info(f"Retry attempt {attempt + 1}/{context.max_retries} for block {block.number}")
                
                # Exponential backoff
                if attempt > 0:
                    wait_time = 2 ** attempt
                    logger.info(f"Waiting {wait_time}s before retry")
                    time.sleep(wait_time)
                
                translated_text = provider_service.translate_text(
                    text=block.text,
                    target_lang=context.target_language,
                    provider_name=context.provider_name
                )
                
                if translated_text:
                    translated_block = block.clone()
                    translated_block.translated_text = translated_text
                    return translated_block
                    
            except Exception as e:
                logger.warning(f"Retry {attempt + 1} failed for block {block.number}: {str(e)}")
                continue
        
        logger.error(f"All retry attempts failed for block {block.number}")
        return None
