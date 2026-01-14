"""
Модели данных для gym CLI приложения.

Содержит dataclass-определения для всех сущностей приложения.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class Exercise:
    """
    Модель упражнения в тренажерном зале.

    Attributes:
        id: Уникальный идентификатор записи (None для новых записей)
        name: Название упражнения (например, "Жим лежа", "Приседания")
        weight: Рабочий вес в килограммах
        reps: Количество повторений в подходе
        sets: Количество подходов
        note: Опциональная заметка к упражнению
        created_at: Дата и время выполнения упражнения
    """
    id: Optional[int]
    name: str
    weight: float
    reps: int
    sets: int
    note: Optional[str]
    created_at: datetime

    def __post_init__(self) -> None:
        """Валидация данных после инициализации."""
        if self.weight < 0:
            raise ValueError("Вес не может быть отрицательным")
        if self.reps < 1:
            raise ValueError("Количество повторений должно быть >= 1")
        if self.sets < 1:
            raise ValueError("Количество подходов должно быть >= 1")
        if not self.name or not self.name.strip():
            raise ValueError("Название упражнения не может быть пустым")

    @property
    def total_volume(self) -> float:
        """
        Вычисляет общий объем нагрузки (вес * повторения * подходы).

        Returns:
            Общий объем в кг
        """
        return self.weight * self.reps * self.sets

    def __str__(self) -> str:
        """Строковое представление упражнения."""
        note_str = f" ({self.note})" if self.note else ""
        return (
            f"{self.name}: {self.weight}кг x {self.reps} повт. x {self.sets} подх."
            f"{note_str}"
        )
