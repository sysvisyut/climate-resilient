"""
Fix setup script to regenerate data and ensure the database is properly initialized
"""
import os
import logging
import sqlite3
from app.utils.data_generator import generate_all_data
from app.utils.data_processor import main as process_and_load_data
from app.models.database import Base, engine
from app.auth.auth import get_password_hash
from app.models.models import User, Location
from sqlalchemy.orm import sessionmaker

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def reset_database():
    """Delete the database file if it exists"""
    db_path = 'climate_health.db'
    if os.path.exists(db_path):
        try:
            os.remove(db_path)
            logger.info(f"Deleted existing database: {db_path}")
        except Exception as e:
            logger.error(f"Error deleting database: {e}")
            return False
    return True

def create_database_schema():
    """Create database schema"""
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("Created database schema")
        return True
    except Exception as e:
        logger.error(f"Error creating database schema: {e}")
        return False

def generate_data():
    """Generate synthetic data"""
    try:
        # Ensure data directories exist
        os.makedirs('./data/raw', exist_ok=True)
        os.makedirs('./data/processed', exist_ok=True)
        
        # Generate synthetic data
        logger.info("Generating synthetic data...")
        generate_all_data(save_path="./data/raw")
        logger.info("Data generation complete")
        return True
    except Exception as e:
        logger.error(f"Error generating data: {e}")
        return False

def process_data():
    """Process and load data into the database"""
    try:
        logger.info("Processing and loading data...")
        process_and_load_data()
        logger.info("Data processing complete")
        return True
    except Exception as e:
        logger.error(f"Error processing data: {e}")
        return False

def create_users():
    """Create admin and hospital users"""
    try:
        # Create a session
        Session = sessionmaker(bind=engine)
        session = Session()
        
        # Create admin user
        admin_user = User(
            email="admin@climate-health.org",
            hashed_password=get_password_hash("admin123"),
            full_name="System Administrator",
            role="admin",
            is_active=True
        )
        session.add(admin_user)
        
        # Create hospital user for each location (state/UT)
        locations = session.query(Location.id, Location.name).all()
        
        for loc_id, loc_name in locations:
            hospital_user = User(
                email=f"hospital{loc_id}@climate-health.org",
                hashed_password=get_password_hash("hospital123"),
                full_name=f"{loc_name} Hospital Manager",
                role="hospital",
                hospital_name=f"{loc_name} Central Hospital",
                location_id=loc_id,
                is_active=True
            )
            session.add(hospital_user)
        
        session.commit()
        session.close()
        
        logger.info("Created users successfully")
        return True
    except Exception as e:
        logger.error(f"Error creating users: {e}")
        return False

def create_enhanced_models():
    """Create enhanced prediction models"""
    try:
        logger.info("Creating enhanced prediction models...")
        # Import here to avoid circular imports
        from save_enhanced_models import save_enhanced_models
        save_enhanced_models()
        logger.info("Enhanced model creation complete")
        return True
    except Exception as e:
        logger.error(f"Error creating enhanced models: {e}")
        return False

def main():
    """Main function to fix setup"""
    logger.info("Starting fix setup process...")
    
    # Reset database
    if not reset_database():
        logger.error("Failed to reset database. Aborting.")
        return False
    
    # Create database schema
    if not create_database_schema():
        logger.error("Failed to create database schema. Aborting.")
        return False
    
    # Generate data
    if not generate_data():
        logger.error("Failed to generate data. Aborting.")
        return False
    
    # Process data
    if not process_data():
        logger.error("Failed to process data. Aborting.")
        return False
    
    # Create users
    if not create_users():
        logger.error("Failed to create users. Aborting.")
        return False
    
    # Create enhanced models
    if not create_enhanced_models():
        logger.error("Failed to create enhanced models. Aborting.")
        return False
    
    logger.info("Fix setup process completed successfully!")
    return True

if __name__ == "__main__":
    main()
