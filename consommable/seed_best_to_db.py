import sqlite3
import csv

DB_PATH = "database_management_1.db"
CSV_PATH = "best.csv"
TABLE = "collaborateurs"

def seed_database():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    with open(CSV_PATH, newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            cursor.execute(
                f"""INSERT OR REPLACE INTO {TABLE} 
                (id, nom, prenom, fimo, caces, aipr, hg0b0, visite_med, brevet_secour, commentaire)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (
                    row['id'],
                    row['nom'],
                    row['prenom'],
                    row['fimo'] if row['fimo'] else None,
                    row['caces'] if row['caces'] else None,
                    row['aipr'] if row['aipr'] else None,
                    row['hg0b0'] if row['hg0b0'] else None,
                    row['visite_med'] if row['visite_med'] else None,
                    row['brevet_secour'] if row['brevet_secour'] else None,
                    row['commentaire'] if row['commentaire'] else None,
                )
            )
    conn.commit()
    conn.close()

if __name__ == "__main__":
    seed_database()
    print("Database seeded from best.csv.")