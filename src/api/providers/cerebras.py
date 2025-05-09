import time
import requests
from .base import BaseProvider, logger

class CerebrasProvider(BaseProvider):
    def __init__(self, api_key: str):
        super().__init__(api_key)
        
        # Danh sách các model được sắp xếp theo thứ tự ưu tiên
        self.models = [
            "cerebras-1",
            "cerebras-2401",
            "slimstral-1",
            "slimstral-2401"
        ]
        
        # Theo dõi trạng thái rate limit của các model
        self.rate_limited_models = {}
        self.rate_limit_reset_time = 60  # Reset sau 60 giây
    
    def _is_rate_limited(self, model):
        """Kiểm tra xem model có đang bị rate limit không"""
        if model not in self.rate_limited_models:
            return False
            
        limit_time = self.rate_limited_models[model]
        current_time = time.time()
        
        # Nếu đã qua thời gian reset, xóa khỏi danh sách bị limit
        if current_time - limit_time > self.rate_limit_reset_time:
            del self.rate_limited_models[model]
            return False
            
        return True
    
    def _try_translate_with_model(self, text: str, target_lang: str, model: str) -> str:
        """Thử dịch sử dụng một model cụ thể"""
        url = "https://api.cerebras.ai/v1/chat/completions"
        headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json'
        }
        data = {
            'model': model,
            'messages': [
                {'role': 'system', 'content': self.get_system_prompt(target_lang)},
                {'role': 'user', 'content': text}
            ]
        }
        try:
            response = requests.post(url, headers=headers, json=data, timeout=30)
            response.raise_for_status()
            return response.json()['choices'][0]['message']['content']
        except requests.exceptions.Timeout:
            logger.error(f"Cerebras API timeout for model {model}")
            raise
        except requests.exceptions.RequestException as e:
            logger.error(f"Cerebras API error for model {model}: {str(e)}")
            
            if "429" in str(e) or "limit" in str(e).lower() or "quota" in str(e).lower():
                # Đánh dấu model này đã bị rate limit
                self.rate_limited_models[model] = time.time()
            raise
        except Exception as e:
            logger.error(f"Unexpected error with Cerebras API for model {model}: {str(e)}")
            raise
    
    def translate(self, text: str, target_lang: str) -> str:
        """Dịch văn bản sử dụng Cerebras API, thử lần lượt các model khác nhau."""
        last_error = None
        
        # Lọc danh sách model chưa bị rate limit
        available_models = [m for m in self.models if not self._is_rate_limited(m)]
        
        if not available_models:
            # Nếu tất cả model đều bị rate limit, reset model có thời gian rate limit lâu nhất
            oldest_model = min(self.rate_limited_models.items(), key=lambda x: x[1])[0]
            available_models = [oldest_model]
            del self.rate_limited_models[oldest_model]
            logger.info(f"All Cerebras models rate limited, trying oldest limited model: {oldest_model}")
        
        for model in available_models:
            try:
                logger.info(f"Trying Cerebras API with model: {model}")
                return self._try_translate_with_model(text, target_lang, model)
            except Exception as e:
                last_error = e
                logger.warning(f"Failed with Cerebras model {model}: {str(e)}, trying next model...")
                continue
                
        # Nếu tất cả các model đều thất bại
        logger.error("All Cerebras models failed")
        raise last_error 