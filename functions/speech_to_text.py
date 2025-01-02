import openai
import os
import pyaudio
import wave
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

# Audio configuration
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 16000  # Whisper works best with 16kHz audio
CHUNK = 1024  # Buffer size for audio chunks

def record_until_silence(filename, silence_threshold=500, silence_duration=2):
    """
    Records audio until silence is detected and saves it to a WAV file.
    """
    audio = pyaudio.PyAudio()
    stream = audio.open(format=FORMAT, channels=CHANNELS,
                        rate=RATE, input=True,
                        frames_per_buffer=CHUNK)

    print("Listening... Speak now.")
    frames = []
    silent_chunks = 0

    while True:
        data = stream.read(CHUNK)
        frames.append(data)
        volume = max(data)

        if volume < silence_threshold:
            silent_chunks += 1
        else:
            silent_chunks = 0

        if silent_chunks > (RATE / CHUNK * silence_duration):
            break

    stream.stop_stream()
    stream.close()
    audio.terminate()

    with wave.open(filename, 'wb') as wf:
        wf.setnchannels(CHANNELS)
        wf.setsampwidth(audio.get_sample_size(FORMAT))
        wf.setframerate(RATE)
        wf.writeframes(b''.join(frames))

def transcribe_audio(filename):
    """
    Transcribes the given audio file using OpenAI Whisper API.
    """
    with open(filename, "rb") as audio_file:
        response = openai.Audio.transcribe(
            model="whisper-1",
            file=audio_file
        )
        return response["text"]

def listen_and_transcribe():
    """
    Listens for speech, waits for silence, transcribes the speech, and prints it.
    """
    filename = "temp_audio.wav"
    record_until_silence(filename)
    print("Processing transcription...")
    transcription = transcribe_audio(filename)
    print("Transcription:", transcription)

if __name__ == "__main__":
    listen_and_transcribe()
