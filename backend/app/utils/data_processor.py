import pandas as pd
import numpy as np
import os
import sqlite3
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import sys
import logging

# Add backend directory to path to allow imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
from app.models.database import engine, SessionLocal
from app.models.models import Base, Location, ClimateData, HealthData, HospitalData

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def init_db():
    """Initialize database schema"""
    Base.metadata.create_all(bind=engine)
    logger.info("Database tables created")

def load_data_from_csv(data_dir="./data/raw"):
    """Load data from CSV files in the specified directory"""
    try:
        locations_df = pd.read_csv(os.path.join(data_dir, "locations.csv"))
        climate_df = pd.read_csv(os.path.join(data_dir, "climate_data.csv"))
        health_df = pd.read_csv(os.path.join(data_dir, "health_data.csv"))
        hospital_df = pd.read_csv(os.path.join(data_dir, "hospital_data.csv"))
        
        logger.info(f"Loaded data from {data_dir}")
        logger.info(f"Locations: {len(locations_df)}")
        logger.info(f"Climate data points: {len(climate_df)}")
        logger.info(f"Health data points: {len(health_df)}")
        logger.info(f"Hospital data points: {len(hospital_df)}")
        
        return {
            "locations": locations_df,
            "climate": climate_df,
            "health": health_df,
            "hospital": hospital_df
        }
    except Exception as e:
        logger.error(f"Error loading data from CSV: {e}")
        raise

def process_locations(locations_df, db):
    """Process and insert location data into the database"""
    try:
        # Convert dataframe to dict for SQLAlchemy
        locations_data = locations_df.to_dict('records')
        
        # Insert locations
        for loc_data in locations_data:
            location = Location(
                id=loc_data["id"],
                name=loc_data["name"],
                type=loc_data["type"],
                population=loc_data["population"],
                area=loc_data["area"]
            )
            db.add(location)
        
        db.commit()
        logger.info(f"Inserted {len(locations_data)} locations into database")
    except Exception as e:
        db.rollback()
        logger.error(f"Error processing locations: {e}")
        raise

def process_climate_data(climate_df, db):
    """Process and insert climate data into the database"""
    try:
        # Convert dataframe to dict for SQLAlchemy
        climate_data = climate_df.to_dict('records')
        
        # Insert climate data
        for data in climate_data:
            # Convert string date to Date object
            date = pd.to_datetime(data["date"]).date()
            
            climate = ClimateData(
                location_id=data["location_id"],
                date=date,
                temperature=data["temperature"],
                rainfall=data["rainfall"],
                humidity=data["humidity"],
                flood_probability=data["flood_probability"],
                cyclone_probability=data["cyclone_probability"],
                heatwave_probability=data["heatwave_probability"],
                is_projected=bool(data["is_projected"]),
                projection_year=data["projection_year"]
            )
            db.add(climate)
        
        db.commit()
        logger.info(f"Inserted {len(climate_data)} climate data points into database")
    except Exception as e:
        db.rollback()
        logger.error(f"Error processing climate data: {e}")
        raise

def process_health_data(health_df, db):
    """Process and insert health data into the database"""
    try:
        # Convert dataframe to dict for SQLAlchemy
        health_data = health_df.to_dict('records')
        
        # Insert health data
        for data in health_data:
            # Convert string date to Date object
            date = pd.to_datetime(data["date"]).date()
            
            health = HealthData(
                location_id=data["location_id"],
                date=date,
                dengue_cases=data["dengue_cases"],
                malaria_cases=data["malaria_cases"],
                heatstroke_cases=data["heatstroke_cases"],
                diarrhea_cases=data["diarrhea_cases"],
                is_projected=bool(data["is_projected"]),
                projection_year=data["projection_year"]
            )
            db.add(health)
        
        db.commit()
        logger.info(f"Inserted {len(health_data)} health data points into database")
    except Exception as e:
        db.rollback()
        logger.error(f"Error processing health data: {e}")
        raise

def process_hospital_data(hospital_df, db):
    """Process and insert hospital data into the database"""
    try:
        # Convert dataframe to dict for SQLAlchemy
        hospital_data = hospital_df.to_dict('records')
        
        # Insert hospital data
        for data in hospital_data:
            # Convert string date to Date object
            date = pd.to_datetime(data["date"]).date()
            
            hospital = HospitalData(
                location_id=data["location_id"],
                date=date,
                total_beds=data["total_beds"],
                available_beds=data["available_beds"],
                doctors=data["doctors"],
                nurses=data["nurses"],
                iv_fluids_stock=data["iv_fluids_stock"],
                antibiotics_stock=data["antibiotics_stock"],
                antipyretics_stock=data["antipyretics_stock"],
                is_projected=bool(data["is_projected"]),
                projection_year=data["projection_year"]
            )
            db.add(hospital)
        
        db.commit()
        logger.info(f"Inserted {len(hospital_data)} hospital data points into database")
    except Exception as e:
        db.rollback()
        logger.error(f"Error processing hospital data: {e}")
        raise

def calculate_derived_metrics():
    """Calculate additional metrics and store them in the processed folder"""
    try:
        # Use SQLAlchemy engine so it works for SQLite or Postgres
        # Get current health data
        current_health_df = pd.read_sql("""
            SELECT h.*, l.name as location_name, l.population
            FROM health_data h
            JOIN locations l ON h.location_id = l.id
            WHERE h.is_projected = 0 
            ORDER BY h.date DESC
        """, engine)
        
        # Calculate disease rates per 100,000 people
        current_health_df['dengue_rate'] = current_health_df['dengue_cases'] * 100000 / current_health_df['population']
        current_health_df['malaria_rate'] = current_health_df['malaria_cases'] * 100000 / current_health_df['population']
        current_health_df['heatstroke_rate'] = current_health_df['heatstroke_cases'] * 100000 / current_health_df['population']
        current_health_df['diarrhea_rate'] = current_health_df['diarrhea_cases'] * 100000 / current_health_df['population']
        
        # Calculate risk scores (0-100) for each disease
        current_health_df['dengue_risk'] = np.minimum(current_health_df['dengue_rate'] / 5, 100)
        current_health_df['malaria_risk'] = np.minimum(current_health_df['malaria_rate'] / 3, 100)
        current_health_df['heatstroke_risk'] = np.minimum(current_health_df['heatstroke_rate'] / 4, 100)
        current_health_df['diarrhea_risk'] = np.minimum(current_health_df['diarrhea_rate'] / 6, 100)
        
        # Calculate overall health risk
        current_health_df['overall_risk'] = (
            current_health_df['dengue_risk'] * 0.25 + 
            current_health_df['malaria_risk'] * 0.25 + 
            current_health_df['heatstroke_risk'] * 0.25 + 
            current_health_df['diarrhea_risk'] * 0.25
        )
        
        # Get current hospital resource data
        current_hospital_df = pd.read_sql("""
            SELECT h.*, l.name as location_name, l.population
            FROM hospital_data h
            JOIN locations l ON h.location_id = l.id
            WHERE h.is_projected = 0
            ORDER BY h.date DESC
        """, engine)
        
        # Calculate resource per 100,000 people
        current_hospital_df['beds_per_100k'] = current_hospital_df['total_beds'] * 100000 / current_hospital_df['population']
        current_hospital_df['available_beds_per_100k'] = current_hospital_df['available_beds'] * 100000 / current_hospital_df['population']
        current_hospital_df['doctors_per_100k'] = current_hospital_df['doctors'] * 100000 / current_hospital_df['population']
        current_hospital_df['nurses_per_100k'] = current_hospital_df['nurses'] * 100000 / current_hospital_df['population']
        
        # Calculate resource sufficiency scores (0-100, higher is better)
        current_hospital_df['beds_score'] = np.minimum(current_hospital_df['beds_per_100k'] / 3, 100)
        current_hospital_df['doctor_score'] = np.minimum(current_hospital_df['doctors_per_100k'] / 1, 100)
        current_hospital_df['nurse_score'] = np.minimum(current_hospital_df['nurses_per_100k'] / 3, 100)
        
        # Calculate overall resource score
        current_hospital_df['resource_score'] = (
            current_hospital_df['beds_score'] * 0.4 + 
            current_hospital_df['doctor_score'] * 0.3 + 
            current_hospital_df['nurse_score'] * 0.3
        )
        
        # Join health risks with resource data
        risk_resource_df = pd.merge(
            current_health_df[['location_id', 'date', 'overall_risk']],
            current_hospital_df[['location_id', 'date', 'resource_score']],
            on=['location_id', 'date'],
            how='inner'
        )
        
        # Calculate resilience score
        risk_resource_df['resilience_score'] = 100 - (risk_resource_df['overall_risk'] * (100 - risk_resource_df['resource_score']) / 100)
        
        # Save processed data
        os.makedirs("./data/processed", exist_ok=True)
        current_health_df.to_csv("./data/processed/current_health_risks.csv", index=False)
        current_hospital_df.to_csv("./data/processed/current_hospital_resources.csv", index=False)
        risk_resource_df.to_csv("./data/processed/resilience_scores.csv", index=False)
        
        # Save as JSON as well
        current_health_df.to_json("./data/processed/current_health_risks.json", orient="records")
        current_hospital_df.to_json("./data/processed/current_hospital_resources.json", orient="records")
        risk_resource_df.to_json("./data/processed/resilience_scores.json", orient="records")
        
        logger.info("Derived metrics calculated and saved")
        
    except Exception as e:
        logger.error(f"Error calculating derived metrics: {e}")
        raise
    finally:
        pass

def main():
    """Main ETL function"""
    # Initialize database
    init_db()
    
    # Create a database session
    db = SessionLocal()
    
    try:
        # Load data from CSV files
        data_dict = load_data_from_csv()
        
        # Process and insert data
        process_locations(data_dict["locations"], db)
        process_climate_data(data_dict["climate"], db)
        process_health_data(data_dict["health"], db)
        process_hospital_data(data_dict["hospital"], db)
        
        # Calculate derived metrics
        calculate_derived_metrics()
        
        logger.info("ETL process completed successfully")
    except Exception as e:
        logger.error(f"ETL process failed: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    main()
