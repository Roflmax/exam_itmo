"""Step definitions для функционала добавления упражнений."""
import pytest
from pytest_bdd import scenarios, given, when, then, parsers
from datetime import datetime

from gym.models import Exercise
from gym.parser import parse_exercise_input

scenarios('../features/add_exercise.feature')


@given('пользователь авторизован в системе')
def user_authorized(exercise_context):
    """Пользователь авторизован."""
    exercise_context['authorized'] = True


@given('существует дневник тренировок')
def workout_diary_exists(temp_db, exercise_context):
    """База данных инициализирована."""
    exercise_context['db'] = temp_db


@when(parsers.parse('пользователь добавляет упражнение "{exercise_name}"'))
def user_adds_exercise(exercise_context, exercise_name):
    """Пользователь добавляет упражнение."""
    exercise_context['name'] = exercise_name


@when(parsers.parse('указывает вес {weight:d} кг'))
def set_weight(exercise_context, weight):
    """Указывает вес."""
    exercise_context['weight'] = float(weight)


@when(parsers.parse('указывает количество повторений {reps:d}'))
def set_reps(exercise_context, reps):
    """Указывает повторения."""
    exercise_context['reps'] = reps


@when(parsers.parse('указывает количество подходов {sets:d}'))
def set_sets(exercise_context, sets):
    """Указывает подходы."""
    exercise_context['sets'] = sets


@when(parsers.parse('добавляет заметку "{note}"'))
def add_note(exercise_context, note):
    """Добавляет заметку."""
    exercise_context['note'] = note


@then('упражнение должно быть сохранено в дневнике')
def exercise_saved_in_diary(temp_db, exercise_context):
    """Сохраняем и проверяем упражнение."""
    exercise = Exercise(
        id=None,
        name=exercise_context['name'],
        weight=exercise_context['weight'],
        reps=exercise_context['reps'],
        sets=exercise_context['sets'],
        note=exercise_context.get('note'),
        created_at=datetime.now()
    )
    exercise_id = temp_db.add_exercise(exercise)
    exercise_context['exercise'] = exercise
    assert exercise_id is not None


@then(parsers.parse('общий объём нагрузки должен быть {total_volume:d} кг'))
def check_total_volume(exercise_context, total_volume):
    """Проверяем объём."""
    exercise = exercise_context['exercise']
    assert exercise.total_volume == total_volume


@then('заметка должна быть прикреплена к упражнению')
def note_attached_to_exercise(exercise_context):
    """Проверяем заметку."""
    assert exercise_context['note'] is not None
    assert exercise_context['exercise'].note == exercise_context['note']


@when(parsers.parse('пользователь вводит упражнение "{exercise_name}" в формате "{input_format}"'))
def user_inputs_exercise_with_format(exercise_context, exercise_name, input_format):
    """Парсим формат ввода."""
    exercise_context['name'] = exercise_name
    try:
        weight, reps, sets = parse_exercise_input(input_format)
        exercise_context['weight'] = weight
        exercise_context['reps'] = reps
        exercise_context['sets'] = sets
    except ValueError as e:
        exercise_context['error'] = str(e)


@then(parsers.parse('система должна распознать вес {weight:d} кг'))
def system_recognizes_weight(exercise_context, weight):
    """Проверяем вес."""
    assert exercise_context['weight'] == weight


@then(parsers.parse('система должна распознать повторения {reps:d}'))
def system_recognizes_reps(exercise_context, reps):
    """Проверяем повторения."""
    assert exercise_context['reps'] == reps


@then(parsers.parse('система должна распознать подходы {sets:d}'))
def system_recognizes_sets(exercise_context, sets):
    """Проверяем подходы."""
    assert exercise_context['sets'] == sets
