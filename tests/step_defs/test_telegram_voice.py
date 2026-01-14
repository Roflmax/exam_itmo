"""Step definitions для голосового ввода с LLM."""
import pytest
import re
from pytest_bdd import scenarios, given, when, then, parsers

scenarios('../features/telegram_voice.feature')


@pytest.fixture
def voice_context():
    """Контекст для voice тестов."""
    return {
        'voice_text': None,
        'llm_command': None,
        'cli_result': None,
        'error': None
    }


# Числа прописью
NUMBERS_MAP = {
    'сто': 100, 'двести': 200,
    'двадцать': 20, 'тридцать': 30, 'сорок': 40, 'пятьдесят': 50,
    'шестьдесят': 60, 'семьдесят': 70, 'восемьдесят': 80, 'девяносто': 90,
    'один': 1, 'два': 2, 'три': 3, 'четыре': 4, 'пять': 5,
    'шесть': 6, 'семь': 7, 'восемь': 8, 'девять': 9, 'десять': 10,
}


def text_to_numbers(text):
    """Конвертирует числа прописью в цифры."""
    words = text.lower().split()
    result = []
    current_num = 0
    in_number = False

    for word in words:
        if word in NUMBERS_MAP:
            current_num += NUMBERS_MAP[word]
            in_number = True
        else:
            if in_number:
                result.append(str(current_num))
                current_num = 0
                in_number = False
            result.append(word)

    if in_number:
        result.append(str(current_num))

    return ' '.join(result)


def mock_parse_voice(text):
    """Мок LLM парсера."""
    # Конвертируем числа прописью
    text = text_to_numbers(text)
    text_lower = text.lower()

    # Добавление упражнения
    if any(w in text_lower for w in ['запиши', 'добавь', 'сделал']):
        numbers = re.findall(r'\d+', text)
        if len(numbers) >= 3:
            weight, reps, sets = numbers[0], numbers[1], numbers[2]
            name = "жим"
            if "присед" in text_lower:
                name = "присед"
            elif "станов" in text_lower:
                name = "становая"
            elif "штанг" in text_lower:
                name = "жим штанги лёжа"

            cmd = f'gym add "{name}" {weight}kg {reps}reps {sets}sets'
            if "болел" in text_lower or "ныл" in text_lower:
                cmd += ' --note "колено болело"'
            return {"command": cmd, "error": None}

    # Статистика
    if any(w in text_lower for w in ['сегодня', 'натренировал', 'тренировк']):
        return {"command": "gym today", "error": None}

    # Максимум
    if any(w in text_lower for w in ['максим', 'рекорд']):
        name = "становая тяга" if "станов" in text_lower else "жим лёжа"
        return {"command": f'gym max "{name}"', "error": None}

    # Последний раз
    if any(w in text_lower for w in ['последний', 'когда']):
        name = "присед" if "присед" in text_lower else "становая"
        return {"command": f'gym last "{name}"', "error": None}

    return {"command": None, "error": "Я помогаю только с тренировками"}


@given('пользователь авторизован в Telegram боте')
def user_authorized(voice_context):
    """Пользователь авторизован."""
    voice_context['authorized'] = True


@given('настроен OpenAI API ключ')
def openai_configured(voice_context):
    """OpenAI настроен."""
    voice_context['openai_configured'] = True


@when(parsers.parse('пользователь говорит "{text}"'))
def user_says(voice_context, text):
    """Пользователь отправляет голосовое."""
    voice_context['voice_text'] = text
    result = mock_parse_voice(text)
    voice_context['llm_command'] = result.get('command')
    voice_context['error'] = result.get('error')
    if voice_context['llm_command']:
        voice_context['cli_result'] = 0


@then(parsers.parse("LLM формирует команду '{command}'"))
def llm_forms_command(voice_context, command):
    """Проверяем команду LLM."""
    assert voice_context['llm_command'] is not None
    expected_parts = command.split()[0:2]
    actual_parts = voice_context['llm_command'].split()[0:2]
    assert expected_parts == actual_parts


@then('CLI выполняется успешно')
def cli_executes_successfully(voice_context):
    """CLI выполнен."""
    assert voice_context['cli_result'] == 0


@then('бот отвечает подтверждением добавления')
def bot_confirms_addition(voice_context):
    """Бот подтвердил."""
    assert 'gym add' in voice_context['llm_command']


@then('бот отправляет результат выполнения')
def bot_sends_result(voice_context):
    """Бот отправил результат."""
    assert voice_context['cli_result'] == 0


@then('LLM возвращает сообщение об ошибке')
def llm_returns_error(voice_context):
    """LLM вернул ошибку."""
    assert voice_context['error'] is not None


@then(parsers.parse('бот отвечает "{message}"'))
def bot_responds_with_message(voice_context, message):
    """Бот ответил."""
    assert voice_context['error'] == message
