"""
AWS Glue ETL Job: Process Hospital Data
Reads hospital resource data from S3, processes it, and writes to RDS PostgreSQL database
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
    hospital_datasource = glueContext.create_dynamic_frame.from_options(
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
        transformation_ctx="hospital_datasource",
    )
    
    logger.info(f"Loaded {hospital_datasource.count()} hospital records from S3")
    
    # Apply data transformations
    hospital_df = hospital_datasource.toDF()
    
    # Data validation and cleaning
    from pyspark.sql.functions import col, to_date, when
    from pyspark.sql.types import IntegerType, DateType, BooleanType
    
    hospital_df = hospital_df.select(
        col("location_id").cast(IntegerType()).alias("location_id"),
        to_date(col("date"), "yyyy-MM-dd").alias("date"),
        col("total_beds").cast(IntegerType()).alias("total_beds"),
        col("available_beds").cast(IntegerType()).alias("available_beds"),
        col("doctors").cast(IntegerType()).alias("doctors"),
        col("nurses").cast(IntegerType()).alias("nurses"),
        col("iv_fluids_stock").cast(IntegerType()).alias("iv_fluids_stock"),
        col("antibiotics_stock").cast(IntegerType()).alias("antibiotics_stock"),
        col("antipyretics_stock").cast(IntegerType()).alias("antipyretics_stock"),
        col("is_projected").cast(BooleanType()).alias("is_projected"),
        col("projection_year").cast(IntegerType()).alias("projection_year")
    )
    
    # Remove rows with null critical fields
    hospital_df = hospital_df.filter(
        (col("location_id").isNotNull()) &
        (col("date").isNotNull())
    )
    
    # Data quality checks - ensure non-negative values
    hospital_df = hospital_df.withColumn(
        "total_beds",
        when(col("total_beds") < 0, 0).otherwise(col("total_beds"))
    )
    hospital_df = hospital_df.withColumn(
        "available_beds",
        when(col("available_beds") < 0, 0).otherwise(col("available_beds"))
    )
    hospital_df = hospital_df.withColumn(
        "doctors",
        when(col("doctors") < 0, 0).otherwise(col("doctors"))
    )
    hospital_df = hospital_df.withColumn(
        "nurses",
        when(col("nurses") < 0, 0).otherwise(col("nurses"))
    )
    hospital_df = hospital_df.withColumn(
        "iv_fluids_stock",
        when(col("iv_fluids_stock") < 0, 0).otherwise(col("iv_fluids_stock"))
    )
    hospital_df = hospital_df.withColumn(
        "antibiotics_stock",
        when(col("antibiotics_stock") < 0, 0).otherwise(col("antibiotics_stock"))
    )
    hospital_df = hospital_df.withColumn(
        "antipyretics_stock",
        when(col("antipyretics_stock") < 0, 0).otherwise(col("antipyretics_stock"))
    )
    
    # Ensure available_beds <= total_beds
    hospital_df = hospital_df.withColumn(
        "available_beds",
        when(col("available_beds") > col("total_beds"), col("total_beds"))
        .otherwise(col("available_beds"))
    )
    
    record_count = hospital_df.count()
    logger.info(f"After data cleaning: {record_count} valid hospital records")
    
    if record_count == 0:
        raise ValueError("No valid records after data cleaning")
    
    # Convert back to DynamicFrame
    hospital_cleaned = DynamicFrame.fromDF(hospital_df, glueContext, "hospital_cleaned")
    
    # Apply mapping for database schema
    hospital_mapped = ApplyMapping.apply(
        frame=hospital_cleaned,
        mappings=[
            ("location_id", "int", "location_id", "int"),
            ("date", "date", "date", "date"),
            ("total_beds", "int", "total_beds", "int"),
            ("available_beds", "int", "available_beds", "int"),
            ("doctors", "int", "doctors", "int"),
            ("nurses", "int", "nurses", "int"),
            ("iv_fluids_stock", "int", "iv_fluids_stock", "int"),
            ("antibiotics_stock", "int", "antibiotics_stock", "int"),
            ("antipyretics_stock", "int", "antipyretics_stock", "int"),
            ("is_projected", "boolean", "is_projected", "boolean"),
            ("projection_year", "int", "projection_year", "int"),
        ],
        transformation_ctx="hospital_mapped",
    )
    
    # Write to RDS PostgreSQL
    logger.info(f"Writing to database: {args['TARGET_TABLE_NAME']}")
    
    glueContext.write_dynamic_frame.from_jdbc_conf(
        frame=hospital_mapped,
        catalog_connection=args['TARGET_DB_CONNECTION'],
        connection_options={
            "database": "climate_health",
            "dbtable": args['TARGET_TABLE_NAME'],
            "overwrite": "false"  # Append mode for time-series data
        },
        transformation_ctx="hospital_sink",
    )
    
    logger.info(f"Successfully processed and loaded {record_count} hospital records")
    
except Exception as e:
    logger.error(f"Job failed with error: {str(e)}")
    raise e
finally:
    job.commit()
