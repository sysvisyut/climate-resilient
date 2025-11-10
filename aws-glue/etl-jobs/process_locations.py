"""
AWS Glue ETL Job: Process Locations Data
Reads location data from S3, processes it, and writes to RDS PostgreSQL database
"""

import sys
from awsglue.transforms import ApplyMapping
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
    locations_datasource = glueContext.create_dynamic_frame.from_options(
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
        transformation_ctx="locations_datasource",
    )
    
    logger.info(f"Loaded {locations_datasource.count()} location records from S3")
    
    # Apply data transformations
    # Convert DynamicFrame to Spark DataFrame for easier manipulation
    locations_df = locations_datasource.toDF()
    
    # Data validation and cleaning
    # Ensure required columns exist and have correct types
    from pyspark.sql.functions import col, trim, when, lit
    from pyspark.sql.types import IntegerType, DoubleType, StringType
    
    # Support multiple possible source schemas. Prefer 'location_id' if present, else fall back to 'id'.
    src_columns = locations_df.columns
    logger.info(f"Source columns detected: {src_columns}")
    
    # Convert columns to lowercase for case-insensitive matching
    src_columns_lower = [c.lower() for c in src_columns]
    
    # Find ID column
    id_col = None
    for i, c in enumerate(src_columns_lower):
        if c in ['location_id', 'id', 'locationid']:
            id_col = src_columns[i]
            break
    
    if not id_col:
        raise ValueError(f'No id/location_id column found in source. Available columns: {src_columns}')

    # Name may be 'district' or 'name'
    name_col = None
    for i, c in enumerate(src_columns_lower):
        if c in ['district', 'name', 'location_name']:
            name_col = src_columns[i]
            break
    if not name_col:
        name_col = src_columns[0]  # fallback to first column

    # Type may be 'urban_rural' or 'type'
    type_col = None
    for i, c in enumerate(src_columns_lower):
        if c in ['urban_rural', 'type', 'location_type', 'urbanrural']:
            type_col = src_columns[i]
            break

    # Area/population may exist
    population_col = None
    for i, c in enumerate(src_columns_lower):
        if c == 'population':
            population_col = src_columns[i]
            break
    
    area_col = None
    for i, c in enumerate(src_columns_lower):
        if c == 'area':
            area_col = src_columns[i]
            break

    select_expr = [
        col(id_col).cast(IntegerType()).alias('id'),
        trim(col(name_col)).cast(StringType()).alias('name')
    ]
    
    if type_col:
        select_expr.append(trim(col(type_col)).cast(StringType()).alias('type'))
    else:
        # Default type if not found
        select_expr.append(lit('Unknown').alias('type'))
    
    if population_col:
        select_expr.append(col(population_col).cast(IntegerType()).alias('population'))
    else:
        # Default population if not found
        select_expr.append(lit(0).alias('population'))
    
    if area_col:
        select_expr.append(col(area_col).cast(DoubleType()).alias('area'))
    else:
        # Default area if not found (use 0.0)
        select_expr.append(lit(0.0).alias('area'))

    locations_df = locations_df.select(*select_expr)
    
    # Remove any rows with null critical fields
    locations_df = locations_df.filter(
        (col("id").isNotNull()) &
        (col("name").isNotNull())
    )
    
    # Add data quality checks
    record_count = locations_df.count()
    logger.info(f"After data cleaning: {record_count} valid location records")
    
    if record_count == 0:
        raise ValueError("No valid records after data cleaning")
    
    # Convert back to DynamicFrame
    locations_cleaned = DynamicFrame.fromDF(locations_df, glueContext, "locations_cleaned")
    
    # Write directly to RDS PostgreSQL (no need for ApplyMapping since we already have correct schema)
    logger.info(f"Writing to database: {args['TARGET_TABLE_NAME']}")
    
    glueContext.write_dynamic_frame.from_jdbc_conf(
        frame=locations_cleaned,
        catalog_connection=args['TARGET_DB_CONNECTION'],
        connection_options={
            "database": "climate_health",
            "dbtable": args['TARGET_TABLE_NAME'],
            "overwrite": "true"  # Use "append" for incremental loads
        },
        transformation_ctx="locations_sink",
    )
    
    logger.info(f"Successfully processed and loaded {record_count} location records")
    
    # Log statistics
    logger.info("Job completed successfully")
    
except Exception as e:
    logger.error(f"Job failed with error: {str(e)}")
    raise e
finally:
    job.commit()
