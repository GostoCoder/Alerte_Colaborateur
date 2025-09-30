#!/usr/bin/env python3
"""
create_collaborateurs_db.py

Creates an SQLite database file with the following schema (table: collaborateurs):

- id               : INTEGER PRIMARY KEY AUTOINCREMENT
- nom              : TEXT NOT NULL
- prenom           : TEXT NOT NULL
- fimo             : DATE (store as ISO YYYY-MM-DD text)
- caces            : DATE
- aipr             : DATE
- hg0b0            : DATE
- visite_med       : DATE
- brevet_secour    : DATE
- commentaire      : TEXT

All fields except `commentaire` are expected to be dates (stored as ISO-formatted TEXT).
"""
from __future__ import annotations
import sqlite3
import argparse
from pathlib import Path

CREATE_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS collaborateurs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nom TEXT NOT NULL,
    prenom TEXT NOT NULL,
    fimo TEXT,
    caces TEXT,
    aipr TEXT,
    hg0b0 TEXT,
    visite_med TEXT,
    brevet_secour TEXT,
    commentaire TEXT
);
"""

def create_db(path: str | Path) -> None:
    db_path = Path(path)
    conn = sqlite3.connect(str(db_path))
    try:
        cur = conn.cursor()
        cur.execute(CREATE_TABLE_SQL)
        conn.commit()
    finally:
        conn.close()

def main() -> None:
    parser = argparse.ArgumentParser(description="Create SQLite DB with 'collaborateurs' schema.")
    parser.add_argument(
        "--db",
        "-d",
        default="database_management_1.db",
        help="Path to output .db file (default: database_management_1.db)",
    )
    args = parser.parse_args()
    create_db(args.db)
    print(f"Database created/updated at: {args.db}")

if __name__ == "__main__":
    main()
