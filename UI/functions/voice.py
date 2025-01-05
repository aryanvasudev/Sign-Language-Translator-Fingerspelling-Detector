import requests
import os
from playsound import playsound 

from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("ELEVENLABS_API_KEY")
if not API_KEY:
    raise ValueError("API key not found in .env file. Please add ELEVENLABS_API_KEY to your .env file.")

VOICE_ID = os.getenv("ELEVENLABS_VOICE_ID")
if not VOICE_ID:
    raise ValueError("Voice ID not found in .env file. Please add ELEVENLABS_VOICE_ID to your .env file.")

def text_to_speech_and_play(text, output_file="output.mp3"):
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

    response = requests.post(url, headers=headers, json=data)
    
    if response.status_code == 200:
        with open(output_file, "wb") as file:
            file.write(response.content)

        print(f"Audio saved to {output_file}. Playing now...")
        playsound(output_file)
        os.remove(output_file)

    else:
        print(f"Error: {response.status_code}, {response.text}")


# Example usage
if __name__ == "__main__":
    sample_text = "Hello! This is a demonstration of ElevenLabs text-to-speech API."
    text_to_speech_and_play(sample_text)
