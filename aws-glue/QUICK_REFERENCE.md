# AWS Glue Quick Reference

## Essential Commands

### Deploy Everything
```bash
cd aws-glue/deployment
python deploy_glue_jobs.py
```

### Start Workflow
```bash
aws glue start-workflow-run --name climate-health-etl-workflow --region ap-south-1
```

### Check Workflow Status
```bash
aws glue get-workflow-run --name climate-health-etl-workflow --run-id <RUN_ID> --region ap-south-1
```

### List Workflow Runs
```bash
aws glue get-workflow-runs --name climate-health-etl-workflow --max-results 10 --region ap-south-1
```

### View Job Logs
```bash
aws logs tail /aws-glue/jobs/output --follow --region ap-south-1
```

### Run Individual Job
```bash
aws glue start-job-run --job-name process-locations --region ap-south-1
```

### Stop Job Run
```bash
aws glue batch-stop-job-run --job-name process-locations --job-run-ids <RUN_ID> --region ap-south-1
```

## S3 Operations

### Upload Data to S3
```bash
aws s3 cp local/locations.csv s3://climate-health-raw-data/locations/ --region ap-south-1
```

### List S3 Objects
```bash
aws s3 ls s3://climate-health-raw-data/ --recursive --region ap-south-1
```

### Download Processed Data
```bash
aws s3 cp s3://climate-health-processed-data/metrics/ ./output/ --recursive --region ap-south-1
```

### Sync Directory to S3
```bash
aws s3 sync ./data/ s3://climate-health-raw-data/ --region ap-south-1
```

## RDS Operations

### Connect to RDS
```bash
psql -h your-rds-endpoint.ap-south-1.rds.amazonaws.com -U postgres -d climate_health
```

### Check Table Row Counts
```sql
SELECT 'locations' as table_name, COUNT(*) as rows FROM locations
UNION ALL
SELECT 'climate_data', COUNT(*) FROM climate_data
UNION ALL
SELECT 'health_data', COUNT(*) FROM health_data
UNION ALL
SELECT 'hospital_data', COUNT(*) FROM hospital_data;
```

### View Recent Data
```sql
SELECT * FROM health_data ORDER BY date DESC LIMIT 10;
```

## Monitoring Commands

### Get Job Statistics
```bash
aws glue get-job-runs --job-name process-locations --max-results 5 --region ap-south-1
```

### View CloudWatch Metrics
```bash
aws cloudwatch get-metric-statistics \
  --namespace Glue \
  --metric-name glue.driver.aggregate.numCompletedTasks \
  --dimensions Name=JobName,Value=process-locations \
  --start-time 2025-01-01T00:00:00Z \
  --end-time 2025-01-02T00:00:00Z \
  --period 3600 \
  --statistics Sum \
  --region ap-south-1
```

### Check Glue Connection
```bash
aws glue test-connection --connection-name climate-health-rds-connection --region ap-south-1
```

## IAM and Security

### Get Role Details
```bash
aws iam get-role --role-name AWSGlueServiceRole-ClimateHealth
```

### List Role Policies
```bash
aws iam list-attached-role-policies --role-name AWSGlueServiceRole-ClimateHealth
```

### Get Secrets Manager Value
```bash
aws secretsmanager get-secret-value --secret-id climate-health/rds/credentials --region ap-south-1
```

## Job Configuration

### Update Job Parameters
```bash
aws glue update-job --job-name process-locations \
  --job-update file://workflows/job-config-locations.json \
  --region ap-south-1
```

### List All Jobs
```bash
aws glue get-jobs --region ap-south-1
```

### Delete Job
```bash
aws glue delete-job --job-name job-name-here --region ap-south-1
```

## Workflow Management

### Update Workflow
```bash
aws glue update-workflow --name climate-health-etl-workflow \
  --description "Updated workflow description" \
  --region ap-south-1
```

### Delete Workflow
```bash
aws glue delete-workflow --name climate-health-etl-workflow --region ap-south-1
```

## Debugging

### Get Job Run Details
```bash
aws glue get-job-run --job-name process-locations --run-id <RUN_ID> --region ap-south-1 | jq '.JobRun.ErrorMessage'
```

### Get Last Failed Job Runs
```bash
aws glue get-job-runs --job-name process-locations --region ap-south-1 | jq '.JobRuns[] | select(.JobRunState == "FAILED")'
```

### View Spark UI (requires job running)
1. Go to AWS Glue Console
2. Select job → History → Click on Run ID
3. Click "View Spark UI"

## Testing

### Test Single Job Locally (Development)
```bash
# Not recommended - Glue jobs should run on AWS
# Use AWS Glue Development Endpoints for testing
```

### Validate Job Syntax
```bash
python -m py_compile etl-jobs/process_locations.py
```

## Cost Management

### Estimate Monthly Costs
- Check DPU usage: Glue Console → Jobs → Metrics
- Calculate: (DPU-hours × $0.44) + S3 storage + RDS costs

### View Glue Costs
```bash
aws ce get-cost-and-usage \
  --time-period Start=2025-01-01,End=2025-02-01 \
  --granularity MONTHLY \
  --metrics BlendedCost \
  --filter file://cost-filter.json \
  --region us-east-1
```

## Environment Variables

Set these before deployment:

```bash
export AWS_REGION=ap-south-1
export RDS_HOST=your-endpoint.rds.amazonaws.com
export RDS_PORT=5432
export RDS_USERNAME=postgres
export RDS_PASSWORD=your-password
```

## Useful Aliases (Add to ~/.zshrc)

```bash
alias glue-deploy='cd ~/aws-glue/deployment && python deploy_glue_jobs.py'
alias glue-start='aws glue start-workflow-run --name climate-health-etl-workflow --region ap-south-1'
alias glue-logs='aws logs tail /aws-glue/jobs/output --follow --region ap-south-1'
alias glue-status='aws glue get-workflow-runs --name climate-health-etl-workflow --max-results 5 --region ap-south-1'
```

## Error Codes

| Error Code | Meaning | Solution |
|------------|---------|----------|
| `EntityNotFoundException` | Resource doesn't exist | Check resource name |
| `AccessDeniedException` | Insufficient permissions | Review IAM role |
| `ConcurrentRunsExceededException` | Too many runs | Wait or increase limit |
| `InvalidInputException` | Invalid parameter | Check configuration |
| `InternalServiceException` | AWS service issue | Retry or contact support |

## Performance Tuning

### Optimize DPU Allocation
- Small jobs (< 100 MB): 2 DPUs
- Medium jobs (100 MB - 1 GB): 5 DPUs
- Large jobs (> 1 GB): 10+ DPUs

### Enable Job Bookmarks
```json
"--job-bookmark-option": "job-bookmark-enable"
```

### Partition Data in S3
```
s3://bucket/table/year=2025/month=01/day=01/data.parquet
```

## Support Resources

- [AWS Glue Documentation](https://docs.aws.amazon.com/glue/)
- [PySpark Documentation](https://spark.apache.org/docs/latest/api/python/)
- [CloudWatch Logs Insights](https://console.aws.amazon.com/cloudwatch/home?region=ap-south-1#logsV2:logs-insights)
