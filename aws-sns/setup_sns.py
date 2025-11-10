#!/usr/bin/env python3
"""
AWS SNS Setup Script for Climate-Resilient Healthcare System
Creates SNS topics, subscriptions, and configures alerting infrastructure
"""

import boto3
import json
import os
from dotenv import load_dotenv
from pathlib import Path

# Load environment variables
env_path = Path(__file__).parent / '.env'
if env_path.exists():
    load_dotenv(env_path)
else:
    print("⚠️  .env file not found. Using default/example values.")
    load_dotenv(Path(__file__).parent / '.env.example')

# Configuration
AWS_REGION = os.getenv('AWS_REGION', 'eu-north-1')
AWS_ACCOUNT_ID = os.getenv('AWS_ACCOUNT_ID', '')

# Parse email addresses
ADMIN_EMAILS = [e.strip() for e in os.getenv('ADMIN_EMAIL_ADDRESSES', '').split(',') if e.strip()]
HOSPITAL_EMAILS = [e.strip() for e in os.getenv('HOSPITAL_EMAIL_ADDRESSES', '').split(',') if e.strip()]
ADMIN_SMS = [s.strip() for s in os.getenv('ADMIN_SMS_NUMBERS', '').split(',') if s.strip()]
URGENT_SMS = [s.strip() for s in os.getenv('URGENT_SMS_NUMBERS', '').split(',') if s.strip()]

# Initialize AWS clients
sns_client = boto3.client('sns', region_name=AWS_REGION)

def create_sns_topic(topic_name, display_name):
    """Create an SNS topic with tags"""
    try:
        response = sns_client.create_topic(
            Name=topic_name,
            Tags=[
                {'Key': 'Project', 'Value': 'ClimateHealth'},
                {'Key': 'Environment', 'Value': 'Production'},
                {'Key': 'ManagedBy', 'Value': 'SNS-Setup-Script'}
            ]
        )
        
        topic_arn = response['TopicArn']
        
        # Set display name
        sns_client.set_topic_attributes(
            TopicArn=topic_arn,
            AttributeName='DisplayName',
            AttributeValue=display_name
        )
        
        print(f"✓ Created topic: {topic_name}")
        print(f"  ARN: {topic_arn}")
        
        return topic_arn
    except Exception as e:
        print(f"✗ Error creating topic {topic_name}: {str(e)}")
        return None

def subscribe_email(topic_arn, email):
    """Subscribe an email address to a topic"""
    try:
        response = sns_client.subscribe(
            TopicArn=topic_arn,
            Protocol='email',
            Endpoint=email
        )
        print(f"  ✓ Subscribed email: {email}")
        return response['SubscriptionArn']
    except Exception as e:
        print(f"  ✗ Error subscribing {email}: {str(e)}")
        return None

def subscribe_sms(topic_arn, phone_number):
    """Subscribe an SMS number to a topic"""
    try:
        response = sns_client.subscribe(
            TopicArn=topic_arn,
            Protocol='sms',
            Endpoint=phone_number
        )
        print(f"  ✓ Subscribed SMS: {phone_number}")
        return response['SubscriptionArn']
    except Exception as e:
        print(f"  ✗ Error subscribing {phone_number}: {str(e)}")
        return None

def set_topic_policy(topic_arn, topic_name):
    """Set access policy for the SNS topic"""
    policy = {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Sid": "AllowPublishFromApplication",
                "Effect": "Allow",
                "Principal": {
                    "AWS": f"arn:aws:iam::{AWS_ACCOUNT_ID}:root"
                },
                "Action": "SNS:Publish",
                "Resource": topic_arn
            }
        ]
    }
    
    try:
        sns_client.set_topic_attributes(
            TopicArn=topic_arn,
            AttributeName='Policy',
            AttributeValue=json.dumps(policy)
        )
        print(f"  ✓ Set policy for {topic_name}")
    except Exception as e:
        print(f"  ✗ Error setting policy: {str(e)}")

def update_env_file(health_topic_arn, resource_topic_arn):
    """Update .env file with topic ARNs"""
    env_file = Path(__file__).parent / '.env'
    
    # Read existing content or create from example
    if env_file.exists():
        with open(env_file, 'r') as f:
            content = f.read()
    else:
        with open(Path(__file__).parent / '.env.example', 'r') as f:
            content = f.read()
    
    # Update topic ARNs
    lines = content.split('\n')
    updated_lines = []
    
    for line in lines:
        if line.startswith('SNS_HEALTH_RISK_TOPIC_ARN='):
            updated_lines.append(f'SNS_HEALTH_RISK_TOPIC_ARN={health_topic_arn}')
        elif line.startswith('SNS_RESOURCE_SHORTAGE_TOPIC_ARN='):
            updated_lines.append(f'SNS_RESOURCE_SHORTAGE_TOPIC_ARN={resource_topic_arn}')
        else:
            updated_lines.append(line)
    
    # Write updated content
    with open(env_file, 'w') as f:
        f.write('\n'.join(updated_lines))
    
    print(f"\n✓ Updated {env_file} with topic ARNs")

def main():
    print("=" * 70)
    print("AWS SNS Setup for Climate-Resilient Healthcare System")
    print(f"Region: {AWS_REGION}")
    print("=" * 70)
    
    if not AWS_ACCOUNT_ID:
        print("\n⚠️  WARNING: AWS_ACCOUNT_ID not set in .env")
        print("   Topics will be created but policies may not work correctly.")
    
    print("\n" + "=" * 70)
    print("Creating SNS Topics")
    print("=" * 70)
    
    # Create health risk alerts topic
    health_topic_arn = create_sns_topic(
        'climate-health-risk-alerts',
        'Climate Health Risk Alerts'
    )
    
    # Create resource shortage alerts topic
    resource_topic_arn = create_sns_topic(
        'climate-resource-shortage-alerts',
        'Climate Resource Shortage Alerts'
    )
    
    if not health_topic_arn or not resource_topic_arn:
        print("\n✗ Failed to create topics. Exiting.")
        return
    
    # Set topic policies
    if AWS_ACCOUNT_ID:
        print("\n" + "=" * 70)
        print("Setting Topic Policies")
        print("=" * 70)
        set_topic_policy(health_topic_arn, 'health-risk-alerts')
        set_topic_policy(resource_topic_arn, 'resource-shortage-alerts')
    
    # Subscribe emails to health risk alerts
    if ADMIN_EMAILS or HOSPITAL_EMAILS:
        print("\n" + "=" * 70)
        print("Subscribing Email Addresses to Health Risk Alerts")
        print("=" * 70)
        for email in ADMIN_EMAILS + HOSPITAL_EMAILS:
            subscribe_email(health_topic_arn, email)
    
    # Subscribe emails to resource shortage alerts
    if ADMIN_EMAILS:
        print("\n" + "=" * 70)
        print("Subscribing Email Addresses to Resource Shortage Alerts")
        print("=" * 70)
        for email in ADMIN_EMAILS:
            subscribe_email(resource_topic_arn, email)
    
    # Subscribe SMS to critical alerts
    if ADMIN_SMS or URGENT_SMS:
        print("\n" + "=" * 70)
        print("Subscribing SMS Numbers to Critical Alerts")
        print("=" * 70)
        print("(Both topics will receive critical SMS alerts)")
        for number in set(ADMIN_SMS + URGENT_SMS):
            subscribe_sms(health_topic_arn, number)
            subscribe_sms(resource_topic_arn, number)
    
    # Update .env file with ARNs
    print("\n" + "=" * 70)
    print("Updating Configuration")
    print("=" * 70)
    update_env_file(health_topic_arn, resource_topic_arn)
    
    # Print summary
    print("\n" + "=" * 70)
    print("Setup Complete!")
    print("=" * 70)
    print(f"\n✓ Health Risk Alerts Topic: {health_topic_arn}")
    print(f"✓ Resource Shortage Alerts Topic: {resource_topic_arn}")
    
    if ADMIN_EMAILS or HOSPITAL_EMAILS:
        print(f"\n📧 Email subscriptions: {len(ADMIN_EMAILS) + len(HOSPITAL_EMAILS)} total")
        print("   ⚠️  Subscribers must confirm their email subscriptions!")
    
    if ADMIN_SMS or URGENT_SMS:
        print(f"\n📱 SMS subscriptions: {len(set(ADMIN_SMS + URGENT_SMS))} total")
    
    print("\n" + "=" * 70)
    print("Next Steps:")
    print("=" * 70)
    print("1. Check email inboxes for subscription confirmation emails")
    print("2. Click 'Confirm subscription' in each email")
    print("3. Run test_sns_alerts.py to verify alerting works")
    print("4. Update backend code to use SNS alerts")
    print("\nTo send a test alert:")
    print(f"  python test_sns_alerts.py")

if __name__ == '__main__':
    main()
