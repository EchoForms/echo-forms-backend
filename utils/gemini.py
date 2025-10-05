import requests
import os
import tempfile
from typing import Optional
import logging
import base64

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def transcribe_audio_file(audio_file_bytes: bytes, filename: str) -> Optional[str]:
    """
    Transcribe audio file using Google Gemini API via simple HTTP request
    
    Args:
        audio_file_bytes: The audio file as bytes
        filename: Original filename (used to determine file type)
    
    Returns:
        Transcribed text or None if transcription fails
    """
    try:
        # Get API key
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            logger.error("GEMINI_API_KEY environment variable is not set")
            return None
        
        # Encode audio file to base64
        audio_base64 = base64.b64encode(audio_file_bytes).decode('utf-8')
        
        # Prepare the API request
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={api_key}"
        
        headers = {
            "Content-Type": "application/json"
        }
        
        # Prepare the request payload
        payload = {
            "contents": [
                {
                    "parts": [
                        {
                            "text": "Please transcribe the following audio file. Return only the transcribed text without any additional commentary or formatting."
                        },
                        {
                            "inline_data": {
                                "mime_type": "audio/webm",
                                "data": audio_base64
                            }
                        }
                    ]
                }
            ],
            "generationConfig": {
                "temperature": 0.1,
                "maxOutputTokens": 1000
            }
        }
        
        # Make the API request
        response = requests.post(url, headers=headers, json=payload, timeout=60)
        
        if response.status_code == 200:
            result = response.json()
            
            # Extract transcribed text from response
            if "candidates" in result and len(result["candidates"]) > 0:
                candidate = result["candidates"][0]
                if "content" in candidate and "parts" in candidate["content"]:
                    parts = candidate["content"]["parts"]
                    if len(parts) > 0 and "text" in parts[0]:
                        transcript = parts[0]["text"].strip()
                        logger.info(f"Successfully transcribed audio file with Gemini: {filename}")
                        return transcript
            
            logger.error("Unexpected response format from Gemini API")
            return None
        else:
            logger.error(f"Gemini API error: {response.status_code} - {response.text}")
            return None
                
    except Exception as e:
        logger.error(f"Error transcribing audio file {filename} with Gemini: {str(e)}")
        return None

def transcribe_audio_from_url(audio_url: str) -> Optional[str]:
    """
    Transcribe audio from a URL using Google Gemini API
    
    Args:
        audio_url: URL to the audio file
    
    Returns:
        Transcribed text or None if transcription fails
    """
    try:
        # Download the audio file
        response = requests.get(audio_url, timeout=30)
        response.raise_for_status()
        
        # Get filename from URL or use default
        filename = audio_url.split('/')[-1] or "audio.webm"
        
        # Transcribe the downloaded audio
        return transcribe_audio_file(response.content, filename)
        
    except Exception as e:
        logger.error(f"Error transcribing audio from URL {audio_url} with Gemini: {str(e)}")
        return None

def transcribe_audio_file_with_fallback(audio_file_bytes: bytes, filename: str) -> Optional[str]:
    """
    Transcribe audio file using Gemini API with Whisper as fallback
    
    Args:
        audio_file_bytes: The audio file as bytes
        filename: Original filename (used to determine file type)
    
    Returns:
        Transcribed text or None if both transcription methods fail
    """
    # Try Gemini first
    transcript = transcribe_audio_file(audio_file_bytes, filename)
    if transcript:
        logger.info("Gemini transcription successful")
        return transcript
    
    # Fallback to Whisper
    logger.info("Gemini failed, trying Whisper as fallback")
    try:
        from .whisper import transcribe_audio_file as whisper_transcribe
        transcript = whisper_transcribe(audio_file_bytes, filename)
        if transcript:
            logger.info("Whisper fallback transcription successful")
        return transcript
    except Exception as e:
        logger.error(f"Both Gemini and Whisper transcription failed: {str(e)}")
        return None
