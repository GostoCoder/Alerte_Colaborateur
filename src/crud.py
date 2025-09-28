# Import necessary libraries
from sqlalchemy.orm import Session
from models import Collaborateur
from typing import Optional, List
import logging
from sqlalchemy import update

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# --- Collaborateur CRUD operations ---


def create_collaborateur(
    db: Session, collaborateur: Collaborateur
) -> Collaborateur:
    """Create a new collaborateur entry"""
    try:
        db.add(collaborateur)
        db.commit()
        db.refresh(collaborateur)
        return collaborateur
    except Exception as e:
        db.rollback()
        logger.error(f"Error creating collaborateur: {str(e)}")
        raise


def get_collaborateur(
    db: Session, collaborateur_id: int
) -> Optional[Collaborateur]:
    """Get a collaborateur by ID"""
    return db.query(Collaborateur).filter(Collaborateur.id == collaborateur_id).first()


def get_collaborateurs(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    search: Optional[str] = None,
    sort_by: Optional[str] = None,
    direction: str = "asc",
) -> List[Collaborateur]:
    """Get all collaborateurs with pagination, search, and sorting functionality"""
    query = db.query(Collaborateur)
    if search:
        search_term = f"%{search}%"
        query = query.filter(
            (Collaborateur.nom.ilike(search_term))
            | (Collaborateur.prenom.ilike(search_term))
        )
    if sort_by and hasattr(Collaborateur, sort_by):
        column = getattr(Collaborateur, sort_by)
        if direction == "desc":
            column = column.desc()
        query = query.order_by(column)
    return query.offset(skip).limit(limit).all()


def update_collaborateur(
    db: Session, collaborateur_id: int, updates: dict
) -> Optional[Collaborateur]:
    """Update a collaborateur's information from a dictionary of updates."""
    if not updates:
        return get_collaborateur(db, collaborateur_id)
    try:
        db.execute(
            update(Collaborateur)
            .where(Collaborateur.id == collaborateur_id)
            .values(**updates)
        )
        db.commit()
        return get_collaborateur(db, collaborateur_id)
    except Exception as e:
        db.rollback()
        logger.error(f"Error updating collaborateur: {str(e)}")
        raise


def delete_collaborateur(db: Session, collaborateur_id: int) -> bool:
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
