-- Climate Health Database Schema
-- Run this script in PostgreSQL to create the required tables

-- Drop tables if they exist (be careful in production!)
DROP TABLE IF EXISTS hospital_data CASCADE;
DROP TABLE IF EXISTS health_data CASCADE;
DROP TABLE IF EXISTS climate_data CASCADE;
DROP TABLE IF EXISTS locations CASCADE;

-- Create locations table (master data)
CREATE TABLE locations (
    location_id INTEGER PRIMARY KEY,
    state VARCHAR(100) NOT NULL,
    district VARCHAR(100) NOT NULL,
    latitude DECIMAL(10, 6),
    longitude DECIMAL(10, 6),
    population INTEGER,
    urban_rural VARCHAR(20),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create climate_data table
CREATE TABLE climate_data (
    id SERIAL PRIMARY KEY,
    location_id INTEGER NOT NULL,
    date DATE NOT NULL,
    temperature DECIMAL(5, 2),
    humidity DECIMAL(5, 2),
    rainfall DECIMAL(10, 2),
    air_quality_index DECIMAL(10, 2),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (location_id) REFERENCES locations(location_id)
);

-- Create health_data table
CREATE TABLE health_data (
    id SERIAL PRIMARY KEY,
    location_id INTEGER NOT NULL,
    date DATE NOT NULL,
    disease_type VARCHAR(100) NOT NULL,
    cases INTEGER,
    deaths INTEGER,
    hospitalizations INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (location_id) REFERENCES locations(location_id)
);

-- Create hospital_data table
CREATE TABLE hospital_data (
    id SERIAL PRIMARY KEY,
    location_id INTEGER NOT NULL,
    date DATE NOT NULL,
    hospital_name VARCHAR(200),
    beds_total INTEGER,
    beds_available INTEGER,
    doctors INTEGER,
    nurses INTEGER,
    equipment_status VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (location_id) REFERENCES locations(location_id)
);

-- Create indexes for better query performance
CREATE INDEX idx_climate_location_date ON climate_data(location_id, date);
CREATE INDEX idx_health_location_date ON health_data(location_id, date);
CREATE INDEX idx_hospital_location_date ON hospital_data(location_id, date);
CREATE INDEX idx_health_disease ON health_data(disease_type);

-- Grant permissions (adjust as needed)
-- GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO admin;
-- GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO admin;

-- Verify tables were created
SELECT table_name FROM information_schema.tables WHERE table_schema = 'public';
