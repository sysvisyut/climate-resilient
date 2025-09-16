Climate-Resilient Healthcare System MVP
This project is a Minimum Viable Product (MVP) for an AI-driven, cloud-native Climate-Resilient Healthcare System. It integrates climate and health data, predicts heat stress risks, sends alerts, and displays results on a dashboard. Built with AWS services, Python (backend/ML), and React/Next.js (frontend), it’s designed for simplicity, security, and scalability. This README guides you through setup, local testing, and AWS deployment using the AWS Management Console Proxy (MCP) and Cursor (or any IDE).
Features

Data Ingestion: Pulls sample climate/health data into Amazon S3.
ETL: Cleans data with AWS Glue, stores in RDS PostgreSQL.
Prediction: Uses SageMaker to predict heat stress risks.
Alerts: Sends notifications via SNS when risks are high.
API: Exposes predictions via API Gateway and Lambda.
Dashboard: React/Next.js UI to view risks and trends.
Security: IAM roles and Secrets Manager for secure access.

Tech Stack

Backend: Python (boto3, pandas, scikit-learn)
ML: XGBoost on Amazon SageMaker
Frontend: React/Next.js, Chart.js
Database: Amazon RDS (PostgreSQL)
AWS Services: EC2, S3, RDS, API Gateway, Lambda, SageMaker, IAM, Secrets Manager, SNS, Glue
Tools: AWS MCP, Cursor (or VSCode), Node.js

Prerequisites

AWS account (free tier recommended)
AWS MCP access (via Console or CLI with MCP setup)
Python 3.8+ (python --version)
Node.js 16+ (node --version)
Git (git --version)
Sample data: Download a NOAA CSV (e.g., daily temps from https://www.ncei.noaa.gov/data/global-summary-of-the-day/archive/)

Setup Instructions
Follow these steps to set up the project using AWS MCP and Cursor.
1. Clone the Repository
git clone <your-repo-url>
cd climate-resilient-healthcare

2. Local Development
Frontend (Day 1)

Open frontend/ in Cursor.
Install dependencies:cd frontend
npm install


Run locally:npm run dev


Build dashboard (pages/index.js):
Shows risk score, temp chart (Chart.js).


Deploy to EC2:
SSH to EC2, install Node.js, copy frontend/, run npm run build && npm start.



Backend (Day 2)

Open backend/ in Cursor.
Install dependencies:pip install boto3 pandas scikit-learn xgboost sqlalchemy psycopg2-binary requests


Ingest Data (ingest.py):
Lambda to fetch NOAA CSV and upload to S3.


ETL (etl.py):
Glue job to clean data and write to RDS.
Trigger via Lambda (trigger_etl.py).


ML (ml/train.py):
Trains XGBoost model on RDS data, deploys to SageMaker.
Run in SageMaker Notebook:python ml/train.py




API & Alerts (api.py):
Lambda to call SageMaker, trigger SNS if risk > 0.7.



3. AWS Setup via MCP (Day 4)
Use AWS Console with MCP for simplicity.
IAM (Security)

In Console (via MCP):
Go to IAM > Roles > Create Role.
Create ClimateAdmin role with trust policy for Lambda:{"Version":"2012-10-17","Statement":[{"Effect":"Allow","Principal":{"Service":"lambda.amazonaws.com"},"Action":"sts:AssumeRole"}]}


Attach policies: AmazonS3FullAccess, AmazonRDSFullAccess.
Create Clinician and Analyst roles with read-only policies (AmazonS3ReadOnlyAccess, AmazonRDSReadOnlyAccess).


Enable MFA: IAM > Users > Security credentials.

Secrets Manager

In Console: Secrets Manager > Store a new secret.
Add a fake NOAA API key: {"key":"abc123"}, name it noaa-api-key.


Test access with Python (boto3):import boto3
client = boto3.client('secretsmanager')
secret = client.get_secret_value(SecretId='noaa-api-key')['SecretString']
print(secret)



S3

In Console: S3 > Create Bucket.
Create climate-health-raw and climate-health-processed.


Verify buckets in Console.

RDS (PostgreSQL)

In Console: RDS > Create Database.
Choose PostgreSQL, db.t3.micro, 20GB storage, public access, username admin, password yourpassword.
Note the endpoint after creation (~10 mins).


Create tables using pgAdmin or SQL:CREATE TABLE climate (date DATE, region VARCHAR, temp FLOAT, humidity FLOAT);
CREATE TABLE health (date DATE, region VARCHAR, heat_cases INT);



Glue

In Console: Glue > Databases > Add Database > Name: climate_db.
Crawler: climate-crawler, target s3://climate-health-raw, role ClimateAdmin.
Run crawler after data ingestion.

SNS

In Console: SNS > Create Topic > Name: climate-alerts.
Subscribe your email: SNS > Subscriptions > Create Subscription > Protocol: Email, Endpoint: your.email@example.com.
Confirm subscription via email.

Lambda

In Console: Lambda > Create Function > Name: IngestData, Runtime: Python 3.8, Role: ClimateAdmin.
Upload ingest.py (zipped) to fetch NOAA CSV to S3.
Test: Trigger function manually.

API Gateway

In Console: API Gateway > Create API > REST API > Name: ClimateAPI.
Create resource /predict, method GET, integrate with Lambda (api.py).
Deploy API to a stage (e.g., prod).

SageMaker

In Console: SageMaker > Notebook Instances > Create > ml.t2.medium.
Use ml/train.py to train/deploy model (see Backend Setup).
Deploy endpoint: heat-risk-endpoint.

EC2

In Console: EC2 > Instances > Launch Instance > t2.micro, select AMI (e.g., Amazon Linux 2), create key pair.
SSH to instance for frontend hosting.

4. Deployment (Day 5)

Backend: Deploy Lambdas, Glue jobs, SageMaker endpoint via Console.
Frontend: SSH to EC2, install Node.js, copy frontend/, run npm run build && npm start.

5. Testing

Upload sample CSV to S3 (s3://climate-health-raw).
Trigger IngestData Lambda via Console.
Run Glue crawler via Console.
Trigger ETL Lambda.
Check RDS for clean data.
Run ml/train.py to deploy SageMaker endpoint.
Call API (/predict) via curl:curl <api-gateway-url>/predict


Verify SNS email for high-risk alerts.
View dashboard at http://<ec2-ip>:3000.

6. Files

backend/ingest.py: Lambda to ingest data to S3.
backend/etl.py: Glue ETL job.
backend/trigger_etl.py: ETL trigger Lambda.
backend/ml/train.py: SageMaker model.
backend/api.py: API/alert Lambda.
frontend/pages/index.js: Dashboard UI.

7. Notes

Data: Use NOAA CSV, fake health data (cases = temp * 0.3).
Cost: Stick to free tier. Monitor with AWS Budgets ($10 alert).
Debug: Check CloudWatch logs for Lambda/Glue.
Scaling: MVP focuses on one region (e.g., India). Expand later.

8. Troubleshooting

Lambda fails? Check IAM permissions in CloudWatch.
RDS not connecting? Verify security group allows port 5432.
SageMaker issues? Ensure data format matches model input.


Built with 💪 by [Your Name] in one week, September 2025. Vibe on!

### Frontend (Day 1 – Sept 17, 2025)

- Stack: Next.js (TypeScript, App Router, `src/`), Tailwind CSS, Chart.js via `react-chartjs-2`, axios
- Location: `frontend/`
- Features:
  - Login with mock credentials and RBAC (Admin, Clinician)
  - Dashboard shows region (Delhi, India), risk score, and temperature trend line chart
  - Admin additionally sees resource suggestion card
  - Mobile-responsive, vibe-driven UI with Tailwind
  - Commented axios snippet prepared for AWS API Gateway `/predict`

#### Run locally

```bash
cd frontend
npm install
npm run dev
# open http://localhost:3000
```

#### Demo credentials

- Admin: `admin` / `admin123`
- Clinician: `clinician` / `clin123`

#### File highlights

- `frontend/src/app/login/page.tsx`: login form and session init
- `frontend/src/app/page.tsx`: protected dashboard route
- `frontend/src/context/AuthContext.tsx`: localStorage-backed mock session and RBAC
- `frontend/src/components/Dashboard.tsx`: header, risk, chart, suggestion (admin only)
- `frontend/src/components/TemperatureChart.tsx`: Chart.js line chart
- `frontend/src/data/mockUsers.ts`, `frontend/src/data/mockData.ts`: mock users and climate data

#### AWS prep (Day 5)

- Swap mock auth for IAM-backed requests to API Gateway using axios with SigV4 (e.g., interceptor or presigned)
- Endpoint: `/predict` (POST). Request: `{ region: "Delhi, India" }`
- Secrets: move creds/config to AWS Secrets Manager or environment variables

#### MCP prompt used

Generate mobile-responsive React/Next.js dashboard with mock authentication (login page, RBAC for Admin/Clinician) and Chart.js for climate trends, compliant with AWS best practices.

#### Day 5 plan (IAM integration)

- Add AWS SigV4 axios interceptor or use presigned requests with temporary creds
- Store secrets in AWS Secrets Manager; load via backend or environment
- Replace mock call with POST `/predict` to API Gateway (IAM auth)
- Handle 401/403 with sign-out and re-auth flow

### Frontend (Enhanced – Sept 17, 2025)

- Role-specific navigation (Admin full, Clinician patient-focused, Analyst analytics-focused)
- Features: login (mock), RBAC, risk score, temp/risk charts with zoom, patient list (sorting, notes for Admin), resource suggestions, alerts, CSV report download, Leaflet risk map for Delhi, light/dark toggle (default light)
- Accessibility and performance: ARIA labels, keyboard-friendly nav, lazy map, memoized charts

Demo users:
- Admin: `admin` / `admin123`
- Clinician: `clinician` / `clin123`
- Analyst: `analyst` / `anal123`

API prep (Day 5): axios placeholders for `/predict` and `/reports` with error handling; swap in IAM auth.