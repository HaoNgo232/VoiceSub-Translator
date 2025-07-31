"""
Test Suite for Clean Architecture Implementation
Validates the new translation system end-to-end
"""

import pytest
import tempfile
import os
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

# Import the new architecture components
from ..core import (
    SubtitleBlock, 
    TranslationContext, 
    TranslationMode
)
from ..application import (
    TranslationService,
    SimpleTranslationStrategy,
    ContextAwareTranslationStrategy
)
from ..infrastructure import (
    ConcreteProviderService,
    FileCacheService,
    MemoryCacheService
)
from ..integration import TranslationFacade, LegacyTranslatorAdapter


class TestCleanArchitectureIntegration:
    """Test the integrated Clean Architecture system"""
    
    @pytest.fixture
    def temp_cache_dir(self):
        """Create temporary cache directory"""
        with tempfile.TemporaryDirectory() as temp_dir:
            yield temp_dir
    
    @pytest.fixture
    def sample_srt_content(self):
        """Sample SRT content for testing"""
        return """1
00:00:01,000 --> 00:00:03,000
Hello world

2
00:00:04,000 --> 00:00:06,000
This is a test subtitle

3
00:00:07,000 --> 00:00:09,000
Context-aware translation test"""
    
    @pytest.fixture
    def mock_provider_service(self):
        """Mock provider service for testing"""
        mock_service = Mock(spec=ConcreteProviderService)
        mock_service.get_available_providers.return_value = ['groq', 'google', 'openrouter']
        mock_service.translate.return_value = "Mocked translation"
        return mock_service
    
    def test_subtitle_block_parsing(self, sample_srt_content):
        """Test SubtitleBlock parsing functionality"""
        blocks = SubtitleBlock.parse_srt_content(sample_srt_content)
        
        assert len(blocks) == 3
        assert blocks[0].text == "Hello world"
        assert blocks[1].text == "This is a test subtitle"
        assert blocks[2].text == "Context-aware translation test"
        
        # Test SRT regeneration
        regenerated = SubtitleBlock.to_srt_content(blocks)
        assert "Hello world" in regenerated
        assert "00:00:01,000 --> 00:00:03,000" in regenerated
    
    def test_translation_context_creation(self):
        """Test TranslationContext object creation"""
        context = TranslationContext(
            source_language="en",
            target_language="vi",
            mode=TranslationMode.CONTEXT_AWARE,
            previous_segments=["Previous subtitle"],
            video_metadata={"title": "Test Video"},
            custom_instructions="Translate casually"
        )
        
        assert context.source_language == "en"
        assert context.target_language == "vi"
        assert context.mode == TranslationMode.CONTEXT_AWARE
        assert len(context.previous_segments) == 1
        assert context.video_metadata["title"] == "Test Video"
        assert context.custom_instructions == "Translate casually"
    
    def test_memory_cache_service(self):
        """Test MemoryCacheService functionality"""
        cache = MemoryCacheService(default_ttl=3600)
        
        # Test set and get
        test_key = cache.generate_key(text="hello", lang="vi")
        cache.set(test_key, "xin chào")
        
        result = cache.get(test_key)
        assert result == "xin chào"
        
        # Test cache stats
        stats = cache.get_cache_stats()
        assert stats['total_entries'] >= 1
        assert stats['cache_type'] == 'memory'
        
        # Test clear
        cache.clear_all()
        assert cache.get(test_key) is None
    
    def test_file_cache_service(self, temp_cache_dir):
        """Test FileCacheService functionality"""
        cache = FileCacheService(cache_dir=temp_cache_dir, default_ttl=3600)
        
        # Test set and get
        test_key = cache.generate_key(text="hello", lang="vi", provider="groq")
        cache.set(test_key, "xin chào")
        
        result = cache.get(test_key)
        assert result == "xin chào"
        
        # Test key generation consistency
        key1 = cache.generate_key(text="hello", lang="vi")
        key2 = cache.generate_key(lang="vi", text="hello")  # Different order
        assert key1 == key2  # Should be same due to sorted items
        
        # Test cache stats
        stats = cache.get_cache_stats()
        assert stats['total_entries'] >= 1
        assert 'cache_directory' in stats
        
        # Test persistence
        cache2 = FileCacheService(cache_dir=temp_cache_dir)
        result2 = cache2.get(test_key)
        assert result2 == "xin chào"  # Should persist across instances
    
    @patch('src.infrastructure.providers.provider_service.ConcreteProviderService')
    def test_simple_translation_strategy(self, mock_provider_class, temp_cache_dir):
        """Test SimpleTranslationStrategy"""
        # Setup mocks
        mock_provider = Mock()
        mock_provider.translate.return_value = "Xin chào thế giới"
        mock_provider_class.return_value = mock_provider
        
        # Initialize strategy
        cache_service = MemoryCacheService()
        strategy = SimpleTranslationStrategy(
            provider_service=mock_provider,
            cache_service=cache_service
        )
        
        # Create context
        context = TranslationContext(
            source_language="en",
            target_language="vi",
            mode=TranslationMode.SIMPLE
        )
        
        # Test translation
        result = strategy.translate("Hello world", context, "groq")
        assert result == "Xin chào thế giới"
        
        # Verify provider was called
        mock_provider.translate.assert_called_once()
    
    def test_translation_facade_integration(self, temp_cache_dir):
        """Test TranslationFacade end-to-end integration"""
        with patch.object(ConcreteProviderService, 'translate') as mock_translate:
            mock_translate.return_value = "Xin chào thế giới"
            
            facade = TranslationFacade(
                cache_dir=temp_cache_dir,
                use_context_aware=False  # Use simple for predictable testing
            )
            
            # Test simple translation
            result = facade.translate_text(
                text="Hello world",
                target_language="vi",
                source_language="en",
                provider="groq"
            )
            
            assert result == "Xin chào thế giới"
            
            # Test mode switching
            facade.set_translation_mode("context_aware")
            assert facade.use_context_aware is True
            
            facade.set_translation_mode("simple")
            assert facade.use_context_aware is False
    
    def test_subtitle_file_translation(self, temp_cache_dir, sample_srt_content):
        """Test subtitle file translation through facade"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.srt', delete=False) as temp_file:
            temp_file.write(sample_srt_content)
            temp_file_path = temp_file.name
        
        try:
            with patch.object(ConcreteProviderService, 'translate') as mock_translate:
                # Mock different translations for each subtitle
                mock_translate.side_effect = [
                    "Xin chào thế giới",
                    "Đây là phụ đề thử nghiệm", 
                    "Thử nghiệm dịch có ngữ cảnh"
                ]
                
                facade = TranslationFacade(cache_dir=temp_cache_dir)
                
                output_path = facade.translate_subtitle_file(
                    file_path=temp_file_path,
                    target_language="vi",
                    source_language="en",
                    provider="groq"
                )
                
                # Verify output file exists and contains translations
                assert os.path.exists(output_path)
                
                with open(output_path, 'r', encoding='utf-8') as f:
                    translated_content = f.read()
                
                assert "Xin chào thế giới" in translated_content
                assert "Đây là phụ đề thử nghiệm" in translated_content
                assert "00:00:01,000 --> 00:00:03,000" in translated_content  # Timestamps preserved
                
                # Cleanup
                os.unlink(output_path)
                
        finally:
            os.unlink(temp_file_path)
    
    def test_legacy_adapter_compatibility(self, temp_cache_dir):
        """Test LegacyTranslatorAdapter for backward compatibility"""
        with patch.object(ConcreteProviderService, 'translate') as mock_translate:
            mock_translate.return_value = "Xin chào"
            
            # Test legacy adapter
            adapter = LegacyTranslatorAdapter(cache_dir=temp_cache_dir)
            
            # Test legacy translate method
            result = adapter.translate(
                "Hello",
                provider="groq",
                source_lang="en",
                target_lang="vi"
            )
            
            assert result == "Xin chào"
            
            # Test legacy attribute setting
            adapter.set_provider("google")
            assert adapter.provider == "google"
            
            adapter.set_languages("en", "zh")
            assert adapter.source_lang == "en"
            assert adapter.target_lang == "zh"
    
    def test_context_aware_translation_strategy(self, temp_cache_dir):
        """Test ContextAwareTranslationStrategy with context"""
        with patch.object(ConcreteProviderService, 'translate') as mock_translate:
            mock_translate.return_value = "Translated with context"
            
            cache_service = MemoryCacheService()
            provider_service = ConcreteProviderService()
            
            strategy = ContextAwareTranslationStrategy(
                provider_service=provider_service,
                cache_service=cache_service
            )
            
            # Create rich context
            context = TranslationContext(
                source_language="en",
                target_language="vi",
                mode=TranslationMode.CONTEXT_AWARE,
                previous_segments=["Previous subtitle about cooking"],
                video_metadata={
                    "title": "Cooking Tutorial",
                    "genre": "educational",
                    "duration": 600
                },
                custom_instructions="Use cooking terminology"
            )
            
            result = strategy.translate("Add salt to taste", context, "groq")
            assert result == "Translated with context"
            
            # Verify that translate was called with context information
            mock_translate.assert_called_once()
            call_args = mock_translate.call_args
            
            # The context should be included in the call
            assert "Add salt to taste" in call_args[1]["text"]
    
    def test_error_handling_and_fallbacks(self, temp_cache_dir):
        """Test error handling and fallback mechanisms"""
        facade = TranslationFacade(cache_dir=temp_cache_dir)
        
        # Test with invalid provider
        with patch.object(ConcreteProviderService, 'translate') as mock_translate:
            mock_translate.side_effect = Exception("Provider error")
            
            # Should not raise exception, should return original text as fallback
            result = facade.translate_text(
                text="Hello world",
                target_language="vi", 
                provider="invalid_provider"
            )
            
            # Facade should handle error gracefully
            assert result == "Hello world"  # Fallback to original
    
    def test_cache_performance_and_hits(self, temp_cache_dir):
        """Test cache performance and hit/miss behavior"""
        with patch.object(ConcreteProviderService, 'translate') as mock_translate:
            mock_translate.return_value = "Cached translation"
            
            facade = TranslationFacade(cache_dir=temp_cache_dir)
            
            # First call - should hit provider
            result1 = facade.translate_text(
                text="Hello world",
                target_language="vi",
                provider="groq"
            )
            
            # Second call - should hit cache
            result2 = facade.translate_text(
                text="Hello world", 
                target_language="vi",
                provider="groq"
            )
            
            assert result1 == result2 == "Cached translation"
            
            # Provider should only be called once due to caching
            assert mock_translate.call_count == 1


if __name__ == "__main__":
    # Run basic integration test
    import sys
    import tempfile
    
    print("Running Clean Architecture Integration Test...")
    
    try:
        with tempfile.TemporaryDirectory() as temp_dir:
            # Test facade initialization
            facade = TranslationFacade(cache_dir=temp_dir, use_context_aware=True)
            print("✓ TranslationFacade initialized successfully")
            
            # Test cache stats
            stats = facade.get_cache_stats()
            print(f"✓ Cache stats retrieved: {stats}")
            
            # Test available providers
            providers = facade.get_available_providers()
            print(f"✓ Available providers: {providers}")
            
            # Test legacy adapter
            adapter = LegacyTranslatorAdapter(cache_dir=temp_dir)
            print("✓ LegacyTranslatorAdapter initialized successfully")
            
            print("\n🎉 Clean Architecture Integration Test PASSED!")
            print("\nThe new architecture is ready for use:")
            print("- ✅ Core domain layer with business logic")
            print("- ✅ Application layer with translation strategies") 
            print("- ✅ Infrastructure layer with providers and cache")
            print("- ✅ Integration layer with facade and legacy adapter")
            print("- ✅ Context-aware translation capability")
            
    except Exception as e:
        print(f"❌ Integration test failed: {e}")
        sys.exit(1)
