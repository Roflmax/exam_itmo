"""Pytest configuration and shared fixtures."""
import pytest
import tempfile
import os


@pytest.fixture
def temp_db():
    """Создаёт временную базу данных для тестов."""
    fd, path = tempfile.mkstemp(suffix='.db')
    os.close(fd)
    yield path
    if os.path.exists(path):
        os.unlink(path)
