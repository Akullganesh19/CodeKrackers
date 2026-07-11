import os
from groq import Groq
from backend.core.config import settings

client = None
if settings.GROQ_API_KEY:
    client = Groq(api_key=settings.GROQ_API_KEY)

def get_groq_client() -> Groq:  # noqa: E302
    if not client:
        raise ValueError("GROQ_API_KEY is not set")
    return client

async def transcribe_audio(file_path: str) -> str:  # noqa: E302
    """
    Transcribe audio using Groq's Whisper API.
    """
    if not client:
        return ""
      # noqa: E114,W293
    with open(file_path, "rb") as file:
        transcription = client.audio.transcriptions.create(
            file=(os.path.basename(file_path), file.read()),
            model="whisper-large-v3",
            response_format="text"
        )
    return transcription
