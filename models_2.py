# Import necessary libraries
from sqlalchemy import Column, Integer, String, DateTime, Text, Date
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

# Create a new base class for declarative models
Base = declarative_base()
class CollaborateurPoidsLouud(Base):
    __tablename__ = "collaborateurs_poids_louud"
    id = Column(Integer, primary_key=True, autoincrement=True)
    nom = Column(String, nullable=False)
    prenom = Column(String, nullable=False)
    date_renouvellement = Column(Date, nullable=True)
    date_validite = Column(Date, nullable=True)
    commentaire = Column(Text, nullable=True)

    def __repr__(self):
        return f"<CollaborateurPoidsLouud(id={self.id}, nom={self.nom}, prenom={self.prenom})>"
