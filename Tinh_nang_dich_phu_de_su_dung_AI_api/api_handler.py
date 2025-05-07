import os
import time
import json
import re
from queue import Queue
import threading
from groq import Groq
import logging
import httpx
from groq import Groq, RateLimitError
from dotenv import load_dotenv
from typing import Optional, Dict, Any, List, Union

# Load biến môi trường từ file .env
load_dotenv()

# Logging sẽ được cấu hình ở main.py

# logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class RateLimiter:
    def __init__(self, min_interval: float = 0.9):
        self.min_interval = min_interval
        self.last_request_time = 0
        self.lock = threading.Lock()

    def wait(self):
        with self.lock:
            current_time = time.time()
            elapsed = current_time - self.last_request_time
            if elapsed < self.min_interval:
                sleep_time = self.min_interval - elapsed
                time.sleep(sleep_time)
            self.last_request_time = time.time()

class GroqAPIHandler:
    def __init__(self, max_retry_per_model: int = 3):
        """
        Khởi tạo API handler với error handling.
        
        Args:
            max_retry_per_model: Số lần thử tối đa cho mỗi model trước khi chuyển model khác
        """
        self.max_retry_per_model = max_retry_per_model
        self.rate_limiter = RateLimiter(min_interval=0.9)  # Giới hạn 0.9s giữa các request
        self._initialize_models()
        self._initialize_api()

    def _initialize_api(self):
        """Khởi tạo API client với error handling."""
        try:
            self.api_key = os.getenv('GROQ_API_KEY')
            if not self.api_key:
                raise ValueError("API_KEY không được để trống")
            if self.api_key == "YOUR_GROQ_API_KEY":
                raise ValueError("API_KEY chưa được cấu hình")

            self.client = Groq(api_key=self.api_key)
            self._test_connection()
            
        except Exception as e:
            logging.error(f"Lỗi khởi tạo API: {str(e)}")
            raise

    def _initialize_models(self):
        """Khởi tạo và cấu hình các model."""
        self.models = {
            "llama-3.3-70b-versatile": self._create_model_config(30, 6000),
            "llama3-70b-8192": self._create_model_config(30, 6000),
            "llama3-8b-8192": self._create_model_config(30, 6000),
            "gemma2-9b-it": self._create_model_config(30, 15000)
        }
        self.model_queue = list(self.models.keys())
        self.current_model_index = 0
        self.model_stats = {}
        # Không cần queue và thread riêng vì xử lý lỗi và retry đã tích hợp trong translate_text
        # self.request_queue = Queue()
        # self.worker_thread = threading.Thread(target=self.process_queue)
        # self.worker_thread.daemon = True
        # self.worker_thread.start()

    def _create_model_config(self, rpm: int, tpm: int) -> Dict[str, Any]:
        """Tạo cấu hình mặc định cho model."""
        return {
            "rpm": rpm,
            "tpm": tpm,
            "errors": 0,
            "consecutive_errors": 0,  # Số lần lỗi liên tiếp
            "last_error": None,
            "retry_after": 0,
            "total_requests": 0,
            "successful_requests": 0,
            "total_tokens": 0,
            "last_success_time": 0
        }

    def _test_connection(self):
        """Test kết nối tới API và khả năng sử dụng model."""
        try:
            logging.info("Kiểm tra kết nối API...")
            test_model = self.model_queue[0]
            
            self.rate_limiter.wait()  # Đợi theo rate limit
            chat_completion = self.client.chat.completions.create(
                messages=[{"role": "user", "content": "test"}],
                model=test_model,
                max_tokens=1
            )
            
            if hasattr(chat_completion, 'response') and isinstance(chat_completion.response, httpx.Response):
                self._update_model_stats(test_model, chat_completion.response)
                
            logging.info(f"Kết nối API thành công với model {test_model}")
        except Exception as e:
            logging.error(f"Không thể kết nối tới API: {str(e)}")
            raise

    def _update_model_stats(self, model: str, response: httpx.Response):
        """Cập nhật thống kê sử dụng và giới hạn của model."""
        try:
            if model not in self.model_stats:
                self.model_stats[model] = {
                    "requests": 0,
                    "tokens": 0,
                    "errors": 0,
                    "last_usage": None,
                    "rate_limits": {}
                }
            
            stats = self.model_stats[model]
            model_info = self.models[model]
            
            # Cập nhật thống kê cơ bản
            stats["requests"] += 1
            stats["last_usage"] = time.time()
            model_info["total_requests"] += 1
            model_info["last_success_time"] = time.time()
            
            # Phân tích headers
            headers = response.headers
            limit_headers = {
                'requests': ('x-ratelimit-limit-requests', 'x-ratelimit-remaining-requests', 'x-ratelimit-reset-requests'),
                'tokens': ('x-ratelimit-limit-tokens', 'x-ratelimit-remaining-tokens', 'x-ratelimit-reset-tokens')
            }
            
            for limit_type, (limit_header, remaining_header, reset_header) in limit_headers.items():
                limit = headers.get(limit_header)
                remaining = headers.get(remaining_header)
                reset_time = headers.get(reset_header)
                
                if limit and remaining:
                    usage_percent = ((float(limit) - float(remaining)) / float(limit)) * 100
                    stats["rate_limits"][limit_type] = {
                        "limit": limit,
                        "remaining": remaining,
                        "reset": reset_time,
                        "usage_percent": usage_percent
                    }
                    
                    # Log cảnh báo khi sắp đạt giới hạn
                    if usage_percent > 80:
                        logging.warning(f"Model {model}: {limit_type} sắp đạt giới hạn ({usage_percent:.1f}%)")
                        
            # Log thông tin chi tiết
            if stats["rate_limits"]:
                logging.info(f"Model {model} stats: {json.dumps(stats['rate_limits'], indent=2)}")
                
        except Exception as e:
            logging.error(f"Lỗi khi cập nhật stats cho model {model}: {str(e)}")

    def get_next_model(self) -> str:
        """Lấy model tiếp theo có thể sử dụng."""
        start_index = self.current_model_index
        tried_models = set()

        while len(tried_models) < len(self.model_queue):
            model = self.model_queue[self.current_model_index]
            self.current_model_index = (self.current_model_index + 1) % len(self.model_queue)

            model_info = self.models[model]
            current_time = time.time()

            # Kiểm tra thời gian chờ
            if model_info["retry_after"] > current_time:
                wait_time = model_info["retry_after"] - current_time
                logging.info(f"Model {model} cần chờ thêm {wait_time:.1f}s")
                tried_models.add(model)
                continue

            # Kiểm tra giới hạn lỗi
            if model_info["consecutive_errors"] >= self.max_retry_per_model:
                logging.warning(
                    f"Model {model} đã gặp {model_info['consecutive_errors']} lỗi liên tiếp. "
                    f"Tổng số lỗi: {model_info['errors']}"
                )
                tried_models.add(model)
                continue

            logging.info(f"Chuyển sang model: {model}")
            return model

        # Nếu không tìm được model phù hợp, reset lại các model và thử lại
        logging.warning("Không tìm được model phù hợp, reset lại trạng thái các model")
        for model in self.models:
            self.models[model]["errors"] = 0
            self.models[model]["retry_after"] = 0
        
        return self.model_queue[0]  # Trả về model đầu tiên

    # Không cần process_queue và check_rate_limits riêng biệt nữa
    # def add_request(self, prompt, callback):
    #     self.request_queue.put((prompt, callback))
    #
    # def process_queue(self):
    #     while True:
    #         if not self.request_queue.empty():
    #             # self.check_rate_limits() # Logic rate limit cũ không cần nữa
    #             prompt, callback = self.request_queue.get()
    #             try:
    #                 response = self.translate_text(prompt) # Gọi hàm dịch mới
    #                 if response: # Chỉ gọi callback nếu dịch thành công
    #                     callback(response)
    #                 else:
    #                     logging.error(f"Bỏ qua callback do dịch thất bại: {prompt}")
    #             except Exception as e:
    #                 logging.error(f"Lỗi trong process_queue: {str(e)}")
    #                 # Xử lý lỗi hoặc retry có thể thêm ở đây nếu cần
    #             finally:
    #                 self.request_queue.task_done()
    #         time.sleep(0.1)
    #
    # def check_rate_limits(self):
    #     # Logic cũ, không cần thiết với cách xử lý mới
    #     pass

    def _validate_translation(self, text: str, translated_text: str) -> bool:
        """Kiểm tra tính hợp lệ của bản dịch."""
        try:
            # Đếm số block trong bản gốc và bản dịch
            original_blocks = text.count('---BLOCK')
            translated_blocks = translated_text.count('---BLOCK')
            
            if original_blocks != translated_blocks:
                logging.error(f"Số lượng block không khớp: gốc {original_blocks}, dịch {translated_blocks}")
                return False
            
            # Kiểm tra cấu trúc block markers
            original_markers = re.findall(r'---BLOCK \d+---', text)
            translated_markers = re.findall(r'---BLOCK \d+---', translated_text)
            
            if original_markers != translated_markers:
                logging.error("Block markers không khớp giữa bản gốc và bản dịch")
                return False
                
            return True
        except Exception as e:
            logging.error(f"Lỗi khi validate bản dịch: {str(e)}")
            return False

    def translate_text(self, text: str, target_language: str = "Vietnamese") -> Optional[str]:
        """Dịch văn bản với xử lý lỗi toàn diện."""
        if not text or not text.strip():
            logging.error("Văn bản đầu vào trống")
            return None

        current_model = self.model_queue[self.current_model_index]
        logging.info(f"Bắt đầu dịch bằng model: {current_model}")

        max_retries = len(self.models) * 2
        retry_count = 0
        last_error = None

        while retry_count < max_retries:
            try:
                # Đợi theo rate limit
                self.rate_limiter.wait()

                # Tạo prompt dịch
                prompt = f"""Translate the following text to {target_language}. Keep all block markers and formatting exactly as is:

{text}

Important:
1. Keep all ---BLOCK X--- and ---END BLOCK X--- markers exactly as they appear
2. Only translate the text between the markers
3. Maintain the exact same number of blocks
4. Do not add or remove any markers
5. Keep all timestamps and numbers unchanged"""

                # Gọi API
                chat_completion = self.client.chat.completions.create(
                    messages=[{"role": "user", "content": prompt}],
                    model=current_model,
                    max_tokens=4000,
                    temperature=0.3
                )

                translated_text = chat_completion.choices[0].message.content.strip()

                # Validate kết quả
                if self._validate_translation(text, translated_text):
                    # Cập nhật thống kê thành công
                    self.models[current_model]["consecutive_errors"] = 0
                    self.models[current_model]["successful_requests"] += 1
                    if hasattr(chat_completion, 'response'):
                        self._update_model_stats(current_model, chat_completion.response)
                    return translated_text
                else:
                    raise ValueError("Bản dịch không hợp lệ")

            except RateLimitError as e:
                logging.warning(f"Rate limit error với model {current_model}: {str(e)}")
                self.models[current_model]["consecutive_errors"] += 1
                self.models[current_model]["errors"] += 1
                self.models[current_model]["last_error"] = str(e)
                self.models[current_model]["retry_after"] = time.time() + 60  # Chờ 1 phút
                current_model = self.get_next_model()

            except Exception as e:
                logging.error(f"Lỗi khi dịch với model {current_model}: {str(e)}")
                self.models[current_model]["consecutive_errors"] += 1
                self.models[current_model]["errors"] += 1
                self.models[current_model]["last_error"] = str(e)
                last_error = e
                current_model = self.get_next_model()

            retry_count += 1

        # Nếu đã thử hết các model mà vẫn thất bại
        error_msg = f"Không thể dịch sau {max_retries} lần thử. Lỗi cuối: {str(last_error)}"
        logging.error(error_msg)
        return None
