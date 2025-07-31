"""
Translation context entity - Chứa thông tin context cho việc dịch thuật
"""

from dataclasses import dataclass
from typing import Optional, Dict, Any, List
from enum import Enum


class TranslationMode(Enum):
    """Các chế độ dịch thuật"""
    SIMPLE = "simple"                    # Dịch từng block riêng lẻ
    CONTEXT_AWARE = "context_aware"      # Dịch với context xung quanh
    BATCH = "batch"                      # Dịch theo batch
    ADAPTIVE = "adaptive"                # Tự động chọn strategy phù hợp


@dataclass
class TranslationContext:
    """
    Context object chứa tất cả thông tin cần thiết cho việc dịch thuật
    
    Principle: Data Transfer Object (DTO) Pattern
    - Encapsulate tất cả parameters cần thiết
    - Giảm parameter passing complexity
    """
    
    # Core translation parameters
    target_language: str
    source_language: Optional[str] = None
    provider_name: Optional[str] = None
    
    # Translation mode và settings
    mode: TranslationMode = TranslationMode.SIMPLE
    max_workers: int = 10
    
    # Context-aware specific settings
    context_window_size: int = 3  # Số blocks xung quanh để làm context
    
    # Quality settings
    use_cache: bool = True
    retry_failed: bool = True
    max_retries: int = 3
    
    # Performance settings
    batch_size: int = 5
    enable_parallel: bool = True
    
    # Advanced options
    preserve_formatting: bool = True
    preserve_technical_terms: bool = True
    custom_prompt_template: Optional[str] = None
    
    # Metadata
    user_preferences: Dict[str, Any] = None
    
    def __post_init__(self):
        """Validate and set defaults"""
        if self.user_preferences is None:
            self.user_preferences = {}
        
        # Validate language codes
        if len(self.target_language) < 2:
            raise ValueError(f"Invalid target_language: {self.target_language}")
        
        # Validate numeric parameters
        if self.context_window_size < 0:
            raise ValueError("context_window_size must be >= 0")
        
        if self.max_workers < 1:
            raise ValueError("max_workers must be >= 1")
        
        if self.batch_size < 1:
            raise ValueError("batch_size must be >= 1")
    
    @property
    def is_context_aware(self) -> bool:
        """Kiểm tra xem có dùng context-aware mode không"""
        return self.mode in [TranslationMode.CONTEXT_AWARE, TranslationMode.ADAPTIVE]
    
    @property
    def effective_context_size(self) -> int:
        """Trả về context size hiệu quả"""
        if not self.is_context_aware:
            return 0
        return self.context_window_size
    
    def get_prompt_template(self) -> str:
        """
        Lấy prompt template phù hợp với mode
        
        Returns:
            Prompt template string
        """
        if self.custom_prompt_template:
            return self.custom_prompt_template
        
        base_template = f"""Translate the following text to {self.target_language}.
IMPORTANT INSTRUCTIONS:
1. Only return the translated text, without any explanations or notes
2. Keep the original format and timing information
3. Keep technical terms and IT concepts in English (e.g. API, CPU, RAM, etc.)
4. Keep certification names in English (e.g. CISP, CISM, etc.)
5. Keep company names in English
6. Keep product names in English
7. Keep programming languages and frameworks in English
8. Keep file extensions in English
9. Keep commands and code snippets in English

Text to translate:
{{text}}"""

        if self.is_context_aware:
            context_template = f"""Translate the following text to {self.target_language}.
IMPORTANT INSTRUCTIONS:
1. Only return the translated text, without any explanations or notes
2. Keep the original format and timing information
3. Keep technical terms and IT concepts in English
4. Use the context below for consistency and accuracy
5. Maintain terminology consistency throughout

Context (for reference only, don't translate):
{{context}}

Translate this specific text to {self.target_language}:
{{text}}"""
            return context_template
        
        return base_template
    
    def get_cache_key_components(self) -> Dict[str, str]:
        """
        Lấy components để tạo cache key
        
        Returns:
            Dict chứa các thành phần cho cache key
        """
        return {
            'target_lang': self.target_language,
            'source_lang': self.source_language or 'auto',
            'provider': self.provider_name or 'auto',
            'mode': self.mode.value,
            'preserve_formatting': str(self.preserve_formatting),
            'preserve_technical': str(self.preserve_technical_terms)
        }
    
    def clone(self, **overrides) -> 'TranslationContext':
        """
        Tạo bản copy với một số thay đổi
        
        Args:
            **overrides: Các fields muốn override
            
        Returns:
            TranslationContext mới
        """
        data = {
            'target_language': self.target_language,
            'source_language': self.source_language,
            'provider_name': self.provider_name,
            'mode': self.mode,
            'max_workers': self.max_workers,
            'context_window_size': self.context_window_size,
            'use_cache': self.use_cache,
            'retry_failed': self.retry_failed,
            'max_retries': self.max_retries,
            'batch_size': self.batch_size,
            'enable_parallel': self.enable_parallel,
            'preserve_formatting': self.preserve_formatting,
            'preserve_technical_terms': self.preserve_technical_terms,
            'custom_prompt_template': self.custom_prompt_template,
            'user_preferences': self.user_preferences.copy()
        }
        
        # Apply overrides
        data.update(overrides)
        
        return TranslationContext(**data)
