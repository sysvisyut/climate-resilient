# AWS S3 Storage Migration - Setup Guide

## Overview
This guide provides step-by-step instructions to migrate your local data storage to AWS S3 buckets.

## Prerequisites

1. AWS CLI configured with proper credentials
2. Python 3.8+ installed
3. Required Python packages installed

## Installation

```bash
# Install required packages
pip install boto3 pandas

# Or add to your requirements.txt
echo "boto3>=1.28.0" >> requirements.txt
echo "pandas>=2.0.0" >> requirements.txt
```

## S3 Bucket Structure

Your data will be organized in three main buckets:

### 1. Raw Data Bucket: `climate-health-raw-data-sharvaj`
```
raw/
├── climate_data.csv
├── health_data.csv
├── hospital_data.csv
└── locations.csv
```

### 2. Processed Data Bucket: `climate-health-processed-data-sharvaj`
```
processed/
├── climate_data_YYYY-MM-DD.csv
├── health_data_YYYY-MM-DD.csv
└── ...
predictions/
├── YYYY-MM-DD/
│   └── predictions_timestamp.json
forecasts/
└── YYYY-MM-DD/
    └── forecasts_timestamp.json
alerts/
└── YYYY-MM-DD/
    └── alerts_timestamp.json
```

### 3. Models Bucket: `climate-health-models-use1-457151800683`
```
models/
├── enhanced_risk_model.pkl
├── enhanced_forecast_model.pkl
├── enhanced_scaler.joblib
└── enhanced_models_metadata.json
```

## Migration Steps

### Step 1: Save Your Models Locally

```bash
cd backend
python save_enhanced_models.py
```

This will create model files in `backend/models/` directory.

### Step 2: Run the Migration Script

```bash
cd backend
python migrate_data_to_s3.py
```

This script will:
- Upload all CSV files from `backend/data/raw/` to S3
- Upload any processed data files to S3
- Upload all model files to S3
- Verify the migration was successful
- Display statistics for each bucket

### Step 3: Test the Integration

```bash
cd backend
python test_s3_integration.py
```

This will run comprehensive tests to ensure:
- S3 storage operations work correctly
- Data can be loaded from S3
- Models can be loaded from S3
- All services are functioning properly

## Using S3 Services in Your Code

### Data Service Example

```python
from app.services.data_service import data_service

# Load data from S3
climate_df = data_service.load_climate_data()
health_df = data_service.load_health_data(location_id='KA')
locations_df = data_service.load_locations()

# Save data to S3
data_service.save_processed_climate_data(processed_df)
data_service.save_predictions(predictions_list)

# Get storage statistics
stats = data_service.get_storage_stats()
```

### Model Service Example

```python
from app.services.model_service import model_service

# Load models from S3
risk_model = model_service.load_risk_model()
forecast_model = model_service.load_forecast_model()
scaler = model_service.load_scaler()

# Save models to S3
model_service.save_risk_model(trained_model)
model_service.save_scaler(fitted_scaler)

# List available models
models = model_service.list_available_models()
```

### Direct S3 Storage Example

```python
from app.utils.s3_storage import s3_storage

# CSV operations
df = pd.DataFrame({'col1': [1, 2], 'col2': [3, 4]})
s3_storage.save_csv_to_s3(df, 'processed/my_data.csv')
loaded_df = s3_storage.load_csv_from_s3('processed/my_data.csv')

# JSON operations
data = {'key': 'value', 'number': 42}
s3_storage.save_json_to_s3(data, 'processed/my_data.json')
loaded_data = s3_storage.load_json_from_s3('processed/my_data.json')

# File operations
s3_storage.upload_file_to_s3('/local/path/file.csv', 'raw/file.csv')
s3_storage.download_file_from_s3('raw/file.csv', '/local/path/file.csv')

# List and check
objects = s3_storage.list_objects('predictions/')
exists = s3_storage.object_exists('raw/climate_data.csv')
```

## Environment Variables

Create a `.env` file in the `backend/` directory:

```env
# AWS Configuration
AWS_REGION=us-east-1
AWS_RAW_DATA_BUCKET=climate-health-raw-data-sharvaj
AWS_PROCESSED_DATA_BUCKET=climate-health-processed-data-sharvaj
AWS_MODELS_BUCKET=climate-health-models-use1-457151800683

# Enable S3 storage
USE_S3_STORAGE=true

# SageMaker Configuration
SAGEMAKER_ENDPOINT=climate-health-endpoint
SAGEMAKER_REGION=us-east-1
```

## Verification Commands

```bash
# Check bucket contents
aws s3 ls s3://climate-health-raw-data-sharvaj/raw/
aws s3 ls s3://climate-health-processed-data-sharvaj/processed/
aws s3 ls s3://climate-health-models-use1-457151800683/models/

# Get bucket sizes
aws s3 ls s3://climate-health-raw-data-sharvaj --recursive --summarize

# Download a specific file
aws s3 cp s3://climate-health-raw-data-sharvaj/raw/climate_data.csv ./local_copy.csv
```

## Troubleshooting

### Issue: Import errors for boto3
**Solution:** Install required packages
```bash
pip install boto3 botocore
```

### Issue: Access denied to S3 bucket
**Solution:** Check AWS credentials and IAM permissions
```bash
aws sts get-caller-identity
aws s3 ls  # Should list your buckets
```

### Issue: Models not found after migration
**Solution:** Ensure models exist locally first
```bash
cd backend
python save_enhanced_models.py
python migrate_data_to_s3.py
```

### Issue: Data files not found
**Solution:** Check your data directory structure
```bash
ls -la backend/data/raw/
```

## Best Practices

1. **Always test after migration**: Run `test_s3_integration.py` after any changes
2. **Use environment variables**: Never hardcode bucket names or credentials
3. **Monitor costs**: Check AWS billing dashboard regularly
4. **Set up lifecycle policies**: Archive old data to Glacier after 90 days
5. **Enable versioning**: For critical data buckets
6. **Use CloudWatch**: Monitor S3 access patterns and errors

## Next Steps

After successful migration:

1. ✅ Update application routes to use `data_service` and `model_service`
2. ✅ Test all API endpoints with S3 storage
3. ✅ Set up Lambda functions to use S3 data
4. ✅ Configure SageMaker to use models from S3
5. ✅ Set up monitoring and alerts
6. ✅ Remove local data files (after verification)

## Support

If you encounter issues:
1. Check the test output from `test_s3_integration.py`
2. Review AWS CloudWatch logs
3. Verify IAM permissions
4. Check bucket names match your configuration
