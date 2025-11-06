# 🚀 AWS Setup Guide - Climate-Resilient Healthcare System
## Complete Step-by-Step Instructions for AWS Migration

---

## 📋 Table of Contents
1. [Prerequisites](#prerequisites)
2. [AWS Account Setup](#aws-account-setup)
3. [Manual AWS Console Configuration](#manual-aws-console-configuration)
4. [Install Required Tools](#install-required-tools)
5. [Configure AWS Credentials](#configure-aws-credentials)
6. [Database Migration (RDS)](#database-migration-rds)
7. [Storage Setup (S3)](#storage-setup-s3)
8. [Lambda Functions](#lambda-functions)
9. [API Gateway Setup](#api-gateway-setup)
10. [SageMaker Setup](#sagemaker-setup)
11. [SNS Alerts](#sns-alerts)
12. [IAM & Secrets Manager](#iam-secrets-manager)
13. [Billing Alerts](#billing-alerts)
14. [Verification Steps](#verification-steps)

---

## 🎯 Prerequisites

### What You Need:
- ✅ Valid email address
- ✅ Phone number for verification
- ✅ Credit/Debit card (for AWS account verification - won't be charged if you stay in Free Tier)
- ✅ Government ID (for some regions)

---

## 🔐 AWS Account Setup

### Step 1: Create AWS Account

1. **Go to AWS Console**
   - Visit: https://aws.amazon.com/
   - Click **"Create an AWS Account"**

2. **Enter Account Details**
   ```
   Root user email: [Your email]
   AWS account name: climate-health-system
   ```

3. **Choose Account Type**
   - Select: **Personal** (for development)
   - Or: **Professional** (for production)

4. **Enter Contact Information**
   ```
   Full Name: [Your name]
   Phone Number: [Your number with country code]
   Country: India
   Address: [Your address]
   City: [Your city]
   State: [Your state]
   Postal Code: [Your PIN code]
   ```

5. **Payment Information**
   - Enter credit/debit card details
   - ⚠️ **Note**: Card is for verification only
   - You won't be charged if staying within Free Tier

6. **Identity Verification**
   - Enter phone number
   - Choose: Call or SMS verification
   - Enter the verification code received

7. **Select Support Plan**
   - Choose: **Basic Support - Free**
   - (You can upgrade later if needed)

8. **Wait for Activation**
   - Usually takes 5-10 minutes
   - Check your email for confirmation

### Step 2: Sign In to AWS Console

1. Go to: https://console.aws.amazon.com/
2. Enter your root email and password
3. **IMPORTANT**: You're now in the AWS Console!

---

## ⚙️ Manual AWS Console Configuration

### 🌍 Step 3: Choose Your Region

**IMPORTANT: Always use the same region for all services!**

1. In AWS Console, top-right corner, click the region dropdown
2. **Recommended for India**: `ap-south-1` (Mumbai)
3. Alternative: `ap-southeast-1` (Singapore)

**✅ VERIFY**: Region shows "Asia Pacific (Mumbai) ap-south-1"

---

### 👤 Step 4: Create IAM User (DO THIS FIRST!)

**⚠️ NEVER use root account for daily operations!**

1. **Navigate to IAM**
   - In AWS Console search bar, type: `IAM`
   - Click: **IAM (Identity and Access Management)**

2. **Create New User**
   - Left sidebar → Click **Users**
   - Click **Create user** button
   
3. **User Details**
   ```
   User name: climate-admin
   ✓ Provide user access to the AWS Management Console
   Console password: Custom password
   Password: [Create a strong password]
   ☐ Users must create a new password at next sign-in (uncheck for now)
   ```
   - Click **Next**

4. **Set Permissions**
   - Choose: **Attach policies directly**
   - Search and select these policies:
     ```
     ✓ AdministratorAccess (for initial setup)
     ```
   - Click **Next**
   - Click **Create user**

5. **Save Credentials**
   - **IMPORTANT**: Download the CSV with credentials
   - Save it securely: `climate-admin-credentials.csv`
   - Contains: Console sign-in URL, username, password

6. **Sign Out from Root Account**
   - Top-right corner → Click your account
   - Click **Sign out**

7. **Sign In with IAM User**
   - Use the Console sign-in URL from CSV
   - Format: `https://[account-id].signin.aws.amazon.com/console`
   - Username: `climate-admin`
   - Password: [Your password]

**✅ VERIFY**: You're now logged in as IAM user (shows "climate-admin" in top-right)

---

### 🔑 Step 5: Create Access Keys for Programmatic Access

1. **In IAM Console**
   - Click **Users** → Click **climate-admin**
   - Go to **Security credentials** tab
   - Scroll to **Access keys**

2. **Create Access Key**
   - Click **Create access key**
   - Use case: Select **Command Line Interface (CLI)**
   - Check: ☐ I understand the above recommendation
   - Click **Next**
   - Description: `Climate Health System CLI`
   - Click **Create access key**

3. **Download Access Key**
   - **CRITICAL**: Download CSV file
   - Contains:
     ```
     Access key ID: AKIA...
     Secret access key: wJalr...
     ```
   - **Save this file securely!** You can't retrieve the secret later

**✅ VERIFY**: You have `climate-admin_accessKeys.csv` saved

---

### 💰 Step 6: Set Up Billing Alerts (CRITICAL!)

**Do this NOW to avoid surprise charges!**

1. **Enable Billing Alerts**
   - Click your account name (top-right)
   - Click **Account**
   - Scroll to **IAM User and Role Access to Billing Information**
   - Click **Edit**
   - Check: ☑ Activate IAM Access
   - Click **Update**

2. **Go to Billing Dashboard**
   - Search bar → Type: `Billing`
   - Click **Billing and Cost Management**

3. **Create Budget**
   - Left sidebar → Click **Budgets**
   - Click **Create budget**
   - Template: **Zero spend budget**
   - Budget name: `climate-health-free-tier-alert`
   - Email: [Your email]
   - Click **Create budget**

4. **Create Cost Alert**
   - Click **Create budget** again
   - Template: **Monthly cost budget**
   - Budget name: `climate-health-cost-limit`
   - Budget amount: `$5.00` (or your limit)
   - Email: [Your email]
   - Alert threshold: `80%` and `100%`
   - Click **Create budget**

**✅ VERIFY**: You have 2 budgets created and will receive email alerts

---

### 📦 Step 7: Create S3 Buckets

1. **Navigate to S3**
   - Search bar → Type: `S3`
   - Click **S3**

2. **Create Raw Data Bucket**
   - Click **Create bucket**
   - Bucket name: `climate-health-raw-data-[your-unique-id]`
     - Example: `climate-health-raw-data-rohit-2025`
     - Must be globally unique!
   - Region: `Asia Pacific (Mumbai) ap-south-1`
   - Object Ownership: **ACLs disabled**
   - Block all public access: ☑ Checked (keep private)
   - Bucket Versioning: **Disable** (to save costs)
   - Encryption: **Server-side encryption with Amazon S3 managed keys (SSE-S3)**
   - Click **Create bucket**

3. **Create Processed Data Bucket**
   - Repeat above with name: `climate-health-processed-data-[your-unique-id]`

4. **Create Models Bucket**
   - Repeat above with name: `climate-health-models-[your-unique-id]`

**✅ VERIFY**: You have 3 S3 buckets in Mumbai region

---

### 🗄️ Step 8: Create RDS PostgreSQL Database

**⚠️ This uses Free Tier: 750 hours/month of db.t3.micro**

1. **Navigate to RDS**
   - Search bar → Type: `RDS`
   - Click **RDS**

2. **Create Database**
   - Click **Create database**

3. **Engine Options**
   - Engine type: **PostgreSQL**
   - Edition: **PostgreSQL**
   - Version: **PostgreSQL 15.4** (or latest)
   - Templates: **☑ Free tier**

4. **Settings**
   ```
   DB instance identifier: climate-health-db
   Master username: postgres
   Master password: [Create strong password]
   Confirm password: [Same password]
   ```
   - **SAVE THIS PASSWORD!**

5. **Instance Configuration**
   - DB instance class: **db.t3.micro** (Free Tier eligible)
   - Storage type: **General Purpose SSD (gp2)**
   - Allocated storage: **20 GiB** (Free Tier limit)
   - ☐ Enable storage autoscaling (uncheck to avoid costs)

6. **Connectivity**
   - Compute resource: **Don't connect to an EC2 compute resource**
   - VPC: **Default VPC**
   - Subnet group: **default**
   - Public access: **Yes** (for development)
   - VPC security group: **Create new**
   - New VPC security group name: `climate-health-db-sg`
   - Availability Zone: **No preference**

7. **Database Authentication**
   - **Password authentication**

8. **Additional Configuration**
   - Initial database name: `climate_health`
   - ☐ Enable automated backups (uncheck to save costs for dev)
   - ☐ Enable encryption (uncheck for dev)

9. **Click Create Database**
   - Wait 5-10 minutes for creation

**✅ VERIFY**: Database status shows "Available"

---

### 🔌 Step 9: Configure Database Security Group

**Allow your IP to connect to database**

1. **Get Database Endpoint**
   - In RDS Console → Click your database
   - Copy **Endpoint**: `climate-health-db.xxxxxxxx.ap-south-1.rds.amazonaws.com`

2. **Edit Security Group**
   - Scroll to **Connectivity & security** tab
   - Click the security group link: `climate-health-db-sg`

3. **Add Inbound Rule**
   - Click **Edit inbound rules**
   - Click **Add rule**
   - Type: **PostgreSQL**
   - Port: **5432** (auto-filled)
   - Source: **My IP** (auto-detects your current IP)
   - Description: `My development machine`
   - Click **Save rules**

**✅ VERIFY**: Security group allows port 5432 from your IP

---

### 🔔 Step 10: Create SNS Topic for Alerts

1. **Navigate to SNS**
   - Search bar → Type: `SNS`
   - Click **Simple Notification Service**

2. **Create Topic**
   - Left sidebar → Click **Topics**
   - Click **Create topic**
   - Type: **Standard**
   - Name: `climate-health-alerts`
   - Display name: `Climate Health Alerts`
   - Click **Create topic**

3. **Create Subscription**
   - Click **Create subscription**
   - Protocol: **Email**
   - Endpoint: [Your email address]
   - Click **Create subscription**

4. **Confirm Subscription**
   - Check your email
   - Click the confirmation link
   - Status should change to **Confirmed**

**✅ VERIFY**: Subscription status is "Confirmed"

---

### 🔐 Step 11: Set Up Secrets Manager

1. **Navigate to Secrets Manager**
   - Search bar → Type: `Secrets Manager`
   - Click **Secrets Manager**

2. **Store Database Credentials**
   - Click **Store a new secret**
   - Secret type: **Credentials for RDS database**
   - User name: `postgres`
   - Password: [Your RDS password]
   - Database: Select your RDS instance
   - Click **Next**
   - Secret name: `climate-health/db/credentials`
   - Description: `Database credentials for Climate Health System`
   - Click **Next**
   - Disable automatic rotation (for dev)
   - Click **Next**
   - Click **Store**

3. **Store JWT Secret**
   - Click **Store a new secret**
   - Secret type: **Other type of secret**
   - Key/value pairs:
     ```
     Key: JWT_SECRET
     Value: [Generate random string - use password generator]
     ```
   - Click **Next**
   - Secret name: `climate-health/api/jwt-secret`
   - Click **Next** → **Next** → **Store**

**✅ VERIFY**: You have 2 secrets stored

---

## 💻 Install Required Tools

### Step 12: Install AWS CLI

**For Windows:**

1. **Download AWS CLI**
   - Visit: https://aws.amazon.com/cli/
   - Download: AWS CLI MSI installer for Windows (64-bit)

2. **Install**
   - Run the downloaded MSI file
   - Follow installation wizard
   - Click **Next** → **Next** → **Install** → **Finish**

3. **Verify Installation**
   ```powershell
   aws --version
   ```
   - Should show: `aws-cli/2.x.x ...`

**✅ VERIFY**: AWS CLI is installed

---

### Step 13: Configure AWS CLI with Your Credentials

1. **Open PowerShell/Command Prompt**

2. **Run Configure Command**
   ```powershell
   aws configure
   ```

3. **Enter Credentials** (from your downloaded CSV file)
   ```
   AWS Access Key ID [None]: AKIA................
   AWS Secret Access Key [None]: wJalr...............
   Default region name [None]: ap-south-1
   Default output format [None]: json
   ```

4. **Verify Configuration**
   ```powershell
   aws sts get-caller-identity
   ```
   - Should show your account ID and user

**✅ VERIFY**: Command returns your AWS account details

---

### Step 14: Install Additional Tools

1. **Install boto3 (AWS SDK for Python)**
   ```powershell
   pip install boto3
   ```

2. **Install psycopg2 (PostgreSQL driver)**
   ```powershell
   pip install psycopg2-binary
   ```

3. **Verify Installation**
   ```powershell
   python -c "import boto3; print(boto3.__version__)"
   python -c "import psycopg2; print(psycopg2.__version__)"
   ```

**✅ VERIFY**: Both libraries import successfully

---

## 🧪 Verification Steps

### Step 15: Test All AWS Connections

Run these commands one by one to verify everything is set up correctly:

#### Test 1: AWS CLI Connection
```powershell
aws sts get-caller-identity
```
**Expected**: Shows your UserId, Account, Arn

#### Test 2: List S3 Buckets
```powershell
aws s3 ls
```
**Expected**: Shows your 3 buckets

#### Test 3: Check RDS Status
```powershell
aws rds describe-db-instances --db-instance-identifier climate-health-db
```
**Expected**: Shows database details with status "available"

#### Test 4: List SNS Topics
```powershell
aws sns list-topics
```
**Expected**: Shows your climate-health-alerts topic

#### Test 5: Test S3 Upload
```powershell
echo "Test file" > test.txt
aws s3 cp test.txt s3://climate-health-raw-data-[your-id]/test.txt
aws s3 ls s3://climate-health-raw-data-[your-id]/
```
**Expected**: File uploads and lists successfully

#### Test 6: Test Database Connection
I'll provide a Python script for this in the next step.

---

## 📊 Summary Checklist

Before proceeding to migration scripts, verify ALL these are complete:

- [ ] AWS account created and activated
- [ ] IAM user `climate-admin` created
- [ ] Access keys downloaded and saved
- [ ] AWS CLI installed and configured
- [ ] Region set to `ap-south-1` (Mumbai)
- [ ] Billing alerts created (2 budgets)
- [ ] S3 buckets created (3 buckets)
- [ ] RDS PostgreSQL database created
- [ ] Database security group configured
- [ ] SNS topic created and email confirmed
- [ ] Secrets Manager has 2 secrets stored
- [ ] boto3 and psycopg2 installed
- [ ] All verification tests passed

---

## 🎯 What's Next

Once ALL the above checkboxes are ✓, you're ready to:

1. **Run database migration script** - Migrate SQLite to PostgreSQL
2. **Upload data to S3** - Move local files to cloud
3. **Deploy Lambda functions** - Set up serverless compute
4. **Configure API Gateway** - Expose your APIs
5. **Update application config** - Point to AWS resources

**I'll provide all these scripts in the next files!**

---

## 💡 Cost Monitoring Tips

### Daily Checks:
1. Go to **Billing Dashboard**
2. Check **Bills** → Current month charges
3. Should show: $0.00 if within Free Tier

### Weekly Checks:
1. Go to **Cost Explorer**
2. Review service-wise costs
3. Look for any unexpected services running

### Monthly Checks:
1. Review **Free Tier usage**
2. Go to: Billing → Free Tier
3. Check usage percentages for each service

---

## ⚠️ Important Warnings

1. **STOP services when not using!**
   - RDS: Stop database (can be stopped for 7 days)
   - EC2: Stop instances when not needed
   - SageMaker: Delete endpoints after use

2. **Delete test resources**
   - Empty S3 buckets if doing test uploads
   - Delete failed CloudFormation stacks
   - Remove unused security groups

3. **Monitor Free Tier limits**
   - RDS: 750 hours/month (run 1 instance 24/7 = 720 hours)
   - S3: 5 GB storage
   - Lambda: 1 million requests/month
   - RDS Storage: 20 GB

---

## 🆘 Troubleshooting

### Issue: Can't connect to RDS
**Solution**: Check security group inbound rules for port 5432

### Issue: S3 bucket name already exists
**Solution**: Add more unique suffix (date, random numbers)

### Issue: Billing alerts not working
**Solution**: Verify email subscription is confirmed

### Issue: AWS CLI not found
**Solution**: Restart terminal after installation

---

**Next:** Proceed to `AWS_MIGRATION_SCRIPTS.md` for automation scripts!
