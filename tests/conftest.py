"""Pytest configuration and shared fixtures."""
import pytest
import tempfile
import os
import sys

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from datetime import datetime
from gym.db import Database
from gym.models import Exercise


@pytest.fixture
def temp_db():
    """Создаёт временную базу данных для тестов."""
    fd, path = tempfile.mkstemp(suffix='.db')
    os.close(fd)
    db = Database(path)
    db.init_db()
    yield db
    if os.path.exists(path):
        os.unlink(path)


@pytest.fixture
def exercise_context():
    """Контекст для хранения данных упражнения между шагами."""
    return {
        'name': None,
        'weight': None,
        'reps': None,
        'sets': None,
        'note': None,
        'exercise': None,
        'exercises': [],
        'result': None,
        'error': None
    }
