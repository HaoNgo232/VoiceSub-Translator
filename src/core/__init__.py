"""
Core domain entities and interfaces
"""

# Entities
from .entities.subtitle_block import SubtitleBlock
from .entities.translation_context import TranslationContext, TranslationMode

# Interfaces
from .interfaces import (
    TranslationStrategy,
    ProviderService, 
    CacheService,
    TranscriptionService
)

__all__ = [
    # Entities
    'SubtitleBlock',
    'TranslationContext', 
    'TranslationMode',
    
    # Interfaces
    'TranslationStrategy',
    'ProviderService',
    'CacheService', 
    'TranscriptionService'
]
