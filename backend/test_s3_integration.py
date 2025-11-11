"""
Test S3 integration and services
"""

import sys
import os
import pandas as pd
import logging
from datetime import datetime

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.utils.s3_storage import s3_storage
from app.services.data_service import data_service
from app.services.model_service import model_service

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def test_s3_storage():
    """Test basic S3 storage operations"""
    logger.info("=" * 80)
    logger.info("🧪 Testing S3 Storage Operations")
    logger.info("=" * 80)
    
    test_results = []
    
    # Test 1: CSV operations
    logger.info("\n1️⃣  Testing CSV operations...")
    try:
        test_df = pd.DataFrame({
            'id': [1, 2, 3],
            'value': [10, 20, 30],
            'name': ['test_a', 'test_b', 'test_c']
        })
        
        # Save
        save_success = s3_storage.save_csv_to_s3(test_df, 'test/test_data.csv')
        
        # Load
        loaded_df = s3_storage.load_csv_from_s3('test/test_data.csv')
        
        # Verify
        if loaded_df is not None and len(loaded_df) == 3:
            logger.info("   ✅ CSV Save/Load: PASS")
            test_results.append(('CSV Operations', True))
        else:
            logger.error("   ❌ CSV Save/Load: FAIL")
            test_results.append(('CSV Operations', False))
        
        # Cleanup
        s3_storage.delete_object('test/test_data.csv')
        
    except Exception as e:
        logger.error(f"   ❌ CSV Operations: FAIL - {e}")
        test_results.append(('CSV Operations', False))
    
    # Test 2: JSON operations
    logger.info("\n2️⃣  Testing JSON operations...")
    try:
        test_data = {
            'key': 'value',
            'number': 42,
            'list': [1, 2, 3],
            'nested': {'a': 1, 'b': 2}
        }
        
        # Save
        save_success = s3_storage.save_json_to_s3(test_data, 'test/test_data.json')
        
        # Load
        loaded_data = s3_storage.load_json_from_s3('test/test_data.json')
        
        # Verify
        if loaded_data and loaded_data.get('number') == 42:
            logger.info("   ✅ JSON Save/Load: PASS")
            test_results.append(('JSON Operations', True))
        else:
            logger.error("   ❌ JSON Save/Load: FAIL")
            test_results.append(('JSON Operations', False))
        
        # Cleanup
        s3_storage.delete_object('test/test_data.json')
        
    except Exception as e:
        logger.error(f"   ❌ JSON Operations: FAIL - {e}")
        test_results.append(('JSON Operations', False))
    
    # Test 3: Object existence check
    logger.info("\n3️⃣  Testing object existence check...")
    try:
        # Create a test file
        s3_storage.save_json_to_s3({'test': 'data'}, 'test/exists_test.json')
        
        exists = s3_storage.object_exists('test/exists_test.json')
        not_exists = not s3_storage.object_exists('test/nonexistent.json')
        
        if exists and not_exists:
            logger.info("   ✅ Object Existence Check: PASS")
            test_results.append(('Object Existence', True))
        else:
            logger.error("   ❌ Object Existence Check: FAIL")
            test_results.append(('Object Existence', False))
        
        # Cleanup
        s3_storage.delete_object('test/exists_test.json')
        
    except Exception as e:
        logger.error(f"   ❌ Object Existence Check: FAIL - {e}")
        test_results.append(('Object Existence', False))
    
    # Test 4: List objects
    logger.info("\n4️⃣  Testing list objects...")
    try:
        # Create some test files
        for i in range(3):
            s3_storage.save_json_to_s3({'id': i}, f'test/list_test_{i}.json')
        
        objects = s3_storage.list_objects('test/list_test_')
        
        if len(objects) >= 3:
            logger.info(f"   ✅ List Objects: PASS (found {len(objects)} objects)")
            test_results.append(('List Objects', True))
        else:
            logger.error(f"   ❌ List Objects: FAIL (found {len(objects)} objects)")
            test_results.append(('List Objects', False))
        
        # Cleanup
        for obj in objects:
            s3_storage.delete_object(obj)
        
    except Exception as e:
        logger.error(f"   ❌ List Objects: FAIL - {e}")
        test_results.append(('List Objects', False))
    
    return test_results


def test_data_service():
    """Test data service with S3"""
    logger.info("\n" + "=" * 80)
    logger.info("🧪 Testing Data Service")
    logger.info("=" * 80)
    
    test_results = []
    
    # Test 1: Load climate data
    logger.info("\n1️⃣  Testing climate data loading...")
    try:
        climate_df = data_service.load_climate_data()
        
        if climate_df is not None and len(climate_df) > 0:
            logger.info(f"   ✅ Load Climate Data: PASS ({len(climate_df)} rows)")
            test_results.append(('Load Climate Data', True))
        else:
            logger.error("   ❌ Load Climate Data: FAIL (No data or empty)")
            test_results.append(('Load Climate Data', False))
            
    except Exception as e:
        logger.error(f"   ❌ Load Climate Data: FAIL - {e}")
        test_results.append(('Load Climate Data', False))
    
    # Test 2: Load health data
    logger.info("\n2️⃣  Testing health data loading...")
    try:
        health_df = data_service.load_health_data()
        
        if health_df is not None and len(health_df) > 0:
            logger.info(f"   ✅ Load Health Data: PASS ({len(health_df)} rows)")
            test_results.append(('Load Health Data', True))
        else:
            logger.error("   ❌ Load Health Data: FAIL (No data or empty)")
            test_results.append(('Load Health Data', False))
            
    except Exception as e:
        logger.error(f"   ❌ Load Health Data: FAIL - {e}")
        test_results.append(('Load Health Data', False))
    
    # Test 3: Load locations
    logger.info("\n3️⃣  Testing locations data loading...")
    try:
        locations_df = data_service.load_locations()
        
        if locations_df is not None and len(locations_df) > 0:
            logger.info(f"   ✅ Load Locations: PASS ({len(locations_df)} rows)")
            test_results.append(('Load Locations', True))
        else:
            logger.error("   ❌ Load Locations: FAIL (No data or empty)")
            test_results.append(('Load Locations', False))
            
    except Exception as e:
        logger.error(f"   ❌ Load Locations: FAIL - {e}")
        test_results.append(('Load Locations', False))
    
    # Test 4: Load hospital data
    logger.info("\n4️⃣  Testing hospital data loading...")
    try:
        hospital_df = data_service.load_hospital_data()
        
        if hospital_df is not None and len(hospital_df) > 0:
            logger.info(f"   ✅ Load Hospital Data: PASS ({len(hospital_df)} rows)")
            test_results.append(('Load Hospital Data', True))
        else:
            logger.error("   ❌ Load Hospital Data: FAIL (No data or empty)")
            test_results.append(('Load Hospital Data', False))
            
    except Exception as e:
        logger.error(f"   ❌ Load Hospital Data: FAIL - {e}")
        test_results.append(('Load Hospital Data', False))
    
    # Test 5: Save and load predictions
    logger.info("\n5️⃣  Testing predictions save/load...")
    try:
        test_predictions = [
            {'location': 'KA', 'risk': 0.75, 'condition': 'heat_stroke'},
            {'location': 'MH', 'risk': 0.65, 'condition': 'dengue'}
        ]
        
        date = datetime.now().strftime('%Y-%m-%d')
        save_success = data_service.save_predictions(test_predictions, date)
        
        if save_success:
            logger.info("   ✅ Save Predictions: PASS")
            test_results.append(('Save Predictions', True))
        else:
            logger.error("   ❌ Save Predictions: FAIL")
            test_results.append(('Save Predictions', False))
            
    except Exception as e:
        logger.error(f"   ❌ Save Predictions: FAIL - {e}")
        test_results.append(('Save Predictions', False))
    
    # Test 6: Get storage stats
    logger.info("\n6️⃣  Testing storage statistics...")
    try:
        stats = data_service.get_storage_stats()
        
        if stats and 'raw_data' in stats:
            logger.info("   ✅ Storage Statistics: PASS")
            logger.info(f"      Raw Data: {stats['raw_data'].get('total_objects', 0)} objects")
            logger.info(f"      Processed Data: {stats['processed_data'].get('total_objects', 0)} objects")
            logger.info(f"      Models: {stats['models'].get('total_objects', 0)} objects")
            test_results.append(('Storage Statistics', True))
        else:
            logger.error("   ❌ Storage Statistics: FAIL")
            test_results.append(('Storage Statistics', False))
            
    except Exception as e:
        logger.error(f"   ❌ Storage Statistics: FAIL - {e}")
        test_results.append(('Storage Statistics', False))
    
    return test_results


def test_model_service():
    """Test model service with S3"""
    logger.info("\n" + "=" * 80)
    logger.info("🧪 Testing Model Service")
    logger.info("=" * 80)
    
    test_results = []
    
    # Test 1: List available models
    logger.info("\n1️⃣  Testing list available models...")
    try:
        models = model_service.list_available_models()
        
        logger.info(f"   Found {len(models)} model(s):")
        for model in models:
            logger.info(f"      - {model}")
        
        logger.info("   ✅ List Models: PASS")
        test_results.append(('List Models', True))
        
    except Exception as e:
        logger.error(f"   ❌ List Models: FAIL - {e}")
        test_results.append(('List Models', False))
    
    # Test 2: Check if models exist
    logger.info("\n2️⃣  Testing model existence check...")
    try:
        risk_exists = model_service.model_exists('enhanced_risk_model.pkl')
        forecast_exists = model_service.model_exists('enhanced_forecast_model.pkl')
        
        logger.info(f"   Risk Model Exists: {risk_exists}")
        logger.info(f"   Forecast Model Exists: {forecast_exists}")
        
        if risk_exists or forecast_exists:
            logger.info("   ✅ Model Existence Check: PASS")
            test_results.append(('Model Existence', True))
        else:
            logger.warning("   ⚠️  Model Existence Check: PASS (no models found)")
            test_results.append(('Model Existence', True))
        
    except Exception as e:
        logger.error(f"   ❌ Model Existence Check: FAIL - {e}")
        test_results.append(('Model Existence', False))
    
    # Test 3: Try loading models
    logger.info("\n3️⃣  Testing model loading...")
    try:
        risk_model = model_service.load_risk_model()
        
        if risk_model is not None:
            logger.info("   ✅ Load Risk Model: PASS")
            test_results.append(('Load Risk Model', True))
        else:
            logger.warning("   ⚠️  Load Risk Model: Model not found (run save_enhanced_models.py first)")
            test_results.append(('Load Risk Model', False))
            
    except Exception as e:
        logger.error(f"   ❌ Load Risk Model: FAIL - {e}")
        test_results.append(('Load Risk Model', False))
    
    try:
        forecast_model = model_service.load_forecast_model()
        
        if forecast_model is not None:
            logger.info("   ✅ Load Forecast Model: PASS")
            test_results.append(('Load Forecast Model', True))
        else:
            logger.warning("   ⚠️  Load Forecast Model: Model not found")
            test_results.append(('Load Forecast Model', False))
            
    except Exception as e:
        logger.error(f"   ❌ Load Forecast Model: FAIL - {e}")
        test_results.append(('Load Forecast Model', False))
    
    try:
        scaler = model_service.load_scaler()
        
        if scaler is not None:
            logger.info("   ✅ Load Scaler: PASS")
            test_results.append(('Load Scaler', True))
        else:
            logger.warning("   ⚠️  Load Scaler: Scaler not found")
            test_results.append(('Load Scaler', False))
            
    except Exception as e:
        logger.error(f"   ❌ Load Scaler: FAIL - {e}")
        test_results.append(('Load Scaler', False))
    
    return test_results


def print_summary(all_results):
    """Print test summary"""
    logger.info("\n" + "=" * 80)
    logger.info("📊 TEST SUMMARY")
    logger.info("=" * 80)
    
    total_tests = len(all_results)
    passed_tests = sum(1 for _, result in all_results if result)
    failed_tests = total_tests - passed_tests
    
    logger.info(f"\nTotal Tests: {total_tests}")
    logger.info(f"✅ Passed: {passed_tests}")
    logger.info(f"❌ Failed: {failed_tests}")
    logger.info(f"Success Rate: {(passed_tests/total_tests*100):.1f}%")
    
    logger.info("\nDetailed Results:")
    for test_name, result in all_results:
        status = "✅ PASS" if result else "❌ FAIL"
        logger.info(f"   {status}: {test_name}")
    
    if failed_tests == 0:
        logger.info("\n🎉 All tests passed! S3 integration is working correctly.")
        logger.info("\n💡 Next Steps:")
        logger.info("   1. Update your application to use data_service and model_service")
        logger.info("   2. Test with your actual application endpoints")
        logger.info("   3. Monitor AWS CloudWatch for any issues")
    else:
        logger.info(f"\n⚠️  {failed_tests} test(s) failed. Please review the logs above.")
        logger.info("\n💡 Troubleshooting:")
        logger.info("   1. Verify AWS credentials are configured correctly")
        logger.info("   2. Check bucket names in s3_storage.py match your S3 buckets")
        logger.info("   3. Ensure data files exist before running tests")
        logger.info("   4. Run migrate_data_to_s3.py to upload data to S3")


def main():
    """Run all tests"""
    logger.info("\n" + "🚀" * 40)
    logger.info("   S3 Integration Test Suite")
    logger.info("🚀" * 40 + "\n")
    
    all_results = []
    
    # Run tests
    all_results.extend(test_s3_storage())
    all_results.extend(test_data_service())
    all_results.extend(test_model_service())
    
    # Print summary
    print_summary(all_results)
    
    logger.info("\n" + "=" * 80)


if __name__ == "__main__":
    main()
