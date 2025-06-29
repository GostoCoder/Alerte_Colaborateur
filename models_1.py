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
    hgo_bo = Column(Date, nullable=True)
    visite_med = Column(Date, nullable=True)
    brevet_secour = Column(Date, nullable=True)

    def __repr__(self):
        return (
            f"<Collaborateur(id={self.id}, nom={self.nom}, prenom={self.prenom})>"
        )

# Define a class to represent a vehicle
class Vehicle(Base):
    # Define the name of the table in the database
    __tablename__ = "vehicles_1"
    
    # Define the columns of the table
    id = Column(Integer, primary_key=True)
    vehicle_type = Column(String, nullable=False)
    brand = Column(String, nullable=False)
    commercial_type = Column(String, nullable=False)
    group_number = Column(Integer, nullable=True)
    license_plate = Column(String, nullable=False, unique=True)
    limit_periodic_inspection = Column(Date, nullable=True)
    kilometer_periodic_inspection = Column(Integer, nullable=True)
    limit_additional_inspection = Column(Date, nullable=True)
    kilometer_additional_inspection = Column(Integer, nullable=True)
    date_periodic_inspection = Column(Date, nullable=True)
    date_additional_inspection = Column(Date, nullable=True)
    comments = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    # Define a relationship with the RoadworthinessTest class
    tests = relationship("RoadworthinessTest", back_populates="vehicle")

    def __repr__(self):
        return f"<Vehicle(id={self.id}, brand={self.brand}, license_plate={self.license_plate})>"

# Define a class to represent a roadworthiness test
class RoadworthinessTest(Base):
    # Define the name of the table in the database
    __tablename__ = "roadworthiness_tests_1"
    # Define the columns of the table
    id = Column(Integer, primary_key=True)  # Unique identifier for the test
    vehicle_id = Column(Integer, ForeignKey("vehicles_1.id"))  # Foreign key referencing the Vehicle class
    # Define a relationship with the Vehicle class
    vehicle = relationship("Vehicle", back_populates="tests")
    test_date = Column(DateTime)  # Date of the test
    test_result = Column(String)  # Result of the test
    next_test_due = Column(DateTime)  # Date of the next test
