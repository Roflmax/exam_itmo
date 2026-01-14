"""
Telegram bot handlers for gym application.

Provides command handlers for managing workout exercises.
"""

import os
import re
from datetime import datetime
from pathlib import Path

from aiogram import F, Router
from aiogram.filters import Command, CommandStart
from aiogram.types import Message

from gym.db import Database
from gym.models import Exercise
from gym.parser import parse_exercise_input, parse_voice_numbers

from .voice import transcribe_voice
from .llm_parser import parse_voice_with_llm, execute_cli_command

# Initialize router
router = Router()

# Database path
DB_PATH = Path.home() / ".gym" / "gym.db"


def get_db() -> Database:
    """Get database instance and ensure it's initialized."""
    db = Database(str(DB_PATH))
    db.init_db()
    return db


@router.message(CommandStart())
async def cmd_start(message: Message) -> None:
    """Handle /start command - welcome message with instructions."""
    welcome_text = """
Привет! Я бот для отслеживания тренировок в зале.

Как использовать:

1. Добавить упражнение:
   /add жим лежа 80 8 3 хорошая форма
   или просто напиши: жим лежа 80 8x3

2. Посмотреть сегодняшние тренировки:
   /today

3. Узнать максимальный вес:
   /max жим лежа

4. Последняя тренировка:
   /last приседания

Формат добавления:
название вес повторения подходы [заметка]

Примеры:
- жим 80 8x3
- приседания 100кг 5x4
- становая 120 5 3 новый рекорд

Напиши /help для списка команд.
"""
    await message.answer(welcome_text.strip())


@router.message(Command("help"))
async def cmd_help(message: Message) -> None:
    """Handle /help command - list of available commands."""
    help_text = """
Доступные команды:

/start - Приветствие и инструкция
/help - Список команд

/add название вес повторения подходы [заметка]
    Добавить упражнение
    Пример: /add жим лежа 80 8 3 легко

/today - Показать все упражнения за сегодня

/max название - Максимальный вес для упражнения
    Пример: /max жим лежа

/last название - Последняя тренировка упражнения
    Пример: /last приседания

Быстрое добавление (без команды):
    жим 80 8x3
    приседания 100кг 5x4
    становая 120 5 3
"""
    await message.answer(help_text.strip())


@router.message(Command("add"))
async def cmd_add(message: Message) -> None:
    """
    Handle /add command - add a new exercise.

    Format: /add название вес повторения подходы [заметка]
    Examples:
        /add жим лежа 80 8 3
        /add приседания 100 5 4 тяжело было
    """
    if not message.text:
        await message.answer("Ошибка: пустое сообщение")
        return

    # Remove /add command prefix
    text = message.text[4:].strip()

    if not text:
        await message.answer(
            "Использование: /add название вес повторения подходы [заметка]\n"
            "Пример: /add жим лежа 80 8 3"
        )
        return

    try:
        exercise = parse_add_input(text)
        db = get_db()
        exercise_id = db.add_exercise(exercise)

        response = (
            f"Упражнение добавлено (ID: {exercise_id}):\n"
            f"{exercise}"
        )
        await message.answer(response)
    except ValueError as e:
        await message.answer(f"Ошибка: {e}")


@router.message(Command("today"))
async def cmd_today(message: Message) -> None:
    """Handle /today command - show today's exercises."""
    db = get_db()
    exercises = db.get_today_exercises()

    if not exercises:
        await message.answer("Сегодня тренировок пока не было. Пора в зал!")
        return

    lines = ["Тренировки за сегодня:", ""]
    total_volume = 0.0

    for i, ex in enumerate(exercises, 1):
        time_str = ex.created_at.strftime("%H:%M")
        note_str = f" ({ex.note})" if ex.note else ""
        lines.append(
            f"{i}. [{time_str}] {ex.name}: {ex.weight}кг x {ex.reps} x {ex.sets}{note_str}"
        )
        total_volume += ex.total_volume

    lines.append("")
    lines.append(f"Всего упражнений: {len(exercises)}")
    lines.append(f"Общий объем: {total_volume:.0f} кг")

    await message.answer("\n".join(lines))


@router.message(Command("max"))
async def cmd_max(message: Message) -> None:
    """
    Handle /max command - show maximum weight for an exercise.

    Format: /max название
    Example: /max жим лежа
    """
    if not message.text:
        await message.answer("Ошибка: пустое сообщение")
        return

    # Remove /max command prefix
    exercise_name = message.text[4:].strip()

    if not exercise_name:
        await message.answer(
            "Использование: /max название\n"
            "Пример: /max жим лежа"
        )
        return

    db = get_db()
    result = db.get_max_weight(exercise_name)

    if result is None:
        await message.answer(f"Упражнение '{exercise_name}' не найдено в базе.")
        return

    weight, date = result
    date_str = date.strftime("%d.%m.%Y")

    await message.answer(
        f"Максимальный вес для '{exercise_name}':\n"
        f"{weight} кг ({date_str})"
    )


@router.message(Command("last"))
async def cmd_last(message: Message) -> None:
    """
    Handle /last command - show last exercise record.

    Format: /last название
    Example: /last приседания
    """
    if not message.text:
        await message.answer("Ошибка: пустое сообщение")
        return

    # Remove /last command prefix
    exercise_name = message.text[5:].strip()

    if not exercise_name:
        await message.answer(
            "Использование: /last название\n"
            "Пример: /last приседания"
        )
        return

    db = get_db()
    exercise = db.get_last_exercise(exercise_name)

    if exercise is None:
        await message.answer(f"Упражнение '{exercise_name}' не найдено в базе.")
        return

    date_str = exercise.created_at.strftime("%d.%m.%Y %H:%M")
    note_str = f"\nЗаметка: {exercise.note}" if exercise.note else ""

    await message.answer(
        f"Последняя тренировка '{exercise.name}':\n"
        f"Дата: {date_str}\n"
        f"Вес: {exercise.weight} кг\n"
        f"Повторения: {exercise.reps}\n"
        f"Подходы: {exercise.sets}"
        f"{note_str}"
    )


def parse_add_input(text: str) -> Exercise:
    """
    Parse input text for adding exercise.

    Expected format: название вес повторения подходы [заметка]
    or: название вес повторенияxподходы [заметка]

    Args:
        text: Input string from user

    Returns:
        Exercise object ready to be saved

    Raises:
        ValueError: If parsing fails
    """
    # Convert Russian number words to digits
    text = parse_voice_numbers(text)

    # Pattern for "название вес повторенияxподходы [заметка]"
    # Example: "жим лежа 80 8x3 было легко"
    pattern_x = r'^(.+?)\s+(\d+(?:\.\d+)?)\s*(?:кг|kg)?\s+(\d+)\s*[xх]\s*(\d+)(?:\s+(.*))?$'
    match = re.match(pattern_x, text, re.IGNORECASE)

    if match:
        name = match.group(1).strip()
        weight = float(match.group(2))
        reps = int(match.group(3))
        sets = int(match.group(4))
        note = match.group(5).strip() if match.group(5) else None

        return Exercise(
            id=None,
            name=name,
            weight=weight,
            reps=reps,
            sets=sets,
            note=note,
            created_at=datetime.now()
        )

    # Pattern for "название вес повторения подходы [заметка]"
    # Example: "жим лежа 80 8 3 было легко"
    pattern_spaces = r'^(.+?)\s+(\d+(?:\.\d+)?)\s*(?:кг|kg)?\s+(\d+)\s+(\d+)(?:\s+(.*))?$'
    match = re.match(pattern_spaces, text, re.IGNORECASE)

    if match:
        name = match.group(1).strip()
        weight = float(match.group(2))
        reps = int(match.group(3))
        sets = int(match.group(4))
        note = match.group(5).strip() if match.group(5) else None

        return Exercise(
            id=None,
            name=name,
            weight=weight,
            reps=reps,
            sets=sets,
            note=note,
            created_at=datetime.now()
        )

    raise ValueError(
        "Неверный формат. Используйте:\n"
        "название вес повторения подходы [заметка]\n"
        "Пример: жим лежа 80 8 3 или жим 80 8x3"
    )


@router.message(F.text)
async def handle_text_message(message: Message) -> None:
    """
    Handle text messages for quick exercise adding without /add command.

    Examples:
        "жим 80 8x3" -> adds exercise
        "приседания 100кг 5x4 тяжело" -> adds exercise with note
    """
    if not message.text:
        return

    text = message.text.strip()

    # Skip if message starts with / (unrecognized command)
    if text.startswith("/"):
        await message.answer(
            "Неизвестная команда. Напиши /help для списка команд."
        )
        return

    # Try to parse as exercise input
    try:
        exercise = parse_add_input(text)
        db = get_db()
        exercise_id = db.add_exercise(exercise)

        response = (
            f"Упражнение добавлено (ID: {exercise_id}):\n"
            f"{exercise}"
        )
        await message.answer(response)
    except ValueError:
        # Not a valid exercise format - provide help
        await message.answer(
            "Не удалось распознать упражнение.\n\n"
            "Формат: название вес повторенияxподходы [заметка]\n"
            "Примеры:\n"
            "- жим 80 8x3\n"
            "- приседания 100кг 5x4\n"
            "- становая 120 5 3 новый рекорд\n\n"
            "Напиши /help для списка команд."
        )


@router.message(F.voice)
async def handle_voice_message(message: Message) -> None:
    """
    Handle voice messages using LLM-based parsing.

    Flow:
    1. Whisper API transcribes voice to text
    2. LLM (GPT-4o-mini) parses text to CLI command
    3. subprocess executes CLI command
    4. Result sent to user

    Supports any natural language formulation:
    - "добавь жим лёжа восемьдесят кило восемь на три"
    - "запиши что я сделал присед сто двадцать на пять"
    - "что я сегодня натренировал"
    - "какой у меня рекорд в становой"
    """
    if not message.voice or not message.bot:
        return

    try:
        # Step 1: Download voice file
        file = await message.bot.get_file(message.voice.file_id)
        if not file.file_path:
            await message.answer("Не удалось получить голосовое сообщение")
            return

        import tempfile
        import os

        with tempfile.NamedTemporaryFile(suffix=".ogg", delete=False) as tmp:
            tmp_path = tmp.name

        await message.bot.download_file(file.file_path, tmp_path)

        # Step 2: Transcribe voice with Whisper
        await message.answer("Распознаю голос...")
        text = await transcribe_voice(tmp_path)

        # Clean up temp file
        os.unlink(tmp_path)

        if not text:
            await message.answer("Не удалось распознать речь. Попробуйте ещё раз.")
            return

        await message.answer(f"Распознано: {text}")

        # Step 3: Parse with LLM
        parsed = await parse_voice_with_llm(text)

        # Check for error from LLM
        if parsed.get("error"):
            await message.answer(parsed["error"])
            return

        command = parsed.get("command")
        if not command:
            await message.answer("Не удалось распознать команду. Попробуйте иначе.")
            return

        # Step 4: Execute CLI command
        await message.answer(f"Выполняю: {command}")
        success, output = await execute_cli_command(command)

        # Step 5: Send result to user
        if success:
            await message.answer(output)
        else:
            await message.answer(f"Ошибка: {output}")

    except Exception as e:
        await message.answer(f"Ошибка обработки голоса: {e}")
