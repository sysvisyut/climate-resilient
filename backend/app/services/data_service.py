"""
Data service for managing data operations with S3
"""

import pandas as pd
from datetime import datetime
from typing import Optional, List, Dict
import logging

from app.utils.s3_storage import s3_storage

logger = logging.getLogger(__name__)


class DataService:
    """Service for managing data operations with S3"""
    
    def __init__(self):
        self.s3 = s3_storage
    
    def load_climate_data(self, location_id: str = None) -> Optional[pd.DataFrame]:
        """
        Load climate data from S3
        
        Args:
            location_id: Optional filter by location ID
            
        Returns:
            DataFrame or None
        """
        try:
            df = self.s3.load_csv_from_s3(
                'raw/climate_data.csv',
                self.s3.RAW_DATA_BUCKET
            )
            
            if df is not None and location_id:
                df = df[df['location_id'] == location_id]
            
            return df
            
        except Exception as e:
            logger.error(f"Error loading climate data: {e}")
            return None
    
    def save_processed_climate_data(self, df: pd.DataFrame, date: str = None) -> bool:
        """
        Save processed climate data to S3
        
        Args:
            df: DataFrame to save
            date: Optional date string (YYYY-MM-DD)
            
        Returns:
            bool: True if successful
        """
        date = date or datetime.now().strftime('%Y-%m-%d')
        key = f"processed/climate_data_{date}.csv"
        
        return self.s3.save_csv_to_s3(df, key)
    
    def load_health_data(self, location_id: str = None) -> Optional[pd.DataFrame]:
        """
        Load health data from S3
        
        Args:
            location_id: Optional filter by location ID
            
        Returns:
            DataFrame or None
        """
        try:
            df = self.s3.load_csv_from_s3(
                'raw/health_data.csv',
                self.s3.RAW_DATA_BUCKET
            )
            
            if df is not None and location_id:
                df = df[df['location_id'] == location_id]
            
            return df
            
        except Exception as e:
            logger.error(f"Error loading health data: {e}")
            return None
    
    def save_processed_health_data(self, df: pd.DataFrame, date: str = None) -> bool:
        """
        Save processed health data to S3
        
        Args:
            df: DataFrame to save
            date: Optional date string (YYYY-MM-DD)
            
        Returns:
            bool: True if successful
        """
        date = date or datetime.now().strftime('%Y-%m-%d')
        key = f"processed/health_data_{date}.csv"
        
        return self.s3.save_csv_to_s3(df, key)
    
    def load_hospital_data(self) -> Optional[pd.DataFrame]:
        """
        Load hospital data from S3
        
        Returns:
            DataFrame or None
        """
        return self.s3.load_csv_from_s3(
            'raw/hospital_data.csv',
            self.s3.RAW_DATA_BUCKET
        )
    
    def save_processed_hospital_data(self, df: pd.DataFrame, date: str = None) -> bool:
        """
        Save processed hospital data to S3
        
        Args:
            df: DataFrame to save
            date: Optional date string (YYYY-MM-DD)
            
        Returns:
            bool: True if successful
        """
        date = date or datetime.now().strftime('%Y-%m-%d')
        key = f"processed/hospital_data_{date}.csv"
        
        return self.s3.save_csv_to_s3(df, key)
    
    def load_locations(self) -> Optional[pd.DataFrame]:
        """
        Load locations data from S3
        
        Returns:
            DataFrame or None
        """
        return self.s3.load_csv_from_s3(
            'raw/locations.csv',
            self.s3.RAW_DATA_BUCKET
        )
    
    def save_predictions(self, predictions: List[Dict], date: str = None) -> bool:
        """
        Save predictions to S3
        
        Args:
            predictions: List of prediction dictionaries
            date: Optional date string (YYYY-MM-DD)
            
        Returns:
            bool: True if successful
        """
        return self.s3.save_predictions_batch(predictions, date)
    
    def load_predictions(self, date: str) -> Optional[List[Dict]]:
        """
        Load predictions from S3 for a specific date
        
        Args:
            date: Date string (YYYY-MM-DD)
            
        Returns:
            List of predictions or None
        """
        objects = self.s3.list_objects(f"predictions/{date}/")
        
        if not objects:
            return None
        
        # Load the most recent prediction file for that date
        latest_key = sorted(objects)[-1]
        data = self.s3.load_json_from_s3(latest_key)
        
        return data.get('predictions') if data else None
    
    def save_forecasts(self, forecasts: List[Dict], date: str = None) -> bool:
        """
        Save forecasts to S3
        
        Args:
            forecasts: List of forecast dictionaries
            date: Optional date string (YYYY-MM-DD)
            
        Returns:
            bool: True if successful
        """
        date = date or datetime.now().strftime('%Y-%m-%d')
        key = f"forecasts/{date}/forecasts_{datetime.now().timestamp()}.json"
        
        return self.s3.save_json_to_s3(
            {'forecasts': forecasts, 'date': date, 'count': len(forecasts)},
            key
        )
    
    def save_alerts(self, alerts: List[Dict], date: str = None) -> bool:
        """
        Save alerts to S3
        
        Args:
            alerts: List of alert dictionaries
            date: Optional date string (YYYY-MM-DD)
            
        Returns:
            bool: True if successful
        """
        date = date or datetime.now().strftime('%Y-%m-%d')
        key = f"alerts/{date}/alerts_{datetime.now().timestamp()}.json"
        
        return self.s3.save_json_to_s3(
            {'alerts': alerts, 'date': date, 'count': len(alerts)},
            key
        )
    
    def list_processed_files(self, prefix: str = 'processed/') -> List[str]:
        """
        List all processed files in S3
        
        Args:
            prefix: Prefix to filter files
            
        Returns:
            List of file keys
        """
        return self.s3.list_objects(prefix)
    
    def get_storage_stats(self) -> Dict[str, Any]:
        """
        Get storage statistics for all buckets
        
        Returns:
            Dictionary with bucket statistics
        """
        stats = {}
        
        stats['raw_data'] = self.s3.get_bucket_size(self.s3.RAW_DATA_BUCKET)
        stats['processed_data'] = self.s3.get_bucket_size(self.s3.PROCESSED_DATA_BUCKET)
        stats['models'] = self.s3.get_bucket_size(self.s3.MODELS_BUCKET)
        
        return stats


# Create global instance
data_service = DataService()
