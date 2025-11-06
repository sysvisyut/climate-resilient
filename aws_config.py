"""
AWS Configuration File
Store all AWS resource identifiers and settings here
"""

# AWS Region
AWS_REGION = "ap-south-1"  # Mumbai

# S3 Bucket Names (Replace with your actual bucket names)
S3_RAW_DATA_BUCKET = "climate-health-raw-data-YOUR-ID"
S3_PROCESSED_DATA_BUCKET = "climate-health-processed-data-YOUR-ID"
S3_MODELS_BUCKET = "climate-health-models-YOUR-ID"

# RDS Database Configuration
RDS_ENDPOINT = "climate-health-db.XXXXXXXXXX.ap-south-1.rds.amazonaws.com"  # Replace after RDS creation
RDS_PORT = 5432
RDS_DATABASE = "climate_health"
RDS_USERNAME = "postgres"
# Password will be retrieved from Secrets Manager

# Secrets Manager Secret Names
SECRET_DB_CREDENTIALS = "climate-health/db/credentials"
SECRET_JWT_SECRET = "climate-health/api/jwt-secret"

# SNS Topic ARN (Replace after SNS creation)
SNS_ALERTS_TOPIC_ARN = "arn:aws:sns:ap-south-1:ACCOUNT-ID:climate-health-alerts"

# Lambda Function Names
LAMBDA_DATA_PROCESSOR = "climate-health-data-processor"
LAMBDA_RISK_PREDICTOR = "climate-health-risk-predictor"
LAMBDA_ALERT_SENDER = "climate-health-alert-sender"

# API Gateway Configuration
API_GATEWAY_NAME = "climate-health-api"
API_GATEWAY_STAGE = "prod"

# SageMaker Configuration
SAGEMAKER_ROLE_ARN = "arn:aws:iam::ACCOUNT-ID:role/SageMakerExecutionRole"
SAGEMAKER_INSTANCE_TYPE = "ml.t3.medium"  # Free Tier eligible

# Free Tier Limits (for monitoring)
FREE_TIER_LIMITS = {
    "RDS_HOURS_PER_MONTH": 750,
    "S3_STORAGE_GB": 5,
    "LAMBDA_REQUESTS_PER_MONTH": 1000000,
    "LAMBDA_COMPUTE_SECONDS": 400000,
    "SNS_NOTIFICATIONS": 1000
}
