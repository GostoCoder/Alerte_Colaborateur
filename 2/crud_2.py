from sqlalchemy.orm import Session
from models_2 import Vehicle2 as Vehicle
from datetime import datetime
from typing import Optional, List
import logging
from sqlalchemy import String

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_vehicle_2(db: Session, 
                    vehicle_type: str,
                    brand: str,
                    commercial_type: str,
                    group_number: Optional[int],
                    license_plate: str,
                    work_with: Optional[str],
                    kilometer_additional_inspection: Optional[int],
                    ct_soeco_date: Optional[datetime],
                    euromaster_chrono: Optional[datetime],
                    euromaster_limiteur: Optional[datetime],
                    ned92_chrono: Optional[datetime],
                    ned92_limiteur: Optional[datetime],
                    date_technical_inspection: Optional[datetime],
                    date_chrono: Optional[datetime],
                    date_limiteur: Optional[datetime],
                    comments: Optional[str] = None) -> Vehicle:
    """Create a new vehicle entry"""
    db_vehicle = Vehicle(
        vehicle_type=vehicle_type,
        brand=brand,
        commercial_type=commercial_type,
        group_number=group_number,
        license_plate=license_plate,
        work_with=work_with,
        kilometer_additional_inspection=kilometer_additional_inspection,
        ct_soeco_date=ct_soeco_date,
        euromaster_chrono=euromaster_chrono,
        euromaster_limiteur=euromaster_limiteur,
        ned92_chrono=ned92_chrono,
        ned92_limiteur=ned92_limiteur,
        date_technical_inspection=date_technical_inspection,
        date_chrono=date_chrono,
        date_limiteur=date_limiteur,
        comments=comments
    )
    try:
        db.add(db_vehicle)
        db.commit()
        db.refresh(db_vehicle)
        logger.info(f"Created vehicle with license plate {license_plate}")
        return db_vehicle
    except Exception as e:
        logger.error(f"Error creating vehicle: {str(e)}")
        db.rollback()
        raise

def get_vehicle_2(db: Session, vehicle_id: int) -> Optional[Vehicle]:
    """Get a vehicle by ID"""
    return db.query(Vehicle).filter(Vehicle.id == vehicle_id).first()

def get_vehicle_by_license_plate_2(db: Session, license_plate: str) -> Optional[Vehicle]:
    """Get a vehicle by license plate"""
    return db.query(Vehicle).filter(Vehicle.license_plate == license_plate).first()

def get_vehicles_2(db: Session, skip: int = 0, limit: int = 100, search: str = None, sort_by: str = None, direction: str = 'asc') -> List[Vehicle]:
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
            (Vehicle.work_with.ilike(search_term)) |
            (Vehicle.kilometer_additional_inspection.cast(String).ilike(search_term)) |
            (Vehicle.comments.ilike(search_term))
        )
    
    # Apply sorting if column exists
    if sort_by and hasattr(Vehicle, sort_by):
        column = getattr(Vehicle, sort_by)
        if direction == 'desc':
            column = column.desc()
        query = query.order_by(column)
    
    return query.offset(skip).limit(limit).all()

def update_vehicle_2(db: Session, 
                    vehicle_id: int,
                    vehicle_type: Optional[str] = None,
                    brand: Optional[str] = None,
                    commercial_type: Optional[str] = None,
                    group_number: Optional[int] = None,
                    license_plate: Optional[str] = None,
                    work_with: Optional[str] = None,
                    kilometer_additional_inspection: Optional[int] = None,
                    ct_soeco_date: Optional[datetime] = None,
                    euromaster_chrono: Optional[datetime] = None,
                    euromaster_limiteur: Optional[datetime] = None,
                    ned92_chrono: Optional[datetime] = None,
                    ned92_limiteur: Optional[datetime] = None,
                    date_technical_inspection: Optional[datetime] = None,
                    date_chrono: Optional[datetime] = None,
                    date_limiteur: Optional[datetime] = None,
                    comments: Optional[str] = None) -> Optional[Vehicle]:
    """Update a vehicle's information"""
    vehicle = db.query(Vehicle).filter(Vehicle.id == vehicle_id).first()
    if vehicle:
        # Update required fields only if they are not None
        if vehicle_type is not None:
            vehicle.vehicle_type = vehicle_type
        if brand is not None:
            vehicle.brand = brand
        if commercial_type is not None:
            vehicle.commercial_type = commercial_type
        if license_plate is not None:
            vehicle.license_plate = license_plate
            
        # Update optional fields, allowing them to be set to None
        vehicle.group_number = group_number
        vehicle.work_with = work_with
        vehicle.kilometer_additional_inspection = kilometer_additional_inspection
        vehicle.ct_soeco_date = ct_soeco_date
        vehicle.euromaster_chrono = euromaster_chrono
        vehicle.euromaster_limiteur = euromaster_limiteur
        vehicle.ned92_chrono = ned92_chrono
        vehicle.ned92_limiteur = ned92_limiteur
        vehicle.date_technical_inspection = date_technical_inspection
        vehicle.date_chrono = date_chrono
        vehicle.date_limiteur = date_limiteur
        vehicle.comments = comments
        
        try:
            db.commit()
            db.refresh(vehicle)
            logger.info(f"Updated vehicle with ID {vehicle_id}")
            return vehicle
        except Exception as e:
            logger.error(f"Error updating vehicle: {str(e)}")
            db.rollback()
            raise
    return None

def delete_vehicle_2(db: Session, vehicle_id: int) -> bool:
    """Delete a vehicle"""
    vehicle = db.query(Vehicle).filter(Vehicle.id == vehicle_id).first()
    if vehicle:
        try:
            db.delete(vehicle)
            db.commit()
            logger.info(f"Deleted vehicle with ID {vehicle_id}")
            return True
        except Exception as e:
            logger.error(f"Error deleting vehicle: {str(e)}")
            db.rollback()
            raise
    return False

def get_vehicles_needing_inspection_2(db: Session) -> List[Vehicle]:
    """Get vehicles that need inspection soon"""
    today = datetime.now().date()
    return db.query(Vehicle).filter(
        Vehicle.date_technical_inspection <= today
    ).order_by(Vehicle.date_technical_inspection).all()
