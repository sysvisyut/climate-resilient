"""
Step 3: Upload Data and Models to S3
This script uploads local files to S3 buckets
"""

import boto3
import os
import sys
from pathlib import Path

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from aws_config import (
    AWS_REGION, S3_RAW_DATA_BUCKET, 
    S3_PROCESSED_DATA_BUCKET, S3_MODELS_BUCKET
)

def upload_directory_to_s3(local_directory, bucket_name, s3_prefix=''):
    """Upload all files in a directory to S3"""
    if not os.path.exists(local_directory):
        print(f"   ⚠️  Directory not found: {local_directory}")
        return 0
    
    s3_client = boto3.client('s3', region_name=AWS_REGION)
    uploaded_count = 0
    
    for root, dirs, files in os.walk(local_directory):
        for file in files:
            local_path = os.path.join(root, file)
            relative_path = os.path.relpath(local_path, local_directory)
            s3_path = os.path.join(s3_prefix, relative_path).replace('\\', '/')
            
            try:
                print(f"   Uploading: {relative_path}")
                s3_client.upload_file(local_path, bucket_name, s3_path)
                uploaded_count += 1
            except Exception as e:
                print(f"   ❌ Error uploading {file}: {e}")
    
    return uploaded_count

def upload_raw_data():
    """Upload raw data to S3"""
    print("\n" + "-"*70)
    print("Uploading Raw Data".center(70))
    print("-"*70 + "\n")
    
    local_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 
                             'backend', 'data', 'raw')
    
    print(f"📂 Source: {local_dir}")
    print(f"☁️  Destination: s3://{S3_RAW_DATA_BUCKET}/raw/")
    
    count = upload_directory_to_s3(local_dir, S3_RAW_DATA_BUCKET, 'raw')
    print(f"\n✅ Uploaded {count} files to raw data bucket")
    
    return count > 0

def upload_processed_data():
    """Upload processed data to S3"""
    print("\n" + "-"*70)
    print("Uploading Processed Data".center(70))
    print("-"*70 + "\n")
    
    local_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 
                             'backend', 'data', 'processed')
    
    print(f"📂 Source: {local_dir}")
    print(f"☁️  Destination: s3://{S3_PROCESSED_DATA_BUCKET}/processed/")
    
    count = upload_directory_to_s3(local_dir, S3_PROCESSED_DATA_BUCKET, 'processed')
    print(f"\n✅ Uploaded {count} files to processed data bucket")
    
    return count > 0

def upload_ml_models():
    """Upload ML models to S3"""
    print("\n" + "-"*70)
    print("Uploading ML Models".center(70))
    print("-"*70 + "\n")
    
    local_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 
                             'backend', 'models')
    
    print(f"📂 Source: {local_dir}")
    print(f"☁️  Destination: s3://{S3_MODELS_BUCKET}/models/")
    
    count = upload_directory_to_s3(local_dir, S3_MODELS_BUCKET, 'models')
    print(f"\n✅ Uploaded {count} files to models bucket")
    
    return count > 0

def verify_bucket_exists(bucket_name):
    """Check if S3 bucket exists"""
    try:
        s3_client = boto3.client('s3', region_name=AWS_REGION)
        s3_client.head_bucket(Bucket=bucket_name)
        return True
    except Exception as e:
        print(f"❌ Bucket {bucket_name} not found: {e}")
        return False

def list_bucket_contents(bucket_name, prefix=''):
    """List contents of S3 bucket"""
    try:
        s3_client = boto3.client('s3', region_name=AWS_REGION)
        response = s3_client.list_objects_v2(Bucket=bucket_name, Prefix=prefix)
        
        if 'Contents' in response:
            print(f"\n   Files in s3://{bucket_name}/{prefix}:")
            for obj in response['Contents'][:10]:  # Show first 10
                print(f"   • {obj['Key']} ({obj['Size']} bytes)")
            if len(response['Contents']) > 10:
                print(f"   ... and {len(response['Contents']) - 10} more files")
            return len(response['Contents'])
        else:
            print(f"\n   No files found in s3://{bucket_name}/{prefix}")
            return 0
            
    except Exception as e:
        print(f"❌ Error listing bucket: {e}")
        return 0

def main():
    """Main upload function"""
    print("\n" + "="*70)
    print("S3 DATA UPLOAD".center(70))
    print("="*70)
    
    # Check if buckets exist
    print("\n🔍 Verifying S3 buckets...")
    buckets = [S3_RAW_DATA_BUCKET, S3_PROCESSED_DATA_BUCKET, S3_MODELS_BUCKET]
    bucket_names = ['Raw Data', 'Processed Data', 'ML Models']
    
    all_exist = True
    for bucket, name in zip(buckets, bucket_names):
        if verify_bucket_exists(bucket):
            print(f"   ✅ {name}: {bucket}")
        else:
            print(f"   ❌ {name}: {bucket} NOT FOUND")
            all_exist = False
    
    if not all_exist:
        print("\n⚠️  Please create missing buckets first!")
        print("   Refer to AWS_SETUP_GUIDE.md Step 7")
        return
    
    # Upload data
    results = []
    results.append(('Raw Data', upload_raw_data()))
    results.append(('Processed Data', upload_processed_data()))
    results.append(('ML Models', upload_ml_models()))
    
    # Verify uploads
    print("\n" + "="*70)
    print("VERIFICATION".center(70))
    print("="*70)
    
    print("\n📦 Raw Data Bucket:")
    list_bucket_contents(S3_RAW_DATA_BUCKET, 'raw')
    
    print("\n📦 Processed Data Bucket:")
    list_bucket_contents(S3_PROCESSED_DATA_BUCKET, 'processed')
    
    print("\n📦 ML Models Bucket:")
    model_count = list_bucket_contents(S3_MODELS_BUCKET, 'models')
    
    # Summary
    print("\n" + "="*70)
    print("UPLOAD SUMMARY".center(70))
    print("="*70 + "\n")
    
    for name, success in results:
        status = "✅ SUCCESS" if success else "⚠️  SKIPPED"
        print(f"{name:.<50} {status}")
    
    if all(success for _, success in results):
        print("\n🎉 All data uploaded to S3 successfully!")
        print("\n💰 Free Tier Note:")
        print("   • You have 5 GB of S3 storage in Free Tier")
        print("   • Monitor usage in AWS Console → S3 → Storage Lens")
    else:
        print("\n⚠️  Some uploads were skipped (no local data found)")
        print("   This is normal if you haven't generated data yet")
    
    print("\n" + "="*70 + "\n")

if __name__ == "__main__":
    main()
