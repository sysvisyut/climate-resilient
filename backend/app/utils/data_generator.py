import pandas as pd
import numpy as np
from faker import Faker
from datetime import datetime, timedelta
import json
import os
import random
from typing import Dict, List, Tuple

# Initialize faker
fake = Faker('en_IN')

# Current date for reference
CURRENT_DATE = datetime(2025, 9, 21)

# Indian states and union territories data
INDIAN_LOCATIONS = [
    # States
    {"name": "Andhra Pradesh", "type": "state", "population": 49577103, "area": 162975},
    {"name": "Arunachal Pradesh", "type": "state", "population": 1383727, "area": 83743},
    {"name": "Assam", "type": "state", "population": 31205576, "area": 78438},
    {"name": "Bihar", "type": "state", "population": 104099452, "area": 94163},
    {"name": "Chhattisgarh", "type": "state", "population": 25545198, "area": 135192},
    {"name": "Goa", "type": "state", "population": 1458545, "area": 3702},
    {"name": "Gujarat", "type": "state", "population": 60439692, "area": 196024},
    {"name": "Haryana", "type": "state", "population": 25351462, "area": 44212},
    {"name": "Himachal Pradesh", "type": "state", "population": 6864602, "area": 55673},
    {"name": "Jharkhand", "type": "state", "population": 32988134, "area": 79714},
    {"name": "Karnataka", "type": "state", "population": 61095297, "area": 191791},
    {"name": "Kerala", "type": "state", "population": 33406061, "area": 38863},
    {"name": "Madhya Pradesh", "type": "state", "population": 72626809, "area": 308252},
    {"name": "Maharashtra", "type": "state", "population": 112374333, "area": 307713},
    {"name": "Manipur", "type": "state", "population": 2855794, "area": 22327},
    {"name": "Meghalaya", "type": "state", "population": 2966889, "area": 22429},
    {"name": "Mizoram", "type": "state", "population": 1097206, "area": 21081},
    {"name": "Nagaland", "type": "state", "population": 1978502, "area": 16579},
    {"name": "Odisha", "type": "state", "population": 41974219, "area": 155707},
    {"name": "Punjab", "type": "state", "population": 27743338, "area": 50362},
    {"name": "Rajasthan", "type": "state", "population": 68548437, "area": 342239},
    {"name": "Sikkim", "type": "state", "population": 610577, "area": 7096},
    {"name": "Tamil Nadu", "type": "state", "population": 72147030, "area": 130058},
    {"name": "Telangana", "type": "state", "population": 35003674, "area": 112077},
    {"name": "Tripura", "type": "state", "population": 3673917, "area": 10486},
    {"name": "Uttar Pradesh", "type": "state", "population": 199812341, "area": 240928},
    {"name": "Uttarakhand", "type": "state", "population": 10086292, "area": 53483},
    {"name": "West Bengal", "type": "state", "population": 91276115, "area": 88752},
    
    # Union Territories
    {"name": "Andaman and Nicobar Islands", "type": "union_territory", "population": 380581, "area": 8249},
    {"name": "Chandigarh", "type": "union_territory", "population": 1055450, "area": 114},
    {"name": "Dadra and Nagar Haveli and Daman and Diu", "type": "union_territory", "population": 585764, "area": 603},
    {"name": "Delhi", "type": "union_territory", "population": 16787941, "area": 1483},
    {"name": "Jammu and Kashmir", "type": "union_territory", "population": 12267032, "area": 42241},
    {"name": "Ladakh", "type": "union_territory", "population": 274000, "area": 59146},
    {"name": "Lakshadweep", "type": "union_territory", "population": 64473, "area": 32},
    {"name": "Puducherry", "type": "union_territory", "population": 1247953, "area": 479}
]

# Seasonal patterns for different regions
SEASONAL_PATTERNS = {
    "North": {
        "summer": {"temp_range": (30, 45), "rainfall_range": (0, 50), "humidity_range": (30, 60)},
        "monsoon": {"temp_range": (25, 35), "rainfall_range": (100, 500), "humidity_range": (70, 90)},
        "winter": {"temp_range": (5, 25), "rainfall_range": (0, 30), "humidity_range": (40, 70)},
        "post_monsoon": {"temp_range": (20, 35), "rainfall_range": (20, 100), "humidity_range": (50, 80)}
    },
    "South": {
        "summer": {"temp_range": (25, 40), "rainfall_range": (10, 100), "humidity_range": (60, 80)},
        "monsoon": {"temp_range": (22, 32), "rainfall_range": (150, 500), "humidity_range": (75, 90)},
        "winter": {"temp_range": (15, 30), "rainfall_range": (20, 150), "humidity_range": (50, 75)},
        "post_monsoon": {"temp_range": (20, 35), "rainfall_range": (50, 200), "humidity_range": (65, 85)}
    },
    "East": {
        "summer": {"temp_range": (28, 40), "rainfall_range": (30, 150), "humidity_range": (50, 75)},
        "monsoon": {"temp_range": (25, 33), "rainfall_range": (200, 500), "humidity_range": (75, 95)},
        "winter": {"temp_range": (10, 28), "rainfall_range": (5, 50), "humidity_range": (45, 70)},
        "post_monsoon": {"temp_range": (18, 30), "rainfall_range": (50, 150), "humidity_range": (60, 85)}
    },
    "West": {
        "summer": {"temp_range": (30, 45), "rainfall_range": (0, 30), "humidity_range": (20, 50)},
        "monsoon": {"temp_range": (25, 35), "rainfall_range": (100, 400), "humidity_range": (70, 90)},
        "winter": {"temp_range": (10, 30), "rainfall_range": (0, 20), "humidity_range": (30, 60)},
        "post_monsoon": {"temp_range": (20, 35), "rainfall_range": (10, 50), "humidity_range": (40, 70)}
    },
    "Northeast": {
        "summer": {"temp_range": (20, 35), "rainfall_range": (100, 250), "humidity_range": (60, 85)},
        "monsoon": {"temp_range": (22, 30), "rainfall_range": (200, 500), "humidity_range": (80, 95)},
        "winter": {"temp_range": (8, 25), "rainfall_range": (10, 100), "humidity_range": (50, 75)},
        "post_monsoon": {"temp_range": (15, 28), "rainfall_range": (50, 200), "humidity_range": (65, 85)}
    },
    "Central": {
        "summer": {"temp_range": (30, 45), "rainfall_range": (0, 30), "humidity_range": (20, 50)},
        "monsoon": {"temp_range": (25, 35), "rainfall_range": (100, 350), "humidity_range": (65, 85)},
        "winter": {"temp_range": (10, 30), "rainfall_range": (0, 20), "humidity_range": (30, 60)},
        "post_monsoon": {"temp_range": (20, 35), "rainfall_range": (20, 80), "humidity_range": (45, 70)}
    }
}

# Map locations to regions
LOCATION_REGIONS = {
    "Jammu and Kashmir": "North", "Himachal Pradesh": "North", "Punjab": "North", 
    "Uttarakhand": "North", "Haryana": "North", "Delhi": "North", "Ladakh": "North",
    
    "Rajasthan": "West", "Gujarat": "West", "Maharashtra": "West", 
    "Goa": "West", "Dadra and Nagar Haveli and Daman and Diu": "West",
    
    "Uttar Pradesh": "Central", "Madhya Pradesh": "Central", "Chhattisgarh": "Central",
    
    "Bihar": "East", "Jharkhand": "East", "West Bengal": "East", "Odisha": "East",
    
    "Arunachal Pradesh": "Northeast", "Assam": "Northeast", "Manipur": "Northeast",
    "Meghalaya": "Northeast", "Mizoram": "Northeast", "Nagaland": "Northeast",
    "Sikkim": "Northeast", "Tripura": "Northeast",
    
    "Andhra Pradesh": "South", "Karnataka": "South", "Kerala": "South", 
    "Tamil Nadu": "South", "Telangana": "South", "Puducherry": "South",
    "Andaman and Nicobar Islands": "South", "Lakshadweep": "South"
}

# Default region for any missed locations
DEFAULT_REGION = "Central"

# Disease thresholds for correlation with climate
DISEASE_THRESHOLDS = {
    "dengue": {
        "temp": 25,  # Degrees C
        "rainfall": 100,  # mm
        "humidity": 70  # %
    },
    "malaria": {
        "temp": 20,  # Degrees C
        "rainfall": 80,  # mm
        "humidity": 60  # %
    },
    "heatstroke": {
        "temp": 40,  # Degrees C
        "humidity": 50  # %
    },
    "diarrhea": {
        "temp": 30,  # Degrees C
        "rainfall": 150,  # mm (floods can cause contamination)
        "flood_probability": 0.3
    }
}

def get_season(date):
    """Determine season based on date"""
    month = date.month
    if 3 <= month <= 5:
        return "summer"
    elif 6 <= month <= 9:
        return "monsoon"
    elif 10 <= month <= 11:
        return "post_monsoon"
    else:  # 12, 1, 2
        return "winter"

def get_region_for_location(location_name):
    """Get the region for a location"""
    return LOCATION_REGIONS.get(location_name, DEFAULT_REGION)

def generate_climate_data(location, date, is_projected=False, projection_year=None):
    """Generate synthetic climate data for a location on a specific date"""
    region = get_region_for_location(location["name"])
    season = get_season(date)
    region_season_data = SEASONAL_PATTERNS[region][season]
    
    # Base climate data
    temp_min, temp_max = region_season_data["temp_range"]
    rainfall_min, rainfall_max = region_season_data["rainfall_range"]
    humidity_min, humidity_max = region_season_data["humidity_range"]
    
    # Add climate change effects for projected data
    if is_projected and projection_year:
        years_in_future = projection_year - 2025
        temp_increase = years_in_future * 0.5  # 0.5°C increase per year
        rainfall_increase_factor = 1 + (years_in_future * 0.03)  # 3% increase per year
        
        temp_min += temp_increase
        temp_max += temp_increase
        rainfall_min *= rainfall_increase_factor
        rainfall_max *= rainfall_increase_factor
    
    # Generate values
    temperature = round(np.random.uniform(temp_min, temp_max), 1)
    rainfall = round(np.random.uniform(rainfall_min, rainfall_max), 1)
    humidity = round(np.random.uniform(humidity_min, humidity_max), 1)
    
    # Generate disaster probabilities
    flood_probability = min(1.0, max(0.0, (rainfall / 500) * 0.8 + np.random.uniform(-0.1, 0.1)))
    
    # Coastal regions have higher cyclone probabilities
    coastal_states = ["Andhra Pradesh", "Odisha", "West Bengal", "Tamil Nadu", "Kerala", 
                      "Gujarat", "Maharashtra", "Goa", "Andaman and Nicobar Islands", "Puducherry"]
    base_cyclone_prob = 0.4 if location["name"] in coastal_states else 0.05
    
    # Cyclones more likely during monsoon and post-monsoon
    season_factor = 1.5 if season in ["monsoon", "post_monsoon"] else 0.5
    cyclone_probability = min(1.0, max(0.0, base_cyclone_prob * season_factor + np.random.uniform(-0.1, 0.1)))
    
    # Heatwaves more likely in summer
    season_factor = 2.0 if season == "summer" else 0.2
    temp_factor = max(0, (temperature - 35) / 10)  # Higher chance if temperature > 35°C
    heatwave_probability = min(1.0, max(0.0, season_factor * temp_factor + np.random.uniform(-0.1, 0.1)))
    
    # Adjust probabilities for projected climate data
    if is_projected and projection_year:
        years_in_future = projection_year - 2025
        flood_probability = min(1.0, flood_probability + (years_in_future * 0.05))
        cyclone_probability = min(1.0, cyclone_probability + (years_in_future * 0.03))
        heatwave_probability = min(1.0, heatwave_probability + (years_in_future * 0.08))
    
    return {
        "location_id": location["id"],
        "date": date.strftime("%Y-%m-%d"),
        "temperature": temperature,
        "rainfall": rainfall,
        "humidity": humidity,
        "flood_probability": round(flood_probability, 3),
        "cyclone_probability": round(cyclone_probability, 3),
        "heatwave_probability": round(heatwave_probability, 3),
        "is_projected": is_projected,
        "projection_year": projection_year if is_projected else None
    }

def generate_health_data(climate_data, location, population_factor=1.0):
    """Generate health data based on climate conditions"""
    temperature = climate_data["temperature"]
    rainfall = climate_data["rainfall"]
    humidity = climate_data["humidity"]
    flood_prob = climate_data["flood_probability"]
    is_projected = climate_data["is_projected"]
    projection_year = climate_data["projection_year"]
    
    # Population-based scaling factor (per 100,000 people)
    population = location["population"]
    pop_scale = population / 100000 * population_factor
    
    # Dengue cases - influenced by temperature, rainfall and humidity
    dengue_thresh = DISEASE_THRESHOLDS["dengue"]
    dengue_temp_factor = max(0, (temperature - dengue_thresh["temp"]) / 15)
    dengue_rain_factor = min(1.0, rainfall / dengue_thresh["rainfall"])
    dengue_humidity_factor = min(1.0, humidity / dengue_thresh["humidity"])
    dengue_risk = dengue_temp_factor * dengue_rain_factor * dengue_humidity_factor
    dengue_cases = int(np.random.poisson(dengue_risk * 50 * pop_scale))
    
    # Malaria cases - similar to dengue but with different thresholds
    malaria_thresh = DISEASE_THRESHOLDS["malaria"]
    malaria_temp_factor = max(0, (temperature - malaria_thresh["temp"]) / 20)
    malaria_rain_factor = min(1.0, rainfall / malaria_thresh["rainfall"])
    malaria_humidity_factor = min(1.0, humidity / malaria_thresh["humidity"])
    malaria_risk = malaria_temp_factor * malaria_rain_factor * malaria_humidity_factor
    malaria_cases = int(np.random.poisson(malaria_risk * 30 * pop_scale))
    
    # Heatstroke cases - mainly influenced by temperature and humidity
    heatstroke_thresh = DISEASE_THRESHOLDS["heatstroke"]
    heatstroke_temp_factor = max(0, (temperature - heatstroke_thresh["temp"]) / 10)
    heatstroke_humidity_modifier = min(1.0, humidity / heatstroke_thresh["humidity"])
    heatstroke_risk = heatstroke_temp_factor * (0.5 + 0.5 * heatstroke_humidity_modifier)
    heatstroke_cases = int(np.random.poisson(heatstroke_risk * 40 * pop_scale))
    
    # Diarrhea cases - influenced by temperature, rainfall, and floods
    diarrhea_thresh = DISEASE_THRESHOLDS["diarrhea"]
    diarrhea_temp_factor = max(0, (temperature - diarrhea_thresh["temp"]) / 15)
    diarrhea_rainfall_factor = min(1.0, rainfall / diarrhea_thresh["rainfall"])
    diarrhea_flood_factor = min(1.0, flood_prob / diarrhea_thresh["flood_probability"])
    diarrhea_risk = max(diarrhea_temp_factor, diarrhea_rainfall_factor, diarrhea_flood_factor)
    diarrhea_cases = int(np.random.poisson(diarrhea_risk * 60 * pop_scale))
    
    # Increase cases for projected future data to account for climate change impact
    if is_projected and projection_year:
        years_in_future = projection_year - 2025
        increase_factor = 1 + (years_in_future * 0.12)  # 12% increase per year
        dengue_cases = int(dengue_cases * increase_factor)
        malaria_cases = int(malaria_cases * increase_factor)
        heatstroke_cases = int(heatstroke_cases * increase_factor * 1.2)  # Heatstroke increases faster
        diarrhea_cases = int(diarrhea_cases * increase_factor)
    
    return {
        "location_id": location["id"],
        "date": climate_data["date"],
        "dengue_cases": dengue_cases,
        "malaria_cases": malaria_cases,
        "heatstroke_cases": heatstroke_cases,
        "diarrhea_cases": diarrhea_cases,
        "is_projected": is_projected,
        "projection_year": projection_year if is_projected else None
    }

def generate_hospital_data(health_data, location, date):
    """Generate hospital resource data based on health statistics"""
    total_cases = (
        health_data["dengue_cases"] + 
        health_data["malaria_cases"] + 
        health_data["heatstroke_cases"] + 
        health_data["diarrhea_cases"]
    )
    
    # Population-based baseline resources
    population = location["population"]
    beds_per_100k = np.random.uniform(150, 300)  # Beds per 100,000 people
    doctors_per_100k = np.random.uniform(50, 100)  # Doctors per 100,000 people
    nurses_per_100k = np.random.uniform(150, 250)  # Nurses per 100,000 people
    
    # Calculate total resources based on population
    total_beds = int(population * beds_per_100k / 100000)
    total_doctors = int(population * doctors_per_100k / 100000)
    total_nurses = int(population * nurses_per_100k / 100000)
    
    # Available beds reduced by disease cases
    available_beds = max(0, total_beds - int(total_cases * 0.4))  # Assume 40% of cases need beds
    
    # Medical supplies
    base_supply = int(population / 10000)  # Base supply per 10,000 people
    iv_fluids_stock = max(0, base_supply - int(health_data["diarrhea_cases"] * 0.5 + health_data["heatstroke_cases"] * 0.7))
    antibiotics_stock = max(0, base_supply - int(health_data["malaria_cases"] * 0.6 + health_data["diarrhea_cases"] * 0.4))
    antipyretics_stock = max(0, base_supply - int(health_data["dengue_cases"] * 0.5 + health_data["malaria_cases"] * 0.3))
    
    # Project resource needs for future
    is_projected = health_data["is_projected"]
    projection_year = health_data["projection_year"]
    
    # Adjust resources for projected data
    if is_projected and projection_year:
        years_in_future = projection_year - 2025
        resource_increase = 1 + (years_in_future * 0.03)  # 3% increase per year
        
        # Projected resources with some growth
        total_beds = int(total_beds * resource_increase)
        total_doctors = int(total_doctors * resource_increase)
        total_nurses = int(total_nurses * resource_increase)
        
        # But available resources may still be strained
        case_increase = 1 + (years_in_future * 0.12)  # 12% increase in cases
        available_beds = max(0, total_beds - int(total_cases * 0.4 * case_increase))
        
        # Projected supplies
        iv_fluids_stock = max(0, base_supply * resource_increase - int((health_data["diarrhea_cases"] + health_data["heatstroke_cases"]) * 0.6))
        antibiotics_stock = max(0, base_supply * resource_increase - int((health_data["malaria_cases"] + health_data["diarrhea_cases"]) * 0.5))
        antipyretics_stock = max(0, base_supply * resource_increase - int((health_data["dengue_cases"] + health_data["malaria_cases"]) * 0.4))
    
    return {
        "location_id": location["id"],
        "date": health_data["date"],
        "total_beds": total_beds,
        "available_beds": available_beds,
        "doctors": total_doctors,
        "nurses": total_nurses,
        "iv_fluids_stock": iv_fluids_stock,
        "antibiotics_stock": antibiotics_stock,
        "antipyretics_stock": antipyretics_stock,
        "is_projected": is_projected,
        "projection_year": projection_year if is_projected else None
    }

def generate_all_data(save_path=None):
    """Generate data for all locations and save to CSV/JSON files"""
    # Add IDs to locations
    for i, location in enumerate(INDIAN_LOCATIONS):
        location["id"] = i + 1
    
    # Data lists
    all_climate_data = []
    all_health_data = []
    all_hospital_data = []
    
    # Generate current data (for September 21, 2025)
    for location in INDIAN_LOCATIONS:
        # Current day data
        current_climate = generate_climate_data(location, CURRENT_DATE)
        all_climate_data.append(current_climate)
        
        current_health = generate_health_data(current_climate, location)
        all_health_data.append(current_health)
        
        current_hospital = generate_hospital_data(current_health, location, CURRENT_DATE)
        all_hospital_data.append(current_hospital)
        
        # Historical data (past 30 days)
        for i in range(1, 31):
            past_date = CURRENT_DATE - timedelta(days=i)
            past_climate = generate_climate_data(location, past_date)
            all_climate_data.append(past_climate)
            
            past_health = generate_health_data(past_climate, location)
            all_health_data.append(past_health)
            
            past_hospital = generate_hospital_data(past_health, location, past_date)
            all_hospital_data.append(past_hospital)
    
    # Generate future projections (for 1-5 years)
    for projection_year in range(2026, 2031):
        future_date = CURRENT_DATE.replace(year=projection_year)
        
        for location in INDIAN_LOCATIONS:
            # Projected climate data
            projected_climate = generate_climate_data(
                location, 
                future_date, 
                is_projected=True, 
                projection_year=projection_year
            )
            all_climate_data.append(projected_climate)
            
            # Projected health impact
            projected_health = generate_health_data(
                projected_climate, 
                location, 
                population_factor=1 + ((projection_year - 2025) * 0.01)  # Population growth factor
            )
            all_health_data.append(projected_health)
            
            # Projected hospital resources
            projected_hospital = generate_hospital_data(projected_health, location, future_date)
            all_hospital_data.append(projected_hospital)
    
    # Convert to dataframes
    locations_df = pd.DataFrame(INDIAN_LOCATIONS)
    climate_df = pd.DataFrame(all_climate_data)
    health_df = pd.DataFrame(all_health_data)
    hospital_df = pd.DataFrame(all_hospital_data)
    
    # Save data if path provided
    if save_path:
        os.makedirs(save_path, exist_ok=True)
        locations_df.to_csv(os.path.join(save_path, "locations.csv"), index=False)
        climate_df.to_csv(os.path.join(save_path, "climate_data.csv"), index=False)
        health_df.to_csv(os.path.join(save_path, "health_data.csv"), index=False)
        hospital_df.to_csv(os.path.join(save_path, "hospital_data.csv"), index=False)
        
        # Save as JSON as well
        locations_df.to_json(os.path.join(save_path, "locations.json"), orient="records")
        climate_df.to_json(os.path.join(save_path, "climate_data.json"), orient="records")
        health_df.to_json(os.path.join(save_path, "health_data.json"), orient="records")
        hospital_df.to_json(os.path.join(save_path, "hospital_data.json"), orient="records")
    
    return {
        "locations": locations_df,
        "climate": climate_df,
        "health": health_df,
        "hospital": hospital_df
    }

if __name__ == "__main__":
    # Generate data and save to raw data folder
    data = generate_all_data(save_path="../data/raw")
    print(f"Generated data for {len(INDIAN_LOCATIONS)} locations")
    print(f"Climate data points: {len(data['climate'])}")
    print(f"Health data points: {len(data['health'])}")
    print(f"Hospital data points: {len(data['hospital'])}")
