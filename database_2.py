import os
import logging
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models_2 import Base

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

from dotenv import load_dotenv
load_dotenv()
# Database configuration
DATABASE_URL = os.getenv("SQLALCHEMY_DATABASE_URL_2", "sqlite:///database_management_2.db")

def get_db():
    """Generator function to get database session"""
    engine = create_engine(DATABASE_URL)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()

def init_db():
    """Initialize the database by creating all tables"""
    try:
        logger.info("Creating database engine")
        # Create all tables
        engine = create_engine(DATABASE_URL)
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables created successfully")
    except Exception as e:
        logger.error(f"Error initializing database: {str(e)}")
        raise

if __name__ == "__main__":
    init_db()
