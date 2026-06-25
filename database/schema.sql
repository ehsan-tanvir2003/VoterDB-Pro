CREATE TABLE IF NOT EXISTS pdf_files (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    checksum TEXT NOT NULL UNIQUE,
    filename TEXT NOT NULL,
    district TEXT,
    upazila TEXT,
    ward TEXT,
    area_name TEXT,
    area_code TEXT,
    gender TEXT,
    total_records INTEGER,
    imported_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS voters (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    pdf_id INTEGER NOT NULL,
    serial TEXT,
    voter_no TEXT NOT NULL UNIQUE,
    name TEXT,
    father TEXT,
    mother TEXT,
    occupation TEXT,
    dob TEXT,
    address TEXT,
    house_no TEXT,
    road TEXT,
    village TEXT,
    post_office TEXT,
    postcode TEXT,
    ward TEXT,
    union_name TEXT,
    municipality TEXT,
    upazila TEXT,
    district TEXT,
    division TEXT,
    gender TEXT,
    page_number INTEGER,
    FOREIGN KEY(pdf_id) REFERENCES pdf_files(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS import_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    checksum TEXT NOT NULL,
    filename TEXT NOT NULL,
    status TEXT NOT NULL,
    message TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_voters_voter_no ON voters(voter_no);
CREATE INDEX IF NOT EXISTS idx_voters_pdf_id ON voters(pdf_id);
CREATE INDEX IF NOT EXISTS idx_voters_district ON voters(district);
CREATE INDEX IF NOT EXISTS idx_voters_upazila ON voters(upazila);
CREATE INDEX IF NOT EXISTS idx_pdf_files_checksum ON pdf_files(checksum);
CREATE INDEX IF NOT EXISTS idx_import_history_checksum ON import_history(checksum);
