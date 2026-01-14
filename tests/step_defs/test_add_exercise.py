"""Step definitions для функционала добавления упражнений в дневник тренировок."""

import pytest
from pytest_bdd import scenarios, given, when, then, parsers

# Загрузка сценариев из feature файла
scenarios('../features/add_exercise.feature')


# === Предыстория (Background) ===

@given('пользователь авторизован в системе')
def user_authorized():
    """Пользователь авторизован в системе."""
    pytest.skip("Реализация будет добавлена позже")


@given('существует дневник тренировок')
def workout_diary_exists():
    """Существует дневник тренировок."""
    pytest.skip("Реализация будет добавлена позже")


# === Шаги для сценария: Добавление упражнения с весом и повторениями ===

@when(parsers.parse('пользователь добавляет упражнение "{exercise_name}"'))
def user_adds_exercise(exercise_name: str):
    """Пользователь добавляет упражнение с заданным названием."""
    pytest.skip("Реализация будет добавлена позже")


@when(parsers.parse('указывает вес {weight:d} кг'))
def set_weight(weight: int):
    """Указывает вес в килограммах."""
    pytest.skip("Реализация будет добавлена позже")


@when(parsers.parse('указывает количество повторений {reps:d}'))
def set_reps(reps: int):
    """Указывает количество повторений."""
    pytest.skip("Реализация будет добавлена позже")


@when(parsers.parse('указывает количество подходов {sets:d}'))
def set_sets(sets: int):
    """Указывает количество подходов."""
    pytest.skip("Реализация будет добавлена позже")


@then('упражнение должно быть сохранено в дневнике')
def exercise_saved_in_diary():
    """Упражнение должно быть сохранено в дневнике."""
    pytest.skip("Реализация будет добавлена позже")


@then(parsers.parse('общий объём нагрузки должен быть {total_volume:d} кг'))
def check_total_volume(total_volume: int):
    """Проверяет общий объём нагрузки (вес * повторения * подходы)."""
    pytest.skip("Реализация будет добавлена позже")


# === Шаги для сценария: Добавление упражнения с заметкой ===

@when(parsers.parse('добавляет заметку "{note}"'))
def add_note(note: str):
    """Добавляет заметку к упражнению."""
    pytest.skip("Реализация будет добавлена позже")


@then('заметка должна быть прикреплена к упражнению')
def note_attached_to_exercise():
    """Заметка должна быть прикреплена к упражнению."""
    pytest.skip("Реализация будет добавлена позже")


# === Шаги для структуры сценария: Парсинг разных форматов ввода ===

@when(parsers.parse('пользователь вводит упражнение "{exercise_name}" в формате "{input_format}"'))
def user_inputs_exercise_with_format(exercise_name: str, input_format: str):
    """Пользователь вводит упражнение в определённом формате."""
    pytest.skip("Реализация будет добавлена позже")


@then(parsers.parse('система должна распознать вес {weight:d} кг'))
def system_recognizes_weight(weight: int):
    """Система должна корректно распознать вес."""
    pytest.skip("Реализация будет добавлена позже")


@then(parsers.parse('система должна распознать повторения {reps:d}'))
def system_recognizes_reps(reps: int):
    """Система должна корректно распознать количество повторений."""
    pytest.skip("Реализация будет добавлена позже")


@then(parsers.parse('система должна распознать подходы {sets:d}'))
def system_recognizes_sets(sets: int):
    """Система должна корректно распознать количество подходов."""
    pytest.skip("Реализация будет добавлена позже")
