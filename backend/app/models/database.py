from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os

# If you plan to use Amazon RDS Postgres, set DATABASE_URL to something like:
# postgresql+psycopg2://TODO_FILL_RDS_USER:TODO_FILL_RDS_PASSWORD@TODO_FILL_RDS_HOST:TODO_FILL_RDS_PORT/TODO_FILL_RDS_DB?sslmode=require
SQLALCHEMY_DATABASE_URL = os.environ.get("DATABASE_URL", "sqlite:///./climate_health.db")

if SQLALCHEMY_DATABASE_URL.startswith("sqlite:"):
    engine = create_engine(
        SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
    )
else:
    engine = create_engine(
        SQLALCHEMY_DATABASE_URL, pool_pre_ping=True
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
