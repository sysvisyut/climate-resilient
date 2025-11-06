# 🚀 AWS Migration - Complete Execution Steps

## ⏱️ Estimated Time: 2-3 Hours

---

## 📋 PHASE 1: AWS Account Setup (30-45 minutes)

### ✅ Step 1.1: Create AWS Account

1. **Go to AWS**: https://aws.amazon.com/
2. **Click**: "Create an AWS Account"
3. **Enter**:
   - Email: [your email]
   - Account name: `climate-health-system`
4. **Choose**: Personal account
5. **Enter payment info**: Card won't be charged for Free Tier
6. **Verify**: Phone number (SMS or call)
7. **Select**: Basic Support Plan (Free)
8. **Wait**: 5-10 minutes for account activation

**✓ VERIFY**: Check email for "Welcome to Amazon Web Services"

---

### ✅ Step 1.2: First Login

1. **Go to**: https://console.aws.amazon.com/
2. **Login**: Root user with your email and password
3. **Top-right corner**: Select region → **Asia Pacific (Mumbai) ap-south-1**
4. **IMPORTANT**: Keep this region for ALL services!

**✓ VERIFY**: Region shows "Asia Pacific (Mumbai)"

---

## 🔐 PHASE 2: Security Setup (20-30 minutes)

### ✅ Step 2.1: Create IAM User

**⚠️ NEVER use root account for daily work!**

1. **Search bar** → Type: `IAM` → Click **IAM**
2. **Left sidebar** → Click **Users**
3. **Click**: "Create user"
4. **Enter**:
   ```
   User name: climate-admin
   ✓ Provide user access to AWS Management Console
   Console password: Custom password
   [Create strong password - save it!]
   ☐ Users must create new password (UNCHECK)
   ```
5. **Click**: "Next"
6. **Select**: "Attach policies directly"
7. **Search and check**: `AdministratorAccess`
8. **Click**: "Next" → "Create user"
9. **IMPORTANT**: Download credentials CSV file
10. **Save as**: `climate-admin-credentials.csv`

**✓ VERIFY**: You have the CSV file saved

---

### ✅ Step 2.2: Switch to IAM User

1. **Sign out** from root account (top-right)
2. **Open CSV file** → Copy the Console sign-in URL
3. **Navigate to** the sign-in URL
4. **Login**:
   - Username: `climate-admin`
   - Password: [from CSV]

**✓ VERIFY**: Top-right shows "climate-admin @ [account-name]"

---

### ✅ Step 2.3: Create Access Keys

1. **In IAM** → **Users** → Click `climate-admin`
2. **Security credentials** tab
3. **Scroll to** "Access keys"
4. **Click**: "Create access key"
5. **Select**: "Command Line Interface (CLI)"
6. **Check**: ☑ "I understand..."
7. **Click**: "Next"
8. **Description**: `Climate Health CLI Access`
9. **Click**: "Create access key"
10. **CRITICAL**: Download CSV file
11. **Save as**: `climate-admin_accessKeys.csv`

**✓ VERIFY**: You have TWO CSV files saved:
- `climate-admin-credentials.csv` (console login)
- `climate-admin_accessKeys.csv` (programmatic access)

---

## 💰 PHASE 3: Billing Protection (15 minutes)

### ✅ Step 3.1: Enable Billing Alerts

1. **Top-right** → Click your name → **Account**
2. **Scroll to**: "IAM User and Role Access to Billing"
3. **Click**: "Edit"
4. **Check**: ☑ "Activate IAM Access"
5. **Click**: "Update"

**✓ VERIFY**: Shows "Activated"

---

### ✅ Step 3.2: Create Budget Alerts

1. **Search** → Type: `Billing` → Click **Billing and Cost Management**
2. **Left sidebar** → **Budgets** → **Create budget**

**Budget 1 - Zero Spend Alert:**
3. **Select**: "Zero spend budget"
4. **Budget name**: `climate-health-zero-spend`
5. **Email**: [your email]
6. **Create budget**

**Budget 2 - Cost Threshold:**
7. **Create budget** again
8. **Select**: "Monthly cost budget"
9. **Budget name**: `climate-health-monthly-limit`
10. **Amount**: `$5.00`
11. **Email**: [your email]
12. **Threshold**: 80% and 100%
13. **Create budget**

**✓ VERIFY**: You have 2 budgets created
**✓ VERIFY**: Check email for budget confirmation

---

## 🗄️ PHASE 4: Database Setup (25-35 minutes)

### ✅ Step 4.1: Create RDS PostgreSQL

1. **Search** → Type: `RDS` → Click **RDS**
2. **Click**: "Create database"
3. **Engine**: PostgreSQL
4. **Template**: ☑ **Free tier**
5. **Settings**:
   ```
   DB instance identifier: climate-health-db
   Master username: postgres
   Master password: [CREATE STRONG PASSWORD]
   Confirm password: [SAME PASSWORD]
   ```
6. **💾 WRITE DOWN PASSWORD**: ________________________
7. **Instance**: db.t3.micro (pre-selected)
8. **Storage**: 20 GiB (pre-selected)
9. **☐ Uncheck**: "Enable storage autoscaling"
10. **Connectivity**:
    - Public access: **Yes**
    - VPC security group: **Create new**
    - Name: `climate-health-db-sg`
11. **Additional configuration**:
    - Initial database name: `climate_health`
12. **☐ Uncheck**: "Enable automated backups"
13. **Click**: "Create database"
14. **Wait**: 5-10 minutes (status will change to "Available")

**✓ VERIFY**: Database status shows "Available"

---

### ✅ Step 4.2: Configure Database Access

1. **Click** your database: `climate-health-db`
2. **Copy** the **Endpoint**: 
   ```
   climate-health-db.XXXXXXXXXX.ap-south-1.rds.amazonaws.com
   ```
3. **💾 SAVE THIS**: ________________________
4. **Connectivity tab** → Click the security group link
5. **Click**: "Edit inbound rules"
6. **Click**: "Add rule"
7. **Configure**:
   - Type: PostgreSQL
   - Port: 5432 (auto-filled)
   - Source: My IP (auto-detects)
   - Description: `My dev machine`
8. **Click**: "Save rules"

**✓ VERIFY**: Inbound rule shows port 5432 from your IP

---

## 📦 PHASE 5: Storage Setup (10-15 minutes)

### ✅ Step 5.1: Create S3 Buckets

**Bucket 1 - Raw Data:**
1. **Search** → Type: `S3` → Click **S3**
2. **Click**: "Create bucket"
3. **Bucket name**: `climate-health-raw-data-[YOUR-UNIQUE-ID]`
   - Example: `climate-health-raw-data-rohit2025`
   - Must be globally unique!
4. **Region**: Asia Pacific (Mumbai) ap-south-1
5. **Block Public Access**: ☑ ALL checked (keep private)
6. **Versioning**: Disable
7. **Encryption**: SSE-S3
8. **Create bucket**
9. **💾 SAVE BUCKET NAME**: ________________________

**Bucket 2 - Processed Data:**
10. Repeat steps 2-8 with name: `climate-health-processed-data-[YOUR-UNIQUE-ID]`
11. **💾 SAVE BUCKET NAME**: ________________________

**Bucket 3 - ML Models:**
12. Repeat steps 2-8 with name: `climate-health-models-[YOUR-UNIQUE-ID]`
13. **💾 SAVE BUCKET NAME**: ________________________

**✓ VERIFY**: You have 3 buckets in Mumbai region
**✓ VERIFY**: All buckets show "Access: Bucket and objects not public"

---

## 🔔 PHASE 6: Notifications Setup (10 minutes)

### ✅ Step 6.1: Create SNS Topic

1. **Search** → Type: `SNS` → Click **Simple Notification Service**
2. **Left sidebar** → **Topics** → **Create topic**
3. **Type**: Standard
4. **Name**: `climate-health-alerts`
5. **Display name**: `Climate Alerts`
6. **Create topic**
7. **💾 COPY Topic ARN**: 
   ```
   arn:aws:sns:ap-south-1:XXXX:climate-health-alerts
   ```
8. **Save it**: ________________________

**✓ VERIFY**: Topic created successfully

---

### ✅ Step 6.2: Subscribe to Alerts

1. **Click**: "Create subscription"
2. **Protocol**: Email
3. **Endpoint**: [your email]
4. **Create subscription**
5. **Check your email**
6. **Click** the confirmation link
7. **Return to AWS Console**
8. **Refresh** the page

**✓ VERIFY**: Subscription status = "Confirmed"

---

## 🔐 PHASE 7: Secrets Manager (10 minutes)

### ✅ Step 7.1: Store Database Credentials

1. **Search** → Type: `Secrets Manager` → Click **Secrets Manager**
2. **Click**: "Store a new secret"
3. **Secret type**: "Credentials for RDS database"
4. **User name**: `postgres`
5. **Password**: [Your RDS password from Step 4.1]
6. **Select database**: `climate-health-db`
7. **Click**: "Next"
8. **Secret name**: `climate-health/db/credentials`
9. **Description**: `RDS credentials for Climate Health System`
10. **Next** → **Next** → **Store**

**✓ VERIFY**: Secret created successfully

---

### ✅ Step 7.2: Store JWT Secret

1. **Store a new secret** again
2. **Secret type**: "Other type of secret"
3. **Key/value**:
   - Key: `JWT_SECRET`
   - Value: [Generate random string - use strong password generator, 32+ characters]
4. **Next**
5. **Secret name**: `climate-health/api/jwt-secret`
6. **Next** → **Next** → **Store**

**✓ VERIFY**: You have 2 secrets in Secrets Manager

---

## 💻 PHASE 8: Local Setup (15-20 minutes)

### ✅ Step 8.1: Install AWS CLI

**For Windows:**
1. **Download**: https://awscli.amazonaws.com/AWSCLIV2.msi
2. **Run** the installer
3. **Follow wizard**: Next → Next → Install → Finish
4. **Open PowerShell** (close and reopen if it was open)
5. **Verify**:
   ```powershell
   aws --version
   ```

**✓ VERIFY**: Shows `aws-cli/2.x.x`

---

### ✅ Step 8.2: Configure AWS CLI

1. **Open PowerShell**
2. **Run**:
   ```powershell
   aws configure
   ```
3. **Enter** (from your `climate-admin_accessKeys.csv`):
   ```
   AWS Access Key ID: AKIA................
   AWS Secret Access Key: wJalr...............
   Default region name: ap-south-1
   Default output format: json
   ```

4. **Test connection**:
   ```powershell
   aws sts get-caller-identity
   ```

**✓ VERIFY**: Shows your Account ID and user ARN

---

### ✅ Step 8.3: Install Python Dependencies

1. **Navigate to backend**:
   ```powershell
   cd c:/Users/rohit/Desktop/Climate/backend
   ```

2. **Install boto3**:
   ```powershell
   pip install boto3
   ```

3. **Install PostgreSQL driver**:
   ```powershell
   pip install psycopg2-binary
   ```

4. **Verify**:
   ```powershell
   python -c "import boto3; print('boto3:', boto3.__version__)"
   python -c "import psycopg2; print('psycopg2:', psycopg2.__version__)"
   ```

**✓ VERIFY**: Both import successfully

---

## 🔧 PHASE 9: Update Configuration (10 minutes)

### ✅ Step 9.1: Update aws_config.py

1. **Open**: `c:/Users/rohit/Desktop/Climate/aws_config.py`
2. **Update** these values with your actual values:

```python
# Replace with YOUR bucket names (from Step 5.1)
S3_RAW_DATA_BUCKET = "climate-health-raw-data-rohit2025"  # YOUR BUCKET
S3_PROCESSED_DATA_BUCKET = "climate-health-processed-data-rohit2025"  # YOUR BUCKET
S3_MODELS_BUCKET = "climate-health-models-rohit2025"  # YOUR BUCKET

# Replace with YOUR RDS endpoint (from Step 4.2)
RDS_ENDPOINT = "climate-health-db.c1234567890.ap-south-1.rds.amazonaws.com"  # YOUR ENDPOINT

# Replace with YOUR SNS topic ARN (from Step 6.1)
SNS_ALERTS_TOPIC_ARN = "arn:aws:sns:ap-south-1:123456789012:climate-health-alerts"  # YOUR ARN
```

3. **Save** the file

**✓ VERIFY**: All values updated with your AWS resources

---

## ✅ PHASE 10: Verification & Testing (20-30 minutes)

### ✅ Step 10.1: Test AWS Connection

```powershell
cd c:/Users/rohit/Desktop/Climate
python aws_migration_scripts/1_test_aws_connection.py
```

**Expected output**: All tests PASS ✅
- AWS Credentials
- S3 Access (shows your 3 buckets)
- RDS Access (shows climate-health-db)
- Secrets Manager (shows 2 secrets)
- SNS Access (shows your topic)

**✓ VERIFY**: All 5 tests pass

---

### ✅ Step 10.2: Migrate Database

```powershell
python aws_migration_scripts/2_migrate_database.py
```

**This will**:
- Connect to local SQLite
- Retrieve RDS credentials from Secrets Manager
- Create tables in PostgreSQL
- Migrate all data (locations, climate, health, hospital, users)

**Expected**: "🎉 Database migration completed successfully!"

**✓ VERIFY**: Migration successful, shows record counts

---

### ✅ Step 10.3: Upload Data to S3

```powershell
python aws_migration_scripts/3_upload_to_s3.py
```

**This will**:
- Upload raw data files
- Upload processed data files  
- Upload ML model files

**Expected**: Files uploaded to all 3 buckets

**✓ VERIFY**: Shows uploaded file counts for each bucket

---

### ✅ Step 10.4: Complete Verification

```powershell
python aws_migration_scripts/4_verify_migration.py
```

**This will verify**:
- RDS connection and data counts
- S3 buckets and file counts
- SNS topic and subscriptions
- Secrets Manager secrets
- IAM user permissions
- Cost estimation

**Expected**: "🎉 ALL VERIFICATIONS PASSED!"

**✓ VERIFY**: All checks pass, cost shows ~$0.80/month

---

## 🎉 SUCCESS CONFIRMATION

### You've successfully migrated when ALL these show ✅:

- [ ] AWS account created with Mumbai region
- [ ] IAM user `climate-admin` created and logged in
- [ ] Access keys created and saved
- [ ] 2 billing budgets active
- [ ] RDS PostgreSQL database running
- [ ] Database security group allows your IP
- [ ] 3 S3 buckets created
- [ ] SNS topic created with confirmed email subscription
- [ ] 2 secrets stored in Secrets Manager
- [ ] AWS CLI installed and configured
- [ ] boto3 and psycopg2 installed
- [ ] aws_config.py updated with your values
- [ ] All 4 migration scripts run successfully
- [ ] Estimated cost is ~$0.80/month

---

## 🔍 How to Verify Everything is Connected

### Test 1: Check AWS Console

1. **Go to RDS** → Should see `climate-health-db` (Available)
2. **Go to S3** → Should see 3 buckets with files
3. **Go to SNS** → Should see topic with confirmed subscription
4. **Go to Secrets Manager** → Should see 2 secrets
5. **Go to Billing** → Should see ~$0.00 current charges

### Test 2: Command Line Tests

```powershell
# Test S3
aws s3 ls

# Test RDS
aws rds describe-db-instances --db-instance-identifier climate-health-db

# Test SNS
aws sns list-topics

# Test Secrets
aws secretsmanager list-secrets
```

All should return your resources!

### Test 3: Database Connection Test

```powershell
cd c:/Users/rohit/Desktop/Climate
python -c "
import boto3, json, psycopg2
sm = boto3.client('secretsmanager', region_name='ap-south-1')
secret = json.loads(sm.get_secret_value(SecretId='climate-health/db/credentials')['SecretString'])
conn = psycopg2.connect(host=secret['host'], port=secret['port'], database=secret['dbname'], user=secret['username'], password=secret['password'])
cursor = conn.cursor()
cursor.execute('SELECT COUNT(*) FROM locations')
print(f'✅ Connected! Locations count: {cursor.fetchone()[0]}')
conn.close()
"
```

**✓ VERIFY**: Shows "✅ Connected! Locations count: 36"

---

## 💰 Free Tier Monitoring

### Daily Checks (1 minute):
1. **Billing Dashboard** → Check current month: $0.00 ✅
2. **Free Tier** → Check usage percentages

### Services to Monitor:
- **RDS**: 750 hours/month (1 instance = ~720 hours ✅)
- **S3**: 5 GB limit (you're using < 1 GB ✅)
- **Lambda**: 1M requests/month (not deployed yet)
- **Secrets Manager**: $0.40/secret/month = $0.80 total ⚠️

### Cost Alert Setup Complete:
- Email alert at $4.00 (80% of $5)
- Email alert at $5.00 (100% of $5)
- Zero spend budget alert

---

## ⚠️ IMPORTANT: Cost Control

### To Stop Incurring Charges:

**Stop RDS (when not using):**
```powershell
aws rds stop-db-instance --db-instance-identifier climate-health-db
```
(Can be stopped for 7 days, saves Free Tier hours)

**Start RDS (when needed):**
```powershell
aws rds start-db-instance --db-instance-identifier climate-health-db
```

**Delete Everything (if needed):**
See `AWS_CLEANUP.md` for complete deletion steps

---

## 🆘 Troubleshooting

### Issue: Can't connect to RDS
**Fix**: Check security group allows your IP on port 5432

### Issue: Bucket name already exists
**Fix**: Use more unique suffix (date, random numbers)

### Issue: Access Denied errors
**Fix**: Verify IAM user has AdministratorAccess policy

### Issue: AWS CLI not found
**Fix**: Restart PowerShell after installing

### Issue: Migration script fails
**Fix**: Check aws_config.py values are correct

---

## 📞 Support Resources

- **AWS Free Tier**: https://aws.amazon.com/free/
- **AWS Documentation**: https://docs.aws.amazon.com/
- **AWS Support**: Basic support included (forum)
- **Billing Help**: https://console.aws.amazon.com/support/

---

## ✅ Final Checklist Before Declaring Success:

Run this final command to verify everything:

```powershell
python aws_migration_scripts/4_verify_migration.py
```

If you see:
```
🎉 ALL VERIFICATIONS PASSED!

Your AWS migration is complete:
   ✅ Database migrated to RDS
   ✅ Files uploaded to S3
   ✅ SNS alerts configured
   ✅ Secrets stored securely
```

**YOU'RE DONE! 🎉**

Your Climate-Resilient Healthcare System is now running on AWS Free Tier!
