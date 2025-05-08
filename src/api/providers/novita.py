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
            'google/gemma-3-27b-it',
            'qwen/qwq-32b',
            'qwen/qwen2.5-vl-72b-instruct',
            'mistralai/mistral-7b-instruct',
            'meta-llama/llama-4-maverick-17b-128e-instruct-fp8',
        ]

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
            raise

    def translate(self, text: str, target_lang: str) -> str:
        """Dịch văn bản sử dụng Novita API, thử lần lượt các model khác nhau."""
        last_error = None
        
        for model in self.models:
            try:
                logger.info(f"Trying Novita API with model: {model}")
                return self._try_translate_with_model(text, target_lang, model)
            except Exception as e:
                last_error = e
                logger.warning(f"Failed with model {model}, trying next model...")
                continue
                
        # Nếu tất cả các model đều thất bại
        logger.error("All Novita models failed")
        raise last_error 