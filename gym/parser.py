"""
Parser module for gym CLI application.
Handles parsing of exercise input in various formats.
"""

import re
from typing import Tuple


# Mapping of Russian number words to their numeric values
UNITS = {
    'ноль': 0, 'один': 1, 'одна': 1, 'два': 2, 'две': 2, 'три': 3,
    'четыре': 4, 'пять': 5, 'шесть': 6, 'семь': 7, 'восемь': 8,
    'девять': 9, 'десять': 10, 'одиннадцать': 11, 'двенадцать': 12,
    'тринадцать': 13, 'четырнадцать': 14, 'пятнадцать': 15,
    'шестнадцать': 16, 'семнадцать': 17, 'восемнадцать': 18,
    'девятнадцать': 19,
}

TENS = {
    'двадцать': 20, 'тридцать': 30, 'сорок': 40, 'пятьдесят': 50,
    'шестьдесят': 60, 'семьдесят': 70, 'восемьдесят': 80, 'девяносто': 90,
}

HUNDREDS = {
    'сто': 100, 'двести': 200, 'триста': 300,
}


def _parse_single_number(words: list[str]) -> int | None:
    """
    Parse a list of Russian number words into a single integer.
    Returns None if parsing fails.
    """
    if not words:
        return None

    total = 0
    has_value = False

    for word in words:
        word_lower = word.lower()
        if word_lower in HUNDREDS:
            total += HUNDREDS[word_lower]
            has_value = True
        elif word_lower in TENS:
            total += TENS[word_lower]
            has_value = True
        elif word_lower in UNITS:
            total += UNITS[word_lower]
            has_value = True
        else:
            # Unknown word - not a number
            return None

    return total if has_value else None


def parse_voice_numbers(text: str) -> str:
    """
    Convert Russian number words to digits.

    Supports numbers from 1 to 300.

    Examples:
        "восемьдесят" -> "80"
        "сто двадцать пять" -> "125"
        "двести" -> "200"

    Args:
        text: Input string potentially containing Russian number words.

    Returns:
        String with Russian number words replaced by digits.
    """
    # Build vocabulary of all known number words
    all_number_words = set(UNITS.keys()) | set(TENS.keys()) | set(HUNDREDS.keys())

    words = text.split()
    result = []
    current_number_words = []

    for word in words:
        word_lower = word.lower()
        if word_lower in all_number_words:
            current_number_words.append(word_lower)
        else:
            # Not a number word - flush accumulated number if any
            if current_number_words:
                parsed = _parse_single_number(current_number_words)
                if parsed is not None:
                    result.append(str(parsed))
                else:
                    # Failed to parse - keep original words
                    result.extend(current_number_words)
                current_number_words = []
            result.append(word)

    # Flush remaining number words
    if current_number_words:
        parsed = _parse_single_number(current_number_words)
        if parsed is not None:
            result.append(str(parsed))
        else:
            result.extend(current_number_words)

    return ' '.join(result)


def parse_exercise_input(input_str: str) -> Tuple[float, int, int]:
    """
    Parse exercise input string into weight, reps, and sets.

    Supported formats:
        - "80kg 8reps 3sets" -> (80, 8, 3)
        - "80kg 8x3" -> (80, 8, 3)
        - "100 5x4" -> (100, 5, 4)
        - "80 8 3" -> (80, 8, 3)
        - "80кг 8x3" -> (80, 8, 3) - Russian "кг" also supported

    Args:
        input_str: Input string containing exercise parameters.

    Returns:
        Tuple of (weight, reps, sets).

    Raises:
        ValueError: If the input format is not recognized.
    """
    # Normalize input: strip whitespace and convert to lowercase
    text = input_str.strip().lower()

    # First, convert any Russian number words to digits
    text = parse_voice_numbers(text)

    # Pattern 1: "80kg 8reps 3sets" or "80кг 8reps 3sets"
    pattern_full = r'^(\d+(?:\.\d+)?)\s*(?:kg|кг)?\s+(\d+)\s*reps?\s+(\d+)\s*sets?$'
    match = re.match(pattern_full, text)
    if match:
        weight = float(match.group(1))
        reps = int(match.group(2))
        sets = int(match.group(3))
        return (weight, reps, sets)

    # Pattern 2: "80kg 8x3" or "80кг 8x3" (weight with unit, then reps x sets)
    pattern_kg_x = r'^(\d+(?:\.\d+)?)\s*(?:kg|кг)\s+(\d+)\s*[xх]\s*(\d+)$'
    match = re.match(pattern_kg_x, text)
    if match:
        weight = float(match.group(1))
        reps = int(match.group(2))
        sets = int(match.group(3))
        return (weight, reps, sets)

    # Pattern 3: "100 5x4" (weight without unit, then reps x sets)
    pattern_x = r'^(\d+(?:\.\d+)?)\s+(\d+)\s*[xх]\s*(\d+)$'
    match = re.match(pattern_x, text)
    if match:
        weight = float(match.group(1))
        reps = int(match.group(2))
        sets = int(match.group(3))
        return (weight, reps, sets)

    # Pattern 4: "80 8 3" (three space-separated numbers)
    pattern_spaces = r'^(\d+(?:\.\d+)?)\s+(\d+)\s+(\d+)$'
    match = re.match(pattern_spaces, text)
    if match:
        weight = float(match.group(1))
        reps = int(match.group(2))
        sets = int(match.group(3))
        return (weight, reps, sets)

    # No pattern matched
    raise ValueError(
        f"Unrecognized input format: '{input_str}'. "
        "Supported formats: '80kg 8reps 3sets', '80kg 8x3', '100 5x4', '80 8 3'"
    )
