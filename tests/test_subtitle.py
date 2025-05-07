import os
import pytest
from src.translator.subtitle import SubtitleTranslator

def test_subtitle_translator_init():
    """Test khởi tạo SubtitleTranslator."""
    translator = SubtitleTranslator()
    assert translator.api_handler is not None

def test_scan_directory(subtitle_translator, test_data_dir):
    """Test quét thư mục tìm file SRT."""
    # Tạo một số file SRT
    srt_files = []
    for i in range(3):
        srt_file = os.path.join(test_data_dir, f"test_{i}.srt")
        with open(srt_file, 'w', encoding='utf-8') as f:
            f.write(f"Test subtitle file {i}")
        srt_files.append(srt_file)
    
    try:
        # Quét thư mục
        found_files = subtitle_translator.scan_directory(test_data_dir)
        
        # Kiểm tra kết quả
        assert len(found_files) >= len(srt_files)
        for srt_file in srt_files:
            assert srt_file in found_files
    finally:
        # Xóa file test
        for srt_file in srt_files:
            if os.path.exists(srt_file):
                os.remove(srt_file)

def test_read_subtitle_file(subtitle_translator, sample_srt_file):
    """Test đọc file phụ đề."""
    # Đọc file
    content = subtitle_translator.read_subtitle_file(sample_srt_file)
    
    # Kiểm tra kết quả
    assert content is not None
    assert isinstance(content, str)
    assert len(content) > 0
    assert "This is a test subtitle file" in content

def test_save_translation(subtitle_translator, sample_srt_file, test_output_dir):
    """Test lưu bản dịch."""
    # Đọc file gốc
    content = subtitle_translator.read_subtitle_file(sample_srt_file)
    assert content is not None
    
    # Lưu bản dịch
    success = subtitle_translator.save_translation(sample_srt_file, content)
    assert success
    
    # Kiểm tra file dịch
    base_name = os.path.splitext(sample_srt_file)[0]
    vi_path = f"{base_name}_vi.srt"
    assert os.path.exists(vi_path)
    
    # Kiểm tra nội dung
    with open(vi_path, 'r', encoding='utf-8') as f:
        translated_content = f.read()
    assert translated_content == content
    
    # Xóa file test
    os.remove(vi_path)

def test_process_file(subtitle_translator, sample_srt_file):
    """Test xử lý một file phụ đề."""
    # Xử lý file
    success = subtitle_translator.process_file(sample_srt_file)
    assert success
    
    # Kiểm tra file dịch
    base_name = os.path.splitext(sample_srt_file)[0]
    vi_path = f"{base_name}_vi.srt"
    assert os.path.exists(vi_path)
    
    # Xóa file test
    os.remove(vi_path)

def test_process_directory(subtitle_translator, test_data_dir):
    """Test xử lý thư mục phụ đề."""
    # Tạo một số file SRT
    srt_files = []
    for i in range(3):
        srt_file = os.path.join(test_data_dir, f"test_{i}.srt")
        with open(srt_file, 'w', encoding='utf-8') as f:
            f.write(f"Test subtitle file {i}")
        srt_files.append(srt_file)
    
    try:
        # Xử lý thư mục
        results = subtitle_translator.process_directory(test_data_dir)
        
        # Kiểm tra kết quả
        assert isinstance(results, dict)
        assert "total" in results
        assert "success" in results
        assert "failed" in results
        assert results["total"] >= len(srt_files)
        assert results["success"] >= 0
        assert results["failed"] >= 0
    finally:
        # Xóa file test
        for srt_file in srt_files:
            if os.path.exists(srt_file):
                os.remove(srt_file)
            vi_path = f"{os.path.splitext(srt_file)[0]}_vi.srt"
            if os.path.exists(vi_path):
                os.remove(vi_path) 