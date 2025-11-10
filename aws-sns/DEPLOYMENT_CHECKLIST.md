# SNS Alerting System - Deployment Checklist

## Pre-Deployment

- [ ] **AWS Account Setup**
  - [ ] AWS account with SNS access
  - [ ] IAM user/role with SNS publish permissions
  - [ ] AWS CLI configured (`aws configure`)

- [ ] **Configuration Files**
  - [ ] Created `aws-sns/.env` from `.env.example`
  - [ ] Set `AWS_REGION` and `AWS_ACCOUNT_ID`
  - [ ] Added admin email addresses
  - [ ] Added hospital staff emails (optional)
  - [ ] Added SMS numbers in E.164 format (optional)

## Deployment Steps

### 1. Install Dependencies

```bash
cd backend
pip install boto3 python-dotenv
```

- [ ] boto3 installed
- [ ] python-dotenv installed

### 2. Create SNS Topics

```bash
cd aws-sns
python3 setup_sns.py
```

Expected output:
```
✓ Created topic: climate-health-risk-alerts
✓ Created topic: climate-resource-shortage-alerts
✓ Subscribed email: admin@example.com
✓ Updated .env with topic ARNs
```

- [ ] Health risk topic created
- [ ] Resource shortage topic created
- [ ] Email subscriptions added
- [ ] SMS subscriptions added
- [ ] `.env` updated with topic ARNs

### 3. Confirm Email Subscriptions

- [ ] Check all email inboxes
- [ ] Click "Confirm subscription" in each email
- [ ] Verify subscription status in AWS console

**To verify:**
```bash
aws sns list-subscriptions-by-topic \
  --topic-arn <YOUR_TOPIC_ARN> \
  --region eu-north-1 \
  --query 'Subscriptions[*].[Endpoint,SubscriptionArn]' \
  --output table
```

### 4. Test Alert System

```bash
cd aws-sns
python3 test_sns_alerts.py
```

- [ ] Test script runs without errors
- [ ] Received test emails
- [ ] Received test SMS (for critical alerts)
- [ ] Alerts appear in AWS SNS console

### 5. Integrate into Backend

- [ ] Import `sns_alerting` module in relevant files
- [ ] Replace console prints with SNS alerts
- [ ] Test integrated alerting in development
- [ ] Verify alerts send correctly

## Post-Deployment Verification

### Check AWS Console

Navigate to: AWS Console → SNS → Topics

- [ ] Both topics exist
- [ ] Topics have subscriptions
- [ ] Subscriptions are "Confirmed"
- [ ] Recent publications show test alerts

### Check Email Delivery

- [ ] Test email received within 1 minute
- [ ] Email format is correct
- [ ] Subject line is descriptive
- [ ] Email body includes all information
- [ ] No emails in spam folder

### Check SMS Delivery (if enabled)

- [ ] Critical test SMS received
- [ ] SMS format is readable
- [ ] Phone number is correct format
- [ ] SMS not delayed (< 30 seconds)

### Test Production Scenarios

- [ ] Health risk alert triggers correctly
- [ ] Resource shortage alert triggers correctly
- [ ] System error alert triggers correctly
- [ ] Severity levels work as expected
- [ ] Metadata is included correctly

## Monitoring Setup

### CloudWatch Metrics

```bash
# View SNS metrics
aws cloudwatch get-metric-statistics \
  --namespace AWS/SNS \
  --metric-name NumberOfNotificationsFailed \
  --dimensions Name=TopicName,Value=climate-health-risk-alerts \
  --start-time 2025-11-01T00:00:00Z \
  --end-time 2025-11-07T23:59:59Z \
  --period 3600 \
  --statistics Sum \
  --region eu-north-1
```

- [ ] SNS metrics visible in CloudWatch
- [ ] No failed notifications
- [ ] Delivery rate is 100%

### Set Up CloudWatch Alarms

```bash
# Alert if SNS delivery fails
aws cloudwatch put-metric-alarm \
  --alarm-name sns-delivery-failures \
  --alarm-description "Alert if SNS message delivery fails" \
  --metric-name NumberOfNotificationsFailed \
  --namespace AWS/SNS \
  --statistic Sum \
  --period 300 \
  --threshold 1 \
  --comparison-operator GreaterThanThreshold \
  --evaluation-periods 1 \
  --region eu-north-1
```

- [ ] CloudWatch alarm created
- [ ] Alarm actions configured
- [ ] Alarm tested

## Security Checklist

- [ ] **IAM Permissions**
  - [ ] Least privilege principle applied
  - [ ] Only required permissions granted
  - [ ] No wildcard permissions

- [ ] **Topic Policies**
  - [ ] Access restricted to application
  - [ ] No public publish access
  - [ ] Cross-account access disabled

- [ ] **Secrets Management**
  - [ ] `.env` file in `.gitignore`
  - [ ] No credentials in code
  - [ ] AWS credentials secure

- [ ] **Data Protection**
  - [ ] No PII in alert messages
  - [ ] Sensitive data redacted
  - [ ] HIPAA compliance reviewed

## Cost Management

- [ ] **Estimate Monthly Costs**
  - [ ] Alert volume estimated
  - [ ] SMS usage calculated
  - [ ] Budget allocated

- [ ] **Set Budget Alerts**
  ```bash
  aws budgets create-budget \
    --account-id YOUR_ACCOUNT_ID \
    --budget file://sns-budget.json
  ```

- [ ] **Monitor Spending**
  - [ ] AWS Cost Explorer enabled
  - [ ] SNS costs tracked
  - [ ] Unusual spikes detected

## Rollback Plan

If issues occur:

1. **Disable Alerting**
   ```env
   # In .env
   ENABLE_EMAIL_ALERTS=false
   ENABLE_SMS_ALERTS=false
   ```

2. **Revert Code Changes**
   ```bash
   git revert <commit>
   ```

3. **Delete Topics** (if needed)
   ```bash
   aws sns delete-topic \
     --topic-arn <TOPIC_ARN> \
     --region eu-north-1
   ```

- [ ] Rollback procedure documented
- [ ] Rollback tested in staging
- [ ] Emergency contacts updated

## Documentation

- [ ] README.md updated
- [ ] Integration examples documented
- [ ] API endpoints documented
- [ ] Troubleshooting guide created
- [ ] Team trained on new system

## Sign-Off

- [ ] Development team approval
- [ ] Operations team approval
- [ ] Security team review
- [ ] Stakeholder notification

---

**Deployment Date**: ________________

**Deployed By**: ________________

**Verified By**: ________________

**Status**: ☐ Not Started | ☐ In Progress | ☐ Complete

**Notes**:
_______________________________________________
_______________________________________________
_______________________________________________
