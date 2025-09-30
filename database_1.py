from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import logging
import os
from models_1 import Collaborateur, Base

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

from config_1 import SQLALCHEMY_DATABASE_URL
engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db():
    logger.info("Creating database tables")
    Base.metadata.create_all(bind=engine)
    logger.info("Database tables created successfully")

if __name__ == "__main__":
    init_db()
