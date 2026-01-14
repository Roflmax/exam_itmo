"""
CLI interface для gym приложения.

Предоставляет команды для отслеживания тренировок:
- add: добавление упражнения
- today: просмотр сегодняшних упражнений
- max: максимальный вес для упражнения
- progress: прогресс за 3 месяца
- last: последнее выполнение упражнения
"""

import os
from datetime import datetime
from pathlib import Path

import click

from gym.db import Database
from gym.models import Exercise
from gym.parser import parse_exercise_input


# Путь к базе данных по умолчанию
DEFAULT_DB_PATH = os.path.expanduser("~/.gym/gym.db")


def get_db() -> Database:
    """
    Получение экземпляра базы данных.
    Создает директорию ~/.gym если её нет.
    """
    db_path = Path(DEFAULT_DB_PATH)
    db_path.parent.mkdir(parents=True, exist_ok=True)
    db = Database(str(db_path))
    db.init_db()
    return db


@click.group()
def cli():
    """
    Gym CLI - трекер тренировок в терминале.

    Примеры использования:

        gym add "жим лёжа" 80kg 8reps 3sets

        gym add "присед" 100kg 5x4 --note "колено ныло"

        gym today

        gym max "жим лёжа"

        gym progress "жим лёжа"

        gym last "присед"
    """
    pass


@cli.command()
@click.argument("name")
@click.argument("params", nargs=-1, required=True)
@click.option("--note", "-n", default=None, help="Заметка к упражнению")
def add(name: str, params: tuple, note: str | None):
    """
    Добавить упражнение в журнал.

    NAME - название упражнения (в кавычках если с пробелами)

    PARAMS - параметры: вес, повторения, подходы

    Примеры:

        gym add "жим лёжа" 80kg 8reps 3sets

        gym add "присед" 100kg 5x4 --note "колено ныло"

        gym add "становая" 120 6 4
    """
    db = get_db()

    # Объединяем параметры в строку для парсера
    params_str = " ".join(params)

    try:
        weight, reps, sets = parse_exercise_input(params_str)
    except ValueError as e:
        click.echo(click.style(f"Ошибка: {e}", fg="red"))
        raise SystemExit(1)

    exercise = Exercise(
        id=None,
        name=name,
        weight=weight,
        reps=reps,
        sets=sets,
        note=note,
        created_at=datetime.now()
    )

    try:
        db.add_exercise(exercise)
        # Форматируем вес: убираем .0 если целое число
        weight_str = f"{int(weight)}" if weight == int(weight) else f"{weight}"
        click.echo(click.style(
            f"Добавлено: {name} {weight_str}кг {reps}x{sets}",
            fg="green"
        ))
    except Exception as e:
        click.echo(click.style(f"Ошибка при сохранении: {e}", fg="red"))
        raise SystemExit(1)


@cli.command()
def today():
    """
    Показать все упражнения за сегодня.

    Выводит пронумерованный список всех упражнений,
    выполненных в текущий день.
    """
    db = get_db()
    exercises = db.get_today_exercises()

    if not exercises:
        click.echo(click.style("Сегодня тренировок не было", fg="yellow"))
        return

    click.echo(click.style("Тренировка за сегодня:", fg="cyan", bold=True))
    click.echo()

    for i, ex in enumerate(exercises, 1):
        # Форматируем вес
        weight_str = f"{int(ex.weight)}" if ex.weight == int(ex.weight) else f"{ex.weight}"
        line = f"{i}. {ex.name}: {weight_str}кг {ex.reps}x{ex.sets}"

        if ex.note:
            line += click.style(f" ({ex.note})", fg="bright_black")

        click.echo(line)


@cli.command("max")
@click.argument("name")
def max_weight(name: str):
    """
    Показать максимальный вес для упражнения.

    NAME - название упражнения

    Пример:

        gym max "жим лёжа"
    """
    db = get_db()
    result = db.get_max_weight(name)

    if result is None:
        click.echo(click.style(f"Упражнение '{name}' не найдено", fg="yellow"))
        return

    weight, date = result
    weight_str = f"{int(weight)}" if weight == int(weight) else f"{weight}"
    date_str = date.strftime("%d.%m.%Y")

    click.echo(click.style(
        f"Максимум {name}: {weight_str}кг ({date_str})",
        fg="green",
        bold=True
    ))


@cli.command()
@click.argument("name")
def progress(name: str):
    """
    Показать прогресс за последние 3 месяца.

    NAME - название упражнения

    Выводит список всех записей упражнения с датами,
    весами и ASCII-графиком прогресса.

    Пример:

        gym progress "жим лёжа"
    """
    db = get_db()
    history = db.get_exercise_history(name, days=90)

    if not history:
        click.echo(click.style(f"Упражнение '{name}' не найдено", fg="yellow"))
        return

    click.echo(click.style(f"Прогресс {name} за 3 месяца:", fg="cyan", bold=True))
    click.echo()

    # Находим минимальный и максимальный вес для графика
    weights = [ex.weight for ex in history]
    min_weight = min(weights)
    max_weight = max(weights)
    weight_range = max_weight - min_weight if max_weight > min_weight else 1

    # Ширина ASCII графика
    graph_width = 20

    for ex in history:
        date_str = ex.created_at.strftime("%d.%m.%Y")
        weight_str = f"{int(ex.weight)}" if ex.weight == int(ex.weight) else f"{ex.weight}"

        # Создаем ASCII бар
        if weight_range > 0:
            bar_length = int((ex.weight - min_weight) / weight_range * graph_width) + 1
        else:
            bar_length = graph_width
        bar = click.style("=" * bar_length, fg="green")

        line = f"  {date_str}  {weight_str:>6}кг {ex.reps}x{ex.sets}  {bar}"
        click.echo(line)

    # Статистика
    click.echo()
    avg_weight = sum(weights) / len(weights)
    avg_str = f"{avg_weight:.1f}"
    min_str = f"{int(min_weight)}" if min_weight == int(min_weight) else f"{min_weight}"
    max_str = f"{int(max_weight)}" if max_weight == int(max_weight) else f"{max_weight}"

    click.echo(click.style(f"Всего записей: {len(history)}", fg="bright_black"))
    click.echo(click.style(f"Мин: {min_str}кг | Макс: {max_str}кг | Среднее: {avg_str}кг", fg="bright_black"))


@cli.command()
@click.argument("name")
def last(name: str):
    """
    Показать последнее выполнение упражнения.

    NAME - название упражнения

    Пример:

        gym last "присед"
    """
    db = get_db()
    exercise = db.get_last_exercise(name)

    if exercise is None:
        click.echo(click.style(f"Упражнение '{name}' не найдено", fg="yellow"))
        return

    date_str = exercise.created_at.strftime("%d.%m.%Y")
    weight_str = f"{int(exercise.weight)}" if exercise.weight == int(exercise.weight) else f"{exercise.weight}"

    result = f"Последний раз {name}: {date_str} - {weight_str}кг {exercise.reps}x{exercise.sets}"

    if exercise.note:
        result += click.style(f" ({exercise.note})", fg="bright_black")

    click.echo(click.style(result, fg="cyan"))


def main():
    """Entry point для CLI приложения."""
    cli()


if __name__ == "__main__":
    main()
