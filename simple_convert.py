import re

def convert_vtt_to_srt(vtt_content):
    """Convert VTT content to SRT format"""
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
            
        # Process lines with timestamps
        lines = chunk.strip().split('\n')
        timestamp_line = None
        text_lines = []
        
        for line in lines:
            if '-->' in line:
                timestamp_line = line.strip()
            elif line.strip():
                text_lines.append(line.strip())
        
        if timestamp_line and text_lines:
            joined_text = '\n'.join(text_lines)
            result.append(f"{subtitle_index}\n{timestamp_line}\n{joined_text}")
            subtitle_index += 1
    
    return '\n\n'.join(result)

# Test the conversion
vtt_file = 'fake_data/test_video_sample.vtt'
try:
    with open(vtt_file, 'r', encoding='utf-8') as f:
        vtt_content = f.read()
    
    print("VTT file loaded successfully")
    print(f"Content preview: {repr(vtt_content[:50])}")
    
    # Convert
    srt_content = convert_vtt_to_srt(vtt_content)
    print("\nSRT content:")
    print(srt_content)
    
    # Save SRT file
    srt_file = vtt_file.replace('.vtt', '.srt')
    with open(srt_file, 'w', encoding='utf-8') as f:
        f.write(srt_content)
    
    print(f"\nSRT file saved: {srt_file}")
    
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
