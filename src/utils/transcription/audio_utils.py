import subprocess
import logging

logger = logging.getLogger(__name__)

def extract_audio(video_path, audio_path):
    """Extract audio from video file using ffmpeg."""
    try:
        # Construct ffmpeg command
        command = [
            'ffmpeg',
            '-i', video_path,  # Input video
            '-vn',  # Disable video
            '-acodec', 'pcm_s16le',  # Audio codec
            '-ar', '16000',  # Sample rate
            '-ac', '1',  # Mono audio
            '-y',  # Overwrite output file
            audio_path
        ]
        
        # Execute ffmpeg command
        logger.info(f"Running ffmpeg command: {' '.join(command)}")
        result = subprocess.run(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=False  # Don't raise exception on non-zero exit
        )
        
        # Check if command was successful
        if result.returncode != 0:
            logger.error(f"FFmpeg error (code {result.returncode}): {result.stderr}")
            return False
            
        logger.info(f"Successfully extracted audio to: {audio_path}")
        return True
        
    except Exception as e:
        logger.error(f"Error extracting audio: {str(e)}")
        return False 