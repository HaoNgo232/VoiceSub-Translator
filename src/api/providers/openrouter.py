import time
import requests
from .base import BaseProvider, logger

class OpenRouterProvider(BaseProvider):
    def __init__(self, api_key: str):
        super().__init__(api_key)
        
        # Danh sách các model được sắp xếp theo thứ tự ưu tiên
        self.models = [
            "deepseek/deepseek-chat:free",
            "deepseek/deepseek-prover-v2:free",
            "meta-llama/llama-3.3-70b-instruct:free",
            "deepseek/deepseek-v3-base:free",
            "qwen/qwen-2.5-72b-instruct:free",
            "deepseek/deepseek-chat-v3-0324:free",
            "featherless/qwerky-72b:free",
            "deepseek/deepseek-chat-v3-0324:free",
            "nvidia/llama-3.1-nemotron-ultra-253b-v1:free",
            "nvidia/llama-3.1-nemotron-ultra-253b-v1:free",
            "mistralai/mistral-small-3.1-24b-instruct:free",
            "deepseek/deepseek-r1-distill-llama-70b:free",
            "qwen/qwen3-30b-a3b:free",
            "qwen/qwen3-32b:free",
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
        url = "https://openrouter.ai/api/v1/chat/completions"
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
            logger.error(f"OpenRouter API timeout for model {model}")
            raise
        except requests.exceptions.RequestException as e:
            logger.error(f"OpenRouter API error for model {model}: {str(e)}")
            
            if "429" in str(e) or "limit" in str(e).lower() or "quota" in str(e).lower():
                # Đánh dấu model này đã bị rate limit
                self.rate_limited_models[model] = time.time()
            raise
        except Exception as e:
            logger.error(f"Unexpected error with OpenRouter API for model {model}: {str(e)}")
            raise
    
    def translate(self, text: str, target_lang: str) -> str:
        """Dịch văn bản sử dụng OpenRouter API, thử lần lượt các model khác nhau."""
        last_error = None
        
        # Lọc danh sách model chưa bị rate limit
        available_models = [m for m in self.models if not self._is_rate_limited(m)]
        
        if not available_models:
            # Nếu tất cả model đều bị rate limit, reset model có thời gian rate limit lâu nhất
            oldest_model = min(self.rate_limited_models.items(), key=lambda x: x[1])[0]
            available_models = [oldest_model]
            del self.rate_limited_models[oldest_model]
            logger.info(f"All OpenRouter models rate limited, trying oldest limited model: {oldest_model}")
        
        for model in available_models:
            try:
                logger.info(f"Trying OpenRouter API with model: {model}")
                return self._try_translate_with_model(text, target_lang, model)
            except Exception as e:
                last_error = e
                logger.warning(f"Failed with OpenRouter model {model}: {str(e)}, trying next model...")
                continue
                
        # Nếu tất cả các model đều thất bại
        logger.error("All OpenRouter models failed")
        raise last_error 