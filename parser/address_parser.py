"""Address parsing and splitting."""

from typing import Dict, Optional
from core.logger import get_logger

logger = get_logger(__name__)


class AddressParser:
    """Parses and splits address into components."""

    def __init__(self):
        """Initialize address parser."""
        self.administrative_areas = {
            "divisions": [
                "Dhaka", "Chittagong", "Khulna", "Rajshahi",
                "Barisal", "Sylhet", "Rangpur", "Mymensingh"
            ],
            "districts": {},  # Would be populated with real data
        }

    def parse(self, address: str) -> Dict[str, Optional[str]]:
        """Parse address into components.
        
        Args:
            address: Full address string
            
        Returns:
            Dictionary with parsed components
        """
        if not address:
            return {}

        components = {
            "house_no": None,
            "road": None,
            "village": None,
            "post_office": None,
            "postcode": None,
            "upazila": None,
            "district": None,
            "division": None,
            "union": None,
            "municipality": None,
            "ward": None,
        }

        # Split address by common delimiters
        parts = self._split_address(address)

        # Extract components from parts
        for part in parts:
            part = part.strip()
            if not part:
                continue

            # Try to identify component type
            component_type = self._identify_component(part)
            if component_type and components[component_type] is None:
                components[component_type] = part

        return {k: v for k, v in components.items() if v is not None}

    def _split_address(self, address: str) -> list:
        """Split address into parts."""
        # Split by comma, slash, hyphen, or multiple spaces
        import re
        parts = re.split(r'[,/\-]|\s{2,}', address)
        return parts

    def _identify_component(self, part: str) -> Optional[str]:
        """Identify component type from text."""
        part_lower = part.lower()

        # Check for postcode (digits only)
        if part.isdigit() and len(part) in [4, 5, 6]:
            return "postcode"

        # Check for known districts/upazilas
        if "upazila" in part_lower or "উপজেলা" in part:
            return "upazila"
        if "district" in part_lower or "জেলা" in part:
            return "district"
        if "division" in part_lower or "বিভাগ" in part:
            return "division"
        if "union" in part_lower or "ইউনিয়ন" in part:
            return "union"
        if "municipality" in part_lower or "পৌর" in part:
            return "municipality"
        if "ward" in part_lower or "ওয়ার্ড" in part:
            return "ward"
        if "village" in part_lower or "গ্রাম" in part:
            return "village"
        if "road" in part_lower or "রোড" in part or "রাস্তা" in part:
            return "road"

        # Default to post office or village
        if len(part) > 3:
            return "village"

        return None

    def extract_postcode(self, address: str) -> Optional[str]:
        """Extract postcode from address."""
        import re
        match = re.search(r'\b\d{4,6}\b', address)
        return match.group(0) if match else None
