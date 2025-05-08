from typing import Dict, Optional
import time
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

class RateLimitHandler:
    def __init__(self):
        self.provider_limits: Dict[str, Dict] = {
            'novita': {
                'requests_per_minute': 60,
                'requests_per_hour': 1000,
                'reset_interval': 60,  # seconds
                'last_reset': datetime.now(),
                'current_count': 0
            },
            'openrouter': {
                'requests_per_minute': 30,
                'requests_per_hour': 500,
                'reset_interval': 60,
                'last_reset': datetime.now(),
                'current_count': 0
            },
            'groq': {
                'requests_per_minute': 50,
                'requests_per_hour': 800,
                'reset_interval': 60,
                'last_reset': datetime.now(),
                'current_count': 0
            }
        }
        
    def check_rate_limit(self, provider: str) -> bool:
        """Kiểm tra xem có vượt quá giới hạn không"""
        if provider not in self.provider_limits:
            return True
            
        limit_info = self.provider_limits[provider]
        current_time = datetime.now()
        
        # Reset counter nếu đã qua interval
        if (current_time - limit_info['last_reset']).total_seconds() >= limit_info['reset_interval']:
            limit_info['current_count'] = 0
            limit_info['last_reset'] = current_time
            
        # Kiểm tra limit
        if limit_info['current_count'] >= limit_info['requests_per_minute']:
            wait_time = limit_info['reset_interval'] - (current_time - limit_info['last_reset']).total_seconds()
            logger.warning(f"Rate limit reached for {provider}. Waiting {wait_time:.2f} seconds")
            time.sleep(wait_time)
            limit_info['current_count'] = 0
            limit_info['last_reset'] = datetime.now()
            
        limit_info['current_count'] += 1
        return True
        
    def handle_error(self, provider: str, error: Exception) -> Optional[str]:
        """Xử lý lỗi từ provider và trả về thông báo phù hợp"""
        error_msg = str(error).lower()
        
        if 'rate limit' in error_msg or 'too many requests' in error_msg:
            logger.warning(f"Rate limit error from {provider}")
            return f"Đã vượt quá giới hạn yêu cầu của {provider}. Vui lòng thử lại sau."
            
        elif 'timeout' in error_msg:
            logger.error(f"Timeout error from {provider}")
            return f"Yêu cầu đến {provider} bị timeout. Vui lòng thử lại."
            
        elif 'authentication' in error_msg or 'unauthorized' in error_msg:
            logger.error(f"Authentication error from {provider}")
            return f"Lỗi xác thực với {provider}. Vui lòng kiểm tra API key."
            
        elif 'quota' in error_msg or 'exceeded' in error_msg:
            logger.error(f"Quota exceeded for {provider}")
            return f"Đã hết quota của {provider}. Vui lòng nâng cấp hoặc thử provider khác."
            
        else:
            logger.error(f"Unexpected error from {provider}: {error}")
            return f"Lỗi không xác định từ {provider}: {error}" 