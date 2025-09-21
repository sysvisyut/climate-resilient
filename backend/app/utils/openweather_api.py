"""
OpenWeather API integration for real-time weather data
"""
import requests
import logging
import json
import os
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
import numpy as np

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# OpenWeather API key - in production, store this in environment variables or secure storage
OPENWEATHER_API_KEY = "efa07bbde5e87fdc177baac21387b040"  # Replace with your actual API key

# Base URL for OpenWeather API
OPENWEATHER_BASE_URL = "https://api.openweathermap.org/data/2.5"

# Indian states and their coordinates (approximate centers)
INDIAN_STATES = {
    "Andhra Pradesh": {"lat": 15.9129, "lon": 79.7400},
    "Arunachal Pradesh": {"lat": 28.2180, "lon": 94.7278},
    "Assam": {"lat": 26.2006, "lon": 92.9376},
    "Bihar": {"lat": 25.0961, "lon": 85.3131},
    "Chhattisgarh": {"lat": 21.2787, "lon": 81.8661},
    "Goa": {"lat": 15.2993, "lon": 74.1240},
    "Gujarat": {"lat": 22.2587, "lon": 71.1924},
    "Haryana": {"lat": 29.0588, "lon": 76.0856},
    "Himachal Pradesh": {"lat": 31.1048, "lon": 77.1734},
    "Jharkhand": {"lat": 23.6102, "lon": 85.2799},
    "Karnataka": {"lat": 15.3173, "lon": 75.7139},
    "Kerala": {"lat": 10.8505, "lon": 76.2711},
    "Madhya Pradesh": {"lat": 22.9734, "lon": 78.6569},
    "Maharashtra": {"lat": 19.7515, "lon": 75.7139},
    "Manipur": {"lat": 24.6637, "lon": 93.9063},
    "Meghalaya": {"lat": 25.4670, "lon": 91.3662},
    "Mizoram": {"lat": 23.1645, "lon": 92.9376},
    "Nagaland": {"lat": 26.1584, "lon": 94.5624},
    "Odisha": {"lat": 20.9517, "lon": 85.0985},
    "Punjab": {"lat": 31.1471, "lon": 75.3412},
    "Rajasthan": {"lat": 27.0238, "lon": 74.2179},
    "Sikkim": {"lat": 27.5330, "lon": 88.5122},
    "Tamil Nadu": {"lat": 11.1271, "lon": 78.6569},
    "Telangana": {"lat": 18.1124, "lon": 79.0193},
    "Tripura": {"lat": 23.9408, "lon": 91.9882},
    "Uttar Pradesh": {"lat": 26.8467, "lon": 80.9462},
    "Uttarakhand": {"lat": 30.0668, "lon": 79.0193},
    "West Bengal": {"lat": 22.9868, "lon": 87.8550},
    "Andaman and Nicobar Islands": {"lat": 11.7401, "lon": 92.6586},
    "Chandigarh": {"lat": 30.7333, "lon": 76.7794},
    "Dadra and Nagar Haveli and Daman and Diu": {"lat": 20.1809, "lon": 73.0169},
    "Delhi": {"lat": 28.7041, "lon": 77.1025},
    "Jammu and Kashmir": {"lat": 33.7782, "lon": 76.5762},
    "Ladakh": {"lat": 34.1526, "lon": 77.5770},
    "Lakshadweep": {"lat": 10.5667, "lon": 72.6417},
    "Puducherry": {"lat": 11.9416, "lon": 79.8083}
}

# Cache for weather data to avoid excessive API calls
WEATHER_CACHE = {}
CACHE_DURATION = 1800  # 30 minutes in seconds

def kelvin_to_celsius(kelvin):
    """Convert temperature from Kelvin to Celsius"""
    return kelvin - 273.15

def get_real_time_weather(location_name: str) -> Dict[str, Any]:
    """
    Get real-time weather data from OpenWeather API for a location
    
    Args:
        location_name: Name of the location (state/UT)
        
    Returns:
        Dictionary with weather data
    """
    # Check cache first
    cache_key = f"{location_name}_{datetime.now().strftime('%Y-%m-%d-%H')}"
    if cache_key in WEATHER_CACHE and (datetime.now() - WEATHER_CACHE[cache_key]['timestamp']).total_seconds() < CACHE_DURATION:
        return WEATHER_CACHE[cache_key]['data']
    
    try:
        # Get coordinates for the location
        if location_name not in INDIAN_STATES:
            # Default to Delhi if location not found
            coords = INDIAN_STATES["Delhi"]
            logger.warning(f"Location {location_name} not found, using Delhi coordinates")
        else:
            coords = INDIAN_STATES[location_name]
        
        # Make API call to OpenWeather
        params = {
            'lat': coords['lat'],
            'lon': coords['lon'],
            'appid': OPENWEATHER_API_KEY,
            'units': 'metric'  # Use metric units
        }
        
        # Current weather
        current_url = f"{OPENWEATHER_BASE_URL}/weather"
        current_response = requests.get(current_url, params=params)
        current_data = current_response.json()
        
        # 5-day forecast
        forecast_url = f"{OPENWEATHER_BASE_URL}/forecast"
        forecast_response = requests.get(forecast_url, params=params)
        forecast_data = forecast_response.json()
        
        # Process current weather data
        if current_response.status_code == 200:
            temperature = current_data['main']['temp']
            humidity = current_data['main']['humidity']
            
            # Get rainfall data if available (last 3 hours)
            rainfall = 0
            if 'rain' in current_data and '3h' in current_data['rain']:
                rainfall = current_data['rain']['3h']
            elif 'rain' in current_data and '1h' in current_data['rain']:
                rainfall = current_data['rain']['1h']
            
            # Calculate disaster probabilities based on weather conditions
            weather_id = current_data['weather'][0]['id']
            wind_speed = current_data['wind']['speed']
            
            # Calculate flood probability
            flood_probability = 0.01  # Base probability
            if rainfall > 20:  # Heavy rain
                flood_probability = min(0.95, rainfall / 100)
            elif weather_id >= 200 and weather_id < 300:  # Thunderstorm
                flood_probability = 0.3
            elif weather_id >= 300 and weather_id < 400:  # Drizzle
                flood_probability = 0.1
            elif weather_id >= 500 and weather_id < 600:  # Rain
                flood_probability = 0.2 + (rainfall / 100)
            
            # Calculate cyclone probability
            cyclone_probability = 0.01  # Base probability
            if wind_speed > 20:  # Strong wind
                cyclone_probability = min(0.95, wind_speed / 50)
            
            # Calculate heatwave probability
            heatwave_probability = 0.01  # Base probability
            if temperature > 35:  # Hot temperature
                heatwave_probability = min(0.95, (temperature - 30) / 15)
            
            # Process forecast data
            forecast = []
            if forecast_response.status_code == 200:
                # Group by day (every 8 items is a new day, as data is 3-hourly)
                for i in range(0, min(40, len(forecast_data['list'])), 8):
                    day_data = forecast_data['list'][i]
                    forecast_date = datetime.fromtimestamp(day_data['dt']).strftime("%Y-%m-%d")
                    
                    # Get rainfall data if available
                    day_rainfall = 0
                    if 'rain' in day_data and '3h' in day_data['rain']:
                        day_rainfall = day_data['rain']['3h']
                    
                    # Calculate disaster probabilities for forecast
                    day_weather_id = day_data['weather'][0]['id']
                    day_wind_speed = day_data['wind']['speed']
                    day_temp = day_data['main']['temp']
                    
                    day_flood_prob = 0.01
                    if day_rainfall > 20:
                        day_flood_prob = min(0.95, day_rainfall / 100)
                    elif day_weather_id >= 200 and day_weather_id < 300:
                        day_flood_prob = 0.3
                    elif day_weather_id >= 500 and day_weather_id < 600:
                        day_flood_prob = 0.2 + (day_rainfall / 100)
                    
                    day_cyclone_prob = 0.01
                    if day_wind_speed > 20:
                        day_cyclone_prob = min(0.95, day_wind_speed / 50)
                    
                    day_heatwave_prob = 0.01
                    if day_temp > 35:
                        day_heatwave_prob = min(0.95, (day_temp - 30) / 15)
                    
                    forecast.append({
                        "date": forecast_date,
                        "temperature": round(day_temp, 1),
                        "humidity": day_data['main']['humidity'],
                        "rainfall": round(day_rainfall, 1),
                        "flood_probability": round(day_flood_prob, 3),
                        "cyclone_probability": round(day_cyclone_prob, 3),
                        "heatwave_probability": round(day_heatwave_prob, 3),
                        "weather_description": day_data['weather'][0]['description']
                    })
            
            # Compile weather data
            weather_data = {
                "location": location_name,
                "latitude": coords["lat"],
                "longitude": coords["lon"],
                "timestamp": datetime.now(),
                "temperature": round(temperature, 1),
                "humidity": round(humidity, 1),
                "rainfall": round(rainfall, 1),
                "flood_probability": round(flood_probability, 3),
                "cyclone_probability": round(cyclone_probability, 3),
                "heatwave_probability": round(heatwave_probability, 3),
                "weather_description": current_data['weather'][0]['description'],
                "weather_icon": current_data['weather'][0]['icon'],
                "forecast": forecast
            }
            
            # Cache the result
            WEATHER_CACHE[cache_key] = {
                'data': weather_data,
                'timestamp': datetime.now()
            }
            
            return weather_data
        else:
            logger.error(f"Error fetching weather data: {current_response.status_code} - {current_data.get('message', 'Unknown error')}")
            # Fall back to synthetic data
            return generate_synthetic_weather(location_name)
    
    except Exception as e:
        logger.error(f"Error fetching weather data for {location_name}: {e}")
        # Fall back to synthetic data
        return generate_synthetic_weather(location_name)

def generate_synthetic_weather(location_name: str) -> Dict[str, Any]:
    """
    Generate synthetic weather data when API fails
    
    Args:
        location_name: Name of the location
        
    Returns:
        Dictionary with synthetic weather data
    """
    # Get coordinates for the location
    if location_name not in INDIAN_STATES:
        coords = INDIAN_STATES["Delhi"]
    else:
        coords = INDIAN_STATES[location_name]
    
    # Current date and month for seasonal patterns
    now = datetime.now()
    month = now.month
    
    # Generate realistic weather based on month and location
    # These are simplified approximations for demonstration
    
    # Temperature patterns by region and season
    base_temp = 25  # Base temperature in Celsius
    
    # Seasonal adjustments (India has mainly 3 seasons: summer, monsoon, winter)
    if 3 <= month <= 6:  # Summer (March to June)
        seasonal_temp_adj = 10
        seasonal_humidity_adj = -10
        seasonal_rainfall_adj = -5
    elif 7 <= month <= 10:  # Monsoon (July to October)
        seasonal_temp_adj = 0
        seasonal_humidity_adj = 30
        seasonal_rainfall_adj = 15
    else:  # Winter (November to February)
        seasonal_temp_adj = -8
        seasonal_humidity_adj = -20
        seasonal_rainfall_adj = -8
    
    # Regional adjustments based on latitude
    # Northern states are cooler in winter, hotter in summer
    latitude = coords["lat"]
    if latitude > 28:  # Northern states
        if month <= 2 or month >= 11:  # Winter
            regional_temp_adj = -10
        else:  # Summer
            regional_temp_adj = 5
    elif latitude < 15:  # Southern states
        if month <= 2 or month >= 11:  # Winter
            regional_temp_adj = -2
        else:  # Summer
            regional_temp_adj = 2
    else:  # Central states
        regional_temp_adj = 0
    
    # Calculate temperature with randomization
    import random
    temp_randomization = random.uniform(-3, 3)
    temperature = base_temp + seasonal_temp_adj + regional_temp_adj + temp_randomization
    
    # Calculate humidity
    base_humidity = 60  # Base humidity percentage
    humidity_randomization = random.uniform(-10, 10)
    humidity = min(100, max(10, base_humidity + seasonal_humidity_adj + humidity_randomization))
    
    # Calculate rainfall (mm per day)
    base_rainfall = 2  # Base rainfall in mm
    rainfall_randomization = random.uniform(0, 5)
    if 7 <= month <= 9:  # Peak monsoon
        rainfall_randomization += random.uniform(0, 20)  # Much higher variation during monsoon
    
    rainfall = max(0, base_rainfall + seasonal_rainfall_adj + rainfall_randomization)
    
    # Calculate disaster probabilities
    # Flood probability - higher during monsoon and in flood-prone states
    flood_prone_states = ["Bihar", "Assam", "West Bengal", "Uttar Pradesh", "Kerala"]
    flood_base = 0.05
    if location_name in flood_prone_states:
        flood_base = 0.15
    flood_seasonal = 0.3 if 7 <= month <= 9 else 0.05
    flood_probability = min(0.95, max(0.01, flood_base + flood_seasonal + random.uniform(-0.05, 0.05)))
    
    # Cyclone probability - higher in coastal states during specific seasons
    cyclone_prone_states = ["Odisha", "Andhra Pradesh", "Tamil Nadu", "West Bengal", "Gujarat"]
    cyclone_base = 0.02
    if location_name in cyclone_prone_states:
        cyclone_base = 0.1
    # Cyclone seasons: April-June and October-December
    cyclone_seasonal = 0.15 if (4 <= month <= 6) or (10 <= month <= 12) else 0.01
    cyclone_probability = min(0.9, max(0.01, cyclone_base + cyclone_seasonal + random.uniform(-0.03, 0.03)))
    
    # Heatwave probability - higher in summer and in hot states
    heatwave_prone_states = ["Rajasthan", "Delhi", "Haryana", "Uttar Pradesh", "Telangana"]
    heatwave_base = 0.05
    if location_name in heatwave_prone_states:
        heatwave_base = 0.2
    heatwave_seasonal = 0.4 if 4 <= month <= 6 else 0.02
    heatwave_probability = min(0.95, max(0.01, heatwave_base + heatwave_seasonal + random.uniform(-0.05, 0.05)))
    
    # Generate forecast data
    forecast = []
    for day in range(1, 6):
        forecast_date = (now + timedelta(days=day)).strftime("%Y-%m-%d")
        
        # Add some randomization but maintain trends
        temp_change = random.uniform(-3, 3)
        humidity_change = random.uniform(-10, 10)
        rainfall_change = random.uniform(-1, 2)
        
        # Ensure values stay within realistic ranges
        day_temp = max(0, min(50, temperature + temp_change))
        day_humidity = max(10, min(100, humidity + humidity_change))
        day_rainfall = max(0, rainfall + rainfall_change)
        
        # Calculate probabilities
        day_flood_prob = max(0.01, min(0.95, 0.05 + day_rainfall / 50))
        day_cyclone_prob = random.uniform(0.01, 0.1)
        day_heatwave_prob = max(0.01, min(0.95, 0.05 + (day_temp - 30) / 20)) if day_temp > 30 else 0.01
        
        forecast.append({
            "date": forecast_date,
            "temperature": round(day_temp, 1),
            "humidity": round(day_humidity, 1),
            "rainfall": round(day_rainfall, 1),
            "flood_probability": round(day_flood_prob, 3),
            "cyclone_probability": round(day_cyclone_prob, 3),
            "heatwave_probability": round(day_heatwave_prob, 3),
            "weather_description": "Generated forecast"
        })
    
    # Return synthetic weather data
    return {
        "location": location_name,
        "latitude": coords["lat"],
        "longitude": coords["lon"],
        "timestamp": datetime.now(),
        "temperature": round(temperature, 1),
        "humidity": round(humidity, 1),
        "rainfall": round(rainfall, 1),
        "flood_probability": round(flood_probability, 3),
        "cyclone_probability": round(cyclone_probability, 3),
        "heatwave_probability": round(heatwave_probability, 3),
        "weather_description": "Generated weather data",
        "weather_icon": "01d",  # Default icon
        "forecast": forecast
    }

def update_climate_data_with_real_weather(db_session, location_id: int, location_name: str) -> bool:
    """
    Update climate data in the database with real-time weather data
    
    Args:
        db_session: SQLAlchemy database session
        location_id: Location ID
        location_name: Location name
        
    Returns:
        True if successful, False otherwise
    """
    try:
        from sqlalchemy import update
        from ..models.models import ClimateData
        
        # Get real-time weather data
        weather_data = get_real_time_weather(location_name)
        
        # Get current date
        current_date = datetime.now().date()
        
        # Update or insert climate data for today
        stmt = update(ClimateData).where(
            ClimateData.location_id == location_id,
            ClimateData.date == current_date,
            ClimateData.is_projected == False
        ).values(
            temperature=weather_data["temperature"],
            humidity=weather_data["humidity"],
            rainfall=weather_data["rainfall"],
            flood_probability=weather_data["flood_probability"],
            cyclone_probability=weather_data["cyclone_probability"],
            heatwave_probability=weather_data["heatwave_probability"],
            last_updated=current_date
        )
        
        result = db_session.execute(stmt)
        
        # If no rows were updated, insert new record
        if result.rowcount == 0:
            from ..models.models import ClimateData
            
            new_climate = ClimateData(
                location_id=location_id,
                date=current_date,
                temperature=weather_data["temperature"],
                humidity=weather_data["humidity"],
                rainfall=weather_data["rainfall"],
                flood_probability=weather_data["flood_probability"],
                cyclone_probability=weather_data["cyclone_probability"],
                heatwave_probability=weather_data["heatwave_probability"],
                is_projected=False,
                last_updated=current_date
            )
            
            db_session.add(new_climate)
        
        db_session.commit()
        logger.info(f"Updated climate data for {location_name} with real-time weather data")
        return True
        
    except Exception as e:
        logger.error(f"Error updating climate data with real-time weather: {e}")
        db_session.rollback()
        return False
