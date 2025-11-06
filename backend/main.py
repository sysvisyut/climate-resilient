import os
import uvicorn
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
import logging
from sqlalchemy.orm import Session

# Apply bcrypt patch first to suppress warnings
from app.auth.bcrypt_fix import patch_bcrypt
patch_bcrypt()

from app.models.database import engine, Base, get_db
from app.models.models import User
from app.routers import auth, data, enhanced_predictions
from app.utils.data_generator import generate_all_data
from app.utils.data_processor import main as process_data

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="Climate-Resilient Healthcare System API",
    description="API for climate-related health risk prediction and resource management",
    version="1.0.0",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins in development
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router)
app.include_router(data.router)
app.include_router(enhanced_predictions.router)


@app.get("/")
async def root():
    return {
        "message": "Welcome to Climate-Resilient Healthcare System API",
        "version": "1.0.0",
        "documentation": "/docs",
    }


@app.get("/health")
async def health():
    return {"status": "healthy"}


@app.get("/setup", status_code=status.HTTP_200_OK)
async def setup_system(db: Session = Depends(get_db)):
    """
    Setup the system by generating synthetic data and processing it.
    This is a convenience endpoint for initial setup.
    """
    try:
        # Check if system is already set up
        user_count = db.query(User).count()
        
        if user_count > 0:
            return {"message": "System is already set up"}
        
        # Generate synthetic data
        logger.info("Generating synthetic data...")
        generate_all_data(save_path="./data/raw")
        
        # Process data
        logger.info("Processing data...")
        process_data()
        
        # Create admin user
        logger.info("Creating admin user...")
        from app.auth.auth import get_password_hash
        admin_user = User(
            email="admin@climate-health.org",
            hashed_password=get_password_hash("admin123"),
            full_name="System Administrator",
            role="admin",
            is_active=True
        )
        
        db.add(admin_user)
        
        # Create hospital user
        hospital_user = User(
            email="hospital@climate-health.org",
            hashed_password=get_password_hash("hospital123"),
            full_name="Hospital Manager",
            role="hospital",
            hospital_name="Central Hospital",
            location_id=1,  # Delhi or another major city
            is_active=True
        )
        
        db.add(hospital_user)
        db.commit()
        
        # Train models
        logger.info("Training ML models...")
        from app.models.ml_models import train_all_models
        train_all_models()
        
        return {"message": "System setup complete"}
    
    except Exception as e:
        logger.error(f"Error during setup: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error during setup: {str(e)}"
        )


@app.on_event("startup")
async def startup_event():
    logger.info("Starting Climate-Resilient Healthcare System API")
    
    # Create database tables if they don't exist
    Base.metadata.create_all(bind=engine)
    logger.info("Database tables created or verified")


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
