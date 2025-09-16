TODO: Climate-Resilient Healthcare System MVP
This file lists daily tasks to build a Climate-Resilient Healthcare System MVP in 5 days (Sept 17–21, 2025). Focus on a simple prototype: ingest climate/health data, predict heat stress risks, send alerts, and show results on a dashboard. Use AWS Management Console Proxy (MCP) via AWS Console for setup, Python for backend/ML, React/Next.js for frontend, and only the specified AWS services: EC2, S3, RDS PostgreSQL, API Gateway, Lambda, SageMaker, IAM, Secrets Manager, SNS, Glue. Work ~8 hours/day in Cursor (or VSCode).
Day 1 (Sept 17): Frontend Dashboard (Local) — Completed

- Next.js initialized in `frontend/` with TS, Tailwind, App Router
- Mock auth + RBAC (Admin/Clinician), session via localStorage
- Dashboard shows Delhi risk (0.7), temp trend chart (Chart.js)
- Admin sees resource suggestion; Clinician sees risk + chart
- Tested locally at http://localhost:3000
- Committed: "Day 1: Local dashboard with mock auth"

Day 2 (Sept 18): Local Backend (Ingestion, ETL, API, Alerts)

 Install Python dependencies: pip install boto3 pandas etc.
 Write ingest.py: Load NOAA CSV locally.
 Write etl.py: Clean, generate mock health, save to SQLite.
 Write api.py: Mock API with alerts.
 Test locally with fake data.
 Commit: git commit -m "Day 2: Local backend"

Day 3 (Sept 19): ML Model (Local + SageMaker Prep)

 Setup SageMaker Notebook in Console (via MCP).
 Write/train XGBoost model (ml/train.py): On mock data.
 Deploy to SageMaker endpoint prep.
 Test: Send sample data, get prediction.
 Commit: git commit -m "Day 3: ML model"

Day 4 (Sept 20): AWS Setup (MCP) + Backend Deployment

 Setup API Gateway in Console (via MCP): Create REST API, /predict.
 Write Lambda (api.py): Call SageMaker, SNS alert if risk > 0.7.
 Create SNS topic in Console: Subscribe email.
 Test: Call API via curl, check email.
 Commit: git commit -m "Day 4: AWS backend"

Day 5 (Sept 21): Frontend Deployment + Testing

 Setup Next.js: npx create-next-app frontend
 Build dashboard (frontend/pages/index.js): Fetch API.
 Test locally: npm run dev.
 Deploy to EC2 via Console (MCP): Launch t2.micro, run frontend.
 Commit: git commit -m "Day 5: Frontend + testing"

Notes

Use sample NOAA CSV, fake health data (cases = temp * 0.3).
Monitor costs (free tier, set $10 Budgets alert).
Debug with CloudWatch logs.

Enhanced Frontend — Completed

- Added role-specific nav, charts (line/scatter with zoom), risk score
- Patient list with sorting and notes (Admin only)
- Alerts list, resource suggestions, report CSV download
- Leaflet risk map (Delhi), light/dark theme (default light)
- Error handling with banner and axios prep for `/predict` & `/reports`
