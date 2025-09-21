# AI-Driven Climate-Resilient Healthcare System

This project is a local-first prototype for an AI-driven climate-resilient healthcare system focused on Indian states and union territories. It predicts climate-related health risks and hospital resource needs based on synthetic climate data.

## Project Structure

```
Climate/
├── backend/
│   ├── app/
│   │   ├── auth/         # JWT authentication
│   │   ├── models/       # SQLite database models
│   │   ├── routers/      # FastAPI endpoints
│   │   └── utils/        # Utility functions
│   ├── data/
│   │   ├── raw/          # Synthetic raw data
│   │   └── processed/    # Processed data
│   └── notebooks/        # ML development notebooks
└── frontend/
    └── src/
        ├── assets/       # Images and static files
        ├── components/   # React components
        ├── pages/        # React pages
        └── utils/        # Frontend utilities
```

## Setup Instructions

### Backend Setup
```bash
cd backend
pip install -r requirements.txt
python main.py
```

### Frontend Setup
```bash
cd frontend
npm install
npm run dev
```

## Features
- Synthetic data generator for all Indian states/UTs
- Climate data prediction and health risk assessment
- Hospital resource needs prediction
- Interactive dashboards with map visualizations
- Role-based access control

## AWS Migration Path
- Local files → S3
- SQLite → RDS PostgreSQL
- FastAPI → API Gateway + Lambda
- ML scripts → SageMaker
- Local auth → IAM + Secrets Manager
- Console alerts → SNS
