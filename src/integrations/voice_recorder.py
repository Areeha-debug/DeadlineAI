import os
import datetime
from groq import Groq

def add_voice_task(audio_file):
    groq_api_key = os.environ.get("GROQ_API_KEY")
    if not groq_api_key:
        raise ValueError("GROQ_API_KEY environment variable is not set")
    
    client = Groq(api_key=groq_api_key)
    
    # We pass the file name and the bytes to the Groq client
    # The audio_file comes directly from st.audio_input
    try:
        transcript = client.audio.transcriptions.create(
            file=("audio.wav", audio_file.getvalue()),
            model="whisper-large-v3",
            response_format="json",
        )
    except Exception as e:
        raise RuntimeError(f"Failed to transcribe voice task: {e}")

    task = {
        "source": "voice",
        "title": transcript.text,
        "timestamp": datetime.datetime.now().isoformat(),
        "priority": None
    }

    print(f"Voice task captured: {transcript.text}")
    return task
