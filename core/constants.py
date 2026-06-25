"""Constants used throughout VoterDB Pro."""

from typing import Final

TABLE_PDF_FILES: Final[str] = "pdf_files"
TABLE_VOTERS: Final[str] = "voters"
TABLE_IMPORT_HISTORY: Final[str] = "import_history"

STATUS_SUCCESS: Final[str] = "SUCCESS"
STATUS_FAILED: Final[str] = "FAILED"
STATUS_SKIPPED: Final[str] = "SKIPPED"
STATUS_PENDING: Final[str] = "PENDING"

PARSER_STATE_START: Final[int] = 0
PARSER_STATE_SERIAL: Final[int] = 1
PARSER_STATE_NAME: Final[int] = 2
PARSER_STATE_VOTER_NO: Final[int] = 3
PARSER_STATE_FATHER: Final[int] = 4
PARSER_STATE_MOTHER: Final[int] = 5
PARSER_STATE_OCCUPATION: Final[int] = 6
PARSER_STATE_DOB: Final[int] = 7
PARSER_STATE_ADDRESS: Final[int] = 8
PARSER_STATE_COMPLETE: Final[int] = 9

MIN_VOTER_NO_LENGTH: Final[int] = 8
MAX_VOTER_NO_LENGTH: Final[int] = 20
MIN_NAME_LENGTH: Final[int] = 2
MAX_NAME_LENGTH: Final[int] = 200
MIN_POSTCODE_LENGTH: Final[int] = 4
MAX_POSTCODE_LENGTH: Final[int] = 10

DEFAULT_PAGE_SIZE: Final[int] = 4096
DEFAULT_CACHE_SIZE: Final[int] = 65536
DEFAULT_TIMEOUT: Final[float] = 30.0
