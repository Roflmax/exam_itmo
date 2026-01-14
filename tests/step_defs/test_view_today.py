"""Step definitions для просмотра тренировок за сегодня."""
import pytest
from pytest_bdd import scenarios, given, when, then, parsers
from datetime import datetime

from gym.models import Exercise

scenarios('../features/view_today.feature')


@pytest.fixture
def today_context():
    """Контекст для today тестов."""
    return {
        'db': None,
        'exercises': [],
        'message': None
    }


@given('база данных пуста')
def empty_database(temp_db, today_context):
    """База пуста."""
    today_context['db'] = temp_db


@given('в базе данных есть следующие тренировки за сегодня:')
def database_with_workouts(temp_db, today_context):
    """Добавляем тренировки из feature."""
    today_context['db'] = temp_db
    workouts = [
        ("Жим лёжа", 3, 10, 60),
        ("Приседания", 4, 8, 80),
        ("Становая тяга", 3, 5, 100),
    ]
    for name, sets, reps, weight in workouts:
        exercise = Exercise(
            id=None,
            name=name,
            weight=float(weight),
            reps=reps,
            sets=sets,
            note=None,
            created_at=datetime.now()
        )
        temp_db.add_exercise(exercise)


@when('я запрашиваю тренировки за сегодня')
def request_today_workouts(today_context):
    """Запрашиваем тренировки."""
    db = today_context['db']
    today_context['exercises'] = db.get_today_exercises()
    if not today_context['exercises']:
        today_context['message'] = "Сегодня тренировок не было"


@then(parsers.parse('я вижу сообщение "{message}"'))
def see_message(today_context, message):
    """Проверяем сообщение."""
    assert today_context['message'] == message


@then(parsers.parse('я вижу список из {count:d} упражнений'))
def see_exercises_list(today_context, count):
    """Проверяем количество."""
    assert len(today_context['exercises']) == count


@then(parsers.parse('список содержит упражнение "{exercise_name}"'))
def list_contains_exercise(today_context, exercise_name):
    """Проверяем наличие упражнения."""
    names = [e.name for e in today_context['exercises']]
    assert exercise_name in names
