"""
Showcase Predictions - Climate-Resilient Healthcare System

This script demonstrates the enhanced prediction models by:
1. Loading the models
2. Making predictions for different climate scenarios
3. Comparing predictions across different states/regions
4. Showing how climate changes affect health risks
5. Demonstrating resource predictions based on health risks

Usage: python showcase_predictions.py
"""

import os
import sys
import pickle
import joblib
import json
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from tabulate import tabulate
import matplotlib.pyplot as plt
from colorama import Fore, Style, init

# Initialize colorama
init(autoreset=True)

# Add the current directory to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import app modules
from app.models.database import SessionLocal
from app.models.models import Location

# Setup directories
MODELS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "models")
OUTPUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "showcase_output")
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Color mappings for risk levels
RISK_COLORS = {
    'low': Fore.GREEN,
    'medium': Fore.YELLOW,
    'high': Fore.RED,
    'critical': Fore.RED + Style.BRIGHT
}

def load_models():
    """Load the enhanced prediction models"""
    print(f"{Fore.CYAN}Loading enhanced prediction models...{Style.RESET_ALL}")
    
    # Load risk model
    risk_model_path = os.path.join(MODELS_DIR, "enhanced_risk_model.pkl")
    with open(risk_model_path, 'rb') as f:
        risk_model = pickle.load(f)
    print(f"✓ Loaded enhanced risk model from {risk_model_path}")
    
    # Load forecast model
    forecast_model_path = os.path.join(MODELS_DIR, "enhanced_forecast_model.pkl")
    with open(forecast_model_path, 'rb') as f:
        forecast_model = pickle.load(f)
    print(f"✓ Loaded enhanced forecast model from {forecast_model_path}")
    
    # Load scaler
    scaler_path = os.path.join(MODELS_DIR, "enhanced_scaler.joblib")
    scaler = joblib.load(scaler_path)
    print(f"✓ Loaded enhanced scaler from {scaler_path}")
    
    # Load metadata
    metadata_path = os.path.join(MODELS_DIR, "enhanced_models_metadata.json")
    with open(metadata_path, 'r') as f:
        metadata = json.load(f)
    print(f"✓ Loaded metadata from {metadata_path}")
    
    return risk_model, forecast_model, scaler, metadata

def get_sample_locations():
    """Get a sample of locations from the database"""
    db = SessionLocal()
    try:
        # Get a mix of states and union territories
        locations = db.query(Location).filter(Location.id.in_([1, 2, 3, 4, 5, 6, 7, 8])).all()
        return [(loc.id, loc.name, loc.type, loc.population) for loc in locations]
    finally:
        db.close()

def generate_climate_scenarios():
    """Generate different climate scenarios for testing"""
    scenarios = {
        "normal": {
            "temperature": 28,
            "rainfall": 50,
            "humidity": 70,
            "flood_probability": 0.1,
            "cyclone_probability": 0.05,
            "heatwave_probability": 0.1
        },
        "heatwave": {
            "temperature": 42,
            "rainfall": 10,
            "humidity": 60,
            "flood_probability": 0.05,
            "cyclone_probability": 0.01,
            "heatwave_probability": 0.85
        },
        "monsoon": {
            "temperature": 30,
            "rainfall": 250,
            "humidity": 90,
            "flood_probability": 0.75,
            "cyclone_probability": 0.3,
            "heatwave_probability": 0.01
        },
        "cyclone": {
            "temperature": 26,
            "rainfall": 300,
            "humidity": 95,
            "flood_probability": 0.9,
            "cyclone_probability": 0.85,
            "heatwave_probability": 0.01
        },
        "drought": {
            "temperature": 38,
            "rainfall": 5,
            "humidity": 30,
            "flood_probability": 0.01,
            "cyclone_probability": 0.01,
            "heatwave_probability": 0.6
        }
    }
    return scenarios

def print_health_risks(risks, scenario_name):
    """Print health risks in a nice format"""
    print(f"\n{Fore.CYAN}Health Risks for {scenario_name.upper()} scenario:{Style.RESET_ALL}")
    
    # Extract and sort conditions by risk level severity
    risk_order = {'critical': 4, 'high': 3, 'medium': 2, 'low': 1}
    conditions = []
    
    for condition, data in risks.items():
        if condition == "overall":
            continue
        risk_level = data.get('risk_level', 'low')
        conditions.append({
            'condition': condition.replace('_', ' ').title(),
            'risk_level': risk_level,
            'probability': data.get('probability', 0),
            'sort_order': risk_order.get(risk_level, 0)
        })
    
    # Sort by risk level (highest first)
    conditions.sort(key=lambda x: x['sort_order'], reverse=True)
    
    # Create table data
    table_data = []
    for c in conditions:
        risk_color = RISK_COLORS.get(c['risk_level'], '')
        table_data.append([
            c['condition'],
            f"{risk_color}{c['risk_level'].upper()}{Style.RESET_ALL}",
            f"{c['probability']:.2f}"
        ])
    
    # Add overall risk at the end
    overall = risks.get('overall', {})
    overall_risk = overall.get('risk_level', 'unknown')
    overall_color = RISK_COLORS.get(overall_risk, '')
    table_data.append([
        f"{Fore.CYAN}OVERALL{Style.RESET_ALL}",
        f"{overall_color}{overall_risk.upper()}{Style.RESET_ALL}",
        f"{overall.get('probability', 0):.2f}"
    ])
    
    # Print table
    print(tabulate(table_data, headers=["Health Condition", "Risk Level", "Probability"], tablefmt="grid"))

def print_resource_needs(resources, scenario_name):
    """Print resource needs in a nice format"""
    print(f"\n{Fore.CYAN}Hospital Resource Needs for {scenario_name.upper()} scenario:{Style.RESET_ALL}")
    
    # Create table data
    table_data = []
    
    # Handle case where resources might be None or not in expected format
    if not resources or not isinstance(resources, dict):
        print("No resource data available")
        return
    
    # Extract resources
    if "resources" in resources:
        # Enhanced model format
        resource_data = resources["resources"]
        peak_resources = resources.get("peak_resources", {})
        overall_risk = resources.get("overall_risk_level", "unknown")
    else:
        # Old model format or direct resources dict
        resource_data = resources
        peak_resources = {}
        overall_risk = "unknown"
    
    # Create table data
    for resource, amount in resource_data.items():
        peak = peak_resources.get(resource, "-")
        table_data.append([
            resource.replace('_', ' ').title(),
            amount,
            peak
        ])
    
    # Print table
    print(tabulate(table_data, headers=["Resource", "Normal Needs", "Peak Needs"], tablefmt="grid"))
    
    # Print overall risk
    risk_color = RISK_COLORS.get(overall_risk, '')
    print(f"\nOverall Resource Risk Level: {risk_color}{overall_risk.upper()}{Style.RESET_ALL}")

def print_natural_disasters(disasters, scenario_name):
    """Print natural disaster predictions in a nice format"""
    print(f"\n{Fore.CYAN}Natural Disaster Risks for {scenario_name.upper()} scenario:{Style.RESET_ALL}")
    
    # Create table data
    table_data = []
    for disaster, data in disasters.items():
        risk_level = data.get('risk_level', 'low')
        risk_color = RISK_COLORS.get(risk_level, '')
        table_data.append([
            disaster.title(),
            f"{risk_color}{risk_level.upper()}{Style.RESET_ALL}",
            f"{data.get('probability', 0):.2f}"
        ])
    
    # Print table
    print(tabulate(table_data, headers=["Disaster Type", "Risk Level", "Probability"], tablefmt="grid"))

def plot_disease_forecast(forecast_data, scenario_name, location_name):
    """Plot disease forecast data"""
    # Extract data
    dates = [item['date'] for item in forecast_data]
    dengue = [item.get('dengue_cases', 0) for item in forecast_data]
    malaria = [item.get('malaria_cases', 0) for item in forecast_data]
    heatstroke = [item.get('heatstroke_cases', 0) for item in forecast_data]
    diarrhea = [item.get('diarrhea_cases', 0) for item in forecast_data]
    
    # Create plot
    plt.figure(figsize=(10, 6))
    plt.plot(dates, dengue, 'r-', label='Dengue')
    plt.plot(dates, malaria, 'g-', label='Malaria')
    plt.plot(dates, heatstroke, 'b-', label='Heatstroke')
    plt.plot(dates, diarrhea, 'y-', label='Diarrhea')
    
    plt.title(f'Disease Forecast for {location_name} ({scenario_name.title()} Scenario)')
    plt.xlabel('Date')
    plt.ylabel('Cases per 100,000 population')
    plt.legend()
    plt.grid(True)
    plt.xticks(rotation=45)
    plt.tight_layout()
    
    # Save plot
    output_path = os.path.join(OUTPUT_DIR, f'forecast_{scenario_name}_{location_name.replace(" ", "_")}.png')
    plt.savefig(output_path)
    print(f"\n✓ Saved forecast plot to {output_path}")
    plt.close()

def compare_locations(risk_model, locations, scenario):
    """Compare health risks across different locations"""
    print(f"\n{Fore.CYAN}Comparing Health Risks Across Locations ({scenario.upper()} scenario):{Style.RESET_ALL}")
    
    # Current date
    current_date = datetime.now().date()
    
    # Create comparison data
    comparison_data = []
    for loc_id, loc_name, loc_type, population in locations:
        # Get risk prediction
        risks = risk_model.predict_risk(
            climate_data=generate_climate_scenarios()[scenario],
            location_id=loc_id,
            location_type=loc_type,
            date=current_date
        )
        
        # Extract overall risk
        overall = risks.get('overall', {})
        overall_risk = overall.get('risk_level', 'unknown')
        overall_color = RISK_COLORS.get(overall_risk, '')
        
        # Add to comparison data
        comparison_data.append([
            loc_name,
            loc_type.replace('_', ' ').title(),
            f"{population:,}",
            f"{overall_color}{overall_risk.upper()}{Style.RESET_ALL}",
            f"{overall.get('probability', 0):.2f}"
        ])
    
    # Print table
    print(tabulate(comparison_data, 
                  headers=["Location", "Type", "Population", "Overall Risk", "Probability"], 
                  tablefmt="grid"))

def compare_climate_scenarios(risk_model, location, scenarios):
    """Compare health risks across different climate scenarios"""
    loc_id, loc_name, loc_type, population = location
    
    print(f"\n{Fore.CYAN}Comparing Climate Scenarios for {loc_name}:{Style.RESET_ALL}")
    
    # Current date
    current_date = datetime.now().date()
    
    # Create comparison data
    comparison_data = []
    for scenario_name, climate_data in scenarios.items():
        # Get risk prediction
        risks = risk_model.predict_risk(
            climate_data=climate_data,
            location_id=loc_id,
            location_type=loc_type,
            date=current_date
        )
        
        # Extract overall risk
        overall = risks.get('overall', {})
        overall_risk = overall.get('risk_level', 'unknown')
        overall_color = RISK_COLORS.get(overall_risk, '')
        
        # Add to comparison data
        comparison_data.append([
            scenario_name.title(),
            f"{climate_data['temperature']}°C",
            f"{climate_data['rainfall']}mm",
            f"{climate_data['humidity']}%",
            f"{climate_data['flood_probability']:.2f}",
            f"{overall_color}{overall_risk.upper()}{Style.RESET_ALL}"
        ])
    
    # Print table
    print(tabulate(comparison_data, 
                  headers=["Scenario", "Temp", "Rainfall", "Humidity", "Flood Prob", "Overall Risk"], 
                  tablefmt="grid"))

def showcase_predictions():
    """Main function to showcase predictions"""
    print(f"\n{Fore.CYAN}{'='*80}{Style.RESET_ALL}")
    print(f"{Fore.CYAN}CLIMATE-RESILIENT HEALTHCARE SYSTEM - PREDICTION SHOWCASE{Style.RESET_ALL}")
    print(f"{Fore.CYAN}{'='*80}{Style.RESET_ALL}")
    
    # Load models
    risk_model, forecast_model, scaler, metadata = load_models()
    
    # Get sample locations
    locations = get_sample_locations()
    
    # Generate climate scenarios
    scenarios = generate_climate_scenarios()
    
    # Select a location for detailed showcase
    showcase_location = locations[0]  # First location
    loc_id, loc_name, loc_type, population = showcase_location
    
    print(f"\n{Fore.CYAN}Showcasing predictions for {loc_name} ({loc_type}){Style.RESET_ALL}")
    print(f"Population: {population:,}")
    
    # Current date
    current_date = datetime.now().date()
    
    # 1. Show health risks for different scenarios
    for scenario_name, climate_data in scenarios.items():
        print(f"\n{Fore.CYAN}{'='*80}{Style.RESET_ALL}")
        print(f"{Fore.CYAN}SCENARIO: {scenario_name.upper()}{Style.RESET_ALL}")
        print(f"Temperature: {climate_data['temperature']}°C, Rainfall: {climate_data['rainfall']}mm, Humidity: {climate_data['humidity']}%")
        print(f"Flood Prob: {climate_data['flood_probability']:.2f}, Cyclone Prob: {climate_data['cyclone_probability']:.2f}, Heatwave Prob: {climate_data['heatwave_probability']:.2f}")
        
        # Get health risk prediction
        risks = risk_model.predict_risk(
            climate_data=climate_data,
            location_id=loc_id,
            location_type=loc_type,
            date=current_date
        )
        
        # Print health risks
        print_health_risks(risks, scenario_name)
        
        # Get natural disaster prediction
        disasters = risk_model.predict_natural_disasters(
            climate_data=climate_data,
            location_name=loc_name,
            date=current_date
        )
        
        # Print natural disaster predictions
        print_natural_disasters(disasters, scenario_name)
        
        # Import the resource prediction function directly
        from app.utils.health_conditions import predict_hospital_resource_needs
        
        # Get resource prediction
        resources = predict_hospital_resource_needs(
            health_predictions=risks,
            population=population
        )
        
        # Print resource needs
        print_resource_needs(resources, scenario_name)
        
        # Get disease forecast
        forecast_result = forecast_model.forecast(
            climate_data=climate_data,
            location_id=loc_id,
            location_type=loc_type,
            start_date=current_date,
            days=14
        )
        
        # Plot disease forecast
        plot_disease_forecast(forecast_result.get('forecasts', []), scenario_name, loc_name)
    
    # 2. Compare locations for a specific scenario
    compare_locations(risk_model, locations, "monsoon")
    
    # 3. Compare climate scenarios for a specific location
    compare_climate_scenarios(risk_model, showcase_location, scenarios)
    
    print(f"\n{Fore.CYAN}{'='*80}{Style.RESET_ALL}")
    print(f"{Fore.CYAN}Showcase completed! Output files saved to {OUTPUT_DIR}{Style.RESET_ALL}")
    print(f"{Fore.CYAN}{'='*80}{Style.RESET_ALL}")

if __name__ == "__main__":
    showcase_predictions()
