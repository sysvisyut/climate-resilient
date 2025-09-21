from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import List, Optional, Dict, Any
from datetime import datetime, date

from ..models.database import get_db
from ..models.models import Location, ClimateData, HealthData, HospitalData
from ..auth.auth import get_current_active_user, User
from ..utils.openweather_api import get_real_time_weather, update_climate_data_with_real_weather

router = APIRouter(
    prefix="/data",
    tags=["data"],
    responses={404: {"description": "Not found"}},
)

@router.get("/locations")
async def get_locations(
    location_type: Optional[str] = None,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get all locations or filter by type.
    """
    query = db.query(Location)
    
    if location_type:
        query = query.filter(Location.type == location_type)
    
    locations = query.all()
    
    if not locations:
        raise HTTPException(status_code=404, detail="No locations found")
    
    return locations


@router.get("/locations/{location_id}")
async def get_location(
    location_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get details for a specific location.
    """
    location = db.query(Location).filter(Location.id == location_id).first()
    
    if not location:
        raise HTTPException(status_code=404, detail="Location not found")
    
    return location


@router.get("/climate/{location_id}")
async def get_climate_data(
    location_id: int,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    is_projected: bool = False,
    projection_year: Optional[int] = None,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get climate data for a location.
    """
    # Check if location exists
    location = db.query(Location).filter(Location.id == location_id).first()
    if not location:
        raise HTTPException(status_code=404, detail="Location not found")
    
    # Build query
    query = db.query(ClimateData).filter(ClimateData.location_id == location_id)
    
    # Apply filters
    query = query.filter(ClimateData.is_projected == is_projected)
    
    if projection_year and is_projected:
        query = query.filter(ClimateData.projection_year == projection_year)
    
    if start_date:
        try:
            start = datetime.strptime(start_date, "%Y-%m-%d").date()
            query = query.filter(ClimateData.date >= start)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid start_date format. Use YYYY-MM-DD")
    
    if end_date:
        try:
            end = datetime.strptime(end_date, "%Y-%m-%d").date()
            query = query.filter(ClimateData.date <= end)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid end_date format. Use YYYY-MM-DD")
    
    # Execute query
    climate_data = query.order_by(ClimateData.date).all()
    
    if not climate_data:
        raise HTTPException(status_code=404, detail="No climate data found for the given criteria")
    
    return climate_data


@router.get("/health/{location_id}")
async def get_health_data(
    location_id: int,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    is_projected: bool = False,
    projection_year: Optional[int] = None,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get health data for a location.
    """
    # Check if location exists
    location = db.query(Location).filter(Location.id == location_id).first()
    if not location:
        raise HTTPException(status_code=404, detail="Location not found")
    
    # Build query
    query = db.query(HealthData).filter(HealthData.location_id == location_id)
    
    # Apply filters
    query = query.filter(HealthData.is_projected == is_projected)
    
    if projection_year and is_projected:
        query = query.filter(HealthData.projection_year == projection_year)
    
    if start_date:
        try:
            start = datetime.strptime(start_date, "%Y-%m-%d").date()
            query = query.filter(HealthData.date >= start)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid start_date format. Use YYYY-MM-DD")
    
    if end_date:
        try:
            end = datetime.strptime(end_date, "%Y-%m-%d").date()
            query = query.filter(HealthData.date <= end)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid end_date format. Use YYYY-MM-DD")
    
    # Execute query
    health_data = query.order_by(HealthData.date).all()
    
    if not health_data:
        raise HTTPException(status_code=404, detail="No health data found for the given criteria")
    
    return health_data


@router.get("/hospital/{location_id}")
async def get_hospital_data(
    location_id: int,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    is_projected: bool = False,
    projection_year: Optional[int] = None,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get hospital data for a location.
    """
    # Check if location exists
    location = db.query(Location).filter(Location.id == location_id).first()
    if not location:
        raise HTTPException(status_code=404, detail="Location not found")
    
    # Build query
    query = db.query(HospitalData).filter(HospitalData.location_id == location_id)
    
    # Apply filters
    query = query.filter(HospitalData.is_projected == is_projected)
    
    if projection_year and is_projected:
        query = query.filter(HospitalData.projection_year == projection_year)
    
    if start_date:
        try:
            start = datetime.strptime(start_date, "%Y-%m-%d").date()
            query = query.filter(HospitalData.date >= start)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid start_date format. Use YYYY-MM-DD")
    
    if end_date:
        try:
            end = datetime.strptime(end_date, "%Y-%m-%d").date()
            query = query.filter(HospitalData.date <= end)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid end_date format. Use YYYY-MM-DD")
    
    # Execute query
    hospital_data = query.order_by(HospitalData.date).all()
    
    if not hospital_data:
        raise HTTPException(status_code=404, detail="No hospital data found for the given criteria")
    
    return hospital_data


@router.get("/summary")
async def get_data_summary(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get a summary of the latest data for all locations including risk levels.
    """
    # Get risk classifier
    from ..models.ml_models import RiskClassifier
    from ..utils.climate_health_correlations import calculate_risk_level
    risk_classifier = RiskClassifier()
    risk_classifier.load_models()
    
    # Get latest date in the database
    latest_climate = db.query(ClimateData)\
        .filter(ClimateData.is_projected == False)\
        .order_by(ClimateData.date.desc())\
        .first()
    
    if not latest_climate:
        raise HTTPException(status_code=404, detail="No climate data available")
    
    latest_date = latest_climate.date
    
    # Get summary data for all locations on the latest date
    summary_data = []
    
    for location in db.query(Location).all():
        # Get climate data
        climate = db.query(ClimateData)\
            .filter(
                ClimateData.location_id == location.id,
                ClimateData.date == latest_date,
                ClimateData.is_projected == False
            )\
            .first()
        
        # Get health data
        health = db.query(HealthData)\
            .filter(
                HealthData.location_id == location.id,
                HealthData.date == latest_date,
                HealthData.is_projected == False
            )\
            .first()
        
        # Get hospital data
        hospital = db.query(HospitalData)\
            .filter(
                HospitalData.location_id == location.id,
                HospitalData.date == latest_date,
                HospitalData.is_projected == False
            )\
            .first()
        
        if climate and health and hospital:
            # Calculate disease rates per 100k
            population = location.population
            dengue_rate = health.dengue_cases * 100000 / population
            malaria_rate = health.malaria_cases * 100000 / population
            heatstroke_rate = health.heatstroke_cases * 100000 / population
            diarrhea_rate = health.diarrhea_cases * 100000 / population
            
            # Calculate overall disease burden (weighted average)
            overall_burden = (
                dengue_rate * 0.25 +
                malaria_rate * 0.25 +
                heatstroke_rate * 0.25 +
                diarrhea_rate * 0.25
            )
            
            # Calculate hospital bed occupancy rate
            bed_occupancy = 1 - (hospital.available_beds / hospital.total_beds) if hospital.total_beds > 0 else 0
            
            # Prepare climate data for risk prediction
            climate_dict = {
                "temperature": climate.temperature,
                "rainfall": climate.rainfall,
                "humidity": climate.humidity,
                "flood_probability": climate.flood_probability,
                "cyclone_probability": climate.cyclone_probability,
                "heatwave_probability": climate.heatwave_probability
            }
            
            # Get risk predictions
            risk_data = {}
            try:
                risk_predictions = risk_classifier.predict_risk(climate_dict, location.id, latest_date)
                risk_data = risk_predictions
            except Exception as e:
                print(f"Error predicting risks for {location.name}: {e}")
                # If prediction fails, calculate risk levels directly from rates
                risk_data = {
                    "dengue": {
                        "risk_level": calculate_risk_level(dengue_rate, "dengue"),
                        "probability": 0.8,
                        "rate_per_100k": float(dengue_rate)
                    },
                    "malaria": {
                        "risk_level": calculate_risk_level(malaria_rate, "malaria"),
                        "probability": 0.8,
                        "rate_per_100k": float(malaria_rate)
                    },
                    "heatstroke": {
                        "risk_level": calculate_risk_level(heatstroke_rate, "heatstroke"),
                        "probability": 0.8,
                        "rate_per_100k": float(heatstroke_rate)
                    },
                    "diarrhea": {
                        "risk_level": calculate_risk_level(diarrhea_rate, "diarrhea"),
                        "probability": 0.8,
                        "rate_per_100k": float(diarrhea_rate)
                    },
                    "overall": {
                        "risk_level": calculate_risk_level(overall_burden, "overall"),
                        "probability": 0.8
                    }
                }
            
            summary_data.append({
                "location_id": location.id,
                "name": location.name,
                "type": location.type,
                "temperature": climate.temperature,
                "rainfall": climate.rainfall,
                "humidity": climate.humidity,
                "flood_probability": climate.flood_probability,
                "cyclone_probability": climate.cyclone_probability,
                "heatwave_probability": climate.heatwave_probability,
                "dengue_cases": health.dengue_cases,
                "dengue_rate": round(dengue_rate, 2),
                "dengue_risk_level": risk_data.get("dengue", {}).get("risk_level", "unknown"),
                "malaria_cases": health.malaria_cases,
                "malaria_rate": round(malaria_rate, 2),
                "malaria_risk_level": risk_data.get("malaria", {}).get("risk_level", "unknown"),
                "heatstroke_cases": health.heatstroke_cases,
                "heatstroke_rate": round(heatstroke_rate, 2),
                "heatstroke_risk_level": risk_data.get("heatstroke", {}).get("risk_level", "unknown"),
                "diarrhea_cases": health.diarrhea_cases,
                "diarrhea_rate": round(diarrhea_rate, 2),
                "diarrhea_risk_level": risk_data.get("diarrhea", {}).get("risk_level", "unknown"),
                "overall_disease_burden": round(overall_burden, 2),
                "overall_risk_level": risk_data.get("overall", {}).get("risk_level", "unknown"),
                "risk_predictions": risk_data,
                "total_beds": hospital.total_beds,
                "available_beds": hospital.available_beds,
                "bed_occupancy_rate": round(bed_occupancy, 2),
                "doctors": hospital.doctors,
                "nurses": hospital.nurses
            })
    
    return {
        "date": latest_date.isoformat(),
        "locations": summary_data
    }


@router.get("/real-time-weather/{location_id}")
async def get_real_time_weather_data(
    location_id: int,
    update_db: bool = False,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Get real-time weather data for a location.
    
    Args:
        location_id: Location ID
        update_db: Whether to update the database with the real-time data
        
    Returns:
        Dictionary with real-time weather data
    """
    # Get location
    location = db.query(Location).filter(Location.id == location_id).first()
    if not location:
        raise HTTPException(status_code=404, detail="Location not found")
    
    # Get real-time weather data
    weather_data = get_real_time_weather(location.name)
    
    # Update database if requested
    if update_db:
        success = update_climate_data_with_real_weather(db, location_id, location.name)
        if not success:
            raise HTTPException(status_code=500, detail="Failed to update climate data")
    
    return {
        "location": {
            "id": location.id,
            "name": location.name,
            "type": location.type
        },
        "weather_data": weather_data,
        "updated_database": update_db
    }

@router.get("/alerts")
async def get_alerts(
    risk_threshold: float = 0.7,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get high-risk alerts for all locations.
    """
    # Get risk model
    from ..models.ml_models import RiskClassifier
    risk_classifier = RiskClassifier()
    risk_classifier.load_models()
    
    # Get latest date in the database
    latest_climate = db.query(ClimateData)\
        .filter(ClimateData.is_projected == False)\
        .order_by(ClimateData.date.desc())\
        .first()
    
    if not latest_climate:
        raise HTTPException(status_code=404, detail="No climate data available")
    
    latest_date = latest_climate.date
    
    # Check all locations for alerts
    alerts = []
    
    for location in db.query(Location).all():
        # Get climate data
        climate = db.query(ClimateData)\
            .filter(
                ClimateData.location_id == location.id,
                ClimateData.date == latest_date,
                ClimateData.is_projected == False
            )\
            .first()
        
        if not climate:
            continue
        
        # Prepare climate data for prediction
        climate_dict = {
            "temperature": climate.temperature,
            "rainfall": climate.rainfall,
            "humidity": climate.humidity,
            "flood_probability": climate.flood_probability,
            "cyclone_probability": climate.cyclone_probability,
            "heatwave_probability": climate.heatwave_probability
        }
        
        # Make risk prediction
        try:
            risk_prediction = risk_classifier.predict_risk(climate_dict, location.id, latest_date)
            
            # Check for high or critical risks
            for disease, risk_data in risk_prediction.items():
                risk_level = risk_data['risk_level']
                probability = risk_data['probability']
                
                if risk_level in ['high', 'critical'] and probability > risk_threshold:
                    alerts.append({
                        "location_id": location.id,
                        "location_name": location.name,
                        "date": latest_date.isoformat(),
                        "disease": disease,
                        "risk_level": risk_level,
                        "probability": probability,
                        "message": f"{risk_level.capitalize()} risk of {disease} in {location.name}"
                    })
        except Exception as e:
            # Log but don't fail if prediction errors occur for a location
            print(f"Error predicting risk for {location.name}: {e}")
            continue
    
    return {
        "date": latest_date.isoformat(),
        "alert_count": len(alerts),
        "alerts": alerts
    }
