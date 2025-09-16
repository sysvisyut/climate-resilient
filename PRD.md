Product Requirements Document: Climate-Resilient Healthcare System MVP
1. Overview
The Climate-Resilient Healthcare System MVP is an AI-driven, cloud-native platform to predict and respond to climate-related health risks (e.g., heat stress). It integrates climate and health data, forecasts risks, sends alerts, and optimizes healthcare resources. Built with AWS (EC2, S3, RDS PostgreSQL, API Gateway, Lambda, SageMaker, IAM, Secrets Manager, SNS, Glue), Python, and React/Next.js, it’s designed for simplicity, security, and scalability. The MVP focuses on heat stress prediction for one region (e.g., India) using sample data, set up via AWS Management Console Proxy (MCP).
2. Objectives

Integrate climate (NOAA) and health (mock WHO) data for unified analysis.
Predict heat stress risks at a regional level.
Send multi-channel alerts (email/SMS) to health officials when risks exceed thresholds.
Recommend resource allocation (e.g., hospital beds) via a dashboard.
Ensure data security with AWS IAM and Secrets Manager.
Scale from a pilot to broader deployment using public datasets.

3. Scope
In-Scope

Data ingestion from public APIs (NOAA CSV, mock health data).
ETL pipeline to clean and store data in RDS.
XGBoost model for heat stress risk prediction.
REST API for predictions and alerts via SNS.
Simple React/Next.js dashboard with risk scores and charts.
Security via IAM roles and Secrets Manager, configured via MCP.
One-week build (Sept 17–21, 2025).

Out-of-Scope

Real-time IoT data or complex geospatial joins.
Multi-region scaling or multiple disease predictions.
Advanced UI features (e.g., interactive maps).

4. Requirements
Functional

User Management (Module 1):
Role-based access (admin, clinician, analyst) via IAM, set up in Console (MCP).
MFA enabled, credentials in Secrets Manager.


Data Ingestion (Module 2):
Pull sample NOAA CSV and mock health data to S3.
Catalog with Glue, store in RDS PostgreSQL.


ETL (Module 3):
Clean data (remove nulls, add lagged temp), write to RDS.
Trigger via Lambda on S3 upload.


AI/ML (Module 4):
Train XGBoost model to predict high-risk days (cases > 10).
Local training, SageMaker endpoint.


API & Integration (Module 5):
Secure REST API via Amazon API Gateway.
Backed by Lambda for predictions.


Alerts (Module 6):
Trigger SNS multi-channel notifications on risk thresholds.


Dashboard (Module 7):
React/Next.js frontend with risk trends, map, alerts, resources, reports.
Role-based views (Admin, Clinician, Analyst), mobile-responsive, light theme by default.
Day 1 delivered: local dashboard with mock RBAC and climate trends for Delhi (risk 0.7, temps 30/35°C). Enhanced with role-specific navigation, patients table, alerts, resource suggestions, reports, and map.


Analytics (Module 8):
Generate reports, audit logs for compliance.



Non-Functional

Security: IAM least privilege, MFA, Secrets Manager.
Performance: Process 1MB CSV <5 mins, predict <1s.
Scalability: One region, scale later.
Cost: Free tier, $10 Budgets alert.

5. Architecture

Data Flow: Ingest to S3 via Lambda → Glue to RDS → SageMaker predicts → Lambda/API Gateway serves → SNS alerts → Dashboard on EC2.
Security: IAM roles, Secrets Manager via MCP.
Datasets: NOAA GSOD CSV for climate, generated mock for health.

6. Deliverables

Code: Python backend/ML, React/Next.js frontend.
AWS Setup: Via MCP for all services.
Files: ingest.py, etl.py, trigger_etl.py, ml/train.py, api.py, report.py, frontend/pages/index.js.
Docs: README, TODO, PRD.
Tests: End-to-end flow.

7. Success Criteria

Local dashboard with mock data.
Local backend/ML with fake data.
AWS deployment via MCP.
End-to-end: CSV → Predict → Alert → Dashboard.
Secure setup.
Complete by Sept 21, 2025.

8. Assumptions

Sample data available (NOAA CSV, mock health).
Solo developer, 8 hours/day.
MCP via Console for AWS setup.

9. Risks

Data issues (use static CSVs).
Cost overruns (monitor Budgets).
Debugging delays (use CloudWatch).

10. Timeline

Day 1: Frontend dashboard (local).
Day 2: Backend ingestion, ETL, API, alerts (local).
Day 3: ML model (local + SageMaker prep).
Day 4: AWS setup (MCP), backend deployment.
Day 5: Frontend deployment, testing.


Author: [Your Name], Sept 2025Vibe: Build fast, keep it simple, save lives!