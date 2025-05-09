import time
from openai import OpenAI
from .base import BaseProvider, logger

class NovitaProvider(BaseProvider):
    def __init__(self, api_key: str):
        super().__init__(api_key)
        self.client = OpenAI(
            base_url="https://api.novita.ai/v3/openai",
            api_key=api_key
        )
        # Danh sách các model được sắp xếp theo thứ tự ưu tiên
        # 1. qwen/qwen2.5-vl-72b-instruct: Model lớn nhất, chất lượng cao nhất cho dịch thuật
        # 2. meta-llama/llama-4-maverick-17b-128e-instruct-fp8: Model cân bằng giữa tốc độ và chất lượng
        # 3. google/gemma-3-27b-it: Model mới của Google, tối ưu cho IT
        # 4. qwen/qwq-32b: Model đa ngôn ngữ tốt
        # 5. mistralai/mistral-7b-instruct: Model nhẹ, nhanh nhưng vẫn đảm bảo chất lượng
        self.models = [
            'deepseek/deepseek-v3-turbo',
            'deepseek/deepseek-v3-0324',
            'deepseek/deepseek_v3',
            'meta-llama/llama-3.1-70b-instruct',
            'meta-llama/llama-3.3-70b-instruct',
            'qwen/qwen2.5-vl-72b-instruct',
            'deepseek/deepseek-r1-distill-llama-70b',
            'sophosympatheia/midnight-rose-70b',
            'jondurbin/airoboros-l2-70b',
            'qwen/qwen3-235b-a22b-fp8',
            'meta-llama/llama-4-maverick-17b-128e-instruct-fp8',
            'thudm/glm-4-32b-0414',
            'google/gemma-3-27b-it',
            'qwen/qwq-32b',
            'deepseek/deepseek-prover-v2-671b',
        ]
        
        # Theo dõi trạng thái rate limit của các model
        self.rate_limited_models = {}
        self.rate_limit_reset_time = 60  # Reset sau 60 giây (1 phút)
    
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
        system_prompt = self.get_system_prompt(target_lang)
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": text}
        ]
        model_params = {
            'temperature': 0.3,
            'max_tokens': 2048,
        }
        if 'qwen2.5-vl-72b' in model:
            model_params['temperature'] = 0.2
            model_params['max_tokens'] = 4096
        elif 'llama-4' in model:
            model_params['temperature'] = 0.25
        elif 'gemma' in model:
            model_params['temperature'] = 0.2
        elif 'mistral' in model:
            model_params['temperature'] = 0.3

        try:
            response = self.client.chat.completions.create(
                model=model,
                messages=messages,
                **model_params
            )
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"Novita API error with model {model}: {str(e)}")
            if "RATE_LIMIT_EXCEEDED" in str(e):
                # Đánh dấu model này đã bị rate limit
                self.rate_limited_models[model] = time.time()
            raise

    def translate(self, text: str, target_lang: str) -> str:
        """Dịch văn bản sử dụng Novita API, thử lần lượt các model không bị rate limit."""
        last_error = None
        
        # Lọc danh sách model chưa bị rate limit
        available_models = [m for m in self.models if not self._is_rate_limited(m)]
        
        if not available_models:
            # Nếu tất cả model đều bị rate limit, reset model có thời gian rate limit lâu nhất
            oldest_model = min(self.rate_limited_models.items(), key=lambda x: x[1])[0]
            available_models = [oldest_model]
            del self.rate_limited_models[oldest_model]
            logger.info(f"All models rate limited, trying oldest limited model: {oldest_model}")
        
        for model in available_models:
            try:
                logger.info(f"Trying Novita API with model: {model}")
                result = self._try_translate_with_model(text, target_lang, model)
                # Nếu thành công, ghi nhớ model này để ưu tiên trong lần sau
                return result
            except Exception as e:
                last_error = e
                logger.warning(f"Failed with model {model}, trying next model...")
                continue
                
        # Nếu tất cả các model đều thất bại
        logger.error("All Novita models failed")
        raise last_error 