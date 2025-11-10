# AWS Glue ETL - Climate Health System

## Overview

This directory contains AWS Glue ETL jobs and workflows for processing climate and health data for the Climate-Resilient Healthcare System.

### Architecture

```
aws-glue/
├── etl-jobs/              # PySpark ETL job scripts
├── workflows/             # Job configurations and workflow definitions
├── deployment/            # Deployment automation scripts
└── docs/                  # Documentation
```

## ETL Jobs

### 1. process_locations.py
Loads location master data from S3 to RDS PostgreSQL.

**Input:** `s3://climate-health-raw-data/locations/locations.csv`  
**Output:** RDS table `locations`  
**Duration:** ~5 minutes  

### 2. process_climate_data.py
Processes climate data with quality checks (temperature, rainfall, probabilities).

**Input:** `s3://climate-health-raw-data/climate/climate_data.csv`  
**Output:** RDS table `climate_data`  
**Duration:** ~10 minutes  

### 3. process_health_data.py
Processes disease case data ensuring non-negative values.

**Input:** `s3://climate-health-raw-data/health/health_data.csv`  
**Output:** RDS table `health_data`  
**Duration:** ~10 minutes  

### 4. process_hospital_data.py
Processes hospital resource data with validation.

**Input:** `s3://climate-health-raw-data/hospital/hospital_data.csv`  
**Output:** RDS table `hospital_data`  
**Duration:** ~10 minutes  

### 5. calculate_derived_metrics.py
Calculates risk scores and resilience metrics from RDS data.

**Input:** RDS tables (health_data, hospital_data, locations)  
**Output:** S3 processed data (CSV and JSON)  
**Duration:** ~15 minutes  

## Quick Start

### Prerequisites

1. AWS Account with appropriate permissions
2. AWS CLI configured
3. Python 3.8+ with boto3 installed
4. RDS PostgreSQL database created

### Environment Variables

Create a `.env` file in the `deployment/` directory:

```bash
AWS_REGION=ap-south-1
RDS_HOST=your-rds-endpoint.ap-south-1.rds.amazonaws.com
RDS_PORT=5432
RDS_USERNAME=postgres
RDS_PASSWORD=your-secure-password
```

### Deployment

**Option 1: Python Script (Recommended)**

```bash
cd deployment
pip install -r requirements.txt
python deploy_glue_jobs.py
```

**Option 2: Bash Script**

```bash
cd deployment
chmod +x deploy_glue_jobs.sh
./deploy_glue_jobs.sh
```

### Manual Execution

Run the workflow:

```bash
aws glue start-workflow-run \
  --name climate-health-etl-workflow \
  --region ap-south-1
```

Monitor progress:

```bash
aws glue get-workflow-run \
  --name climate-health-etl-workflow \
  --run-id <run-id> \
  --region ap-south-1
```

## AWS Resources Created

- **S3 Buckets:** 5 (raw-data, processed-data, scripts, temp, logs)
- **Glue Jobs:** 5 (one for each ETL process)
- **Glue Workflow:** 1 (orchestrates all jobs)
- **Glue Connection:** 1 (to RDS PostgreSQL)
- **IAM Role:** 1 (AWSGlueServiceRole-ClimateHealth)

## Cost Estimate

**Development/Testing (10 runs/day):**
- Glue DPUs: ~$20/day
- S3 Storage: ~$5/month
- RDS db.t3.micro: ~$15/month
- **Total:** ~$630/month

**Production (4 runs/day):**
- Glue DPUs: ~$8/day
- S3 Storage: ~$20/month
- RDS db.t3.small: ~$30/month
- **Total:** ~$290/month

## Monitoring

### CloudWatch Logs

View logs:
```bash
aws logs tail /aws-glue/jobs/output --follow
```

### Glue Console

Navigate to: AWS Console → Glue → Jobs → [Select Job] → History

## Troubleshooting

### Job Failures

1. Check CloudWatch logs
2. Verify S3 input files exist
3. Test RDS connection
4. Check IAM role permissions

### Common Issues

**Issue:** "Could not resolve host"  
**Solution:** Check VPC configuration for Glue connection

**Issue:** "Access Denied to S3"  
**Solution:** Verify IAM role has S3 permissions

**Issue:** "Table not found in RDS"  
**Solution:** Run database schema creation script first

## Documentation

For detailed documentation, see:

- [Migration Guide](./GLUE_MIGRATION_GUIDE.md) - Complete step-by-step guide
- [Quick Reference](./QUICK_REFERENCE.md) - Command reference
- [Implementation Summary](./IMPLEMENTATION_SUMMARY.md) - Technical details
- [Architecture Diagrams](./ARCHITECTURE_DIAGRAMS.md) - Visual architecture

## Support

For issues or questions:
1. Check documentation in `docs/` directory
2. Review CloudWatch logs
3. Verify AWS resource configurations

## License

Part of the Climate-Resilient Healthcare System project.
