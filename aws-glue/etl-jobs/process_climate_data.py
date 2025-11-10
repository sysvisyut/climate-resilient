"""
AWS Glue ETL Job: Process Climate Data
Reads climate data from S3, processes it, and writes to RDS PostgreSQL database
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
    climate_datasource = glueContext.create_dynamic_frame.from_options(
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
        transformation_ctx="climate_datasource",
    )
    
    logger.info(f"Loaded {climate_datasource.count()} climate records from S3")
    
    # Apply data transformations
    climate_df = climate_datasource.toDF()
    
    # Data validation and cleaning
    from pyspark.sql.functions import col, trim, to_date, when
    from pyspark.sql.types import IntegerType, DoubleType, StringType, DateType, BooleanType
    
    climate_df = climate_df.select(
        col("location_id").cast(IntegerType()).alias("location_id"),
        to_date(col("date"), "yyyy-MM-dd").alias("date"),
        col("temperature").cast(DoubleType()).alias("temperature"),
        col("rainfall").cast(DoubleType()).alias("rainfall"),
        col("humidity").cast(DoubleType()).alias("humidity"),
        col("flood_probability").cast(DoubleType()).alias("flood_probability"),
        col("cyclone_probability").cast(DoubleType()).alias("cyclone_probability"),
        col("heatwave_probability").cast(DoubleType()).alias("heatwave_probability"),
        col("is_projected").cast(BooleanType()).alias("is_projected"),
        col("projection_year").cast(IntegerType()).alias("projection_year")
    )
    
    # Remove rows with null critical fields
    climate_df = climate_df.filter(
        (col("location_id").isNotNull()) &
        (col("date").isNotNull()) &
        (col("temperature").isNotNull())
    )
    
    # Data quality checks - ensure probabilities are between 0 and 1
    climate_df = climate_df.withColumn(
        "flood_probability",
        when((col("flood_probability") < 0) | (col("flood_probability") > 1), 0.0)
        .otherwise(col("flood_probability"))
    )
    climate_df = climate_df.withColumn(
        "cyclone_probability",
        when((col("cyclone_probability") < 0) | (col("cyclone_probability") > 1), 0.0)
        .otherwise(col("cyclone_probability"))
    )
    climate_df = climate_df.withColumn(
        "heatwave_probability",
        when((col("heatwave_probability") < 0) | (col("heatwave_probability") > 1), 0.0)
        .otherwise(col("heatwave_probability"))
    )
    
    record_count = climate_df.count()
    logger.info(f"After data cleaning: {record_count} valid climate records")
    
    if record_count == 0:
        raise ValueError("No valid records after data cleaning")
    
    # Convert back to DynamicFrame
    climate_cleaned = DynamicFrame.fromDF(climate_df, glueContext, "climate_cleaned")
    
    # Apply mapping for database schema
    climate_mapped = ApplyMapping.apply(
        frame=climate_cleaned,
        mappings=[
            ("location_id", "int", "location_id", "int"),
            ("date", "date", "date", "date"),
            ("temperature", "double", "temperature", "double"),
            ("rainfall", "double", "rainfall", "double"),
            ("humidity", "double", "humidity", "double"),
            ("flood_probability", "double", "flood_probability", "double"),
            ("cyclone_probability", "double", "cyclone_probability", "double"),
            ("heatwave_probability", "double", "heatwave_probability", "double"),
            ("is_projected", "boolean", "is_projected", "boolean"),
            ("projection_year", "int", "projection_year", "int"),
        ],
        transformation_ctx="climate_mapped",
    )
    
    # Write to RDS PostgreSQL
    logger.info(f"Writing to database: {args['TARGET_TABLE_NAME']}")
    
    glueContext.write_dynamic_frame.from_jdbc_conf(
        frame=climate_mapped,
        catalog_connection=args['TARGET_DB_CONNECTION'],
        connection_options={
            "database": "climate_health",
            "dbtable": args['TARGET_TABLE_NAME'],
            "overwrite": "false",  # Append mode for time-series data
            "preactions": "DELETE FROM climate_data WHERE location_id IN (SELECT DISTINCT location_id FROM climate_data_temp)",
            "postactions": "DROP TABLE IF EXISTS climate_data_temp"
        },
        transformation_ctx="climate_sink",
    )
    
    logger.info(f"Successfully processed and loaded {record_count} climate records")
    
except Exception as e:
    logger.error(f"Job failed with error: {str(e)}")
    raise e
finally:
    job.commit()
