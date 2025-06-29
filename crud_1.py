# Import necessary libraries
from database_1 import SessionLocal, get_db
from models_1 import Vehicle, Collaborateur
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
    hgo_bo: Optional[date] = None,
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
        hgo_bo=hgo_bo,
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
    hgo_bo: Optional[date] = None,
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
    db_collab.hgo_bo = hgo_bo
    db_collab.visite_med = visite_med
    db_collab.brevet_secour = brevet_secour
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

def create_vehicle(db: SessionLocal, 
                  vehicle_type: str,
                  brand: str,
                  commercial_type: str,
                  group_number: Optional[int],
                  license_plate: str,
                  limit_periodic_inspection: Optional[datetime],
                  kilometer_periodic_inspection: Optional[int],
                  limit_additional_inspection: Optional[datetime],
                  kilometer_additional_inspection: Optional[int],
                  date_periodic_inspection: Optional[datetime],
                  date_additional_inspection: Optional[datetime],
                  comments: Optional[str] = None) -> Vehicle:
    """Create a new vehicle entry"""
    db_vehicle = Vehicle(
        vehicle_type=vehicle_type,
        brand=brand,
        commercial_type=commercial_type,
        group_number=group_number,
        license_plate=license_plate,
        limit_periodic_inspection=limit_periodic_inspection,
        kilometer_periodic_inspection=kilometer_periodic_inspection,
        limit_additional_inspection=limit_additional_inspection,
        kilometer_additional_inspection=kilometer_additional_inspection,
        date_periodic_inspection=date_periodic_inspection,
        date_additional_inspection=date_additional_inspection,
        comments=comments
    )
    try:
        db.add(db_vehicle)
        db.commit()
        db.refresh(db_vehicle)
        return db_vehicle
    except Exception as e:
        db.rollback()
        logger.error(f"Error creating vehicle: {str(e)}")
        raise

def get_vehicle(db: SessionLocal, vehicle_id: int) -> Optional[Vehicle]:
    """Get a vehicle by ID"""
    return db.query(Vehicle).filter(Vehicle.id == vehicle_id).first()

def get_vehicle_by_license_plate(db: SessionLocal, license_plate: str) -> Optional[Vehicle]:
    """Get a vehicle by license plate"""
    return db.query(Vehicle).filter(Vehicle.license_plate == license_plate).first()

def get_vehicles(db: SessionLocal, skip: int = 0, limit: int = 100, search: str = None, sort_by: str = None, direction: str = 'asc') -> List[Vehicle]:
    """Get all vehicles with pagination, search, and sorting functionality"""
    query = db.query(Vehicle)
    
    if search:
        search_term = f"%{search}%"
        query = query.filter(
            (Vehicle.vehicle_type.ilike(search_term)) |
            (Vehicle.brand.ilike(search_term)) |
            (Vehicle.commercial_type.ilike(search_term)) |
            (Vehicle.group_number.cast(String).ilike(search_term)) |
            (Vehicle.license_plate.ilike(search_term)) |
            (Vehicle.comments.ilike(search_term))
        )
    
    # Apply sorting if column exists
    if sort_by and hasattr(Vehicle, sort_by):
        column = getattr(Vehicle, sort_by)
        if direction == 'desc':
            column = column.desc()
        query = query.order_by(column)
    
    return query.offset(skip).limit(limit).all()

def update_vehicle(db: SessionLocal, 
                  vehicle_id: int,
                  vehicle_type: Optional[str] = None,
                  brand: Optional[str] = None,
                  commercial_type: Optional[str] = None,
                  group_number: Optional[int] = None,
                  license_plate: Optional[str] = None,
                  limit_periodic_inspection: Optional[datetime] = None,
                  kilometer_periodic_inspection: Optional[int] = None,
                  limit_additional_inspection: Optional[datetime] = None,
                  kilometer_additional_inspection: Optional[int] = None,
                  date_periodic_inspection: Optional[datetime] = None,
                  date_additional_inspection: Optional[datetime] = None,
                  comments: Optional[str] = None) -> Optional[Vehicle]:
    """Update a vehicle's information"""
    db_vehicle = get_vehicle(db, vehicle_id)
    if not db_vehicle:
        return None
    
    # Update all fields that are provided in the parameters, including None values
    if vehicle_type is not None:
        db_vehicle.vehicle_type = vehicle_type
    if brand is not None:
        db_vehicle.brand = brand
    if commercial_type is not None:
        db_vehicle.commercial_type = commercial_type
    # group_number can be None
    db_vehicle.group_number = group_number
    if license_plate is not None:
        db_vehicle.license_plate = license_plate
    # All date and numeric fields can be None
    db_vehicle.limit_periodic_inspection = limit_periodic_inspection
    db_vehicle.kilometer_periodic_inspection = kilometer_periodic_inspection
    db_vehicle.limit_additional_inspection = limit_additional_inspection
    db_vehicle.kilometer_additional_inspection = kilometer_additional_inspection
    db_vehicle.date_periodic_inspection = date_periodic_inspection
    db_vehicle.date_additional_inspection = date_additional_inspection
    if comments is not None:
        db_vehicle.comments = comments
    
    try:
        db.commit()
        db.refresh(db_vehicle)
        return db_vehicle
    except Exception as e:
        db.rollback()
        logger.error(f"Error updating vehicle: {str(e)}")
        raise

def delete_vehicle(db: SessionLocal, vehicle_id: int) -> bool:
    """Delete a vehicle"""
    db_vehicle = get_vehicle(db, vehicle_id)
    if not db_vehicle:
        return False
    try:
        db.delete(db_vehicle)
        db.commit()
        return True
    except Exception as e:
        db.rollback()
        logger.error(f"Error deleting vehicle: {str(e)}")
        raise
