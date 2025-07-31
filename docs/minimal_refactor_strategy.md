# Minimal Refactor for Context-Aware Translation 🎯

## Quick Strategy Pattern Implementation

### 1. Create Translation Strategy Interface
```python
# src/translator/strategies/__init__.py
from abc import ABC, abstractmethod
from typing import List, Optional, Dict

class TranslationStrategy(ABC):
    """Interface for different translation strategies"""
    
    @abstractmethod
    def translate_blocks(
        self, 
        blocks: List[str], 
        target_lang: str, 
        service: str,
        translator_service,
        **kwargs
    ) -> List[Optional[str]]:
        """Translate subtitle blocks using specific strategy"""
        pass

# src/translator/strategies/simple_strategy.py  
class SimpleTranslationStrategy(TranslationStrategy):
    """Current block-by-block translation"""
    
    def translate_blocks(self, blocks, target_lang, service, translator_service, **kwargs):
        # Move current parallel translation logic here
        pass

# src/translator/strategies/context_aware_strategy.py
class ContextAwareTranslationStrategy(TranslationStrategy):
    """Context-aware translation with surrounding blocks"""
    
    def __init__(self, window_size=3):
        self.window_size = window_size
    
    def translate_blocks(self, blocks, target_lang, service, translator_service, **kwargs):
        # Implement context-aware logic here
        pass
```

### 2. Update SubtitleTranslator
```python
# src/translator/subtitle.py
class SubtitleTranslator:
    def __init__(self, ..., translation_strategy=None):
        # ... existing init ...
        self.translation_strategy = translation_strategy or SimpleTranslationStrategy()
    
    def set_translation_strategy(self, strategy: TranslationStrategy):
        """Change translation strategy at runtime"""
        self.translation_strategy = strategy
    
    def _translate_blocks_parallel(self, blocks, target_lang, service, max_workers, stats):
        """Delegate to strategy"""
        return self.translation_strategy.translate_blocks(
            blocks, target_lang, service, self.translator_service,
            max_workers=max_workers, stats=stats
        )
```

This approach:
- ✅ Minimal changes to existing code
- ✅ Easy to add context-aware strategy  
- ✅ Can implement in 1-2 days
- ✅ Backward compatible

Ready to proceed with this approach?
