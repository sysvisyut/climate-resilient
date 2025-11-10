#!/usr/bin/env python3
"""
Test script for SNS alerting system
Sends test alerts through both topics to verify configuration
"""

import sys
import os
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'backend'))

from app.utils.sns_alerting import (
    SNSAlerter, 
    AlertSeverity, 
    AlertType,
    health_risk_alert,
    resource_shortage_alert,
    data_quality_alert,
    system_error_alert
)

def test_basic_alerts():
    """Test basic alert functionality"""
    print("=" * 70)
    print("Testing Basic Alert Functionality")
    print("=" * 70)
    
    alerter = SNSAlerter()
    
    # Test INFO alert
    print("\n1. Testing INFO level alert...")
    alerter.send_alert(
        title="System Started",
        message="The Climate-Resilient Healthcare System has started successfully.",
        severity=AlertSeverity.INFO,
        alert_type=AlertType.HEALTH_RISK
    )
    
    # Test WARNING alert
    print("\n2. Testing WARNING level alert...")
    alerter.send_alert(
        title="High Temperature Detected",
        message="Temperature readings above 40°C detected in multiple locations.",
        severity=AlertSeverity.WARNING,
        alert_type=AlertType.HEALTH_RISK,
        metadata={
            'max_temperature': '42.5°C',
            'affected_locations': '15 districts'
        }
    )
    
    # Test ERROR alert
    print("\n3. Testing ERROR level alert...")
    alerter.send_alert(
        title="Database Connection Issue",
        message="Failed to connect to the database. Retrying...",
        severity=AlertSeverity.ERROR,
        alert_type=AlertType.SYSTEM_ERROR
    )

def test_health_risk_alerts():
    """Test health risk specific alerts"""
    print("\n" + "=" * 70)
    print("Testing Health Risk Alerts")
    print("=" * 70)
    
    # Dengue risk alert
    print("\n1. Testing Dengue risk alert...")
    health_risk_alert(
        location="Mumbai, Maharashtra",
        disease="Dengue",
        risk_level="HIGH",
        prediction=0.78,
        severity=AlertSeverity.WARNING
    )
    
    # Malaria risk alert
    print("\n2. Testing Malaria risk alert...")
    health_risk_alert(
        location="Kolkata, West Bengal",
        disease="Malaria",
        risk_level="CRITICAL",
        prediction=0.89,
        severity=AlertSeverity.CRITICAL
    )

def test_resource_shortage_alerts():
    """Test resource shortage alerts"""
    print("\n" + "=" * 70)
    print("Testing Resource Shortage Alerts")
    print("=" * 70)
    
    # Hospital beds shortage
    print("\n1. Testing hospital beds shortage...")
    resource_shortage_alert(
        location="Delhi Central Hospital",
        resource_type="ICU Beds",
        available=5,
        required=50,
        severity=AlertSeverity.CRITICAL
    )
    
    # Ventilator shortage
    print("\n2. Testing ventilator shortage...")
    resource_shortage_alert(
        location="Chennai Regional Hospital",
        resource_type="Ventilators",
        available=3,
        required=20,
        severity=AlertSeverity.ERROR
    )
    
    # Medical staff shortage
    print("\n3. Testing medical staff shortage...")
    resource_shortage_alert(
        location="Bangalore District Hospital",
        resource_type="Nurses",
        available=15,
        required=40,
        severity=AlertSeverity.WARNING
    )

def test_data_quality_alerts():
    """Test data quality alerts"""
    print("\n" + "=" * 70)
    print("Testing Data Quality Alerts")
    print("=" * 70)
    
    print("\n1. Testing missing data alert...")
    data_quality_alert(
        dataset="climate_data",
        issue="Missing temperature readings for 15 locations in the past 24 hours",
        severity=AlertSeverity.WARNING
    )
    
    print("\n2. Testing anomaly detection alert...")
    data_quality_alert(
        dataset="health_data",
        issue="Unusual spike in reported cases - possible data entry error",
        severity=AlertSeverity.INFO
    )

def test_system_alerts():
    """Test system error alerts"""
    print("\n" + "=" * 70)
    print("Testing System Error Alerts")
    print("=" * 70)
    
    print("\n1. Testing API error alert...")
    system_error_alert(
        component="Weather API",
        error_message="Rate limit exceeded - 429 Too Many Requests",
        severity=AlertSeverity.ERROR
    )
    
    print("\n2. Testing prediction model error...")
    system_error_alert(
        component="ML Prediction Model",
        error_message="Model file corrupted or missing",
        severity=AlertSeverity.CRITICAL
    )

def test_all_severity_levels():
    """Test all severity levels"""
    print("\n" + "=" * 70)
    print("Testing All Severity Levels")
    print("=" * 70)
    
    alerter = SNSAlerter()
    
    severities = [
        (AlertSeverity.DEBUG, "Debug message - system trace"),
        (AlertSeverity.INFO, "Info message - routine notification"),
        (AlertSeverity.WARNING, "Warning message - attention needed"),
        (AlertSeverity.ERROR, "Error message - problem detected"),
        (AlertSeverity.CRITICAL, "Critical message - immediate action required"),
    ]
    
    for severity, msg in severities:
        print(f"\nTesting {severity.name} level...")
        alerter.send_alert(
            title=f"Test {severity.name} Alert",
            message=msg,
            severity=severity,
            alert_type=AlertType.HEALTH_RISK
        )

def main():
    print("=" * 70)
    print("AWS SNS Alerting System - Test Suite")
    print("=" * 70)
    print("\nThis script will send test alerts to verify your SNS configuration.")
    print("Make sure you have:")
    print("  1. Run setup_sns.py to create topics")
    print("  2. Confirmed email subscriptions")
    print("  3. Updated .env with topic ARNs")
    
    input("\nPress Enter to start testing (or Ctrl+C to cancel)...")
    
    try:
        # Run all tests
        test_basic_alerts()
        test_health_risk_alerts()
        test_resource_shortage_alerts()
        test_data_quality_alerts()
        test_system_alerts()
        test_all_severity_levels()
        
        print("\n" + "=" * 70)
        print("All Tests Complete!")
        print("=" * 70)
        print("\n✓ Check your email inbox for test alerts")
        print("✓ Check your phone for SMS alerts (critical only)")
        print("✓ Check AWS SNS console for delivery status")
        print("\nIf you didn't receive alerts, check:")
        print("  - Email subscriptions are confirmed")
        print("  - Topic ARNs in .env are correct")
        print("  - AWS credentials have SNS publish permissions")
        print("  - Check SNS console > Topics > Your Topic > Recent Deliveries")
        
    except KeyboardInterrupt:
        print("\n\nTest cancelled by user.")
    except Exception as e:
        print(f"\n✗ Error during testing: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    main()
