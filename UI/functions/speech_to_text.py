"""
Speech to Text Module

This module provides speech recognition functionality using the
SpeechRecognition library with Google's Speech Recognition API.
"""

import logging
from typing import Optional
import speech_recognition as sr

# Configure logging
logger = logging.getLogger(__name__)

# Speech recognition settings
AMBIENT_NOISE_DURATION = 0.5  # seconds
PHRASE_TIME_LIMIT = 10  # seconds


def speech_to_text(
    timeout: Optional[int] = None,
    phrase_time_limit: int = PHRASE_TIME_LIMIT
) -> Optional[str]:
    """Convert speech input from microphone to text.

    Args:
        timeout: Maximum time to wait for speech to start (None = no timeout).
        phrase_time_limit: Maximum time for a single phrase.

    Returns:
        Recognized text string, or None if recognition failed.
    """
    recognizer = sr.Recognizer()

    try:
        with sr.Microphone() as source:
            logger.info("Adjusting for ambient noise...")
            recognizer.adjust_for_ambient_noise(source, duration=AMBIENT_NOISE_DURATION)

            logger.info("Listening for speech...")
            audio = recognizer.listen(
                source,
                timeout=timeout,
                phrase_time_limit=phrase_time_limit
            )

            logger.info("Processing audio...")
            text = recognizer.recognize_google(audio)
            logger.info(f"Recognized text: {text}")
            return text

    except sr.WaitTimeoutError:
        logger.warning("Speech recognition timed out waiting for audio")
        return None
    except sr.UnknownValueError:
        logger.warning("Could not understand audio - speech unclear")
        return None
    except sr.RequestError as e:
        logger.error(f"Google Speech Recognition API error: {e}")
        return None
    except OSError as e:
        logger.error(f"Microphone access error: {e}")
        return None
    except Exception as e:
        logger.error(f"Unexpected error in speech recognition: {e}")
        return None


def check_microphone_available() -> bool:
    """Check if a microphone is available.

    Returns:
        True if microphone is available, False otherwise.
    """
    try:
        with sr.Microphone() as source:
            return True
    except OSError:
        return False


# Example usage
if __name__ == "__main__":
    print("Checking microphone availability...")
    if check_microphone_available():
        print("Microphone found!")
        print("\nSpeak now (you have 10 seconds)...")
        result = speech_to_text(timeout=5, phrase_time_limit=10)
        if result:
            print(f"You said: {result}")
        else:
            print("Could not recognize speech")
    else:
        print("No microphone found!")
