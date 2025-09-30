from database_1 import SessionLocal
from models_1 import Collaborateur
from typing import Optional, List
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def create_collaborateur(db,
                         nom: str,
                         prenom: str,
                         fimo: Optional[str] = None,
                         caces: Optional[str] = None,
                         aipr: Optional[str] = None,
                         hg0b0: Optional[str] = None,
                         visite_med: Optional[str] = None,
                         brevet_secour: Optional[str] = None,
                         commentaire: Optional[str] = None) -> Collaborateur:
    """Create a new collaborateur entry"""
    collab = Collaborateur(
        nom=nom,
        prenom=prenom,
        fimo=fimo,
        caces=caces,
        aipr=aipr,
        hg0b0=hg0b0,
        visite_med=visite_med,
        brevet_secour=brevet_secour,
        commentaire=commentaire
    )
    try:
        db.add(collab)
        db.commit()
        db.refresh(collab)
        return collab
    except Exception as e:
        db.rollback()
        logger.error(f"Error creating collaborateur: {str(e)}")
        raise

def get_collaborateur(db, collaborateur_id: int) -> Optional[Collaborateur]:
    """Get a collaborateur by ID"""
    return db.query(Collaborateur).filter(Collaborateur.id == collaborateur_id).first()

def get_collaborateur_by_nom_prenom(db, nom: str, prenom: str) -> Optional[Collaborateur]:
    """Get a collaborateur by name and surname"""
    return db.query(Collaborateur).filter(Collaborateur.nom == nom, Collaborateur.prenom == prenom).first()

def get_collaborateurs(db, skip: int = 0, limit: int = 100, search: Optional[str] = None) -> List[Collaborateur]:
    """Get all collaborateurs with optional search and pagination"""
    query = db.query(Collaborateur)
    if search:
        search_term = f"%{search}%"
        query = query.filter(
            (Collaborateur.nom.ilike(search_term)) |
            (Collaborateur.prenom.ilike(search_term)) |
            (Collaborateur.commentaire.ilike(search_term))
        )
    return query.offset(skip).limit(limit).all()

def update_collaborateur(db,
                         collaborateur_id: int,
                         nom: Optional[str] = None,
                         prenom: Optional[str] = None,
                         fimo: Optional[str] = None,
                         caces: Optional[str] = None,
                         aipr: Optional[str] = None,
                         hg0b0: Optional[str] = None,
                         visite_med: Optional[str] = None,
                         brevet_secour: Optional[str] = None,
                         commentaire: Optional[str] = None) -> Optional[Collaborateur]:
    """Update a collaborateur's information"""
    collab = get_collaborateur(db, collaborateur_id)
    if not collab:
        return None
    if nom is not None:
        setattr(collab, "nom", nom)
    if prenom is not None:
        setattr(collab, "prenom", prenom)
    if fimo is not None:
        setattr(collab, "fimo", fimo)
    if caces is not None:
        setattr(collab, "caces", caces)
    if aipr is not None:
        setattr(collab, "aipr", aipr)
    if hg0b0 is not None:
        setattr(collab, "hg0b0", hg0b0)
    if visite_med is not None:
        setattr(collab, "visite_med", visite_med)
    if brevet_secour is not None:
        setattr(collab, "brevet_secour", brevet_secour)
    if commentaire is not None:
        setattr(collab, "commentaire", commentaire)
    try:
        db.commit()
        db.refresh(collab)
        return collab
    except Exception as e:
        db.rollback()
        logger.error(f"Error updating collaborateur: {str(e)}")
        raise

def delete_collaborateur(db, collaborateur_id: int) -> bool:
    """Delete a collaborateur"""
    collab = get_collaborateur(db, collaborateur_id)
    if not collab:
        return False
    try:
        db.delete(collab)
        db.commit()
        return True
    except Exception as e:
        db.rollback()
        logger.error(f"Error deleting collaborateur: {str(e)}")
        raise
