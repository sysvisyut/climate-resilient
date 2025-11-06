"""
Step 2: Migrate Database from SQLite to PostgreSQL on RDS
This script migrates all data from local SQLite to AWS RDS PostgreSQL
"""

import sqlite3
import psycopg2
import boto3
import json
import sys
import os
from datetime import datetime

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from aws_config import (
    AWS_REGION, RDS_ENDPOINT, RDS_PORT, RDS_DATABASE, 
    RDS_USERNAME, SECRET_DB_CREDENTIALS
)

def get_rds_credentials():
    """Retrieve RDS credentials from AWS Secrets Manager"""
    print("📡 Retrieving database credentials from Secrets Manager...")
    
    try:
        client = boto3.client('secretsmanager', region_name=AWS_REGION)
        response = client.get_secret_value(SecretId=SECRET_DB_CREDENTIALS)
        
        if 'SecretString' in response:
            secret = json.loads(response['SecretString'])
            print("✅ Credentials retrieved successfully")
            return secret
        else:
            print("❌ Secret not found in expected format")
            return None
            
    except Exception as e:
        print(f"❌ Error retrieving credentials: {e}")
        return None

def connect_to_rds(credentials):
    """Connect to RDS PostgreSQL database"""
    print("\n🔌 Connecting to RDS PostgreSQL...")
    
    try:
        conn = psycopg2.connect(
            host=credentials.get('host', RDS_ENDPOINT),
            port=credentials.get('port', RDS_PORT),
            database=credentials.get('dbname', RDS_DATABASE),
            user=credentials.get('username', RDS_USERNAME),
            password=credentials['password']
        )
        print("✅ Connected to RDS successfully")
        return conn
        
    except Exception as e:
        print(f"❌ Connection error: {e}")
        return None

def create_postgresql_schema(pg_conn):
    """Create tables in PostgreSQL"""
    print("\n📋 Creating PostgreSQL schema...")
    
    schema_sql = """
    -- Locations table
    CREATE TABLE IF NOT EXISTS locations (
        id SERIAL PRIMARY KEY,
        name VARCHAR(255) UNIQUE NOT NULL,
        type VARCHAR(50),
        population INTEGER,
        area FLOAT
    );

    -- Climate data table
    CREATE TABLE IF NOT EXISTS climate_data (
        id SERIAL PRIMARY KEY,
        location_id INTEGER REFERENCES locations(id),
        date DATE NOT NULL,
        temperature FLOAT,
        rainfall FLOAT,
        humidity FLOAT,
        flood_probability FLOAT,
        cyclone_probability FLOAT,
        heatwave_probability FLOAT,
        is_projected BOOLEAN DEFAULT FALSE,
        projection_year INTEGER,
        last_updated DATE
    );

    -- Health data table
    CREATE TABLE IF NOT EXISTS health_data (
        id SERIAL PRIMARY KEY,
        location_id INTEGER REFERENCES locations(id),
        date DATE NOT NULL,
        dengue_cases INTEGER,
        malaria_cases INTEGER,
        heatstroke_cases INTEGER,
        diarrhea_cases INTEGER,
        is_projected BOOLEAN DEFAULT FALSE,
        projection_year INTEGER
    );

    -- Hospital data table
    CREATE TABLE IF NOT EXISTS hospital_data (
        id SERIAL PRIMARY KEY,
        location_id INTEGER REFERENCES locations(id),
        date DATE NOT NULL,
        total_beds INTEGER,
        available_beds INTEGER,
        doctors INTEGER,
        nurses INTEGER,
        iv_fluids_stock INTEGER,
        antibiotics_stock INTEGER,
        antipyretics_stock INTEGER,
        is_projected BOOLEAN DEFAULT FALSE,
        projection_year INTEGER
    );

    -- Users table
    CREATE TABLE IF NOT EXISTS users (
        id SERIAL PRIMARY KEY,
        email VARCHAR(255) UNIQUE NOT NULL,
        hashed_password VARCHAR(255),
        full_name VARCHAR(255),
        hospital_name VARCHAR(255),
        location_id INTEGER REFERENCES locations(id),
        is_active BOOLEAN DEFAULT TRUE,
        role VARCHAR(50)
    );

    -- Create indexes
    CREATE INDEX IF NOT EXISTS idx_climate_location ON climate_data(location_id);
    CREATE INDEX IF NOT EXISTS idx_climate_date ON climate_data(date);
    CREATE INDEX IF NOT EXISTS idx_health_location ON health_data(location_id);
    CREATE INDEX IF NOT EXISTS idx_health_date ON health_data(date);
    CREATE INDEX IF NOT EXISTS idx_hospital_location ON hospital_data(location_id);
    CREATE INDEX IF NOT EXISTS idx_hospital_date ON hospital_data(date);
    """
    
    try:
        cursor = pg_conn.cursor()
        cursor.execute(schema_sql)
        pg_conn.commit()
        print("✅ Schema created successfully")
        return True
        
    except Exception as e:
        print(f"❌ Schema creation error: {e}")
        pg_conn.rollback()
        return False

def migrate_table(sqlite_conn, pg_conn, table_name, columns):
    """Migrate a single table from SQLite to PostgreSQL"""
    print(f"\n📦 Migrating table: {table_name}")
    
    try:
        # Read from SQLite
        sqlite_cursor = sqlite_conn.cursor()
        sqlite_cursor.execute(f"SELECT {', '.join(columns)} FROM {table_name}")
        rows = sqlite_cursor.fetchall()
        
        if not rows:
            print(f"   ⚠️  No data found in {table_name}")
            return True
        
        # Insert into PostgreSQL
        pg_cursor = pg_conn.cursor()
        placeholders = ', '.join(['%s'] * len(columns))
        insert_sql = f"INSERT INTO {table_name} ({', '.join(columns)}) VALUES ({placeholders})"
        
        pg_cursor.executemany(insert_sql, rows)
        pg_conn.commit()
        
        print(f"   ✅ Migrated {len(rows)} rows")
        return True
        
    except Exception as e:
        print(f"   ❌ Migration error: {e}")
        pg_conn.rollback()
        return False

def main():
    """Main migration function"""
    print("\n" + "="*70)
    print("DATABASE MIGRATION: SQLite → PostgreSQL (RDS)".center(70))
    print("="*70)
    
    # Connect to SQLite
    print("\n📂 Connecting to local SQLite database...")
    sqlite_db_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 
                                   'backend', 'climate_health.db')
    
    if not os.path.exists(sqlite_db_path):
        print(f"❌ SQLite database not found at: {sqlite_db_path}")
        return
    
    sqlite_conn = sqlite3.connect(sqlite_db_path)
    print("✅ Connected to SQLite")
    
    # Get RDS credentials
    credentials = get_rds_credentials()
    if not credentials:
        print("\n❌ Cannot proceed without database credentials")
        return
    
    # Connect to PostgreSQL
    pg_conn = connect_to_rds(credentials)
    if not pg_conn:
        print("\n❌ Cannot proceed without RDS connection")
        return
    
    # Create schema
    if not create_postgresql_schema(pg_conn):
        print("\n❌ Schema creation failed")
        return
    
    # Migrate tables
    tables = {
        'locations': ['id', 'name', 'type', 'population', 'area'],
        'climate_data': ['id', 'location_id', 'date', 'temperature', 'rainfall', 
                        'humidity', 'flood_probability', 'cyclone_probability', 
                        'heatwave_probability', 'is_projected', 'projection_year', 'last_updated'],
        'health_data': ['id', 'location_id', 'date', 'dengue_cases', 'malaria_cases',
                       'heatstroke_cases', 'diarrhea_cases', 'is_projected', 'projection_year'],
        'hospital_data': ['id', 'location_id', 'date', 'total_beds', 'available_beds',
                         'doctors', 'nurses', 'iv_fluids_stock', 'antibiotics_stock',
                         'antipyretics_stock', 'is_projected', 'projection_year'],
        'users': ['id', 'email', 'hashed_password', 'full_name', 'hospital_name',
                 'location_id', 'is_active', 'role']
    }
    
    success_count = 0
    for table_name, columns in tables.items():
        if migrate_table(sqlite_conn, pg_conn, table_name, columns):
            success_count += 1
    
    # Close connections
    sqlite_conn.close()
    pg_conn.close()
    
    # Summary
    print("\n" + "="*70)
    print("MIGRATION SUMMARY".center(70))
    print("="*70)
    print(f"\n✅ Successfully migrated {success_count}/{len(tables)} tables")
    
    if success_count == len(tables):
        print("\n🎉 Database migration completed successfully!")
        print(f"\n📊 Your data is now on RDS:")
        print(f"   Host: {credentials.get('host', RDS_ENDPOINT)}")
        print(f"   Database: {RDS_DATABASE}")
    else:
        print("\n⚠️  Some tables failed to migrate. Check errors above.")
    
    print("\n" + "="*70 + "\n")

if __name__ == "__main__":
    main()
