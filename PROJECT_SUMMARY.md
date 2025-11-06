# AI-Driven Climate-Resilient Healthcare System Project Summary

## Overview
This project is a local-first prototype for an AI-driven climate-resilient healthcare system focused on Indian states and union territories. It demonstrates how machine learning can be used to predict climate-related health risks and optimize hospital resource allocation based on climate projections.

## Key Features

1. **Synthetic Data Generation**
   - Climate data (temperature, rainfall, humidity, disaster probabilities)
   - Health data (disease cases for dengue, malaria, heatstroke, diarrhea)
   - Hospital resource data (beds, staff, supplies)
   - Current data and future projections (+1-5 years)

2. **Machine Learning Models**
   - XGBoost for health risk classification
   - LSTM for time-series disease forecasting
   - Resource needs prediction models

3. **Interactive Dashboards**
   - India map heatmap for disease risk visualization
   - Location-specific risk predictions
   - Resource allocation recommendations

4. **Role-Based Access**
   - Admin portal for system-wide analytics
   - Hospital portal for location-specific information

## Technical Architecture

### Backend
- **Framework**: FastAPI
- **Database**: SQLite (local development), PostgreSQL (AWS)
- **ML Libraries**: Scikit-learn, TensorFlow, XGBoost
- **Data Processing**: Pandas, NumPy
- **Authentication**: JWT-based auth with role-based access control

### Frontend
- **Framework**: Next.js/React
- **UI Library**: Material-UI
- **Data Visualization**: Plotly.js
- **State Management**: React Query for server state

### AWS Migration Path
- **Storage**: S3 for data and models
- **Database**: RDS (PostgreSQL)
- **Computing**: EC2, Lambda for serverless functions
- **API Layer**: API Gateway
- **ML Infrastructure**: SageMaker
- **Authentication**: IAM, Secrets Manager
- **ETL**: AWS Glue
- **Alerts**: SNS

## Project Structure
```
Climate/
├── backend/
│   ├── app/
│   │   ├── auth/         # JWT authentication
│   │   ├── models/       # Database and ML models
│   │   ├── routers/      # API endpoints
│   │   └── utils/        # Data generation and processing
│   ├── data/
│   │   ├── raw/          # Synthetic raw data
│   │   └── processed/    # Processed data
│   └── models/           # Saved ML models
├── frontend/
│   └── src/
│       ├── components/   # React components
│       ├── pages/        # Next.js pages
│       └── utils/        # API client and auth utils
├── SETUP.md              # Setup instructions
└── AWS_MIGRATION.md      # AWS migration guide
```

## Running the Project
See [SETUP.md](SETUP.md) for detailed instructions on setting up and running the project locally.

## Future Enhancements
1. **Real-time Data Integration**: Connect to actual climate and health data APIs
2. **Advanced ML Models**: Implement more sophisticated models with ensemble techniques
3. **Geospatial Analysis**: Add more detailed geographical analysis at district level
4. **Mobile Applications**: Develop companion mobile apps for field workers
5. **IoT Integration**: Connect with IoT devices for real-time climate monitoring

## Learning Resources
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Next.js Documentation](https://nextjs.org/docs)
- [Scikit-learn Documentation](https://scikit-learn.org/stable/)
- [TensorFlow Documentation](https://www.tensorflow.org/api_docs)
- [XGBoost Documentation](https://xgboost.readthedocs.io/)
- [AWS Documentation](https://docs.aws.amazon.com/)
