"""Batch writer for efficient database inserts."""

from typing import List, Dict, Any, Optional
from core.logger import get_logger
from database.database import Database

logger = get_logger(__name__)


class BatchWriter:
    """Handles batch inserts into database."""

    def __init__(self, db: Database, table: str, batch_size: int = 1000):
        """Initialize batch writer.
        
        Args:
            db: Database instance
            table: Table name
            batch_size: Number of rows per batch
        """
        self.db = db
        self.table = table
        self.batch_size = batch_size
        self.batch: List[Dict[str, Any]] = []
        self.total_written = 0

    def add(self, record: Dict[str, Any]) -> None:
        """Add record to batch.
        
        Args:
            record: Dictionary with column names as keys
        """
        self.batch.append(record)
        if len(self.batch) >= self.batch_size:
            self.flush()

    def flush(self) -> int:
        """Write batch to database.
        
        Returns:
            Number of rows written
        """
        if not self.batch:
            return 0

        try:
            columns = list(self.batch[0].keys())
            placeholders = ",".join(["?" for _ in columns])
            query = f"INSERT INTO {self.table} ({','.join(columns)}) VALUES ({placeholders})"
            
            values = [
                tuple(record.get(col) for col in columns)
                for record in self.batch
            ]
            
            rows_written = self.db.executemany(query, values)
            self.total_written += rows_written
            logger.debug(f"Batch written: {rows_written} rows to {self.table}")
            self.batch = []
            return rows_written
        except Exception as e:
            logger.error(f"Batch write failed: {e}")
            raise

    def close(self) -> int:
        """Flush remaining records and return total written.
        
        Returns:
            Total number of rows written
        """
        self.flush()
        return self.total_written
