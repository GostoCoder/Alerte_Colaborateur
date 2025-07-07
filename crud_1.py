# Import necessary libraries
from database_1 import SessionLocal, get_db
from models_1 import Collaborateur
from datetime import datetime, date
from typing import Optional, List
import logging
from sqlalchemy import String

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# --- Collaborateur CRUD operations ---

def create_collaborateur(
    db: SessionLocal,
    nom: str,
    prenom: str,
    ifo: Optional[date] = None,
    caces: Optional[date] = None,
    airr: Optional[date] = None,
    hgo: Optional[date] = None,
    bo: Optional[date] = None,
    commentaire: Optional[str] = None,
    visite_med: Optional[date] = None,
    brevet_secour: Optional[date] = None
) -> Collaborateur:
    """Create a new collaborateur entry"""
    db_collab = Collaborateur(
        nom=nom,
        prenom=prenom,
        ifo=ifo,
        caces=caces,
        airr=airr,
        hgo=hgo,
        bo=bo,
        commentaire=commentaire,
        visite_med=visite_med,
        brevet_secour=brevet_secour
    )
    try:
        db.add(db_collab)
        db.commit()
        db.refresh(db_collab)
        return db_collab
    except Exception as e:
        db.rollback()
        logger.error(f"Error creating collaborateur: {str(e)}")
        raise

def get_collaborateur(db: SessionLocal, collaborateur_id: int) -> Optional[Collaborateur]:
    """Get a collaborateur by ID"""
    return db.query(Collaborateur).filter(Collaborateur.id == collaborateur_id).first()

def get_collaborateurs(
    db: SessionLocal,
    skip: int = 0,
    limit: int = 100,
    search: Optional[str] = None,
    sort_by: Optional[str] = None,
    direction: str = 'asc'
) -> List[Collaborateur]:
    """Get all collaborateurs with pagination, search, and sorting functionality"""
    query = db.query(Collaborateur)
    if search:
        search_term = f"%{search}%"
        query = query.filter(
            (Collaborateur.nom.ilike(search_term)) |
            (Collaborateur.prenom.ilike(search_term))
        )
    if sort_by and hasattr(Collaborateur, sort_by):
        column = getattr(Collaborateur, sort_by)
        if direction == 'desc':
            column = column.desc()
        query = query.order_by(column)
    return query.offset(skip).limit(limit).all()

def update_collaborateur(
    db: SessionLocal,
    collaborateur_id: int,
    nom: Optional[str] = None,
    prenom: Optional[str] = None,
    ifo: Optional[date] = None,
    caces: Optional[date] = None,
    airr: Optional[date] = None,
    hgo: Optional[date] = None,
    bo: Optional[date] = None,
    commentaire: Optional[str] = None,
    visite_med: Optional[date] = None,
    brevet_secour: Optional[date] = None
) -> Optional[Collaborateur]:
    """Update a collaborateur's information"""
    db_collab = get_collaborateur(db, collaborateur_id)
    if not db_collab:
        return None
    if nom is not None:
        db_collab.nom = nom
    if prenom is not None:
        db_collab.prenom = prenom
    db_collab.ifo = ifo
    db_collab.caces = caces
    db_collab.airr = airr
    db_collab.hgo = hgo
    db_collab.bo = bo
    db_collab.visite_med = visite_med
    db_collab.brevet_secour = brevet_secour
    db_collab.commentaire = commentaire
    try:
        db.commit()
        db.refresh(db_collab)
        return db_collab
    except Exception as e:
        db.rollback()
        logger.error(f"Error updating collaborateur: {str(e)}")
        raise

def delete_collaborateur(db: SessionLocal, collaborateur_id: int) -> bool:
    """Delete a collaborateur"""
    db_collab = get_collaborateur(db, collaborateur_id)
    if not db_collab:
        return False
    try:
        db.delete(db_collab)
        db.commit()
        return True
    except Exception as e:
        db.rollback()
        logger.error(f"Error deleting collaborateur: {str(e)}")
        raise
