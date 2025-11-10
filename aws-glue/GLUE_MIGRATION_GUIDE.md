# AWS Glue Migration Guide - Step-by-Step Implementation

## Overview

This guide provides **exact, detailed steps** to migrate your Climate-Resilient Healthcare System's ETL processing from local Python scripts (`data_processor.py`) to AWS Glue. This is part of your AWS migration project.

## What We're Migrating

**Current State (Local):**
- `backend/app/utils/data_processor.py` - Processes CSV files and loads into SQLite
- Runs on local machine manually or via cron
- Limited scalability and monitoring

**Target State (AWS Glue):**
- 5 Glue ETL jobs processing data in parallel
- Automated workflow with job dependencies
- Scheduled and event-driven triggers
- Reads from S3, writes to RDS PostgreSQL
- Cloud-scale processing with monitoring

---

## Prerequisites Checklist

Before starting, ensure you have:

- [ ] AWS Account with admin access
- [ ] AWS CLI installed and configured (`aws configure`)
- [ ] Python 3.8+ installed
- [ ] RDS PostgreSQL database created (see AWS_MIGRATION.md Step 1)
- [ ] VPC, Subnets, and Security Groups configured
- [ ] IAM role for Glue: `AWSGlueServiceRole` with policies:
  - `AWSGlueServiceRole` (managed policy)
  - `AmazonS3FullAccess` (or scoped S3 access)
  - `AmazonRDSFullAccess` (or scoped RDS access)
  - `CloudWatchLogsFullAccess`

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                         AWS Glue Workflow                       │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌──────────────┐                                              │
│  │   Trigger    │  (Daily 2 AM UTC or S3 Event)                │
│  └──────┬───────┘                                              │
│         │                                                       │
│         ▼                                                       │
│  ┌──────────────────────────────────────────┐                 │
│  │  Job 1: Process Locations (Master Data)  │                 │
│  └──────┬───────────────────────────────────┘                 │
│         │                                                       │
│         ├─────────────┬─────────────┬──────────────┐          │
│         ▼             ▼             ▼              ▼          │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐     │
│  │Job 2:    │  │Job 3:    │  │Job 4:    │  │          │     │
│  │Climate   │  │Health    │  │Hospital  │  │  Parallel│     │
│  │Data      │  │Data      │  │Data      │  │  Jobs   │     │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘  └──────────┘     │
│       │             │             │                            │
│       └─────────────┴─────────────┘                           │
│                     │                                          │
│                     ▼                                          │
│  ┌──────────────────────────────────────────┐                │
│  │  Job 5: Calculate Derived Metrics        │                │
│  └──────────────────────────────────────────┘                │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘

Data Flow:
S3 (Raw CSV) → Glue Jobs → RDS PostgreSQL
                         → S3 (Processed Metrics)
```

---

## Step-by-Step Implementation

### Phase 1: Pre-Deployment Setup (30 minutes)

#### Step 1.1: Create IAM Role for Glue

1. Go to AWS IAM Console → Roles → Create Role
2. Select **AWS Service** → **Glue**
3. Attach policies:
   - `AWSGlueServiceRole`
   - `AmazonS3FullAccess`
   - `AmazonRDSFullAccess`
   - `CloudWatchLogsFullAccess`
4. Name: `AWSGlueServiceRole`
5. Copy the Role ARN (you'll need it later)

#### Step 1.2: Create RDS PostgreSQL Database

If not already done:

```bash
# Via AWS CLI
aws rds create-db-instance \
    --db-instance-identifier climate-health-db \
    --db-instance-class db.t3.micro \
    --engine postgres \
    --master-username admin \
    --master-user-password <YourSecurePassword> \
    --allocated-storage 20 \
    --vpc-security-group-ids <your-security-group-id> \
    --db-subnet-group-name <your-subnet-group> \
    --publicly-accessible false \
    --backup-retention-period 7 \
    --region us-east-1
```

**Wait for database to be available (5-10 minutes)**

Check status:
```bash
aws rds describe-db-instances \
    --db-instance-identifier climate-health-db \
    --query 'DBInstances[0].DBInstanceStatus'
```

#### Step 1.3: Store Database Credentials in Secrets Manager

```bash
# Create secret for database credentials
aws secretsmanager create-secret \
    --name climate-health-db-credentials \
    --description "RDS credentials for Climate Health database" \
    --secret-string '{
        "username": "admin",
        "password": "<YourSecurePassword>",
        "engine": "postgres",
        "host": "<your-rds-endpoint>",
        "port": 5432,
        "dbname": "climate_health"
    }' \
    --region us-east-1
```

#### Step 1.4: Get Your AWS Account ID

```bash
# Get your AWS Account ID
export AWS_ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
echo "Your AWS Account ID: $AWS_ACCOUNT_ID"

# Set your region
export AWS_REGION="us-east-1"
```

---

### Phase 2: Deploy AWS Glue Infrastructure (20 minutes)

#### Step 2.1: Update Configuration Files

1. Open `aws-glue/deployment/deploy_glue_jobs.py`
2. Update line 13:
   ```python
   ACCOUNT_ID = os.getenv('AWS_ACCOUNT_ID', '<ACCOUNT_ID>')
   ```
   Replace `<ACCOUNT_ID>` with your actual account ID

3. Open each job config file in `aws-glue/workflows/` and replace `<ACCOUNT_ID>`

#### Step 2.2: Install Deployment Dependencies

```bash
cd aws-glue/deployment
pip install -r requirements.txt
```

#### Step 2.3: Run Deployment Script (Python)

```bash
# Set environment variables
export AWS_ACCOUNT_ID="<your-account-id>"
export AWS_REGION="us-east-1"

# Run deployment
python deploy_glue_jobs.py
```

**OR** use the shell script:

```bash
# Make script executable
chmod +x deploy_glue_jobs.sh

# Run deployment
./deploy_glue_jobs.sh
```

**Expected Output:**
```
======================================================================
AWS Glue Deployment for Climate-Resilient Healthcare System
======================================================================

AWS Account: 123456789012
AWS Region: us-east-1

Creating S3 buckets...
  ✓ Created bucket: climate-health-glue-scripts
  ✓ Created bucket: climate-health-raw-data
  ✓ Created bucket: climate-health-processed-data
  ✓ Created bucket: climate-health-glue-temp
  ✓ Created bucket: climate-health-glue-logs

Uploading Glue ETL scripts to S3...
  ✓ Uploaded process_locations.py
  ✓ Uploaded process_climate_data.py
  ✓ Uploaded process_health_data.py
  ✓ Uploaded process_hospital_data.py
  ✓ Uploaded calculate_derived_metrics.py

Creating Glue jobs...
  ✓ Created job: climate-health-process-locations
  ✓ Created job: climate-health-process-climate-data
  ✓ Created job: climate-health-process-health-data
  ✓ Created job: climate-health-process-hospital-data
  ✓ Created job: climate-health-calculate-metrics

Creating Glue workflow...
  ✓ Created workflow: climate-health-etl-workflow
  ✓ Created trigger: climate-health-daily-trigger

======================================================================
✓ Deployment completed successfully!
======================================================================
```

---

### Phase 3: Configure Glue Connection to RDS (15 minutes)

#### Step 3.1: Create Glue Connection in AWS Console

1. Go to **AWS Glue Console** → **Data Catalog** → **Connections**
2. Click **Create connection**
3. Fill in details:
   - **Connection name**: `climate-health-rds-connection`
   - **Connection type**: `JDBC`
   - **JDBC URL**: `jdbc:postgresql://<your-rds-endpoint>:5432/climate_health`
   - **Username**: Get from Secrets Manager or enter directly
   - **Password**: Get from Secrets Manager or enter directly
   - **VPC**: Select your RDS VPC
   - **Subnet**: Select subnet where RDS resides
   - **Security groups**: Select security group that allows Glue access to RDS

4. Click **Create connection**

#### Step 3.2: Test Connection

1. Select the connection you just created
2. Click **Test connection**
3. Select the IAM role: `AWSGlueServiceRole`
4. Click **Test connection**

**Expected**: "Successfully tested connection"

**If fails**: Check security group rules allow port 5432 from Glue subnet

---

### Phase 4: Upload Initial Data to S3 (10 minutes)

#### Step 4.1: Generate Data Locally (if not already done)

```bash
cd backend
python run_setup.py
```

This creates CSV files in `backend/data/raw/`

#### Step 4.2: Upload CSV Files to S3

```bash
# Upload raw data files
aws s3 cp backend/data/raw/locations.csv s3://climate-health-raw-data/ --region us-east-1
aws s3 cp backend/data/raw/climate_data.csv s3://climate-health-raw-data/ --region us-east-1
aws s3 cp backend/data/raw/health_data.csv s3://climate-health-raw-data/ --region us-east-1
aws s3 cp backend/data/raw/hospital_data.csv s3://climate-health-raw-data/ --region us-east-1
```

#### Step 4.3: Verify Upload

```bash
aws s3 ls s3://climate-health-raw-data/ --region us-east-1
```

**Expected Output:**
```
2025-11-05 10:30:45       1234 climate_data.csv
2025-11-05 10:30:46       5678 health_data.csv
2025-11-05 10:30:47       9012 hospital_data.csv
2025-11-05 10:30:48        456 locations.csv
```

---

### Phase 5: Initialize RDS Database Schema (10 minutes)

#### Step 5.1: Create Database Tables

You need to create tables in PostgreSQL. Connect to RDS:

```bash
# Get RDS endpoint
aws rds describe-db-instances \
    --db-instance-identifier climate-health-db \
    --query 'DBInstances[0].Endpoint.Address' \
    --output text
```

Connect using psql or pgAdmin:

```bash
psql -h <rds-endpoint> -U admin -d climate_health
```

Run this SQL:

```sql
-- Create tables
CREATE TABLE locations (
    id INTEGER PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    type VARCHAR(50) NOT NULL,
    population INTEGER,
    area DOUBLE PRECISION
);

CREATE TABLE climate_data (
    id SERIAL PRIMARY KEY,
    location_id INTEGER REFERENCES locations(id),
    date DATE NOT NULL,
    temperature DOUBLE PRECISION,
    rainfall DOUBLE PRECISION,
    humidity DOUBLE PRECISION,
    flood_probability DOUBLE PRECISION,
    cyclone_probability DOUBLE PRECISION,
    heatwave_probability DOUBLE PRECISION,
    is_projected BOOLEAN DEFAULT FALSE,
    projection_year INTEGER
);

CREATE TABLE health_data (
    id SERIAL PRIMARY KEY,
    location_id INTEGER REFERENCES locations(id),
    date DATE NOT NULL,
    dengue_cases INTEGER DEFAULT 0,
    malaria_cases INTEGER DEFAULT 0,
    heatstroke_cases INTEGER DEFAULT 0,
    diarrhea_cases INTEGER DEFAULT 0,
    is_projected BOOLEAN DEFAULT FALSE,
    projection_year INTEGER
);

CREATE TABLE hospital_data (
    id SERIAL PRIMARY KEY,
    location_id INTEGER REFERENCES locations(id),
    date DATE NOT NULL,
    total_beds INTEGER DEFAULT 0,
    available_beds INTEGER DEFAULT 0,
    doctors INTEGER DEFAULT 0,
    nurses INTEGER DEFAULT 0,
    iv_fluids_stock INTEGER DEFAULT 0,
    antibiotics_stock INTEGER DEFAULT 0,
    antipyretics_stock INTEGER DEFAULT 0,
    is_projected BOOLEAN DEFAULT FALSE,
    projection_year INTEGER
);

-- Create indexes for better performance
CREATE INDEX idx_climate_location_date ON climate_data(location_id, date);
CREATE INDEX idx_health_location_date ON health_data(location_id, date);
CREATE INDEX idx_hospital_location_date ON hospital_data(location_id, date);
```

---

### Phase 6: Test Run the Glue Workflow (20 minutes)

#### Step 6.1: Start Workflow Manually

```bash
# Start the workflow
aws glue start-workflow-run \
    --name climate-health-etl-workflow \
    --region us-east-1
```

**Expected Output:**
```json
{
    "RunId": "wr_abc123..."
}
```

Copy the `RunId` for monitoring.

#### Step 6.2: Monitor Workflow Execution

```bash
# Check workflow status
aws glue get-workflow-run \
    --name climate-health-etl-workflow \
    --run-id <your-run-id> \
    --region us-east-1
```

**OR** use AWS Console:
1. Go to **AWS Glue Console** → **Workflows**
2. Click on `climate-health-etl-workflow`
3. View the **Run history** tab
4. Watch jobs execute in the graph view

#### Step 6.3: Monitor Individual Jobs

```bash
# List all job runs
aws glue get-job-runs \
    --job-name climate-health-process-locations \
    --region us-east-1
```

View logs in CloudWatch:
1. Go to **CloudWatch Console** → **Log groups**
2. Find `/aws-glue/jobs/logs-v2/`
3. View job-specific log streams

---

### Phase 7: Verify Data in RDS (10 minutes)

#### Step 7.1: Connect to RDS and Query Data

```bash
psql -h <rds-endpoint> -U admin -d climate_health
```

Run verification queries:

```sql
-- Check locations loaded
SELECT COUNT(*) FROM locations;
-- Expected: 36 (all Indian states + UTs)

-- Check climate data
SELECT COUNT(*) FROM climate_data;
-- Expected: Thousands of records

-- Check health data
SELECT COUNT(*) FROM health_data;

-- Check hospital data
SELECT COUNT(*) FROM hospital_data;

-- Sample query to see data
SELECT l.name, c.date, c.temperature, h.dengue_cases
FROM locations l
JOIN climate_data c ON l.id = c.location_id
JOIN health_data h ON c.location_id = h.location_id AND c.date = h.date
LIMIT 10;
```

#### Step 7.2: Verify Processed Metrics in S3

```bash
# Check processed data
aws s3 ls s3://climate-health-processed-data/metrics/ --recursive --region us-east-1
```

**Expected folders:**
- `current_health_risks/`
- `current_hospital_resources/`
- `resilience_scores/`
- `current_health_risks_json/`
- `current_hospital_resources_json/`
- `resilience_scores_json/`

Download a sample:
```bash
aws s3 cp s3://climate-health-processed-data/metrics/resilience_scores_json/ . --recursive
```

---

### Phase 8: Set Up Automated Triggers (10 minutes)

#### Step 8.1: Verify Daily Scheduled Trigger

Already created by deployment script. Verify:

```bash
aws glue get-trigger \
    --name climate-health-daily-trigger \
    --region us-east-1
```

Should show:
- Type: `SCHEDULED`
- Schedule: `cron(0 2 * * ? *)`  (2 AM UTC daily)
- State: `ACTIVATED`

#### Step 8.2: Create S3 Event Trigger (Optional)

For real-time processing when new files arrive:

```bash
# Create S3 event notification
aws s3api put-bucket-notification-configuration \
    --bucket climate-health-raw-data \
    --notification-configuration file://s3-event-config.json
```

Create `s3-event-config.json`:
```json
{
  "LambdaFunctionConfigurations": [
    {
      "Id": "TriggerGlueOnNewData",
      "LambdaFunctionArn": "arn:aws:lambda:us-east-1:<account-id>:function:TriggerGlueWorkflow",
      "Events": ["s3:ObjectCreated:*"],
      "Filter": {
        "Key": {
          "FilterRules": [
            {
              "Name": "suffix",
              "Value": ".csv"
            }
          ]
        }
      }
    }
  ]
}
```

*(Lambda function creation is beyond this scope but mentioned for completeness)*

---

### Phase 9: Monitoring and Alerts (15 minutes)

#### Step 9.1: Create CloudWatch Dashboard

```bash
aws cloudwatch put-dashboard \
    --dashboard-name ClimateHealthGlueDashboard \
    --dashboard-body file://dashboard-config.json
```

#### Step 9.2: Set Up Failure Alerts

```bash
# Create SNS topic for alerts
aws sns create-topic \
    --name glue-job-failures \
    --region us-east-1

# Subscribe your email
aws sns subscribe \
    --topic-arn arn:aws:sns:us-east-1:<account-id>:glue-job-failures \
    --protocol email \
    --notification-endpoint your-email@example.com

# Create CloudWatch alarm
aws cloudwatch put-metric-alarm \
    --alarm-name glue-job-failure-alarm \
    --alarm-description "Alert when Glue job fails" \
    --metric-name JobFailures \
    --namespace AWS/Glue \
    --statistic Sum \
    --period 300 \
    --threshold 1 \
    --comparison-operator GreaterThanThreshold \
    --evaluation-periods 1 \
    --alarm-actions arn:aws:sns:us-east-1:<account-id>:glue-job-failures
```

---

## Troubleshooting Guide

### Issue 1: Glue Job Fails with "Connection Error"

**Symptom**: Job fails when trying to connect to RDS

**Solution**:
1. Check security group allows inbound traffic on port 5432
2. Verify Glue connection test passes
3. Ensure RDS is in same VPC or peering is configured
4. Check Glue IAM role has RDS permissions

### Issue 2: S3 Access Denied

**Symptom**: Job fails with "Access Denied" for S3

**Solution**:
1. Verify IAM role has S3 read/write permissions
2. Check bucket policies allow Glue access
3. Ensure bucket names match in job configurations

### Issue 3: No Data in RDS After Job Completion

**Symptom**: Job succeeds but tables are empty

**Solution**:
1. Check CloudWatch logs for detailed error messages
2. Verify CSV files have correct format and headers
3. Run test query in RDS to check table structure
4. Review job bookmark settings (might skip data on reruns)

### Issue 4: Derived Metrics Not Generated

**Symptom**: Metrics job completes but S3 folder is empty

**Solution**:
1. Ensure all previous jobs completed successfully
2. Check if data exists in RDS tables
3. Verify S3 bucket has correct write permissions
4. Review CloudWatch logs for pandas/spark errors

---

## Cost Estimation

**Monthly costs for moderate usage:**

- **AWS Glue Jobs**: $0.44 per DPU-Hour
  - 5 jobs × 10 minutes × 2 DPUs × 30 days = ~$22/month
- **S3 Storage**: $0.023 per GB
  - ~5 GB data = ~$0.12/month
- **RDS PostgreSQL**: db.t3.micro
  - ~$15/month (with reserved instance: ~$9/month)
- **Data Transfer**: Minimal (same region)
  - ~$1/month

**Total**: ~$38/month (or ~$32 with reserved RDS)

---

## Next Steps

After successful migration:

1. **Update Backend Application**
   - Modify `backend/app/models/database.py` to use RDS connection
   - Update data reading functions to use S3 instead of local files

2. **Integrate with Frontend**
   - Update API endpoints to read processed metrics from S3
   - Configure CloudFront for fast S3 access

3. **Set Up CI/CD**
   - Automate Glue script updates when code changes
   - Use AWS CodePipeline for deployment

4. **Optimize Performance**
   - Tune Glue job worker counts based on data volume
   - Enable Glue job bookmarks for incremental processing
   - Partition S3 data by date for faster queries

5. **Implement Data Quality Checks**
   - Add AWS Glue Data Quality rules
   - Set up data validation jobs
   - Create data lineage tracking

---

## Support and Resources

- **AWS Glue Documentation**: https://docs.aws.amazon.com/glue/
- **AWS Glue Python API**: https://docs.aws.amazon.com/glue/latest/dg/aws-glue-api.html
- **CloudWatch Logs**: https://console.aws.amazon.com/cloudwatch/
- **Project Repository**: Your GitHub repo

---

## Summary Checklist

- [ ] IAM role created with correct permissions
- [ ] RDS PostgreSQL database created and configured
- [ ] Database credentials stored in Secrets Manager
- [ ] S3 buckets created (5 buckets)
- [ ] Glue ETL scripts uploaded to S3
- [ ] Glue jobs created (5 jobs)
- [ ] Glue connection to RDS configured and tested
- [ ] Workflow created with job dependencies
- [ ] Triggers created (scheduled + optional event-based)
- [ ] Initial data uploaded to S3
- [ ] Test workflow run completed successfully
- [ ] Data verified in RDS and S3
- [ ] CloudWatch monitoring configured
- [ ] SNS alerts set up for failures

**Congratulations! Your ETL processing is now running on AWS Glue! 🎉**
