import pytest
import importlib.util
from pathlib import Path

# Load SubtitleProcessor module directly to avoid heavy package imports
spec = importlib.util.spec_from_file_location(
    "subtitle_processor", Path(__file__).resolve().parents[1] / "src/translator/subtitle_processor.py"
)
subtitle_processor = importlib.util.module_from_spec(spec)
spec.loader.exec_module(subtitle_processor)
SubtitleProcessor = subtitle_processor.SubtitleProcessor


def test_read_subtitle_file_unsupported_encoding(tmp_path, monkeypatch):
    # Create a dummy subtitle file
    file_path = tmp_path / "bad.srt"
    file_path.write_bytes(b"\x80\x81")

    processor = SubtitleProcessor()

    # Mock open to always raise UnicodeDecodeError to simulate unsupported encoding
    def mock_open(*args, **kwargs):
        raise UnicodeDecodeError("dummy", b"", 0, 1, "reason")

    monkeypatch.setattr("builtins.open", mock_open)

    with pytest.raises(RuntimeError):
        processor.read_subtitle_file(str(file_path))
