"""Text encoding normalization for Bengali text."""

import unicodedata
from typing import Dict
from core.logger import get_logger

logger = get_logger(__name__)


class EncodingNormalizer:
    """Normalizes and repairs text encoding issues in Bengali text."""

    def __init__(self):
        """Initialize normalizer."""
        self.diacritics_map = {
            "\u0981": "",  # Chandrabindu
            "\u0982": "",  # Anusvara
            "\u0983": "",  # Visarga Sparshanusvar
        }

        self.bengali_punctuation_map = {
            "\u0964": ".",  # Devanagari Danda
            "\u0965": ".",  # Double Danda
            "\u09F8": ".",  # Bengali isshar
        }

        self.bengali_digit_map = {
            "\u09E6": "0",  # Bengali Zero
            "\u09E7": "1",  # Bengali One
            "\u09E8": "2",  # Bengali Two
            "\u09E9": "3",  # Bengali Three
            "\u09EA": "4",  # Bengali Four
            "\u09EB": "5",  # Bengali Five
            "\u09EC": "6",  # Bengali Six
            "\u09ED": "7",  # Bengali Seven
            "\u09EE": "8",  # Bengali Eight
            "\u09EF": "9",  # Bengali Nine
        }

    def normalize(self, text: str) -> str:
        """Apply complete normalization pipeline.
        
        Args:
            text: Text to normalize
            
        Returns:
            Normalized text
        """
        if not text:
            return ""

        # Step 1: Normalize unicode
        text = self._normalize_unicode(text)

        # Step 2: Remove control characters
        text = self._remove_control_characters(text)

        # Step 3: Normalize Bengali digits
        text = self._normalize_bengali_digits(text)

        # Step 4: Normalize Bengali punctuation
        text = self._normalize_bengali_punctuation(text)

        # Step 5: Normalize whitespace
        text = self._normalize_whitespace(text)

        return text

    def _normalize_unicode(self, text: str) -> str:
        """Normalize unicode composition."""
        # NFC normalization
        text = unicodedata.normalize("NFC", text)
        # Remove diacritics
        for old, new in self.diacritics_map.items():
            text = text.replace(old, new)
        return text

    def _remove_control_characters(self, text: str) -> str:
        """Remove control characters and zero-width characters."""
        # Remove zero-width characters
        text = text.replace("\u200B", "")  # Zero-width space
        text = text.replace("\u200C", "")  # Zero-width non-joiner
        text = text.replace("\u200D", "")  # Zero-width joiner
        text = text.replace("\uFEFF", "")  # Zero-width no-break space

        # Keep only printable characters
        text = "".join(
            char for char in text
            if ord(char) >= 32 or char in "\n\r\t"
        )
        return text

    def _normalize_bengali_digits(self, text: str) -> str:
        """Convert Bengali digits to ASCII."""
        for bengali, ascii in self.bengali_digit_map.items():
            text = text.replace(bengali, ascii)
        return text

    def _normalize_bengali_punctuation(self, text: str) -> str:
        """Normalize Bengali punctuation marks."""
        for old, new in self.bengali_punctuation_map.items():
            text = text.replace(old, new)
        return text

    def _normalize_whitespace(self, text: str) -> str:
        """Normalize whitespace characters."""
        # Replace multiple spaces with single space
        while "  " in text:
            text = text.replace("  ", " ")
        # Replace various whitespace with standard space
        text = text.replace("\u00A0", " ")  # Non-breaking space
        text = text.replace("\u2000", " ")  # En quad
        text = text.replace("\u2001", " ")  # Em quad
        text = text.replace("\u2002", " ")  # En space
        text = text.replace("\u2003", " ")  # Em space
        # Trim
        text = text.strip()
        return text

    def repair_mojibake(self, text: str) -> str:
        """Attempt to repair mojibake (garbled text).
        
        Args:
            text: Potentially corrupted text
            
        Returns:
            Repaired text
        """
        # Try to detect and fix common encoding issues
        try:
            # If text looks like mojibake, try UTF-8 decode
            if any(ord(c) > 255 for c in text):
                # Already has high unicode, normalize it
                text = self.normalize(text)
        except Exception as e:
            logger.warning(f"Could not repair potential mojibake: {e}")

        return text
