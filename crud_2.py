from sqlalchemy.orm import Session
from models_2 import CollaborateurPoidsLouud
from datetime import date
from typing import Optional, List
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_collaborateur_2(
    db: Session,
    nom: str,
    prenom: str,
    date_renouvellement: Optional[date] = None,
    date_validite: Optional[date] = None,
    commentaire: Optional[str] = None
) -> CollaborateurPoidsLouud:
    """Create a new collaborateur entry"""
    db_collaborateur = CollaborateurPoidsLouud(
        nom=nom,
        prenom=prenom,
        date_renouvellement=date_renouvellement,
        date_validite=date_validite,
        commentaire=commentaire
    )
    try:
        db.add(db_collaborateur)
        db.commit()
        db.refresh(db_collaborateur)
        logger.info(f"Created collaborateur {nom} {prenom}")
        return db_collaborateur
    except Exception as e:
        logger.error(f"Error creating collaborateur: {str(e)}")
        db.rollback()
        raise

def get_collaborateur_2(db: Session, collaborateur_id: int) -> Optional[CollaborateurPoidsLouud]:
    """Get a collaborateur by ID"""
    return db.query(CollaborateurPoidsLouud).filter(CollaborateurPoidsLouud.id == collaborateur_id).first()

def get_collaborateurs_2(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    search: Optional[str] = None,
    sort_by: Optional[str] = None,
    direction: str = 'asc'
) -> List[CollaborateurPoidsLouud]:
    """Get all collaborateurs with pagination, search, and sorting functionality"""
    query = db.query(CollaborateurPoidsLouud)
    if search:
        search_term = f"%{search}%"
        query = query.filter(
            (CollaborateurPoidsLouud.nom.ilike(search_term)) |
            (CollaborateurPoidsLouud.prenom.ilike(search_term)) |
            (CollaborateurPoidsLouud.commentaire.ilike(search_term))
        )
    if sort_by and hasattr(CollaborateurPoidsLouud, sort_by):
        column = getattr(CollaborateurPoidsLouud, sort_by)
        if direction == 'desc':
            column = column.desc()
        query = query.order_by(column)
    return query.offset(skip).limit(limit).all()

def update_collaborateur_2(
    db: Session,
    collaborateur_id: int,
    nom: Optional[str] = None,
    prenom: Optional[str] = None,
    date_renouvellement: Optional[date] = None,
    date_validite: Optional[date] = None,
    commentaire: Optional[str] = None
) -> Optional[CollaborateurPoidsLouud]:
    """Update a collaborateur's information"""
    collaborateur = db.query(CollaborateurPoidsLouud).filter(CollaborateurPoidsLouud.id == collaborateur_id).first()
    if collaborateur:
        if nom is not None:
            setattr(collaborateur, "nom", nom)
        if prenom is not None:
            setattr(collaborateur, "prenom", prenom)
        if date_renouvellement is not None:
            setattr(collaborateur, "date_renouvellement", date_renouvellement)
        if date_validite is not None:
            setattr(collaborateur, "date_validite", date_validite)
        if commentaire is not None:
            setattr(collaborateur, "commentaire", commentaire)
        try:
            db.commit()
            db.refresh(collaborateur)
            logger.info(f"Updated collaborateur with ID {collaborateur_id}")
            return collaborateur
        except Exception as e:
            logger.error(f"Error updating collaborateur: {str(e)}")
            db.rollback()
            raise
    return None

def delete_collaborateur_2(db: Session, collaborateur_id: int) -> bool:
    """Delete a collaborateur"""
    collaborateur = db.query(CollaborateurPoidsLouud).filter(CollaborateurPoidsLouud.id == collaborateur_id).first()
    if collaborateur:
        try:
            db.delete(collaborateur)
            db.commit()
            logger.info(f"Deleted collaborateur with ID {collaborateur_id}")
            return True
        except Exception as e:
            logger.error(f"Error deleting collaborateur: {str(e)}")
            db.rollback()
            raise
    return False

def get_collaborateurs_expiring_soon_2(db: Session, days: int = 30) -> List[CollaborateurPoidsLouud]:
    """Get collaborateurs whose date_validite expires within the next 'days' days"""
    from datetime import datetime, timedelta
    today = datetime.now().date()
    soon = today + timedelta(days=days)
    return db.query(CollaborateurPoidsLouud).filter(
        CollaborateurPoidsLouud.date_validite <= soon,
        CollaborateurPoidsLouud.date_validite >= today
    ).order_by(CollaborateurPoidsLouud.date_validite).all()
