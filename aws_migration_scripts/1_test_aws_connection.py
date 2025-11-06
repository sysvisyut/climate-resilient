"""
Step 1: Test AWS Connection
This script verifies that your AWS credentials are properly configured
"""

import boto3
from botocore.exceptions import ClientError, NoCredentialsError
import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from aws_config import AWS_REGION

def test_aws_credentials():
    """Test if AWS credentials are configured"""
    print("\n" + "="*70)
    print("Testing AWS Credentials".center(70))
    print("="*70 + "\n")
    
    try:
        sts = boto3.client('sts', region_name=AWS_REGION)
        identity = sts.get_caller_identity()
        
        print("✅ AWS Credentials are valid!")
        print(f"   Account ID: {identity['Account']}")
        print(f"   User ARN: {identity['Arn']}")
        print(f"   User ID: {identity['UserId']}")
        return True
        
    except NoCredentialsError:
        print("❌ AWS credentials not found!")
        print("   Run: aws configure")
        print("   And enter your Access Key ID and Secret Access Key")
        return False
        
    except ClientError as e:
        print(f"❌ Error: {e}")
        return False

def test_s3_access():
    """Test S3 access"""
    print("\n" + "-"*70)
    print("Testing S3 Access".center(70))
    print("-"*70 + "\n")
    
    try:
        s3 = boto3.client('s3', region_name=AWS_REGION)
        buckets = s3.list_buckets()
        
        print("✅ S3 Access successful!")
        print(f"   Found {len(buckets['Buckets'])} buckets:")
        for bucket in buckets['Buckets']:
            print(f"   • {bucket['Name']}")
        return True
        
    except ClientError as e:
        print(f"❌ S3 Access Error: {e}")
        return False

def test_rds_access():
    """Test RDS access"""
    print("\n" + "-"*70)
    print("Testing RDS Access".center(70))
    print("-"*70 + "\n")
    
    try:
        rds = boto3.client('rds', region_name=AWS_REGION)
        instances = rds.describe_db_instances()
        
        print("✅ RDS Access successful!")
        print(f"   Found {len(instances['DBInstances'])} database instances:")
        for db in instances['DBInstances']:
            print(f"   • {db['DBInstanceIdentifier']}")
            print(f"     Status: {db['DBInstanceStatus']}")
            print(f"     Endpoint: {db.get('Endpoint', {}).get('Address', 'N/A')}")
        return True
        
    except ClientError as e:
        print(f"❌ RDS Access Error: {e}")
        return False

def test_secrets_manager_access():
    """Test Secrets Manager access"""
    print("\n" + "-"*70)
    print("Testing Secrets Manager Access".center(70))
    print("-"*70 + "\n")
    
    try:
        secrets = boto3.client('secretsmanager', region_name=AWS_REGION)
        secret_list = secrets.list_secrets()
        
        print("✅ Secrets Manager Access successful!")
        print(f"   Found {len(secret_list['SecretList'])} secrets:")
        for secret in secret_list['SecretList']:
            print(f"   • {secret['Name']}")
        return True
        
    except ClientError as e:
        print(f"❌ Secrets Manager Access Error: {e}")
        return False

def test_sns_access():
    """Test SNS access"""
    print("\n" + "-"*70)
    print("Testing SNS Access".center(70))
    print("-"*70 + "\n")
    
    try:
        sns = boto3.client('sns', region_name=AWS_REGION)
        topics = sns.list_topics()
        
        print("✅ SNS Access successful!")
        print(f"   Found {len(topics['Topics'])} topics:")
        for topic in topics['Topics']:
            print(f"   • {topic['TopicArn']}")
        return True
        
    except ClientError as e:
        print(f"❌ SNS Access Error: {e}")
        return False

def main():
    """Run all tests"""
    print("\n" + "="*70)
    print("AWS CONNECTION VERIFICATION".center(70))
    print("="*70)
    
    results = []
    results.append(("AWS Credentials", test_aws_credentials()))
    results.append(("S3 Access", test_s3_access()))
    results.append(("RDS Access", test_rds_access()))
    results.append(("Secrets Manager", test_secrets_manager_access()))
    results.append(("SNS Access", test_sns_access()))
    
    # Summary
    print("\n" + "="*70)
    print("TEST SUMMARY".center(70))
    print("="*70 + "\n")
    
    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{name:.<50} {status}")
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    print(f"\n{passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All tests passed! You're ready to proceed with migration.")
    else:
        print("\n⚠️  Some tests failed. Please fix the issues before proceeding.")
        print("   Refer to AWS_SETUP_GUIDE.md for troubleshooting.")
    
    print("\n" + "="*70 + "\n")

if __name__ == "__main__":
    main()
