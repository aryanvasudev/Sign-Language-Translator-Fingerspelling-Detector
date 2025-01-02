import openai
import os
import pyaudio
import wave
from dotenv import load_dotenv
import time

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 16000  
CHUNK = 1024  
MIN_RECORD_SECONDS = 5  

def record_until_silence(filename, silence_threshold=500, silence_duration=2):
    
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

        if elapsed_time > MIN_RECORD_SECONDS and silent_chunks > (RATE / CHUNK * silence_duration):
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
    
    with open(filename, "rb") as audio_file:
        response = openai.Audio.transcribe(
            model="whisper-1",
            file=audio_file
        )
        return response["text"]

def listen_and_transcribe():
    
    filename = "temp_audio.wav"
    record_until_silence(filename)
    print("Processing transcription...")
    transcription = transcribe_audio(filename)
    print("Transcription:", transcription)

if __name__ == "__main__":
    listen_and_transcribe()
