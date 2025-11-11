"""
Migrate existing local data to S3 buckets
"""

import os
import sys
import pandas as pd
import logging
from pathlib import Path

# Add backend to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.utils.s3_storage import s3_storage

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def migrate_raw_data():
    """Migrate local raw data files to S3"""
    
    # Define local data directory
    data_dir = Path(__file__).parent / 'data' / 'raw'
    
    if not data_dir.exists():
        logger.warning(f"Raw data directory not found: {data_dir}")
        return False
    
    # Raw data files to migrate
    raw_files = {
        'climate_data.csv': 'raw/climate_data.csv',
        'health_data.csv': 'raw/health_data.csv',
        'hospital_data.csv': 'raw/hospital_data.csv',
        'locations.csv': 'raw/locations.csv'
    }
    
    logger.info("=" * 80)
    logger.info("📦 Starting raw data migration to S3...")
    logger.info("=" * 80)
    
    success_count = 0
    fail_count = 0
    
    for local_file, s3_key in raw_files.items():
        local_path = data_dir / local_file
        
        if local_path.exists():
            try:
                # Read CSV
                df = pd.read_csv(local_path)
                logger.info(f"\n📄 Processing {local_file}...")
                logger.info(f"   Rows: {len(df)}")
                logger.info(f"   Size: {local_path.stat().st_size / 1024:.2f} KB")
                
                # Save to S3
                success = s3_storage.save_csv_to_s3(
                    df, 
                    s3_key, 
                    s3_storage.RAW_DATA_BUCKET
                )
                
                if success:
                    logger.info(f"   ✅ Successfully migrated to s3://{s3_storage.RAW_DATA_BUCKET}/{s3_key}")
                    success_count += 1
                else:
                    logger.error(f"   ❌ Failed to migrate {local_file}")
                    fail_count += 1
                    
            except Exception as e:
                logger.error(f"   ❌ Error migrating {local_file}: {e}")
                fail_count += 1
        else:
            logger.warning(f"   ⚠️  File not found: {local_path}")
            fail_count += 1
    
    logger.info(f"\n📊 Raw Data Migration Summary:")
    logger.info(f"   ✅ Success: {success_count}")
    logger.info(f"   ❌ Failed: {fail_count}")
    
    return fail_count == 0


def migrate_processed_data():
    """Migrate processed data to S3"""
    
    processed_dir = Path(__file__).parent / 'data' / 'processed'
    
    if not processed_dir.exists():
        logger.warning(f"\n⚠️  Processed data directory not found: {processed_dir}")
        logger.info("   Skipping processed data migration.")
        return True
    
    logger.info("\n" + "=" * 80)
    logger.info("📊 Starting processed data migration to S3...")
    logger.info("=" * 80)
    
    success_count = 0
    fail_count = 0
    
    # Find all CSV files in processed directory
    csv_files = list(processed_dir.glob('**/*.csv'))
    
    if not csv_files:
        logger.info("   No processed CSV files found.")
        return True
    
    for csv_file in csv_files:
        try:
            # Get relative path
            rel_path = csv_file.relative_to(processed_dir)
            s3_key = f"processed/{rel_path}"
            
            logger.info(f"\n📄 Processing {rel_path}...")
            
            # Read and upload
            df = pd.read_csv(csv_file)
            logger.info(f"   Rows: {len(df)}")
            logger.info(f"   Size: {csv_file.stat().st_size / 1024:.2f} KB")
            
            success = s3_storage.save_csv_to_s3(df, s3_key)
            
            if success:
                logger.info(f"   ✅ Successfully migrated to s3://{s3_storage.PROCESSED_DATA_BUCKET}/{s3_key}")
                success_count += 1
            else:
                logger.error(f"   ❌ Failed to migrate {rel_path}")
                fail_count += 1
                
        except Exception as e:
            logger.error(f"   ❌ Error migrating {csv_file}: {e}")
            fail_count += 1
    
    logger.info(f"\n📊 Processed Data Migration Summary:")
    logger.info(f"   ✅ Success: {success_count}")
    logger.info(f"   ❌ Failed: {fail_count}")
    
    return fail_count == 0


def migrate_models():
    """Migrate ML models to S3"""
    
    models_dir = Path(__file__).parent / 'models'
    
    if not models_dir.exists():
        logger.warning(f"\n⚠️  Models directory not found: {models_dir}")
        logger.info("   Skipping models migration. Run save_enhanced_models.py first.")
        return True
    
    logger.info("\n" + "=" * 80)
    logger.info("🤖 Starting models migration to S3...")
    logger.info("=" * 80)
    
    success_count = 0
    fail_count = 0
    
    # Find all model files
    model_extensions = ['.pkl', '.joblib', '.h5', '.pt', '.pth', '.json']
    model_files = [f for f in models_dir.iterdir() if f.suffix in model_extensions]
    
    if not model_files:
        logger.info("   No model files found.")
        return True
    
    for model_file in model_files:
        try:
            s3_key = f"models/{model_file.name}"
            
            logger.info(f"\n📄 Processing {model_file.name}...")
            logger.info(f"   Size: {model_file.stat().st_size / 1024:.2f} KB")
            
            # Upload file directly
            success = s3_storage.upload_file_to_s3(
                str(model_file),
                s3_key,
                s3_storage.MODELS_BUCKET
            )
            
            if success:
                logger.info(f"   ✅ Successfully migrated to s3://{s3_storage.MODELS_BUCKET}/{s3_key}")
                success_count += 1
            else:
                logger.error(f"   ❌ Failed to migrate {model_file.name}")
                fail_count += 1
                
        except Exception as e:
            logger.error(f"   ❌ Error migrating {model_file.name}: {e}")
            fail_count += 1
    
    logger.info(f"\n📊 Models Migration Summary:")
    logger.info(f"   ✅ Success: {success_count}")
    logger.info(f"   ❌ Failed: {fail_count}")
    
    return fail_count == 0


def verify_migration():
    """Verify data was migrated successfully"""
    
    logger.info("\n" + "=" * 80)
    logger.info("🔍 Verifying Migration...")
    logger.info("=" * 80)
    
    # Check raw data bucket
    logger.info(f"\n📦 Raw Data Bucket: {s3_storage.RAW_DATA_BUCKET}")
    raw_objects = s3_storage.list_objects('raw/', s3_storage.RAW_DATA_BUCKET)
    logger.info(f"   Total objects: {len(raw_objects)}")
    for obj in raw_objects:
        logger.info(f"   ✓ {obj}")
    
    # Check processed data bucket
    logger.info(f"\n📊 Processed Data Bucket: {s3_storage.PROCESSED_DATA_BUCKET}")
    processed_objects = s3_storage.list_objects('processed/', s3_storage.PROCESSED_DATA_BUCKET)
    logger.info(f"   Total objects: {len(processed_objects)}")
    if processed_objects:
        for obj in processed_objects[:10]:  # Show first 10
            logger.info(f"   ✓ {obj}")
        if len(processed_objects) > 10:
            logger.info(f"   ... and {len(processed_objects) - 10} more")
    
    # Check models bucket
    logger.info(f"\n🤖 Models Bucket: {s3_storage.MODELS_BUCKET}")
    model_objects = s3_storage.list_objects('models/', s3_storage.MODELS_BUCKET)
    logger.info(f"   Total objects: {len(model_objects)}")
    for obj in model_objects:
        logger.info(f"   ✓ {obj}")
    
    # Get bucket sizes
    logger.info("\n📊 Bucket Statistics:")
    
    buckets = [
        ('Raw Data', s3_storage.RAW_DATA_BUCKET),
        ('Processed Data', s3_storage.PROCESSED_DATA_BUCKET),
        ('Models', s3_storage.MODELS_BUCKET)
    ]
    
    for name, bucket in buckets:
        stats = s3_storage.get_bucket_size(bucket)
        logger.info(f"   {name}:")
        logger.info(f"      Objects: {stats.get('total_objects', 0)}")
        logger.info(f"      Size: {stats.get('total_size_mb', 0)} MB")
    
    return True


def main():
    """Run migration"""
    logger.info("\n" + "🚀" * 40)
    logger.info("   Starting Data Migration to S3")
    logger.info("🚀" * 40 + "\n")
    
    # Migrate data
    raw_success = migrate_raw_data()
    processed_success = migrate_processed_data()
    models_success = migrate_models()
    
    # Verify
    verify_migration()
    
    # Final summary
    logger.info("\n" + "=" * 80)
    logger.info("📋 FINAL MIGRATION SUMMARY")
    logger.info("=" * 80)
    logger.info(f"   Raw Data: {'✅ SUCCESS' if raw_success else '❌ FAILED'}")
    logger.info(f"   Processed Data: {'✅ SUCCESS' if processed_success else '❌ FAILED'}")
    logger.info(f"   Models: {'✅ SUCCESS' if models_success else '❌ FAILED'}")
    
    if raw_success and processed_success and models_success:
        logger.info("\n🎉 All data successfully migrated to S3!")
        logger.info("\n💡 Next Steps:")
        logger.info("   1. Test S3 integration: python test_s3_integration.py")
        logger.info("   2. Update your application to use S3 services")
        logger.info("   3. Optionally remove local data files after verification")
    else:
        logger.info("\n⚠️  Some migrations failed. Please check the logs above.")
    
    logger.info("\n" + "=" * 80)


if __name__ == "__main__":
    main()
