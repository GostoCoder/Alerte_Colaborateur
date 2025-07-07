# Import necessary libraries
from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey, Date
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

# Create a new base class for declarative models
Base = declarative_base()
# Define the Collaborateur model
class Collaborateur(Base):
    __tablename__ = "collaborateurs"
    id = Column(Integer, primary_key=True, index=True)
    nom = Column(String, nullable=False)
    prenom = Column(String, nullable=False)
    ifo = Column(Date, nullable=True)
    caces = Column(Date, nullable=True)
    airr = Column(Date, nullable=True)
    hgo = Column(Date, nullable=True)
    bo = Column(Date, nullable=True)
    visite_med = Column(Date, nullable=True)
    brevet_secour = Column(Date, nullable=True)
    commentaire = Column(Text, nullable=True)

    def __repr__(self):
        return (
            f"<Collaborateur(id={self.id}, nom={self.nom}, prenom={self.prenom})>"
        )
