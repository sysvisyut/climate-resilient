#!/bin/bash

echo "Fixing Glue job configurations..."

# Update process-locations
echo "Updating process-locations..."
aws glue update-job --job-name process-locations --region eu-north-1 --job-update '{
  "Role": "AWSGlueServiceRole-ClimateHealth",
  "Command": {
    "Name": "glueetl",
    "ScriptLocation": "s3://climate-health-scripts-sharvaj-2024/etl-jobs/process_locations.py",
    "PythonVersion": "3"
  },
  "DefaultArguments": {
    "--job-language": "python",
    "--job-bookmark-option": "job-bookmark-enable",
    "--enable-metrics": "true",
    "--enable-continuous-cloudwatch-log": "true",
    "--enable-spark-ui": "true",
    "--spark-event-logs-path": "s3://climate-health-metrics-sharvaj-2024/spark-logs/",
    "--TempDir": "s3://climate-health-temp-sharvaj-2024/temp/",
    "--SOURCE_S3_BUCKET": "climate-health-raw-sharvaj-2024",
    "--SOURCE_S3_KEY": "raw/locations.csv",
    "--TARGET_DB_CONNECTION": "climate-health-rds-connection",
    "--TARGET_TABLE_NAME": "locations"
  }
}'

# Update process-climate-data
echo "Updating process-climate-data..."
aws glue update-job --job-name process-climate-data --region eu-north-1 --job-update '{
  "Role": "AWSGlueServiceRole-ClimateHealth",
  "Command": {
    "Name": "glueetl",
    "ScriptLocation": "s3://climate-health-scripts-sharvaj-2024/etl-jobs/process_climate_data.py",
    "PythonVersion": "3"
  },
  "DefaultArguments": {
    "--job-language": "python",
    "--job-bookmark-option": "job-bookmark-enable",
    "--enable-metrics": "true",
    "--enable-continuous-cloudwatch-log": "true",
    "--TempDir": "s3://climate-health-temp-sharvaj-2024/temp/",
    "--SOURCE_S3_BUCKET": "climate-health-raw-sharvaj-2024",
    "--SOURCE_S3_KEY": "raw/climate_data.csv",
    "--TARGET_DB_CONNECTION": "climate-health-rds-connection",
    "--TARGET_TABLE_NAME": "climate_data"
  }
}'

# Update process-health-data
echo "Updating process-health-data..."
aws glue update-job --job-name process-health-data --region eu-north-1 --job-update '{
  "Role": "AWSGlueServiceRole-ClimateHealth",
  "Command": {
    "Name": "glueetl",
    "ScriptLocation": "s3://climate-health-scripts-sharvaj-2024/etl-jobs/process_health_data.py",
    "PythonVersion": "3"
  },
  "DefaultArguments": {
    "--job-language": "python",
    "--job-bookmark-option": "job-bookmark-enable",
    "--enable-metrics": "true",
    "--enable-continuous-cloudwatch-log": "true",
    "--TempDir": "s3://climate-health-temp-sharvaj-2024/temp/",
    "--SOURCE_S3_BUCKET": "climate-health-raw-sharvaj-2024",
    "--SOURCE_S3_KEY": "raw/health_data.csv",
    "--TARGET_DB_CONNECTION": "climate-health-rds-connection",
    "--TARGET_TABLE_NAME": "health_data"
  }
}'

# Update process-hospital-data
echo "Updating process-hospital-data..."
aws glue update-job --job-name process-hospital-data --region eu-north-1 --job-update '{
  "Role": "AWSGlueServiceRole-ClimateHealth",
  "Command": {
    "Name": "glueetl",
    "ScriptLocation": "s3://climate-health-scripts-sharvaj-2024/etl-jobs/process_hospital_data.py",
    "PythonVersion": "3"
  },
  "DefaultArguments": {
    "--job-language": "python",
    "--job-bookmark-option": "job-bookmark-enable",
    "--enable-metrics": "true",
    "--enable-continuous-cloudwatch-log": "true",
    "--TempDir": "s3://climate-health-temp-sharvaj-2024/temp/",
    "--SOURCE_S3_BUCKET": "climate-health-raw-sharvaj-2024",
    "--SOURCE_S3_KEY": "raw/hospital_data.csv",
    "--TARGET_DB_CONNECTION": "climate-health-rds-connection",
    "--TARGET_TABLE_NAME": "hospital_data"
  }
}'

# Update calculate-derived-metrics
echo "Updating calculate-derived-metrics..."
aws glue update-job --job-name calculate-derived-metrics --region eu-north-1 --job-update '{
  "Role": "AWSGlueServiceRole-ClimateHealth",
  "Command": {
    "Name": "glueetl",
    "ScriptLocation": "s3://climate-health-scripts-sharvaj-2024/etl-jobs/calculate_derived_metrics.py",
    "PythonVersion": "3"
  },
  "DefaultArguments": {
    "--job-language": "python",
    "--job-bookmark-option": "job-bookmark-enable",
    "--enable-metrics": "true",
    "--enable-continuous-cloudwatch-log": "true",
    "--TempDir": "s3://climate-health-temp-sharvaj-2024/temp/",
    "--TARGET_DB_CONNECTION": "climate-health-rds-connection",
    "--S3_OUTPUT_BUCKET": "climate-health-processed-sharvaj-2024",
    "--S3_OUTPUT_PATH": "metrics/"
  }
}'

echo "✅ All jobs updated successfully!"
