import os
import pytest
from src.processor.video import VideoProcessor

def test_video_processor_init():
    """Test khởi tạo VideoProcessor."""
    processor = VideoProcessor()
    assert processor.model is not None

def test_extract_audio(video_processor, sample_video_file):
    """Test trích xuất audio từ video."""
    audio_path = video_processor.extract_audio(sample_video_file)
    assert audio_path is not None
    assert os.path.exists(audio_path)
    assert audio_path.endswith(".wav")
    
    # Xóa file audio tạm
    os.remove(audio_path)

def test_transcribe_audio(video_processor, sample_video_file):
    """Test chuyển đổi audio thành text."""
    # Trích xuất audio
    audio_path = video_processor.extract_audio(sample_video_file)
    assert audio_path is not None
    
    try:
        # Transcribe audio
        text = video_processor.transcribe_audio(audio_path)
        assert text is not None
        assert isinstance(text, str)
        assert len(text) > 0
    finally:
        # Xóa file audio tạm
        if audio_path and os.path.exists(audio_path):
            os.remove(audio_path)

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

def test_process_video(video_processor, sample_video_file, test_output_dir):
    """Test xử lý một video."""
    # Xử lý video
    success = video_processor.process_video(sample_video_file, test_output_dir)
    assert success
    
    # Kiểm tra file phụ đề
    base_name = os.path.splitext(os.path.basename(sample_video_file))[0]
    srt_path = os.path.join(test_output_dir, f"{base_name}.srt")
    assert os.path.exists(srt_path)
    
    # Xóa file test
    os.remove(srt_path)

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