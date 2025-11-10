# 🎯 COMPLETE STEP-BY-STEP GUIDE: AWS Glue ETL Migration

**FOLLOW THIS GUIDE FROM TOP TO BOTTOM - NO STEPS SKIPPED**

This is your ONE guide to complete the AWS Glue migration without any errors. Follow each step carefully.

---

## 📋 Table of Contents

1. [Prerequisites Checklist](#prerequisites-checklist)
2. [AWS Account Setup](#aws-account-setup)
3. [Local Environment Setup](#local-environment-setup)
4. [AWS Console Configuration](#aws-console-configuration)
5. [Deployment Steps](#deployment-steps)
6. [Testing & Verification](#testing-verification)
7. [Troubleshooting](#troubleshooting)

---

## ✅ Prerequisites Checklist

Before starting, make sure you have:

- [ ] AWS Account (with billing enabled)
- [ ] AWS Access Key ID and Secret Access Key
- [ ] Python 3.8 or higher installed
- [ ] pip (Python package manager) installed
- [ ] Terminal/Command Line access
- [ ] Code editor (VS Code) open with this project
- [ ] Credit card (AWS will charge for services)

**Estimated Time:** 2-3 hours  
**Estimated Cost:** $10-50/month (depending on usage)

---

## 🌐 AWS Account Setup

### Step 1: Create/Access AWS Account

1. **Go to:** https://aws.amazon.com
2. **Click:** "Create an AWS Account" (or "Sign In" if you have one)
3. **Enter:**
   - Email address
   - Password
   - AWS account name
4. **Complete:**
   - Contact information
   - Payment information (credit card)
   - Identity verification (phone)
   - Support plan (choose "Basic" - it's free)

### Step 2: Create IAM User (IMPORTANT!)

**⚠️ DO NOT use your root account for daily work!**

1. **Sign in to AWS Console:** https://console.aws.amazon.com
2. **Search for "IAM"** in the top search bar
3. **Click:** "Users" in left sidebar
4. **Click:** "Create user" (orange button)
5. **Enter:**
   - User name: `glue-admin`
6. **Check:** "Provide user access to the AWS Management Console"
7. **Select:** "I want to create an IAM user"
8. **Click:** "Next"

### Step 3: Set Permissions for IAM User

1. **Select:** "Attach policies directly"
2. **Search and check these policies:**
   - ✅ `AWSGlueConsoleFullAccess`
   - ✅ `AmazonS3FullAccess`
   - ✅ `AmazonRDSFullAccess`
   - ✅ `IAMFullAccess`
   - ✅ `CloudWatchFullAccess`
   - ✅ `SecretsManagerReadWrite`
3. **Click:** "Next"
4. **Click:** "Create user"
5. **IMPORTANT:** Download the `.csv` file with credentials (you'll need this!)

### Step 4: Create Access Keys

1. **Click** on your new user `glue-admin`
2. **Click:** "Security credentials" tab
3. **Scroll down** to "Access keys"
4. **Click:** "Create access key"
5. **Select:** "Command Line Interface (CLI)"
6. **Check:** "I understand the above recommendation"
7. **Click:** "Next"
8. **Click:** "Create access key"
9. **COPY** both:
   - Access Key ID
   - Secret Access Key
10. **Click:** "Download .csv file" (backup!)
11. **Click:** "Done"

**⚠️ SAVE THESE KEYS SECURELY - You cannot retrieve the secret key later!**

---

## 💻 Local Environment Setup

### Step 5: Install AWS CLI

**On macOS (your system):**

```bash
# Install AWS CLI using Homebrew
brew install awscli

# Verify installation
aws --version
```

You should see: `aws-cli/2.x.x Python/3.x.x Darwin/...`

### Step 6: Configure AWS CLI

```bash
# Configure AWS credentials
aws configure
```

**Enter when prompted:**
```
AWS Access Key ID: [paste your Access Key ID]
AWS Secret Access Key: [paste your Secret Access Key]
Default region name: us-east-1
Default output format: json
```

**Verify configuration:**
```bash
# Test AWS connection
aws sts get-caller-identity
```

You should see your account ID and user ARN.

### Step 7: Install Python Dependencies

```bash
# Navigate to aws-glue directory
cd /Users/sharvajvidyutgmail.com/Desktop/vs/curriculum/projects/climate-resilient/aws-glue

# Install deployment dependencies
pip install -r deployment/requirements.txt
```

**Expected output:**
```
Successfully installed boto3-1.28.x awscli-1.29.x python-dotenv-1.0.x
```

### Step 8: Create Environment File

```bash
# Create .env file in aws-glue directory
touch .env
```

**Open `.env` in VS Code and add:**

```env
# AWS Configuration
AWS_REGION=us-east-1
AWS_ACCOUNT_ID=your-account-id-here

# S3 Buckets
S3_RAW_DATA_BUCKET=climate-health-raw-data
S3_PROCESSED_DATA_BUCKET=climate-health-processed-data
S3_GLUE_SCRIPTS_BUCKET=climate-health-glue-scripts
S3_GLUE_TEMP_BUCKET=climate-health-glue-temp
S3_GLUE_LOGS_BUCKET=climate-health-glue-logs

# RDS Configuration
DB_HOST=your-rds-endpoint-here
DB_PORT=5432
DB_NAME=climate_health
DB_USER=admin
DB_PASSWORD=your-secure-password-here

# Glue Configuration
GLUE_DATABASE=climate_health_db
GLUE_ROLE_NAME=AWSGlueServiceRole-ClimateHealth
```

**To find your AWS Account ID:**
```bash
aws sts get-caller-identity --query Account --output text
```

**Paste the account ID** into `.env` file where it says `your-account-id-here`

---

## ☁️ AWS Console Configuration

### Step 9: Create S3 Buckets

**Option A: Using AWS Console (Recommended for first time)**

1. **Go to:** https://s3.console.aws.amazon.com
2. **For EACH bucket below, do this:**

**Bucket 1: Raw Data**
- Click: "Create bucket"
- Bucket name: `climate-health-raw-data-YOURNAME` (must be globally unique)
- Region: `US East (N. Virginia) us-east-1`
- Uncheck: "Block all public access"
- Check: "I acknowledge that the current settings might result in this bucket and the objects within becoming public"
- Click: "Create bucket"

**Bucket 2: Processed Data**
- Repeat above with name: `climate-health-processed-data-YOURNAME`

**Bucket 3: Glue Scripts**
- Repeat above with name: `climate-health-glue-scripts-YOURNAME`

**Bucket 4: Glue Temp**
- Repeat above with name: `climate-health-glue-temp-YOURNAME`

**Bucket 5: Glue Logs**
- Repeat above with name: `climate-health-glue-logs-YOURNAME`

**Update your .env file** with the actual bucket names you created.

**Option B: Using AWS CLI (Faster)**

```bash
# Create all 5 buckets at once
aws s3 mb s3://climate-health-raw-data-YOURNAME --region us-east-1
aws s3 mb s3://climate-health-processed-data-YOURNAME --region us-east-1
aws s3 mb s3://climate-health-glue-scripts-YOURNAME --region us-east-1
aws s3 mb s3://climate-health-glue-temp-YOURNAME --region us-east-1
aws s3 mb s3://climate-health-glue-logs-YOURNAME --region us-east-1

# Verify buckets created
aws s3 ls
```

### Step 10: Create RDS PostgreSQL Database

1. **Go to:** https://console.aws.amazon.com/rds
2. **Click:** "Create database"
3. **Choose:** "Standard create"
4. **Engine type:** PostgreSQL
5. **Engine version:** PostgreSQL 15.4 (or latest)
6. **Templates:** "Free tier" (if available) OR "Dev/Test"
7. **Settings:**
   - DB instance identifier: `climate-health-db`
   - Master username: `admin`
   - Master password: (create a strong password)
   - Confirm password: (same password)
8. **DB instance class:**
   - Burstable classes: `db.t3.micro` (free tier eligible)
9. **Storage:**
   - Storage type: General Purpose SSD (gp3)
   - Allocated storage: 20 GB
   - Uncheck: "Enable storage autoscaling"
10. **Connectivity:**
    - VPC: (default)
    - Public access: **YES** (important for Glue access)
    - VPC security group: Create new
    - New VPC security group name: `glue-rds-sg`
11. **Database authentication:** Password authentication
12. **Additional configuration:**
    - Initial database name: `climate_health`
    - Uncheck: "Enable automated backups" (for dev/test)
    - Uncheck: "Enable encryption" (optional)
13. **Click:** "Create database"

**⏳ Wait 5-10 minutes** for database to be created.

### Step 11: Configure RDS Security Group

1. **Go to:** https://console.aws.amazon.com/rds
2. **Click:** on your database `climate-health-db`
3. **Under "Security group rules"**, click on the security group link
4. **Click:** "Edit inbound rules"
5. **Click:** "Add rule"
6. **Configure:**
   - Type: `PostgreSQL`
   - Protocol: `TCP`
   - Port range: `5432`
   - Source: `0.0.0.0/0` (anywhere - for dev/test only!)
7. **Click:** "Save rules"

### Step 12: Get RDS Endpoint

1. **Go to:** https://console.aws.amazon.com/rds
2. **Click:** on your database `climate-health-db`
3. **Copy** the "Endpoint" (looks like: `climate-health-db.xxxxx.us-east-1.rds.amazonaws.com`)
4. **Update `.env` file:**
   ```
   DB_HOST=climate-health-db.xxxxx.us-east-1.rds.amazonaws.com
   DB_PASSWORD=your-actual-password
   ```

### Step 13: Store RDS Credentials in Secrets Manager

1. **Go to:** https://console.aws.amazon.com/secretsmanager
2. **Click:** "Store a new secret"
3. **Select:** "Credentials for RDS database"
4. **Enter:**
   - User name: `admin`
   - Password: (your RDS password)
5. **Select:** your RDS database `climate-health-db`
6. **Click:** "Next"
7. **Secret name:** `rds/climate-health/credentials`
8. **Click:** "Next"
9. **Disable automatic rotation** (for now)
10. **Click:** "Next"
11. **Click:** "Store"

### Step 14: Create IAM Role for Glue

1. **Go to:** https://console.aws.amazon.com/iam
2. **Click:** "Roles" in left sidebar
3. **Click:** "Create role"
4. **Select:** "AWS service"
5. **Use case:** "Glue"
6. **Click:** "Next"
7. **Search and attach these policies:**
   - ✅ `AWSGlueServiceRole`
   - ✅ `AmazonS3FullAccess`
   - ✅ `AmazonRDSFullAccess`
   - ✅ `CloudWatchLogsFullAccess`
   - ✅ `SecretsManagerReadWrite`
8. **Click:** "Next"
9. **Role name:** `AWSGlueServiceRole-ClimateHealth`
10. **Click:** "Create role"

### Step 15: Create Glue Database

1. **Go to:** https://console.aws.amazon.com/glue
2. **Click:** "Databases" in left sidebar (under Data Catalog)
3. **Click:** "Add database"
4. **Database name:** `climate_health_db`
5. **Description:** `Climate and health data catalog`
6. **Click:** "Create database"

---

## 🚀 Deployment Steps

### Step 16: Upload Sample Data to S3

First, let's generate and upload sample data:

```bash
# Navigate to backend directory
cd /Users/sharvajvidyutgmail.com/Desktop/vs/curriculum/projects/climate-resilient/backend

# Generate sample data (if not already generated)
python -c "from app.utils.data_generator import main; main()"

# Navigate back to aws-glue directory
cd ../aws-glue

# Upload sample data to S3 raw bucket
aws s3 cp ../backend/data/raw/ s3://climate-health-raw-data-YOURNAME/raw/ --recursive

# Verify upload
aws s3 ls s3://climate-health-raw-data-YOURNAME/raw/
```

You should see files like:
- `locations.csv`
- `climate_data.csv`
- `health_data.csv`
- `hospital_data.csv`

### Step 17: Deploy Glue Jobs - Method 1 (Python Script - Recommended)

```bash
# Navigate to aws-glue directory
cd /Users/sharvajvidyutgmail.com/Desktop/vs/curriculum/projects/climate-resilient/aws-glue

# Run deployment script
python deployment/deploy_glue_jobs.py
```

**Expected output:**
```
Starting AWS Glue deployment...
✅ Created S3 bucket: climate-health-raw-data-YOURNAME
✅ Created S3 bucket: climate-health-processed-data-YOURNAME
...
✅ Uploaded: etl-jobs/process_locations.py
✅ Uploaded: etl-jobs/process_climate_data.py
...
✅ Created Glue connection: climate-health-rds
✅ Created Glue job: process-locations
✅ Created Glue job: process-climate-data
...
✅ Created Glue workflow: climate-health-etl-workflow
Deployment completed successfully!
```

**If you see errors:**
- Check your `.env` file has correct values
- Verify AWS credentials: `aws sts get-caller-identity`
- Check IAM permissions for your user

### Step 18: Deploy Glue Jobs - Method 2 (Bash Script - Alternative)

```bash
# Make script executable
chmod +x deployment/deploy_glue_jobs.sh

# Run deployment
./deployment/deploy_glue_jobs.sh
```

### Step 19: Verify Deployment in AWS Console

**Check S3 Scripts:**
1. Go to: https://s3.console.aws.amazon.com
2. Open: `climate-health-glue-scripts-YOURNAME`
3. You should see 5 Python files:
   - `process_locations.py`
   - `process_climate_data.py`
   - `process_health_data.py`
   - `process_hospital_data.py`
   - `calculate_derived_metrics.py`

**Check Glue Jobs:**
1. Go to: https://console.aws.amazon.com/glue
2. Click: "ETL jobs" in left sidebar
3. You should see 5 jobs:
   - `process-locations`
   - `process-climate-data`
   - `process-health-data`
   - `process-hospital-data`
   - `calculate-derived-metrics`

**Check Glue Workflow:**
1. Stay in Glue console
2. Click: "Workflows" in left sidebar
3. You should see: `climate-health-etl-workflow`

---

## ✅ Testing & Verification

### Step 20: Run Individual Glue Job (Test)

**Option A: AWS Console**

1. **Go to:** https://console.aws.amazon.com/glue
2. **Click:** "ETL jobs" in left sidebar
3. **Select:** `process-locations` (checkbox)
4. **Click:** "Run job" button at top
5. **Click:** "Run job" in popup
6. **Monitor:** Click on "Runs" tab to see status
7. **Wait:** Job should complete in 2-5 minutes

**Status indicators:**
- 🟡 **Running:** Job is executing
- 🟢 **Succeeded:** Job completed successfully
- 🔴 **Failed:** Job had an error (check CloudWatch logs)

**Option B: AWS CLI**

```bash
# Start the locations job
aws glue start-job-run --job-name process-locations

# Get the job run ID from output, then check status
aws glue get-job-run --job-name process-locations --run-id jr_xxxxx
```

### Step 21: Check Job Logs

1. **Go to:** https://console.aws.amazon.com/cloudwatch
2. **Click:** "Log groups" in left sidebar
3. **Search for:** `/aws-glue/jobs/output`
4. **Click:** on the log group
5. **Click:** on latest log stream
6. **Review:** Job execution logs

**Look for:**
- ✅ `Job completed successfully`
- ✅ `Records processed: X`
- ❌ Any error messages

### Step 22: Verify Data in RDS

```bash
# Install PostgreSQL client (if not installed)
brew install postgresql

# Connect to RDS database
psql -h climate-health-db.xxxxx.us-east-1.rds.amazonaws.com \
     -U admin \
     -d climate_health \
     -p 5432
```

**When prompted, enter your RDS password.**

**Run these SQL queries:**

```sql
-- Check if tables exist
\dt

-- Count records in locations table
SELECT COUNT(*) FROM locations;

-- View sample data
SELECT * FROM locations LIMIT 5;

-- Exit
\q
```

**Expected results:**
- Should see 4 tables: `locations`, `climate_data`, `health_data`, `hospital_data`
- `locations` table should have 100+ records

### Step 23: Run Complete Workflow

**Option A: AWS Console**

1. **Go to:** https://console.aws.amazon.com/glue
2. **Click:** "Workflows" in left sidebar
3. **Select:** `climate-health-etl-workflow`
4. **Click:** "Run" button at top
5. **Monitor:** Watch the workflow graph as jobs execute
6. **Wait:** All 5 jobs should complete in 15-30 minutes

**Workflow execution order:**
1. `process-locations` (runs first)
2. `process-climate-data`, `process-health-data`, `process-hospital-data` (run in parallel)
3. `calculate-derived-metrics` (runs last after all data loaded)

**Option B: AWS CLI**

```bash
# Trigger workflow
aws glue start-workflow-run --name climate-health-etl-workflow

# Get workflow run ID and check status
aws glue get-workflow-run --name climate-health-etl-workflow --run-id wr_xxxxx
```

### Step 24: Verify Output Files in S3

```bash
# Check processed data bucket
aws s3 ls s3://climate-health-processed-data-YOURNAME/metrics/ --recursive

# Download a sample output file
aws s3 cp s3://climate-health-processed-data-YOURNAME/metrics/derived_metrics.csv ./
aws s3 cp s3://climate-health-processed-data-YOURNAME/metrics/derived_metrics.json ./

# View contents
cat derived_metrics.csv | head -20
cat derived_metrics.json | head -50
```

**Expected files:**
- `derived_metrics.csv` - CSV format with all metrics
- `derived_metrics.json` - JSON format with all metrics
- Both should contain: disease rates, risk scores, resilience metrics

---

## 🔧 Troubleshooting

### Common Issues and Solutions

#### Issue 1: "AccessDenied" errors

**Symptoms:** Jobs fail with access denied errors

**Solution:**
```bash
# Check IAM role has correct policies
aws iam list-attached-role-policies --role-name AWSGlueServiceRole-ClimateHealth

# If missing, attach policies:
aws iam attach-role-policy \
  --role-name AWSGlueServiceRole-ClimateHealth \
  --policy-arn arn:aws:iam::aws:policy/AmazonS3FullAccess

aws iam attach-role-policy \
  --role-name AWSGlueServiceRole-ClimateHealth \
  --policy-arn arn:aws:iam::aws:policy/AmazonRDSFullAccess
```

#### Issue 2: RDS connection timeout

**Symptoms:** Jobs fail with "could not connect to server"

**Solution:**
1. Check RDS security group allows port 5432
2. Verify RDS is publicly accessible
3. Test connection from terminal:
   ```bash
   nc -zv climate-health-db.xxxxx.us-east-1.rds.amazonaws.com 5432
   ```

#### Issue 3: S3 bucket not found

**Symptoms:** "NoSuchBucket" error

**Solution:**
```bash
# List all your buckets
aws s3 ls

# Create missing bucket
aws s3 mb s3://climate-health-raw-data-YOURNAME --region us-east-1
```

#### Issue 4: Glue job fails with "File not found"

**Symptoms:** Job fails looking for CSV files

**Solution:**
```bash
# Verify data files exist in S3
aws s3 ls s3://climate-health-raw-data-YOURNAME/raw/

# If missing, upload data:
cd /Users/sharvajvidyutgmail.com/Desktop/vs/curriculum/projects/climate-resilient/backend
python -c "from app.utils.data_generator import main; main()"
aws s3 cp data/raw/ s3://climate-health-raw-data-YOURNAME/raw/ --recursive
```

#### Issue 5: Job succeeds but no data in RDS

**Symptoms:** Job shows success but tables are empty

**Solution:**
```bash
# Check job bookmarks - might be skipping data
# Disable job bookmarks and rerun:
aws glue update-job \
  --job-name process-locations \
  --job-update '{
    "JobBookmarksEncryption": {"JobBookmarksEncryptionMode": "DISABLED"}
  }'

# Then rerun job
aws glue start-job-run --job-name process-locations
```

#### Issue 6: High costs

**Symptoms:** AWS bill is higher than expected

**Solutions:**
1. **Stop unused jobs:**
   ```bash
   # List running jobs
   aws glue get-job-runs --job-name process-locations --max-results 5
   ```

2. **Reduce DPU allocation:**
   - Edit job in console
   - Change "Maximum capacity" from 10 to 2 DPUs

3. **Delete test data:**
   ```bash
   # Empty and delete temp bucket
   aws s3 rm s3://climate-health-glue-temp-YOURNAME --recursive
   ```

4. **Stop RDS when not in use:**
   - Go to RDS console
   - Select database
   - Actions → Stop

---

## 📊 Cost Monitoring

### Check Current Costs

1. **Go to:** https://console.aws.amazon.com/billing
2. **Click:** "Bills" in left sidebar
3. **Review:** Current month charges
4. **Check:** Services breakdown

**Expected costs:**
- Glue: $0.44 per DPU-hour (2 DPU = $0.88/hour)
- RDS: $0.017/hour for db.t3.micro (~$12.50/month)
- S3: $0.023 per GB per month (minimal for small datasets)
- **Total estimate:** $20-30/month for development

### Set Up Billing Alerts

1. **Go to:** https://console.aws.amazon.com/billing
2. **Click:** "Budgets" in left sidebar
3. **Click:** "Create budget"
4. **Select:** "Cost budget - Recommended"
5. **Enter:** Budget name: `Monthly-Budget`
6. **Enter:** Amount: `$50`
7. **Click:** "Next"
8. **Add email alert** at 80% and 100%
9. **Click:** "Create budget"

---

## ✨ Success Checklist

Before you're done, verify:

- [ ] All 5 S3 buckets created and have content
- [ ] RDS PostgreSQL database running and accessible
- [ ] All 5 Glue jobs created and show green checkmarks
- [ ] Glue workflow created with all 5 jobs
- [ ] Test job run succeeded (check CloudWatch logs)
- [ ] RDS tables have data (checked with psql)
- [ ] Derived metrics CSV/JSON files in S3 processed bucket
- [ ] Billing alerts set up
- [ ] Credentials stored in Secrets Manager

---

## 🎓 What You've Accomplished

You've successfully:

1. ✅ Migrated local Python ETL scripts to AWS Glue
2. ✅ Set up distributed data processing with Apache Spark
3. ✅ Created a production-ready data pipeline
4. ✅ Implemented data quality checks and validations
5. ✅ Configured automated workflow orchestration
6. ✅ Set up monitoring and logging with CloudWatch
7. ✅ Secured credentials with AWS Secrets Manager
8. ✅ Built a scalable cloud data architecture

**This ETL pipeline can now:**
- Process millions of records
- Run on a schedule (daily/hourly)
- Scale automatically based on data volume
- Handle failures with automatic retries
- Generate derived analytics for machine learning

---

## 📚 Next Steps

1. **Schedule Workflow:**
   - Set up daily runs using Glue triggers
   - See: `GLUE_MIGRATION_GUIDE.md` Section 6

2. **Integrate with FastAPI Backend:**
   - Update backend to read from RDS instead of SQLite
   - Update connection strings in `backend/app/models/database.py`

3. **Set Up CI/CD:**
   - Automate deployments with GitHub Actions
   - See: `IMPLEMENTATION_SUMMARY.md` Section 4

4. **Optimize Performance:**
   - Tune Spark configurations
   - Implement data partitioning
   - See: `QUICK_REFERENCE.md` Performance section

5. **Production Hardening:**
   - Set up VPC endpoints
   - Enable encryption at rest
   - Implement least-privilege IAM policies

---

## 🆘 Getting Help

**If stuck:**

1. **Check CloudWatch Logs:**
   - Most errors show detailed stack traces in logs

2. **Review Documentation:**
   - `GLUE_MIGRATION_GUIDE.md` - Detailed technical guide
   - `QUICK_REFERENCE.md` - Command reference
   - `ARCHITECTURE_DIAGRAMS.md` - System architecture

3. **AWS Support:**
   - https://console.aws.amazon.com/support
   - Check AWS Glue troubleshooting docs

4. **Common Error Messages:**
   - "NoSuchBucket" → Check bucket names in .env
   - "AccessDenied" → Check IAM role permissions
   - "Connection timeout" → Check security groups
   - "File not found" → Verify S3 file paths

---

## 🎯 Quick Start Summary

**Shortest path to success:**

```bash
# 1. Install and configure
brew install awscli postgresql
aws configure
cd aws-glue
pip install -r deployment/requirements.txt

# 2. Create .env file with your AWS account details

# 3. Create AWS resources via console:
#    - 5 S3 buckets
#    - 1 RDS PostgreSQL database
#    - 1 IAM role for Glue
#    - 1 Glue database

# 4. Generate and upload data
cd ../backend
python -c "from app.utils.data_generator import main; main()"
aws s3 cp data/raw/ s3://YOUR-RAW-BUCKET/raw/ --recursive

# 5. Deploy Glue jobs
cd ../aws-glue
python deployment/deploy_glue_jobs.py

# 6. Run test job
aws glue start-job-run --job-name process-locations

# 7. Run full workflow
aws glue start-workflow-run --name climate-health-etl-workflow

# 8. Verify results
psql -h YOUR-RDS-ENDPOINT -U admin -d climate_health
```

---

**📝 Last Updated:** November 6, 2025  
**🔖 Version:** 1.0.0  
**👤 Author:** Climate-Resilient Healthcare Team

---

**Good luck with your migration! 🚀**
