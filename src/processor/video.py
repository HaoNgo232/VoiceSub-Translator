import os
import subprocess
import logging
from typing import Optional, List, Dict, Any
import whisper

class VideoProcessor:
    """Class xử lý video để tạo phụ đề."""
    
    def __init__(self, model_name: str = "small.en"):
        """Khởi tạo processor với model whisper."""
        self.model = whisper.load_model(model_name)
        
    def extract_audio(self, video_path: str) -> Optional[str]:
        """Trích xuất audio từ video."""
        try:
            # Tạo thư mục tạm
            temp_dir = os.path.join("/tmp", f"whisper_{os.getpid()}")
            os.makedirs(temp_dir, exist_ok=True)
            
            # Đường dẫn file audio tạm
            audio_path = os.path.join(temp_dir, "extracted_audio.wav")
            
            # Sử dụng ffmpeg để trích xuất audio
            cmd = [
                "ffmpeg", "-i", video_path,
                "-vn", "-acodec", "pcm_s16le",
                "-ar", "16000", "-ac", "1",
                audio_path
            ]
            
            subprocess.run(cmd, check=True, capture_output=True)
            return audio_path
            
        except Exception as e:
            logging.error(f"Lỗi khi trích xuất audio từ {video_path}: {str(e)}")
            return None
    
    def transcribe_audio(self, audio_path: str) -> Optional[str]:
        """Chuyển đổi audio thành text."""
        try:
            # Sử dụng whisper để transcribe
            result = self.model.transcribe(audio_path)
            return result["text"]
            
        except Exception as e:
            logging.error(f"Lỗi khi transcribe audio {audio_path}: {str(e)}")
            return None
    
    def save_subtitle(self, text: str, output_path: str) -> bool:
        """Lưu phụ đề vào file."""
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(text)
            return True
        except Exception as e:
            logging.error(f"Lỗi khi lưu phụ đề vào {output_path}: {str(e)}")
            return False
    
    def process_video(self, video_path: str, output_dir: str) -> bool:
        """Xử lý một video để tạo phụ đề."""
        logging.info(f"Đang xử lý video: {video_path}")
        
        # Tạo thư mục output nếu chưa tồn tại
        os.makedirs(output_dir, exist_ok=True)
        
        # Lấy tên file không có phần mở rộng
        base_name = os.path.splitext(os.path.basename(video_path))[0]
        srt_path = os.path.join(output_dir, f"{base_name}.srt")
        
        # Kiểm tra xem đã có phụ đề chưa
        if os.path.exists(srt_path):
            logging.info(f"File {srt_path} đã tồn tại, bỏ qua")
            return True
        
        # Trích xuất audio
        audio_path = self.extract_audio(video_path)
        if not audio_path:
            return False
        
        try:
            # Transcribe audio
            text = self.transcribe_audio(audio_path)
            if not text:
                return False
            
            # Lưu phụ đề
            return self.save_subtitle(text, srt_path)
            
        finally:
            # Xóa file audio tạm
            if audio_path and os.path.exists(audio_path):
                os.remove(audio_path)
    
    def process_directory(self, input_dir: str, output_dir: str) -> Dict[str, Any]:
        """Xử lý tất cả video trong thư mục."""
        results = {
            "total": 0,
            "success": 0,
            "failed": 0,
            "skipped": 0
        }
        
        # Tìm tất cả file video
        video_extensions = ['.mp4', '.avi', '.mkv', '.mov']
        video_files = []
        
        for root, _, files in os.walk(input_dir):
            for file in files:
                if any(file.lower().endswith(ext) for ext in video_extensions):
                    video_files.append(os.path.join(root, file))
        
        results["total"] = len(video_files)
        
        # Xử lý từng video
        for video_path in video_files:
            if self.process_video(video_path, output_dir):
                results["success"] += 1
            else:
                results["failed"] += 1
        
        return results 