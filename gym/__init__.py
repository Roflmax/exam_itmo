"""
Gym CLI приложение для отслеживания тренировок.

Модули:
    models: Dataclass-модели для Exercise
    db: Database layer для работы с SQLite
"""

from .models import Exercise
from .db import Database

__all__ = ["Exercise", "Database"]
