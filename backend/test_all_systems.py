"""
Comprehensive System Test - Climate-Resilient Healthcare System
Tests all ML models, backend APIs, and database functionality
"""

import requests
import json
from datetime import datetime

# Configuration
BASE_URL = "http://localhost:8000"
TEST_USER = {
    "username": "admin@climate-health.org",
    "password": "admin123"
}

# Color codes for output
GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
BLUE = "\033[94m"
RESET = "\033[0m"

def print_section(title):
    print(f"\n{BLUE}{'='*70}{RESET}")
    print(f"{BLUE}{title:^70}{RESET}")
    print(f"{BLUE}{'='*70}{RESET}\n")

def print_test(name, status, details=""):
    icon = f"{GREEN}✓{RESET}" if status else f"{RED}✗{RESET}"
    print(f"{icon} {name}")
    if details:
        print(f"  → {details}")

def get_auth_token():
    """Get authentication token"""
    try:
        response = requests.post(
            f"{BASE_URL}/auth/token",
            data=TEST_USER
        )
        if response.status_code == 200:
            return response.json()["access_token"]
        return None
    except Exception as e:
        print(f"{RED}Error getting token: {e}{RESET}")
        return None

def test_backend_health():
    """Test backend server health"""
    print_section("BACKEND SERVER TESTS")
    
    # Test 1: Root endpoint
    try:
        response = requests.get(f"{BASE_URL}/")
        print_test("Root Endpoint (/)", response.status_code == 200, 
                   f"Status: {response.status_code}")
    except Exception as e:
        print_test("Root Endpoint (/)", False, str(e))
    
    # Test 2: Health check
    try:
        response = requests.get(f"{BASE_URL}/health")
        data = response.json()
        print_test("Health Check (/health)", 
                   response.status_code == 200 and data.get("status") == "healthy",
                   f"Status: {data.get('status')}")
    except Exception as e:
        print_test("Health Check", False, str(e))
    
    # Test 3: API Documentation
    try:
        response = requests.get(f"{BASE_URL}/docs")
        print_test("API Documentation (/docs)", 
                   response.status_code == 200,
                   "Swagger UI accessible")
    except Exception as e:
        print_test("API Documentation", False, str(e))

def test_authentication():
    """Test authentication system"""
    print_section("AUTHENTICATION TESTS")
    
    # Test 1: Login with correct credentials
    try:
        response = requests.post(f"{BASE_URL}/auth/token", data=TEST_USER)
        if response.status_code == 200:
            data = response.json()
            print_test("Admin Login", True, 
                       f"Token received, Role: {data.get('role')}")
            return data["access_token"]
        else:
            print_test("Admin Login", False, f"Status: {response.status_code}")
            return None
    except Exception as e:
        print_test("Admin Login", False, str(e))
        return None
    
    # Test 2: Login with wrong credentials
    try:
        response = requests.post(f"{BASE_URL}/auth/token", 
                                data={"username": "test@test.com", "password": "wrong"})
        print_test("Invalid Login Rejection", 
                   response.status_code == 401,
                   "Correctly rejected invalid credentials")
    except Exception as e:
        print_test("Invalid Login Rejection", False, str(e))

def test_data_endpoints(token):
    """Test data retrieval endpoints"""
    print_section("DATA ENDPOINTS TESTS")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # Test 1: Get all locations
    try:
        response = requests.get(f"{BASE_URL}/data/locations", headers=headers)
        if response.status_code == 200:
            locations = response.json()
            print_test("Get All Locations", True, 
                       f"Found {len(locations)} Indian states/UTs")
        else:
            print_test("Get All Locations", False, f"Status: {response.status_code}")
    except Exception as e:
        print_test("Get All Locations", False, str(e))
    
    # Test 2: Get specific location (Delhi - ID 32)
    try:
        response = requests.get(f"{BASE_URL}/data/locations/32", headers=headers)
        if response.status_code == 200:
            location = response.json()
            print_test("Get Specific Location (Delhi)", True, 
                       f"Name: {location.get('name')}, Population: {location.get('population'):,}")
        else:
            print_test("Get Specific Location", False)
    except Exception as e:
        print_test("Get Specific Location", False, str(e))
    
    # Test 3: Get climate data
    try:
        response = requests.get(f"{BASE_URL}/data/climate/32", headers=headers)
        if response.status_code == 200:
            data = response.json()
            print_test("Get Climate Data", True, 
                       f"Retrieved {len(data)} climate records")
        else:
            print_test("Get Climate Data", False)
    except Exception as e:
        print_test("Get Climate Data", False, str(e))
    
    # Test 4: Get health data
    try:
        response = requests.get(f"{BASE_URL}/data/health/32", headers=headers)
        if response.status_code == 200:
            data = response.json()
            print_test("Get Health Data", True, 
                       f"Retrieved {len(data)} health records")
        else:
            print_test("Get Health Data", False)
    except Exception as e:
        print_test("Get Health Data", False, str(e))
    
    # Test 5: Get hospital data
    try:
        response = requests.get(f"{BASE_URL}/data/hospital/32", headers=headers)
        if response.status_code == 200:
            data = response.json()
            print_test("Get Hospital Data", True, 
                       f"Retrieved {len(data)} hospital records")
        else:
            print_test("Get Hospital Data", False)
    except Exception as e:
        print_test("Get Hospital Data", False, str(e))
    
    # Test 6: Get data summary
    try:
        response = requests.get(f"{BASE_URL}/data/summary", headers=headers)
        if response.status_code == 200:
            summary = response.json()
            print_test("Data Summary", True, 
                       f"Locations: {summary.get('total_locations')}, "
                       f"Climate records: {summary.get('total_climate_records')}")
        else:
            print_test("Data Summary", False)
    except Exception as e:
        print_test("Data Summary", False, str(e))

def test_ml_predictions(token):
    """Test ML model predictions"""
    print_section("ML MODEL PREDICTION TESTS")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # Test 1: Risk prediction
    try:
        response = requests.get(f"{BASE_URL}/predictions/risk/32", headers=headers)
        if response.status_code == 200:
            risk = response.json()
            print_test("Health Risk Prediction", True, 
                       f"Overall risk: {risk.get('overall_risk', 'N/A')}")
        else:
            print_test("Health Risk Prediction", False, f"Status: {response.status_code}")
    except Exception as e:
        print_test("Health Risk Prediction", False, str(e))
    
    # Test 2: Disease forecast
    try:
        response = requests.get(f"{BASE_URL}/predictions/forecast/32?days=7", headers=headers)
        if response.status_code == 200:
            forecast = response.json()
            print_test("Disease Forecasting", True, 
                       f"Forecast generated for {len(forecast.get('forecasts', []))} days")
        else:
            print_test("Disease Forecasting", False, f"Status: {response.status_code}")
    except Exception as e:
        print_test("Disease Forecasting", False, str(e))
    
    # Test 3: Resource prediction
    try:
        response = requests.get(f"{BASE_URL}/predictions/resources/32", headers=headers)
        if response.status_code == 200:
            resources = response.json()
            print_test("Resource Needs Prediction", True, 
                       f"Predicted beds needed: {resources.get('predicted_beds_needed', 'N/A')}")
        else:
            print_test("Resource Needs Prediction", False, f"Status: {response.status_code}")
    except Exception as e:
        print_test("Resource Needs Prediction", False, str(e))

def test_enhanced_predictions(token):
    """Test enhanced prediction endpoints"""
    print_section("ENHANCED PREDICTION TESTS")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # Test 1: Enhanced health risks
    try:
        response = requests.get(f"{BASE_URL}/enhanced/health-risks/32?use_real_time=false", 
                               headers=headers)
        if response.status_code == 200:
            risks = response.json()
            print_test("Enhanced Health Risks", True, 
                       f"Risk level: {risks.get('risk_level', 'N/A')}")
        else:
            print_test("Enhanced Health Risks", False, f"Status: {response.status_code}")
    except Exception as e:
        print_test("Enhanced Health Risks", False, str(e))
    
    # Test 2: Enhanced resource needs
    try:
        response = requests.get(f"{BASE_URL}/enhanced/resource-needs/32?use_real_time=false", 
                               headers=headers)
        if response.status_code == 200:
            resources = response.json()
            print_test("Enhanced Resource Needs", True, 
                       f"Total beds needed: {resources.get('total_beds_needed', 'N/A')}")
        else:
            print_test("Enhanced Resource Needs", False, f"Status: {response.status_code}")
    except Exception as e:
        print_test("Enhanced Resource Needs", False, str(e))
    
    # Test 3: Natural disasters prediction
    try:
        response = requests.get(f"{BASE_URL}/enhanced/natural-disasters/32?days_ahead=7", 
                               headers=headers)
        if response.status_code == 200:
            disasters = response.json()
            print_test("Natural Disaster Forecast", True, 
                       f"Forecasts for {len(disasters.get('forecasts', []))} days")
        else:
            print_test("Natural Disaster Forecast", False, f"Status: {response.status_code}")
    except Exception as e:
        print_test("Natural Disaster Forecast", False, str(e))
    
    # Test 4: Peak times prediction
    try:
        response = requests.get(f"{BASE_URL}/enhanced/peak-times/32", headers=headers)
        if response.status_code == 200:
            peaks = response.json()
            print_test("Peak Times Prediction", True, 
                       f"Peak month: {peaks.get('peak_month', 'N/A')}")
        else:
            print_test("Peak Times Prediction", False, f"Status: {response.status_code}")
    except Exception as e:
        print_test("Peak Times Prediction", False, str(e))

def test_database():
    """Test database integrity"""
    print_section("DATABASE INTEGRITY TESTS")
    
    import sqlite3
    
    try:
        conn = sqlite3.connect('climate_health.db')
        cursor = conn.cursor()
        
        # Test 1: Check tables exist
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row[0] for row in cursor.fetchall()]
        expected_tables = ['locations', 'climate_data', 'health_data', 'hospital_data', 'users']
        all_exist = all(table in tables for table in expected_tables)
        print_test("All Required Tables Exist", all_exist, 
                   f"Found: {', '.join(tables)}")
        
        # Test 2: Check locations count
        cursor.execute("SELECT COUNT(*) FROM locations")
        location_count = cursor.fetchone()[0]
        print_test("Locations Data", location_count == 36, 
                   f"Found {location_count} locations (expected 36)")
        
        # Test 3: Check climate data
        cursor.execute("SELECT COUNT(*) FROM climate_data")
        climate_count = cursor.fetchone()[0]
        print_test("Climate Data", climate_count > 0, 
                   f"Found {climate_count:,} climate records")
        
        # Test 4: Check health data
        cursor.execute("SELECT COUNT(*) FROM health_data")
        health_count = cursor.fetchone()[0]
        print_test("Health Data", health_count > 0, 
                   f"Found {health_count:,} health records")
        
        # Test 5: Check hospital data
        cursor.execute("SELECT COUNT(*) FROM hospital_data")
        hospital_count = cursor.fetchone()[0]
        print_test("Hospital Data", hospital_count > 0, 
                   f"Found {hospital_count:,} hospital records")
        
        # Test 6: Check users
        cursor.execute("SELECT COUNT(*) FROM users")
        user_count = cursor.fetchone()[0]
        print_test("User Accounts", user_count > 0, 
                   f"Found {user_count} users")
        
        conn.close()
        
    except Exception as e:
        print_test("Database Connection", False, str(e))

def test_ml_models():
    """Test ML models existence"""
    print_section("ML MODELS TESTS")
    
    import os
    
    model_dir = "models"
    
    # Check if models directory exists
    if os.path.exists(model_dir):
        print_test("Models Directory", True, f"Found at: {model_dir}")
        
        # List model files
        model_files = os.listdir(model_dir) if os.path.exists(model_dir) else []
        if model_files:
            print_test("Model Files", True, f"Found {len(model_files)} model files:")
            for model_file in model_files:
                print(f"    • {model_file}")
        else:
            print_test("Model Files", False, "No model files found - run /setup to train models")
    else:
        print_test("Models Directory", False, "Directory not found - run /setup to train models")

def test_frontend_connectivity():
    """Test frontend server"""
    print_section("FRONTEND SERVER TESTS")
    
    try:
        response = requests.get("http://localhost:3000", timeout=3)
        print_test("Frontend Server", response.status_code == 200, 
                   "Running on http://localhost:3000")
    except requests.exceptions.ConnectionError:
        print_test("Frontend Server", False, "Not responding - may need to start")
    except Exception as e:
        print_test("Frontend Server", False, str(e))

def print_summary():
    """Print test summary"""
    print_section("SYSTEM STATUS SUMMARY")
    
    print(f"{GREEN}✓ Backend API:{RESET} http://localhost:8000")
    print(f"{GREEN}✓ API Docs:{RESET} http://localhost:8000/docs")
    print(f"{GREEN}✓ Frontend:{RESET} http://localhost:3000")
    print(f"\n{YELLOW}Admin Credentials:{RESET}")
    print(f"  Email: admin@climate-health.org")
    print(f"  Password: admin123")
    print(f"\n{BLUE}Next Steps:{RESET}")
    print(f"  1. Login at http://localhost:3000")
    print(f"  2. View India disease risk map")
    print(f"  3. Check predictions for different states")
    print(f"  4. Review resource allocation needs")

def main():
    """Run all tests"""
    print(f"\n{BLUE}{'='*70}{RESET}")
    print(f"{BLUE}{'CLIMATE-RESILIENT HEALTHCARE SYSTEM':^70}{RESET}")
    print(f"{BLUE}{'Comprehensive System Test':^70}{RESET}")
    print(f"{BLUE}{'='*70}{RESET}")
    print(f"{YELLOW}Testing Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}{RESET}")
    
    # Run all test suites
    test_backend_health()
    token = test_authentication()
    
    if token:
        test_data_endpoints(token)
        test_ml_predictions(token)
        test_enhanced_predictions(token)
    else:
        print(f"\n{RED}⚠ Skipping authenticated tests - login failed{RESET}")
    
    test_database()
    test_ml_models()
    test_frontend_connectivity()
    print_summary()
    
    print(f"\n{GREEN}{'='*70}{RESET}")
    print(f"{GREEN}{'TEST COMPLETE':^70}{RESET}")
    print(f"{GREEN}{'='*70}{RESET}\n")

if __name__ == "__main__":
    main()
