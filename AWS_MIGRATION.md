# AWS Migration Guide for Climate-Resilient Healthcare System

This guide outlines how to migrate the local Climate-Resilient Healthcare System to AWS cloud infrastructure.

## Architecture Overview

The system will use the following AWS services:

1. **Amazon EC2** - For hosting the application server
2. **Amazon RDS (PostgreSQL)** - For replacing the local SQLite database
3. **Amazon S3** - For storing data files and ML models
4. **Amazon API Gateway** - For managing API endpoints
5. **AWS Lambda** - For serverless backend processing
6. **Amazon SageMaker** - For ML model training and hosting
7. **AWS IAM** - For identity and access management
8. **AWS Secrets Manager** - For securely storing credentials
9. **Amazon SNS** - For alerts and notifications
10. **AWS Glue** - For ETL processing

## Migration Steps

### 1. Database Migration (SQLite → RDS PostgreSQL)

1. Create a PostgreSQL instance in Amazon RDS:
   - Use the AWS console to create a PostgreSQL DB instance
   - Configure security groups to allow connections from your application

2. Modify database models:
   - Update database connection string in `backend/app/models/database.py`
   - Change from SQLite to PostgreSQL:
   ```python
   # Replace
   SQLALCHEMY_DATABASE_URL = "sqlite:///./climate_health.db"
   
   # With
   SQLALCHEMY_DATABASE_URL = "postgresql://username:password@your-rds-endpoint:5432/climate_health"
   ```

3. Install PostgreSQL driver:
   - Add `psycopg2-binary` to `requirements.txt`

4. Migrate data:
   - Create a migration script that reads from SQLite and writes to PostgreSQL
   - Update any SQLite-specific queries to be PostgreSQL compatible

### 2. Storage Migration (Local Files → S3)

1. Create S3 buckets:
   - Raw data bucket: `climate-health-raw-data`
   - Processed data bucket: `climate-health-processed-data`
   - ML models bucket: `climate-health-models`

2. Update data storage code:
   - Install boto3: `pip install boto3`
   - Modify data saving/loading functions to use S3:

   ```python
   import boto3
   
   s3 = boto3.client('s3')
   
   # Replace local file operations like:
   # df.to_csv(os.path.join(save_path, "file.csv"))
   
   # With S3 operations:
   def save_to_s3(df, bucket, key):
       csv_buffer = StringIO()
       df.to_csv(csv_buffer)
       s3.put_object(Bucket=bucket, Key=key, Body=csv_buffer.getvalue())
   
   # And for loading:
   def load_from_s3(bucket, key):
       obj = s3.get_object(Bucket=bucket, Key=key)
       return pd.read_csv(io.BytesIO(obj['Body'].read()))
   ```

3. Update the model saving/loading code to use S3 for model artifacts

### 3. API Layer Migration (FastAPI → API Gateway + Lambda)

1. Structure the application for Lambda:
   - Split the FastAPI app into Lambda function handlers
   - Create separate Lambda functions for different endpoint groups (auth, data, predictions)

2. Deploy to Lambda:
   - Package each function with its dependencies
   - Configure environment variables for database connections and S3 buckets
   - Set appropriate IAM roles and permissions

3. Set up API Gateway:
   - Create a new REST API
   - Define resources and methods that map to your Lambda functions
   - Configure authentication and authorization
   - Set up custom domain name if needed

### 4. ML Infrastructure (Local Scripts → SageMaker)

1. Migrate ML training scripts to SageMaker:
   - Adapt `backend/app/models/ml_models.py` to SageMaker training script format
   - Create SageMaker training jobs for XGBoost and LSTM models

2. Use SageMaker for model hosting:
   - Deploy trained models as SageMaker endpoints
   - Update prediction code to call SageMaker endpoints instead of local models

3. Set up scheduled retraining jobs:
   - Use SageMaker Pipelines or AWS Step Functions to orchestrate data processing and model training

### 5. Authentication (JWT → IAM + Secrets Manager)

1. Store secrets in AWS Secrets Manager:
   - JWT secret key
   - Database credentials
   - API keys

2. Enhance authentication with AWS Cognito:
   - Set up user pools for admin and hospital users
   - Configure app clients and authentication flows
   - Update frontend to use Cognito authentication

### 6. ETL Processing (Python Scripts → AWS Glue)

1. Migrate data processing scripts to AWS Glue:
   - Convert `data_processor.py` to Glue ETL jobs
   - Configure Glue jobs to read from and write to S3

2. Set up Glue workflows:
   - Create workflows for regular data processing
   - Configure triggers based on new data or schedule

### 7. Alerting System (Console → SNS)

1. Create SNS topics:
   - Health risk alerts topic
   - Resource shortage alerts topic

2. Set up subscriptions:
   - Email notifications for admins
   - SMS notifications for urgent alerts

3. Update alerting code:
   - Replace console prints with SNS publish operations
   - Add severity levels and routing logic

## Infrastructure as Code (Optional)

Consider using AWS CloudFormation or AWS CDK to define and provision your infrastructure:

```yaml
# Example CloudFormation snippet for RDS
Resources:
  ClimateHealthDatabase:
    Type: AWS::RDS::DBInstance
    Properties:
      Engine: postgres
      DBInstanceClass: db.t3.micro
      AllocatedStorage: 20
      DBName: climate_health
      MasterUsername: !Ref DBUsername
      MasterUserPassword: !Ref DBPassword
      VPCSecurityGroups:
        - !Ref DatabaseSecurityGroup
```

## Cost Optimization

1. Use reserved instances for EC2 and RDS to reduce costs
2. Configure auto-scaling for resources based on demand
3. Set up S3 lifecycle policies to archive infrequently accessed data
4. Use SageMaker endpoints in serverless mode for infrequent predictions

## Security Considerations

1. Ensure proper IAM roles and permissions with least privilege principle
2. Enable encryption at rest for S3 buckets and RDS
3. Use VPC for network isolation
4. Set up AWS WAF to protect API Gateway endpoints
5. Implement CloudTrail for auditing and monitoring

## Monitoring and Logging

1. Set up CloudWatch dashboards and alarms
2. Configure log aggregation and analysis
3. Use X-Ray for tracing and performance monitoring
4. Set up health checks and automated recovery procedures
