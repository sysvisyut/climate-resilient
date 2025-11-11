"""
Model service for managing ML models in S3
"""

import logging
from typing import Optional, Any, List

from app.utils.s3_storage import s3_storage

logger = logging.getLogger(__name__)


class ModelService:
    """Service for managing ML models in S3"""
    
    def __init__(self):
        self.s3 = s3_storage
    
    def load_model(self, model_name: str, model_type: str = 'pickle') -> Optional[Any]:
        """
        Load model from S3
        
        Args:
            model_name: Name of the model file
            model_type: 'pickle' or 'joblib'
            
        Returns:
            Model object or None
        """
        key = f"models/{model_name}"
        return self.s3.load_model_from_s3(key, model_type)
    
    def save_model(self, model: Any, model_name: str, model_type: str = 'pickle') -> bool:
        """
        Save model to S3
        
        Args:
            model: Model object to save
            model_name: Name for the model file
            model_type: 'pickle' or 'joblib'
            
        Returns:
            bool: True if successful
        """
        key = f"models/{model_name}"
        return self.s3.save_model_to_s3(model, key, model_type)
    
    def load_risk_model(self):
        """
        Load the enhanced risk model
        
        Returns:
            Risk model object or None
        """
        try:
            return self.load_model('enhanced_risk_model.pkl', 'pickle')
        except Exception as e:
            logger.error(f"Error loading risk model: {e}")
            return None
    
    def load_forecast_model(self):
        """
        Load the enhanced forecast model
        
        Returns:
            Forecast model object or None
        """
        try:
            return self.load_model('enhanced_forecast_model.pkl', 'pickle')
        except Exception as e:
            logger.error(f"Error loading forecast model: {e}")
            return None
    
    def load_scaler(self):
        """
        Load the data scaler
        
        Returns:
            Scaler object or None
        """
        try:
            return self.load_model('enhanced_scaler.joblib', 'joblib')
        except Exception as e:
            logger.error(f"Error loading scaler: {e}")
            return None
    
    def save_risk_model(self, model: Any) -> bool:
        """
        Save the risk model
        
        Args:
            model: Risk model object
            
        Returns:
            bool: True if successful
        """
        return self.save_model(model, 'enhanced_risk_model.pkl', 'pickle')
    
    def save_forecast_model(self, model: Any) -> bool:
        """
        Save the forecast model
        
        Args:
            model: Forecast model object
            
        Returns:
            bool: True if successful
        """
        return self.save_model(model, 'enhanced_forecast_model.pkl', 'pickle')
    
    def save_scaler(self, scaler: Any) -> bool:
        """
        Save the data scaler
        
        Args:
            scaler: Scaler object
            
        Returns:
            bool: True if successful
        """
        return self.save_model(scaler, 'enhanced_scaler.joblib', 'joblib')
    
    def list_available_models(self) -> List[str]:
        """
        List all available models in S3
        
        Returns:
            List of model file keys
        """
        return self.s3.list_objects('models/', self.s3.MODELS_BUCKET)
    
    def model_exists(self, model_name: str) -> bool:
        """
        Check if a model exists in S3
        
        Args:
            model_name: Name of the model file
            
        Returns:
            bool: True if exists
        """
        key = f"models/{model_name}"
        return self.s3.object_exists(key, self.s3.MODELS_BUCKET)


# Create global instance
model_service = ModelService()
