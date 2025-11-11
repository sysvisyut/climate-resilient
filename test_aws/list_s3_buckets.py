"""
Script to list all S3 buckets and their contents
"""

import boto3
import logging
from botocore.exceptions import ClientError

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def list_s3_buckets():
    """List all S3 buckets and their contents"""
    try:
        # Create S3 client
        s3_client = boto3.client('s3')
        
        # List all buckets
        logger.info("Fetching S3 buckets...")
        response = s3_client.list_buckets()
        
        buckets = response.get('Buckets', [])
        logger.info(f"Found {len(buckets)} bucket(s)")
        
        # Iterate through each bucket
        for bucket in buckets:
            bucket_name = bucket['Name']
            creation_date = bucket['CreationDate']
            
            print(f"\n{'='*80}")
            print(f"Bucket: {bucket_name}")
            print(f"Created: {creation_date}")
            print(f"{'='*80}")
            
            try:
                # Get bucket region
                location = s3_client.get_bucket_location(Bucket=bucket_name)
                region = location['LocationConstraint'] or 'us-east-1'
                print(f"Region: {region}")
                
                # List objects in the bucket
                paginator = s3_client.get_paginator('list_objects_v2')
                pages = paginator.paginate(Bucket=bucket_name)
                
                object_count = 0
                total_size = 0
                
                print("\nObjects:")
                for page in pages:
                    if 'Contents' in page:
                        for obj in page['Contents']:
                            object_count += 1
                            total_size += obj['Size']
                            size_mb = obj['Size'] / (1024 * 1024)
                            print(f"  - {obj['Key']} ({size_mb:.2f} MB) - Modified: {obj['LastModified']}")
                
                print(f"\nTotal Objects: {object_count}")
                print(f"Total Size: {total_size / (1024 * 1024):.2f} MB")
                
            except ClientError as e:
                logger.error(f"Error accessing bucket {bucket_name}: {e}")
                print(f"Error: {e}")
        
        return True
        
    except ClientError as e:
        logger.error(f"Error listing buckets: {e}")
        return False

if __name__ == "__main__":
    logger.info("Starting S3 bucket listing...")
    list_s3_buckets()
    logger.info("Done!")