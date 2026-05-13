"""
Gerador de dados simulados para demonstração do dashboard.
Execute este script para popular o banco antes de subir o Streamlit.

Uso:
    python seed_data.py
    python seed_data.py --days 7 --records 2000
"""

import sqlite3
import random
import argparse
import os
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv()

DB_PATH = os.getenv("DB_PATH", "data/detections.db")
CLASSES = ["person", "car", "truck", "bicycle"]

# Distribuição de probabilidade realista por hora (índice = hora do dia)
HOUR_WEIGHTS = [
    0.1, 0.05, 0.03, 0.02, 0.02, 0.05,   # 00–05h (madrugada)
    0.3,  0.8,  1.0,  0.9,  0.7,  0.8,   # 06–11h (manhã)
    1.0,  0.9,  0.7,  0.6,  0.8,  1.0,   # 12–17h (tarde)
    0.9,  0.7,  0.5,  0.4,  0.3,  0.2,   # 18–23h (noite)
]


def seed(db_path: str, days: int, total_records: int) -> None:
    """
    Popula o banco de dados com registros simulados de detecção.

    Args:
        db_path (str): Caminho para o arquivo SQLite.
        days (int): Quantos dias passados incluir nos dados.
        total_records (int): Número total de registros a inserir.
    """
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    conn = sqlite3.connect(db_path)

    conn.executescript("""
        CREATE TABLE IF NOT EXISTS logs_deteccao (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp   TEXT    NOT NULL,
            class_name  TEXT    NOT NULL,
            confidence  REAL    NOT NULL,
            bbox_x1     INTEGER,
            bbox_y1     INTEGER,
            bbox_x2     INTEGER,
            bbox_y2     INTEGER
        );
        CREATE INDEX IF NOT EXISTS idx_timestamp  ON logs_deteccao (timestamp);
        CREATE INDEX IF NOT EXISTS idx_class_name ON logs_deteccao (class_name);
    """)

    now = datetime.now()
    rows = []

    for _ in range(total_records):
        day_offset = random.randint(0, days - 1)
        hour = random.choices(range(24), weights=HOUR_WEIGHTS)[0]
        minute = random.randint(0, 59)
        second = random.randint(0, 59)
        ts = (now - timedelta(days=day_offset)).replace(
            hour=hour, minute=minute, second=second, microsecond=0
        )

        cls = random.choices(
            CLASSES, weights=[0.55, 0.25, 0.12, 0.08]
        )[0]
        conf = round(random.uniform(0.45, 0.99), 4)
        x1 = random.randint(0, 600)
        y1 = random.randint(0, 400)
        x2 = x1 + random.randint(40, 200)
        y2 = y1 + random.randint(40, 200)

        rows.append((ts.isoformat(), cls, conf, x1, y1, x2, y2))

    conn.executemany(
        "INSERT INTO logs_deteccao (timestamp, class_name, confidence, bbox_x1, bbox_y1, bbox_x2, bbox_y2) VALUES (?,?,?,?,?,?,?)",
        rows,
    )
    conn.commit()
    conn.close()
    print(f"✅ {total_records} registros inseridos em '{db_path}' ({days} dias de histórico)")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Seed de dados simulados")
    parser.add_argument("--days",    type=int, default=30,   help="Dias de histórico")
    parser.add_argument("--records", type=int, default=5000, help="Total de registros")
    args = parser.parse_args()
    seed(DB_PATH, args.days, args.records)
