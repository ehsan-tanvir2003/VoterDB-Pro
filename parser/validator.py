"""Data validation utilities."""

import re
from typing import Optional
from core.logger import get_logger
from core.constants import (
    MIN_VOTER_NO_LENGTH,
    MAX_VOTER_NO_LENGTH,
    MIN_NAME_LENGTH,
    MAX_NAME_LENGTH,
)

logger = get_logger(__name__)


class DataValidator:
    """Validates voter record data."""

    @staticmethod
    def validate_voter_no(voter_no: str) -> bool:
        """Validate voter number."""
        if not voter_no:
            return False
        # Should be numeric and within length bounds
        if not re.match(r'^\d+$', voter_no.strip()):
            return False
        length = len(voter_no)
        return MIN_VOTER_NO_LENGTH <= length <= MAX_VOTER_NO_LENGTH

    @staticmethod
    def validate_name(name: str) -> bool:
        """Validate name field."""
        if not name:
            return False
        length = len(name.strip())
        return MIN_NAME_LENGTH <= length <= MAX_NAME_LENGTH

    @staticmethod
    def validate_date(date_str: str) -> bool:
        """Validate date format."""
        if not date_str:
            return False
        # Check for common date formats
        patterns = [
            r'^\d{1,4}[/-]\d{1,2}[/-]\d{1,4}$',
            r'^\d{2}/\d{2}/\d{4}$',
        ]
        return any(re.match(p, date_str.strip()) for p in patterns)

    @staticmethod
    def validate_postcode(postcode: str) -> bool:
        """Validate postcode."""
        if not postcode:
            return False
        return bool(re.match(r'^\d{4,6}$', postcode.strip()))

    @staticmethod
    def is_valid_voter_record(voter: dict) -> bool:
        """Validate complete voter record."""
        # Must have voter number and name
        if not DataValidator.validate_voter_no(voter.get('voter_no', '')):
            return False
        if not DataValidator.validate_name(voter.get('name', '')):
            return False
        return True
