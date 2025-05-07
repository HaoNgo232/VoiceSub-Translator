import os
import pytest
from pathlib import Path

@pytest.fixture
def test_data_dir():
    """Tạo thư mục test data."""
    test_dir = Path("tests/data")
    test_dir.mkdir(parents=True, exist_ok=True)
    return test_dir

@pytest.fixture
def test_output_dir():
    """Tạo thư mục test output."""
    output_dir = Path("tests/output")
    output_dir.mkdir(parents=True, exist_ok=True)
    return output_dir

@pytest.fixture
def sample_srt_file(test_data_dir):
    """Tạo file SRT mẫu."""
    srt_content = """1
00:00:01,000 --> 00:00:04,000
This is a test subtitle file.

2
00:00:05,000 --> 00:00:08,000
It contains multiple subtitle blocks.

3
00:00:09,000 --> 00:00:12,000
Each block has a number, timestamp and text."""
    
    srt_file = test_data_dir / "sample.srt"
    srt_file.write_text(srt_content)
    return srt_file

@pytest.fixture
def sample_video_file(test_data_dir):
    """Tạo file video mẫu."""
    # Tạo file video giả với ffmpeg
    video_file = test_data_dir / "sample.mp4"
    if not video_file.exists():
        os.system(f"ffmpeg -f lavfi -i testsrc=duration=5:size=1280x720:rate=30 -c:v libx264 {video_file}")
    return video_file

@pytest.fixture
def mock_env_vars(monkeypatch):
    """Mock các biến môi trường."""
    monkeypatch.setenv("GROQ_API_KEY", "test_api_key") 