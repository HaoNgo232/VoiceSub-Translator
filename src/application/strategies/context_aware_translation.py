"""
Context-Aware Translation Strategy
Implements smart translation using surrounding context for better accuracy
"""

import logging
import concurrent.futures
from typing import List, Optional, Dict, Tuple
from ...core import SubtitleBlock, TranslationContext, TranslationStrategy, ProviderService

logger = logging.getLogger(__name__)


class ContextAwareTranslationStrategy(TranslationStrategy):
    """
    Strategy for context-aware translation
    
    Principle: Strategy Pattern + Domain-Driven Design
    - Uses surrounding subtitle blocks as context
    - Improves translation accuracy and consistency
    - Maintains terminology consistency across blocks
    """
    
    def get_strategy_name(self) -> str:
        return "context_aware"
    
    def translate_blocks(
        self, 
        blocks: List[SubtitleBlock], 
        context: TranslationContext,
        provider_service: ProviderService
    ) -> List[Optional[SubtitleBlock]]:
        """
        Dịch blocks với context awareness
        
        Key Innovation: Sử dụng context xung quanh để cải thiện chất lượng dịch
        
        Args:
            blocks: Danh sách subtitle blocks
            context: Translation context
            provider_service: Service để gọi providers
            
        Returns:
            List các blocks đã dịch với quality tốt hơn
        """
        logger.info(f"Starting context-aware translation for {len(blocks)} blocks")
        logger.info(f"Using context window size: {context.effective_context_size}")
        
        if not context.enable_parallel:
            return self._translate_sequential_with_context(blocks, context, provider_service)
        else:
            return self._translate_parallel_with_context(blocks, context, provider_service)
    
    def _translate_sequential_with_context(
        self, 
        blocks: List[SubtitleBlock], 
        context: TranslationContext,
        provider_service: ProviderService
    ) -> List[Optional[SubtitleBlock]]:
        """Dịch tuần tự với context"""
        translated_blocks = []
        
        for i, block in enumerate(blocks):
            logger.info(f"Translating block {i+1}/{len(blocks)} with context")
            
            # Build context for current block
            block_context = self._build_context_for_block(
                blocks, i, context.effective_context_size, translated_blocks
            )
            
            translated_block = self._translate_single_block_with_context(
                block, block_context, context, provider_service
            )
            translated_blocks.append(translated_block)
        
        return translated_blocks
    
    def _translate_parallel_with_context(
        self, 
        blocks: List[SubtitleBlock], 
        context: TranslationContext,
        provider_service: ProviderService
    ) -> List[Optional[SubtitleBlock]]:
        """
        Parallel translation với context
        
        Challenge: Context dependency makes pure parallel processing complex
        Solution: Process in overlapping batches
        """
        logger.info("Using batch-parallel approach for context-aware translation")
        
        batch_size = min(context.batch_size, len(blocks))
        translated_blocks = [None] * len(blocks)
        
        # Process in batches to balance context and parallelism
        for batch_start in range(0, len(blocks), batch_size):
            batch_end = min(batch_start + batch_size, len(blocks))
            batch_blocks = blocks[batch_start:batch_end]
            
            logger.info(f"Processing batch {batch_start//batch_size + 1}: blocks {batch_start+1}-{batch_end}")
            
            # Translate batch with context
            batch_results = self._translate_batch_with_context(
                batch_blocks, batch_start, blocks, context, provider_service, translated_blocks
            )
            
            # Store results
            for i, result in enumerate(batch_results):
                translated_blocks[batch_start + i] = result
        
        return translated_blocks
    
    def _translate_batch_with_context(
        self,
        batch_blocks: List[SubtitleBlock],
        batch_start_index: int,
        all_blocks: List[SubtitleBlock],
        context: TranslationContext,
        provider_service: ProviderService,
        previous_translations: List[Optional[SubtitleBlock]]
    ) -> List[Optional[SubtitleBlock]]:
        """Translate a batch of blocks with context"""
        
        def translate_block_wrapper(batch_index: int, block: SubtitleBlock):
            try:
                global_index = batch_start_index + batch_index
                
                # Build context using both original and previously translated blocks
                block_context = self._build_context_for_block(
                    all_blocks, global_index, context.effective_context_size, 
                    previous_translations, include_previous_translations=True
                )
                
                return batch_index, self._translate_single_block_with_context(
                    block, block_context, context, provider_service
                )
            except Exception as e:
                logger.error(f"Error translating block {batch_start_index + batch_index + 1}: {str(e)}")
                return batch_index, None
        
        batch_results = [None] * len(batch_blocks)
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=min(context.max_workers, len(batch_blocks))) as executor:
            future_to_index = {
                executor.submit(translate_block_wrapper, i, block): i 
                for i, block in enumerate(batch_blocks)
            }
            
            for future in concurrent.futures.as_completed(future_to_index):
                try:
                    batch_index, translated_block = future.result()
                    batch_results[batch_index] = translated_block
                except Exception as e:
                    batch_index = future_to_index[future]
                    logger.error(f"Exception in batch translation task {batch_index}: {str(e)}")
                    batch_results[batch_index] = None
        
        return batch_results
    
    def _build_context_for_block(
        self, 
        all_blocks: List[SubtitleBlock], 
        target_index: int, 
        window_size: int,
        previous_translations: List[Optional[SubtitleBlock]] = None,
        include_previous_translations: bool = False
    ) -> Dict[str, any]:
        """
        Build context dictionary for a specific block
        
        Args:
            all_blocks: All subtitle blocks
            target_index: Index of target block
            window_size: Size of context window
            previous_translations: Previously translated blocks
            include_previous_translations: Whether to include previous translations
            
        Returns:
            Context dictionary with surrounding blocks
        """
        context_data = {
            'previous_blocks': [],
            'following_blocks': [],
            'target_block': all_blocks[target_index],
            'previous_translations': []
        }
        
        # Get previous blocks
        start_idx = max(0, target_index - window_size)
        for i in range(start_idx, target_index):
            context_data['previous_blocks'].append({
                'text': all_blocks[i].text,
                'position': i - target_index  # Relative position
            })
        
        # Get following blocks  
        end_idx = min(len(all_blocks), target_index + window_size + 1)
        for i in range(target_index + 1, end_idx):
            context_data['following_blocks'].append({
                'text': all_blocks[i].text,
                'position': i - target_index  # Relative position
            })
        
        # Include previous translations if available
        if include_previous_translations and previous_translations:
            for i in range(start_idx, target_index):
                if i < len(previous_translations) and previous_translations[i]:
                    context_data['previous_translations'].append({
                        'original': all_blocks[i].text,
                        'translated': previous_translations[i].translated_text,
                        'position': i - target_index
                    })
        
        return context_data
    
    def _translate_single_block_with_context(
        self, 
        block: SubtitleBlock, 
        block_context: Dict,
        translation_context: TranslationContext,
        provider_service: ProviderService
    ) -> Optional[SubtitleBlock]:
        """
        Translate single block using context
        
        Key Feature: Smart prompt construction with context
        """
        if block.is_empty():
            translated_block = block.clone()
            translated_block.translated_text = ""
            return translated_block
        
        try:
            # Build context-aware prompt
            context_prompt = self._build_context_prompt(
                block, block_context, translation_context
            )
            
            # Translate with context
            translated_text = provider_service.translate_text(
                text=context_prompt,
                target_lang=translation_context.target_language,
                provider_name=translation_context.provider_name
            )
            
            if translated_text:
                # Extract just the translation (remove context)
                clean_translation = self._extract_translation_from_response(
                    translated_text, block.text
                )
                
                translated_block = block.clone()
                translated_block.translated_text = clean_translation
                return translated_block
            else:
                logger.warning(f"Failed to translate block {block.number} with context")
                return None
                
        except Exception as e:
            logger.error(f"Error in context-aware translation for block {block.number}: {str(e)}")
            
            if translation_context.retry_failed:
                logger.info(f"Retrying block {block.number} with simplified context")
                return self._retry_with_simplified_context(
                    block, block_context, translation_context, provider_service
                )
            
            return None
    
    def _build_context_prompt(
        self, 
        target_block: SubtitleBlock, 
        block_context: Dict,
        translation_context: TranslationContext
    ) -> str:
        """
        Build smart prompt with context information
        
        Key Innovation: Context-aware prompt engineering
        """
        # Get base template
        template = translation_context.get_prompt_template()
        
        # Build context string
        context_parts = []
        
        # Add previous blocks
        if block_context['previous_blocks']:
            context_parts.append("Previous subtitles:")
            for ctx_block in block_context['previous_blocks'][-2:]:  # Last 2 blocks
                context_parts.append(f"  {ctx_block['text']}")
        
        # Add following blocks  
        if block_context['following_blocks']:
            context_parts.append("Following subtitles:")
            for ctx_block in block_context['following_blocks'][:2]:  # Next 2 blocks
                context_parts.append(f"  {ctx_block['text']}")
        
        # Add previous translations for consistency
        if block_context['previous_translations']:
            context_parts.append("Recent translations:")
            for trans in block_context['previous_translations'][-1:]:  # Last translation
                context_parts.append(f"  '{trans['original']}' → '{trans['translated']}'")
        
        context_string = '\n'.join(context_parts)
        
        # Format final prompt
        if '{context}' in template:
            return template.format(
                context=context_string,
                text=target_block.text
            )
        else:
            # Fallback for templates without context placeholder
            return f"{context_string}\n\n{template.format(text=target_block.text)}"
    
    def _extract_translation_from_response(self, response: str, original_text: str) -> str:
        """
        Extract clean translation from AI response
        
        Handle cases where AI includes extra context or explanations
        """
        # Split response into lines
        lines = response.strip().split('\n')
        
        # Look for the most likely translation line
        candidates = []
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            # Skip lines that look like context or instructions
            if any(skip_word in line.lower() for skip_word in [
                'context', 'translate', 'following', 'previous', 'reference'
            ]):
                continue
            
            # Skip lines that are too similar to original
            if line == original_text:
                continue
                
            candidates.append(line)
        
        if candidates:
            # Return the first good candidate
            return candidates[0]
        else:
            # Fallback: return the whole response cleaned up
            return response.strip()
    
    def _retry_with_simplified_context(
        self, 
        block: SubtitleBlock, 
        block_context: Dict,
        translation_context: TranslationContext,
        provider_service: ProviderService
    ) -> Optional[SubtitleBlock]:
        """Retry with simpler context if full context fails"""
        try:
            # Simplify context to just the immediate neighbors
            simplified_context = []
            
            if block_context['previous_blocks']:
                simplified_context.append(f"Previous: {block_context['previous_blocks'][-1]['text']}")
            
            if block_context['following_blocks']:
                simplified_context.append(f"Next: {block_context['following_blocks'][0]['text']}")
            
            simple_prompt = f"""Translate to {translation_context.target_language}:

Context: {' | '.join(simplified_context)}

Text: {block.text}"""
            
            translated_text = provider_service.translate_text(
                text=simple_prompt,
                target_lang=translation_context.target_language,
                provider_name=translation_context.provider_name
            )
            
            if translated_text:
                clean_translation = self._extract_translation_from_response(
                    translated_text, block.text
                )
                
                translated_block = block.clone()
                translated_block.translated_text = clean_translation
                return translated_block
            
        except Exception as e:
            logger.error(f"Simplified context retry also failed for block {block.number}: {str(e)}")
        
        return None
