"""Step definitions для голосового ввода с LLM."""
import pytest
from pytest_bdd import scenarios, given, when, then, parsers

# Загрузка сценариев
scenarios('../features/telegram_voice.feature')


# Fixtures для хранения состояния теста
@pytest.fixture
def voice_context():
    """Контекст для хранения данных между шагами."""
    return {
        'voice_text': None,
        'llm_command': None,
        'cli_result': None,
        'bot_response': None,
        'error': None
    }


# Background steps
@given('пользователь авторизован в Telegram боте')
def user_authorized(voice_context):
    """Пользователь авторизован."""
    voice_context['authorized'] = True


@given('настроен OpenAI API ключ')
def openai_configured(voice_context):
    """OpenAI API настроен."""
    voice_context['openai_configured'] = True


# When steps
@when(parsers.parse('пользователь говорит "{text}"'))
def user_says(voice_context, text):
    """Пользователь отправляет голосовое сообщение."""
    voice_context['voice_text'] = text
    # TODO: Вызвать LLM парсер
    pytest.skip("Реализация LLM парсера будет добавлена")


# Then steps
@then(parsers.parse("LLM формирует команду '{command}'"))
def llm_forms_command(voice_context, command):
    """Проверка что LLM сформировал правильную команду."""
    # TODO: Проверить результат LLM
    pytest.skip("Реализация проверки LLM будет добавлена")


@then('CLI выполняется успешно')
def cli_executes_successfully(voice_context):
    """CLI команда выполнена успешно."""
    # TODO: Проверить returncode == 0
    pytest.skip("Реализация проверки CLI будет добавлена")


@then('бот отвечает подтверждением добавления')
def bot_confirms_addition(voice_context):
    """Бот отправил подтверждение."""
    # TODO: Проверить что ответ содержит "Записал" или подобное
    pytest.skip("Реализация проверки ответа будет добавлена")


@then('бот отправляет результат выполнения')
def bot_sends_result(voice_context):
    """Бот отправил результат CLI."""
    # TODO: Проверить что stdout передан пользователю
    pytest.skip("Реализация проверки результата будет добавлена")


@then('LLM возвращает сообщение об ошибке')
def llm_returns_error(voice_context):
    """LLM вернул ошибку вместо команды."""
    # TODO: Проверить что error != None
    pytest.skip("Реализация проверки ошибки будет добавлена")


@then(parsers.parse('бот отвечает "{message}"'))
def bot_responds_with_message(voice_context, message):
    """Бот отправил конкретное сообщение."""
    # TODO: Проверить текст ответа
    pytest.skip("Реализация проверки сообщения будет добавлена")
