"""
Translation strategies package
"""

from .simple_translation import SimpleTranslationStrategy
from .context_aware_translation import ContextAwareTranslationStrategy

__all__ = [
    'SimpleTranslationStrategy',
    'ContextAwareTranslationStrategy'
]
