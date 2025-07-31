"""
Legacy Adapter - Giúp migration từ old translator sang Clean Architecture
Provides drop-in replacement cho existing code
"""

import logging
from src.integration import LegacyTranslatorAdapter as NewLegacyAdapter

logger = logging.getLogger(__name__)

# Drop-in replacement cho SubtitleTranslator cũ
SubtitleTranslator = NewLegacyAdapter

# Migration helper message
def show_migration_notice():
    """Show migration notice for developers"""
    print("""
    📢 MIGRATION NOTICE:
    
    Bạn đang dùng legacy adapter cho SubtitleTranslator.
    Code hiện tại sẽ hoạt động bình thường, nhưng nên migrate sang Clean Architecture mới:
    
    OLD:
    from src.translator.subtitle import SubtitleTranslator
    
    NEW: 
    from src.integration import TranslationFacade
    
    Hoặc dùng legacy adapter:
    from src.integration import LegacyTranslatorAdapter as SubtitleTranslator
    
    Benefits của Clean Architecture:
    ✅ Context-aware translation (chất lượng dịch tốt hơn)
    ✅ Better caching & performance
    ✅ More reliable error handling  
    ✅ Easier to extend & maintain
    
    📖 Xem MIGRATION_PLAN.md để biết chi tiết
    """)

# Auto-show notice when imported (chỉ 1 lần)
_migration_notice_shown = False

def _show_notice_once():
    global _migration_notice_shown
    if not _migration_notice_shown:
        logger.info("Using legacy adapter for SubtitleTranslator - see MIGRATION_PLAN.md")
        _migration_notice_shown = True

_show_notice_once()

__all__ = ['SubtitleTranslator', 'show_migration_notice']
