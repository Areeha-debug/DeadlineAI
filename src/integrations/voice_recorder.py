import os
import tempfile
import datetime
import sounddevice as sd
from scipy.io import wavfile
from openai import OpenAI


def record_voice_task(duration=5):
    fs = 44100  # Sample rate
    temp_wav_path = None

    try:
        # Record audio
        recording = sd.rec(int(duration * fs), samplerate=fs,
                           channels=1, dtype='int16')
        sd.wait()  # Wait until recording is finished

        # Save to temp file
        temp_fd, temp_wav_path = tempfile.mkstemp(suffix=".wav")
        os.close(temp_fd)  # Close file descriptor so wavfile.write can open it
        wavfile.write(temp_wav_path, fs, recording)

        # Transcribe with Whisper
        openai_api_key = os.environ.get("OPENAI_API_KEY")
        if not openai_api_key:
            raise ValueError("OPENAI_API_KEY environment variable is not set")

        client = OpenAI(api_key=openai_api_key)
        with open(temp_wav_path, "rb") as audio_file:
            transcript = client.audio.transcriptions.create(
                model="whisper-1",
                file=audio_file
            )

        return transcript.text

    except Exception as e:
        raise RuntimeError(f"Failed to record or transcribe voice task: {e}")

    finally:
        # Ensure cleanup of the temporary file
        if temp_wav_path and os.path.exists(temp_wav_path):
            try:
                os.remove(temp_wav_path)
            except Exception as e:
                print(
                    f"Warning: failed to delete temp file {temp_wav_path}: {e}")


def add_voice_task(duration=5):
    transcript = record_voice_task(duration)

    task = {
        "source": "voice",
        "title": transcript,
        "timestamp": datetime.datetime.now().isoformat(),
        "priority": None
    }

    print(f"Voice task captured: {transcript}")
    return task
