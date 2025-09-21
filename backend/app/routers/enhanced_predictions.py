"""
Enhanced prediction endpoints for comprehensive health risk assessment
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Dict, Any, List, Optional
from datetime import datetime, date
import pandas as pd
import numpy as np
import logging

from ..models.database import get_db
from ..models.models import Location, ClimateData, HealthData, HospitalData, User
from ..auth.auth import get_current_active_user, get_current_admin_user
from ..utils.health_conditions import (
    predict_all_health_conditions,
    calculate_peak_times,
    predict_hospital_resource_needs
)
from ..utils.openweather_api import get_real_time_weather, update_climate_data_with_real_weather

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/enhanced",
    tags=["enhanced predictions"],
    responses={404: {"description": "Not found"}},
)

@router.get("/health-risks/{location_id}")
async def predict_enhanced_health_risks(
    location_id: int,
    use_real_time: bool = True,  # Default to True for real-time data
    date_str: Optional[str] = None,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Predict comprehensive health risks for a location based on climate data.
    
    Args:
        location_id: Location ID
        use_real_time: Whether to use real-time weather data
        date_str: Date string in YYYY-MM-DD format (ignored if use_real_time is True)
        
    Returns:
        Dictionary with comprehensive health risk predictions
    """
    # Get location
    location = db.query(Location).filter(Location.id == location_id).first()
    if not location:
        raise HTTPException(status_code=404, detail="Location not found")
    
    # Get climate data
    climate_data = {}
    
    if use_real_time:
        # Get real-time weather data
        weather_data = get_real_time_weather(location.name)
        
        # Extract climate factors
        climate_data = {
            "temperature": weather_data["temperature"],
            "humidity": weather_data["humidity"],
            "rainfall": weather_data["rainfall"],
            "flood_probability": weather_data["flood_probability"],
            "cyclone_probability": weather_data["cyclone_probability"],
            "heatwave_probability": weather_data["heatwave_probability"]
        }
        
        # Use current date
        current_date = datetime.now().date()
        
    else:
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
        climate_db = db.query(ClimateData)\
            .filter(
                ClimateData.location_id == location_id,
                ClimateData.date == query_date
            )\
            .first()
        
        if not climate_db:
            raise HTTPException(
                status_code=404, 
                detail=f"No climate data available for location {location_id} on {query_date}"
            )
        
        # Extract climate factors
        climate_data = {
            "temperature": climate_db.temperature,
            "humidity": climate_db.humidity,
            "rainfall": climate_db.rainfall,
            "flood_probability": climate_db.flood_probability,
            "cyclone_probability": climate_db.cyclone_probability,
            "heatwave_probability": climate_db.heatwave_probability
        }
        
        current_date = query_date
    
    # Get current month
    current_month = current_date.month
    
    # Predict health risks
    health_predictions = predict_all_health_conditions(climate_data, location.id, location.type, current_date)
    
    # Get peak times for high-risk conditions
    peak_times = {}
    for condition, prediction in health_predictions.items():
        if condition == "overall":
            continue
            
        if prediction["risk_level"] in ["high", "critical"]:
            peak_times[condition] = calculate_peak_times(condition, current_month)
    
    # Compile alerts
    alerts = []
    for condition, prediction in health_predictions.items():
        if condition == "overall":
            continue
            
        if prediction["risk_level"] in ["high", "critical"] and prediction["probability"] > 0.7:
            alerts.append({
                "condition": condition,
                "risk_level": prediction["risk_level"],
                "risk_score": prediction["risk_score"],
                "probability": prediction["probability"],
                "message": f"{prediction['risk_level'].capitalize()} risk of {condition.replace('_', ' ')} in {location.name}"
            })
    
    # Format response
    response = {
        "location": {
            "id": location.id,
            "name": location.name,
            "type": location.type,
            "population": location.population
        },
        "date": current_date.isoformat(),
        "climate_data": climate_data,
        "health_predictions": health_predictions,
        "peak_times": peak_times,
        "alerts": alerts,
        "data_source": "real-time weather API" if use_real_time else "historical database"
    }
    
    return response

@router.get("/resource-needs/{location_id}")
async def predict_enhanced_resource_needs(
    location_id: int,
    use_real_time: bool = True,  # Always use real-time data
    date_str: Optional[str] = None,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Predict comprehensive hospital resource needs for a location.
    
    Args:
        location_id: Location ID
        use_real_time: Whether to use real-time weather data
        date_str: Date string in YYYY-MM-DD format (ignored if use_real_time is True)
        
    Returns:
        Dictionary with comprehensive resource predictions
    """
    # First get health predictions
    health_response = await predict_enhanced_health_risks(
        location_id=location_id,
        use_real_time=use_real_time,
        date_str=date_str,
        current_user=current_user,
        db=db
    )
    
    # Get location
    location = db.query(Location).filter(Location.id == location_id).first()
    if not location:
        raise HTTPException(status_code=404, detail="Location not found")
    
    # Predict resource needs
    resource_predictions = predict_hospital_resource_needs(
        health_response["health_predictions"],
        location.population
    )
    
    # Get current hospital data for comparison
    current_hospital = db.query(HospitalData)\
        .filter(
            HospitalData.location_id == location_id,
            HospitalData.date == datetime.now().date()
        )\
        .first()
    
    if not current_hospital:
        # Try to get the most recent hospital data
        current_hospital = db.query(HospitalData)\
            .filter(HospitalData.location_id == location_id)\
            .order_by(HospitalData.date.desc())\
            .first()
    
    # Current resources
    current_resources = {}
    if current_hospital:
        current_resources = {
            "beds": current_hospital.total_beds,
            "available_beds": current_hospital.available_beds,
            "doctors": current_hospital.doctors,
            "nurses": current_hospital.nurses,
            "iv_fluids": current_hospital.iv_fluids_stock,
            "antibiotics": current_hospital.antibiotics_stock,
            "antipyretics": current_hospital.antipyretics_stock,
            # Default values for new resources
            "ventilators": int(current_hospital.total_beds * 0.05),  # Estimate 5% of beds have ventilators
            "ambulances": max(2, int(location.population / 100000)),  # Rough estimate
            "blood_units": int(current_hospital.total_beds * 0.5),  # Rough estimate
            "oxygen_cylinders": int(current_hospital.total_beds * 0.25)  # Rough estimate
        }
    
    # Calculate resource gaps
    resource_gaps = {}
    recommendations = []
    
    for resource, predicted in resource_predictions["resources"].items():
        current = current_resources.get(resource, 0)
        gap = predicted - current
        resource_gaps[resource] = gap
        
        if gap > 0:
            recommendations.append({
                "resource": resource,
                "gap": gap,
                "message": f"Need {gap} more {resource.replace('_', ' ')} in {location.name}"
            })
    
    # Format response
    response = {
        "location": {
            "id": location.id,
            "name": location.name,
            "type": location.type,
            "population": location.population
        },
        "date": datetime.now().date().isoformat(),
        "current_resources": current_resources,
        "predicted_resources": resource_predictions["resources"],
        "peak_resources": resource_predictions["peak_resources"],
        "resource_gaps": resource_gaps,
        "recommendations": recommendations,
        "overall_risk_level": resource_predictions["overall_risk_level"],
        "health_predictions": health_response["health_predictions"]
    }
    
    return response

@router.get("/natural-disasters/{location_id}")
async def predict_natural_disasters(
    location_id: int,
    use_real_time: bool = True,  # Always use real-time data
    days_ahead: int = 7,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Predict natural disaster risks for a location.
    
    Args:
        location_id: Location ID
        use_real_time: Whether to use real-time weather data
        days_ahead: Number of days to predict ahead
        
    Returns:
        Dictionary with natural disaster predictions
    """
    # Get location
    location = db.query(Location).filter(Location.id == location_id).first()
    if not location:
        raise HTTPException(status_code=404, detail="Location not found")
    
    # Get weather data with forecast
    weather_data = get_real_time_weather(location.name)
    
    # Extract disaster probabilities
    current_disasters = {
        "flood": {
            "probability": weather_data["flood_probability"],
            "risk_level": get_risk_level(weather_data["flood_probability"])
        },
        "cyclone": {
            "probability": weather_data["cyclone_probability"],
            "risk_level": get_risk_level(weather_data["cyclone_probability"])
        },
        "heatwave": {
            "probability": weather_data["heatwave_probability"],
            "risk_level": get_risk_level(weather_data["heatwave_probability"])
        },
        "landslide": {
            # Landslide risk is related to rainfall and flood probability
            "probability": min(0.95, max(0.01, (weather_data["rainfall"] / 50) * 0.5 + weather_data["flood_probability"] * 0.5)),
            "risk_level": get_risk_level(min(0.95, max(0.01, (weather_data["rainfall"] / 50) * 0.5 + weather_data["flood_probability"] * 0.5)))
        },
        "drought": {
            # Drought risk is inversely related to rainfall and directly related to temperature
            "probability": min(0.95, max(0.01, (1 - weather_data["rainfall"] / 50) * 0.7 + (weather_data["temperature"] / 45) * 0.3)),
            "risk_level": get_risk_level(min(0.95, max(0.01, (1 - weather_data["rainfall"] / 50) * 0.7 + (weather_data["temperature"] / 45) * 0.3)))
        }
    }
    
    # Process forecast data
    forecast_disasters = []
    
    for day in weather_data.get("forecast", []):
        day_disasters = {
            "date": day["date"],
            "disasters": {
                "flood": {
                    "probability": day["flood_probability"],
                    "risk_level": get_risk_level(day["flood_probability"])
                },
                "cyclone": {
                    "probability": day["cyclone_probability"],
                    "risk_level": get_risk_level(day["cyclone_probability"])
                },
                "heatwave": {
                    "probability": day["heatwave_probability"],
                    "risk_level": get_risk_level(day["heatwave_probability"])
                },
                "landslide": {
                    "probability": min(0.95, max(0.01, (day["rainfall"] / 50) * 0.5 + day["flood_probability"] * 0.5)),
                    "risk_level": get_risk_level(min(0.95, max(0.01, (day["rainfall"] / 50) * 0.5 + day["flood_probability"] * 0.5)))
                },
                "drought": {
                    "probability": min(0.95, max(0.01, (1 - day["rainfall"] / 50) * 0.7 + (day["temperature"] / 45) * 0.3)),
                    "risk_level": get_risk_level(min(0.95, max(0.01, (1 - day["rainfall"] / 50) * 0.7 + (day["temperature"] / 45) * 0.3)))
                }
            }
        }
        forecast_disasters.append(day_disasters)
    
    # Generate alerts
    alerts = []
    for disaster, data in current_disasters.items():
        if data["risk_level"] in ["high", "critical"]:
            alerts.append({
                "disaster": disaster,
                "risk_level": data["risk_level"],
                "probability": data["probability"],
                "message": f"{data['risk_level'].capitalize()} risk of {disaster} in {location.name}"
            })
    
    # Format response
    response = {
        "location": {
            "id": location.id,
            "name": location.name,
            "type": location.type
        },
        "current_date": datetime.now().date().isoformat(),
        "current_disasters": current_disasters,
        "forecast_disasters": forecast_disasters,
        "alerts": alerts
    }
    
    return response

@router.get("/peak-times/{location_id}")
async def predict_peak_times(
    location_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Predict peak times for health conditions and hospital resource needs.
    
    Args:
        location_id: Location ID
        
    Returns:
        Dictionary with peak time predictions
    """
    # Get health predictions first
    health_response = await predict_enhanced_health_risks(
        location_id=location_id,
        use_real_time=True,
        current_user=current_user,
        db=db
    )
    
    # Get location
    location = db.query(Location).filter(Location.id == location_id).first()
    if not location:
        raise HTTPException(status_code=404, detail="Location not found")
    
    # Current month
    current_month = datetime.now().month
    
    # Get peak times for all conditions
    peak_times = {}
    for condition in health_response["health_predictions"]:
        if condition == "overall":
            continue
            
        peak_times[condition] = calculate_peak_times(condition, current_month)
    
    # Predict resource needs
    resource_predictions = predict_hospital_resource_needs(
        health_response["health_predictions"],
        location.population
    )
    
    # Format response
    response = {
        "location": {
            "id": location.id,
            "name": location.name,
            "type": location.type
        },
        "current_date": datetime.now().date().isoformat(),
        "current_month": current_month,
        "peak_times": peak_times,
        "peak_resources": resource_predictions["peak_resources"],
        "health_predictions": health_response["health_predictions"]
    }
    
    return response

def get_risk_level(probability: float) -> str:
    """Helper function to convert probability to risk level"""
    if probability >= 0.75:
        return "critical"
    elif probability >= 0.5:
        return "high"
    elif probability >= 0.25:
        return "medium"
    else:
        return "low"
