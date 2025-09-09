import requests
import os
import tempfile
from typing import Optional
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def transcribe_audio_file(audio_file_bytes: bytes, filename: str) -> Optional[str]:
    """
    Transcribe audio file using OpenAI Whisper API via simple HTTP request
    
    Args:
        audio_file_bytes: The audio file as bytes
        filename: Original filename (used to determine file type)
    
    Returns:
        Transcribed text or None if transcription fails
    """
    try:
        # Get API key
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            logger.error("OPENAI_API_KEY environment variable is not set")
            return None
        
        # Create a temporary file to store the audio
        with tempfile.NamedTemporaryFile(delete=False, suffix=f".{filename.split('.')[-1]}") as temp_file:
            temp_file.write(audio_file_bytes)
            temp_file_path = temp_file.name
        
        try:
            # Prepare the API request
            url = "https://api.openai.com/v1/audio/transcriptions"
            headers = {
                "Authorization": f"Bearer {api_key}"
            }
            
            # Prepare the file for upload
            with open(temp_file_path, "rb") as audio_file:
                files = {
                    "file": (filename, audio_file, "audio/webm")
                }
                data = {
                    "model": "whisper-1",
                    "response_format": "text"
                }
                
                # Make the API request
                response = requests.post(url, headers=headers, files=files, data=data, timeout=30)
                
                if response.status_code == 200:
                    transcript = response.text.strip()
                    logger.info(f"Successfully transcribed audio file: {filename}")
                    return transcript
                else:
                    logger.error(f"OpenAI API error: {response.status_code} - {response.text}")
                    return None
                
        finally:
            # Clean up temporary file
            if os.path.exists(temp_file_path):
                os.unlink(temp_file_path)
                
    except Exception as e:
        logger.error(f"Error transcribing audio file {filename}: {str(e)}")
        return None

def transcribe_audio_from_url(audio_url: str) -> Optional[str]:
    """
    Transcribe audio from a URL using OpenAI Whisper API
    
    Args:
        audio_url: URL to the audio file
    
    Returns:
        Transcribed text or None if transcription fails
    """
    try:
        import requests
        
        # Download the audio file
        response = requests.get(audio_url, timeout=30)
        response.raise_for_status()
        
        # Get filename from URL or use default
        filename = audio_url.split('/')[-1] or "audio.webm"
        
        # Transcribe the downloaded audio
        return transcribe_audio_file(response.content, filename)
        
    except Exception as e:
        logger.error(f"Error transcribing audio from URL {audio_url}: {str(e)}")
        return None
