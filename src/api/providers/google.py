import time
import google.generativeai as genai
from .base import BaseProvider, logger

class GoogleProvider(BaseProvider):
    def __init__(self, api_key: str):
        super().__init__(api_key)
        # Configure the SDK with your API key
        genai.configure(api_key=api_key)
        
        # Danh sách các model được sắp xếp theo thứ tự ưu tiên
        self.models = [
            "gemini-2.0-flash",
            "gemini-2.0-pro",
            "gemini-1.5-flash",
            "gemini-1.5-pro"
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
        try:
            prompt = f"{self.get_system_prompt(target_lang)}\n\nText to translate:\n{text}"
            # Updated API usage
            model_obj = genai.GenerativeModel(model_name=model)
            response = model_obj.generate_content(prompt)
            return response.text.strip()
        except Exception as e:
            logger.error(f"Error translating with Gemini model {model}: {str(e)}")
            if "quota" in str(e).lower() or "rate limit" in str(e).lower() or "limit exceeded" in str(e).lower():
                # Đánh dấu model này đã bị rate limit
                self.rate_limited_models[model] = time.time()
            raise
        
    def translate(self, text: str, target_lang: str) -> str:
        """Dịch văn bản sử dụng Gemini API, thử lần lượt các model khác nhau."""
        last_error = None
        
        # Lọc danh sách model chưa bị rate limit
        available_models = [m for m in self.models if not self._is_rate_limited(m)]
        
        if not available_models:
            # Nếu tất cả model đều bị rate limit, reset model có thời gian rate limit lâu nhất
            oldest_model = min(self.rate_limited_models.items(), key=lambda x: x[1])[0]
            available_models = [oldest_model]
            del self.rate_limited_models[oldest_model]
            logger.info(f"All Gemini models rate limited, trying oldest limited model: {oldest_model}")
        
        for model in available_models:
            try:
                logger.info(f"Trying Gemini API with model: {model}")
                return self._try_translate_with_model(text, target_lang, model)
            except Exception as e:
                last_error = e
                logger.warning(f"Failed with Gemini model {model}: {str(e)}, trying next model...")
                continue
                
        # Nếu tất cả các model đều thất bại
        logger.error("All Gemini models failed")
        raise last_error