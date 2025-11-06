# Climate-Resilient Healthcare System Setup Instructions

This document provides instructions for setting up and running the AI-Driven Climate-Resilient Healthcare System.

## Prerequisites

- Python 3.8+
- Node.js 16+
- npm or yarn

## Backend Setup

1. Navigate to the backend directory:
   ```
   cd backend
   ```

2. Create a virtual environment (optional but recommended):
   ```
   python -m venv venv
   ```

3. Activate the virtual environment:
   - Windows:
     ```
     venv\Scripts\activate
     ```
   - macOS/Linux:
     ```
     source venv/bin/activate
     ```

4. Install required packages:
   ```
   pip install -r requirements.txt
   ```

5. Run the application:
   ```
   python main.py
   ```

   The backend API will be accessible at `http://localhost:8000`.

6. Initialize the system (only needed once):
   - Visit `http://localhost:8000/setup` in your browser or use a tool like Postman to make a GET request to this endpoint
   - This will generate synthetic data, create the database, and train the ML models
   - The initial setup may take a few minutes as it generates data and trains models

## Frontend Setup

1. Navigate to the frontend directory:
   ```
   cd frontend
   ```

2. Install dependencies:
   ```
   npm install
   ```
   or
   ```
   yarn install
   ```

3. Run the development server:
   ```
   npm run dev
   ```
   or
   ```
   yarn dev
   ```

   The frontend will be accessible at `http://localhost:3000`.

## Login Credentials

After setting up the system, you can log in with the following credentials:

- Admin User:
  - Email: admin@climate-health.org
  - Password: admin123

- Hospital User:
  - Email: hospital@climate-health.org
  - Password: hospital123

## System Overview

### Backend Components

- FastAPI server at `http://localhost:8000`
- SQLite database at `backend/climate_health.db`
- ML models stored in `backend/models/` directory
- Synthetic data stored in `backend/data/` directory

### Frontend Components

- Next.js app at `http://localhost:3000`
- Admin dashboard at `/admin/dashboard`
- Hospital dashboard at `/hospital/dashboard`

## API Documentation

The backend API documentation is available at `http://localhost:8000/docs` when the server is running.

## AWS Migration Path

For future migration to AWS, the following services would be used:

- Local files → Amazon S3
- SQLite → Amazon RDS (PostgreSQL)
- FastAPI → API Gateway + Lambda
- ML scripts → SageMaker
- Local auth → IAM + Secrets Manager
- Console alerts → SNS

## Troubleshooting

- If you encounter errors during model training, make sure you have enough disk space and memory available.
- If the frontend can't connect to the backend, verify that the backend server is running and that the API URL in `frontend/src/utils/api.ts` matches your backend server address.
- If authentication fails, try restarting the backend server and ensure the database has been properly initialized via the `/setup` endpoint.
