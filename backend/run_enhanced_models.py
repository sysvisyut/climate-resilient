"""
Script to run the enhanced prediction models
"""

import os
import sys
import logging
import sqlite3
import requests
from datetime import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Add the current directory to the path so we can import app modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import app modules
from app.models.database import Base, engine
from app.models.models import Location, ClimateData
from app.utils.openweather_api import get_real_time_weather, update_climate_data_with_real_weather
from app.utils.health_conditions import predict_all_health_conditions, predict_hospital_resource_needs

def run_enhanced_models():
    """Run the enhanced prediction models for all locations"""
    logger.info("Starting enhanced prediction models run")
    
    # Create a session
    Session = sessionmaker(bind=engine)
    session = Session()
    
    try:
        # Get all locations
        locations = session.query(Location).all()
        logger.info(f"Found {len(locations)} locations")
        
        # Process each location
        for location in locations:
            logger.info(f"Processing location: {location.name} (ID: {location.id})")
            
            # Get real-time weather data
            try:
                weather_data = get_real_time_weather(location.name)
                logger.info(f"Got weather data for {location.name}: {weather_data['temperature']}°C, {weather_data['humidity']}%, {weather_data['rainfall']}mm")
                
                # Update climate data in the database
                success = update_climate_data_with_real_weather(session, location.id, location.name)
                if success:
                    logger.info(f"Updated climate data for {location.name}")
                else:
                    logger.warning(f"Failed to update climate data for {location.name}")
                
                # Extract climate factors for predictions
                climate_data = {
                    "temperature": weather_data["temperature"],
                    "humidity": weather_data["humidity"],
                    "rainfall": weather_data["rainfall"],
                    "flood_probability": weather_data["flood_probability"],
                    "cyclone_probability": weather_data["cyclone_probability"],
                    "heatwave_probability": weather_data["heatwave_probability"]
                }
                
                # Get current month for seasonal factors
                current_month = datetime.now().month
                
                # Run health predictions
                health_predictions = predict_all_health_conditions(climate_data, current_month, location.type)
                logger.info(f"Health predictions for {location.name}: {len(health_predictions)} conditions")
                
                # Run resource predictions
                resource_predictions = predict_hospital_resource_needs(health_predictions, location.population)
                logger.info(f"Resource predictions for {location.name}: {len(resource_predictions['resources'])} resources")
                
                # Print some sample predictions
                logger.info(f"Overall risk level for {location.name}: {health_predictions['overall']['risk_level']}")
                logger.info(f"Dengue risk for {location.name}: {health_predictions.get('dengue', {}).get('risk_level', 'unknown')}")
                logger.info(f"Predicted beds needed for {location.name}: {resource_predictions['resources'].get('beds', 0)}")
                
            except Exception as e:
                logger.error(f"Error processing location {location.name}: {e}")
        
        logger.info("Enhanced prediction models run completed successfully")
        return True
        
    except Exception as e:
        logger.error(f"Error running enhanced prediction models: {e}")
        return False
    finally:
        session.close()

def test_api_endpoints():
    """Test the enhanced prediction API endpoints"""
    logger.info("Testing enhanced prediction API endpoints")
    
    base_url = "http://localhost:8000"
    endpoints = [
        "/enhanced/health-risks/1",
        "/enhanced/resource-needs/1",
        "/enhanced/natural-disasters/1",
        "/enhanced/peak-times/1"
    ]
    
    for endpoint in endpoints:
        try:
            url = f"{base_url}{endpoint}"
            logger.info(f"Testing endpoint: {url}")
            
            response = requests.get(url)
            if response.status_code == 200:
                logger.info(f"Endpoint {endpoint} is working")
                # Print a sample of the response
                data = response.json()
                if "location" in data:
                    logger.info(f"Location: {data['location']['name']}")
                if "health_predictions" in data:
                    logger.info(f"Health predictions: {len(data['health_predictions'])} conditions")
                if "current_disasters" in data:
                    logger.info(f"Current disasters: {len(data['current_disasters'])} types")
            else:
                logger.error(f"Endpoint {endpoint} returned status code {response.status_code}")
                
        except Exception as e:
            logger.error(f"Error testing endpoint {endpoint}: {e}")
    
    logger.info("API endpoint testing completed")

if __name__ == "__main__":
    logger.info("Starting enhanced prediction models script")
    
    # Run the enhanced models
    success = run_enhanced_models()
    
    # Test the API endpoints if requested
    if len(sys.argv) > 1 and sys.argv[1] == "--test-api":
        test_api_endpoints()
    
    logger.info("Script completed")
    sys.exit(0 if success else 1)
