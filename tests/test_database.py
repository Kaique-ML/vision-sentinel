"""
Testes unitários para o módulo de banco de dados.
"""

import os
import pytest
from src.database import DatabaseManager

TEST_DB = "data/test_sentinel.db"


@pytest.fixture(autouse=True)
def cleanup():
    yield
    if os.path.exists(TEST_DB):
        os.remove(TEST_DB)


def test_initialize_creates_file():
    db = DatabaseManager(db_path=TEST_DB)
    db.initialize()
    assert os.path.exists(TEST_DB)
    db.close()


def test_log_detection_inserts_row():
    import sqlite3
    db = DatabaseManager(db_path=TEST_DB)
    db.initialize()
    db.log_detection("person", 0.92, (10, 20, 100, 200))
    db.close()

    conn = sqlite3.connect(TEST_DB)
    row = conn.execute("SELECT class_name, confidence FROM logs_deteccao").fetchone()
    conn.close()

    assert row is not None
    assert row[0] == "person"
    assert abs(row[1] - 0.92) < 0.0001


def test_log_without_connection_does_not_crash():
    db = DatabaseManager(db_path=TEST_DB)
    # Não chama initialize — conn é None
    db.log_detection("car", 0.80, (0, 0, 50, 50))  # não deve lançar exceção
