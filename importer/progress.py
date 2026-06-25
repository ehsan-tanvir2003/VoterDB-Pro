"""Progress tracking and reporting."""

import time
from typing import Optional
from datetime import datetime, timedelta
from core.logger import get_logger

logger = get_logger(__name__)


class ProgressTracker:
    """Tracks and reports import progress."""

    def __init__(self, total_items: int):
        """Initialize progress tracker.
        
        Args:
            total_items: Total number of items to process
        """
        self.total_items = total_items
        self.processed = 0
        self.successful = 0
        self.failed = 0
        self.skipped = 0
        self.start_time = time.time()
        self.last_update = self.start_time

    def update(self, success: bool = True, skipped: bool = False) -> None:
        """Update progress.
        
        Args:
            success: Whether item was processed successfully
            skipped: Whether item was skipped
        """
        self.processed += 1
        if skipped:
            self.skipped += 1
        elif success:
            self.successful += 1
        else:
            self.failed += 1

    def get_progress(self) -> dict:
        """Get current progress statistics."""
        elapsed = time.time() - self.start_time
        rate = self.processed / elapsed if elapsed > 0 else 0
        remaining = self.total_items - self.processed
        eta_seconds = remaining / rate if rate > 0 else 0

        return {
            "processed": self.processed,
            "total": self.total_items,
            "successful": self.successful,
            "failed": self.failed,
            "skipped": self.skipped,
            "elapsed_seconds": elapsed,
            "rate_per_second": rate,
            "eta_seconds": eta_seconds,
            "percent_complete": (self.processed / self.total_items * 100) if self.total_items > 0 else 0,
        }

    def print_progress(self, current_pdf: Optional[str] = None) -> None:
        """Print progress to console.
        
        Args:
            current_pdf: Name of current PDF being processed
        """
        progress = self.get_progress()
        percent = progress["percent_complete"]
        elapsed = int(progress["elapsed_seconds"])
        eta = int(progress["eta_seconds"])

        print(f"\nProgress: {progress['processed']}/{progress['total']} ({percent:.1f}%)")
        if current_pdf:
            print(f"Current: {current_pdf}")
        print(f"Successful: {progress['successful']} | Failed: {progress['failed']} | Skipped: {progress['skipped']}")
        print(f"Speed: {progress['rate_per_second']:.1f} PDFs/sec")
        print(f"Elapsed: {elapsed}s | ETA: {eta}s")

    def get_eta_time(self) -> Optional[str]:
        """Get estimated completion time."""
        progress = self.get_progress()
        if progress["eta_seconds"] > 0:
            eta_datetime = datetime.now() + timedelta(seconds=progress["eta_seconds"])
            return eta_datetime.strftime("%H:%M:%S")
        return None
