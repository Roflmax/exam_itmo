"""
Database layer для gym CLI приложения.

Предоставляет класс Database для работы с SQLite базой данных,
включая CRUD операции для упражнений и аналитические запросы.
"""

import sqlite3
from contextlib import contextmanager
from datetime import datetime, timedelta
from pathlib import Path
from typing import Iterator, List, Optional, Tuple

from .models import Exercise


def normalize_exercise_name(name: str) -> str:
    """Нормализация названия упражнения: ё→е, lowercase, strip."""
    return name.lower().replace('ё', 'е').strip()


class Database:
    """
    Класс для работы с SQLite базой данных упражнений.

    Предоставляет методы для добавления, получения и анализа
    данных о тренировках.

    Attributes:
        db_path: Путь к файлу базы данных SQLite

    Example:
        >>> db = Database("gym.db")
        >>> db.init_db()
        >>> exercise = Exercise(
        ...     id=None,
        ...     name="Жим лежа",
        ...     weight=80.0,
        ...     reps=10,
        ...     sets=4,
        ...     note="Хорошая форма",
        ...     created_at=datetime.now()
        ... )
        >>> exercise_id = db.add_exercise(exercise)
    """

    def __init__(self, db_path: str) -> None:
        """
        Инициализация подключения к базе данных.

        Args:
            db_path: Путь к файлу SQLite базы данных.
                    Если файл не существует, он будет создан.
        """
        self.db_path = Path(db_path)
        # Создаем директорию, если не существует
        self.db_path.parent.mkdir(parents=True, exist_ok=True)

    @contextmanager
    def _get_connection(self) -> Iterator[sqlite3.Connection]:
        """
        Context manager для безопасного управления соединением с БД.

        Автоматически коммитит транзакцию при успехе и откатывает
        при возникновении исключения.

        Yields:
            sqlite3.Connection: Активное соединение с базой данных

        Example:
            >>> with self._get_connection() as conn:
            ...     cursor = conn.execute("SELECT * FROM exercises")
        """
        conn = sqlite3.connect(
            self.db_path,
            detect_types=sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES
        )
        # Включаем поддержку foreign keys
        conn.execute("PRAGMA foreign_keys = ON")
        # Настраиваем row factory для удобного доступа к колонкам
        conn.row_factory = sqlite3.Row
        try:
            yield conn
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()

    def init_db(self) -> None:
        """
        Инициализация схемы базы данных.

        Создает таблицу exercises, если она не существует.
        Также создает индексы для оптимизации частых запросов.
        """
        with self._get_connection() as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS exercises (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    weight REAL NOT NULL CHECK (weight >= 0),
                    reps INTEGER NOT NULL CHECK (reps >= 1),
                    sets INTEGER NOT NULL CHECK (sets >= 1),
                    note TEXT,
                    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # Индекс для поиска по имени упражнения (частый запрос)
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_exercises_name
                ON exercises (name)
            """)

            # Индекс для фильтрации по дате
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_exercises_created_at
                ON exercises (created_at)
            """)

            # Композитный индекс для запросов по имени и дате
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_exercises_name_created_at
                ON exercises (name, created_at)
            """)

    def add_exercise(self, exercise: Exercise) -> int:
        """
        Добавление нового упражнения в базу данных.

        Args:
            exercise: Объект Exercise для сохранения.
                     Поле id игнорируется (генерируется автоматически).

        Returns:
            int: ID созданной записи в базе данных

        Raises:
            sqlite3.IntegrityError: При нарушении ограничений БД
            ValueError: При невалидных данных в exercise

        Example:
            >>> exercise = Exercise(
            ...     id=None, name="Приседания", weight=100.0,
            ...     reps=8, sets=5, note=None, created_at=datetime.now()
            ... )
            >>> new_id = db.add_exercise(exercise)
            >>> print(f"Создано упражнение с ID: {new_id}")
        """
        with self._get_connection() as conn:
            cursor = conn.execute(
                """
                INSERT INTO exercises (name, weight, reps, sets, note, created_at)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    exercise.name.strip(),
                    exercise.weight,
                    exercise.reps,
                    exercise.sets,
                    exercise.note,
                    exercise.created_at
                )
            )
            return cursor.lastrowid

    def _row_to_exercise(self, row: sqlite3.Row) -> Exercise:
        """
        Конвертация строки из БД в объект Exercise.

        Args:
            row: Строка результата запроса sqlite3

        Returns:
            Exercise: Объект упражнения
        """
        created_at = row["created_at"]
        # Обработка случая, когда datetime приходит как строка
        if isinstance(created_at, str):
            created_at = datetime.fromisoformat(created_at)

        return Exercise(
            id=row["id"],
            name=row["name"],
            weight=row["weight"],
            reps=row["reps"],
            sets=row["sets"],
            note=row["note"],
            created_at=created_at
        )

    def get_today_exercises(self) -> List[Exercise]:
        """
        Получение всех упражнений за сегодняшний день.

        Возвращает упражнения с 00:00:00 текущего дня до текущего момента,
        отсортированные по времени создания.

        Returns:
            List[Exercise]: Список упражнений за сегодня (может быть пустым)

        Example:
            >>> today_exercises = db.get_today_exercises()
            >>> for ex in today_exercises:
            ...     print(f"{ex.name}: {ex.weight}кг")
        """
        today_start = datetime.now().replace(
            hour=0, minute=0, second=0, microsecond=0
        )

        with self._get_connection() as conn:
            cursor = conn.execute(
                """
                SELECT id, name, weight, reps, sets, note, created_at
                FROM exercises
                WHERE created_at >= ?
                ORDER BY created_at ASC
                """,
                (today_start,)
            )
            return [self._row_to_exercise(row) for row in cursor.fetchall()]

    def get_max_weight(
        self, exercise_name: str
    ) -> Optional[Tuple[float, datetime]]:
        """
        Получение максимального веса для указанного упражнения.

        Поиск выполняется без учета регистра (case-insensitive).

        Args:
            exercise_name: Название упражнения для поиска

        Returns:
            Optional[Tuple[float, datetime]]: Кортеж (макс_вес, дата_достижения)
                                              или None, если записей нет

        Example:
            >>> result = db.get_max_weight("Жим лежа")
            >>> if result:
            ...     weight, date = result
            ...     print(f"Рекорд: {weight}кг ({date.strftime('%d.%m.%Y')})")
        """
        normalized_name = normalize_exercise_name(exercise_name)
        with self._get_connection() as conn:
            cursor = conn.execute(
                """
                SELECT weight, created_at
                FROM exercises
                WHERE LOWER(REPLACE(name, 'ё', 'е')) = ?
                ORDER BY weight DESC, created_at ASC
                LIMIT 1
                """,
                (normalized_name,)
            )
            row = cursor.fetchone()

            if row is None:
                return None

            created_at = row["created_at"]
            if isinstance(created_at, str):
                created_at = datetime.fromisoformat(created_at)

            return (row["weight"], created_at)

    def get_last_exercise(self, exercise_name: str) -> Optional[Exercise]:
        """
        Получение последней записи для указанного упражнения.

        Поиск выполняется без учета регистра (case-insensitive).

        Args:
            exercise_name: Название упражнения для поиска

        Returns:
            Optional[Exercise]: Последнее выполненное упражнение
                               или None, если записей нет

        Example:
            >>> last = db.get_last_exercise("Становая тяга")
            >>> if last:
            ...     print(f"Последний раз: {last.weight}кг x {last.reps}")
        """
        normalized_name = normalize_exercise_name(exercise_name)
        with self._get_connection() as conn:
            cursor = conn.execute(
                """
                SELECT id, name, weight, reps, sets, note, created_at
                FROM exercises
                WHERE LOWER(REPLACE(name, 'ё', 'е')) = ?
                ORDER BY created_at DESC
                LIMIT 1
                """,
                (normalized_name,)
            )
            row = cursor.fetchone()

            if row is None:
                return None

            return self._row_to_exercise(row)

    def get_exercise_history(
        self, exercise_name: str, days: int = 90
    ) -> List[Exercise]:
        """
        Получение истории упражнения за указанный период.

        Возвращает все записи для упражнения за последние N дней,
        отсортированные от старых к новым.

        Args:
            exercise_name: Название упражнения для поиска
            days: Количество дней истории (по умолчанию 90)

        Returns:
            List[Exercise]: Список упражнений за период (может быть пустым)

        Raises:
            ValueError: Если days <= 0

        Example:
            >>> history = db.get_exercise_history("Жим лежа", days=30)
            >>> for ex in history:
            ...     print(f"{ex.created_at.date()}: {ex.weight}кг")
        """
        if days <= 0:
            raise ValueError("Количество дней должно быть положительным")

        start_date = datetime.now() - timedelta(days=days)

        with self._get_connection() as conn:
            cursor = conn.execute(
                """
                SELECT id, name, weight, reps, sets, note, created_at
                FROM exercises
                WHERE LOWER(name) = LOWER(?)
                  AND created_at >= ?
                ORDER BY created_at ASC
                """,
                (exercise_name.strip(), start_date)
            )
            return [self._row_to_exercise(row) for row in cursor.fetchall()]

    def delete_exercise(self, exercise_id: int) -> bool:
        """
        Удаление упражнения по ID.

        Args:
            exercise_id: ID упражнения для удаления

        Returns:
            bool: True если запись была удалена, False если не найдена
        """
        with self._get_connection() as conn:
            cursor = conn.execute(
                "DELETE FROM exercises WHERE id = ?",
                (exercise_id,)
            )
            return cursor.rowcount > 0

    def get_all_exercise_names(self) -> List[str]:
        """
        Получение списка всех уникальных названий упражнений.

        Returns:
            List[str]: Отсортированный список названий упражнений
        """
        with self._get_connection() as conn:
            cursor = conn.execute(
                """
                SELECT DISTINCT name
                FROM exercises
                ORDER BY name ASC
                """
            )
            return [row["name"] for row in cursor.fetchall()]
