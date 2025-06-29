import pandas as pd
import sqlite3
from datetime import datetime
import os

# Define absolute paths
current_dir = os.path.dirname(os.path.abspath(__file__))
csv_path = os.path.join(current_dir, 'data_management_1.csv')
db_path = os.path.join(current_dir, 'database_management_1.db')

print(f"CSV path: {csv_path}")
print(f"Database path: {db_path}")

# Verify files exist
if not os.path.exists(csv_path):
    raise FileNotFoundError(f"CSV file not found at: {csv_path}")

# Read the CSV file
try:
    df = pd.read_csv(csv_path)
    print(f"Successfully read CSV with {len(df)} rows")
except Exception as e:
    print(f"Error reading CSV: {str(e)}")
    raise

# Connect to the SQLite database
try:
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    print("Successfully connected to database")
except Exception as e:
    print(f"Error connecting to database: {str(e)}")
    raise

# Create the table if it doesn't exist
try:
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS vehicles_1 (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            vehicle_type TEXT NOT NULL,
            brand TEXT NOT NULL,
            commercial_type TEXT NOT NULL,
            group_number INTEGER,
            license_plate TEXT NOT NULL UNIQUE,
            limit_periodic_inspection TEXT,
            kilometer_periodic_inspection INTEGER,
            limit_additional_inspection TEXT,
            kilometer_additional_inspection INTEGER,
            date_periodic_inspection TEXT,
            date_additional_inspection TEXT,
            comments TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    print("Table created/verified successfully")
except Exception as e:
    print(f"Error creating table: {str(e)}")
    raise

# Function to convert date format if not null
def convert_date(date_str):
    if pd.isna(date_str):
        return None
    try:
        # Convert to datetime object and then to desired format
        date_obj = pd.to_datetime(date_str)
        return date_obj.strftime('%Y-%m-%d')  # Changed to SQLite date format
    except:
        return None

# Convert date columns to the required format
date_columns = ['Limit Periodic Inspection', 'Limit Additional Inspection', 
                'Date Periodic Inspection', 'Date Additional Inspection']
for col in date_columns:
    df[col] = df[col].apply(convert_date)

# Clear existing data
try:
    cursor.execute('DELETE FROM vehicles_1')
    print("Cleared existing data from table")
except Exception as e:
    print(f"Error clearing table: {str(e)}")
    raise

# Insert data into the database
rows_inserted = 0
try:
    for _, row in df.iterrows():
        cursor.execute('''
            INSERT INTO vehicles_1 (
                vehicle_type,
                brand,
                commercial_type,
                group_number,
                license_plate,
                limit_periodic_inspection,
                kilometer_periodic_inspection,
                limit_additional_inspection,
                kilometer_additional_inspection,
                date_periodic_inspection,
                date_additional_inspection,
                comments
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            row['Vehicle type'],
            row['Brand'],
            row['Commercial type'],
            row['Group number'] if pd.notna(row['Group number']) else None,
            row['License plate'],
            row['Limit Periodic Inspection'],
            row['Kilometer Periodic Inspection'] if pd.notna(row['Kilometer Periodic Inspection']) else None,
            row['Limit Additional Inspection'],
            row['Kilometer Additional Inspection'] if pd.notna(row['Kilometer Additional Inspection']) else None,
            row['Date Periodic Inspection'],
            row['Date Additional Inspection'],
            row['Comments'] if pd.notna(row['Comments']) else None
        ))
        rows_inserted += 1
    print(f"Inserted {rows_inserted} rows")
except Exception as e:
    print(f"Error inserting data: {str(e)}")
    raise

# Commit the changes and close the connection
try:
    conn.commit()
    print("Changes committed successfully")
except Exception as e:
    print(f"Error committing changes: {str(e)}")
    raise
finally:
    conn.close()

print("Data import completed successfully!")
