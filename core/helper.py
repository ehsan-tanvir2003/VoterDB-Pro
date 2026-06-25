"""Helper utilities for VoterDB Pro."""

import re
from datetime import datetime
from pathlib import Path
from typing import Any, List, Optional, Union


def ensure_directory(path: Union[str, Path]) -> Path:
    """Ensure a directory exists, creating it if necessary."""
    path = Path(path)
    path.mkdir(parents=True, exist_ok=True)
    return path


def get_file_size(file_path: Union[str, Path]) -> int:
    """Get file size in bytes."""
    return Path(file_path).stat().st_size


def format_file_size(size_bytes: int) -> str:
    """Format bytes to human-readable size."""
    for unit in ["B", "KB", "MB", "GB", "TB"]:
        if size_bytes < 1024.0:
            return f"{size_bytes:.2f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.2f} PB"


def sanitize_filename(filename: str) -> str:
    """Remove invalid characters from filename."""
    invalid_chars = r'[<>:"/\\\|?*]'
    return re.sub(invalid_chars, "_", filename)


def is_valid_voter_number(voter_no: str) -> bool:
    """Validate voter number format."""
    if not voter_no:
        return False
    return bool(re.match(r"^\d{8,20}$", voter_no.strip()))


def is_valid_postcode(postcode: str) -> bool:
    """Validate postcode format."""
    if not postcode:
        return False
    return bool(re.match(r"^\d{4,6}$", postcode.strip()))


def clean_text(text: str) -> str:
    """Clean text by removing extra whitespace and control characters."""
    if not text:
        return ""
    text = "".join(char for char in text if ord(char) >= 32 or char in "\n\r\t")
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def parse_date(date_str: str, formats: Optional[List[str]] = None) -> Optional[datetime]:
    """Parse date string with multiple format support."""
    if not date_str:
        return None

    if formats is None:
        formats = ["%d/%m/%Y", "%d-%m-%Y", "%Y-%m-%d", "%d/%m/%y", "%d-%m-%y"]

    for fmt in formats:
        try:
            return datetime.strptime(date_str.strip(), fmt)
        except ValueError:
            continue

    return None


def truncate_string(text: str, max_length: int, suffix: str = "...") -> str:
    """Truncate string to maximum length."""
    if len(text) <= max_length:
        return text
    return text[: max_length - len(suffix)] + suffix


def group_by(items: List[dict], key: str) -> dict:
    """Group list of dicts by a key."""
    result = {}
    for item in items:
        k = item.get(key)
        if k not in result:
            result[k] = []
        result[k].append(item)
    return result


def batch_list(items: List[Any], batch_size: int) -> List[List[Any]]:
    """Split list into batches."""
    return [items[i : i + batch_size] for i in range(0, len(items), batch_size)]
