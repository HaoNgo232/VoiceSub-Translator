#!/usr/bin/env python3

import re

def convert_vtt_to_srt_improved(vtt_content):
    """Convert VTT content to SRT format - improved version"""
    # Remove WEBVTT header
    content = re.sub(r'^WEBVTT\s*\n', '', vtt_content)
    
    # Convert timestamp format (dots to commas)
    content = re.sub(r'(\d{2}:\d{2}:\d{2})\.(\d{3})', r'\1,\2', content)
    
    # Split into chunks
    chunks = re.split(r'\n\s*\n', content.strip())
    result = []
    subtitle_index = 1
    
    for chunk in chunks:
        # Skip NOTE chunks or empty ones
        if chunk.strip().startswith("NOTE") or not chunk.strip():
            continue
            
        # Process lines in chunk
        lines = chunk.strip().split('\n')
        timestamp_line = None
        text_lines = []
        
        for line in lines:
            line = line.strip()
            if '-->' in line:
                timestamp_line = line
            elif line and not re.match(r'^\d+$', line):  # Skip lines with only numbers (old sequence numbers)
                # Remove HTML/VTT tags like <v ->, <v Speaker>, etc.
                line = re.sub(r'<v[^>]*>', '', line)  # Remove opening <v ...> tags
                line = re.sub(r'</v>', '', line)      # Remove closing </v> tags
                line = re.sub(r'<[^>]+>', '', line)   # Remove other HTML tags
                line = line.strip()
                if line:  # Only add if line is not empty after removing tags
                    text_lines.append(line)
        
        if timestamp_line and text_lines:
            joined_text = '\n'.join(text_lines)
            result.append(f"{subtitle_index}\n{timestamp_line}\n{joined_text}")
            subtitle_index += 1
    
    return '\n\n'.join(result)

# Test the improved conversion
def test_conversion():
    vtt_files = [
        'fake_data/test_video_sample.vtt',
        'fake_data/react_course.vtt'
    ]
    
    for vtt_file in vtt_files:
        try:
            print(f"\n=== Testing {vtt_file} ===")
            with open(vtt_file, 'r', encoding='utf-8') as f:
                vtt_content = f.read()
            
            print("VTT content:")
            print(vtt_content[:200] + "..." if len(vtt_content) > 200 else vtt_content)
            
            # Convert
            srt_content = convert_vtt_to_srt_improved(vtt_content)
            print(f"\nSRT content:")
            print(srt_content)
            
            # Save SRT file
            srt_file = vtt_file.replace('.vtt', '_converted.srt')
            with open(srt_file, 'w', encoding='utf-8') as f:
                f.write(srt_content)
            
            print(f"\nSRT file saved: {srt_file}")
            
        except Exception as e:
            print(f"Error processing {vtt_file}: {e}")

if __name__ == "__main__":
    test_conversion()
