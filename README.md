# VoterDB Pro v1.0

A production-grade Python application for importing Bangladesh Election Commission voter-list PDFs into an optimized SQLite database.

## Overview

VoterDB Pro is designed to handle **200,000+ voter-list PDFs** with:

- **Fast imports**: Batch processing with optimized SQLite
- **Memory efficient**: Sub-500MB memory footprint
- **Robust parsing**: State-machine PDF parser with encoding repair
- **Resume capability**: Checkpoint-based import with duplicate detection
- **Production quality**: Comprehensive logging, error handling, and tests

## Features

✅ Recursive PDF scanning with SHA256 checksums  
✅ State-machine voter parser (no regex)  
✅ Bangladesh EC encoding normalization  
✅ Multiline address parsing and splitting  
✅ Batch insert optimization (1000 rows/transaction)  
✅ Import resumption and duplicate detection  
✅ Detailed import history tracking  
✅ SQLite WAL mode and performance optimization  
✅ Comprehensive logging and progress reporting  
✅ CSV and Excel exports  
✅ Unit tests with full coverage  

## Requirements

- Python 3.12+
- Windows 10/11 (or any OS with Python 3.12+)
- ~1GB disk space (grows with PDF count)

## Installation

1. **Clone the repository**:
   ```bash
   git clone https://github.com/ehsan-tanvir2003/VoterDB-Pro.git
   cd VoterDB-Pro
   ```

2. **Create virtual environment**:
   ```bash
   python -m venv venv
   venv\Scripts\activate  # Windows
   source venv/bin/activate  # Linux/Mac
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure the application** (optional):
   - Edit `config.py` to customize paths, logging, and database settings

## Quick Start

1. **Place PDFs** in the `pdfs/` folder

2. **Run the application**:
   ```bash
   python main.py
   ```

3. **Select operation**:
   ```
   VoterDB Pro v1.0
   
   1. Import PDFs
   2. Verify Database
   3. Optimize Database
   4. Rebuild Indexes
   5. Exit
   
   Select option (1-5): 1
   ```

## Usage

### Import PDFs

```bash
python main.py
# Select option 1 to import PDFs from pdfs/ directory
```

The importer will:
- Scan for PDFs recursively
- Extract metadata (district, upazila, ward, gender, etc.)
- Parse voters using state-machine parser
- Batch insert 1000 rows per transaction
- Skip duplicates and resume from checkpoints
- Log all operations and errors

### Verify Database

```bash
python main.py
# Select option 2 to verify database integrity
```

### Optimize Database

```bash
python main.py
# Select option 3 to optimize database
```

Vacuums and analyzes database for performance.

### Export Data

```python
from exports.csv_export import export_to_csv
from exports.excel_export import export_to_excel

export_to_csv('voters.csv')
export_to_excel('voters.xlsx')
```

## Project Structure

```
VoterDB-Pro/
├── main.py                 # Entry point
├── config.py              # Configuration
├── requirements.txt       # Dependencies
├── README.md             # This file
│
├── core/                 # Core utilities
│   ├── config.py        # Environment config
│   ├── constants.py     # Constants
│   ├── logger.py        # Logging setup
│   ├── checksum.py      # SHA256 checksums
│   └── helper.py        # Helper utilities
│
├── database/            # Database layer
│   ├── database.py      # SQLite connection
│   ├── schema.sql       # Database schema
│   ├── models.py        # Data models
│   ├── migrate.py       # Schema migration
│   ├── batch_writer.py  # Batch insert
│   ├── history.py       # Import history
│   └── optimize.py      # Database optimization
│
├── parser/              # PDF parsing
│   ├── pdf_reader.py    # PyMuPDF wrapper
│   ├── block_reader.py  # Text block reading
│   ├── encoding.py      # Encoding normalization
│   ├── tokenizer.py     # Text tokenization
│   ├── metadata.py      # Metadata extraction
│   ├── voter_parser.py  # State-machine voter parser
│   ├── address_parser.py# Address splitting
│   └── validator.py     # Data validation
│
├── importer/            # Import engine
│   ├── importer.py      # Main importer
│   ├── scanner.py       # PDF scanner
│   ├── checkpoint.py    # Checkpoint support
│   ├── progress.py      # Progress reporting
│   ├── worker.py        # Worker threads
│   └── queue.py         # Task queue
│
├── exports/             # Export modules
│   ├── csv_export.py    # CSV export
│   └── excel_export.py  # Excel export
│
├── tests/               # Unit tests
│   ├── test_parser.py
│   ├── test_database.py
│   ├── test_encoding.py
│   ├── test_importer.py
│   └── test_address_parser.py
│
├── data/                # Database storage
│   └── voterdb.sqlite
│
├── pdfs/                # Input PDFs
│
├── logs/                # Application logs
│
└── docs/                # Documentation
    ├── ARCHITECTURE.md
    ├── INSTALLATION.md
    ├── PARSER.md
    └── DATABASE.md
```

## Database Schema

### pdf_files
Stores metadata about imported PDFs:
- `checksum`: SHA256 hash (unique)
- `filename`: Original filename
- `district`, `upazila`, `ward`: Location data
- `area_name`, `area_code`: Area identification
- `gender`: Voter gender
- `total_records`: Voter count in PDF
- `imported_at`: Import timestamp

### voters
Stores parsed voter records:
- `voter_no`: Unique voter number (indexed)
- `serial`, `name`, `father`, `mother`: Basic info
- `occupation`, `dob`: Professional and demographic data
- `address`, `house_no`, `road`, `village`: Full address
- `post_office`, `postcode`: Postal info
- `ward`, `union_name`, `municipality`: Administrative areas
- `upazila`, `district`, `division`: Geographic hierarchy
- `gender`, `page_number`: Additional data

### import_history
Tracks all import operations:
- `checksum`: PDF identifier
- `filename`: Source PDF
- `status`: SUCCESS, FAILED, SKIPPED
- `message`: Detailed status message
- `created_at`: Timestamp

## Performance

### Optimization Features

- **SQLite WAL mode**: Concurrent read/write
- **NORMAL sync**: Balance between safety and speed
- **Memory temp store**: Fast temporary data
- **Large cache**: 64MB page cache
- **Foreign keys**: Data integrity
- **Batch inserts**: 1000 rows per transaction
- **Indexed searches**: Voter number index

### Benchmarks

Expected performance on modern hardware:
- **Parsing**: 100-200 voters/second per PDF
- **Import**: 50-100 PDFs/minute (depends on PDF size)
- **Memory**: <500MB for 40M+ voters
- **Storage**: ~2GB per 1M voters

## Error Handling

VoterDB Pro continues processing on errors:

- **Malformed PDFs**: Logged and skipped
- **Encoding errors**: Repaired using normalization pipeline
- **Duplicate voters**: Detected and skipped
- **Duplicate PDFs**: SHA256 prevents re-import
- **Unexpected formats**: Logged with context

No single PDF failure stops the entire import.

## Logging

Logs are written to `logs/voterdb.log`:

```
2026-06-25 14:30:45,123 [INFO] Starting VoterDB Pro v1.0
2026-06-25 14:30:46,456 [INFO] Database initialized
2026-06-25 14:30:47,789 [INFO] Scanning pdfs/ directory...
2026-06-25 14:31:02,345 [INFO] Found 5 PDFs to process
2026-06-25 14:31:15,678 [INFO] PDF: voter_list_dhaka_001.pdf (2,345 voters)
2026-06-25 14:31:45,901 [INFO] Imported 2,345 voters in 30.22 seconds
```

## Testing

Run comprehensive tests:

```bash
pytest tests/ -v
pytest tests/ --cov=core,parser,database,importer
```

Test coverage includes:
- Parser accuracy
- Database integrity
- Encoding normalization
- Address parsing
- Import process
- Error handling

## API Reference

### Core

```python
from core.logger import setup_logger
from core.checksum import calculate_sha256
from core.config import settings

logger = setup_logger('voterdb')
sha256 = calculate_sha256('path/to/file.pdf')
config = settings
```

### Database

```python
from database.database import Database
from database.models import VoterRecord, PDFFile

db = Database('data/voterdb.sqlite')
db.initialize()
voters = db.get_voters(limit=100)
```

### Parser

```python
from parser.pdf_reader import PDFReader
from parser.voter_parser import VoterParser

reader = PDFReader('path/to/pdf')
parser = VoterParser(reader)
voters = parser.parse()
```

### Importer

```python
from importer.importer import Importer

importer = Importer()
importer.import_pdfs_from_directory('pdfs/')
```

## Contributing

Contributions are welcome! Please:

1. Follow PEP8 style
2. Add type hints to all functions
3. Write tests for new features
4. Update documentation
5. Follow the modular architecture

## License

MIT License - See LICENSE file for details

## Changelog

### v1.0 (2026-06-25)
- Initial release
- PDF parsing with state-machine
- SQLite database with WAL mode
- Batch import with checkpoints
- Comprehensive logging and error handling
- CSV and Excel exports
- Full test coverage

## Support

For issues, questions, or suggestions:

1. Check existing issues on GitHub
2. Review documentation in `docs/`
3. Create a new GitHub issue with details

## Roadmap

Future enhancements:

- GUI application (PyQt6)
- REST API (FastAPI)
- Full-text search (FTS5)
- Advanced analytics dashboard
- Parallel PDF processing
- Cloud storage support

---

**VoterDB Pro** - Production-grade voter database for Bangladesh Election Commission data.
