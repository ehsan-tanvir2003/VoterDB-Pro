"""Import history tracking."""

from datetime import datetime
from typing import Optional, List
from core.logger import get_logger
from database.database import Database
from database.models import ImportHistoryRecord
from core.constants import STATUS_SUCCESS, STATUS_FAILED, STATUS_SKIPPED

logger = get_logger(__name__)


class ImportHistory:
    """Manages import history records."""

    def __init__(self, db: Database):
        """Initialize import history manager.
        
        Args:
            db: Database instance
        """
        self.db = db
        self.table = "import_history"

    def record_success(
        self, checksum: str, filename: str, message: str = ""
    ) -> None:
        """Record successful import."""
        self.add_record(checksum, filename, STATUS_SUCCESS, message)

    def record_failure(
        self, checksum: str, filename: str, message: str
    ) -> None:
        """Record failed import."""
        self.add_record(checksum, filename, STATUS_FAILED, message)

    def record_skip(
        self, checksum: str, filename: str, message: str = "Duplicate"
    ) -> None:
        """Record skipped import."""
        self.add_record(checksum, filename, STATUS_SKIPPED, message)

    def add_record(
        self, checksum: str, filename: str, status: str, message: str = ""
    ) -> None:
        """Add import history record."""
        try:
            record = ImportHistoryRecord(
                checksum=checksum,
                filename=filename,
                status=status,
                message=message or "",
                created_at=datetime.now(),
            )
            query = (
                f"INSERT INTO {self.table} "
                f"(checksum, filename, status, message, created_at) "
                f"VALUES (?, ?, ?, ?, ?)"
            )
            self.db.execute(
                query,
                (
                    record.checksum,
                    record.filename,
                    record.status,
                    record.message,
                    record.created_at,
                ),
            )
            logger.debug(f"History recorded: {filename} - {status}")
        except Exception as e:
            logger.error(f"Failed to record history: {e}")

    def get_by_checksum(self, checksum: str) -> Optional[dict]:
        """Get import history by checksum."""
        return self.db.fetch_one(
            f"SELECT * FROM {self.table} WHERE checksum = ?", (checksum,)
        )

    def get_all(self, limit: int = 100) -> List[dict]:
        """Get all import history records."""
        return self.db.fetch_all(
            f"SELECT * FROM {self.table} ORDER BY created_at DESC LIMIT ?",
            (limit,),
        )

    def is_imported(self, checksum: str) -> bool:
        """Check if file was already imported."""
        record = self.get_by_checksum(checksum)
        return record is not None and record["status"] == STATUS_SUCCESS
