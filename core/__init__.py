"""Core module for VoterDB Pro.

Provides essential utilities including configuration, logging, checksums,
and helper functions used throughout the application.
"""

from core.logger import setup_logger
from core.checksum import calculate_sha256
from core.config import Config, settings

__all__ = ["setup_logger", "calculate_sha256", "Config", "settings"]
