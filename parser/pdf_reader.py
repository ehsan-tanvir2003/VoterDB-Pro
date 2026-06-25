"""PDF reader using PyMuPDF."""

from pathlib import Path
from typing import List, Optional, Union
import fitz
from core.logger import get_logger

logger = get_logger(__name__)


class PDFReader:
    """Reads and extracts text from PDF files using PyMuPDF."""

    def __init__(self, pdf_path: Union[str, Path]):
        """Initialize PDF reader.
        
        Args:
            pdf_path: Path to PDF file
        """
        self.pdf_path = Path(pdf_path)
        self.document: Optional[fitz.Document] = None
        self.page_count = 0

    def open(self) -> None:
        """Open PDF document."""
        if not self.pdf_path.exists():
            raise FileNotFoundError(f"PDF not found: {self.pdf_path}")

        try:
            self.document = fitz.open(str(self.pdf_path))
            self.page_count = len(self.document)
            logger.debug(f"PDF opened: {self.pdf_path} ({self.page_count} pages)")
        except Exception as e:
            logger.error(f"Failed to open PDF: {e}")
            raise

    def close(self) -> None:
        """Close PDF document."""
        if self.document:
            self.document.close()
            self.document = None
            logger.debug(f"PDF closed: {self.pdf_path}")

    def get_page_text_blocks(self, page_num: int) -> List[dict]:
        """Extract text blocks from a page.
        
        Args:
            page_num: Page number (0-indexed)
            
        Returns:
            List of text block dictionaries
        """
        if not self.document:
            self.open()

        if page_num < 0 or page_num >= self.page_count:
            raise ValueError(f"Invalid page number: {page_num}")

        try:
            page = self.document[page_num]
            blocks = page.get_text("blocks")
            return blocks
        except Exception as e:
            logger.error(f"Failed to extract blocks from page {page_num}: {e}")
            return []

    def get_page_text(self, page_num: int) -> str:
        """Extract text from a page.
        
        Args:
            page_num: Page number (0-indexed)
            
        Returns:
            Extracted text
        """
        blocks = self.get_page_text_blocks(page_num)
        text = ""
        for block in blocks:
            if isinstance(block, tuple) and len(block) >= 4:
                text += block[4] + "\n"
        return text

    def get_all_text(self) -> str:
        """Extract text from all pages.
        
        Returns:
            Combined text from all pages
        """
        if not self.document:
            self.open()

        try:
            text = ""
            for page_num in range(self.page_count):
                text += self.get_page_text(page_num)
                text += "\n--- PAGE BREAK ---\n"
            return text
        except Exception as e:
            logger.error(f"Failed to extract all text: {e}")
            return ""

    def get_metadata(self) -> dict:
        """Get PDF metadata.
        
        Returns:
            Dictionary with metadata
        """
        if not self.document:
            self.open()

        try:
            return self.document.metadata
        except Exception as e:
            logger.error(f"Failed to get metadata: {e}")
            return {}

    def __enter__(self):
        """Context manager entry."""
        self.open()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()
