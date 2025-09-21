from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, Float, Date
from sqlalchemy.orm import relationship

from .database import Base


class Location(Base):
    __tablename__ = "locations"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    type = Column(String)  # 'state' or 'union_territory'
    population = Column(Integer)
    area = Column(Float)
    
    climate_data = relationship("ClimateData", back_populates="location")
    health_data = relationship("HealthData", back_populates="location")
    hospital_data = relationship("HospitalData", back_populates="location")


class ClimateData(Base):
    __tablename__ = "climate_data"

    id = Column(Integer, primary_key=True, index=True)
    location_id = Column(Integer, ForeignKey("locations.id"))
    date = Column(Date, index=True)
    temperature = Column(Float)
    rainfall = Column(Float)
    humidity = Column(Float)
    flood_probability = Column(Float)
    cyclone_probability = Column(Float)
    heatwave_probability = Column(Float)
    is_projected = Column(Boolean, default=False)
    projection_year = Column(Integer, nullable=True)
    last_updated = Column(Date, nullable=True)
    
    location = relationship("Location", back_populates="climate_data")


class HealthData(Base):
    __tablename__ = "health_data"

    id = Column(Integer, primary_key=True, index=True)
    location_id = Column(Integer, ForeignKey("locations.id"))
    date = Column(Date, index=True)
    dengue_cases = Column(Integer)
    malaria_cases = Column(Integer)
    heatstroke_cases = Column(Integer)
    diarrhea_cases = Column(Integer)
    is_projected = Column(Boolean, default=False)
    projection_year = Column(Integer, nullable=True)
    
    location = relationship("Location", back_populates="health_data")


class HospitalData(Base):
    __tablename__ = "hospital_data"

    id = Column(Integer, primary_key=True, index=True)
    location_id = Column(Integer, ForeignKey("locations.id"))
    date = Column(Date, index=True)
    total_beds = Column(Integer)
    available_beds = Column(Integer)
    doctors = Column(Integer)
    nurses = Column(Integer)
    iv_fluids_stock = Column(Integer)
    antibiotics_stock = Column(Integer)
    antipyretics_stock = Column(Integer)
    is_projected = Column(Boolean, default=False)
    projection_year = Column(Integer, nullable=True)
    
    location = relationship("Location", back_populates="hospital_data")


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    full_name = Column(String)
    hospital_name = Column(String, nullable=True)
    location_id = Column(Integer, ForeignKey("locations.id"), nullable=True)
    is_active = Column(Boolean, default=True)
    role = Column(String)  # 'admin' or 'hospital'
