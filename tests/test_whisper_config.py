import os
import pytest
from unittest.mock import patch, MagicMock
from src.utils.transcription.whisper_processor import transcribe_audio
from src.utils.subtitle_generator import generate_subtitles
from src.utils.whisper_transcriber import main
from pathlib import Path
from src.utils.transcription import WhisperProcessor

@pytest.fixture
def mock_env_vars(monkeypatch):
    """Mock các biến môi trường"""
    monkeypatch.setenv('WHISPER_MODEL', 'base.en')
    monkeypatch.setenv('WHISPER_DEVICE', 'cpu')

@pytest.fixture
def mock_whisper_model(monkeypatch):
    """Mock Whisper model"""
    class MockModel:
        def transcribe(self, *args, **kwargs):
            return {
                'text': 'Test transcription',
                'segments': [
                    {
                        'start': 0,
                        'end': 1,
                        'text': 'Test'
                    }
                ]
            }
    monkeypatch.setattr('whisper.load_model', lambda *args, **kwargs: MockModel())

def test_whisper_processor_config(mock_env_vars, mock_whisper_model, tmp_path):
    """Test cấu hình WhisperProcessor"""
    # Tạo file audio test
    test_audio = tmp_path / "test.wav"
    test_audio.write_bytes(b"dummy audio data")
    
    # Khởi tạo processor
    processor = WhisperProcessor()
    
    # Test transcribe
    result = processor.transcribe_audio(str(test_audio))
    assert result is not None
    assert 'text' in result
    assert result['text'] == 'Test transcription'

def test_whisper_processor_custom_config(mock_whisper_model, tmp_path):
    """Test cấu hình tùy chỉnh của WhisperProcessor"""
    # Tạo file audio test
    test_audio = tmp_path / "test.wav"
    test_audio.write_bytes(b"dummy audio data")
    
    # Khởi tạo processor với cấu hình tùy chỉnh
    processor = WhisperProcessor(
        model_name='tiny.en',
        device='cpu'
    )
    
    # Test transcribe
    result = processor.transcribe_audio(str(test_audio))
    assert result is not None
    assert 'text' in result
    assert result['text'] == 'Test transcription'

def test_whisper_processor_error_handling(tmp_path):
    """Test xử lý lỗi của WhisperProcessor"""
    # Tạo file audio không tồn tại
    test_audio = tmp_path / "nonexistent.wav"
    
    # Khởi tạo processor
    processor = WhisperProcessor()
    
    # Test transcribe với file không tồn tại
    result = processor.transcribe_audio(str(test_audio))
    assert result is None

def test_generate_subtitles_config(mock_env_vars, mock_whisper_model, tmp_path):
    """Test cấu hình generate_subtitles"""
    with patch('whisper.load_model', return_value=mock_whisper_model):
        # Tạo file test
        test_video = tmp_path / "test.mp4"
        test_video.write_bytes(b"dummy video data")
        output_path = tmp_path / "output.srt"
        
        # Test với các tham số mặc định
        result = generate_subtitles(str(test_video), str(output_path))
        assert result is True
        assert output_path.exists()
        
        # Test với các tham số tùy chỉnh
        custom_output = tmp_path / "custom.srt"
        result = generate_subtitles(
            str(test_video),
            str(custom_output),
            model_name="base",
            language="en",
            device="cpu"
        )
        assert result is True
        assert custom_output.exists()

def test_whisper_transcriber_cli(mock_env_vars, mock_whisper_model, tmp_path):
    """Test CLI interface của whisper_transcriber"""
    with patch('whisper.load_model', return_value=mock_whisper_model):
        # Tạo file test
        test_audio = tmp_path / "test.wav"
        test_audio.write_bytes(b"dummy audio data")
        output_path = tmp_path / "output.srt"
        
        # Test với các tham số mặc định
        with patch('sys.argv', ['whisper_transcriber.py', str(test_audio)]):
            main()
            assert output_path.exists()
        
        # Test với các tham số tùy chỉnh
        custom_output = tmp_path / "custom.srt"
        with patch('sys.argv', [
            'whisper_transcriber.py',
            str(test_audio),
            '--output', str(custom_output),
            '--model', 'base',
            '--language', 'en',
            '--device', 'cpu'
        ]):
            main()
            assert custom_output.exists()

def test_error_handling(mock_env_vars, tmp_path):
    """Test xử lý lỗi"""
    # Test với file không tồn tại
    result = transcribe_audio(
        "nonexistent.wav",
        str(tmp_path / "output.srt")
    )
    assert result is False
    
    # Test với model không hợp lệ
    with patch('whisper.load_model', side_effect=Exception("Invalid model")):
        test_audio = tmp_path / "test.wav"
        test_audio.write_bytes(b"dummy audio data")
        result = transcribe_audio(
            str(test_audio),
            str(tmp_path / "output.srt")
        )
        assert result is False 