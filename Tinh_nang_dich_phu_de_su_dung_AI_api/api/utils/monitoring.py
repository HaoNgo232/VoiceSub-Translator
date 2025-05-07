import logging
import time
from datetime import datetime
from typing import Dict, Any, Optional
from functools import wraps
from threading import Lock

class MetricsCollector:
    """Collect and manage metrics for API operations."""
    
    def __init__(self):
        self._metrics = {
            "requests": {
                "total": 0,
                "success": 0,
                "failed": 0,
                "rate_limited": 0
            },
            "latency": {
                "total": 0,
                "count": 0,
                "min": float('inf'),
                "max": 0
            },
            "tokens": {
                "total": 0,
                "providers": {}
            },
            "providers": {}
        }
        self._lock = Lock()

    def record_request(self, provider: str, success: bool, latency: float, 
                      tokens: Optional[int] = None, rate_limited: bool = False):
        """Record metrics for an API request."""
        with self._lock:
            # Update general request metrics
            self._metrics["requests"]["total"] += 1
            if success:
                self._metrics["requests"]["success"] += 1
            else:
                self._metrics["requests"]["failed"] += 1
            if rate_limited:
                self._metrics["requests"]["rate_limited"] += 1

            # Update latency metrics
            self._metrics["latency"]["total"] += latency
            self._metrics["latency"]["count"] += 1
            self._metrics["latency"]["min"] = min(self._metrics["latency"]["min"], latency)
            self._metrics["latency"]["max"] = max(self._metrics["latency"]["max"], latency)

            # Update token usage
            if tokens:
                self._metrics["tokens"]["total"] += tokens
                if provider not in self._metrics["tokens"]["providers"]:
                    self._metrics["tokens"]["providers"][provider] = 0
                self._metrics["tokens"]["providers"][provider] += tokens

            # Update provider-specific metrics
            if provider not in self._metrics["providers"]:
                self._metrics["providers"][provider] = {
                    "requests": {
                        "total": 0,
                        "success": 0,
                        "failed": 0,
                        "rate_limited": 0
                    },
                    "latency": {
                        "total": 0,
                        "count": 0,
                        "min": float('inf'),
                        "max": 0
                    }
                }
            
            provider_metrics = self._metrics["providers"][provider]
            provider_metrics["requests"]["total"] += 1
            if success:
                provider_metrics["requests"]["success"] += 1
            else:
                provider_metrics["requests"]["failed"] += 1
            if rate_limited:
                provider_metrics["requests"]["rate_limited"] += 1

            provider_metrics["latency"]["total"] += latency
            provider_metrics["latency"]["count"] += 1
            provider_metrics["latency"]["min"] = min(provider_metrics["latency"]["min"], latency)
            provider_metrics["latency"]["max"] = max(provider_metrics["latency"]["max"], latency)

    def get_metrics(self) -> Dict[str, Any]:
        """Get current metrics."""
        with self._lock:
            metrics = self._metrics.copy()
            # Calculate averages
            if metrics["latency"]["count"] > 0:
                metrics["latency"]["avg"] = metrics["latency"]["total"] / metrics["latency"]["count"]
            for provider in metrics["providers"]:
                if metrics["providers"][provider]["latency"]["count"] > 0:
                    metrics["providers"][provider]["latency"]["avg"] = (
                        metrics["providers"][provider]["latency"]["total"] / 
                        metrics["providers"][provider]["latency"]["count"]
                    )
            return metrics

    def reset_metrics(self):
        """Reset all metrics."""
        with self._lock:
            self.__init__()

# Global metrics collector instance
metrics = MetricsCollector()

def setup_logging(level: int = logging.INFO):
    """Configure logging with a standardized format."""
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

def log_api_call(func):
    """Decorator to log API calls and collect metrics."""
    @wraps(func)
    def wrapper(self, *args, **kwargs):
        provider = self.__class__.__name__
        start_time = time.time()
        success = False
        rate_limited = False
        tokens = None
        
        try:
            result = func(self, *args, **kwargs)
            success = True
            return result
        except Exception as e:
            if "rate limit" in str(e).lower():
                rate_limited = True
            raise
        finally:
            latency = time.time() - start_time
            metrics.record_request(
                provider=provider,
                success=success,
                latency=latency,
                tokens=tokens,
                rate_limited=rate_limited
            )
            
            # Log detailed metrics
            if success:
                logging.info(f"{provider}: Request completed in {latency:.2f}s")
                if tokens:
                    logging.info(f"{provider}: Used {tokens} tokens")
            else:
                if rate_limited:
                    logging.warning(f"{provider}: Rate limited, request took {latency:.2f}s")
                else:
                    logging.error(f"{provider}: Request failed after {latency:.2f}s")
    
    return wrapper
