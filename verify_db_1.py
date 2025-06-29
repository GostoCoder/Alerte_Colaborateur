import sqlite3
import os

# Get the absolute path to the database
current_dir = os.path.dirname(os.path.abspath(__file__))
db_path = os.path.join(current_dir, 'database_management_1.db')

# Connect to the database
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Get the number of rows
cursor.execute('SELECT COUNT(*) FROM vehicles')
count = cursor.fetchone()[0]
print(f"Total number of rows in database: {count}")

# Get the first few rows
print("\nFirst 5 rows from the database:")
cursor.execute('SELECT * FROM vehicles LIMIT 5')
rows = cursor.fetchall()
for row in rows:
    print(row)

conn.close()
