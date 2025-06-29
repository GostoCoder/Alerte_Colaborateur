import os
from sqlalchemy import create_engine
from models_1 import Base as Base_1
from models_2 import Base as Base_2
from models_3 import Base as Base_3
from models_4 import Base as Base_4

def reset_database(db_number):
    print(f"Resetting database {db_number}...")
    
    # Define database URL based on the database number
    if db_number == 1:
        db_url = "sqlite:///database_management_1.db"
        Base = Base_1
    elif db_number == 2:
        db_url = "sqlite:///vehicle_management_2.db"
        Base = Base_2
    elif db_number == 3:
        db_url = "sqlite:///database_management_3.db"  # Updated to match database_3.py
        Base = Base_3
    elif db_number == 4:
        db_url = "sqlite:///database_management_4.db"  # Updated to match database_4.py
        Base = Base_4
    
    # Remove existing database file if it exists
    db_file = db_url.replace("sqlite:///", "")
    if os.path.exists(db_file):
        os.remove(db_file)
        print(f"Removed existing database file: {db_file}")
    
    # Create engine
    engine = create_engine(db_url)
    
    # Create all tables
    Base.metadata.create_all(bind=engine)
    print(f"Created all tables in database {db_number}")

def reset_all_databases():
    for db_number in range(1, 5):
        reset_database(db_number)
    print("All databases have been reset successfully!")

if __name__ == "__main__":
    reset_all_databases()
