import logging
from api.providers.openrouter import OpenRouterAPIHandler
from api.config import APIConfig

# Cấu hình logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def test_openrouter():
    """Test chức năng cơ bản của OpenRouter provider."""
    try:
        # Khởi tạo config và provider
        config = APIConfig()
        provider_config = config.get_provider_config('openrouter')
        if not provider_config:
            raise ValueError("OpenRouter configuration not found. Please check your .env file.")
            
        handler = OpenRouterAPIHandler(provider_config)
        
        # Test text với multiple blocks
        test_text = """---BLOCK 1---
Hello world! How are you?
---END BLOCK 1---
---BLOCK 2---
This is a test message.
---END BLOCK 2---
---BLOCK 3---
Let's see how well this translation works.
---END BLOCK 3---"""

        print("\n=== Starting OpenRouter Test ===")
        print("\nSource text:")
        print(test_text)
        
        # Kiểm tra model khả dụng
        print("\nChecking available models...")
        model = handler.rate_limiter.get_available_model("openrouter", handler.MODELS)
        if model:
            print(f"Using model: {model}")
        else:
            print("Warning: No models available within rate limits")
        
        # Thực hiện dịch
        print("\nTranslating...")
        result = handler.translate_text(test_text)
        
        print("\nTranslated text:")
        print(result)
        
        # Kiểm tra rate limits
        print("\nRate limit status:")
        usage_stats = handler.rate_limiter.get_usage_stats()
        for provider, data in usage_stats.items():
            print(f"\n{provider.upper()} Usage:")
            for model, limits in data.get("models", {}).items():
                print(f"\n  {model}:")
                for limit_type, info in limits.items():
                    print(f"    {limit_type}:")
                    print(f"      limit: {info['limit']}")
                    print(f"      count: {info['count']}")
                    print(f"      reset at: {info['reset_at']}")
        
        # Test validate translation
        print("\nValidating translation structure...")
        if handler._validate_translation(test_text, result):
            print("✓ Validation passed - Block structure maintained")
        else:
            print("✗ Validation failed - Block structure changed")
            
    except Exception as e:
        print(f"\nError during test: {str(e)}")
    
    print("\n=== Test Complete ===")

if __name__ == "__main__":
    test_openrouter()
