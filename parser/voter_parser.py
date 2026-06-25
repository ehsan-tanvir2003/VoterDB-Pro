"""Voter record parser using state machine."""

from typing import List, Optional, Dict, Any
from dataclasses import dataclass
from enum import Enum
from core.logger import get_logger
from database.models import VoterRecord
from parser.encoding import EncodingNormalizer
from parser.address_parser import AddressParser

logger = get_logger(__name__)


class ParserState(Enum):
    """Parser state machine states."""

    START = 0
    SERIAL = 1
    NAME = 2
    VOTER_NO = 3
    FATHER = 4
    MOTHER = 5
    OCCUPATION = 6
    DOB = 7
    ADDRESS = 8
    COMPLETE = 9


class VoterParser:
    """Parses voter records from PDF text using state machine."""

    def __init__(self, text_blocks: List[str]):
        """Initialize voter parser.
        
        Args:
            text_blocks: List of text blocks from PDF
        """
        self.text_blocks = text_blocks
        self.normalizer = EncodingNormalizer()
        self.address_parser = AddressParser()
        self.voters: List[VoterRecord] = []
        self.current_voter: Optional[VoterRecord] = None
        self.state = ParserState.START

    def parse(self) -> List[VoterRecord]:
        """Parse all voters from text blocks.
        
        Returns:
            List of parsed voter records
        """
        self.voters = []

        for block_num, block in enumerate(self.text_blocks):
            if not isinstance(block, str) or not block.strip():
                continue

            lines = block.split("\n")
            for line in lines:
                line = self.normalizer.normalize(line.strip())
                if line:
                    self._process_line(line, block_num)

        # Finalize last voter if any
        if self.current_voter and self.current_voter.voter_no:
            self.voters.append(self.current_voter)

        return self.voters

    def _process_line(self, line: str, block_num: int) -> None:
        """Process a single line of text."""
        if self.state == ParserState.START:
            self._handle_start_state(line)
        elif self.state == ParserState.SERIAL:
            self._handle_serial_state(line)
        elif self.state == ParserState.NAME:
            self._handle_name_state(line)
        elif self.state == ParserState.VOTER_NO:
            self._handle_voter_no_state(line)
        elif self.state == ParserState.FATHER:
            self._handle_father_state(line)
        elif self.state == ParserState.MOTHER:
            self._handle_mother_state(line)
        elif self.state == ParserState.OCCUPATION:
            self._handle_occupation_state(line)
        elif self.state == ParserState.DOB:
            self._handle_dob_state(line)
        elif self.state == ParserState.ADDRESS:
            self._handle_address_state(line)

    def _handle_start_state(self, line: str) -> None:
        """Handle START state - look for serial number."""
        # Check if line is a serial number (numeric)
        if line.isdigit() and 1 <= int(line) <= 999999:
            self.current_voter = VoterRecord(serial=line)
            self.state = ParserState.NAME

    def _handle_serial_state(self, line: str) -> None:
        """Handle SERIAL state."""
        if line.isdigit():
            self.current_voter.serial = line
            self.state = ParserState.NAME

    def _handle_name_state(self, line: str) -> None:
        """Handle NAME state."""
        if len(line) > 2:
            self.current_voter.name = line
            self.state = ParserState.VOTER_NO

    def _handle_voter_no_state(self, line: str) -> None:
        """Handle VOTER_NO state."""
        # Extract numeric voter number
        import re
        match = re.search(r'\b(\d{10,18})\b', line)
        if match:
            self.current_voter.voter_no = match.group(1)
            self.state = ParserState.FATHER
        else:
            # Try to extract from line
            digits = re.sub(r'\D', '', line)
            if len(digits) >= 10:
                self.current_voter.voter_no = digits[:18]
                self.state = ParserState.FATHER

    def _handle_father_state(self, line: str) -> None:
        """Handle FATHER state."""
        if len(line) > 2 and line != self.current_voter.name:
            self.current_voter.father = line
            self.state = ParserState.MOTHER

    def _handle_mother_state(self, line: str) -> None:
        """Handle MOTHER state."""
        if len(line) > 2:
            self.current_voter.mother = line
            self.state = ParserState.OCCUPATION

    def _handle_occupation_state(self, line: str) -> None:
        """Handle OCCUPATION state."""
        if len(line) > 1:
            self.current_voter.occupation = line
            self.state = ParserState.DOB

    def _handle_dob_state(self, line: str) -> None:
        """Handle DOB state."""
        # Try to parse date
        import re
        if re.search(r'\d{1,4}[/-]\d{1,2}[/-]\d{1,4}', line):
            self.current_voter.dob = line
            self.state = ParserState.ADDRESS
        elif len(line) > 3:
            self.current_voter.occupation = line

    def _handle_address_state(self, line: str) -> None:
        """Handle ADDRESS state."""
        if not self.current_voter.address:
            self.current_voter.address = line
        else:
            self.current_voter.address += " " + line

        # Check if we should move to next voter
        if line.isdigit() and 1 <= int(line) <= 999999:
            # Save current voter and start new one
            if self.current_voter.voter_no:
                self.voters.append(self.current_voter)
            self.current_voter = VoterRecord(serial=line)
            self.state = ParserState.NAME
