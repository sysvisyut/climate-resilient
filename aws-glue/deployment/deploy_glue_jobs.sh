#!/bin/bash

# AWS Glue Deployment Script - Shell version
# This script deploys Glue jobs and workflows using AWS CLI

set -e  # Exit on error

# Configuration
AWS_REGION="${AWS_REGION:-us-east-1}"
ACCOUNT_ID="${AWS_ACCOUNT_ID:-<YOUR_ACCOUNT_ID>}"
GLUE_ROLE_ARN="arn:aws:iam::${ACCOUNT_ID}:role/AWSGlueServiceRole"

# S3 Buckets
SCRIPTS_BUCKET="climate-health-glue-scripts"
RAW_DATA_BUCKET="climate-health-raw-data"
PROCESSED_DATA_BUCKET="climate-health-processed-data"
TEMP_BUCKET="climate-health-glue-temp"
LOGS_BUCKET="climate-health-glue-logs"

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo "======================================================================"
echo "AWS Glue Deployment for Climate-Resilient Healthcare System"
echo "======================================================================"

# Check AWS CLI is installed
if ! command -v aws &> /dev/null; then
    echo -e "${RED}✗ AWS CLI is not installed${NC}"
    echo "Please install AWS CLI: https://aws.amazon.com/cli/"
    exit 1
fi

# Check AWS credentials
echo -e "\nVerifying AWS credentials..."
if ! aws sts get-caller-identity --region "$AWS_REGION" &> /dev/null; then
    echo -e "${RED}✗ AWS credentials not configured${NC}"
    echo "Please run: aws configure"
    exit 1
fi

CALLER_IDENTITY=$(aws sts get-caller-identity --region "$AWS_REGION")
echo -e "${GREEN}✓ AWS credentials verified${NC}"
echo "$CALLER_IDENTITY"

# Function to create S3 bucket
create_bucket() {
    local bucket_name=$1
    
    if aws s3 ls "s3://${bucket_name}" --region "$AWS_REGION" 2>&1 | grep -q 'NoSuchBucket'; then
        echo -e "  Creating bucket: ${bucket_name}"
        if [ "$AWS_REGION" = "us-east-1" ]; then
            aws s3 mb "s3://${bucket_name}" --region "$AWS_REGION"
        else
            aws s3 mb "s3://${bucket_name}" --region "$AWS_REGION" --create-bucket-configuration LocationConstraint="$AWS_REGION"
        fi
        echo -e "${GREEN}  ✓ Created bucket: ${bucket_name}${NC}"
    else
        echo -e "${YELLOW}  ⚠ Bucket ${bucket_name} already exists${NC}"
    fi
}

# Step 1: Create S3 buckets
echo -e "\n1. Creating S3 buckets..."
create_bucket "$SCRIPTS_BUCKET"
create_bucket "$RAW_DATA_BUCKET"
create_bucket "$PROCESSED_DATA_BUCKET"
create_bucket "$TEMP_BUCKET"
create_bucket "$LOGS_BUCKET"

# Step 2: Upload Glue scripts to S3
echo -e "\n2. Uploading Glue ETL scripts to S3..."
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../etl-jobs" && pwd)"

for script in "$SCRIPT_DIR"/*.py; do
    script_name=$(basename "$script")
    echo -e "  Uploading ${script_name}..."
    aws s3 cp "$script" "s3://${SCRIPTS_BUCKET}/etl-jobs/${script_name}" --region "$AWS_REGION"
    echo -e "${GREEN}  ✓ Uploaded ${script_name}${NC}"
done

# Step 3: Create Glue connection (manual step required)
echo -e "\n3. Creating Glue RDS connection..."
echo -e "${YELLOW}  ⚠ Please create the RDS connection manually in AWS Glue Console:${NC}"
echo "    - Connection name: climate-health-rds-connection"
echo "    - Connection type: JDBC"
echo "    - JDBC URL: jdbc:postgresql://YOUR_RDS_ENDPOINT:5432/climate_health"
echo "    - Username/Password: From AWS Secrets Manager"
echo "    - VPC, Subnet, and Security Group: Your RDS configuration"

# Step 4: Create Glue jobs
echo -e "\n4. Creating Glue jobs..."
CONFIG_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../workflows" && pwd)"

# Replace ACCOUNT_ID in config files
for config in "$CONFIG_DIR"/job-config-*.json; do
    config_name=$(basename "$config")
    job_name=$(jq -r '.Name' "$config" | sed "s/<ACCOUNT_ID>/${ACCOUNT_ID}/g")
    
    echo -e "  Creating job: ${job_name}..."
    
    # Create temporary config with replaced values
    temp_config=$(mktemp)
    sed "s/<ACCOUNT_ID>/${ACCOUNT_ID}/g" "$config" > "$temp_config"
    
    # Try to create or update job
    if aws glue get-job --job-name "$job_name" --region "$AWS_REGION" &> /dev/null; then
        echo -e "${YELLOW}  ⚠ Job ${job_name} already exists, updating...${NC}"
        # Update job (requires different parameters)
        # aws glue update-job --job-name "$job_name" --job-update file://"$temp_config" --region "$AWS_REGION"
    else
        aws glue create-job --cli-input-json file://"$temp_config" --region "$AWS_REGION"
        echo -e "${GREEN}  ✓ Created job: ${job_name}${NC}"
    fi
    
    rm "$temp_config"
done

# Step 5: Create workflow
echo -e "\n5. Creating Glue workflow..."
WORKFLOW_NAME="climate-health-etl-workflow"

if aws glue get-workflow --name "$WORKFLOW_NAME" --region "$AWS_REGION" &> /dev/null; then
    echo -e "${YELLOW}  ⚠ Workflow ${WORKFLOW_NAME} already exists${NC}"
else
    aws glue create-workflow \
        --name "$WORKFLOW_NAME" \
        --description "Complete ETL workflow for processing climate and health data" \
        --max-concurrent-runs 1 \
        --region "$AWS_REGION"
    echo -e "${GREEN}  ✓ Created workflow: ${WORKFLOW_NAME}${NC}"
fi

# Step 6: Create triggers
echo -e "\n6. Creating triggers..."

# Daily scheduled trigger
TRIGGER_NAME="climate-health-daily-trigger"
if aws glue get-trigger --name "$TRIGGER_NAME" --region "$AWS_REGION" &> /dev/null; then
    echo -e "${YELLOW}  ⚠ Trigger ${TRIGGER_NAME} already exists${NC}"
else
    aws glue create-trigger \
        --name "$TRIGGER_NAME" \
        --workflow-name "$WORKFLOW_NAME" \
        --type SCHEDULED \
        --schedule "cron(0 2 * * ? *)" \
        --actions JobName=climate-health-process-locations \
        --start-on-creation \
        --region "$AWS_REGION"
    echo -e "${GREEN}  ✓ Created trigger: ${TRIGGER_NAME}${NC}"
fi

# Summary
echo -e "\n======================================================================"
echo -e "${GREEN}✓ Deployment completed successfully!${NC}"
echo -e "======================================================================"
echo -e "\nNext steps:"
echo "1. Update the RDS connection details in AWS Glue Console"
echo "2. Upload your raw data CSV files to S3:"
echo "   aws s3 cp backend/data/raw/locations.csv s3://${RAW_DATA_BUCKET}/"
echo "   aws s3 cp backend/data/raw/climate_data.csv s3://${RAW_DATA_BUCKET}/"
echo "   aws s3 cp backend/data/raw/health_data.csv s3://${RAW_DATA_BUCKET}/"
echo "   aws s3 cp backend/data/raw/hospital_data.csv s3://${RAW_DATA_BUCKET}/"
echo "3. Test run the workflow:"
echo "   aws glue start-workflow-run --name ${WORKFLOW_NAME} --region ${AWS_REGION}"
echo "4. Monitor job execution:"
echo "   aws glue get-workflow-run-properties --name ${WORKFLOW_NAME} --region ${AWS_REGION}"
