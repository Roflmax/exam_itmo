"""
LLM-based parser for voice commands.
Uses OpenAI GPT to understand natural language and convert to CLI commands.
"""

import json
import os
from typing import Optional

from openai import AsyncOpenAI


# System prompt for LLM
SYSTEM_PROMPT = """Ты - парсер команд для CLI приложения gym (дневник тренировок).

Доступные команды:
- gym add "название" <вес>kg <повторения>reps <подходы>sets [--note "заметка"]
- gym today
- gym max "название"
- gym last "название"
- gym progress "название"

Правила:
1. Преобразуй числа прописью в цифры (восемьдесят → 80, сто двадцать → 120)
2. Определи intent пользователя из контекста
3. Сформируй точную CLI команду
4. Название упражнения всегда в кавычках
5. Если упоминается боль/дискомфорт/заметка - добавь --note
6. Если запрос не про тренировки - верни error

Примеры:
- "добавь жим лёжа 80 кг 8 раз 3 подхода" → gym add "жим лёжа" 80kg 8reps 3sets
- "сделал присед сто двадцать на 5 по 4, колено болит" → gym add "присед" 120kg 5reps 4sets --note "колено болит"
- "что сегодня делал" → gym today
- "покажи тренировку за сегодня" → gym today
- "какой мой максимум на жиме" → gym max "жим"
- "когда последний раз делал становую" → gym last "становая"

Ответь ТОЛЬКО валидным JSON без markdown:
{"command": "gym ...", "error": null}
или
{"command": null, "error": "Я помогаю только с тренировками. Скажи что добавить или спроси про статистику."}
"""


def _get_openai_client() -> AsyncOpenAI:
    """Get AsyncOpenAI client with API key from environment."""
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError(
            "OPENAI_API_KEY environment variable is not set. "
            "Please set it to use LLM parsing."
        )
    return AsyncOpenAI(api_key=api_key)


async def parse_voice_with_llm(text: str) -> dict:
    """
    Parse voice command using LLM (GPT-4o-mini).

    Args:
        text: Transcribed text from voice message.

    Returns:
        Dictionary with:
            - "command": CLI command string or None
            - "error": Error message or None

    Examples:
        >>> await parse_voice_with_llm("добавь жим 80 кг 8 раз 3 подхода")
        {"command": 'gym add "жим" 80kg 8reps 3sets', "error": None}

        >>> await parse_voice_with_llm("расскажи анекдот")
        {"command": None, "error": "Я помогаю только с тренировками..."}
    """
    try:
        client = _get_openai_client()

        response = await client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": text}
            ],
            temperature=0.1,  # Low temperature for consistent parsing
            max_tokens=200
        )

        # Extract response content
        content = response.choices[0].message.content
        if not content:
            return {"command": None, "error": "Пустой ответ от LLM"}

        # Parse JSON response
        try:
            result = json.loads(content.strip())
            return {
                "command": result.get("command"),
                "error": result.get("error")
            }
        except json.JSONDecodeError:
            # If LLM returned invalid JSON, try to extract command
            if content.strip().startswith("gym "):
                return {"command": content.strip(), "error": None}
            return {"command": None, "error": f"Не удалось распознать: {content}"}

    except ValueError as e:
        # API key not set
        return {"command": None, "error": str(e)}
    except Exception as e:
        return {"command": None, "error": f"Ошибка LLM: {str(e)}"}


async def execute_cli_command(command: str) -> tuple[bool, str]:
    """
    Execute gym CLI command via subprocess.

    Args:
        command: CLI command to execute (e.g., 'gym add "жим" 80kg 8reps 3sets')

    Returns:
        Tuple of (success: bool, output: str)
    """
    import asyncio

    try:
        # Run command asynchronously
        process = await asyncio.create_subprocess_shell(
            command,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )

        stdout, stderr = await process.communicate()

        if process.returncode == 0:
            output = stdout.decode('utf-8').strip()
            return True, output if output else "Команда выполнена"
        else:
            error = stderr.decode('utf-8').strip()
            return False, error if error else "Ошибка выполнения команды"

    except Exception as e:
        return False, f"Ошибка: {str(e)}"
