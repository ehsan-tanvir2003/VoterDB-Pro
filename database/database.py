"""SQLite database connection and operations."""

import sqlite3
from pathlib import Path
from typing import Any, List, Optional, Tuple
from contextlib import contextmanager

from core.logger import get_logger
from config import Config

logger = get_logger(__name__)


class Database:
    """SQLite database wrapper with optimizations."""

    def __init__(self, db_path: str | Path):
        """Initialize database connection."""
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.connection: Optional[sqlite3.Connection] = None
        self._initialized = False

    def connect(self) -> sqlite3.Connection:
        """Create database connection with optimizations."""
        if self.connection is not None:
            return self.connection

        try:
            self.connection = sqlite3.connect(
                str(self.db_path),
                timeout=Config.DATABASE_TIMEOUT,
                check_same_thread=False,
            )
            self.connection.row_factory = sqlite3.Row
            self._optimize_connection()
            logger.info(f"Database connected: {self.db_path}")
            return self.connection
        except sqlite3.Error as e:
            logger.error(f"Failed to connect to database: {e}")
            raise

    def _optimize_connection(self) -> None:
        """Apply SQLite optimizations."""
        if self.connection is None:
            return

        cursor = self.connection.cursor()
        try:
            cursor.execute("PRAGMA journal_mode=WAL")
            cursor.execute("PRAGMA synchronous=NORMAL")
            cursor.execute("PRAGMA temp_store=MEMORY")
            cursor.execute(f"PRAGMA cache_size={Config.DATABASE_CACHE_SIZE}")
            cursor.execute(f"PRAGMA page_size={Config.DATABASE_PAGE_SIZE}")
            cursor.execute("PRAGMA foreign_keys=ON")
            self.connection.commit()
            logger.debug("Database optimizations applied")
        except sqlite3.Error as e:
            logger.error(f"Failed to apply optimizations: {e}")
            raise
        finally:
            cursor.close()

    def initialize(self, schema_file: str | Path = "database/schema.sql") -> None:
        """Initialize database schema."""
        if self._initialized:
            return

        schema_path = Path(schema_file)
        if not schema_path.exists():
            logger.error(f"Schema file not found: {schema_path}")
            return

        try:
            with open(schema_path, "r", encoding="utf-8") as f:
                schema = f.read()

            cursor = self.connection.cursor()
            cursor.executescript(schema)
            self.connection.commit()
            self._initialized = True
            logger.info("Database schema initialized")
        except (sqlite3.Error, IOError) as e:
            logger.error(f"Failed to initialize schema: {e}")
            raise
        finally:
            cursor.close()

    @contextmanager
    def transaction(self):
        """Context manager for database transactions."""
        if self.connection is None:
            self.connect()

        try:
            yield self.connection
            self.connection.commit()
        except Exception as e:
            self.connection.rollback()
            logger.error(f"Transaction failed: {e}")
            raise

    def execute(self, query: str, params: tuple = ()) -> sqlite3.Cursor:
        """Execute a query."""
        if self.connection is None:
            self.connect()

        cursor = self.connection.cursor()
        try:
            cursor.execute(query, params)
            self.connection.commit()
            return cursor
        except sqlite3.Error as e:
            logger.error(f"Query execution failed: {e}")
            self.connection.rollback()
            raise

    def executemany(self, query: str, params: List[tuple]) -> int:
        """Execute multiple queries."""
        if self.connection is None:
            self.connect()

        cursor = self.connection.cursor()
        try:
            cursor.executemany(query, params)
            self.connection.commit()
            return cursor.rowcount
        except sqlite3.Error as e:
            logger.error(f"Batch execution failed: {e}")
            self.connection.rollback()
            raise
        finally:
            cursor.close()

    def fetch_one(self, query: str, params: tuple = ()) -> Optional[dict]:
        """Fetch a single row."""
        cursor = self.execute(query, params)
        row = cursor.fetchone()
        cursor.close()
        return dict(row) if row else None

    def fetch_all(self, query: str, params: tuple = ()) -> List[dict]:
        """Fetch all rows."""
        cursor = self.execute(query, params)
        rows = cursor.fetchall()
        cursor.close()
        return [dict(row) for row in rows]

    def close(self) -> None:
        """Close database connection."""
        if self.connection:
            self.connection.close()
            self.connection = None
            logger.info("Database connection closed")

    def vacuum(self) -> None:
        """Vacuum database to optimize space."""
        try:
            self.execute("VACUUM")
            logger.info("Database vacuumed")
        except sqlite3.Error as e:
            logger.error(f"Vacuum failed: {e}")

    def analyze(self) -> None:
        """Analyze database for query optimization."""
        try:
            self.execute("ANALYZE")
            logger.info("Database analyzed")
        except sqlite3.Error as e:
            logger.error(f"Analyze failed: {e}")

    def get_table_count(self, table_name: str) -> int:
        """Get count of rows in a table."""
        result = self.fetch_one(f"SELECT COUNT(*) as count FROM {table_name}")
        return result["count"] if result else 0

    def __enter__(self):
        """Context manager entry."""
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()
