import requests
import os
from playsound import playsound  #pip install playsound==1.2.2

from dotenv import load_dotenv  # For loading .env files

# Load environment variables from .env file
load_dotenv()

# Get the ElevenLabs API key from the .env file
API_KEY = os.getenv("ELEVENLABS_API_KEY")
if not API_KEY:
    raise ValueError("API key not found in .env file. Please add ELEVENLABS_API_KEY to your .env file.")

VOICE_ID = os.getenv("ELEVENLABS_VOICE_ID")
if not VOICE_ID:
    raise ValueError("Voice ID not found in .env file. Please add ELEVENLABS_VOICE_ID to your .env file.")

# Function to convert text to speech and play the audio
def text_to_speech_and_play(text, output_file="output.mp3"):
    # Clean up input text to ensure proper sentence formatting
    cleaned_text = ' '.join(text.split())  # Remove extra spaces and line breaks

    url = f"https://api.elevenlabs.io/v1/text-to-speech/{VOICE_ID}"
    headers = {
        "xi-api-key": API_KEY,
        "Content-Type": "application/json"
    }
    data = {
        "text": cleaned_text,
        "voice_settings": {
            "stability": 0.7,
            "similarity_boost": 0.8
        }
    }

    # Send POST request to ElevenLabs API
    response = requests.post(url, headers=headers, json=data)
    
    if response.status_code == 200:
        # Save the audio content to a file
        with open(output_file, "wb") as file:
            file.write(response.content)
        
        print(f"Audio saved to {output_file}. Playing now...")
        
        # Play the audio file
        playsound(output_file)
        
        # Optionally, delete the file after playing
        os.remove(output_file)
    else:
        print(f"Error: {response.status_code}, {response.text}")

# Example usage (for testing purposes only)
if __name__ == "__main__":
    sample_text = "Hello! This is a demonstration of ElevenLabs text-to-speech API."
    text_to_speech_and_play(sample_text)
