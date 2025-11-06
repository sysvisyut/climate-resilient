"""
This script manually runs the setup process for the Climate-Resilient Healthcare System.
It generates synthetic data, processes it, and trains models.
"""

import os
import sys
import logging

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# Make sure directories exist
os.makedirs("data/raw", exist_ok=True)
os.makedirs("data/processed", exist_ok=True) 
os.makedirs("models", exist_ok=True)

# Check if all directories were created
for path in ["data/raw", "data/processed", "models"]:
    logger.info(f"Directory '{path}' exists: {os.path.exists(path)}")

try:
    # Generate synthetic data
    logger.info("Step 1: Generating synthetic data...")
    from app.utils.data_generator import generate_all_data
    data = generate_all_data(save_path="./data/raw")
    logger.info(f"Generated data for {len(data['locations'])} locations")
    logger.info(f"Climate data points: {len(data['climate'])}")
    logger.info(f"Health data points: {len(data['health'])}")
    logger.info(f"Hospital data points: {len(data['hospital'])}")
    
    # Process data
    logger.info("Step 2: Processing data...")
    from app.utils.data_processor import main as process_data
    process_data()
    
    # Train models
    logger.info("Step 3: Training ML models...")
    from app.models.ml_models import train_all_models
    success = train_all_models()
    
    if success:
        logger.info("All models trained successfully")
    else:
        logger.error("Model training failed")
    
    # Check for model files
    logger.info("Checking for model files...")
    model_files = os.listdir("models")
    logger.info(f"Found {len(model_files)} model files: {model_files}")
    
    logger.info("Setup process completed successfully!")
    
except Exception as e:
    logger.error(f"Error during setup: {e}")
    import traceback
    logger.error(traceback.format_exc())
    sys.exit(1)
