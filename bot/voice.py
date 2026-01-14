"""
Voice recognition module for Gym Telegram bot.
Uses OpenAI Whisper API for speech-to-text conversion.
"""

import os
import re
from typing import Optional

from openai import AsyncOpenAI

from gym.parser import parse_voice_numbers


# Initialize OpenAI client (API key from environment variable)
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


def parse_voice_command(text: str) -> dict:
    """
    Parse voice command text and determine the user's intent.

    Args:
        text: Transcribed text from voice message.

    Returns:
        Dictionary with:
            - "command": "add" | "today" | "max" | "last" | "unknown"
            - "exercise_name": str (if applicable)
            - "params": str (if applicable, formatted as "weight repsXsets")

    Examples:
        - "добавь жим лёжа восемьдесят кило восемь на три"
          -> {"command": "add", "exercise_name": "жим лёжа", "params": "80 8x3"}
        - "что я сегодня делал"
          -> {"command": "today"}
        - "какой у меня максимум на приседе"
          -> {"command": "max", "exercise_name": "присед"}
        - "когда последний раз делал становую"
          -> {"command": "last", "exercise_name": "становая"}
    """
    # Normalize text: lowercase and strip
    text_lower = text.lower().strip()

    # Convert Russian number words to digits
    text_converted = parse_voice_numbers(text_lower)

    # Patterns for different commands

    # ADD command patterns
    add_patterns = [
        r'^добавь\s+',
        r'^добавить\s+',
        r'^запиши\s+',
        r'^записать\s+',
        r'^сделал\s+',
    ]

    for pattern in add_patterns:
        if re.match(pattern, text_converted):
            return _parse_add_command(text_converted, pattern)

    # TODAY command patterns
    today_patterns = [
        r'что.*сегодня',
        r'сегодня.*делал',
        r'сегодняшн',
        r'тренировк.*сегодня',
        r'покажи.*сегодня',
    ]

    for pattern in today_patterns:
        if re.search(pattern, text_converted):
            return {"command": "today"}

    # MAX command patterns
    max_patterns = [
        r'максимум',
        r'макс\b',
        r'рекорд',
        r'лучший\s+результат',
        r'максимальн',
    ]

    for pattern in max_patterns:
        if re.search(pattern, text_converted):
            return _parse_max_command(text_converted)

    # LAST command patterns
    last_patterns = [
        r'последний\s+раз',
        r'когда.*делал',
        r'когда.*последн',
        r'в\s+последний',
    ]

    for pattern in last_patterns:
        if re.search(pattern, text_converted):
            return _parse_last_command(text_converted)

    # Unknown command
    return {"command": "unknown"}


def _parse_add_command(text: str, matched_pattern: str) -> dict:
    """
    Parse ADD command to extract exercise name and parameters.

    Args:
        text: Normalized and converted text.
        matched_pattern: The pattern that matched the ADD command.

    Returns:
        Dictionary with command="add", exercise_name, and params.
    """
    # Remove the command prefix
    remainder = re.sub(matched_pattern, '', text).strip()

    # Try to extract weight, reps, sets from the end
    # Pattern: exercise_name ... weight (кило/кг) reps (на/x) sets
    # Example: "жим лёжа 80 кило 8 на 3" or "жим лёжа 80 8 3"

    # Pattern for: weight (кило/кг) reps (на/x/раз) sets
    params_pattern = r'(\d+)\s*(?:кило|кг|килограмм)?\s+(\d+)\s*(?:на|x|х|раз|повтор\w*)?\s*(\d+)\s*$'
    match = re.search(params_pattern, remainder)

    if match:
        weight = match.group(1)
        reps = match.group(2)
        sets = match.group(3)

        # Extract exercise name (everything before the params)
        exercise_name = remainder[:match.start()].strip()

        # Clean up exercise name - remove trailing prepositions and noise
        exercise_name = re.sub(r'\s+(на|по|с|в)\s*$', '', exercise_name)
        exercise_name = exercise_name.strip()

        # Format params as "weight repsXsets"
        params = f"{weight} {reps}x{sets}"

        return {
            "command": "add",
            "exercise_name": exercise_name,
            "params": params
        }

    # Try simpler pattern: just three numbers at the end
    simple_pattern = r'(\d+)\s+(\d+)\s+(\d+)\s*$'
    match = re.search(simple_pattern, remainder)

    if match:
        weight = match.group(1)
        reps = match.group(2)
        sets = match.group(3)

        exercise_name = remainder[:match.start()].strip()
        params = f"{weight} {reps}x{sets}"

        return {
            "command": "add",
            "exercise_name": exercise_name,
            "params": params
        }

    # Could not parse params - return what we have
    return {
        "command": "add",
        "exercise_name": remainder,
        "params": ""
    }


def _parse_max_command(text: str) -> dict:
    """
    Parse MAX command to extract exercise name.

    Args:
        text: Normalized and converted text.

    Returns:
        Dictionary with command="max" and exercise_name if found.
    """
    exercise_name = _extract_exercise_name(text)

    result = {"command": "max"}
    if exercise_name:
        result["exercise_name"] = exercise_name

    return result


def _parse_last_command(text: str) -> dict:
    """
    Parse LAST command to extract exercise name.

    Args:
        text: Normalized and converted text.

    Returns:
        Dictionary with command="last" and exercise_name if found.
    """
    exercise_name = _extract_exercise_name(text)

    result = {"command": "last"}
    if exercise_name:
        result["exercise_name"] = exercise_name

    return result


def _extract_exercise_name(text: str) -> Optional[str]:
    """
    Extract exercise name from text by looking for known exercise patterns.

    Args:
        text: Input text to search.

    Returns:
        Extracted exercise name or None.
    """
    # Common exercise names in Russian (nominative, genitive, prepositional cases)
    exercise_patterns = {
        # Жим лёжа variations
        r'жим[еуа]?\s*л[её]жа': 'жим лёжа',
        r'жим\b': 'жим',

        # Присед variations
        r'присед[еуа]?': 'присед',
        r'приседани[яие]': 'присед',

        # Становая variations
        r'станов[ауо][яйю]': 'становая',
        r'становой': 'становая',
        r'становую': 'становая',

        # Подтягивания
        r'подтягивани[яие]': 'подтягивания',

        # Тяга variations
        r'тяг[уае]': 'тяга',

        # Отжимания
        r'отжимани[яие]': 'отжимания',
    }

    for pattern, exercise in exercise_patterns.items():
        if re.search(pattern, text):
            return exercise

    return None
