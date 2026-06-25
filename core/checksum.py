"""Checksum calculation for file integrity verification."""

import hashlib
from pathlib import Path
from typing import Union


def calculate_sha256(file_path: Union[str, Path], chunk_size: int = 8192) -> str:
    """Calculate SHA256 checksum of a file.

    Args:
        file_path: Path to the file
        chunk_size: Size of chunks to read (default 8KB)

    Returns:
        Hexadecimal SHA256 hash string
    """
    file_path = Path(file_path)

    if not file_path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")

    if not file_path.is_file():
        raise ValueError(f"Path is not a file: {file_path}")

    sha256_hash = hashlib.sha256()

    try:
        with open(file_path, "rb") as f:
            while True:
                data = f.read(chunk_size)
                if not data:
                    break
                sha256_hash.update(data)
    except IOError as e:
        raise IOError(f"Cannot read file {file_path}: {e}") from e

    return sha256_hash.hexdigest()


def calculate_sha256_string(text: str) -> str:
    """Calculate SHA256 hash of a string."""
    return hashlib.sha256(text.encode("utf-8")).hexdigest()
