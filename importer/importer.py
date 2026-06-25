"""Main import engine."""

import time
from pathlib import Path
from typing import Optional, List
from core.logger import get_logger
from core.checksum import calculate_sha256
from config import Config
from database.database import Database
from database.batch_writer import BatchWriter
from database.history import ImportHistory
from database.optimize import DatabaseOptimizer
from parser.pdf_reader import PDFReader
from parser.voter_parser import VoterParser
from parser.encoding import EncodingNormalizer
from parser.address_parser import AddressParser
from parser.validator import DataValidator
from importer.scanner import PDFScanner
from importer.progress import ProgressTracker
from importer.checkpoint import CheckpointManager
from core.constants import STATUS_SUCCESS, STATUS_FAILED, STATUS_SKIPPED

logger = get_logger(__name__)


class Importer:
    """Main import engine for processing PDF files."""

    def __init__(self, db_path: Optional[str | Path] = None):
        """Initialize importer.
        
        Args:
            db_path: Database path (default: config path)
        """
        self.db_path = db_path or Config.DATABASE_PATH
        self.db = Database(self.db_path)
        self.db.connect()
        self.db.initialize()
        self.history = ImportHistory(self.db)
        self.checkpoint = CheckpointManager()
        self.normalizer = EncodingNormalizer()
        self.address_parser = AddressParser()
        self.validator = DataValidator()
        self.total_voters_imported = 0

    def import_from_directory(self, directory: str | Path, skip_duplicates: bool = True) -> dict:
        """Import PDFs from a directory.
        
        Args:
            directory: Directory containing PDFs
            skip_duplicates: Skip files already imported
            
        Returns:
            Import statistics
        """
        logger.info(f"Starting import from {directory}")
        directory = Path(directory)

        if not directory.exists():
            logger.error(f"Directory not found: {directory}")
            return {"error": "Directory not found"}

        # Scan for PDFs
        scanner = PDFScanner(directory)
        pdf_files = scanner.scan()

        if not pdf_files:
            logger.warning("No PDF files found")
            return {"error": "No PDFs found", "total": 0}

        # Initialize progress tracker
        progress = ProgressTracker(len(pdf_files))
        stats = {
            "total_pdfs": len(pdf_files),
            "successful": 0,
            "failed": 0,
            "skipped": 0,
            "total_voters": 0,
            "start_time": time.time(),
        }

        # Process each PDF
        for pdf_path, checksum in pdf_files:
            try:
                # Skip if already processed and skip_duplicates enabled
                if skip_duplicates and self.checkpoint.is_processed(checksum):
                    logger.debug(f"Skipping duplicate: {pdf_path.name}")
                    progress.update(skipped=True)
                    stats["skipped"] += 1
                    continue

                # Check if already in database
                existing = self.db.fetch_one(
                    "SELECT id FROM pdf_files WHERE checksum = ?", (checksum,)
                )
                if existing and skip_duplicates:
                    logger.debug(f"Skipping already imported: {pdf_path.name}")
                    self.checkpoint.mark_processed(checksum)
                    progress.update(skipped=True)
                    stats["skipped"] += 1
                    continue

                # Import PDF
                voters_count = self._import_pdf(pdf_path, checksum)
                self.checkpoint.mark_processed(checksum)
                progress.update(success=True)
                stats["successful"] += 1
                stats["total_voters"] += voters_count
                logger.info(f"Imported {pdf_path.name}: {voters_count} voters")

            except Exception as e:
                logger.error(f"Failed to import {pdf_path.name}: {e}")
                self.history.record_failure(checksum, pdf_path.name, str(e))
                progress.update(success=False)
                stats["failed"] += 1

            # Print progress
            progress.print_progress(pdf_path.name)

        # Finalize
        stats["elapsed_seconds"] = time.time() - stats["start_time"]
        stats["total_voters_imported"] = self.total_voters_imported

        logger.info(f"Import completed: {stats['successful']} successful, {stats['failed']} failed, {stats['skipped']} skipped")
        logger.info(f"Total voters imported: {stats['total_voters']}")

        return stats

    def _import_pdf(self, pdf_path: Path, checksum: str) -> int:
        """Import a single PDF file.
        
        Args:
            pdf_path: Path to PDF
            checksum: File checksum
            
        Returns:
            Number of voters imported
        """
        voter_count = 0

        try:
            # Read PDF
            reader = PDFReader(pdf_path)
            reader.open()

            # Extract metadata (simplified)
            metadata_text = reader.get_page_text(0) if reader.page_count > 0 else ""

            # Record PDF file
            pdf_record = {
                "checksum": checksum,
                "filename": pdf_path.name,
                "total_records": 0,
                "imported_at": None,
            }
            pdf_cursor = self.db.execute(
                "INSERT INTO pdf_files (checksum, filename) VALUES (?, ?)",
                (checksum, pdf_path.name),
            )
            pdf_id = pdf_cursor.lastrowid
            pdf_cursor.close()

            # Parse voters
            all_blocks = []
            for page_num in range(reader.page_count):
                blocks = reader.get_page_text_blocks(page_num)
                for block in blocks:
                    if isinstance(block, tuple) and len(block) >= 4:
                        text = block[4]
                        if text.strip():
                            all_blocks.append(text)

            # Use VoterParser
            voter_parser = VoterParser(all_blocks)
            voters = voter_parser.parse()

            # Batch write voters
            if voters:
                batch_writer = BatchWriter(self.db, "voters", Config.BATCH_SIZE)
                for voter in voters:
                    if self.validator.is_valid_voter_record(voter.__dict__):
                        voter_dict = voter.to_dict_with_pdf(pdf_id)
                        batch_writer.add(voter_dict)
                        voter_count += 1
                batch_writer.close()

            # Update PDF record
            self.db.execute(
                "UPDATE pdf_files SET total_records = ? WHERE id = ?",
                (voter_count, pdf_id),
            )

            # Record in history
            self.history.record_success(checksum, pdf_path.name, f"{voter_count} voters")
            self.total_voters_imported += voter_count

            reader.close()

        except Exception as e:
            logger.error(f"PDF import error for {pdf_path.name}: {e}")
            self.history.record_failure(checksum, pdf_path.name, str(e))
            raise

        return voter_count

    def verify_database(self) -> dict:
        """Verify database integrity."""
        logger.info("Verifying database...")
        optimizer = DatabaseOptimizer(self.db)
        return optimizer.get_database_info()

    def optimize_database(self) -> None:
        """Optimize database."""
        logger.info("Optimizing database...")
        optimizer = DatabaseOptimizer(self.db)
        optimizer.optimize()

    def rebuild_indexes(self) -> None:
        """Rebuild database indexes."""
        logger.info("Rebuilding indexes...")
        optimizer = DatabaseOptimizer(self.db)
        optimizer.rebuild_indexes()

    def close(self) -> None:
        """Close database connection."""
        self.db.close()

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()
