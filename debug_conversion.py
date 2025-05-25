#!/usr/bin/env python3

import sys
import os
sys.path.insert(0, os.getcwd())

# Test import module by module
try:
    print("Testing imports...")
    
    print("1. Testing base converter import...")
    from src.utils.subtitle_format_converter.converter import SubtitleFormatConverter
    print("   ✓ Base converter imported")
    
    print("2. Testing VTT provider import...")
    from src.utils.subtitle_format_converter.providers.vtt_provider import VttProvider
    print("   ✓ VTT provider imported")
    
    print("3. Testing get_all_providers...")
    from src.utils.subtitle_format_converter.providers import get_all_providers
    providers = get_all_providers()
    print(f"   ✓ Found {len(providers)} providers: {[p.__name__ for p in providers]}")
    
    print("4. Testing conversion function...")
    from src.utils.subtitle_format_converter import convert_to_srt
    print("   ✓ convert_to_srt imported")
    
    print("5. Testing actual conversion...")
    result = convert_to_srt('fake_data/test_video_sample.vtt', 'fake_data/test_converted.srt')
    print(f"   Result: {result}")
    
    if result:
        print("6. Checking output file...")
        if os.path.exists('fake_data/test_converted.srt'):
            print("   ✓ Output file created")
            with open('fake_data/test_converted.srt', 'r', encoding='utf-8') as f:
                content = f.read()
            print(f"   Content preview: {content[:100]}...")
        else:
            print("   ✗ Output file not found")
    
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
