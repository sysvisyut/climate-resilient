import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import os

# Create directories
os.makedirs('data/raw', exist_ok=True)

print("Generating sample data...")

# 1. Generate Locations Data
locations_data = {
    'location_id': range(1, 37),
    'state': ['Maharashtra', 'Karnataka', 'Tamil Nadu', 'Delhi', 'West Bengal', 'Gujarat'] * 6,
    'district': [f'District_{i}' for i in range(1, 37)],
    'latitude': np.random.uniform(8.0, 35.0, 36),
    'longitude': np.random.uniform(68.0, 97.0, 36),
    'population': np.random.randint(100000, 5000000, 36),
    'urban_rural': np.random.choice(['Urban', 'Rural'], 36)
}
locations_df = pd.DataFrame(locations_data)
locations_df.to_csv('data/raw/locations.csv', index=False)
print(f"✓ Created locations.csv with {len(locations_df)} locations")

# 2. Generate Climate Data (36 locations × 36 months)
climate_records = []
start_date = datetime(2022, 1, 1)

for loc_id in range(1, 37):
    for month in range(36):
        date = start_date + timedelta(days=30 * month)
        climate_records.append({
            'location_id': loc_id,
            'date': date.strftime('%Y-%m-%d'),
            'temperature': np.random.uniform(15, 40),
            'humidity': np.random.uniform(40, 90),
            'rainfall': np.random.uniform(0, 300),
            'air_quality_index': np.random.uniform(50, 300)
        })

climate_df = pd.DataFrame(climate_records)
climate_df.to_csv('data/raw/climate_data.csv', index=False)
print(f"✓ Created climate_data.csv with {len(climate_df)} records")

# 3. Generate Health Data
health_records = []
diseases = ['Dengue', 'Malaria', 'Respiratory', 'Diarrhea', 'Heat_Stroke']

for loc_id in range(1, 37):
    for month in range(36):
        date = start_date + timedelta(days=30 * month)
        health_records.append({
            'location_id': loc_id,
            'date': date.strftime('%Y-%m-%d'),
            'disease_type': np.random.choice(diseases),
            'cases': np.random.randint(10, 500),
            'deaths': np.random.randint(0, 20),
            'hospitalizations': np.random.randint(5, 200)
        })

health_df = pd.DataFrame(health_records)
health_df.to_csv('data/raw/health_data.csv', index=False)
print(f"✓ Created health_data.csv with {len(health_df)} records")

# 4. Generate Hospital Data
hospital_records = []

for loc_id in range(1, 37):
    for month in range(36):
        date = start_date + timedelta(days=30 * month)
        hospital_records.append({
            'location_id': loc_id,
            'date': date.strftime('%Y-%m-%d'),
            'hospital_name': f'Hospital_{loc_id}',
            'beds_total': np.random.randint(50, 500),
            'beds_available': np.random.randint(10, 100),
            'doctors': np.random.randint(10, 100),
            'nurses': np.random.randint(20, 200),
            'equipment_status': np.random.choice(['Good', 'Fair', 'Poor'])
        })

hospital_df = pd.DataFrame(hospital_records)
hospital_df.to_csv('data/raw/hospital_data.csv', index=False)
print(f"✓ Created hospital_data.csv with {len(hospital_df)} records")

print("\n✅ All sample data generated successfully!")
print(f"Location: {os.path.abspath('data/raw/')}")
print("\nFiles created:")
print("  - locations.csv")
print("  - climate_data.csv")
print("  - health_data.csv")
print("  - hospital_data.csv")
