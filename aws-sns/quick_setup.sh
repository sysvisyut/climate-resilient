#!/bin/bash

# Quick Setup Script for SNS Alerting System
# This script automates the initial setup process

set -e  # Exit on error

echo "=========================================="
echo "SNS Alerting System - Quick Setup"
echo "=========================================="
echo ""

# Check if running from correct directory
if [ ! -f "setup_sns.py" ]; then
    echo "❌ Error: Please run this script from the aws-sns directory"
    echo "   cd aws-sns && ./quick_setup.sh"
    exit 1
fi

# Check for AWS CLI
if ! command -v aws &> /dev/null; then
    echo "❌ Error: AWS CLI not found"
    echo "   Install from: https://aws.amazon.com/cli/"
    exit 1
fi

echo "✓ AWS CLI found"

# Check AWS credentials
if ! aws sts get-caller-identity &> /dev/null; then
    echo "❌ Error: AWS credentials not configured"
    echo "   Run: aws configure"
    exit 1
fi

echo "✓ AWS credentials configured"

# Get AWS account ID
AWS_ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
echo "✓ AWS Account ID: $AWS_ACCOUNT_ID"

# Check for Python 3
if ! command -v python3 &> /dev/null; then
    echo "❌ Error: Python 3 not found"
    exit 1
fi

echo "✓ Python 3 found"

# Install Python dependencies
echo ""
echo "Installing Python dependencies..."
pip3 install boto3 python-dotenv -q
echo "✓ Dependencies installed"

# Create .env if it doesn't exist
if [ ! -f ".env" ]; then
    echo ""
    echo "Creating .env file..."
    cp .env.example .env
    
    # Update AWS_ACCOUNT_ID in .env
    sed -i.bak "s/AWS_ACCOUNT_ID=your-account-id/AWS_ACCOUNT_ID=$AWS_ACCOUNT_ID/" .env
    rm .env.bak
    
    echo "✓ Created .env file"
    echo ""
    echo "⚠️  IMPORTANT: Edit .env and add:"
    echo "   - ADMIN_EMAIL_ADDRESSES"
    echo "   - HOSPITAL_EMAIL_ADDRESSES (optional)"
    echo "   - ADMIN_SMS_NUMBERS (optional)"
    echo "   - URGENT_SMS_NUMBERS (optional)"
    echo ""
    read -p "Press Enter after editing .env file..."
else
    echo "✓ .env file exists"
fi

# Run setup script
echo ""
echo "Creating SNS topics and subscriptions..."
python3 setup_sns.py

# Check if setup was successful
if [ $? -eq 0 ]; then
    echo ""
    echo "=========================================="
    echo "✅ Setup Complete!"
    echo "=========================================="
    echo ""
    echo "Next steps:"
    echo "1. Check your email and confirm SNS subscriptions"
    echo "2. Run: python3 test_sns_alerts.py"
    echo "3. Integrate into your backend code"
    echo ""
    echo "Documentation: cat README.md"
else
    echo ""
    echo "❌ Setup failed. Check error messages above."
    exit 1
fi
