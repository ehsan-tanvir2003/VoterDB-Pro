"""Data models for VoterDB Pro."""

from dataclasses import dataclass, field
from typing import Optional
from datetime import datetime


@dataclass
class VoterRecord:
    """Represents a single voter record."""

    id: Optional[int] = None
    pdf_id: Optional[int] = None
    serial: Optional[str] = None
    voter_no: str = ""
    name: Optional[str] = None
    father: Optional[str] = None
    mother: Optional[str] = None
    occupation: Optional[str] = None
    dob: Optional[str] = None
    address: Optional[str] = None
    house_no: Optional[str] = None
    road: Optional[str] = None
    village: Optional[str] = None
    post_office: Optional[str] = None
    postcode: Optional[str] = None
    ward: Optional[str] = None
    union_name: Optional[str] = None
    municipality: Optional[str] = None
    upazila: Optional[str] = None
    district: Optional[str] = None
    division: Optional[str] = None
    gender: Optional[str] = None
    page_number: Optional[int] = None

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            k: v
            for k, v in self.__dict__.items()
            if v is not None and k != "id" and k != "pdf_id"
        }

    def to_dict_with_pdf(self, pdf_id: int) -> dict:
        """Convert to dictionary with pdf_id."""
        data = self.to_dict()
        data["pdf_id"] = pdf_id
        return data


@dataclass
class PDFFileRecord:
    """Represents a PDF file record."""

    id: Optional[int] = None
    checksum: str = ""
    filename: str = ""
    district: Optional[str] = None
    upazila: Optional[str] = None
    ward: Optional[str] = None
    area_name: Optional[str] = None
    area_code: Optional[str] = None
    gender: Optional[str] = None
    total_records: int = 0
    imported_at: Optional[datetime] = None

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            k: v
            for k, v in self.__dict__.items()
            if v is not None and k != "id"
        }


@dataclass
class ImportHistoryRecord:
    """Represents an import history record."""

    id: Optional[int] = None
    checksum: str = ""
    filename: str = ""
    status: str = ""
    message: Optional[str] = None
    created_at: Optional[datetime] = None

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            k: v
            for k, v in self.__dict__.items()
            if v is not None and k != "id"
        }
