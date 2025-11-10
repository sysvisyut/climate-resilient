#!/usr/bin/env python3
"""
AWS Glue Deployment Script
Automates the deployment of Glue jobs, workflows, and related infrastructure
"""

import boto3
import json
import os
import sys
from pathlib import Path
from botocore.exceptions import ClientError
from dotenv import load_dotenv

# Configuration
PROJECT_ROOT = Path(__file__).parent.parent
ETL_JOBS_DIR = PROJECT_ROOT / "etl-jobs"
WORKFLOWS_DIR = PROJECT_ROOT / "workflows"

# Load environment variables from .env file
env_file = PROJECT_ROOT / '.env'
print(f"Loading .env from: {env_file}")
print(f".env exists: {env_file.exists()}")
load_dotenv(env_file)

# Read configuration from environment variables
AWS_REGION = os.getenv('AWS_REGION')
AWS_ACCOUNT_ID = os.getenv('AWS_ACCOUNT_ID')
GLUE_ROLE_NAME = os.getenv('GLUE_ROLE_NAME', 'AWSGlueServiceRole-ClimateHealth')
RDS_CONNECTION_NAME = 'climate-health-rds-connection'

# S3 Buckets from environment variables
S3_RAW_BUCKET = os.getenv('S3_RAW_BUCKET')
S3_PROCESSED_BUCKET = os.getenv('S3_PROCESSED_BUCKET')
S3_SCRIPTS_BUCKET = os.getenv('S3_SCRIPTS_BUCKET')
S3_TEMP_BUCKET = os.getenv('S3_TEMP_BUCKET')
S3_METRICS_BUCKET = os.getenv('S3_METRICS_BUCKET')

S3_BUCKETS = {
    'raw-data': S3_RAW_BUCKET,
    'processed-data': S3_PROCESSED_BUCKET,
    'glue-scripts': S3_SCRIPTS_BUCKET,
    'glue-temp': S3_TEMP_BUCKET,
    'glue-logs': S3_METRICS_BUCKET
}

# RDS Configuration from environment variables
DB_HOST = os.getenv('DB_HOST')
DB_PORT = os.getenv('DB_PORT', '5432')
DB_NAME = os.getenv('DB_NAME', 'climate_health')
DB_USER = os.getenv('DB_USER', 'admin')
DB_PASSWORD = os.getenv('DB_PASSWORD')

RDS_CONFIG = {
    'host': DB_HOST,
    'port': DB_PORT,
    'database': DB_NAME,
    'username': DB_USER,
    'password': DB_PASSWORD
}

# Debug: Print loaded configuration
print("\n=== Loaded Configuration ===")
print(f"AWS_REGION: {AWS_REGION}")
print(f"AWS_ACCOUNT_ID: {AWS_ACCOUNT_ID}")
print(f"S3_RAW_BUCKET: {S3_RAW_BUCKET}")
print(f"S3_PROCESSED_BUCKET: {S3_PROCESSED_BUCKET}")
print(f"S3_SCRIPTS_BUCKET: {S3_SCRIPTS_BUCKET}")
print(f"S3_TEMP_BUCKET: {S3_TEMP_BUCKET}")
print(f"S3_METRICS_BUCKET: {S3_METRICS_BUCKET}")
print(f"DB_HOST: {DB_HOST}")
print(f"GLUE_ROLE_NAME: {GLUE_ROLE_NAME}")
print("============================\n")

# Validate required variables
if not AWS_REGION or not S3_RAW_BUCKET:
    print("ERROR: Required environment variables not loaded!")
    print("Make sure .env file exists with all required variables")
    sys.exit(1)

# Initialize AWS clients with the loaded region
glue_client = boto3.client('glue', region_name=AWS_REGION)
s3_client = boto3.client('s3', region_name=AWS_REGION)
rds_client = boto3.client('rds', region_name=AWS_REGION)
secretsmanager_client = boto3.client('secretsmanager', region_name=AWS_REGION)
iam_client = boto3.client('iam', region_name=AWS_REGION)


def print_section(title):
    """Print a formatted section header"""
    print(f"\n{'='*80}")
    print(f" {title}")
    print(f"{'='*80}\n")


def create_s3_buckets():
    """Create required S3 buckets if they don't exist"""
    print_section("Creating S3 Buckets")
    
    for bucket_type, bucket_name in S3_BUCKETS.items():
        try:
            s3_client.head_bucket(Bucket=bucket_name)
            print(f"✓ Bucket '{bucket_name}' already exists")
        except ClientError as e:
            error_code = e.response['Error']['Code']
            if error_code == '404':
                try:
                    if AWS_REGION == 'us-east-1':
                        s3_client.create_bucket(Bucket=bucket_name)
                    else:
                        s3_client.create_bucket(
                            Bucket=bucket_name,
                            CreateBucketConfiguration={'LocationConstraint': AWS_REGION}
                        )
                    print(f"✓ Created bucket '{bucket_name}'")
                    
                    # Enable versioning for critical buckets
                    if bucket_type in ['raw-data', 'processed-data']:
                        s3_client.put_bucket_versioning(
                            Bucket=bucket_name,
                            VersioningConfiguration={'Status': 'Enabled'}
                        )
                        print(f"  - Enabled versioning")
                    
                except ClientError as create_error:
                    print(f"✗ Failed to create bucket '{bucket_name}': {create_error}")
                    return False
            else:
                print(f"✗ Error checking bucket '{bucket_name}': {e}")
                return False
    
    return True


def upload_glue_scripts():
    """Upload Glue ETL job scripts to S3"""
    print_section("Uploading Glue Scripts to S3")
    
    scripts_bucket = S3_BUCKETS['glue-scripts']
    
    for script_file in ETL_JOBS_DIR.glob("*.py"):
        try:
            s3_key = f"etl-jobs/{script_file.name}"
            s3_client.upload_file(
                str(script_file),
                scripts_bucket,
                s3_key
            )
            print(f"✓ Uploaded {script_file.name} to s3://{scripts_bucket}/{s3_key}")
        except ClientError as e:
            print(f"✗ Failed to upload {script_file.name}: {e}")
            return False
    
    return True


def create_glue_role():
    """Create IAM role for Glue if it doesn't exist"""
    print_section("Creating IAM Role for Glue")
    
    trust_policy = {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Effect": "Allow",
                "Principal": {
                    "Service": "glue.amazonaws.com"
                },
                "Action": "sts:AssumeRole"
            }
        ]
    }
    
    try:
        iam_client.get_role(RoleName=GLUE_ROLE_NAME)
        print(f"✓ Role '{GLUE_ROLE_NAME}' already exists")
    except ClientError as e:
        if e.response['Error']['Code'] == 'NoSuchEntity':
            try:
                iam_client.create_role(
                    RoleName=GLUE_ROLE_NAME,
                    AssumeRolePolicyDocument=json.dumps(trust_policy),
                    Description='Role for AWS Glue to access S3 and RDS'
                )
                print(f"✓ Created role '{GLUE_ROLE_NAME}'")
                
                # Attach managed policies
                policies = [
                    'arn:aws:iam::aws:policy/service-role/AWSGlueServiceRole',
                    'arn:aws:iam::aws:policy/AmazonS3FullAccess',
                    'arn:aws:iam::aws:policy/CloudWatchLogsFullAccess'
                ]
                
                for policy_arn in policies:
                    iam_client.attach_role_policy(
                        RoleName=GLUE_ROLE_NAME,
                        PolicyArn=policy_arn
                    )
                    print(f"  - Attached policy {policy_arn.split('/')[-1]}")
                
            except ClientError as create_error:
                print(f"✗ Failed to create role: {create_error}")
                return False
        else:
            print(f"✗ Error checking role: {e}")
            return False
    
    return True


def create_glue_connection():
    """Create Glue connection to RDS PostgreSQL"""
    print_section("Creating Glue Connection to RDS")
    
    if not RDS_CONFIG['host'] or not RDS_CONFIG['password']:
        print("⚠ RDS_HOST and RDS_PASSWORD environment variables must be set")
        print("  Skipping connection creation...")
        return True
    
    connection_input = {
        'Name': RDS_CONNECTION_NAME,
        'Description': 'Connection to RDS PostgreSQL for climate health data',
        'ConnectionType': 'JDBC',
        'ConnectionProperties': {
            'JDBC_CONNECTION_URL': f"jdbc:postgresql://{RDS_CONFIG['host']}:{RDS_CONFIG['port']}/{RDS_CONFIG['database']}",
            'USERNAME': RDS_CONFIG['username'],
            'PASSWORD': RDS_CONFIG['password']
        }
    }
    
    try:
        glue_client.get_connection(Name=RDS_CONNECTION_NAME)
        print(f"✓ Connection '{RDS_CONNECTION_NAME}' already exists")
        # Update connection
        glue_client.update_connection(
            Name=RDS_CONNECTION_NAME,
            ConnectionInput=connection_input
        )
        print(f"  - Updated connection configuration")
    except ClientError as e:
        if e.response['Error']['Code'] == 'EntityNotFoundException':
            try:
                glue_client.create_connection(ConnectionInput=connection_input)
                print(f"✓ Created connection '{RDS_CONNECTION_NAME}'")
            except ClientError as create_error:
                print(f"✗ Failed to create connection: {create_error}")
                return False
        else:
            print(f"✗ Error checking connection: {e}")
            return False
    
    return True


def create_glue_job(config_file):
    """Create or update a Glue job from configuration"""
    with open(config_file, 'r') as f:
        config = json.load(f)
    
    # Update bucket names in configuration
    if 'Command' in config and 'ScriptLocation' in config['Command']:
        script_loc = config['Command']['ScriptLocation']
        # Replace old bucket name with new one
        script_loc = script_loc.replace('climate-health-glue-scripts', S3_SCRIPTS_BUCKET)
        config['Command']['ScriptLocation'] = script_loc
    
    # Update default arguments with correct bucket names
    if 'DefaultArguments' in config:
        for key, value in config['DefaultArguments'].items():
            if isinstance(value, str):
                value = value.replace('climate-health-raw-data', S3_RAW_BUCKET)
                value = value.replace('climate-health-processed-data', S3_PROCESSED_BUCKET)
                value = value.replace('climate-health-glue-temp', S3_TEMP_BUCKET)
                value = value.replace('climate-health-glue-logs', S3_METRICS_BUCKET)
                config['DefaultArguments'][key] = value
    
    job_name = config['Name']
    
    try:
        glue_client.get_job(JobName=job_name)
        # Job exists, update it
        # Build JobUpdate payload only with present values to avoid None parameters
        job_update = {
            'Description': config.get('Description'),
            'Role': config.get('Role'),
            'ExecutionProperty': config.get('ExecutionProperty'),
            'Command': config.get('Command'),
            'DefaultArguments': config.get('DefaultArguments'),
            'MaxRetries': config.get('MaxRetries'),
            'Timeout': config.get('Timeout'),
            'GlueVersion': config.get('GlueVersion')
        }
        # Optional compute settings
        if config.get('MaxCapacity') is not None:
            job_update['MaxCapacity'] = config.get('MaxCapacity')
        if config.get('NumberOfWorkers') is not None:
            job_update['NumberOfWorkers'] = config.get('NumberOfWorkers')
        if config.get('WorkerType') is not None:
            job_update['WorkerType'] = config.get('WorkerType')

        glue_client.update_job(JobName=job_name, JobUpdate=job_update)
        print(f"✓ Updated job '{job_name}'")
    except ClientError as e:
        if e.response['Error']['Code'] == 'EntityNotFoundException':
            # Job doesn't exist, create it
            glue_client.create_job(**config)
            print(f"✓ Created job '{job_name}'")
        else:
            print(f"✗ Failed to create/update job '{job_name}': {e}")
            return False
    
    return True


def create_glue_workflow():
    """Create or update the Glue workflow"""
    print_section("Creating Glue Workflow")
    
    workflow_file = WORKFLOWS_DIR / "workflow-definition.json"
    with open(workflow_file, 'r') as f:
        workflow_config = json.load(f)
    
    workflow_name = workflow_config['Name']
    
    try:
        glue_client.get_workflow(Name=workflow_name)
        print(f"✓ Workflow '{workflow_name}' already exists")
    except ClientError as e:
        if e.response['Error']['Code'] == 'EntityNotFoundException':
            try:
                glue_client.create_workflow(
                    Name=workflow_name,
                    Description=workflow_config['Description'],
                    DefaultRunProperties=workflow_config.get('DefaultRunProperties', {}),
                    MaxConcurrentRuns=workflow_config.get('MaxConcurrentRuns', 1),
                    Tags=workflow_config.get('Tags', {})
                )
                print(f"✓ Created workflow '{workflow_name}'")
            except ClientError as create_error:
                print(f"✗ Failed to create workflow: {create_error}")
                return False
        else:
            print(f"✗ Error checking workflow: {e}")
            return False
    
    return True


def main():
    """Main deployment function"""
    print(f"\n{'#'*80}")
    print(f"# AWS Glue Deployment Script")
    print(f"# Region: {AWS_REGION}")
    print(f"{'#'*80}\n")
    
    steps = [
        ("Creating S3 Buckets", create_s3_buckets),
        ("Uploading Glue Scripts", upload_glue_scripts),
        ("Creating IAM Role", create_glue_role),
        ("Creating Glue Connection", create_glue_connection),
    ]
    
    # Execute initial steps
    for step_name, step_func in steps:
        if not step_func():
            print(f"\n✗ Deployment failed at: {step_name}")
            sys.exit(1)
    
    # Create Glue jobs
    print_section("Creating Glue Jobs")
    for config_file in WORKFLOWS_DIR.glob("job-config-*.json"):
        if not create_glue_job(config_file):
            print(f"\n✗ Deployment failed creating jobs")
            sys.exit(1)
    
    # Create workflow
    if not create_glue_workflow():
        print(f"\n✗ Deployment failed creating workflow")
        sys.exit(1)
    
    print_section("Deployment Complete!")
    print("✓ All resources deployed successfully")
    print("\nNext steps:")
    print("1. Verify RDS database schema is created")
    print("2. Upload sample data to S3 raw-data bucket")
    print("3. Start the Glue workflow manually or wait for scheduled trigger")
    print(f"\nTo run workflow: aws glue start-workflow-run --name climate-health-etl-workflow --region {AWS_REGION}")


if __name__ == "__main__":
    main()
