import os
import pytest
from pathlib import Path
from src.processor.video import VideoProcessor
from src.utils.transcription import WhisperProcessor

@pytest.fixture
def video_processor():
    """Fixture để tạo VideoProcessor"""
    return VideoProcessor()

@pytest.fixture
def sample_video_file(tmp_path):
    """Fixture để tạo file video test"""
    video_file = tmp_path / "test.mp4"
    video_file.write_bytes(b"dummy video data")
    return video_file

def test_video_processor_init():
    """Test khởi tạo VideoProcessor."""
    processor = VideoProcessor()
    assert processor.model is not None

def test_extract_audio(video_processor, sample_video_file):
    """Test trích xuất audio từ video."""
    audio_path = video_processor.extract_audio(sample_video_file)
    assert audio_path is not None
    assert Path(audio_path).exists()
    
    # Xóa file audio tạm
    os.remove(audio_path)

def test_transcribe_audio(video_processor, sample_video_file):
    """Test chuyển đổi audio thành văn bản"""
    # Trích xuất audio
    audio_path = video_processor.extract_audio(sample_video_file)
    assert audio_path is not None
    
    # Khởi tạo WhisperProcessor
    processor = WhisperProcessor()
    
    # Test transcribe
    result = processor.transcribe_audio(audio_path)
    assert result is not None
    assert 'text' in result

def test_save_subtitle(video_processor, test_output_dir):
    """Test lưu phụ đề vào file."""
    text = "This is a test subtitle."
    output_path = os.path.join(test_output_dir, "test.srt")
    
    # Lưu phụ đề
    success = video_processor.save_subtitle(text, output_path)
    assert success
    assert os.path.exists(output_path)
    
    # Kiểm tra nội dung
    with open(output_path, 'r', encoding='utf-8') as f:
        content = f.read()
    assert content == text
    
    # Xóa file test
    os.remove(output_path)

def test_process_video(video_processor, sample_video_file):
    """Test xử lý video hoàn chỉnh"""
    # Xử lý video
    result = video_processor.process_video(sample_video_file)
    assert result is not None
    assert 'text' in result

def test_process_directory(video_processor, test_data_dir, test_output_dir):
    """Test xử lý thư mục video."""
    # Xử lý thư mục
    results = video_processor.process_directory(test_data_dir, test_output_dir)
    
    # Kiểm tra kết quả
    assert isinstance(results, dict)
    assert "total" in results
    assert "success" in results
    assert "failed" in results
    assert results["total"] >= 0
    assert results["success"] >= 0
    assert results["failed"] >= 0 