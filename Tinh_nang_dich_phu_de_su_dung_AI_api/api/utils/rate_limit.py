import os
import json
import logging
from threading import Lock
from datetime import datetime, timezone, timedelta
from typing import Optional, Dict, Any

class RateLimitManager:
    """Quản lý rate limits cho các API provider."""
    
    def __init__(self, data_dir: str = "data"):
        """
        Khởi tạo rate limit manager.
        
        Args:
            data_dir: Thư mục lưu file rate limits
        """
        self.data_dir = data_dir
        self.file_path = os.path.join(data_dir, "rate_limits.json")
        self.lock = Lock()
        
        # Tạo thư mục data nếu chưa tồn tại
        os.makedirs(data_dir, exist_ok=True)
        
        # Khởi tạo file nếu chưa tồn tại
        if not os.path.exists(self.file_path):
            self._save_data({})

    def _load_data(self) -> Dict:
        """Load rate limit data từ file."""
        try:
            with open(self.file_path, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            return {}
        except json.JSONDecodeError as e:
            logging.error(f"Invalid rate limits JSON: {e}")
            return {}

    def _save_data(self, data: Dict) -> None:
        """Lưu rate limit data vào file."""
        try:
            with open(self.file_path, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            logging.error(f"Failed to save rate limits: {e}")

    def initialize_model(self, provider: str, model: str) -> None:
        """
        Khởi tạo rate limits cho model mới.
        
        Args:
            provider: Tên provider (e.g. "openrouter")
            model: Tên model
        """
        with self.lock:
            data = self._load_data()
            
            # Khởi tạo provider nếu chưa tồn tại
            if provider not in data:
                data[provider] = {"models": {}}
            
            # Khởi tạo model nếu chưa tồn tại
            if model not in data[provider]["models"]:
                now = datetime.now(timezone.utc)
                tomorrow = now + timedelta(days=1)
                next_minute = now + timedelta(minutes=1)
                
                data[provider]["models"][model] = {
                    "daily": {
                        "limit": 200,
                        "count": 0,
                        "reset_at": tomorrow.replace(
                            hour=0, minute=0, second=0, microsecond=0
                        ).isoformat()
                    },
                    "minute": {
                        "limit": 20,
                        "count": 0,
                        "reset_at": next_minute.replace(
                            second=0, microsecond=0
                        ).isoformat()
                    }
                }
                
                self._save_data(data)

    def _is_limit_exceeded(self, limit_data: Dict) -> bool:
        """
        Kiểm tra xem đã vượt quá limit chưa.
        
        Args:
            limit_data: Thông tin về limit
        
        Returns:
            True nếu đã vượt limit, False nếu chưa
        """
        now = datetime.now(timezone.utc)
        reset_time = datetime.fromisoformat(limit_data["reset_at"])
        
        # Reset counter nếu đã qua thời gian reset
        if now >= reset_time:
            if "daily" in str(limit_data["limit"]):
                next_reset = now + timedelta(days=1)
                limit_data["reset_at"] = next_reset.replace(
                    hour=0, minute=0, second=0, microsecond=0
                ).isoformat()
            else:
                next_reset = now + timedelta(minutes=1)
                limit_data["reset_at"] = next_reset.replace(
                    second=0, microsecond=0
                ).isoformat()
            limit_data["count"] = 0
            
        return limit_data["count"] >= limit_data["limit"]

    def can_use_model(self, provider: str, model: str) -> bool:
        """
        Kiểm tra xem có thể sử dụng model không.
        
        Args:
            provider: Tên provider
            model: Tên model
            
        Returns:
            True nếu có thể sử dụng, False nếu đã hit limit
        """
        with self.lock:
            data = self._load_data()
            if provider not in data or model not in data[provider]["models"]:
                return True
                
            model_limits = data[provider]["models"][model]
            
            # Kiểm tra daily limit
            if self._is_limit_exceeded(model_limits["daily"]):
                return False
                
            # Kiểm tra minute limit
            if self._is_limit_exceeded(model_limits["minute"]):
                return False
                
            return True

    def increment_usage(self, provider: str, model: str) -> None:
        """
        Tăng counter usage cho model.
        
        Args:
            provider: Tên provider
            model: Tên model
        """
        with self.lock:
            data = self._load_data()
            if provider in data and model in data[provider]["models"]:
                model_limits = data[provider]["models"][model]
                
                # Cập nhật daily counter
                if not self._is_limit_exceeded(model_limits["daily"]):
                    model_limits["daily"]["count"] += 1
                    
                # Cập nhật minute counter
                if not self._is_limit_exceeded(model_limits["minute"]):
                    model_limits["minute"]["count"] += 1
                    
                self._save_data(data)

    def get_available_model(self, provider: str, models: list) -> Optional[str]:
        """
        Lấy model đầu tiên còn trong limit.
        
        Args:
            provider: Tên provider
            models: Danh sách các model cần check
            
        Returns:
            Tên model nếu có model available, None nếu không có
        """
        for model in models:
            self.initialize_model(provider, model)
            if self.can_use_model(provider, model):
                return model
        return None

    def get_usage_stats(self) -> Dict[str, Any]:
        """
        Lấy thống kê usage của tất cả models.
        
        Returns:
            Dictionary chứa thống kê usage
        """
        with self.lock:
            return self._load_data()
