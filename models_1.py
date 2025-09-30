from sqlalchemy import Column, Integer, String, Text, Date
from sqlalchemy.orm import declarative_base

Base = declarative_base()

class Collaborateur(Base):
    __tablename__ = "collaborateurs"
    id = Column(Integer, primary_key=True, autoincrement=True)
    nom = Column(String(100), nullable=False)
    prenom = Column(String(100), nullable=False)
    fimo = Column(Date, nullable=True)
    caces = Column(Date, nullable=True)
    aipr = Column(Date, nullable=True)
    hg0b0 = Column(Date, nullable=True)
    visite_med = Column(Date, nullable=True)
    brevet_secour = Column(Date, nullable=True)
    commentaire = Column(Text, nullable=True)

    def __repr__(self):
        return f"<Collaborateur(id={self.id}, nom={self.nom}, prenom={self.prenom})>"
