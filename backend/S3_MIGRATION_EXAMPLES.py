"""
Example: Updating existing code to use S3 storage

This file demonstrates how to migrate from local file storage to S3 storage.
"""

# ============================================================================
# BEFORE: Using Local File Storage
# ============================================================================

# Old approach - reading from local files
def load_climate_data_old():
    import pandas as pd
    import os
    
    # Local file path
    file_path = os.path.join('backend', 'data', 'raw', 'climate_data.csv')
    
    # Read from local filesystem
    df = pd.read_csv(file_path)
    return df


# Old approach - saving to local files
def save_predictions_old(predictions, date):
    import pandas as pd
    import os
    import json
    
    # Local directory path
    output_dir = os.path.join('backend', 'data', 'processed', 'predictions')
    os.makedirs(output_dir, exist_ok=True)
    
    # Save to local file
    output_file = os.path.join(output_dir, f'predictions_{date}.json')
    with open(output_file, 'w') as f:
        json.dump(predictions, f, indent=2)


# Old approach - loading models
def load_model_old():
    import pickle
    import os
    
    model_path = os.path.join('backend', 'models', 'risk_model.pkl')
    
    with open(model_path, 'rb') as f:
        model = pickle.load(f)
    
    return model


# ============================================================================
# AFTER: Using S3 Storage
# ============================================================================

# New approach - using data service
def load_climate_data_new():
    from app.services.data_service import data_service
    
    # Load from S3 via service
    df = data_service.load_climate_data()
    return df


# New approach - using data service for predictions
def save_predictions_new(predictions, date):
    from app.services.data_service import data_service
    
    # Save to S3 via service
    success = data_service.save_predictions(predictions, date)
    return success


# New approach - using model service
def load_model_new():
    from app.services.model_service import model_service
    
    # Load from S3 via service
    model = model_service.load_risk_model()
    return model


# ============================================================================
# MIGRATION EXAMPLE: Updating a Real Function
# ============================================================================

# BEFORE - Local storage version
def generate_health_report_old(location_id, date):
    """Generate health report using local files"""
    import pandas as pd
    import os
    import json
    
    # Load data from local files
    climate_file = os.path.join('data', 'raw', 'climate_data.csv')
    health_file = os.path.join('data', 'raw', 'health_data.csv')
    
    climate_df = pd.read_csv(climate_file)
    health_df = pd.read_csv(health_file)
    
    # Filter by location
    climate_df = climate_df[climate_df['location_id'] == location_id]
    health_df = health_df[health_df['location_id'] == location_id]
    
    # Generate report
    report = {
        'location_id': location_id,
        'date': date,
        'climate_records': len(climate_df),
        'health_records': len(health_df)
    }
    
    # Save report locally
    output_dir = os.path.join('data', 'processed', 'reports')
    os.makedirs(output_dir, exist_ok=True)
    
    output_file = os.path.join(output_dir, f'report_{location_id}_{date}.json')
    with open(output_file, 'w') as f:
        json.dump(report, f, indent=2)
    
    return report


# AFTER - S3 storage version
def generate_health_report_new(location_id, date):
    """Generate health report using S3 storage"""
    from app.services.data_service import data_service
    
    # Load data from S3 via service
    climate_df = data_service.load_climate_data(location_id=location_id)
    health_df = data_service.load_health_data(location_id=location_id)
    
    # Generate report
    report = {
        'location_id': location_id,
        'date': date,
        'climate_records': len(climate_df) if climate_df is not None else 0,
        'health_records': len(health_df) if health_df is not None else 0
    }
    
    # Save report to S3 via service (using the s3_storage utility directly)
    from app.utils.s3_storage import s3_storage
    success = s3_storage.save_json_to_s3(
        report,
        f"reports/{date}/report_{location_id}_{date}.json"
    )
    
    return report


# ============================================================================
# MIGRATION EXAMPLE: Updating API Endpoints
# ============================================================================

# BEFORE - FastAPI endpoint using local storage
def old_prediction_endpoint():
    from fastapi import FastAPI, HTTPException
    import pandas as pd
    import pickle
    import os
    
    app = FastAPI()
    
    @app.post("/predictions")
    async def create_prediction(location_id: str, date: str):
        try:
            # Load model from local file
            model_path = os.path.join('models', 'risk_model.pkl')
            with open(model_path, 'rb') as f:
                model = pickle.load(f)
            
            # Load data from local file
            data_path = os.path.join('data', 'raw', 'climate_data.csv')
            df = pd.read_csv(data_path)
            df = df[df['location_id'] == location_id]
            
            # Make prediction
            prediction = model.predict(df)
            
            # Save result locally
            output_dir = os.path.join('data', 'processed', 'predictions')
            os.makedirs(output_dir, exist_ok=True)
            
            result = {'prediction': prediction.tolist(), 'location': location_id}
            
            return result
            
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))


# AFTER - FastAPI endpoint using S3 storage
def new_prediction_endpoint():
    from fastapi import FastAPI, HTTPException
    from app.services.data_service import data_service
    from app.services.model_service import model_service
    
    app = FastAPI()
    
    @app.post("/predictions")
    async def create_prediction(location_id: str, date: str):
        try:
            # Load model from S3
            model = model_service.load_risk_model()
            if model is None:
                raise HTTPException(status_code=500, detail="Model not found")
            
            # Load data from S3
            df = data_service.load_climate_data(location_id=location_id)
            if df is None or len(df) == 0:
                raise HTTPException(status_code=404, detail="No data found for location")
            
            # Make prediction
            prediction = model.predict(df)
            
            # Save result to S3
            result = {'prediction': prediction.tolist(), 'location': location_id, 'date': date}
            data_service.save_predictions([result], date)
            
            return result
            
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# BEST PRACTICES FOR MIGRATION
# ============================================================================

def migration_best_practices():
    """
    Best practices when migrating from local to S3 storage:
    
    1. Use Service Layer
       - Always use data_service and model_service
       - Don't call s3_storage directly unless necessary
       - Services provide consistent error handling
    
    2. Handle Errors Gracefully
       - Check for None returns from load operations
       - Provide meaningful error messages
       - Use try-except blocks for S3 operations
    
    3. Optimize Data Access
       - Cache frequently accessed data
       - Use filters when loading data (e.g., by location_id)
       - Load only the columns you need
    
    4. Organize Data Logically
       - Use consistent naming conventions
       - Organize by date/time for easy cleanup
       - Use prefixes for different data types
    
    5. Monitor and Log
       - Log all S3 operations
       - Monitor CloudWatch for errors
       - Track S3 costs and usage
    """
    pass


# ============================================================================
# STEP-BY-STEP MIGRATION CHECKLIST
# ============================================================================

"""
Migration Checklist:

□ 1. Install dependencies
     pip install boto3 pandas

□ 2. Create S3 utility and services
     ✓ app/utils/s3_storage.py
     ✓ app/services/data_service.py
     ✓ app/services/model_service.py

□ 3. Save models locally
     python save_enhanced_models.py

□ 4. Migrate data to S3
     python migrate_data_to_s3.py

□ 5. Test S3 integration
     python test_s3_integration.py

□ 6. Update API endpoints
     - Replace file I/O with service calls
     - Update error handling
     - Test each endpoint

□ 7. Update background jobs
     - Replace file operations
     - Test scheduled tasks

□ 8. Update frontend API calls
     - Verify endpoints still work
     - Check response formats

□ 9. Performance testing
     - Test with large datasets
     - Monitor response times
     - Check S3 costs

□ 10. Deploy and monitor
     - Deploy to production
     - Monitor CloudWatch logs
     - Set up alerts
"""


# ============================================================================
# COMMON PATTERNS
# ============================================================================

# Pattern 1: Loading data with fallback
def load_data_with_fallback(location_id):
    from app.services.data_service import data_service
    
    # Try to load from S3
    df = data_service.load_climate_data(location_id=location_id)
    
    # Check if data was loaded
    if df is None or len(df) == 0:
        # Handle missing data
        return None
    
    return df


# Pattern 2: Batch processing with S3
def batch_process_predictions(location_ids, date):
    from app.services.data_service import data_service
    from app.services.model_service import model_service
    
    # Load model once
    model = model_service.load_risk_model()
    
    predictions = []
    
    # Process each location
    for location_id in location_ids:
        # Load data for location
        df = data_service.load_climate_data(location_id=location_id)
        
        if df is not None and len(df) > 0:
            # Make prediction
            pred = model.predict(df)
            predictions.append({
                'location_id': location_id,
                'prediction': pred.tolist()
            })
    
    # Save all predictions at once
    data_service.save_predictions(predictions, date)
    
    return predictions


# Pattern 3: Checking data freshness
def check_data_freshness():
    from app.utils.s3_storage import s3_storage
    from datetime import datetime, timedelta
    
    # Check if today's data exists
    today = datetime.now().strftime('%Y-%m-%d')
    key = f"processed/climate_data_{today}.csv"
    
    exists = s3_storage.object_exists(key)
    
    if not exists:
        # Data needs to be processed
        return False
    
    return True


# Pattern 4: Listing and filtering data
def get_recent_predictions(days=7):
    from app.utils.s3_storage import s3_storage
    from datetime import datetime, timedelta
    
    predictions = []
    
    # Get dates for last N days
    for i in range(days):
        date = (datetime.now() - timedelta(days=i)).strftime('%Y-%m-%d')
        
        # List objects for this date
        objects = s3_storage.list_objects(f"predictions/{date}/")
        
        # Load each prediction file
        for obj_key in objects:
            data = s3_storage.load_json_from_s3(obj_key)
            if data:
                predictions.extend(data.get('predictions', []))
    
    return predictions
