"""Database connection manager and migration initializer."""
import sqlite3
from pathlib import Path
from typing import Generator
from utils.logger import logger


class DatabaseManager:
    """Manages SQLite database connections, schema creation, and transactions."""

    def __init__(self, db_path: str = "data/jobs_agent.db"):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    def get_connection(self) -> sqlite3.Connection:
        """Creates and returns a thread-safe connection to the SQLite DB.

        Returns:
            sqlite3.Connection object with WAL journaling enabled.
        """
        conn = sqlite3.connect(str(self.db_path), timeout=30.0)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON;")
        conn.execute("PRAGMA journal_mode = WAL;")
        return conn

    def _init_db(self) -> None:
        """Executes DDL schema file on startup to create tables & indexes."""
        schema_file = Path(__file__).parent / "schema.sql"
        if not schema_file.exists():
            logger.error(f"Schema file not found at {schema_file}")
            raise FileNotFoundError(f"Schema file missing: {schema_file}")

        with open(schema_file, "r", encoding="utf-8") as f:
            schema_script = f.read()

        with self.get_connection() as conn:
            conn.executescript(schema_script)
            conn.commit()
        logger.info(f"Database initialized successfully at: {self.db_path}")


_db_manager_instance = None


def get_db(db_path: str = "data/jobs_agent.db") -> DatabaseManager:
    """Singleton getter for DatabaseManager."""
    global _db_manager_instance
    if _db_manager_instance is None:
        _db_manager_instance = DatabaseManager(db_path=db_path)
    return _db_manager_instance
