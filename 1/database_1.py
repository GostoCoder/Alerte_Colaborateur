from sqlalchemy import create_engine, Column, Integer, String, Text
from sqlalchemy.orm import sessionmaker, declarative_base
import logging
import os

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

Base = declarative_base()

class Collaborateur(Base):
    __tablename__ = "collaborateurs"
    id = Column(Integer, primary_key=True, autoincrement=True)
    nom = Column(String, nullable=False)
    prenom = Column(String, nullable=False)
    fimo = Column(String)
    caces = Column(String)
    aipr = Column(String)
    hg0b0 = Column(String)
    visite_med = Column(String)
    brevet_secour = Column(String)
    commentaire = Column(Text)

SQLALCHEMY_DATABASE_URL = "sqlite:///database_management_1.db"
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
