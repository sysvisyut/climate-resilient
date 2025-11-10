#!/bin/bash

# SNS Verification Script
# Run this to check if your SNS setup is working correctly

echo "================================================"
echo "AWS SNS Setup Verification"
echo "================================================"
echo ""

# Check if AWS CLI is configured
echo "1. Checking AWS CLI configuration..."
if aws sts get-caller-identity &> /dev/null; then
    echo "   ✓ AWS CLI configured"
    ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
    echo "   Account ID: $ACCOUNT_ID"
else
    echo "   ✗ AWS CLI not configured. Run: aws configure"
    exit 1
fi

echo ""
echo "2. Listing SNS Topics..."
aws sns list-topics --region eu-north-1 --query 'Topics[?contains(TopicArn, `climate`)]' --output table

echo ""
echo "3. Checking Subscriptions..."
aws sns list-subscriptions --region eu-north-1 --query 'Subscriptions[?contains(TopicArn, `climate`)].[Endpoint,Protocol,SubscriptionArn]' --output table

echo ""
echo "4. Checking Topic Details..."
for topic in "climate-health-risk-alerts" "climate-resource-shortage-alerts"; do
    echo ""
    echo "   Topic: $topic"
    TOPIC_ARN="arn:aws:sns:eu-north-1:$ACCOUNT_ID:$topic"
    
    # Get topic attributes
    aws sns get-topic-attributes --topic-arn "$TOPIC_ARN" --region eu-north-1 --query 'Attributes.{DisplayName:DisplayName,SubscriptionsConfirmed:SubscriptionsConfirmed,SubscriptionsPending:SubscriptionsPending}' --output table 2>/dev/null || echo "   Topic not found"
done

echo ""
echo "5. Testing SNS Publish (sending test message)..."
HEALTH_TOPIC_ARN="arn:aws:sns:eu-north-1:$ACCOUNT_ID:climate-health-risk-alerts"
aws sns publish \
    --topic-arn "$HEALTH_TOPIC_ARN" \
    --subject "Test Alert from Verification Script" \
    --message "This is a test message to verify SNS is working correctly. If you receive this, your SNS setup is operational!" \
    --region eu-north-1 2>/dev/null

if [ $? -eq 0 ]; then
    echo "   ✓ Test message published successfully"
    echo "   Check your email for the test message"
else
    echo "   ✗ Failed to publish test message"
    echo "   Check IAM permissions and topic ARN"
fi

echo ""
echo "================================================"
echo "Verification Complete"
echo "================================================"
echo ""
echo "AWS Console Links:"
echo "  Topics: https://eu-north-1.console.aws.amazon.com/sns/v3/home?region=eu-north-1#/topics"
echo "  Subscriptions: https://eu-north-1.console.aws.amazon.com/sns/v3/home?region=eu-north-1#/subscriptions"
echo ""
echo "To view metrics in CloudWatch:"
echo "  https://eu-north-1.console.aws.amazon.com/cloudwatch/home?region=eu-north-1#metricsV2:graph=~();namespace=AWS/SNS"
