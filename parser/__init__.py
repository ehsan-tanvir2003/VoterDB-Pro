"""Parser module for PDF text extraction and voter record parsing."""

from parser.pdf_reader import PDFReader
from parser.voter_parser import VoterParser
from parser.encoding import EncodingNormalizer
from parser.address_parser import AddressParser

__all__ = [
    "PDFReader",
    "VoterParser",
    "EncodingNormalizer",
    "AddressParser",
]
