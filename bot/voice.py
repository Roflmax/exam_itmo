"""
Voice recognition module for Gym Telegram bot.
Uses OpenAI Whisper API for speech-to-text conversion.
"""

import os

from openai import AsyncOpenAI


def _get_openai_client() -> AsyncOpenAI:
    """Get AsyncOpenAI client with API key from environment."""
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError(
            "OPENAI_API_KEY environment variable is not set. "
            "Please set it to use voice recognition."
        )
    return AsyncOpenAI(api_key=api_key)


async def transcribe_voice(voice_file_path: str) -> str:
    """
    Transcribe voice message using OpenAI Whisper API.

    Args:
        voice_file_path: Path to the voice file (.ogg format supported).

    Returns:
        Transcribed text from the voice message.

    Raises:
        FileNotFoundError: If the voice file doesn't exist.
        ValueError: If OPENAI_API_KEY is not set.
        Exception: If transcription fails.
    """
    # Check if file exists
    if not os.path.exists(voice_file_path):
        raise FileNotFoundError(f"Voice file not found: {voice_file_path}")

    try:
        client = _get_openai_client()

        # Open and send file to Whisper API
        with open(voice_file_path, "rb") as audio_file:
            transcription = await client.audio.transcriptions.create(
                model="whisper-1",
                file=audio_file,
                language="ru",  # Russian language
                response_format="text"
            )

        return transcription.strip()

    except ValueError:
        # Re-raise ValueError for missing API key
        raise
    except FileNotFoundError:
        # Re-raise FileNotFoundError
        raise
    except Exception as e:
        raise Exception(f"Failed to transcribe voice: {str(e)}")
