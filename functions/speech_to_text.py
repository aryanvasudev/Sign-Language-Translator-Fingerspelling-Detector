import openai
import os
import pyaudio
import wave
from dotenv import load_dotenv
import threading

# Load environment variables from .env file
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

# Audio configuration
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 16000  # Whisper works best with 16kHz audio
CHUNK = 1024  # Buffer size for audio chunks
RECORD_SECONDS = 5  # Length of each audio snippet to process

def record_audio_to_file(filename):
    """Records audio from the microphone and saves it to a WAV file."""
    audio = pyaudio.PyAudio()
    stream = audio.open(format=FORMAT, channels=CHANNELS,
                        rate=RATE, input=True,
                        frames_per_buffer=CHUNK)
    frames = []
    for _ in range(0, int(RATE / CHUNK * RECORD_SECONDS)):
        data = stream.read(CHUNK)
        frames.append(data)
    stream.stop_stream()
    stream.close()
    audio.terminate()

    # Save the recording to a WAV file
    with wave.open(filename, 'wb') as wf:
        wf.setnchannels(CHANNELS)
        wf.setsampwidth(audio.get_sample_size(FORMAT))
        wf.setframerate(RATE)
        wf.writeframes(b''.join(frames))

def transcribe_audio(filename):
    """Transcribes the given audio file using OpenAI Whisper API."""
    with open(filename, "rb") as audio_file:
        response = openai.Audio.transcribe(
            model="whisper-1",
            file=audio_file
        )
        print("Transcription:", response["text"])

def real_time_transcription():
    """Continuously records and transcribes audio in real time."""
    while True:
        filename = "temp_audio.wav"
        record_audio_to_file(filename)
        transcribe_audio(filename)

if __name__ == "__main__":
    transcription_thread = threading.Thread(target=real_time_transcription)
    transcription_thread.start()
