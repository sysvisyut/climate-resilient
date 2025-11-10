"""
Example Integration: Using SNS Alerts in Prediction Router

This file demonstrates how to integrate SNS alerting into your existing code.
Replace console prints with SNS alerts for important events.
"""

# Example 1: Replace error logging with SNS alerts
# BEFORE:
# print(f"Error predicting risks for {location.name}: {e}")

# AFTER:
from app.utils.sns_alerting import system_error_alert, AlertSeverity

try:
    # ... prediction code ...
    pass
except Exception as e:
    system_error_alert(
        component="Prediction Engine",
        error_message=f"Failed to predict risks for {location.name}: {str(e)}",
        severity=AlertSeverity.ERROR
    )


# Example 2: Alert on high risk predictions
# BEFORE:
# if risk_score > 0.7:
#     print(f"High risk detected for {disease} in {location}")

# AFTER:
from app.utils.sns_alerting import health_risk_alert, AlertSeverity

if risk_score > 0.7:
    severity = AlertSeverity.CRITICAL if risk_score > 0.9 else AlertSeverity.WARNING
    health_risk_alert(
        location=location_name,
        disease=disease_name,
        risk_level="HIGH" if risk_score > 0.9 else "MODERATE",
        prediction=risk_score,
        severity=severity
    )


# Example 3: Alert on resource shortages
# BEFORE:
# if available_beds < required_beds:
#     print(f"Bed shortage in {hospital_name}")

# AFTER:
from app.utils.sns_alerting import resource_shortage_alert, AlertSeverity

if available_beds < required_beds:
    shortage_pct = ((required_beds - available_beds) / required_beds) * 100
    severity = AlertSeverity.CRITICAL if shortage_pct > 80 else AlertSeverity.WARNING
    
    resource_shortage_alert(
        location=hospital_name,
        resource_type="Hospital Beds",
        available=available_beds,
        required=required_beds,
        severity=severity
    )


# Example 4: Alert on data quality issues
# BEFORE:
# if missing_data_count > threshold:
#     print(f"Warning: Missing data in {dataset_name}")

# AFTER:
from app.utils.sns_alerting import data_quality_alert, AlertSeverity

if missing_data_count > threshold:
    data_quality_alert(
        dataset=dataset_name,
        issue=f"Missing {missing_data_count} data points (>{threshold} threshold)",
        severity=AlertSeverity.WARNING
    )


# Example 5: Integration in FastAPI endpoint
from fastapi import APIRouter
from app.utils.sns_alerting import health_risk_alert, system_error_alert, AlertSeverity

router = APIRouter()

@router.get("/predictions/{location_id}")
async def get_predictions(location_id: int):
    try:
        # Get predictions
        predictions = get_location_predictions(location_id)
        
        # Check for high-risk conditions and alert
        for disease, risk_data in predictions.items():
            if risk_data['risk_score'] > 0.75:
                # Send alert for high risk
                health_risk_alert(
                    location=risk_data['location_name'],
                    disease=disease,
                    risk_level=risk_data['risk_level'],
                    prediction=risk_data['risk_score'],
                    severity=AlertSeverity.WARNING
                )
        
        return predictions
        
    except Exception as e:
        # Log error and send alert
        system_error_alert(
            component="Predictions API",
            error_message=f"Failed to get predictions for location {location_id}: {str(e)}",
            severity=AlertSeverity.ERROR
        )
        raise


# Example 6: Batch processing with alerts
def process_daily_predictions():
    """Daily batch job that sends alerts for high-risk locations"""
    from app.utils.sns_alerting import send_alert, AlertType, AlertSeverity
    
    try:
        locations = get_all_locations()
        high_risk_locations = []
        
        for location in locations:
            predictions = calculate_risk(location)
            
            if predictions['max_risk'] > 0.8:
                high_risk_locations.append({
                    'name': location.name,
                    'disease': predictions['primary_disease'],
                    'risk': predictions['max_risk']
                })
        
        # Send summary alert if any high-risk locations found
        if high_risk_locations:
            summary = "\\n".join([
                f"- {loc['name']}: {loc['disease']} ({loc['risk']:.1%})"
                for loc in high_risk_locations
            ])
            
            send_alert(
                title=f"Daily Risk Summary: {len(high_risk_locations)} High-Risk Locations",
                message=f"The following locations have elevated health risks:\\n\\n{summary}",
                severity=AlertSeverity.WARNING,
                alert_type=AlertType.HEALTH_RISK,
                metadata={'high_risk_count': len(high_risk_locations)}
            )
    
    except Exception as e:
        system_error_alert(
            component="Daily Predictions Batch Job",
            error_message=str(e),
            severity=AlertSeverity.CRITICAL
        )


# Example 7: Conditional alerting based on configuration
def smart_alert(title, message, **kwargs):
    """
    Smart alerting that respects configuration and prevents alert fatigue
    """
    from app.utils.sns_alerting import send_alert
    import os
    
    # Check if alerting is enabled
    if os.getenv('ENABLE_ALERTS', 'true').lower() != 'true':
        print(f"[ALERT DISABLED] {title}: {message}")
        return False
    
    # Implement rate limiting or deduplication here if needed
    # (e.g., don't send same alert more than once per hour)
    
    return send_alert(title=title, message=message, **kwargs)
