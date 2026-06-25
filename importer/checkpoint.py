"""Checkpoint management for resuming imports."""

import json
from pathlib import Path
from typing import Optional, Set
from core.logger import get_logger

logger = get_logger(__name__)


class CheckpointManager:
    """Manages import checkpoints for resuming interrupted imports."""

    def __init__(self, checkpoint_file: str | Path = "data/checkpoint.json"):
        """Initialize checkpoint manager.
        
        Args:
            checkpoint_file: Path to checkpoint file
        """
        self.checkpoint_file = Path(checkpoint_file)
        self.checkpoint_file.parent.mkdir(parents=True, exist_ok=True)
        self.processed_files: Set[str] = set()
        self.load()

    def load(self) -> None:
        """Load checkpoint from file."""
        if self.checkpoint_file.exists():
            try:
                with open(self.checkpoint_file, "r") as f:
                    data = json.load(f)
                    self.processed_files = set(data.get("processed_files", []))
                logger.info(f"Loaded checkpoint with {len(self.processed_files)} processed files")
            except Exception as e:
                logger.warning(f"Failed to load checkpoint: {e}")
                self.processed_files = set()

    def save(self) -> None:
        """Save checkpoint to file."""
        try:
            data = {"processed_files": list(self.processed_files)}
            with open(self.checkpoint_file, "w") as f:
                json.dump(data, f, indent=2)
            logger.debug(f"Checkpoint saved with {len(self.processed_files)} files")
        except Exception as e:
            logger.error(f"Failed to save checkpoint: {e}")

    def mark_processed(self, checksum: str) -> None:
        """Mark a file as processed.
        
        Args:
            checksum: File checksum
        """
        self.processed_files.add(checksum)
        self.save()

    def is_processed(self, checksum: str) -> bool:
        """Check if file was already processed.
        
        Args:
            checksum: File checksum
            
        Returns:
            True if file was processed
        """
        return checksum in self.processed_files

    def clear(self) -> None:
        """Clear checkpoint."""
        self.processed_files.clear()
        if self.checkpoint_file.exists():
            self.checkpoint_file.unlink()
        logger.info("Checkpoint cleared")

    def get_processed_count(self) -> int:
        """Get count of processed files."""
        return len(self.processed_files)
