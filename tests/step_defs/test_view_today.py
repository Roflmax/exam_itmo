"""Step definitions для просмотра тренировок за сегодня."""
import pytest
from pytest_bdd import scenarios, given, when, then, parsers

# Загрузка сценариев из feature файла
scenarios('../features/view_today.feature')


@given('база данных пуста')
def empty_database(temp_db):
    """Подготовка пустой базы данных."""
    pytest.skip("Реализация будет добавлена позже")


@given(parsers.parse('в базе данных есть следующие тренировки за сегодня:\n{table}'))
def database_with_workouts(temp_db, table):
    """Подготовка базы данных с тренировками."""
    pytest.skip("Реализация будет добавлена позже")


@when('я запрашиваю тренировки за сегодня')
def request_today_workouts():
    """Запрос тренировок за сегодняшний день."""
    pytest.skip("Реализация будет добавлена позже")


@then(parsers.parse('я вижу сообщение "{message}"'))
def see_message(message):
    """Проверка отображения сообщения."""
    pytest.skip("Реализация будет добавлена позже")


@then(parsers.parse('я вижу список из {count:d} упражнений'))
def see_exercises_list(count):
    """Проверка количества упражнений в списке."""
    pytest.skip("Реализация будет добавлена позже")


@then(parsers.parse('список содержит упражнение "{exercise_name}"'))
def list_contains_exercise(exercise_name):
    """Проверка наличия упражнения в списке."""
    pytest.skip("Реализация будет добавлена позже")
