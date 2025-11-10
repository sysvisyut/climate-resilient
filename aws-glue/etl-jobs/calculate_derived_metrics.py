"""
AWS Glue ETL Job: Calculate Derived Metrics
Reads processed health and hospital data, calculates risk scores and resilience metrics,
and writes results back to S3
"""

import sys
from awsglue.transforms import *
from awsglue.utils import getResolvedOptions
from pyspark.context import SparkContext
from awsglue.context import GlueContext
from awsglue.job import Job
from awsglue.dynamicframe import DynamicFrame
import logging

# Set up logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Get job parameters
args = getResolvedOptions(sys.argv, [
    'JOB_NAME',
    'SOURCE_DB_CONNECTION',
    'TARGET_S3_BUCKET',
    'TARGET_S3_PREFIX'
])

# Initialize Glue context
sc = SparkContext()
glueContext = GlueContext(sc)
spark = glueContext.spark_session
job = Job(glueContext)
job.init(args['JOB_NAME'], args)

logger.info(f"Starting job: {args['JOB_NAME']}")

try:
    # Read current health data from RDS
    health_df = glueContext.create_dynamic_frame.from_options(
        connection_type="postgresql",
        connection_options={
            "useConnectionProperties": "true",
            "dbtable": "(SELECT h.*, l.name as location_name, l.population FROM health_data h JOIN locations l ON h.location_id = l.id WHERE h.is_projected = false ORDER BY h.date DESC) AS health_view",
            "connectionName": args['SOURCE_DB_CONNECTION']
        }
    ).toDF()
    
    logger.info(f"Loaded {health_df.count()} health records")
    
    # Read current hospital data from RDS
    hospital_df = glueContext.create_dynamic_frame.from_options(
        connection_type="postgresql",
        connection_options={
            "useConnectionProperties": "true",
            "dbtable": "(SELECT h.*, l.name as location_name, l.population FROM hospital_data h JOIN locations l ON h.location_id = l.id WHERE h.is_projected = false ORDER BY h.date DESC) AS hospital_view",
            "connectionName": args['SOURCE_DB_CONNECTION']
        }
    ).toDF()
    
    logger.info(f"Loaded {hospital_df.count()} hospital records")
    
    # Import functions for calculations
    from pyspark.sql.functions import col, lit, when, least
    
    # Calculate disease rates per 100,000 people
    health_df = health_df.withColumn(
        "dengue_rate",
        (col("dengue_cases") * 100000 / col("population"))
    )
    health_df = health_df.withColumn(
        "malaria_rate",
        (col("malaria_cases") * 100000 / col("population"))
    )
    health_df = health_df.withColumn(
        "heatstroke_rate",
        (col("heatstroke_cases") * 100000 / col("population"))
    )
    health_df = health_df.withColumn(
        "diarrhea_rate",
        (col("diarrhea_cases") * 100000 / col("population"))
    )
    
    # Calculate risk scores (0-100) for each disease
    health_df = health_df.withColumn(
        "dengue_risk",
        least(col("dengue_rate") / 5.0, lit(100.0))
    )
    health_df = health_df.withColumn(
        "malaria_risk",
        least(col("malaria_rate") / 3.0, lit(100.0))
    )
    health_df = health_df.withColumn(
        "heatstroke_risk",
        least(col("heatstroke_rate") / 4.0, lit(100.0))
    )
    health_df = health_df.withColumn(
        "diarrhea_risk",
        least(col("diarrhea_rate") / 6.0, lit(100.0))
    )
    
    # Calculate overall health risk
    health_df = health_df.withColumn(
        "overall_risk",
        (col("dengue_risk") * 0.25 + 
         col("malaria_risk") * 0.25 + 
         col("heatstroke_risk") * 0.25 + 
         col("diarrhea_risk") * 0.25)
    )
    
    # Calculate resource metrics per 100,000 people
    hospital_df = hospital_df.withColumn(
        "beds_per_100k",
        (col("total_beds") * 100000 / col("population"))
    )
    hospital_df = hospital_df.withColumn(
        "available_beds_per_100k",
        (col("available_beds") * 100000 / col("population"))
    )
    hospital_df = hospital_df.withColumn(
        "doctors_per_100k",
        (col("doctors") * 100000 / col("population"))
    )
    hospital_df = hospital_df.withColumn(
        "nurses_per_100k",
        (col("nurses") * 100000 / col("population"))
    )
    
    # Calculate resource sufficiency scores (0-100, higher is better)
    hospital_df = hospital_df.withColumn(
        "beds_score",
        least(col("beds_per_100k") / 3.0, lit(100.0))
    )
    hospital_df = hospital_df.withColumn(
        "doctor_score",
        least(col("doctors_per_100k") / 1.0, lit(100.0))
    )
    hospital_df = hospital_df.withColumn(
        "nurse_score",
        least(col("nurses_per_100k") / 3.0, lit(100.0))
    )
    
    # Calculate overall resource score
    hospital_df = hospital_df.withColumn(
        "resource_score",
        (col("beds_score") * 0.4 + 
         col("doctor_score") * 0.3 + 
         col("nurse_score") * 0.3)
    )
    
    # Join health risks with resource data
    risk_resource_df = health_df.select(
        col("location_id"),
        col("date"),
        col("location_name"),
        col("overall_risk")
    ).join(
        hospital_df.select(
            col("location_id"),
            col("date"),
            col("resource_score")
        ),
        on=["location_id", "date"],
        how="inner"
    )
    
    # Calculate resilience score
    risk_resource_df = risk_resource_df.withColumn(
        "resilience_score",
        lit(100.0) - (col("overall_risk") * (lit(100.0) - col("resource_score")) / lit(100.0))
    )
    
    logger.info(f"Calculated metrics for {risk_resource_df.count()} location-date combinations")
    
    # Convert to DynamicFrames for writing
    health_metrics_df = DynamicFrame.fromDF(health_df, glueContext, "health_metrics")
    hospital_metrics_df = DynamicFrame.fromDF(hospital_df, glueContext, "hospital_metrics")
    resilience_metrics_df = DynamicFrame.fromDF(risk_resource_df, glueContext, "resilience_metrics")
    
    # Write to S3 as CSV
    glueContext.write_dynamic_frame.from_options(
        frame=health_metrics_df,
        connection_type="s3",
        format="csv",
        connection_options={
            "path": f"s3://{args['TARGET_S3_BUCKET']}/{args['TARGET_S3_PREFIX']}/current_health_risks/",
            "partitionKeys": []
        },
        format_options={
            "withHeader": True,
            "separator": ","
        },
        transformation_ctx="health_metrics_sink"
    )
    
    glueContext.write_dynamic_frame.from_options(
        frame=hospital_metrics_df,
        connection_type="s3",
        format="csv",
        connection_options={
            "path": f"s3://{args['TARGET_S3_BUCKET']}/{args['TARGET_S3_PREFIX']}/current_hospital_resources/",
            "partitionKeys": []
        },
        format_options={
            "withHeader": True,
            "separator": ","
        },
        transformation_ctx="hospital_metrics_sink"
    )
    
    glueContext.write_dynamic_frame.from_options(
        frame=resilience_metrics_df,
        connection_type="s3",
        format="csv",
        connection_options={
            "path": f"s3://{args['TARGET_S3_BUCKET']}/{args['TARGET_S3_PREFIX']}/resilience_scores/",
            "partitionKeys": []
        },
        format_options={
            "withHeader": True,
            "separator": ","
        },
        transformation_ctx="resilience_metrics_sink"
    )
    
    # Also write as JSON for API consumption
    glueContext.write_dynamic_frame.from_options(
        frame=health_metrics_df,
        connection_type="s3",
        format="json",
        connection_options={
            "path": f"s3://{args['TARGET_S3_BUCKET']}/{args['TARGET_S3_PREFIX']}/current_health_risks_json/",
            "partitionKeys": []
        },
        transformation_ctx="health_metrics_json_sink"
    )
    
    glueContext.write_dynamic_frame.from_options(
        frame=hospital_metrics_df,
        connection_type="s3",
        format="json",
        connection_options={
            "path": f"s3://{args['TARGET_S3_BUCKET']}/{args['TARGET_S3_PREFIX']}/current_hospital_resources_json/",
            "partitionKeys": []
        },
        transformation_ctx="hospital_metrics_json_sink"
    )
    
    glueContext.write_dynamic_frame.from_options(
        frame=resilience_metrics_df,
        connection_type="s3",
        format="json",
        connection_options={
            "path": f"s3://{args['TARGET_S3_BUCKET']}/{args['TARGET_S3_PREFIX']}/resilience_scores_json/",
            "partitionKeys": []
        },
        transformation_ctx="resilience_metrics_json_sink"
    )
    
    logger.info("Successfully wrote all derived metrics to S3")
    
except Exception as e:
    logger.error(f"Job failed with error: {str(e)}")
    raise e
finally:
    job.commit()
