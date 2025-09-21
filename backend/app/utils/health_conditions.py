"""
Health conditions and natural disasters definitions for the enhanced prediction models
"""

# Comprehensive list of climate-sensitive health conditions with their properties
HEALTH_CONDITIONS = {
    "dengue": {
        "name": "Dengue Fever",
        "type": "Vector-borne",
        "climate_factors": ["temperature", "rainfall", "humidity"],
        "symptoms": ["High fever", "Severe headache", "Joint and muscle pain", "Rash", "Mild bleeding"],
        "resource_needs": {"beds": 0.6, "doctors": 0.05, "nurses": 0.15, "iv_fluids": 3, "antipyretics": 2, "blood_units": 0.1},
        "peak_season": [6, 7, 8, 9, 10], # Monsoon and post-monsoon
        "base_rate_per_100k": 5.0,
        "risk_thresholds": {'low': 5, 'medium': 20, 'high': 50, 'critical': 100}
    },
    "malaria": {
        "name": "Malaria",
        "type": "Vector-borne",
        "climate_factors": ["temperature", "rainfall", "humidity"],
        "symptoms": ["Fever", "Chills", "Sweating", "Headache", "Nausea", "Vomiting"],
        "resource_needs": {"beds": 0.5, "doctors": 0.04, "nurses": 0.12, "antimalarials": 2, "iv_fluids": 2, "blood_units": 0.05},
        "peak_season": [7, 8, 9, 10, 11], # Monsoon and post-monsoon
        "base_rate_per_100k": 4.0,
        "risk_thresholds": {'low': 3, 'medium': 10, 'high': 30, 'critical': 60}
    },
    "heatstroke": {
        "name": "Heat Stroke",
        "type": "Temperature-related",
        "climate_factors": ["temperature", "humidity"],
        "symptoms": ["High body temperature", "Altered mental state", "Nausea", "Headache", "Hot, dry skin"],
        "resource_needs": {"beds": 0.3, "doctors": 0.03, "nurses": 0.1, "iv_fluids": 4, "cooling_equipment": 1},
        "peak_season": [3, 4, 5, 6], # Summer
        "base_rate_per_100k": 2.0,
        "risk_thresholds": {'low': 2, 'medium': 10, 'high': 25, 'critical': 50}
    },
    "diarrhea": {
        "name": "Diarrheal Diseases",
        "type": "Water-borne",
        "climate_factors": ["temperature", "rainfall", "flood_probability"],
        "symptoms": ["Loose watery stools", "Abdominal cramps", "Dehydration", "Fever"],
        "resource_needs": {"beds": 0.4, "doctors": 0.03, "nurses": 0.08, "iv_fluids": 5, "antibiotics": 1, "oral_rehydration": 3},
        "peak_season": [6, 7, 8, 9], # Monsoon
        "base_rate_per_100k": 8.0,
        "risk_thresholds": {'low': 10, 'medium': 30, 'high': 60, 'critical': 120}
    },
    "cholera": {
        "name": "Cholera",
        "type": "Water-borne",
        "climate_factors": ["temperature", "rainfall", "flood_probability"],
        "symptoms": ["Severe watery diarrhea", "Vomiting", "Dehydration", "Leg cramps"],
        "resource_needs": {"beds": 0.7, "doctors": 0.06, "nurses": 0.15, "iv_fluids": 8, "antibiotics": 1, "oral_rehydration": 5},
        "peak_season": [6, 7, 8, 9], # Monsoon
        "base_rate_per_100k": 0.5,
        "risk_thresholds": {'low': 0.5, 'medium': 2, 'high': 5, 'critical': 10}
    },
    "typhoid": {
        "name": "Typhoid Fever",
        "type": "Water-borne",
        "climate_factors": ["temperature", "rainfall", "flood_probability"],
        "symptoms": ["Sustained fever", "Headache", "Abdominal pain", "Constipation or diarrhea"],
        "resource_needs": {"beds": 0.8, "doctors": 0.07, "nurses": 0.15, "iv_fluids": 4, "antibiotics": 2},
        "peak_season": [6, 7, 8, 9, 10], # Monsoon and post-monsoon
        "base_rate_per_100k": 1.0,
        "risk_thresholds": {'low': 1, 'medium': 5, 'high': 15, 'critical': 30}
    },
    "leptospirosis": {
        "name": "Leptospirosis",
        "type": "Water-borne",
        "climate_factors": ["rainfall", "flood_probability"],
        "symptoms": ["Fever", "Headache", "Muscle pain", "Jaundice", "Red eyes"],
        "resource_needs": {"beds": 0.6, "doctors": 0.05, "nurses": 0.12, "antibiotics": 2, "iv_fluids": 3},
        "peak_season": [7, 8, 9], # Peak monsoon
        "base_rate_per_100k": 0.2,
        "risk_thresholds": {'low': 0.2, 'medium': 1, 'high': 3, 'critical': 6}
    },
    "respiratory_infections": {
        "name": "Acute Respiratory Infections",
        "type": "Air-borne",
        "climate_factors": ["temperature", "humidity", "rainfall"],
        "symptoms": ["Cough", "Sore throat", "Runny nose", "Fever", "Difficulty breathing"],
        "resource_needs": {"beds": 0.3, "doctors": 0.03, "nurses": 0.08, "antibiotics": 1, "oxygen": 0.2},
        "peak_season": [11, 12, 1, 2], # Winter
        "base_rate_per_100k": 15.0,
        "risk_thresholds": {'low': 15, 'medium': 50, 'high': 100, 'critical': 200}
    },
    "skin_infections": {
        "name": "Skin Infections",
        "type": "Contact-related",
        "climate_factors": ["temperature", "humidity", "rainfall", "flood_probability"],
        "symptoms": ["Rash", "Itching", "Redness", "Swelling", "Pain"],
        "resource_needs": {"beds": 0.1, "doctors": 0.02, "nurses": 0.05, "antibiotics": 1, "topical_medications": 2},
        "peak_season": [6, 7, 8, 9], # Monsoon
        "base_rate_per_100k": 5.0,
        "risk_thresholds": {'low': 5, 'medium': 15, 'high': 30, 'critical': 60}
    },
    "snake_bites": {
        "name": "Snake Bites",
        "type": "Disaster-related",
        "climate_factors": ["rainfall", "flood_probability"],
        "symptoms": ["Puncture marks", "Pain", "Swelling", "Difficulty breathing", "Blurred vision"],
        "resource_needs": {"beds": 0.5, "doctors": 0.05, "nurses": 0.1, "antivenom": 1, "iv_fluids": 2},
        "peak_season": [6, 7, 8, 9], # Monsoon
        "base_rate_per_100k": 0.5,
        "risk_thresholds": {'low': 0.5, 'medium': 2, 'high': 5, 'critical': 10}
    },
    "heat_exhaustion": {
        "name": "Heat Exhaustion",
        "type": "Temperature-related",
        "climate_factors": ["temperature", "humidity"],
        "symptoms": ["Heavy sweating", "Cool, pale skin", "Dizziness", "Headache", "Nausea"],
        "resource_needs": {"beds": 0.2, "doctors": 0.02, "nurses": 0.05, "iv_fluids": 2},
        "peak_season": [3, 4, 5, 6], # Summer
        "base_rate_per_100k": 5.0,
        "risk_thresholds": {'low': 5, 'medium': 15, 'high': 30, 'critical': 60}
    },
    "heat_rash": {
        "name": "Heat Rash",
        "type": "Temperature-related",
        "climate_factors": ["temperature", "humidity"],
        "symptoms": ["Red clusters of small blisters", "Itching", "Prickling sensation"],
        "resource_needs": {"doctors": 0.01, "nurses": 0.02, "topical_medications": 1},
        "peak_season": [3, 4, 5, 6], # Summer
        "base_rate_per_100k": 10.0,
        "risk_thresholds": {'low': 10, 'medium': 30, 'high': 60, 'critical': 120}
    },
    "heat_syncope": {
        "name": "Heat Syncope",
        "type": "Temperature-related",
        "climate_factors": ["temperature", "humidity"],
        "symptoms": ["Fainting", "Dizziness", "Light-headedness"],
        "resource_needs": {"beds": 0.1, "doctors": 0.01, "nurses": 0.03, "iv_fluids": 1},
        "peak_season": [3, 4, 5, 6], # Summer
        "base_rate_per_100k": 1.0,
        "risk_thresholds": {'low': 1, 'medium': 3, 'high': 6, 'critical': 12}
    },
    "dehydration": {
        "name": "Dehydration",
        "type": "Temperature-related",
        "climate_factors": ["temperature", "humidity"],
        "symptoms": ["Thirst", "Dry mouth", "Fatigue", "Dark urine", "Dizziness"],
        "resource_needs": {"beds": 0.2, "doctors": 0.02, "nurses": 0.05, "iv_fluids": 3, "oral_rehydration": 2},
        "peak_season": [3, 4, 5, 6], # Summer
        "base_rate_per_100k": 8.0,
        "risk_thresholds": {'low': 8, 'medium': 20, 'high': 40, 'critical': 80}
    },
    "cardiovascular_stress": {
        "name": "Cardiovascular Stress",
        "type": "Temperature-related",
        "climate_factors": ["temperature", "humidity"],
        "symptoms": ["Chest pain", "Rapid heartbeat", "Shortness of breath", "Fatigue"],
        "resource_needs": {"beds": 0.5, "doctors": 0.05, "nurses": 0.1, "cardiac_monitors": 0.5, "oxygen": 0.3},
        "peak_season": [3, 4, 5, 6], # Summer
        "base_rate_per_100k": 2.0,
        "risk_thresholds": {'low': 2, 'medium': 5, 'high': 10, 'critical': 20}
    },
    "injuries": {
        "name": "Disaster-Related Injuries",
        "type": "Disaster-related",
        "climate_factors": ["flood_probability", "cyclone_probability"],
        "symptoms": ["Trauma", "Fractures", "Lacerations", "Contusions"],
        "resource_needs": {"beds": 0.8, "doctors": 0.1, "nurses": 0.2, "surgical_kits": 0.2, "blood_units": 0.3, "antibiotics": 0.5},
        "peak_season": [6, 7, 8, 9, 10], # Monsoon and cyclone seasons
        "base_rate_per_100k": 3.0,
        "risk_thresholds": {'low': 3, 'medium': 10, 'high': 25, 'critical': 50}
    },
    "trauma": {
        "name": "Psychological Trauma",
        "type": "Disaster-related",
        "climate_factors": ["flood_probability", "cyclone_probability"],
        "symptoms": ["Anxiety", "Depression", "Insomnia", "Flashbacks"],
        "resource_needs": {"mental_health_specialists": 0.05, "counseling_sessions": 3},
        "peak_season": [6, 7, 8, 9, 10], # Monsoon and cyclone seasons
        "base_rate_per_100k": 5.0,
        "risk_thresholds": {'low': 5, 'medium': 15, 'high': 30, 'critical': 60}
    },
    "landslide_injuries": {
        "name": "Landslide Related Injuries",
        "type": "Disaster-related",
        "climate_factors": ["rainfall"],
        "symptoms": ["Trauma", "Fractures", "Crush injuries", "Asphyxiation"],
        "resource_needs": {"beds": 1.5, "doctors": 0.2, "nurses": 0.5, "ambulances": 0.5, "blood_units": 0.5, "surgical_kits": 0.2},
        "peak_season": [6, 7, 8, 9], # Monsoon
        "base_rate_per_100k": 0.1,
        "risk_thresholds": {'low': 0.1, 'medium': 0.5, 'high': 1.5, 'critical': 3.0}
    },
    "drought_related_illnesses": {
        "name": "Drought-Related Illnesses",
        "type": "Disaster-related",
        "climate_factors": ["rainfall", "temperature"],
        "symptoms": ["Malnutrition", "Dehydration", "Water-borne diseases (due to poor water quality)", "Respiratory issues (dust)"],
        "resource_needs": {"beds": 0.8, "doctors": 0.08, "nurses": 0.2, "iv_fluids": 4, "nutritional_supplements": 5, "water_purification_kits": 1},
        "peak_season": [3, 4, 5, 6], # Pre-monsoon and early monsoon (if drought persists)
        "base_rate_per_100k": 3.0,
        "risk_thresholds": {'low': 3, 'medium': 10, 'high': 25, 'critical': 50}
    }
}

# Natural disasters with their properties
NATURAL_DISASTERS = {
    "flood": {
        "name": "Flood",
        "climate_factors": ["rainfall", "humidity"],
        "threshold_multiplier": 1.5, # Multiplier for base probability
        "health_impacts": ["diarrhea", "cholera", "typhoid", "leptospirosis", "dengue", "malaria", "respiratory_infections", "skin_infections", "snake_bites", "injuries"]
    },
    "cyclone": {
        "name": "Cyclone",
        "climate_factors": ["wind_speed", "pressure", "rainfall"],
        "threshold_multiplier": 2.0,
        "health_impacts": ["injuries", "diarrhea", "cholera", "typhoid", "respiratory_infections", "snake_bites", "dengue", "malaria"]
    },
    "heatwave": {
        "name": "Heatwave",
        "climate_factors": ["temperature", "humidity"],
        "threshold_multiplier": 1.8,
        "health_impacts": ["heatstroke", "heat_exhaustion", "heat_rash", "heat_syncope", "dehydration", "cardiovascular_stress"]
    },
    "landslide": {
        "name": "Landslide",
        "climate_factors": ["rainfall"],
        "threshold_multiplier": 1.2,
        "health_impacts": ["landslide_injuries", "trauma", "asphyxiation"]
    },
    "drought": {
        "name": "Drought",
        "climate_factors": ["rainfall", "temperature"],
        "threshold_multiplier": 1.0,
        "health_impacts": ["drought_related_illnesses", "malnutrition", "dehydration", "water_borne_diseases"]
    }
}

def predict_all_health_conditions(climate_data, location_id, location_type, date):
    """
    Predict all health conditions for a location based on climate data
    
    Args:
        climate_data: Dictionary with climate factors
        location_id: Location ID
        location_type: Location type ('state' or 'union_territory')
        date: Date for prediction
        
    Returns:
        Dictionary with health condition predictions
    """
    from app.utils.climate_health_correlations import calculate_disease_risk, calculate_risk_level
    
    # Get month for seasonal factors
    if isinstance(date, str):
        from datetime import datetime
        date = datetime.strptime(date, "%Y-%m-%d").date()
    month = date.month
    
    # Calculate risk for each health condition
    predictions = {}
    overall_risk_score = 0
    conditions_count = 0
    
    for condition, details in HEALTH_CONDITIONS.items():
        # Calculate rate based on climate factors and seasonality
        rate = calculate_disease_risk(climate_data, location_type, month, condition)
        
        # Calculate risk level based on rate
        risk_level = calculate_risk_level(rate, condition)
        
        # Calculate risk score (for overall risk calculation)
        risk_score_map = {"low": 1, "medium": 2, "high": 3, "critical": 4}
        risk_score = risk_score_map.get(risk_level, 1)
        
        # Calculate probability based on rate and thresholds
        thresholds = details.get("risk_thresholds", {'critical': 100})
        probability = min(0.95, max(0.1, rate / thresholds.get('critical', 100)))
        
        # Store prediction
        predictions[condition] = {
            "risk_level": risk_level,
            "probability": float(probability),
            "rate": float(rate),
            "risk_score": risk_score
        }
        
        # Update overall risk
        overall_risk_score += risk_score
        conditions_count += 1
    
    # Calculate overall risk
    if conditions_count > 0:
        avg_risk_score = overall_risk_score / conditions_count
        if avg_risk_score >= 3.5:
            overall_risk_level = "critical"
            overall_probability = 0.9
        elif avg_risk_score >= 2.5:
            overall_risk_level = "high"
            overall_probability = 0.7
        elif avg_risk_score >= 1.5:
            overall_risk_level = "medium"
            overall_probability = 0.5
        else:
            overall_risk_level = "low"
            overall_probability = 0.3
    else:
        overall_risk_level = "unknown"
        overall_probability = 0.1
    
    # Add overall risk to predictions
    predictions["overall"] = {
        "risk_level": overall_risk_level,
        "probability": float(overall_probability),
        "risk_score": float(avg_risk_score) if conditions_count > 0 else 0
    }
    
    return predictions

def calculate_peak_times(condition, current_month):
    """
    Calculate peak times for a health condition
    
    Args:
        condition: Health condition
        current_month: Current month (1-12)
        
    Returns:
        Dictionary with peak time information
    """
    if condition not in HEALTH_CONDITIONS:
        return {"status": "unknown", "months_to_peak": 0}
    
    peak_season = HEALTH_CONDITIONS[condition].get("peak_season", [])
    if not peak_season:
        return {"status": "unknown", "months_to_peak": 0}
    
    return get_peak_time_prediction(current_month, peak_season)

def get_peak_time_prediction(current_month, peak_season):
    """
    Calculate peak time prediction based on current month and peak season
    
    Args:
        current_month: Current month (1-12)
        peak_season: List of months in peak season
        
    Returns:
        Dictionary with peak time information
    """
    if not peak_season:
        return {"status": "unknown", "months_to_peak": 0}
    
    # Check if current month is in peak season
    if current_month in peak_season:
        return {"status": "peak", "months_to_peak": 0}
    
    # Calculate months to next peak
    months_to_peak = 0
    month = current_month
    while True:
        month = (month % 12) + 1  # Move to next month, wrap around to 1 after 12
        months_to_peak += 1
        if month in peak_season:
            break
        if months_to_peak >= 12:  # Safeguard against infinite loop
            return {"status": "unknown", "months_to_peak": 0}
    
    if months_to_peak <= 3:
        return {"status": "approaching", "months_to_peak": months_to_peak}
    else:
        return {"status": "off-peak", "months_to_peak": months_to_peak}

def predict_hospital_resource_needs(health_predictions, population):
    """
    Predict hospital resource needs based on health predictions
    
    Args:
        health_predictions: Dictionary with health predictions
        population: Population of the location
        
    Returns:
        Dictionary with resource predictions
    """
    # Initialize resources
    resources = {
        "beds": 0,
        "doctors": 0,
        "nurses": 0,
        "iv_fluids": 0,
        "antibiotics": 0,
        "antipyretics": 0,
        "antimalarials": 0,
        "oral_rehydration": 0,
        "cooling_equipment": 0,
        "oxygen": 0,
        "surgical_kits": 0,
        "blood_units": 0,
        "ambulances": 0,
        "mental_health_specialists": 0,
        "counseling_sessions": 0,
        "topical_medications": 0,
        "antivenom": 0,
        "cardiac_monitors": 0,
        "nutritional_supplements": 0,
        "water_purification_kits": 0
    }
    
    # Calculate total cases for each condition
    total_cases = {}
    for condition, prediction in health_predictions.items():
        if condition == "overall":
            continue
        
        # Convert rate per 100k to estimated cases
        rate = prediction.get("rate", 0)
        estimated_cases = (rate / 100000) * population
        total_cases[condition] = estimated_cases
    
    # Calculate resource needs for each condition
    for condition, cases in total_cases.items():
        if condition not in HEALTH_CONDITIONS:
            continue
        
        resource_ratios = HEALTH_CONDITIONS[condition].get("resource_needs", {})
        for resource, ratio in resource_ratios.items():
            if resource in resources:
                resources[resource] += cases * ratio
    
    # Round resource needs to integers
    for resource in resources:
        resources[resource] = int(resources[resource])
    
    # Calculate peak resource needs (25% higher than current)
    peak_resources = {resource: int(amount * 1.25) for resource, amount in resources.items()}
    
    # Determine overall risk level based on bed capacity
    if resources["beds"] > population * 0.001:  # More than 0.1% of population needs beds
        overall_risk_level = "critical"
    elif resources["beds"] > population * 0.0005:  # More than 0.05% of population needs beds
        overall_risk_level = "high"
    elif resources["beds"] > population * 0.0002:  # More than 0.02% of population needs beds
        overall_risk_level = "medium"
    else:
        overall_risk_level = "low"
    
    return {
        "resources": resources,
        "peak_resources": peak_resources,
        "overall_risk_level": overall_risk_level
    }

def get_natural_disaster_prediction(climate_data, location_name, date):
    """
    Predict natural disaster probabilities based on climate data
    
    Args:
        climate_data: Dictionary with climate factors
        location_name: Name of the location
        date: Date for prediction
        
    Returns:
        Dictionary with natural disaster predictions
    """
    predictions = {}
    
    for disaster, details in NATURAL_DISASTERS.items():
        # Calculate base probability based on climate factors
        base_probability = 0.01  # Minimum probability
        
        for factor in details["climate_factors"]:
            if factor in climate_data:
                if factor == "temperature" and climate_data[factor] > 35:
                    # High temperature increases probability for heat-related disasters
                    base_probability += 0.1 + (climate_data[factor] - 35) / 10
                elif factor == "rainfall" and climate_data[factor] > 50:
                    # Heavy rainfall increases probability for flood-related disasters
                    base_probability += 0.1 + (climate_data[factor] - 50) / 100
                elif factor == "humidity" and climate_data[factor] > 80:
                    # High humidity increases probability for certain disasters
                    base_probability += 0.05 + (climate_data[factor] - 80) / 100
                elif factor == "flood_probability":
                    # Direct probability factor
                    base_probability += climate_data[factor] * 0.5
                elif factor == "cyclone_probability":
                    # Direct probability factor
                    base_probability += climate_data[factor] * 0.5
                elif factor == "heatwave_probability":
                    # Direct probability factor
                    base_probability += climate_data[factor] * 0.5
        
        # Apply threshold multiplier
        probability = min(0.95, base_probability * details.get("threshold_multiplier", 1.0))
        
        # Determine risk level based on probability
        if probability >= 0.75:
            risk_level = "critical"
        elif probability >= 0.5:
            risk_level = "high"
        elif probability >= 0.25:
            risk_level = "medium"
        else:
            risk_level = "low"
        
        # Store prediction
        predictions[disaster] = {
            "probability": float(probability),
            "risk_level": risk_level,
            "health_impacts": details.get("health_impacts", [])
        }
    
    return predictions