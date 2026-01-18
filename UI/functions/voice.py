"""
Voice Module

This module provides text-to-speech functionality using the ElevenLabs API.
It converts text into natural-sounding speech and plays it back.
"""

import os
import logging
from typing import Optional
import requests
from playsound import playsound
from dotenv import load_dotenv

# Configure logging
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

API_KEY: Optional[str] = os.getenv("ELEVENLABS_API_KEY")
if not API_KEY:
    logger.error("ELEVENLABS_API_KEY not found in .env file")
    raise ValueError("API key not found in .env file. Please add ELEVENLABS_API_KEY to your .env file.")

VOICE_ID: Optional[str] = os.getenv("ELEVENLABS_VOICE_ID")
if not VOICE_ID:
    logger.error("ELEVENLABS_VOICE_ID not found in .env file")
    raise ValueError("Voice ID not found in .env file. Please add ELEVENLABS_VOICE_ID to your .env file.")

# ElevenLabs API configuration
ELEVENLABS_API_URL = "https://api.elevenlabs.io/v1/text-to-speech"
DEFAULT_STABILITY = 0.7
DEFAULT_SIMILARITY_BOOST = 0.8


def text_to_speech_and_play(
    text: str,
    output_file: str = "output.mp3",
    stability: float = DEFAULT_STABILITY,
    similarity_boost: float = DEFAULT_SIMILARITY_BOOST
) -> bool:
    """Convert text to speech using ElevenLabs API and play it.

    Args:
        text: The text to convert to speech.
        output_file: Path for the temporary audio file.
        stability: Voice stability setting (0.0-1.0).
        similarity_boost: Voice similarity boost setting (0.0-1.0).

    Returns:
        True if successful, False otherwise.

    Raises:
        ValueError: If text is empty.
        requests.RequestException: If API call fails.
    """
    if not text or not text.strip():
        logger.warning("Empty text provided to text_to_speech_and_play")
        return False

    # Clean up text - remove extra whitespace
    cleaned_text = ' '.join(text.split())
    logger.info(f"Converting text to speech: {cleaned_text[:50]}...")

    url = f"{ELEVENLABS_API_URL}/{VOICE_ID}"
    headers = {
        "xi-api-key": API_KEY,
        "Content-Type": "application/json"
    }
    data = {
        "text": cleaned_text,
        "voice_settings": {
            "stability": stability,
            "similarity_boost": similarity_boost
        }
    }

    try:
        response = requests.post(url, headers=headers, json=data, timeout=30)

        if response.status_code == 200:
            # Save audio to file
            with open(output_file, "wb") as file:
                file.write(response.content)

            logger.info(f"Audio saved to {output_file}. Playing now...")

            # Play the audio
            try:
                playsound(output_file)
            except Exception as e:
                logger.error(f"Error playing audio: {e}")
                return False
            finally:
                # Clean up the temporary file
                if os.path.exists(output_file):
                    os.remove(output_file)
                    logger.debug(f"Cleaned up temporary file: {output_file}")

            return True
        else:
            logger.error(f"ElevenLabs API error: {response.status_code}, {response.text}")
            return False

    except requests.Timeout:
        logger.error("ElevenLabs API request timed out")
        return False
    except requests.RequestException as e:
        logger.error(f"ElevenLabs API request failed: {e}")
        return False
    except Exception as e:
        logger.error(f"Unexpected error in text_to_speech_and_play: {e}")
        return False


# Example usage
if __name__ == "__main__":
    sample_text = "Hello! This is a demonstration of ElevenLabs text-to-speech API."
    success = text_to_speech_and_play(sample_text)
    print(f"Text-to-speech {'succeeded' if success else 'failed'}")
