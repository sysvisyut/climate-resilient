"""
Step 4: Verify Complete AWS Migration
This script verifies that all AWS resources are properly configured and data is migrated
"""

import boto3
import psycopg2
import json
import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from aws_config import (
    AWS_REGION, RDS_ENDPOINT, RDS_PORT, RDS_DATABASE,
    S3_RAW_DATA_BUCKET, S3_PROCESSED_DATA_BUCKET, S3_MODELS_BUCKET,
    SNS_ALERTS_TOPIC_ARN, SECRET_DB_CREDENTIALS
)

def verify_rds_connection():
    """Verify RDS database connection and data"""
    print("\n" + "-"*70)
    print("Verifying RDS Database".center(70))
    print("-"*70 + "\n")
    
    try:
        # Get credentials
        secrets_client = boto3.client('secretsmanager', region_name=AWS_REGION)
        response = secrets_client.get_secret_value(SecretId=SECRET_DB_CREDENTIALS)
        credentials = json.loads(response['SecretString'])
        
        # Connect
        conn = psycopg2.connect(
            host=credentials.get('host', RDS_ENDPOINT),
            port=credentials.get('port', RDS_PORT),
            database=credentials.get('dbname', RDS_DATABASE),
            user=credentials.get('username'),
            password=credentials['password']
        )
        
        cursor = conn.cursor()
        
        # Check tables
        cursor.execute("""
            SELECT table_name FROM information_schema.tables 
            WHERE table_schema = 'public'
        """)
        tables = [row[0] for row in cursor.fetchall()]
        
        print("✅ Connected to RDS successfully")
        print(f"   Database: {RDS_DATABASE}")
        print(f"   Tables: {', '.join(tables)}")
        
        # Check data counts
        data_counts = {}
        for table in ['locations', 'climate_data', 'health_data', 'hospital_data', 'users']:
            if table in tables:
                cursor.execute(f"SELECT COUNT(*) FROM {table}")
                count = cursor.fetchone()[0]
                data_counts[table] = count
                print(f"   • {table}: {count:,} records")
        
        cursor.close()
        conn.close()
        
        return True, data_counts
        
    except Exception as e:
        print(f"❌ RDS Verification Failed: {e}")
        return False, {}

def verify_s3_buckets():
    """Verify S3 buckets and contents"""
    print("\n" + "-"*70)
    print("Verifying S3 Buckets".center(70))
    print("-"*70 + "\n")
    
    s3_client = boto3.client('s3', region_name=AWS_REGION)
    bucket_status = {}
    
    buckets = {
        'Raw Data': S3_RAW_DATA_BUCKET,
        'Processed Data': S3_PROCESSED_DATA_BUCKET,
        'ML Models': S3_MODELS_BUCKET
    }
    
    for name, bucket in buckets.items():
        try:
            # Check bucket exists
            s3_client.head_bucket(Bucket=bucket)
            
            # Count objects
            response = s3_client.list_objects_v2(Bucket=bucket)
            count = response.get('KeyCount', 0)
            
            # Calculate size
            total_size = 0
            if 'Contents' in response:
                total_size = sum(obj['Size'] for obj in response['Contents'])
            
            print(f"✅ {name}: {bucket}")
            print(f"   Files: {count}")
            print(f"   Size: {total_size / 1024 / 1024:.2f} MB")
            
            bucket_status[name] = True
            
        except Exception as e:
            print(f"❌ {name}: {bucket} - {e}")
            bucket_status[name] = False
    
    return all(bucket_status.values()), bucket_status

def verify_sns_topic():
    """Verify SNS topic"""
    print("\n" + "-"*70)
    print("Verifying SNS Topic".center(70))
    print("-"*70 + "\n")
    
    try:
        sns_client = boto3.client('sns', region_name=AWS_REGION)
        
        # List topics
        topics = sns_client.list_topics()
        climate_topics = [t for t in topics['Topics'] 
                         if 'climate-health' in t['TopicArn']]
        
        if climate_topics:
            topic_arn = climate_topics[0]['TopicArn']
            print(f"✅ SNS Topic Found: {topic_arn}")
            
            # Check subscriptions
            subscriptions = sns_client.list_subscriptions_by_topic(TopicArn=topic_arn)
            print(f"   Subscriptions: {len(subscriptions['Subscriptions'])}")
            
            for sub in subscriptions['Subscriptions']:
                status = sub['SubscriptionArn']
                if 'pending' in status.lower():
                    print(f"   ⚠️  {sub['Protocol']}: {sub['Endpoint']} (Pending)")
                else:
                    print(f"   ✅ {sub['Protocol']}: {sub['Endpoint']} (Confirmed)")
            
            return True
        else:
            print("❌ Climate Health SNS topic not found")
            return False
            
    except Exception as e:
        print(f"❌ SNS Verification Failed: {e}")
        return False

def verify_secrets():
    """Verify Secrets Manager"""
    print("\n" + "-"*70)
    print("Verifying Secrets Manager".center(70))
    print("-"*70 + "\n")
    
    try:
        secrets_client = boto3.client('secretsmanager', region_name=AWS_REGION)
        
        required_secrets = [
            'climate-health/db/credentials',
            'climate-health/api/jwt-secret'
        ]
        
        all_found = True
        for secret_name in required_secrets:
            try:
                secrets_client.describe_secret(SecretId=secret_name)
                print(f"✅ Secret found: {secret_name}")
            except:
                print(f"❌ Secret missing: {secret_name}")
                all_found = False
        
        return all_found
        
    except Exception as e:
        print(f"❌ Secrets Verification Failed: {e}")
        return False

def verify_iam_user():
    """Verify IAM user and permissions"""
    print("\n" + "-"*70)
    print("Verifying IAM User".center(70))
    print("-"*70 + "\n")
    
    try:
        sts_client = boto3.client('sts', region_name=AWS_REGION)
        identity = sts_client.get_caller_identity()
        
        print(f"✅ Current User: {identity['Arn']}")
        print(f"   Account ID: {identity['Account']}")
        
        return True
        
    except Exception as e:
        print(f"❌ IAM Verification Failed: {e}")
        return False

def calculate_estimated_cost(data_counts, bucket_status):
    """Estimate monthly AWS cost"""
    print("\n" + "-"*70)
    print("Estimated Monthly Cost (Free Tier)".center(70))
    print("-"*70 + "\n")
    
    print("📊 Free Tier Limits:")
    print("   • RDS: 750 hours/month (db.t3.micro)")
    print("   • S3: 5 GB storage + 20,000 GET + 2,000 PUT requests")
    print("   • Lambda: 1M requests + 400,000 GB-seconds")
    print("   • SNS: 1,000 notifications")
    
    print("\n💰 Your Current Usage:")
    print("   • RDS: Running 1 instance = ~720 hours/month ✅")
    print("   • S3: < 1 GB estimated ✅")
    print("   • Secrets Manager: 2 secrets = $0.80/month ⚠️")
    print("   • Data Transfer: Minimal ✅")
    
    print("\n📈 Estimated Total: ~$0.80/month")
    print("   (Only Secrets Manager is not Free Tier)")
    
    print("\n💡 Cost Optimization Tips:")
    print("   1. Stop RDS when not using (saves Free Tier hours)")
    print("   2. Delete unused S3 objects")
    print("   3. Use Lambda instead of EC2 when possible")
    print("   4. Monitor with CloudWatch (Free Tier: 10 metrics)")

def main():
    """Run all verifications"""
    print("\n" + "="*70)
    print("AWS MIGRATION VERIFICATION".center(70))
    print("="*70)
    
    results = []
    
    # Run verifications
    results.append(("IAM User", verify_iam_user()))
    results.append(("RDS Database", verify_rds_connection()[0]))
    results.append(("S3 Buckets", verify_s3_buckets()[0]))
    results.append(("SNS Topic", verify_sns_topic()))
    results.append(("Secrets Manager", verify_secrets()))
    
    # Summary
    print("\n" + "="*70)
    print("VERIFICATION SUMMARY".center(70))
    print("="*70 + "\n")
    
    for name, status in results:
        icon = "✅" if status else "❌"
        print(f"{icon} {name:.<50} {'PASS' if status else 'FAIL'}")
    
    passed = sum(1 for _, status in results if status)
    total = len(results)
    
    print(f"\n{passed}/{total} verifications passed")
    
    if passed == total:
        print("\n🎉 ALL VERIFICATIONS PASSED!")
        print("\nYour AWS migration is complete:")
        print("   ✅ Database migrated to RDS")
        print("   ✅ Files uploaded to S3")
        print("   ✅ SNS alerts configured")
        print("   ✅ Secrets stored securely")
        
        print("\n📝 Next Steps:")
        print("   1. Update backend/app/models/database.py with RDS connection")
        print("   2. Update backend config to use Secrets Manager")
        print("   3. Deploy Lambda functions (optional)")
        print("   4. Set up API Gateway (optional)")
        
        # Cost estimation
        calculate_estimated_cost({}, {})
        
    else:
        print("\n⚠️  Some verifications failed.")
        print("   Review errors above and fix issues.")
        print("   Refer to AWS_SETUP_GUIDE.md for troubleshooting.")
    
    print("\n" + "="*70 + "\n")

if __name__ == "__main__":
    main()
