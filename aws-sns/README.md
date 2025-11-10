# AWS SNS Alerting System for Climate-Resilient Healthcare

Complete implementation of AWS Simple Notification Service (SNS) for automated alerting.

## 📋 Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Quick Start](#quick-start)
- [Configuration](#configuration)
- [Usage Examples](#usage-examples)
- [Testing](#testing)
- [Integration Guide](#integration-guide)
- [Best Practices](#best-practices)
- [Troubleshooting](#troubleshooting)

## 🎯 Overview

This alerting system replaces console logging with AWS SNS notifications, providing:
- **Email alerts** for all important events
- **SMS alerts** for critical situations
- **Severity-based routing** (DEBUG, INFO, WARNING, ERROR, CRITICAL)
- **Alert categorization** (Health Risk, Resource Shortage, System Error, Data Quality)
- **Structured messaging** with metadata
- **Failover to console** if SNS is unavailable

## ✨ Features

### Alert Types
1. **Health Risk Alerts** - Disease outbreak predictions, elevated risk warnings
2. **Resource Shortage Alerts** - Hospital beds, medical equipment, staff shortages
3. **Data Quality Alerts** - Missing data, anomalies, validation issues
4. **System Error Alerts** - API failures, model errors, infrastructure issues

### Severity Levels
- **DEBUG** (0) - Development/diagnostic information
- **INFO** (1) - Routine notifications
- **WARNING** (2) - Attention needed, not urgent
- **ERROR** (3) - Problems requiring investigation
- **CRITICAL** (4) - Immediate action required (triggers SMS)

### Smart Routing
- Health risk and prediction alerts → Health Risk topic
- Resource and system alerts → Resource Shortage topic
- Critical severity → SMS + Email
- Lower severity → Email only

## 🚀 Quick Start

### 1. Set Up Configuration

```bash
cd aws-sns
cp .env.example .env
```

Edit `.env` with your settings:

```env
AWS_REGION=eu-north-1
AWS_ACCOUNT_ID=457151800683

# Email addresses (comma-separated)
ADMIN_EMAIL_ADDRESSES=admin@hospital.com,manager@hospital.com
HOSPITAL_EMAIL_ADDRESSES=staff@hospital.com

# SMS numbers (E.164 format: +countrycode+number)
ADMIN_SMS_NUMBERS=+1234567890
URGENT_SMS_NUMBERS=+1234567890

# Alert settings
ENABLE_EMAIL_ALERTS=true
ENABLE_SMS_ALERTS=true
ALERT_MIN_SEVERITY=INFO
SMS_MIN_SEVERITY=CRITICAL
```

### 2. Create SNS Topics and Subscriptions

```bash
cd aws-sns
python3 setup_sns.py
```

This will:
- Create two SNS topics (health risk & resource shortage)
- Subscribe email addresses (requires confirmation)
- Subscribe SMS numbers
- Update .env with topic ARNs

### 3. Confirm Email Subscriptions

Check email inboxes for AWS SNS subscription confirmation emails and click "Confirm subscription".

### 4. Test Alerts

```bash
python3 test_sns_alerts.py
```

This sends test alerts through both topics to verify configuration.

### 5. Integrate into Backend

```python
from app.utils.sns_alerting import health_risk_alert, AlertSeverity

# Send a health risk alert
health_risk_alert(
    location="Mumbai, Maharashtra",
    disease="Dengue",
    risk_level="HIGH",
    prediction=0.85,
    severity=AlertSeverity.WARNING
)
```

## ⚙️ Configuration

### Environment Variables

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `AWS_REGION` | AWS region for SNS | `eu-north-1` | Yes |
| `AWS_ACCOUNT_ID` | Your AWS account ID | - | Yes |
| `SNS_HEALTH_RISK_TOPIC_ARN` | Health risk topic ARN | - | Auto-filled |
| `SNS_RESOURCE_SHORTAGE_TOPIC_ARN` | Resource topic ARN | - | Auto-filled |
| `ADMIN_EMAIL_ADDRESSES` | Admin emails (comma-separated) | - | Optional |
| `HOSPITAL_EMAIL_ADDRESSES` | Hospital staff emails | - | Optional |
| `ADMIN_SMS_NUMBERS` | SMS numbers for admins | - | Optional |
| `URGENT_SMS_NUMBERS` | Critical alert SMS | - | Optional |
| `ENABLE_EMAIL_ALERTS` | Enable email notifications | `true` | Optional |
| `ENABLE_SMS_ALERTS` | Enable SMS notifications | `true` | Optional |
| `ALERT_MIN_SEVERITY` | Minimum severity for alerts | `INFO` | Optional |
| `SMS_MIN_SEVERITY` | Minimum severity for SMS | `CRITICAL` | Optional |

## 📖 Usage Examples

### Basic Alert

```python
from app.utils.sns_alerting import send_alert, AlertSeverity, AlertType

send_alert(
    title="System Started",
    message="The application has started successfully",
    severity=AlertSeverity.INFO,
    alert_type=AlertType.HEALTH_RISK
)
```

### Health Risk Alert

```python
from app.utils.sns_alerting import health_risk_alert, AlertSeverity

health_risk_alert(
    location="Delhi NCR",
    disease="Heat Stroke",
    risk_level="CRITICAL",
    prediction=0.92,
    severity=AlertSeverity.CRITICAL  # Will trigger SMS
)
```

### Resource Shortage Alert

```python
from app.utils.sns_alerting import resource_shortage_alert, AlertSeverity

resource_shortage_alert(
    location="AIIMS Delhi",
    resource_type="ICU Beds",
    available=5,
    required=50,
    severity=AlertSeverity.CRITICAL
)
```

### Data Quality Alert

```python
from app.utils.sns_alerting import data_quality_alert, AlertSeverity

data_quality_alert(
    dataset="climate_data",
    issue="Missing temperature data for 15 locations",
    severity=AlertSeverity.WARNING
)
```

### System Error Alert

```python
from app.utils.sns_alerting import system_error_alert, AlertSeverity

try:
    # ... code that might fail ...
    result = call_external_api()
except Exception as e:
    system_error_alert(
        component="Weather API",
        error_message=f"API call failed: {str(e)}",
        severity=AlertSeverity.ERROR
    )
```

### With Metadata

```python
from app.utils.sns_alerting import send_alert, AlertSeverity, AlertType

send_alert(
    title="Unusual Activity Detected",
    message="Spike in dengue cases detected in multiple locations",
    severity=AlertSeverity.WARNING,
    alert_type=AlertType.HEALTH_RISK,
    metadata={
        'affected_locations': 25,
        'case_increase': '150%',
        'time_period': '24 hours',
        'recommended_action': 'Increase surveillance'
    }
)
```

## 🧪 Testing

### Test All Alerts

```bash
cd aws-sns
python3 test_sns_alerts.py
```

### Test Individual Components

```python
# Test basic functionality
from app.utils.sns_alerting import SNSAlerter, AlertSeverity, AlertType

alerter = SNSAlerter()

# Send a test alert
alerter.send_alert(
    title="Test Alert",
    message="This is a test",
    severity=AlertSeverity.INFO,
    alert_type=AlertType.HEALTH_RISK
)
```

### Verify Delivery

1. **Email**: Check inbox for alerts (check spam folder too)
2. **SMS**: Check phone for text messages
3. **AWS Console**: 
   - Go to SNS → Topics → Your Topic
   - Check "Recent Publications"
   - View delivery status in "Subscriptions"

## 🔌 Integration Guide

### Replace Console Prints

**Before:**
```python
if risk_score > 0.7:
    print(f"High risk detected: {disease} in {location}")
```

**After:**
```python
from app.utils.sns_alerting import health_risk_alert, AlertSeverity

if risk_score > 0.7:
    health_risk_alert(
        location=location_name,
        disease=disease,
        risk_level="HIGH",
        prediction=risk_score,
        severity=AlertSeverity.WARNING
    )
```

### In FastAPI Endpoints

```python
from fastapi import APIRouter, HTTPException
from app.utils.sns_alerting import system_error_alert, AlertSeverity

router = APIRouter()

@router.get("/predictions/{location_id}")
async def get_predictions(location_id: int):
    try:
        predictions = generate_predictions(location_id)
        
        # Alert on high risk
        if predictions['max_risk'] > 0.8:
            health_risk_alert(
                location=predictions['location_name'],
                disease=predictions['primary_disease'],
                risk_level='HIGH',
                prediction=predictions['max_risk'],
                severity=AlertSeverity.WARNING
            )
        
        return predictions
        
    except Exception as e:
        system_error_alert(
            component="Predictions API",
            error_message=f"Failed for location {location_id}: {str(e)}",
            severity=AlertSeverity.ERROR
        )
        raise HTTPException(status_code=500, detail=str(e))
```

### In Batch Jobs

```python
from app.utils.sns_alerting import send_alert, AlertType, AlertSeverity

def daily_risk_assessment():
    """Run daily and send summary alerts"""
    high_risk_locations = []
    
    for location in get_all_locations():
        risk = calculate_risk(location)
        if risk > 0.75:
            high_risk_locations.append(location)
    
    if high_risk_locations:
        summary = "\\n".join([f"- {loc.name}" for loc in high_risk_locations])
        
        send_alert(
            title=f"Daily Summary: {len(high_risk_locations)} High-Risk Locations",
            message=f"Locations requiring attention:\\n\\n{summary}",
            severity=AlertSeverity.WARNING,
            alert_type=AlertType.HEALTH_RISK,
            metadata={'count': len(high_risk_locations)}
        )
```

## 📚 Best Practices

### 1. Choose Appropriate Severity

- **DEBUG**: Development only, verbose logging
- **INFO**: Routine operations, successful completions
- **WARNING**: Potential issues, elevated metrics
- **ERROR**: Failures requiring investigation
- **CRITICAL**: Immediate action needed, service degradation

### 2. Prevent Alert Fatigue

```python
# Don't alert on every minor event
if temperature > 35:  # Don't do this for every reading
    send_alert(...)

# Instead, alert on trends or thresholds
if consecutive_high_temp_days > 5:
    send_alert(...)
```

### 3. Include Actionable Information

```python
# Bad: Vague message
send_alert(title="Problem", message="Something is wrong")

# Good: Specific with context
send_alert(
    title="ICU Capacity at 90%",
    message="AIIMS Delhi ICU at 90% capacity (45/50 beds occupied). "
            "Expected to reach 100% in 6 hours based on current admission rate.",
    metadata={'current_capacity': '90%', 'time_to_full': '6 hours'}
)
```

### 4. Use Metadata

```python
send_alert(
    title="Alert Title",
    message="Description",
    metadata={
        'location_id': 123,
        'timestamp': datetime.now().isoformat(),
        'source': 'prediction_model',
        'version': '2.1'
    }
)
```

### 5. Test Before Deploying

```python
# Use a test instance that doesn't send real alerts
alerter = SNSAlerter(enable_sns=False)  # Console only
alerter.send_alert(...)  # Will print but not send SNS
```

## 🔧 Troubleshooting

### No Emails Received

1. **Check subscription confirmation**:
   ```bash
   aws sns list-subscriptions-by-topic \
     --topic-arn arn:aws:sns:REGION:ACCOUNT:TOPIC \
     --region REGION
   ```
   Status should be "Confirmed", not "PendingConfirmation"

2. **Check spam folder**: SNS emails might be filtered

3. **Verify topic ARN**: Check `.env` has correct ARNs

4. **Check AWS credentials**: Ensure publish permissions

### No SMS Received

1. **Verify phone number format**: Must be E.164 (+countrycode+number)
2. **Check SMS spending limits**: AWS has default limits
3. **Verify region supports SMS**: Some regions don't support SMS
4. **Check subscriptions**: SMS subscriptions should be confirmed

### Alerts Not Sending

1. **Check enable flags**:
   ```env
   ENABLE_EMAIL_ALERTS=true
   ENABLE_SMS_ALERTS=true
   ```

2. **Check severity threshold**:
   ```env
   ALERT_MIN_SEVERITY=INFO  # Lower severity = more alerts
   ```

3. **Check AWS permissions**:
   ```bash
   aws sns publish \
     --topic-arn arn:aws:sns:REGION:ACCOUNT:TOPIC \
     --message "Test" \
     --region REGION
   ```

4. **Check CloudWatch logs**:
   ```bash
   aws logs tail /aws/lambda/YOUR_FUNCTION --follow
   ```

### Import Errors

If you see "Import could not be resolved":

```python
# Make sure aws-sns/.env exists and has topic ARNs
# Run setup_sns.py first
```

## 💰 Cost Estimation

### SNS Pricing (as of 2024)

- **Email**: $2 per 100,000 emails
- **SMS**: $0.00645 per SMS (US, varies by country)
- **HTTP/HTTPS**: $0.60 per 1 million notifications

### Example Monthly Costs

**Low Volume** (100 alerts/day):
- 3,000 emails/month: $0.06
- 30 SMS/month: $0.19
- **Total: ~$0.25/month**

**Medium Volume** (1,000 alerts/day):
- 30,000 emails/month: $0.60
- 100 SMS/month: $0.65
- **Total: ~$1.25/month**

**High Volume** (10,000 alerts/day):
- 300,000 emails/month: $6.00
- 500 SMS/month: $3.23
- **Total: ~$9.23/month**

## 📝 File Structure

```
aws-sns/
├── .env.example          # Configuration template
├── .env                  # Your configuration (gitignored)
├── setup_sns.py          # Setup script
├── test_sns_alerts.py    # Test script
└── README.md             # This file

backend/app/utils/
├── sns_alerting.py       # Main alerting module
└── sns_integration_examples.py  # Usage examples
```

## 🔗 Resources

- [AWS SNS Documentation](https://docs.aws.amazon.com/sns/)
- [SNS Pricing](https://aws.amazon.com/sns/pricing/)
- [boto3 SNS Reference](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/sns.html)

## ✅ Checklist

- [ ] Created `.env` with configuration
- [ ] Run `setup_sns.py` to create topics
- [ ] Confirmed email subscriptions
- [ ] Tested with `test_sns_alerts.py`
- [ ] Integrated into backend code
- [ ] Verified alerts in production
- [ ] Set up monitoring/logging
- [ ] Documented custom alert types

## 📞 Support

For issues or questions:
1. Check the troubleshooting section
2. Review AWS SNS console for delivery status
3. Check CloudWatch logs
4. Verify IAM permissions for SNS publish

---

**Status**: ✅ Complete and Production-Ready
**Last Updated**: November 7, 2025
