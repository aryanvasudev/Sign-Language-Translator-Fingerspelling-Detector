import openai
import os
import pyaudio
import wave
from dotenv import load_dotenv
import time

# Load environment variables
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

# Audio recording settings
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 16000
CHUNK = 1024
MIN_RECORD_SECONDS = 5

def record_until_silence(filename, silence_threshold=500, silence_duration=2):
    """
    Records audio until a period of silence is detected.

    Args:
        filename (str): The file path where the recorded audio will be saved.
        silence_threshold (int): Volume level below which audio is considered silent.
        silence_duration (int): Duration in seconds of continuous silence to stop recording.
    """
    audio = pyaudio.PyAudio()
    stream = audio.open(format=FORMAT, channels=CHANNELS,
                        rate=RATE, input=True,
                        frames_per_buffer=CHUNK)

    print("Listening... Speak now.")
    frames = []
    silent_chunks = 0
    start_time = time.time()

    while True:
        data = stream.read(CHUNK)
        frames.append(data)
        volume = max(data)

        if volume < silence_threshold:
            silent_chunks += 1
        else:
            silent_chunks = 0

        elapsed_time = time.time() - start_time

        # Stop recording if minimum time has passed and silence is detected
        if elapsed_time > MIN_RECORD_SECONDS and silent_chunks > (RATE / CHUNK * silence_duration):
            break

    stream.stop_stream()
    stream.close()
    audio.terminate()

    # Save the recorded audio to a file
    with wave.open(filename, 'wb') as wf:
        wf.setnchannels(CHANNELS)
        wf.setsampwidth(audio.get_sample_size(FORMAT))
        wf.setframerate(RATE)
        wf.writeframes(b''.join(frames))

def transcribe_audio(filename):
    """
    Transcribes audio from a file using OpenAI's Whisper model.

    Args:
        filename (str): The file path of the audio to transcribe.

    Returns:
        str: The transcribed text.
    """
    with open(filename, "rb") as audio_file:
        response = openai.Audio.transcribe(
            model="whisper-1",
            file=audio_file
        )
        return response["text"]

def listen_and_transcribe():
    """
    Records audio, transcribes it to text, and prints the transcription.
    
    Returns:
        str: The transcribed text.
    """
    filename = "temp_audio.wav"
    record_until_silence(filename)
    print("Processing transcription...")
    transcription = transcribe_audio(filename)
    print("Transcription:", transcription)
    return transcription

if __name__ == "__main__":
    listen_and_transcribe()
