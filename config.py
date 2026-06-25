"""Configuration module for VoterDB Pro.

This module provides centralized configuration management for the application,
including database paths, logging settings, and import parameters.
"""

from pathlib import Path
from typing import Optional


class Config:
    """Application configuration."""

    # Project paths
    PROJECT_ROOT = Path(__file__).parent
    DATA_DIR = PROJECT_ROOT / "data"
    PDFS_DIR = PROJECT_ROOT / "pdfs"
    LOGS_DIR = PROJECT_ROOT / "logs"
    DOCS_DIR = PROJECT_ROOT / "docs"
    TESTS_DIR = PROJECT_ROOT / "tests"

    # Database
    DATABASE_PATH = DATA_DIR / "voterdb.sqlite"
    DATABASE_TIMEOUT = 30.0
    DATABASE_CACHE_SIZE = 64 * 1024  # 64MB
    DATABASE_PAGE_SIZE = 4096

    # Logging
    LOG_FILE = LOGS_DIR / "voterdb.log"
    LOG_LEVEL = "INFO"
    LOG_FORMAT = "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
    LOG_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"

    # Import settings
    BATCH_SIZE = 1000  # Rows per transaction
    CHECKPOINT_INTERVAL = 10  # PDFs between checkpoints
    MAX_WORKERS = 4  # Parallel import workers
    TIMEOUT_PER_PDF = 300  # Seconds

    # Application
    APP_NAME = "VoterDB Pro"
    APP_VERSION = "1.0"
    PYTHON_VERSION = "3.12+"

    @classmethod
    def initialize(cls) -> None:
        """Create necessary directories."""
        for directory in [cls.DATA_DIR, cls.PDFS_DIR, cls.LOGS_DIR, cls.DOCS_DIR]:
            directory.mkdir(parents=True, exist_ok=True)

    @classmethod
    def get_config(cls) -> dict:
        """Get configuration as dictionary."""
        return {
            "app_name": cls.APP_NAME,
            "app_version": cls.APP_VERSION,
            "python_version": cls.PYTHON_VERSION,
            "project_root": str(cls.PROJECT_ROOT),
            "database_path": str(cls.DATABASE_PATH),
            "pdfs_directory": str(cls.PDFS_DIR),
            "logs_directory": str(cls.LOGS_DIR),
            "batch_size": cls.BATCH_SIZE,
            "checkpoint_interval": cls.CHECKPOINT_INTERVAL,
            "max_workers": cls.MAX_WORKERS,
        }


# Create default configuration
settings = Config()
