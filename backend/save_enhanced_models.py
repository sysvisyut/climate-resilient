"""
Script to save enhanced prediction models to the models folder
"""

import os
import sys
import pickle
import joblib
import logging
import numpy as np
import pandas as pd
from datetime import datetime
from sklearn.preprocessing import StandardScaler

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Add the current directory to the path so we can import app modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Define models directory
MODELS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "models")

# Import app modules
from app.utils.health_conditions import HEALTH_CONDITIONS, NATURAL_DISASTERS
from app.utils.climate_health_correlations import (
    get_realistic_risk_prediction, 
    calculate_resource_needs,
    get_natural_disaster_prediction, 
    get_peak_time_prediction,
    get_all_health_condition_risks
)

class EnhancedRiskModel:
    """Enhanced risk prediction model using climate-health correlations"""
    
    def __init__(self):
        self.health_conditions = HEALTH_CONDITIONS
        self.natural_disasters = NATURAL_DISASTERS
        self.model_version = "1.0.0"
        self.creation_date = datetime.now().strftime("%Y-%m-%d")
    
    def predict_risk(self, climate_data, location_id, location_type, date):
        """
        Predict health risks based on climate data
        
        Args:
            climate_data: Dictionary with climate factors
            location_id: Location ID
            location_type: Location type ('state' or 'union_territory')
            date: Date for prediction
            
        Returns:
            Dictionary with risk predictions
        """
        # Convert date to datetime if it's a string
        if isinstance(date, str):
            date = datetime.strptime(date, "%Y-%m-%d").date()
        elif not isinstance(date, datetime) and not hasattr(date, 'month'):
            date = datetime.now().date()
        
        # Get month for seasonal factors
        month = date.month
        
        # Get health condition risks
        return get_all_health_condition_risks(climate_data, location_id, location_type, date)
    
    def predict_resources(self, health_predictions, population):
        """
        Predict resource needs based on health predictions
        
        Args:
            health_predictions: Dictionary with health predictions
            population: Population of the location
            
        Returns:
            Dictionary with resource predictions
        """
        return calculate_resource_needs(health_predictions, population)
    
    def predict_natural_disasters(self, climate_data, location_name, date):
        """
        Predict natural disaster probabilities
        
        Args:
            climate_data: Dictionary with climate factors
            location_name: Name of the location
            date: Date for prediction
            
        Returns:
            Dictionary with natural disaster predictions
        """
        return get_natural_disaster_prediction(climate_data, location_name, date)
    
    def predict_peak_times(self, current_month, condition):
        """
        Predict peak times for a health condition
        
        Args:
            current_month: Current month (1-12)
            condition: Health condition
            
        Returns:
            Dictionary with peak time predictions
        """
        if condition in self.health_conditions:
            peak_season = self.health_conditions[condition].get('peak_season', [])
            return get_peak_time_prediction(current_month, peak_season)
        return {"status": "unknown", "months_to_peak": 0}

class EnhancedForecastModel:
    """Enhanced disease forecasting model"""
    
    def __init__(self):
        self.health_conditions = HEALTH_CONDITIONS
        self.model_version = "1.0.0"
        self.creation_date = datetime.now().strftime("%Y-%m-%d")
    
    def forecast(self, climate_data, location_id, location_type, start_date, days=14):
        """
        Forecast disease cases for a number of days
        
        Args:
            climate_data: Dictionary with climate factors
            location_id: Location ID
            location_type: Location type ('state' or 'union_territory')
            start_date: Start date for forecast
            days: Number of days to forecast
            
        Returns:
            Dictionary with forecasted cases
        """
        # Convert start_date to datetime if it's a string
        if isinstance(start_date, str):
            start_date = datetime.strptime(start_date, "%Y-%m-%d").date()
        elif not isinstance(start_date, datetime) and not hasattr(start_date, 'month'):
            start_date = datetime.now().date()
        
        # Generate forecasts for each day
        forecasts = []
        for day in range(days):
            # Calculate date for this forecast
            forecast_date = start_date + pd.Timedelta(days=day)
            
            # Get month for seasonal factors
            month = forecast_date.month
            
            # Get health predictions for this day
            health_predictions = get_all_health_condition_risks(
                climate_data, 
                location_id, 
                location_type, 
                forecast_date
            )
            
            # Extract rates for each disease
            forecast_data = {
                "date": forecast_date.strftime("%Y-%m-%d"),
                "dengue_cases": health_predictions.get("dengue", {}).get("rate", 0),
                "malaria_cases": health_predictions.get("malaria", {}).get("rate", 0),
                "heatstroke_cases": health_predictions.get("heatstroke", {}).get("rate", 0),
                "diarrhea_cases": health_predictions.get("diarrhea", {}).get("rate", 0),
            }
            
            forecasts.append(forecast_data)
        
        return {
            "forecasts": forecasts,
            "baseline_date": start_date.strftime("%Y-%m-%d"),
            "baseline": {
                "dengue_cases": health_predictions.get("dengue", {}).get("rate", 0),
                "malaria_cases": health_predictions.get("malaria", {}).get("rate", 0),
                "heatstroke_cases": health_predictions.get("heatstroke", {}).get("rate", 0),
                "diarrhea_cases": health_predictions.get("diarrhea", {}).get("rate", 0),
            }
        }

def save_enhanced_models():
    """Save enhanced prediction models to the models folder"""
    logger.info("Saving enhanced prediction models...")
    
    # Create models directory if it doesn't exist
    os.makedirs(MODELS_DIR, exist_ok=True)
    
    # Create and save enhanced risk model
    risk_model = EnhancedRiskModel()
    risk_model_path = os.path.join(MODELS_DIR, "enhanced_risk_model.pkl")
    with open(risk_model_path, 'wb') as f:
        pickle.dump(risk_model, f)
    logger.info(f"Saved enhanced risk model to {risk_model_path}")
    
    # Create and save enhanced forecast model
    forecast_model = EnhancedForecastModel()
    forecast_model_path = os.path.join(MODELS_DIR, "enhanced_forecast_model.pkl")
    with open(forecast_model_path, 'wb') as f:
        pickle.dump(forecast_model, f)
    logger.info(f"Saved enhanced forecast model to {forecast_model_path}")
    
    # Save standard scaler for input normalization
    scaler = StandardScaler()
    # Fit with some dummy data to make it usable
    dummy_data = np.array([[25, 50, 70, 0.1, 0.1, 0.1], 
                          [30, 100, 80, 0.5, 0.3, 0.4]])
    scaler.fit(dummy_data)
    scaler_path = os.path.join(MODELS_DIR, "enhanced_scaler.joblib")
    joblib.dump(scaler, scaler_path)
    logger.info(f"Saved enhanced scaler to {scaler_path}")
    
    # Create a metadata file with model information
    metadata = {
        "models": [
            {
                "name": "enhanced_risk_model",
                "type": "risk_prediction",
                "version": risk_model.model_version,
                "created_at": risk_model.creation_date,
                "file": "enhanced_risk_model.pkl"
            },
            {
                "name": "enhanced_forecast_model",
                "type": "disease_forecasting",
                "version": forecast_model.model_version,
                "created_at": forecast_model.creation_date,
                "file": "enhanced_forecast_model.pkl"
            }
        ],
        "scalers": [
            {
                "name": "enhanced_scaler",
                "type": "standard_scaler",
                "file": "enhanced_scaler.joblib"
            }
        ],
        "health_conditions": list(HEALTH_CONDITIONS.keys()),
        "natural_disasters": list(NATURAL_DISASTERS.keys())
    }
    
    metadata_path = os.path.join(MODELS_DIR, "enhanced_models_metadata.json")
    with open(metadata_path, 'w') as f:
        import json
        json.dump(metadata, f, indent=2)
    logger.info(f"Saved metadata to {metadata_path}")
    
    logger.info("Enhanced prediction models saved successfully!")
    return True

if __name__ == "__main__":
    logger.info("Starting enhanced models saving process...")
    success = save_enhanced_models()
    logger.info("Process completed successfully!")
    sys.exit(0 if success else 1)
