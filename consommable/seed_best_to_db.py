import sqlite3
import csv
import os
from datetime import datetime

DB_PATH = "database_management_1.db"
CSV_PATH = os.path.join(os.path.dirname(__file__), "best.csv")
TABLE = "collaborateurs"

EXPECTED_FIELDS = ['id','nom','prenom','fimo','caces','aipr','hg0b0','visite_med','brevet_secour','commentaire']

def parse_date(value):
    """Parse an ISO date string (YYYY-MM-DD) and return ISO date (YYYY-MM-DD) or None.

    Accept only "%Y-%m-%d".
    """
    if not value:
        return None
    value = value.strip()
    if not value:
        return None
    try:
        return datetime.strptime(value, "%Y-%m-%d").strftime("%Y-%m-%d")
    except Exception:
        return None

def normalize_row(raw_row):
    """Return a dict with expected keys and stripped values (strings)."""
    row = {}
    # Build a lookup of original keys by their normalized form (strip+lower)
    key_map = {k.strip().lower(): k for k in raw_row.keys()}
    for key in EXPECTED_FIELDS:
        k_lower = key.strip().lower()
        orig_key = key_map.get(k_lower)
        # prefer the original-cased header if present, fall back to the raw key name
        val = raw_row.get(orig_key) if orig_key is not None else raw_row.get(key)
        if val is None:
            val = ""
        row[key] = val.strip() if isinstance(val, str) else str(val).strip()
    return row

def process_row(row, line_no):
    row = normalize_row(row)
    # id
    id_val = None
    if row['id']:
        try:
            id_val = int(row['id'])
        except Exception:
            print(f"Warning: invalid id on line {line_no}: {row['id']!r} -> storing NULL")
            id_val = None
    nom = row['nom'] or None
    prenom = row['prenom'] or None
    dates = []
    for field in ('fimo','caces','aipr','hg0b0','visite_med','brevet_secour'):
        raw = row.get(field,"") or ""
        parsed = parse_date(raw)
        if raw and parsed is None:
            print(f"Warning: unrecognized date format for '{field}' on line {line_no}: {raw!r} -> stored as NULL")
        dates.append(parsed)
    commentaire = row['commentaire'] or None
    return (id_val, nom, prenom, *dates, commentaire)

def seed_database():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    inserted = 0
    with open(CSV_PATH, newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        # validate header presence
        if reader.fieldnames is None:
            raise ValueError("CSV has no header")
        header = [h.strip().lower() for h in reader.fieldnames]
        expected_lower = [h.lower() for h in EXPECTED_FIELDS]
        missing = set(expected_lower) - set(header)
        if missing:
            raise ValueError(f"CSV is missing expected fields: {sorted(missing)}. Found header: {reader.fieldnames}")
        if header != expected_lower:
            # order differs but all expected fields are present — mapping by name will be used
            print(f"Warning: CSV header order differs from expected. Expected order: {EXPECTED_FIELDS}\n Found: {reader.fieldnames}\n Proceeding using mapping by field name.")
        for i, raw in enumerate(reader, start=2):
            try:
                values = process_row(raw, i)
                cursor.execute(
                    f"""INSERT OR REPLACE INTO {TABLE}
 (id, nom, prenom, fimo, caces, aipr, hg0b0, visite_med, brevet_secour, commentaire)
 VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                    values
                )
                inserted += 1
            except Exception as e:
                print(f"Error inserting line {i}: {e}")
    conn.commit()
    conn.close()
    print(f"Database seeded from best.csv. {inserted} rows inserted/updated.")

if __name__ == "__main__":
    seed_database()
