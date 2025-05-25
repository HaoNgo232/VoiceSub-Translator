#!/usr/bin/env python3
import os
import sys

# Add current directory to Python path
sys.path.insert(0, os.getcwd())

from src.utils.subtitle_format_converter.providers import get_all_providers
from src.utils.subtitle_format_converter import convert_to_srt

def test_vtt_conversion():
    """Test chuyển đổi VTT sang SRT"""
    print("=== Test chuyển đổi VTT sang SRT ===")
    
    # Get all providers
    providers = get_all_providers()
    print(f"Providers found: {[p.__name__ for p in providers]}")
    
    # Read test file
    vtt_file = "fake_data/test_video_sample.vtt"
    if not os.path.exists(vtt_file):
        print(f"File {vtt_file} không tồn tại!")
        return
        
    with open(vtt_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    print(f"File content start: {repr(content[:100])}")
    
    # Test each provider
    for provider_class in providers:
        provider = provider_class()
        extension = provider.get_extension()
        detected = provider.detect_format(content)
        print(f"{provider_class.__name__}: extension={extension}, detect={detected}")
        
        if extension == ".vtt" and detected:
            print("Testing VTT conversion...")
            srt_content = provider.convert_to_srt(content)
            print("SRT content:")
            print(srt_content[:300])
    
    # Test convert_to_srt function
    print("\n=== Test convert_to_srt function ===")
    success = convert_to_srt(vtt_file)
    print(f"Convert result: {success}")
    
    # Check if SRT file was created
    srt_file = vtt_file.replace('.vtt', '.srt')
    if os.path.exists(srt_file):
        print(f"SRT file created: {srt_file}")
        with open(srt_file, 'r', encoding='utf-8') as f:
            srt_content = f.read()
        print("SRT content:")
        print(srt_content)
    else:
        print("SRT file not created")

if __name__ == "__main__":
    test_vtt_conversion()
