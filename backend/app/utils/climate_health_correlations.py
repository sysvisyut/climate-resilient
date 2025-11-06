"""
Climate-health correlation functions for enhanced prediction models
"""

import numpy as np
import pandas as pd
import logging
from datetime import datetime
from typing import Dict, Any, List

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Import health conditions and natural disasters
from .health_conditions import HEALTH_CONDITIONS, NATURAL_DISASTERS

# Define risk thresholds for different diseases (rates per 100k population)
RISK_THRESHOLDS = {
    'dengue': {'low': 5, 'medium': 20, 'high': 50, 'critical': 100},
    'malaria': {'low': 3, 'medium': 10, 'high': 30, 'critical': 60},
    'heatstroke': {'low': 2, 'medium': 10, 'high': 25, 'critical': 50},
    'diarrhea': {'low': 10, 'medium': 30, 'high': 60, 'critical': 120},
    'overall': {'low': 10, 'medium': 30, 'high': 60, 'critical': 120} # Overall burden
}

# Define climate factor sensitivities for each disease
# Values represent how much a 1-unit increase in climate factor affects disease risk (relative)
CLIMATE_SENSITIVITIES = {
    'dengue': {'temperature': 0.05, 'rainfall': 0.1, 'humidity': 0.03, 'flood_probability': 0.15, 'cyclone_probability': 0.05, 'heatwave_probability': -0.02},
    'malaria': {'temperature': 0.03, 'rainfall': 0.12, 'humidity': 0.04, 'flood_probability': 0.1, 'cyclone_probability': 0.03, 'heatwave_probability': -0.01},
    'heatstroke': {'temperature': 0.15, 'rainfall': -0.05, 'humidity': 0.02, 'flood_probability': -0.01, 'cyclone_probability': -0.01, 'heatwave_probability': 0.2},
    'diarrhea': {'temperature': 0.07, 'rainfall': 0.08, 'humidity': 0.02, 'flood_probability': 0.18, 'cyclone_probability': 0.04, 'heatwave_probability': 0.01},
}

# Seasonal adjustments (multiplicative factor for disease risk by month)
SEASONAL_ADJUSTMENTS = {
    'dengue': {1:0.8, 2:0.8, 3:0.9, 4:1.0, 5:1.2, 6:1.5, 7:1.8, 8:1.7, 9:1.5, 10:1.2, 11:1.0, 12:0.9},
    'malaria': {1:0.7, 2:0.7, 3:0.8, 4:1.0, 5:1.3, 6:1.6, 7:1.9, 8:1.8, 9:1.4, 10:1.1, 11:0.9, 12:0.8},
    'heatstroke': {1:0.5, 2:0.7, 3:1.0, 4:1.5, 5:2.0, 6:1.8, 7:1.2, 8:0.9, 9:0.7, 10:0.6, 11:0.5, 12:0.5},
    'diarrhea': {1:0.9, 2:0.9, 3:1.0, 4:1.1, 5:1.3, 6:1.5, 7:1.4, 8:1.2, 9:1.1, 10:1.0, 11:0.9, 12:0.9},
}

# Base disease rates (per 100k population)
BASE_RATES = {
    'dengue': 5.0,
    'malaria': 4.0,
    'heatstroke': 2.0,
    'diarrhea': 8.0,
}

# Resource ratios per 100 cases (approximate)
RESOURCE_RATIOS_PER_100_CASES = {
    'beds': 60,
    'doctors': 5,
    'nurses': 15,
    'iv_fluids': 300, # units
    'antibiotics': 50, # units
    'antipyretics': 300 # units
}

def calculate_disease_risk(climate_data, location_type, month, disease):
    """
    Calculates a realistic disease risk rate (per 100k population) based on climate data,
    location type, and seasonality.
    """
    # Get base rate from HEALTH_CONDITIONS if available, otherwise use BASE_RATES
    if disease in HEALTH_CONDITIONS:
        base_rate = HEALTH_CONDITIONS[disease].get('base_rate_per_100k', 5.0)
    else:
        base_rate = BASE_RATES.get(disease, 5.0)
    
    # Get sensitivity from CLIMATE_SENSITIVITIES if available
    sensitivity = CLIMATE_SENSITIVITIES.get(disease, {})
    
    # Get seasonal adjustment from SEASONAL_ADJUSTMENTS if available
    seasonal_adj = SEASONAL_ADJUSTMENTS.get(disease, {}).get(month, 1.0)

    # Start with base rate
    risk_rate = base_rate

    # Apply climate sensitivities
    for factor, coeff in sensitivity.items():
        if factor in climate_data:
            # Normalize climate data to a reasonable range (e.g., temperature around 25, rainfall around 50)
            normalized_value = climate_data[factor]
            if factor == 'temperature':
                normalized_value = (climate_data[factor] - 25) / 5 # Deviation from 25C, scaled
            elif factor == 'rainfall':
                normalized_value = (climate_data[factor] - 50) / 20 # Deviation from 50mm, scaled
            elif factor == 'humidity':
                normalized_value = (climate_data[factor] - 70) / 10 # Deviation from 70%, scaled
            # Probabilities are already 0-1, use directly

            risk_rate += risk_rate * coeff * normalized_value

    # Apply seasonal adjustment
    risk_rate *= seasonal_adj

    # Add some random noise for realism
    risk_rate *= (1 + np.random.uniform(-0.1, 0.1)) # +/- 10%

    # Ensure non-negative
    return max(0.1, risk_rate)

def calculate_risk_level(rate, disease_type):
    """Determines risk level based on calculated rate and predefined thresholds."""
    # Get thresholds from HEALTH_CONDITIONS if available, otherwise use RISK_THRESHOLDS
    if disease_type in HEALTH_CONDITIONS:
        thresholds = HEALTH_CONDITIONS[disease_type].get('risk_thresholds', RISK_THRESHOLDS.get(disease_type, RISK_THRESHOLDS['overall']))
    else:
        thresholds = RISK_THRESHOLDS.get(disease_type, RISK_THRESHOLDS['overall'])
    
    if rate >= thresholds['critical']:
        return 'critical'
    elif rate >= thresholds['high']:
        return 'high'
    elif rate >= thresholds['medium']:
        return 'medium'
    else:
        return 'low'

def get_realistic_risk_prediction(climate_data, location_id, location_type, date):
    """
    Generates realistic risk predictions for all diseases and overall risk.
    """
    month = date.month
    predictions = {}
    overall_rates = []

    for disease in ['dengue', 'malaria', 'heatstroke', 'diarrhea']:
        rate = calculate_disease_risk(climate_data, location_type, month, disease)
        risk_level = calculate_risk_level(rate, disease)
        probability = min(1.0, max(0.1, rate / RISK_THRESHOLDS[disease]['critical'])) # Simple probability based on rate
        predictions[disease] = {
            'risk_level': risk_level,
            'probability': float(probability),
            'rate': float(rate)
        }
        overall_rates.append(rate)

    # Calculate overall risk
    overall_burden = np.mean(overall_rates) if overall_rates else 0.0
    overall_risk_level = calculate_risk_level(overall_burden, 'overall')
    overall_probability = min(1.0, max(0.1, overall_burden / RISK_THRESHOLDS['overall']['critical']))

    predictions['overall'] = {
        'risk_level': overall_risk_level,
        'probability': float(overall_probability),
        'rate': float(overall_burden)
    }
    return predictions

def calculate_resource_needs(disease_cases, population):
    """
    Calculates hospital resource needs based on disease cases and population.
    """
    total_cases = sum(disease_cases.values())
    
    # Scale total cases to a "per 100 cases" basis for ratio application
    scaled_cases_for_ratios = total_cases / 100.0

    resources = {}
    for resource, ratio in RESOURCE_RATIOS_PER_100_CASES.items():
        # Calculate base need
        need = scaled_cases_for_ratios * ratio
        
        # Add some variability
        need *= (1 + np.random.uniform(-0.1, 0.1)) # +/- 10%
        
        resources[resource] = int(max(0, need)) # Ensure non-negative integer

    return resources

def get_all_health_condition_risks(climate_data, location_id, location_type, date):
    """
    Get risk predictions for all health conditions defined in HEALTH_CONDITIONS
    
    Args:
        climate_data: Dictionary with climate factors
        location_id: Location ID
        location_type: Location type ('state' or 'union_territory')
        date: Date for prediction
        
    Returns:
        Dictionary with health condition predictions
    """
    # Import predict_all_health_conditions from health_conditions
    from .health_conditions import predict_all_health_conditions
    
    # Get predictions
    return predict_all_health_conditions(climate_data, location_id, location_type, date)

def get_natural_disaster_prediction(climate_data, location_name, date):
    """
    Get natural disaster predictions
    
    Args:
        climate_data: Dictionary with climate factors
        location_name: Name of the location
        date: Date for prediction
        
    Returns:
        Dictionary with natural disaster predictions
    """
    # Import get_natural_disaster_prediction from health_conditions
    from .health_conditions import get_natural_disaster_prediction as get_disaster_prediction
    
    # Get predictions
    return get_disaster_prediction(climate_data, location_name, date)

def get_peak_time_prediction(current_month, peak_season):
    """
    Get peak time prediction
    
    Args:
        current_month: Current month (1-12)
        peak_season: List of months in peak season
        
    Returns:
        Dictionary with peak time prediction
    """
    # Import get_peak_time_prediction from health_conditions
    from .health_conditions import get_peak_time_prediction as get_peak_prediction
    
    # Get prediction
    return get_peak_prediction(current_month, peak_season)