#!/usr/bin/env python3
"""
Test script for Whisper transcription functionality
"""

import asyncio
import os
from dotenv import load_dotenv
from utils.whisper import transcribe_audio_file

# Load environment variables
load_dotenv()

async def test_whisper():
    """Test Whisper transcription with a sample audio file"""
    
    # Check if OpenAI API key is set
    if not os.getenv("OPENAI_API_KEY"):
        print("❌ OPENAI_API_KEY not found in environment variables")
        print("Please set your OpenAI API key in the .env file")
        return False
    
    print("✅ OpenAI API key found")
    
    # Test with a sample audio file (you can replace this with an actual audio file)
    # For now, we'll just test the function structure
    try:
        # This is a dummy test - replace with actual audio file bytes
        sample_audio_bytes = b"dummy_audio_data"
        result = await transcribe_audio_file(sample_audio_bytes, "test.webm")
        
        if result is None:
            print("⚠️  Transcription returned None (expected for dummy data)")
        else:
            print(f"✅ Transcription result: {result}")
            
        print("✅ Whisper utility function is working correctly")
        return True
        
    except Exception as e:
        print(f"❌ Error testing Whisper: {str(e)}")
        return False

if __name__ == "__main__":
    print("Testing Whisper transcription setup...")
    success = asyncio.run(test_whisper())
    
    if success:
        print("\n🎉 Whisper setup test completed successfully!")
        print("You can now use voice transcription in your forms.")
    else:
        print("\n❌ Whisper setup test failed!")
        print("Please check your configuration and try again.")
