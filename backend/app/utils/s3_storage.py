"""
S3 Storage utility for managing data and models in AWS S3
"""

import boto3
import pandas as pd
import pickle
import joblib
import json
import io
import logging
from datetime import datetime
from typing import Optional, Dict, Any, List
from botocore.exceptions import ClientError

logger = logging.getLogger(__name__)


class S3Storage:
    """Utility class for S3 storage operations"""
    
    def __init__(self, region_name: str = 'us-east-1'):
        """
        Initialize S3 client
        
        Args:
            region_name: AWS region name
        """
        self.s3_client = boto3.client('s3', region_name=region_name)
        self.s3_resource = boto3.resource('s3', region_name=region_name)
        
        # Define bucket names
        self.RAW_DATA_BUCKET = 'climate-health-raw-data-sharvaj'
        self.PROCESSED_DATA_BUCKET = 'climate-health-processed-data-sharvaj'
        self.MODELS_BUCKET = 'climate-health-models-use1-457151800683'
    
    # ==================== CSV/DataFrame Operations ====================
    
    def save_csv_to_s3(self, df: pd.DataFrame, key: str, bucket: str = None) -> bool:
        """
        Save DataFrame as CSV to S3
        
        Args:
            df: Pandas DataFrame to save
            key: S3 key (file path in bucket)
            bucket: S3 bucket name (defaults to processed data bucket)
            
        Returns:
            bool: True if successful, False otherwise
        """
        bucket = bucket or self.PROCESSED_DATA_BUCKET
        
        try:
            csv_buffer = io.StringIO()
            df.to_csv(csv_buffer, index=False)
            
            self.s3_client.put_object(
                Bucket=bucket,
                Key=key,
                Body=csv_buffer.getvalue(),
                ContentType='text/csv'
            )
            
            logger.info(f"✓ Saved CSV to s3://{bucket}/{key}")
            return True
            
        except ClientError as e:
            logger.error(f"✗ Error saving CSV to S3: {e}")
            return False
    
    def load_csv_from_s3(self, key: str, bucket: str = None) -> Optional[pd.DataFrame]:
        """
        Load CSV from S3 as DataFrame
        
        Args:
            key: S3 key (file path in bucket)
            bucket: S3 bucket name (defaults to processed data bucket)
            
        Returns:
            DataFrame or None if error
        """
        bucket = bucket or self.PROCESSED_DATA_BUCKET
        
        try:
            obj = self.s3_client.get_object(Bucket=bucket, Key=key)
            df = pd.read_csv(io.BytesIO(obj['Body'].read()))
            
            logger.info(f"✓ Loaded CSV from s3://{bucket}/{key}")
            return df
            
        except ClientError as e:
            logger.error(f"✗ Error loading CSV from S3: {e}")
            return None
    
    # ==================== JSON Operations ====================
    
    def save_json_to_s3(self, data: Dict[Any, Any], key: str, bucket: str = None) -> bool:
        """
        Save dictionary as JSON to S3
        
        Args:
            data: Dictionary to save
            key: S3 key (file path in bucket)
            bucket: S3 bucket name
            
        Returns:
            bool: True if successful
        """
        bucket = bucket or self.PROCESSED_DATA_BUCKET
        
        try:
            self.s3_client.put_object(
                Bucket=bucket,
                Key=key,
                Body=json.dumps(data, indent=2),
                ContentType='application/json'
            )
            
            logger.info(f"✓ Saved JSON to s3://{bucket}/{key}")
            return True
            
        except ClientError as e:
            logger.error(f"✗ Error saving JSON to S3: {e}")
            return False
    
    def load_json_from_s3(self, key: str, bucket: str = None) -> Optional[Dict]:
        """
        Load JSON from S3 as dictionary
        
        Args:
            key: S3 key (file path in bucket)
            bucket: S3 bucket name
            
        Returns:
            Dictionary or None if error
        """
        bucket = bucket or self.PROCESSED_DATA_BUCKET
        
        try:
            obj = self.s3_client.get_object(Bucket=bucket, Key=key)
            data = json.loads(obj['Body'].read().decode('utf-8'))
            
            logger.info(f"✓ Loaded JSON from s3://{bucket}/{key}")
            return data
            
        except ClientError as e:
            logger.error(f"✗ Error loading JSON from S3: {e}")
            return None
    
    # ==================== Model Operations ====================
    
    def save_model_to_s3(self, model: Any, key: str, model_type: str = 'pickle') -> bool:
        """
        Save ML model to S3
        
        Args:
            model: Model object to save
            key: S3 key (file path in bucket)
            model_type: 'pickle' or 'joblib'
            
        Returns:
            bool: True if successful
        """
        try:
            buffer = io.BytesIO()
            
            if model_type == 'joblib':
                joblib.dump(model, buffer)
            else:
                pickle.dump(model, buffer)
            
            buffer.seek(0)
            
            self.s3_client.put_object(
                Bucket=self.MODELS_BUCKET,
                Key=key,
                Body=buffer.getvalue(),
                ContentType='application/octet-stream'
            )
            
            logger.info(f"✓ Saved model to s3://{self.MODELS_BUCKET}/{key}")
            return True
            
        except Exception as e:
            logger.error(f"✗ Error saving model to S3: {e}")
            return False
    
    def load_model_from_s3(self, key: str, model_type: str = 'pickle') -> Optional[Any]:
        """
        Load ML model from S3
        
        Args:
            key: S3 key (file path in bucket)
            model_type: 'pickle' or 'joblib'
            
        Returns:
            Model object or None if error
        """
        try:
            obj = self.s3_client.get_object(Bucket=self.MODELS_BUCKET, Key=key)
            buffer = io.BytesIO(obj['Body'].read())
            
            if model_type == 'joblib':
                model = joblib.load(buffer)
            else:
                model = pickle.load(buffer)
            
            logger.info(f"✓ Loaded model from s3://{self.MODELS_BUCKET}/{key}")
            return model
            
        except Exception as e:
            logger.error(f"✗ Error loading model from S3: {e}")
            return None
    
    # ==================== File Operations ====================
    
    def upload_file_to_s3(self, local_path: str, key: str, bucket: str = None) -> bool:
        """
        Upload local file to S3
        
        Args:
            local_path: Local file path
            key: S3 key (file path in bucket)
            bucket: S3 bucket name
            
        Returns:
            bool: True if successful
        """
        bucket = bucket or self.RAW_DATA_BUCKET
        
        try:
            self.s3_client.upload_file(local_path, bucket, key)
            logger.info(f"✓ Uploaded {local_path} to s3://{bucket}/{key}")
            return True
            
        except ClientError as e:
            logger.error(f"✗ Error uploading file to S3: {e}")
            return False
    
    def download_file_from_s3(self, key: str, local_path: str, bucket: str = None) -> bool:
        """
        Download file from S3 to local path
        
        Args:
            key: S3 key (file path in bucket)
            local_path: Local file path to save
            bucket: S3 bucket name
            
        Returns:
            bool: True if successful
        """
        bucket = bucket or self.RAW_DATA_BUCKET
        
        try:
            self.s3_client.download_file(bucket, key, local_path)
            logger.info(f"✓ Downloaded s3://{bucket}/{key} to {local_path}")
            return True
            
        except ClientError as e:
            logger.error(f"✗ Error downloading file from S3: {e}")
            return False
    
    def list_objects(self, prefix: str = '', bucket: str = None) -> List[str]:
        """
        List objects in S3 bucket with given prefix
        
        Args:
            prefix: Prefix to filter objects
            bucket: S3 bucket name
            
        Returns:
            List of object keys
        """
        bucket = bucket or self.PROCESSED_DATA_BUCKET
        
        try:
            response = self.s3_client.list_objects_v2(
                Bucket=bucket,
                Prefix=prefix
            )
            
            if 'Contents' in response:
                objects = [obj['Key'] for obj in response['Contents']]
                logger.info(f"✓ Found {len(objects)} objects in s3://{bucket}/{prefix}")
                return objects
            
            return []
            
        except ClientError as e:
            logger.error(f"✗ Error listing objects in S3: {e}")
            return []
    
    def delete_object(self, key: str, bucket: str = None) -> bool:
        """
        Delete object from S3
        
        Args:
            key: S3 key (file path in bucket)
            bucket: S3 bucket name
            
        Returns:
            bool: True if successful
        """
        bucket = bucket or self.PROCESSED_DATA_BUCKET
        
        try:
            self.s3_client.delete_object(Bucket=bucket, Key=key)
            logger.info(f"✓ Deleted s3://{bucket}/{key}")
            return True
            
        except ClientError as e:
            logger.error(f"✗ Error deleting object from S3: {e}")
            return False
    
    def object_exists(self, key: str, bucket: str = None) -> bool:
        """
        Check if object exists in S3
        
        Args:
            key: S3 key (file path in bucket)
            bucket: S3 bucket name
            
        Returns:
            bool: True if exists
        """
        bucket = bucket or self.PROCESSED_DATA_BUCKET
        
        try:
            self.s3_client.head_object(Bucket=bucket, Key=key)
            return True
        except ClientError:
            return False
    
    # ==================== Batch Operations ====================
    
    def save_predictions_batch(self, predictions: List[Dict], date: str = None) -> bool:
        """
        Save batch of predictions to S3
        
        Args:
            predictions: List of prediction dictionaries
            date: Date string (YYYY-MM-DD)
            
        Returns:
            bool: True if successful
        """
        date = date or datetime.now().strftime('%Y-%m-%d')
        key = f"predictions/{date}/predictions_{datetime.now().timestamp()}.json"
        
        return self.save_json_to_s3(
            {'predictions': predictions, 'date': date, 'count': len(predictions)},
            key,
            self.PROCESSED_DATA_BUCKET
        )
    
    def get_bucket_size(self, bucket: str = None) -> Dict[str, Any]:
        """
        Get bucket statistics
        
        Args:
            bucket: S3 bucket name
            
        Returns:
            Dictionary with bucket stats
        """
        bucket = bucket or self.PROCESSED_DATA_BUCKET
        
        try:
            response = self.s3_client.list_objects_v2(Bucket=bucket)
            
            if 'Contents' not in response:
                return {'total_objects': 0, 'total_size_mb': 0}
            
            total_size = sum(obj['Size'] for obj in response['Contents'])
            total_objects = len(response['Contents'])
            
            return {
                'bucket': bucket,
                'total_objects': total_objects,
                'total_size_mb': round(total_size / (1024 * 1024), 2),
                'total_size_bytes': total_size
            }
            
        except ClientError as e:
            logger.error(f"✗ Error getting bucket size: {e}")
            return {'error': str(e)}


# Create global instance
s3_storage = S3Storage()
