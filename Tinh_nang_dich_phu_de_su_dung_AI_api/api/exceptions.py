class TranslationAPIError(Exception):
    """Base exception for all translation API errors."""
    pass

class RateLimitError(TranslationAPIError):
    """Exception raised when API rate limit is hit."""
    def __init__(self, retry_after: int, message: str = "API rate limit exceeded"):
        self.retry_after = retry_after
        self.message = message
        super().__init__(self.message)

class ValidationError(TranslationAPIError):
    """Exception raised when translation validation fails."""
    pass

class AuthenticationError(TranslationAPIError):
    """Exception raised when API authentication fails."""
    pass

class ConfigurationError(TranslationAPIError):
    """Exception raised when API configuration is invalid."""
    pass

class ConnectionError(TranslationAPIError):
    """Exception raised when API connection fails."""
    pass

class NoAvailableProvidersError(TranslationAPIError):
    """Exception raised when no API providers are available."""
    pass

class NoAvailableModelsError(TranslationAPIError):
    """Exception raised when no models are available within rate limits."""
    pass

class TranslationError(TranslationAPIError):
    """Exception raised when translation fails."""
    def __init__(self, provider: str, error_details: str):
        self.provider = provider
        self.error_details = error_details
        self.message = f"Translation failed with provider {provider}: {error_details}"
        super().__init__(self.message)
