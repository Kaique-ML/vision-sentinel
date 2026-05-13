"""
Camada de persistência com SQLite.
Gerencia conexão, criação de schema e escrita dos logs de detecção.
"""

import sqlite3
import logging
import os
from datetime import datetime
from typing import Tuple, Optional

from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)

DB_PATH = os.getenv("DB_PATH", "data/detections.db")


class DatabaseManager:
    """
    Gerencia todas as operações de banco de dados do VisionSentinel.

    Attributes:
        db_path (str): Caminho para o arquivo SQLite.
        conn: Conexão ativa com o banco de dados.
    """

    def __init__(self, db_path: str = DB_PATH):
        self.db_path = db_path
        self.conn: Optional[sqlite3.Connection] = None

    def initialize(self) -> None:
        """
        Cria o diretório e o arquivo do banco de dados se não existirem,
        e garante que as tabelas necessárias estejam criadas.

        Raises:
            sqlite3.Error: Se houver falha ao conectar ou criar tabelas.
        """
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        try:
            self.conn = sqlite3.connect(self.db_path, check_same_thread=False)
            self._create_tables()
            logger.info(f"Banco de dados inicializado em: {self.db_path}")
        except sqlite3.Error as e:
            logger.error(f"Falha ao inicializar banco de dados: {e}")
            raise

    def _create_tables(self) -> None:
        """
        Cria as tabelas do schema caso ainda não existam.
        """
        ddl = """
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
        """
        self.conn.executescript(ddl)
        self.conn.commit()

    def log_detection(
        self,
        class_name: str,
        confidence: float,
        bbox: Tuple[int, int, int, int],
    ) -> None:
        """
        Insere um registro de detecção no banco de dados.

        Args:
            class_name (str): Nome da classe detectada (ex: 'person').
            confidence (float): Confiança da detecção (0.0 a 1.0).
            bbox (tuple): Coordenadas do bounding box (x1, y1, x2, y2).
        """
        if not self.conn:
            logger.warning("Tentativa de log sem conexão ativa com o banco.")
            return

        sql = """
        INSERT INTO logs_deteccao (timestamp, class_name, confidence, bbox_x1, bbox_y1, bbox_x2, bbox_y2)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """
        x1, y1, x2, y2 = bbox
        try:
            self.conn.execute(
                sql,
                (datetime.now().isoformat(), class_name, confidence, x1, y1, x2, y2),
            )
            self.conn.commit()
        except sqlite3.OperationalError as e:
            logger.error(f"Erro ao inserir detecção (banco ocupado?): {e}")

    def close(self) -> None:
        """
        Fecha a conexão com o banco de dados de forma segura.
        """
        if self.conn:
            self.conn.close()
            logger.info("Conexão com o banco de dados encerrada.")
