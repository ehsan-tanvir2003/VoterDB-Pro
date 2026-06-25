"""PDF directory scanner."""

from pathlib import Path
from typing import List, Tuple, Optional
from core.logger import get_logger
from core.checksum import calculate_sha256

logger = get_logger(__name__)


class PDFScanner:
    """Scans directories for PDF files."""

    def __init__(self, root_directory: str | Path):
        """Initialize PDF scanner.
        
        Args:
            root_directory: Root directory to scan
        """
        self.root_directory = Path(root_directory)
        if not self.root_directory.exists():
            raise FileNotFoundError(f"Directory not found: {self.root_directory}")

    def scan(self) -> List[Tuple[Path, str]]:
        """Scan directory for PDF files.
        
        Returns:
            List of tuples (pdf_path, checksum)
        """
        pdf_files = []

        try:
            for pdf_path in self.root_directory.rglob("*.pdf"):
                if pdf_path.is_file():
                    try:
                        checksum = calculate_sha256(pdf_path)
                        pdf_files.append((pdf_path, checksum))
                        logger.debug(f"Found PDF: {pdf_path.name}")
                    except Exception as e:
                        logger.warning(f"Could not calculate checksum for {pdf_path}: {e}")
            logger.info(f"Scanned directory: found {len(pdf_files)} PDFs")
        except Exception as e:
            logger.error(f"Scan failed: {e}")
            raise

        return pdf_files

    def get_pdf_count(self) -> int:
        """Get count of PDF files in directory."""
        return len(list(self.root_directory.rglob("*.pdf")))
