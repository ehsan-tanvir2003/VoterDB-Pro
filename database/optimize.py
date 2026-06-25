"""Database optimization utilities."""

from core.logger import get_logger
from database.database import Database

logger = get_logger(__name__)


class DatabaseOptimizer:
    """Handles database optimization and maintenance."""

    def __init__(self, db: Database):
        """Initialize optimizer.
        
        Args:
            db: Database instance
        """
        self.db = db

    def vacuum(self) -> None:
        """Vacuum database to reclaim space."""
        logger.info("Starting database vacuum...")
        try:
            self.db.vacuum()
            logger.info("Database vacuumed successfully")
        except Exception as e:
            logger.error(f"Vacuum failed: {e}")
            raise

    def analyze(self) -> None:
        """Analyze database for query optimization."""
        logger.info("Starting database analysis...")
        try:
            self.db.analyze()
            logger.info("Database analyzed successfully")
        except Exception as e:
            logger.error(f"Analysis failed: {e}")
            raise

    def optimize(self) -> None:
        """Run full optimization: analyze and vacuum."""
        logger.info("Starting full database optimization...")
        try:
            self.analyze()
            self.vacuum()
            logger.info("Database optimization completed")
        except Exception as e:
            logger.error(f"Optimization failed: {e}")
            raise

    def rebuild_indexes(self) -> None:
        """Rebuild all indexes."""
        logger.info("Rebuilding database indexes...")
        try:
            self.db.execute("REINDEX")
            logger.info("Indexes rebuilt successfully")
        except Exception as e:
            logger.error(f"Index rebuild failed: {e}")
            raise

    def get_database_info(self) -> dict:
        """Get database statistics."""
        try:
            pdf_count = self.db.get_table_count("pdf_files")
            voter_count = self.db.get_table_count("voters")
            history_count = self.db.get_table_count("import_history")

            return {
                "pdf_files": pdf_count,
                "voters": voter_count,
                "import_history": history_count,
                "database_path": str(self.db.db_path),
                "database_size": self.db.db_path.stat().st_size if self.db.db_path.exists() else 0,
            }
        except Exception as e:
            logger.error(f"Failed to get database info: {e}")
            return {}

    def verify_integrity(self) -> bool:
        """Verify database integrity."""
        logger.info("Verifying database integrity...")
        try:
            result = self.db.fetch_one("PRAGMA integrity_check")
            if result and result[0] == "ok":
                logger.info("Database integrity check passed")
                return True
            else:
                logger.error(f"Database integrity check failed: {result}")
                return False
        except Exception as e:
            logger.error(f"Integrity check failed: {e}")
            return False
