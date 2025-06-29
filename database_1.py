# Import necessary libraries
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models_1 import Base
import logging
import os

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Define the URL of the SQLite database
SQLALCHEMY_DATABASE_URL = "sqlite:///database_management_1.db"

# Create a new database engine
logger.info("Creating database engine")
engine = create_engine(SQLALCHEMY_DATABASE_URL)

# Create a new session maker
logger.info("Creating session maker")
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Define a function to get a database connection
def get_db():
    logger.info("Getting database connection")
    # Create a new database connection
    db = SessionLocal()
    try:
        # Yield the database connection
        yield db
    finally:
        # Close the database connection
        logger.info("Closing database connection")
        db.close()

def init_db():
    """Initialize the database"""
    logger.info("Creating database tables")
    Base.metadata.create_all(bind=engine)
    logger.info("Database tables created successfully")

# Initialize the database when this module is imported
if __name__ == "__main__":
    init_db()
