"""
AWS Glue ETL Job: Process Health Data
Reads health data from S3, processes it, and writes to RDS PostgreSQL database
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
    'SOURCE_S3_BUCKET',
    'SOURCE_S3_KEY',
    'TARGET_DB_CONNECTION',
    'TARGET_TABLE_NAME'
])

# Initialize Glue context
sc = SparkContext()
glueContext = GlueContext(sc)
spark = glueContext.spark_session
job = Job(glueContext)
job.init(args['JOB_NAME'], args)

logger.info(f"Starting job: {args['JOB_NAME']}")
logger.info(f"Reading from S3: s3://{args['SOURCE_S3_BUCKET']}/{args['SOURCE_S3_KEY']}")

try:
    # Read data from S3
    health_datasource = glueContext.create_dynamic_frame.from_options(
        format_options={
            "quoteChar": "\"",
            "withHeader": True,
            "separator": ",",
            "optimizePerformance": False,
        },
        connection_type="s3",
        format="csv",
        connection_options={
            "paths": [f"s3://{args['SOURCE_S3_BUCKET']}/{args['SOURCE_S3_KEY']}"],
            "recurse": True,
        },
        transformation_ctx="health_datasource",
    )
    
    logger.info(f"Loaded {health_datasource.count()} health records from S3")
    
    # Apply data transformations
    health_df = health_datasource.toDF()
    
    # Data validation and cleaning
    from pyspark.sql.functions import col, to_date, when
    from pyspark.sql.types import IntegerType, DateType, BooleanType
    
    health_df = health_df.select(
        col("location_id").cast(IntegerType()).alias("location_id"),
        to_date(col("date"), "yyyy-MM-dd").alias("date"),
        col("dengue_cases").cast(IntegerType()).alias("dengue_cases"),
        col("malaria_cases").cast(IntegerType()).alias("malaria_cases"),
        col("heatstroke_cases").cast(IntegerType()).alias("heatstroke_cases"),
        col("diarrhea_cases").cast(IntegerType()).alias("diarrhea_cases"),
        col("is_projected").cast(BooleanType()).alias("is_projected"),
        col("projection_year").cast(IntegerType()).alias("projection_year")
    )
    
    # Remove rows with null critical fields
    health_df = health_df.filter(
        (col("location_id").isNotNull()) &
        (col("date").isNotNull())
    )
    
    # Data quality checks - ensure case counts are non-negative
    health_df = health_df.withColumn(
        "dengue_cases",
        when(col("dengue_cases") < 0, 0).otherwise(col("dengue_cases"))
    )
    health_df = health_df.withColumn(
        "malaria_cases",
        when(col("malaria_cases") < 0, 0).otherwise(col("malaria_cases"))
    )
    health_df = health_df.withColumn(
        "heatstroke_cases",
        when(col("heatstroke_cases") < 0, 0).otherwise(col("heatstroke_cases"))
    )
    health_df = health_df.withColumn(
        "diarrhea_cases",
        when(col("diarrhea_cases") < 0, 0).otherwise(col("diarrhea_cases"))
    )
    
    record_count = health_df.count()
    logger.info(f"After data cleaning: {record_count} valid health records")
    
    if record_count == 0:
        raise ValueError("No valid records after data cleaning")
    
    # Convert back to DynamicFrame
    health_cleaned = DynamicFrame.fromDF(health_df, glueContext, "health_cleaned")
    
    # Apply mapping for database schema
    health_mapped = ApplyMapping.apply(
        frame=health_cleaned,
        mappings=[
            ("location_id", "int", "location_id", "int"),
            ("date", "date", "date", "date"),
            ("dengue_cases", "int", "dengue_cases", "int"),
            ("malaria_cases", "int", "malaria_cases", "int"),
            ("heatstroke_cases", "int", "heatstroke_cases", "int"),
            ("diarrhea_cases", "int", "diarrhea_cases", "int"),
            ("is_projected", "boolean", "is_projected", "boolean"),
            ("projection_year", "int", "projection_year", "int"),
        ],
        transformation_ctx="health_mapped",
    )
    
    # Write to RDS PostgreSQL
    logger.info(f"Writing to database: {args['TARGET_TABLE_NAME']}")
    
    glueContext.write_dynamic_frame.from_jdbc_conf(
        frame=health_mapped,
        catalog_connection=args['TARGET_DB_CONNECTION'],
        connection_options={
            "database": "climate_health",
            "dbtable": args['TARGET_TABLE_NAME'],
            "overwrite": "false"  # Append mode for time-series data
        },
        transformation_ctx="health_sink",
    )
    
    logger.info(f"Successfully processed and loaded {record_count} health records")
    
except Exception as e:
    logger.error(f"Job failed with error: {str(e)}")
    raise e
finally:
    job.commit()
