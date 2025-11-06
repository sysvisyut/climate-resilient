# ⚡ AWS Migration - Quick Reference Card

## 📝 Save These Values

### IAM User:
```
Username: climate-admin
Password: ___________________________
Console URL: https://____________.signin.aws.amazon.com/console
```

### Access Keys:
```
Access Key ID: AKIA____________________
Secret Access Key: _______________________________________
```

### RDS Database:
```
Endpoint: climate-health-db.____________.ap-south-1.rds.amazonaws.com
Username: postgres
Password: ___________________________
Database: climate_health
Port: 5432
```

### S3 Buckets:
```
Raw Data: climate-health-raw-data-_______________
Processed: climate-health-processed-data-_______________
Models: climate-health-models-_______________
```

### SNS Topic:
```
ARN: arn:aws:sns:ap-south-1:____________:climate-health-alerts
Email: ___________________________
```

### Secrets Manager:
```
DB Credentials: climate-health/db/credentials
JWT Secret: climate-health/api/jwt-secret
```

---

## 🚀 Quick Commands

### AWS CLI Setup:
```powershell
aws configure
# Enter: Access Key, Secret Key, ap-south-1, json
```

### Test Connection:
```powershell
aws sts get-caller-identity
aws s3 ls
aws rds describe-db-instances
```

### Run Migration Scripts:
```powershell
cd c:/Users/rohit/Desktop/Climate
python aws_migration_scripts/1_test_aws_connection.py
python aws_migration_scripts/2_migrate_database.py
python aws_migration_scripts/3_upload_to_s3.py
python aws_migration_scripts/4_verify_migration.py
```

---

## 💰 Free Tier Limits

| Service | Limit | Your Usage |
|---------|-------|------------|
| RDS | 750 hrs/month | ~720 hrs ✅ |
| S3 Storage | 5 GB | < 1 GB ✅ |
| Lambda | 1M requests | 0 (not deployed) |
| SNS | 1000 notifications | < 10 ✅ |
| Secrets Manager | $0.40/secret | 2 secrets = $0.80/mo ⚠️ |

**Total Cost**: ~$0.80/month

---

## 🎯 Daily Checks (30 seconds)

1. **Billing Dashboard**: https://console.aws.amazon.com/billing/
   - Current charges should be: ~$0.00 - $0.80
   
2. **Free Tier Usage**: Console → Billing → Free Tier
   - All should be < 80%

---

## ⚙️ Common Operations

### Stop RDS (Save Money):
```powershell
aws rds stop-db-instance --db-instance-identifier climate-health-db
```

### Start RDS:
```powershell
aws rds start-db-instance --db-instance-identifier climate-health-db
```

### List S3 Files:
```powershell
aws s3 ls s3://climate-health-raw-data-YOUR-ID/ --recursive
```

### Send Test SNS Alert:
```powershell
aws sns publish --topic-arn arn:aws:sns:ap-south-1:ACCOUNT:climate-health-alerts --message "Test alert"
```

---

## 🔍 Verification Checklist

- [ ] AWS account created (Mumbai region)
- [ ] IAM user created and logged in
- [ ] Billing alerts active (2 budgets)
- [ ] RDS database running (Available status)
- [ ] 3 S3 buckets created
- [ ] SNS topic with confirmed subscription
- [ ] 2 secrets in Secrets Manager
- [ ] AWS CLI configured
- [ ] All 4 migration scripts passed

---

## 📊 AWS Console URLs

| Service | URL |
|---------|-----|
| **Dashboard** | https://console.aws.amazon.com/ |
| **RDS** | https://ap-south-1.console.aws.amazon.com/rds/ |
| **S3** | https://s3.console.aws.amazon.com/s3/buckets |
| **SNS** | https://ap-south-1.console.aws.amazon.com/sns/ |
| **Secrets** | https://ap-south-1.console.aws.amazon.com/secretsmanager/ |
| **IAM** | https://console.aws.amazon.com/iam/ |
| **Billing** | https://console.aws.amazon.com/billing/ |

---

## ⚠️ Emergency: Delete Everything

If you need to delete all resources to stop charges:

```powershell
# Delete RDS
aws rds delete-db-instance --db-instance-identifier climate-health-db --skip-final-snapshot

# Empty and delete S3 buckets
aws s3 rm s3://climate-health-raw-data-YOUR-ID --recursive
aws s3 rb s3://climate-health-raw-data-YOUR-ID
# Repeat for other 2 buckets

# Delete SNS topic
aws sns delete-topic --topic-arn arn:aws:sns:ap-south-1:ACCOUNT:climate-health-alerts

# Delete secrets
aws secretsmanager delete-secret --secret-id climate-health/db/credentials
aws secretsmanager delete-secret --secret-id climate-health/api/jwt-secret
```

---

## 📞 Help & Support

- **AWS Documentation**: https://docs.aws.amazon.com/
- **AWS Free Tier FAQ**: https://aws.amazon.com/free/free-tier-faqs/
- **Cost Calculator**: https://calculator.aws/
- **Support (Basic)**: https://console.aws.amazon.com/support/

---

## 🎓 Learning Resources

- **RDS Tutorial**: https://docs.aws.amazon.com/rds/
- **S3 Guide**: https://docs.aws.amazon.com/s3/
- **Lambda**: https://docs.aws.amazon.com/lambda/
- **boto3 Docs**: https://boto3.amazonaws.com/v1/documentation/api/latest/index.html

---

**Keep this document handy for quick reference!**
