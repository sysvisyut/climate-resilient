"""
AWS-enabled database configuration
Uses RDS PostgreSQL instead of SQLite
Retrieves credentials from AWS Secrets Manager
"""

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import boto3
import json
import os

# AWS Configuration
AWS_REGION = os.getenv("AWS_REGION", "ap-south-1")
SECRET_NAME = os.getenv("DB_SECRET_NAME", "climate-health/db/credentials")
USE_AWS = os.getenv("USE_AWS", "false").lower() == "true"

def get_database_url():
    """Get database URL - either from AWS or local SQLite"""
    if USE_AWS:
        try:
            # Retrieve credentials from AWS Secrets Manager
            client = boto3.client('secretsmanager', region_name=AWS_REGION)
            response = client.get_secret_value(SecretId=SECRET_NAME)
            
            if 'SecretString' in response:
                secret = json.loads(response['SecretString'])
                
                # Build PostgreSQL connection string
                username = secret.get('username', 'postgres')
                password = secret['password']
                host = secret.get('host')
                port = secret.get('port', 5432)
                dbname = secret.get('dbname', 'climate_health')
                
                database_url = f"postgresql://{username}:{password}@{host}:{port}/{dbname}"
                print(f"✅ Using AWS RDS PostgreSQL at {host}")
                return database_url
            else:
                raise Exception("Secret not in expected format")
                
        except Exception as e:
            print(f"⚠️  Error connecting to AWS: {e}")
            print("   Falling back to local SQLite")
            return "sqlite:///./climate_health.db"
    else:
        # Use local SQLite
        print("📂 Using local SQLite database")
        return "sqlite:///./climate_health.db"

# Get database URL
SQLALCHEMY_DATABASE_URL = get_database_url()

# Create engine with appropriate settings
if SQLALCHEMY_DATABASE_URL.startswith("sqlite"):
    engine = create_engine(
        SQLALCHEMY_DATABASE_URL, 
        connect_args={"check_same_thread": False}
    )
else:
    # PostgreSQL settings
    engine = create_engine(
        SQLALCHEMY_DATABASE_URL,
        pool_size=5,
        max_overflow=10,
        pool_pre_ping=True,  # Verify connections before using
        pool_recycle=3600,   # Recycle connections after 1 hour
        echo=False
    )

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
