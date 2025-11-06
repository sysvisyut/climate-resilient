# 🚀 AWS Migration Package - README

## 📦 What I've Created for You

I've created a **complete AWS migration package** with detailed guides, automated scripts, and step-by-step instructions to migrate your Climate-Resilient Healthcare System to AWS Free Tier.

---

## 📁 Files Created

### 1. **AWS_SETUP_GUIDE.md** (Main Guide - 15 pages)
Complete manual setup instructions for AWS Console:
- AWS account creation
- IAM user setup
- RDS PostgreSQL database
- S3 buckets
- SNS notifications
- Secrets Manager
- Billing alerts
- Security groups
- Verification steps

**👉 START HERE!**

---

### 2. **AWS_EXECUTION_STEPS.md** (Step-by-Step - 12 pages)
Detailed execution checklist with exact commands:
- 10 phases of migration
- Time estimates for each phase
- Exact values to enter
- Verification steps after each phase
- Troubleshooting tips
- Final success confirmation

**👉 Follow this during migration!**

---

### 3. **AWS_QUICK_REFERENCE.md** (Cheat Sheet - 4 pages)
Quick reference card with:
- Template for saving credentials
- Common commands
- AWS console URLs
- Daily monitoring checklist
- Emergency cleanup commands

**👉 Keep this handy for daily use!**

---

### 4. **aws_config.py** (Configuration File)
Central configuration for all AWS resources:
- Region settings
- S3 bucket names
- RDS endpoints
- SNS topic ARNs
- Secret names
- Free Tier limits

**👉 Update with your actual AWS values!**

---

### 5. **Migration Scripts** (4 Python Scripts)

#### **1_test_aws_connection.py**
Tests AWS credentials and service access:
- ✅ AWS credentials validation
- ✅ S3 access
- ✅ RDS access
- ✅ Secrets Manager access
- ✅ SNS access

#### **2_migrate_database.py**
Migrates SQLite to PostgreSQL RDS:
- Retrieves credentials from Secrets Manager
- Creates PostgreSQL schema
- Migrates all tables (locations, climate, health, hospital, users)
- Verifies data counts

#### **3_upload_to_s3.py**
Uploads local files to S3:
- Uploads raw data files
- Uploads processed data files
- Uploads ML model files
- Verifies uploads

#### **4_verify_migration.py**
Complete verification and cost estimation:
- RDS connection test
- S3 bucket verification
- SNS topic check
- Secrets Manager validation
- Cost estimation (~$0.80/month)

---

### 6. **database_aws.py** (Updated Database Config)
AWS-enabled database connection:
- Automatically retrieves RDS credentials from Secrets Manager
- Falls back to SQLite if AWS is not configured
- Environment variable control (USE_AWS=true/false)
- Connection pooling for PostgreSQL

---

## 🎯 How to Use This Package

### **Phase 1: Manual AWS Console Setup** (2 hours)

1. **Open**: `AWS_SETUP_GUIDE.md` OR `AWS_EXECUTION_STEPS.md`
2. **Follow** Steps 1-7 to create:
   - AWS account
   - IAM user
   - RDS database
   - S3 buckets
   - SNS topic
   - Secrets Manager secrets
   - Billing alerts

3. **Save all credentials** as you go

---

### **Phase 2: Local Configuration** (15 minutes)

1. **Install AWS CLI** (instructions in guides)

2. **Configure AWS CLI**:
   ```powershell
   aws configure
   ```

3. **Install Python dependencies**:
   ```powershell
   pip install boto3 psycopg2-binary
   ```

4. **Update** `aws_config.py` with your actual:
   - S3 bucket names
   - RDS endpoint
   - SNS topic ARN

---

### **Phase 3: Run Migration Scripts** (30 minutes)

```powershell
cd c:/Users/rohit/Desktop/Climate

# Test 1: Verify AWS connection
python aws_migration_scripts/1_test_aws_connection.py

# Test 2: Migrate database
python aws_migration_scripts/2_migrate_database.py

# Test 3: Upload files to S3
python aws_migration_scripts/3_upload_to_s3.py

# Test 4: Verify everything
python aws_migration_scripts/4_verify_migration.py
```

---

### **Phase 4: Verification** (10 minutes)

**All scripts should show**:
- ✅ All tests passed
- ✅ Data migrated successfully
- ✅ Files uploaded
- ✅ Cost: ~$0.80/month

**Final check**:
```powershell
python -c "import boto3, json, psycopg2; sm = boto3.client('secretsmanager', region_name='ap-south-1'); secret = json.loads(sm.get_secret_value(SecretId='climate-health/db/credentials')['SecretString']); conn = psycopg2.connect(host=secret['host'], port=secret['port'], database=secret['dbname'], user=secret['username'], password=secret['password']); cursor = conn.cursor(); cursor.execute('SELECT COUNT(*) FROM locations'); print(f'✅ Connected! Locations: {cursor.fetchone()[0]}'); conn.close()"
```

Should show: `✅ Connected! Locations: 36`

---

## 💰 Free Tier Coverage

### ✅ **100% Free (Forever)**:
- IAM (user management)
- Lambda (1M requests/month)
- SNS (1000 notifications/month)
- S3 requests (20K GET, 2K PUT)

### ✅ **Free for 12 Months**:
- RDS (750 hours/month of db.t3.micro)
- S3 Storage (5 GB)
- EC2 (750 hours/month of t2.micro) - if needed

### ⚠️ **Minimal Cost**:
- Secrets Manager: $0.40/secret/month = **$0.80/month**
  - This is the ONLY service that costs money
  - Necessary for secure credential storage

### **Total Estimated Cost**: ~$0.80/month

---

## 📊 Services You're Using

| Service | Purpose | Free Tier | Your Usage |
|---------|---------|-----------|------------|
| **RDS PostgreSQL** | Database | 750 hrs/mo | ~720 hrs ✅ |
| **S3** | File storage | 5 GB | < 1 GB ✅ |
| **SNS** | Alerts | 1000 notif/mo | < 10 ✅ |
| **Secrets Manager** | Credentials | $0.40/secret | 2 = $0.80 ⚠️ |
| **IAM** | Access control | Free | Free ✅ |
| **Lambda** | Serverless (optional) | 1M req/mo | 0 ✅ |
| **API Gateway** | APIs (optional) | Free tier | 0 ✅ |

---

## 🎓 What You'll Learn

By completing this migration, you'll learn:
- ✅ AWS account and IAM setup
- ✅ RDS database management
- ✅ S3 object storage
- ✅ Secrets Manager for security
- ✅ SNS notifications
- ✅ AWS CLI usage
- ✅ boto3 SDK (Python)
- ✅ PostgreSQL vs SQLite
- ✅ Cost optimization
- ✅ Free Tier monitoring

---

## ⏱️ Time Estimates

| Phase | Duration | Difficulty |
|-------|----------|-----------|
| AWS account setup | 30 min | Easy |
| IAM & security | 20 min | Easy |
| RDS database | 30 min | Medium |
| S3 buckets | 15 min | Easy |
| SNS & Secrets | 20 min | Easy |
| Local setup | 20 min | Easy |
| Run scripts | 30 min | Easy |
| Verification | 15 min | Easy |
| **TOTAL** | **~3 hours** | **Beginner friendly** |

---

## ✅ Success Criteria

You've successfully migrated when:

1. **All 4 migration scripts pass** ✅
2. **Can connect to RDS from Python** ✅
3. **S3 buckets contain your files** ✅
4. **SNS email subscription confirmed** ✅
5. **Billing shows ~$0.80/month** ✅
6. **Can query database via AWS** ✅

---

## 🆘 Troubleshooting

### Common Issues:

**"Access Denied"**
- Solution: Check IAM user has AdministratorAccess policy

**"Bucket already exists"**
- Solution: Use more unique suffix in bucket names

**"Can't connect to RDS"**
- Solution: Check security group allows your IP on port 5432

**"AWS CLI not found"**
- Solution: Restart PowerShell after AWS CLI installation

**"Module boto3 not found"**
- Solution: `pip install boto3`

**"Secret not found"**
- Solution: Create secrets in Secrets Manager first

---

## 📚 Documentation Structure

```
Climate/
├── AWS_SETUP_GUIDE.md           ← Main manual setup guide
├── AWS_EXECUTION_STEPS.md       ← Detailed step-by-step
├── AWS_QUICK_REFERENCE.md       ← Quick commands cheat sheet
├── AWS_MIGRATION_README.md      ← This file
├── aws_config.py                ← Configuration file (UPDATE THIS!)
│
├── aws_migration_scripts/
│   ├── 1_test_aws_connection.py ← Test AWS access
│   ├── 2_migrate_database.py    ← SQLite → PostgreSQL
│   ├── 3_upload_to_s3.py        ← Upload files to S3
│   └── 4_verify_migration.py    ← Final verification
│
└── backend/app/models/
    └── database_aws.py          ← AWS-enabled database config
```

---

## 🚀 Quick Start (TL;DR)

1. **Read**: `AWS_EXECUTION_STEPS.md`
2. **Follow**: All 10 phases
3. **Update**: `aws_config.py` with your values
4. **Run**: All 4 migration scripts
5. **Verify**: Last script shows "ALL PASSED"

**That's it!** 🎉

---

## 💡 Pro Tips

1. **Use Mumbai region (ap-south-1)** - Lowest latency for India
2. **Stop RDS when not using** - Saves Free Tier hours
3. **Monitor billing daily** - First week especially
4. **Set up budget alerts** - Get notified at $4 and $5
5. **Keep credentials CSV safe** - You'll need them
6. **Document your setup** - Fill in QUICK_REFERENCE.md

---

## 📞 Support

- **Guides**: All 3 markdown files have troubleshooting sections
- **AWS Docs**: https://docs.aws.amazon.com/
- **AWS Support**: Basic support included (forums)
- **Billing Help**: https://console.aws.amazon.com/support/

---

## 🎯 Next Steps After Migration

1. **Update backend** to use `database_aws.py` instead of `database.py`
2. **Set environment variable**: `USE_AWS=true`
3. **Test application** with AWS resources
4. **Deploy Lambda functions** (optional, see AWS_MIGRATION.md)
5. **Set up API Gateway** (optional, see AWS_MIGRATION.md)
6. **Configure SageMaker** for ML training (optional)

---

## ⚠️ Important Notes

1. **Secrets Manager costs $0.80/month** - Only non-free service
2. **RDS can be stopped** for up to 7 days to save hours
3. **Monitor Free Tier usage** in billing dashboard
4. **Keep security groups restrictive** - Only allow your IP
5. **Never commit AWS credentials** to git

---

## 🎉 Congratulations!

You now have:
- ✅ Complete AWS migration documentation
- ✅ Automated migration scripts
- ✅ Step-by-step execution guide
- ✅ Quick reference for daily use
- ✅ Cost optimized setup (~$0.80/month)
- ✅ Production-ready AWS infrastructure

**Everything is designed to stay within Free Tier limits!**

---

**Ready to migrate? Start with `AWS_EXECUTION_STEPS.md`** 🚀

---

*Created: 2025-11-01*
*For: Climate-Resilient Healthcare System*
*Region: Asia Pacific (Mumbai) ap-south-1*
