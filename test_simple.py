#!/usr/bin/env python3

import sys
import os

# Add current directory to path
sys.path.insert(0, os.getcwd())

from src.utils.subtitle_format_converter.providers.vtt_provider import VttProvider

def main():
    # Read VTT file
    vtt_file = 'fake_data/test_video_sample.vtt'
    with open(vtt_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    print(f"VTT content preview: {repr(content[:50])}")
    print(f"Starts with WEBVTT: {content.strip().startswith('WEBVTT')}")
    
    # Test provider
    provider = VttProvider()
    print(f"Extension: {provider.get_extension()}")
    print(f"Detect format: {provider.detect_format(content)}")
    
    # Convert to SRT
    if provider.detect_format(content):
        srt_content = provider.convert_to_srt(content)
        print("Conversion successful!")
        print("SRT content:")
        print(srt_content)
        
        # Write SRT file
        srt_file = vtt_file.replace('.vtt', '.srt')
        with open(srt_file, 'w', encoding='utf-8') as f:
            f.write(srt_content)
        print(f"SRT file created: {srt_file}")
    else:
        print("Failed to detect VTT format")

if __name__ == "__main__":
    main()
