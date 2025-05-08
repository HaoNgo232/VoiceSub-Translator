import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from .base import BaseProvider, logger

class NovitaProvider(BaseProvider):
    def __init__(self, api_key: str):
        super().__init__(api_key)
        # Cấu hình retry
        self.session = requests.Session()
        retries = Retry(
            total=2,  # Giảm số lần retry xuống 2
            backoff_factor=0.5,  # Giảm thời gian chờ
            status_forcelist=[500, 502, 503, 504]
        )
        self.session.mount('https://', HTTPAdapter(max_retries=retries))
        
        # Danh sách các model được sắp xếp theo thứ tự ưu tiên
        # 1. qwen/qwen2.5-vl-72b-instruct: Model lớn nhất, chất lượng cao nhất cho dịch thuật
        # 2. meta-llama/llama-4-maverick-17b-128e-instruct-fp8: Model cân bằng giữa tốc độ và chất lượng
        # 3. google/gemma-3-27b-it: Model mới của Google, tối ưu cho IT
        # 4. qwen/qwq-32b: Model đa ngôn ngữ tốt
        # 5. mistralai/mistral-7b-instruct: Model nhẹ, nhanh nhưng vẫn đảm bảo chất lượng
        self.models = [
            'qwen/qwen2.5-vl-72b-instruct',
            'meta-llama/llama-4-maverick-17b-128e-instruct-fp8',
            'google/gemma-3-27b-it',
            'qwen/qwq-32b',
            'mistralai/mistral-7b-instruct'
        ]

    def _try_translate_with_model(self, text: str, target_lang: str, model: str) -> str:
        """Thử dịch với một model cụ thể"""
        url = "https://api.novita.ai/v3/openai/chat/completions"
        headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json'
        }
        
        # Điều chỉnh tham số dựa trên model
        model_params = {
            'temperature': 0.3,
            'max_tokens': 2048,
            'stream': False
        }
        
        # Điều chỉnh tham số đặc biệt cho từng model
        if 'qwen2.5-vl-72b' in model:
            model_params['temperature'] = 0.2  # Giảm nhiệt độ để kết quả chính xác hơn
            model_params['max_tokens'] = 4096  # Tăng token limit cho model lớn
        elif 'llama-4' in model:
            model_params['temperature'] = 0.25
        elif 'gemma' in model:
            model_params['temperature'] = 0.2  # Gemma hoạt động tốt với nhiệt độ thấp
        elif 'mistral' in model:
            model_params['temperature'] = 0.3  # Giữ nguyên cho Mistral
            
        data = {
            'model': model,
            'messages': [
                {
                    'role': 'system',
                    'content': self.get_system_prompt(target_lang)
                },
                {
                    'role': 'user',
                    'content': text
                }
            ],
            **model_params
        }
        
        try:
            response = self.session.post(url, headers=headers, json=data, timeout=30)
            response.raise_for_status()
            return response.json()['choices'][0]['message']['content']
        except (requests.exceptions.Timeout, requests.exceptions.RequestException) as e:
            logger.error(f"Novita API error with model {model}: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error with Novita API (model {model}): {str(e)}")
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