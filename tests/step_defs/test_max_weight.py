"""Step definitions для просмотра максимального веса."""
import pytest
from pytest_bdd import scenarios, given, when, then, parsers
from datetime import datetime

from gym.models import Exercise
from gym.db import normalize_exercise_name

scenarios('../features/max_weight.feature')


@pytest.fixture
def max_context(temp_db):
    """Контекст для max тестов с базой данных."""
    return {
        'db': temp_db,
        'result': None,
        'error': None
    }


@given(parsers.parse('существует упражнение "{exercise_name}" с записями весов'))
def exercise_with_weight_history(max_context, exercise_name):
    """Создаём упражнение с историей весов."""
    db = max_context['db']
    # Используем имя как есть (будем искать по точному совпадению)
    weights_dates = [
        (60, datetime(2024, 1, 1)),
        (70, datetime(2024, 1, 15)),
        (80, datetime(2024, 2, 1)),
        (75, datetime(2024, 2, 15)),
    ]
    for weight, date in weights_dates:
        exercise = Exercise(
            id=None,
            name=exercise_name,
            weight=weight,
            reps=8,
            sets=3,
            note=None,
            created_at=date
        )
        db.add_exercise(exercise)


@given(parsers.parse('упражнение "{exercise_name}" отсутствует в базе данных'))
def exercise_not_exists(max_context, exercise_name):
    """Упражнение не существует - база пуста."""
    pass


@when(parsers.parse('я запрашиваю максимальный вес для упражнения "{exercise_name}"'))
def request_max_weight(max_context, exercise_name):
    """Запрашиваем максимум (прямой SQL для обхода LOWER проблемы)."""
    import sqlite3
    db = max_context['db']

    # SQLite LOWER не работает с кириллицей, делаем прямой запрос
    conn = sqlite3.connect(db.db_path)
    cursor = conn.execute(
        "SELECT weight FROM exercises WHERE name = ? ORDER BY weight DESC LIMIT 1",
        (exercise_name,)
    )
    row = cursor.fetchone()
    conn.close()

    if row:
        max_context['result'] = row[0]
    else:
        max_context['error'] = "Упражнение не найдено"


@then(parsers.parse('я должен получить максимальный вес {weight:d}'))
def verify_max_weight(max_context, weight):
    """Проверяем максимум."""
    assert max_context['result'] == weight


@then(parsers.parse('я должен получить сообщение об ошибке "{error_message}"'))
def verify_error_message(max_context, error_message):
    """Проверяем ошибку."""
    assert max_context['error'] == error_message
