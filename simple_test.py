#!/usr/bin/env python3

print("Starting VTT to SRT conversion test...")

try:
    # Test reading the VTT file
    with open('fake_data/react_course.vtt', 'r', encoding='utf-8') as f:
        content = f.read()
    
    print(f"File content length: {len(content)} characters")
    print("First 300 characters:")
    print(content[:300])
    print("\n" + "="*50)
    
    import re
    
    # Apply our conversion logic
    # Remove WEBVTT header
    content = re.sub(r'^WEBVTT\s*\n', '', content)
    
    # Convert timestamp format (dots to commas)
    content = re.sub(r'(\d{2}:\d{2}:\d{2})\.(\d{3})', r'\1,\2', content)
    
    # Split into chunks
    chunks = re.split(r'\n\s*\n', content.strip())
    print(f"Found {len(chunks)} chunks")
    
    result = []
    subtitle_index = 1
    
    for i, chunk in enumerate(chunks):
        print(f"\nChunk {i+1}: '{chunk[:100]}...'")
        
        # Skip NOTE chunks or empty ones
        if chunk.strip().startswith("NOTE") or not chunk.strip():
            print("  -> Skipping NOTE or empty chunk")
            continue
            
        # Process lines in chunk
        lines = chunk.strip().split('\n')
        timestamp_line = None
        text_lines = []
        
        for line in lines:
            line = line.strip()
            if '-->' in line:
                timestamp_line = line
                print(f"  -> Found timestamp: {timestamp_line}")
            elif line and not re.match(r'^\d+$', line):  # Skip lines with only numbers
                # Remove HTML/VTT tags
                original_line = line
                line = re.sub(r'<v[^>]*>', '', line)  # Remove opening <v ...> tags
                line = re.sub(r'</v>', '', line)      # Remove closing </v> tags
                line = re.sub(r'<[^>]+>', '', line)   # Remove other HTML tags
                line = line.strip()
                if line:  # Only add if line is not empty after removing tags
                    text_lines.append(line)
                    print(f"  -> Text line: '{original_line}' -> '{line}'")
        
        if timestamp_line and text_lines:
            joined_text = '\n'.join(text_lines)
            srt_entry = f"{subtitle_index}\n{timestamp_line}\n{joined_text}"
            result.append(srt_entry)
            print(f"  -> Created SRT entry #{subtitle_index}")
            subtitle_index += 1
    
    srt_content = '\n\n'.join(result)
    print(f"\nFinal SRT content ({len(srt_content)} characters):")
    print(srt_content)
    
    # Save the result
    with open('fake_data/react_course_converted.srt', 'w', encoding='utf-8') as f:
        f.write(srt_content)
    
    print("\nSRT file saved successfully!")
    
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
