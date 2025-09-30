# Import necessary libraries
from sqlalchemy import Column, Integer, String, DateTime, Text, Date
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

# Create a new base class for declarative models
Base = declarative_base()

# Define a class to represent a vehicle in the second database
class Vehicle2(Base):
    __tablename__ = "vehicles_2"
    
    # Define the columns of the table
    id = Column(Integer, primary_key=True)
    vehicle_type = Column(String, nullable=False)
    brand = Column(String, nullable=False)
    commercial_type = Column(String, nullable=False)
    group_number = Column(Integer, nullable=True)
    license_plate = Column(String, nullable=False, unique=True)
    work_with = Column(String, nullable=True)
    kilometer_additional_inspection = Column(Integer, nullable=True)
    ct_soeco_date = Column(Date, nullable=True)
    euromaster_chrono = Column(Date, nullable=True)
    euromaster_limiteur = Column(Date, nullable=True)
    ned92_chrono = Column(Date, nullable=True)
    ned92_limiteur = Column(Date, nullable=True)
    date_technical_inspection = Column(Date, nullable=True)
    date_chrono = Column(Date, nullable=True)
    date_limiteur = Column(Date, nullable=True)
    comments = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f"<Vehicle(id={self.id}, brand={self.brand}, license_plate={self.license_plate})>"
