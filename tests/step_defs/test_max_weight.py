"""Step definitions для функционала просмотра максимального веса."""
import pytest
from pytest_bdd import scenarios, given, when, then, parsers

# Загрузка сценариев из feature файла
scenarios('../features/max_weight.feature')


@given(parsers.parse('существует упражнение "{exercise_name}" с записями весов'))
def exercise_with_weight_history(exercise_name):
    """Создание упражнения с историей весов."""
    # TODO: Реализовать создание упражнения с записями весов из таблицы
    pytest.skip("Реализация будет добавлена позже")


@given(parsers.parse('упражнение "{exercise_name}" отсутствует в базе данных'))
def exercise_not_exists(exercise_name):
    """Проверка отсутствия упражнения в базе данных."""
    # TODO: Реализовать проверку отсутствия упражнения
    pytest.skip("Реализация будет добавлена позже")


@when(parsers.parse('я запрашиваю максимальный вес для упражнения "{exercise_name}"'))
def request_max_weight(exercise_name):
    """Запрос максимального веса для упражнения."""
    # TODO: Реализовать запрос максимального веса
    pytest.skip("Реализация будет добавлена позже")


@then(parsers.parse('я должен получить максимальный вес {weight:d}'))
def verify_max_weight(weight):
    """Проверка полученного максимального веса."""
    # TODO: Реализовать проверку максимального веса
    pytest.skip("Реализация будет добавлена позже")


@then(parsers.parse('я должен получить сообщение об ошибке "{error_message}"'))
def verify_error_message(error_message):
    """Проверка сообщения об ошибке."""
    # TODO: Реализовать проверку сообщения об ошибке
    pytest.skip("Реализация будет добавлена позже")
