from sqlalchemy import Column, Integer, String, Text
from sqlalchemy.orm import declarative_base

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
