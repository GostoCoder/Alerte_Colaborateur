from sqlalchemy import Column, Integer, String, Date, Text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from typing import Optional
import datetime


class Base(DeclarativeBase):
    pass


class Collaborateur(Base):
    __tablename__ = "collaborateurs"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    nom: Mapped[str] = mapped_column(String, nullable=False)
    prenom: Mapped[str] = mapped_column(String, nullable=False)
    ifo: Mapped[Optional[datetime.date]] = mapped_column(Date, nullable=True)
    caces: Mapped[Optional[datetime.date]] = mapped_column(Date, nullable=True)
    airr: Mapped[Optional[datetime.date]] = mapped_column(Date, nullable=True)
    hgo: Mapped[Optional[datetime.date]] = mapped_column(Date, nullable=True)
    bo: Mapped[Optional[datetime.date]] = mapped_column(Date, nullable=True)
    visite_med: Mapped[Optional[datetime.date]] = mapped_column(Date, nullable=True)
    brevet_secour: Mapped[Optional[datetime.date]] = mapped_column(Date, nullable=True)
    commentaire: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    def __init__(
        self,
        nom: str,
        prenom: str,
        ifo: Optional[datetime.date] = None,
        caces: Optional[datetime.date] = None,
        airr: Optional[datetime.date] = None,
        hgo: Optional[datetime.date] = None,
        bo: Optional[datetime.date] = None,
        visite_med: Optional[datetime.date] = None,
        brevet_secour: Optional[datetime.date] = None,
        commentaire: Optional[str] = None,
    ):
        self.nom = nom
        self.prenom = prenom
        self.ifo = ifo
        self.caces = caces
        self.airr = airr
        self.hgo = hgo
        self.bo = bo
        self.visite_med = visite_med
        self.brevet_secour = brevet_secour
        self.commentaire = commentaire

    def __repr__(self):
        return f"<Collaborateur(id={self.id}, nom={self.nom}, prenom={self.prenom})>"
