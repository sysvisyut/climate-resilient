from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Dict, Any, Optional
from datetime import datetime, date
import pandas as pd
import numpy as np
import logging
from sqlalchemy import text

from ..models.database import get_db
from ..models.models import Location, ClimateData, HealthData, HospitalData
from ..models.ml_models import RiskClassifier, DiseaseForecaster, ResourcePredictor
from ..auth.auth import get_current_active_user, get_current_admin_user
from ..models.models import User

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/predictions",
    tags=["predictions"],
    responses={404: {"description": "Not found"}},
)

# Initialize models
risk_classifier = RiskClassifier()
disease_forecaster = DiseaseForecaster()
resource_predictor = ResourcePredictor()

try:
    # Try to load the old models first for backward compatibility
    try:
        risk_classifier.load_models()
        disease_forecaster.load_models()
        resource_predictor.load_model()
        logger.info("Loaded old models successfully")
    except Exception as e:
        logger.warning(f"Could not load old models: {e}")
    
    # Try to load enhanced models
    import os
    import pickle
    import joblib
    
    model_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "models")
    
    # Load enhanced risk model
    enhanced_risk_model_path = os.path.join(model_dir, "enhanced_risk_model.pkl")
    if os.path.exists(enhanced_risk_model_path):
        with open(enhanced_risk_model_path, 'rb') as f:
            enhanced_risk_model = pickle.load(f)
            logger.info(f"Loaded enhanced risk model from {enhanced_risk_model_path}")
    
    # Load enhanced forecast model
    enhanced_forecast_model_path = os.path.join(model_dir, "enhanced_forecast_model.pkl")
    if os.path.exists(enhanced_forecast_model_path):
        with open(enhanced_forecast_model_path, 'rb') as f:
            enhanced_forecast_model = pickle.load(f)
            logger.info(f"Loaded enhanced forecast model from {enhanced_forecast_model_path}")
    
    # Load enhanced scaler
    enhanced_scaler_path = os.path.join(model_dir, "enhanced_scaler.joblib")
    if os.path.exists(enhanced_scaler_path):
        enhanced_scaler = joblib.load(enhanced_scaler_path)
        logger.info(f"Loaded enhanced scaler from {enhanced_scaler_path}")
except Exception as e:
    logger.warning(f"Could not load models: {e}")


@router.get("/risk/{location_id}")
async def predict_risk(
    location_id: int, 
    date_str: str = None,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Predict health risks for a location based on climate data.
    If date is not provided, uses the latest climate data.
    """
    # Check if location exists
    location = db.query(Location).filter(Location.id == location_id).first()
    if not location:
        raise HTTPException(status_code=404, detail="Location not found")
    
    # Determine date to use
    if date_str:
        try:
            query_date = datetime.strptime(date_str, "%Y-%m-%d").date()
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DD")
    else:
        # Use latest available data
        latest_climate = db.query(ClimateData)\
            .filter(ClimateData.location_id == location_id, ClimateData.is_projected == False)\
            .order_by(ClimateData.date.desc())\
            .first()
        
        if not latest_climate:
            raise HTTPException(status_code=404, detail="No climate data available for this location")
        
        query_date = latest_climate.date
    
    # Get climate data for the specified date
    climate_data = db.query(ClimateData)\
        .filter(
            ClimateData.location_id == location_id,
            ClimateData.date == query_date
        )\
        .first()
    
    if not climate_data:
        raise HTTPException(
            status_code=404, 
            detail=f"No climate data available for location {location_id} on {query_date}"
        )
    
    # Prepare climate data for prediction
    climate_dict = {
        "temperature": climate_data.temperature,
        "rainfall": climate_data.rainfall,
        "humidity": climate_data.humidity,
        "flood_probability": climate_data.flood_probability,
        "cyclone_probability": climate_data.cyclone_probability,
        "heatwave_probability": climate_data.heatwave_probability
    }
    
    # Make risk prediction using enhanced model if available
    try:
        # Try to use the enhanced model first
        if 'enhanced_risk_model' in globals():
            risk_prediction = enhanced_risk_model.predict_risk(climate_dict, location_id, location.type, query_date)
            logger.info("Used enhanced risk model for prediction")
        else:
            # Fall back to old model
            risk_prediction = risk_classifier.predict_risk(climate_dict, location_id, query_date)
            logger.info("Used old risk model for prediction")
    except Exception as e:
        logger.error(f"Error using enhanced model, falling back to old model: {e}")
        risk_prediction = risk_classifier.predict_risk(climate_dict, location_id, query_date)
    
    # Check if any risk is high or critical
    alerts = []
    for disease, risk_data in risk_prediction.items():
        if disease == "overall":
            continue
            
        risk_level = risk_data.get('risk_level', 'low')
        probability = risk_data.get('probability', 0)
        
        if risk_level in ['high', 'critical'] and probability > 0.7:
            alerts.append({
                "disease": disease,
                "risk_level": risk_level,
                "probability": probability,
                "message": f"{risk_level.capitalize()} risk of {disease} in {location.name}"
            })
    
    # Format response
    response = {
        "location": {
            "id": location.id,
            "name": location.name,
            "type": location.type
        },
        "date": query_date.isoformat(),
        "climate_data": climate_dict,
        "risk_prediction": risk_prediction,
        "alerts": alerts
    }
    
    return response


@router.get("/forecast/{location_id}")
async def forecast_diseases(
    location_id: int,
    days: int = 7,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Forecast disease cases for a location for the specified number of days.
    Uses LSTM model based on recent climate data trends.
    """
    # Check if location exists
    location = db.query(Location).filter(Location.id == location_id).first()
    if not location:
        raise HTTPException(status_code=404, detail="Location not found")
    
    # Get recent climate data
    recent_climate = db.query(ClimateData)\
        .filter(
            ClimateData.location_id == location_id,
            ClimateData.is_projected == False
        )\
        .order_by(ClimateData.date.desc())\
        .limit(14).all()  # Get last 14 days
    
    if len(recent_climate) < 7:
        raise HTTPException(status_code=404, detail="Not enough climate data for forecasting")
    
    # Convert to list of dictionaries for the forecaster
    recent_climate_list = [
        {
            "date": c.date,
            "temperature": c.temperature,
            "rainfall": c.rainfall,
            "humidity": c.humidity,
            "flood_probability": c.flood_probability,
            "cyclone_probability": c.cyclone_probability,
            "heatwave_probability": c.heatwave_probability
        }
        for c in recent_climate
    ]
    
    # Get latest climate data for current conditions
    latest_climate = recent_climate[0]
    climate_dict = {
        "temperature": latest_climate.temperature,
        "rainfall": latest_climate.rainfall,
        "humidity": latest_climate.humidity,
        "flood_probability": latest_climate.flood_probability,
        "cyclone_probability": latest_climate.cyclone_probability,
        "heatwave_probability": latest_climate.heatwave_probability
    }
    
    # Make forecast using enhanced model if available
    try:
        # Try to use the enhanced model first
        if 'enhanced_forecast_model' in globals():
            latest_date = max([c.date for c in recent_climate])
            forecast_result = enhanced_forecast_model.forecast(
                climate_dict, 
                location_id, 
                location.type, 
                latest_date, 
                days=days
            )
            logger.info("Used enhanced forecast model for prediction")
            daily_forecasts = forecast_result.get("forecasts", [])
            baseline = forecast_result.get("baseline", {})
        else:
            # Fall back to old model
            forecast = disease_forecaster.forecast_cases(location_id, recent_climate_list)
            if not forecast:
                raise HTTPException(status_code=500, detail="Error generating forecast")
                
            # Generate daily forecasts for specified number of days
            daily_forecasts = []
            latest_date = max([c.date for c in recent_climate])
            population = location.population
            
            for day in range(1, days + 1):
                forecast_date = latest_date + pd.Timedelta(days=day)
                
                # Calculate forecasted cases based on rates and population
                forecasted_cases = {
                    "date": forecast_date.isoformat(),
                    "dengue_cases": int(forecast['dengue']['forecasted_rate'] * population / 100000),
                    "malaria_cases": int(forecast['malaria']['forecasted_rate'] * population / 100000),
                    "heatstroke_cases": int(forecast['heatstroke']['forecasted_rate'] * population / 100000),
                    "diarrhea_cases": int(forecast['diarrhea']['forecasted_rate'] * population / 100000)
                }
                
                daily_forecasts.append(forecasted_cases)
                
            # Get latest health data for baseline
            latest_health = db.query(HealthData)\
                .filter(
                    HealthData.location_id == location_id,
                    HealthData.is_projected == False
                )\
                .order_by(HealthData.date.desc())\
                .first()
            
            if not latest_health:
                raise HTTPException(status_code=404, detail="No health data available for this location")
                
            baseline = {
                "dengue_cases": latest_health.dengue_cases,
                "malaria_cases": latest_health.malaria_cases,
                "heatstroke_cases": latest_health.heatstroke_cases,
                "diarrhea_cases": latest_health.diarrhea_cases
            }
            logger.info("Used old forecast model for prediction")
    except Exception as e:
        logger.error(f"Error using enhanced model, falling back to old model: {e}")
        # Fall back to old model
        forecast = disease_forecaster.forecast_cases(location_id, recent_climate_list)
        if not forecast:
            raise HTTPException(status_code=500, detail="Error generating forecast")
            
        # Get latest health data for baseline
        latest_health = db.query(HealthData)\
            .filter(
                HealthData.location_id == location_id,
                HealthData.is_projected == False
            )\
            .order_by(HealthData.date.desc())\
            .first()
        
        if not latest_health:
            raise HTTPException(status_code=404, detail="No health data available for this location")
        
        # Generate daily forecasts for specified number of days
        daily_forecasts = []
        latest_date = max([c.date for c in recent_climate])
        
        population = location.population
        
        for day in range(1, days + 1):
            forecast_date = latest_date + pd.Timedelta(days=day)
            
            # Calculate forecasted cases based on rates and population
            forecasted_cases = {
                "date": forecast_date.isoformat(),
                "dengue_cases": int(forecast['dengue']['forecasted_rate'] * population / 100000),
                "malaria_cases": int(forecast['malaria']['forecasted_rate'] * population / 100000),
                "heatstroke_cases": int(forecast['heatstroke']['forecasted_rate'] * population / 100000),
                "diarrhea_cases": int(forecast['diarrhea']['forecasted_rate'] * population / 100000)
            }
            
            daily_forecasts.append(forecasted_cases)
            
        baseline = {
            "dengue_cases": latest_health.dengue_cases,
            "malaria_cases": latest_health.malaria_cases,
            "heatstroke_cases": latest_health.heatstroke_cases,
            "diarrhea_cases": latest_health.diarrhea_cases
        }
    
    # Format response
    response = {
        "location": {
            "id": location.id,
            "name": location.name,
            "type": location.type
        },
        "baseline_date": latest_health.date.isoformat(),
        "baseline": {
            "dengue_cases": latest_health.dengue_cases,
            "malaria_cases": latest_health.malaria_cases,
            "heatstroke_cases": latest_health.heatstroke_cases,
            "diarrhea_cases": latest_health.diarrhea_cases
        },
        "forecasts": daily_forecasts
    }
    
    return response


@router.get("/resources/{location_id}")
async def predict_resources(
    location_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Predict hospital resource needs for a location based on current or forecasted health data.
    """
    # Check if location exists
    location = db.query(Location).filter(Location.id == location_id).first()
    if not location:
        raise HTTPException(status_code=404, detail="Location not found")
    
    # Get latest health data
    latest_health = db.query(HealthData)\
        .filter(
            HealthData.location_id == location_id,
            HealthData.is_projected == False
        )\
        .order_by(HealthData.date.desc())\
        .first()
    
    if not latest_health:
        raise HTTPException(status_code=404, detail="No health data available for this location")
    
    # Get current hospital data for comparison
    current_hospital = db.query(HospitalData)\
        .filter(
            HospitalData.location_id == location_id,
            HospitalData.date == latest_health.date
        )\
        .first()
    
    if not current_hospital:
        raise HTTPException(status_code=404, detail="No hospital data available for this location")
    
    # Prepare health data for prediction
    health_dict = {
        "dengue_cases": latest_health.dengue_cases,
        "malaria_cases": latest_health.malaria_cases,
        "heatstroke_cases": latest_health.heatstroke_cases,
        "diarrhea_cases": latest_health.diarrhea_cases
    }
    
    # Make resource prediction using enhanced model if available
    try:
        # Try to use the enhanced model first
        if 'enhanced_risk_model' in globals():
            # First get health predictions from the enhanced model
            # We need to get climate data for the current date
            climate_data = db.query(ClimateData)\
                .filter(
                    ClimateData.location_id == location_id,
                    ClimateData.date == latest_health.date
                )\
                .first()
                
            if not climate_data:
                # Use the most recent climate data
                climate_data = db.query(ClimateData)\
                    .filter(
                        ClimateData.location_id == location_id,
                        ClimateData.is_projected == False
                    )\
                    .order_by(ClimateData.date.desc())\
                    .first()
            
            climate_dict = {
                "temperature": climate_data.temperature,
                "rainfall": climate_data.rainfall,
                "humidity": climate_data.humidity,
                "flood_probability": climate_data.flood_probability,
                "cyclone_probability": climate_data.cyclone_probability,
                "heatwave_probability": climate_data.heatwave_probability
            }
            
            # Get health predictions
            health_predictions = enhanced_risk_model.predict_risk(climate_dict, location_id, location.type, latest_health.date)
            
            # Get resource predictions
            resource_prediction = enhanced_risk_model.predict_resources(health_predictions, location.population)
            logger.info("Used enhanced risk model for resource prediction")
        else:
            # Fall back to old model
            resource_prediction = resource_predictor.predict_resources(
                health_dict, location_id, location.population
            )
            logger.info("Used old resource model for prediction")
    except Exception as e:
        logger.error(f"Error using enhanced model, falling back to old model: {e}")
        # Fall back to old model
        resource_prediction = resource_predictor.predict_resources(
            health_dict, location_id, location.population
        )
    
    if not resource_prediction:
        raise HTTPException(status_code=500, detail="Error generating resource prediction")
    
    # Handle different formats of resource prediction
    if isinstance(resource_prediction, dict) and "resources" in resource_prediction:
        # Enhanced model format
        resource_data = resource_prediction["resources"]
    else:
        # Old model format
        resource_data = resource_prediction
    
    # Calculate resource gaps
    resource_gaps = {}
    for resource in resource_data:
        if resource in ["beds", "doctors", "nurses", "iv_fluids", "antibiotics", "antipyretics"]:
            current_value = getattr(current_hospital, {
                "beds": "total_beds",
                "doctors": "doctors",
                "nurses": "nurses",
                "iv_fluids": "iv_fluids_stock",
                "antibiotics": "antibiotics_stock",
                "antipyretics": "antipyretics_stock"
            }.get(resource, resource))
            
            resource_gaps[resource] = resource_data[resource] - current_value
    
    # Generate resource recommendations
    recommendations = []
    for resource, gap in resource_gaps.items():
        if gap > 0:
            recommendations.append({
                "resource": resource,
                "gap": gap,
                "message": f"Need {gap} more {resource} in {location.name}"
            })
    
    # Format response
    response = {
        "location": {
            "id": location.id,
            "name": location.name,
            "type": location.type
        },
        "date": latest_health.date.isoformat(),
        "current_resources": {
            "beds": current_hospital.total_beds,
            "doctors": current_hospital.doctors,
            "nurses": current_hospital.nurses,
            "iv_fluids": current_hospital.iv_fluids_stock,
            "antibiotics": current_hospital.antibiotics_stock,
            "antipyretics": current_hospital.antipyretics_stock
        },
        "predicted_resources": resource_data,
        "resource_gaps": resource_gaps,
        "recommendations": recommendations
    }
    
    # Add peak resources if available from enhanced model
    if isinstance(resource_prediction, dict) and "peak_resources" in resource_prediction:
        response["peak_resources"] = resource_prediction["peak_resources"]
        
    # Add overall risk level if available from enhanced model
    if isinstance(resource_prediction, dict) and "overall_risk_level" in resource_prediction:
        response["overall_risk_level"] = resource_prediction["overall_risk_level"]
    
    return response


@router.get("/climate-projections/{location_id}")
async def get_climate_projections(
    location_id: int,
    year: Optional[int] = None,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get climate projections for a location for future years.
    If year is specified, returns data for that year only.
    Otherwise returns data for all available projection years.
    """
    # Check if location exists
    location = db.query(Location).filter(Location.id == location_id).first()
    if not location:
        raise HTTPException(status_code=404, detail="Location not found")
    
    # Build query for climate projections
    query = db.query(ClimateData)\
        .filter(
            ClimateData.location_id == location_id,
            ClimateData.is_projected == True
        )
    
    # Filter by year if specified
    if year:
        query = query.filter(ClimateData.projection_year == year)
    
    # Execute query
    projections = query.all()
    
    if not projections:
        raise HTTPException(
            status_code=404, 
            detail=f"No climate projections available for location {location_id}"
            + (f" in year {year}" if year else "")
        )
    
    # Group projections by year
    projection_by_year = {}
    for p in projections:
        year = p.projection_year
        if year not in projection_by_year:
            projection_by_year[year] = []
        
        projection_by_year[year].append({
            "date": p.date.isoformat(),
            "temperature": p.temperature,
            "rainfall": p.rainfall,
            "humidity": p.humidity,
            "flood_probability": p.flood_probability,
            "cyclone_probability": p.cyclone_probability,
            "heatwave_probability": p.heatwave_probability
        })
    
    # Format response
    response = {
        "location": {
            "id": location.id,
            "name": location.name,
            "type": location.type
        },
        "projections": projection_by_year
    }
    
    return response


@router.get("/climate-health-correlation")
async def get_climate_health_correlation(
    current_user: User = Depends(get_current_admin_user),  # Admin only
    db: Session = Depends(get_db)
):
    """
    Get correlation analysis between climate factors and disease incidence.
    Admin only endpoint.
    """
    # Get climate and health data
    query = """
    SELECT 
        c.temperature, c.rainfall, c.humidity, 
        c.flood_probability, c.cyclone_probability, c.heatwave_probability,
        h.dengue_cases, h.malaria_cases, h.heatstroke_cases, h.diarrhea_cases,
        l.population, l.name as location_name
    FROM climate_data c
    JOIN health_data h ON c.location_id = h.location_id AND c.date = h.date
    JOIN locations l ON c.location_id = l.id
    WHERE c.is_projected = 0
    """
    
    # Execute raw SQL query with proper text() wrapper
    result = db.execute(text(query))
    rows = result.fetchall()
    
    if not rows:
        raise HTTPException(status_code=404, detail="No data available for correlation analysis")
    
    # Convert to DataFrame
    df = pd.DataFrame(rows)
    
    # Normalize disease cases by population
    df['dengue_rate'] = df['dengue_cases'] * 100000 / df['population']
    df['malaria_rate'] = df['malaria_cases'] * 100000 / df['population']
    df['heatstroke_rate'] = df['heatstroke_cases'] * 100000 / df['population']
    df['diarrhea_rate'] = df['diarrhea_cases'] * 100000 / df['population']
    
    # Calculate correlations with NaN handling
    climate_factors = ['temperature', 'rainfall', 'humidity', 'flood_probability', 'cyclone_probability', 'heatwave_probability']
    disease_rates = ['dengue_rate', 'malaria_rate', 'heatstroke_rate', 'diarrhea_rate']
    
    correlations = {}
    for disease in disease_rates:
        disease_name = disease.replace('_rate', '')
        correlations[disease_name] = {}
        
        for factor in climate_factors:
            try:
                # Handle NaN values by removing them before correlation
                valid_data = df[[factor, disease]].dropna()
                if len(valid_data) > 1:  # Need at least 2 points for correlation
                    corr = valid_data[factor].corr(valid_data[disease])
                    # Replace NaN with 0 if correlation calculation fails
                    correlations[disease_name][factor] = round(float(0 if pd.isna(corr) else corr), 3)
                else:
                    correlations[disease_name][factor] = 0.0
            except Exception as e:
                logger.error(f"Error calculating correlation for {disease} and {factor}: {e}")
                correlations[disease_name][factor] = 0.0
    
    # Format response with more detailed interpretations based on our climate-health model
    response = {
        "correlations": correlations,
        "interpretation": {
            "dengue": "Strong positive correlation with rainfall (breeding sites) and humidity (mosquito survival). Temperature shows moderate correlation with optimal range 25-32°C.",
            "malaria": "Moderate to strong correlation with humidity and rainfall. Temperature correlation peaks around 28°C, decreasing at higher temperatures.",
            "heatstroke": "Very strong positive correlation with temperature and heatwave probability. Negative correlation with rainfall due to cooling effect.",
            "diarrhea": "Moderate correlation with temperature. Strong correlation with flood probability due to water contamination. Seasonal patterns observed during monsoon."
        }
    }
    
    return response


@router.post("/train-models")
async def train_models(
    current_user: User = Depends(get_current_admin_user),  # Admin only
    db: Session = Depends(get_db)
):
    """
    Train or retrain all ML models.
    Admin only endpoint.
    """
    try:
        # Use the enhanced models creator instead of the old models
        import sys
        import os
        sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
        from save_enhanced_models import save_enhanced_models
        
        success = save_enhanced_models()
        
        if success:
            # Reload the models after training
            risk_classifier.load_models()
            disease_forecaster.load_models()
            resource_predictor.load_model()
            
            # Delete old model files that are no longer needed
            model_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "models")
            old_models = [
                "dengue_risk_model.pkl", "malaria_risk_model.pkl", 
                "heatstroke_risk_model.pkl", "diarrhea_risk_model.pkl",
                "overall_risk_model.pkl", "dengue_forecast_model.pkl",
                "malaria_forecast_model.pkl", "heatstroke_forecast_model.pkl",
                "diarrhea_forecast_model.pkl", "resource_predictor.pkl"
            ]
            
            for model in old_models:
                try:
                    model_path = os.path.join(model_dir, model)
                    if os.path.exists(model_path):
                        os.remove(model_path)
                        logger.info(f"Deleted old model: {model}")
                except Exception as e:
                    logger.warning(f"Failed to delete old model {model}: {e}")
            
            return {"message": "Enhanced models created successfully and old models deleted"}
        else:
            logger.error("Enhanced model creation failed")
            return {"message": "Enhanced model creation failed", "success": False}
    except Exception as e:
        logger.error(f"Error creating enhanced models: {e}")
        # Return a 200 response with error details instead of 500
        # This makes debugging easier and prevents frontend issues
        return {
            "message": f"Error creating enhanced models: {str(e)}",
            "success": False,
            "error": str(e)
        }
