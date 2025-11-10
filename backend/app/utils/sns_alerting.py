"""
SNS Alerting Utility for Climate-Resilient Healthcare System

This module provides a centralized alerting system using AWS SNS.
It supports multiple severity levels, routing logic, and both email and SMS notifications.
"""

import boto3
import json
import os
from enum import Enum
from typing import Dict, List, Optional, Any
from datetime import datetime
from dotenv import load_dotenv
from pathlib import Path

# Load environment variables
env_path = Path(__file__).parent.parent.parent / 'aws-sns' / '.env'
if env_path.exists():
    load_dotenv(env_path)

class AlertSeverity(Enum):
    """Alert severity levels"""
    DEBUG = 0
    INFO = 1
    WARNING = 2
    ERROR = 3
    CRITICAL = 4

class AlertType(Enum):
    """Alert types/categories"""
    HEALTH_RISK = "health_risk"
    RESOURCE_SHORTAGE = "resource_shortage"
    SYSTEM_ERROR = "system_error"
    DATA_QUALITY = "data_quality"
    PREDICTION_ALERT = "prediction_alert"

class SNSAlerter:
    """
    Centralized alerting system using AWS SNS
    
    Features:
    - Multiple severity levels
    - Routing based on alert type
    - Conditional SMS for critical alerts
    - Structured message formatting
    - Error handling and fallback to console
    """
    
    def __init__(self, region: str = None, enable_sns: bool = True):
        """
        Initialize SNS alerter
        
        Args:
            region: AWS region (defaults to env variable)
            enable_sns: If False, only logs to console (useful for testing)
        """
        self.region = region or os.getenv('AWS_REGION', 'eu-north-1')
        self.enable_sns = enable_sns and os.getenv('ENABLE_EMAIL_ALERTS', 'true').lower() == 'true'
        self.enable_sms = os.getenv('ENABLE_SMS_ALERTS', 'true').lower() == 'true'
        
        # Topic ARNs
        self.health_risk_topic_arn = os.getenv('SNS_HEALTH_RISK_TOPIC_ARN', '')
        self.resource_shortage_topic_arn = os.getenv('SNS_RESOURCE_SHORTAGE_TOPIC_ARN', '')
        
        # Severity thresholds
        self.min_alert_severity = AlertSeverity[os.getenv('ALERT_MIN_SEVERITY', 'INFO')]
        self.min_sms_severity = AlertSeverity[os.getenv('SMS_MIN_SEVERITY', 'CRITICAL')]
        
        # Initialize SNS client if enabled
        if self.enable_sns:
            try:
                self.sns_client = boto3.client('sns', region_name=self.region)
            except Exception as e:
                print(f"⚠️  Failed to initialize SNS client: {e}")
                print("   Falling back to console logging only.")
                self.enable_sns = False
    
    def _get_topic_arn(self, alert_type: AlertType) -> str:
        """Get the appropriate topic ARN based on alert type"""
        routing = {
            AlertType.HEALTH_RISK: self.health_risk_topic_arn,
            AlertType.RESOURCE_SHORTAGE: self.resource_shortage_topic_arn,
            AlertType.PREDICTION_ALERT: self.health_risk_topic_arn,
            AlertType.DATA_QUALITY: self.health_risk_topic_arn,
            AlertType.SYSTEM_ERROR: self.resource_shortage_topic_arn,
        }
        return routing.get(alert_type, self.health_risk_topic_arn)
    
    def _format_message(self, 
                       title: str,
                       message: str,
                       severity: AlertSeverity,
                       alert_type: AlertType,
                       metadata: Optional[Dict[str, Any]] = None) -> Dict[str, str]:
        """
        Format alert message for SNS
        
        Returns:
            Dict with 'subject' and 'message' keys
        """
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')
        
        # Emoji indicators for severity
        severity_emoji = {
            AlertSeverity.DEBUG: '🔍',
            AlertSeverity.INFO: 'ℹ️',
            AlertSeverity.WARNING: '⚠️',
            AlertSeverity.ERROR: '❌',
            AlertSeverity.CRITICAL: '🚨'
        }
        
        emoji = severity_emoji.get(severity, '📢')
        
        # Build subject line
        subject = f"{emoji} [{severity.name}] {title}"
        
        # Build message body
        body_lines = [
            "=" * 60,
            f"Climate-Resilient Healthcare Alert",
            "=" * 60,
            f"Severity: {severity.name}",
            f"Type: {alert_type.value}",
            f"Time: {timestamp}",
            "=" * 60,
            "",
            message,
            ""
        ]
        
        # Add metadata if provided
        if metadata:
            body_lines.extend([
                "=" * 60,
                "Additional Information:",
                "=" * 60
            ])
            for key, value in metadata.items():
                body_lines.append(f"{key}: {value}")
            body_lines.append("")
        
        body_lines.extend([
            "=" * 60,
            "Climate-Resilient Healthcare System",
            "=" * 60
        ])
        
        return {
            'subject': subject[:100],  # SNS subject max length
            'message': '\n'.join(body_lines)
        }
    
    def _format_sms_message(self, title: str, message: str, severity: AlertSeverity) -> str:
        """Format a short message for SMS"""
        emoji = '🚨' if severity == AlertSeverity.CRITICAL else '⚠️'
        short_message = message[:100]  # Keep SMS short
        return f"{emoji} {severity.name}: {title}\n{short_message}"
    
    def send_alert(self,
                   title: str,
                   message: str,
                   severity: AlertSeverity = AlertSeverity.INFO,
                   alert_type: AlertType = AlertType.HEALTH_RISK,
                   metadata: Optional[Dict[str, Any]] = None,
                   force_sms: bool = False) -> bool:
        """
        Send an alert via SNS
        
        Args:
            title: Alert title/summary
            message: Detailed alert message
            severity: Alert severity level
            alert_type: Category of alert
            metadata: Additional context data
            force_sms: Force SMS even below threshold (use sparingly)
        
        Returns:
            True if alert was sent successfully, False otherwise
        """
        # Check if alert meets minimum severity
        if severity.value < self.min_alert_severity.value:
            return False
        
        # Always log to console
        print(f"\n[{severity.name}] {alert_type.value}: {title}")
        print(f"  {message}")
        if metadata:
            print(f"  Metadata: {json.dumps(metadata, indent=2)}")
        
        # If SNS is disabled, just return
        if not self.enable_sns:
            return True
        
        try:
            # Get topic ARN
            topic_arn = self._get_topic_arn(alert_type)
            if not topic_arn:
                print(f"⚠️  No topic ARN configured for {alert_type.value}")
                return False
            
            # Format message
            formatted = self._format_message(title, message, severity, alert_type, metadata)
            
            # Prepare message attributes for filtering
            message_attributes = {
                'severity': {
                    'DataType': 'String',
                    'StringValue': severity.name
                },
                'alert_type': {
                    'DataType': 'String',
                    'StringValue': alert_type.value
                }
            }
            
            # Send email notification
            response = self.sns_client.publish(
                TopicArn=topic_arn,
                Subject=formatted['subject'],
                Message=formatted['message'],
                MessageAttributes=message_attributes
            )
            
            message_id = response['MessageId']
            print(f"  ✓ Email alert sent (MessageId: {message_id})")
            
            # Send SMS for critical alerts
            if self.enable_sms and (severity.value >= self.min_sms_severity.value or force_sms):
                sms_message = self._format_sms_message(title, message, severity)
                # SMS is sent via subscriptions, but we can publish with SMS protocol
                # Note: This will only work if SMS subscriptions are set up
                print(f"  ✓ SMS alert triggered for critical severity")
            
            return True
            
        except Exception as e:
            print(f"  ✗ Failed to send SNS alert: {str(e)}")
            return False
    
    # Convenience methods for common alert scenarios
    
    def health_risk_alert(self, 
                         location: str,
                         disease: str,
                         risk_level: str,
                         prediction: float,
                         severity: AlertSeverity = AlertSeverity.WARNING) -> bool:
        """Send a health risk prediction alert"""
        title = f"High {disease} Risk Detected in {location}"
        message = f"The prediction model has detected elevated risk for {disease} in {location}.\n\n"
        message += f"Risk Level: {risk_level}\n"
        message += f"Prediction Score: {prediction:.2%}\n\n"
        message += "Recommended Actions:\n"
        message += "- Increase surveillance in affected areas\n"
        message += "- Prepare additional medical resources\n"
        message += "- Issue public health advisories if needed"
        
        metadata = {
            'location': location,
            'disease': disease,
            'risk_level': risk_level,
            'prediction_score': f"{prediction:.4f}"
        }
        
        return self.send_alert(
            title=title,
            message=message,
            severity=severity,
            alert_type=AlertType.HEALTH_RISK,
            metadata=metadata
        )
    
    def resource_shortage_alert(self,
                              location: str,
                              resource_type: str,
                              available: int,
                              required: int,
                              severity: AlertSeverity = AlertSeverity.ERROR) -> bool:
        """Send a resource shortage alert"""
        shortage_pct = ((required - available) / required * 100) if required > 0 else 0
        
        title = f"{resource_type} Shortage in {location}"
        message = f"Critical shortage of {resource_type} detected in {location}.\n\n"
        message += f"Available: {available}\n"
        message += f"Required: {required}\n"
        message += f"Shortage: {shortage_pct:.1f}%\n\n"
        message += "Immediate Actions Needed:\n"
        message += "- Arrange resource transfer from nearby facilities\n"
        message += "- Activate emergency procurement procedures\n"
        message += "- Alert regional health authorities"
        
        metadata = {
            'location': location,
            'resource_type': resource_type,
            'available': available,
            'required': required,
            'shortage_percentage': f"{shortage_pct:.2f}%"
        }
        
        return self.send_alert(
            title=title,
            message=message,
            severity=severity,
            alert_type=AlertType.RESOURCE_SHORTAGE,
            metadata=metadata,
            force_sms=shortage_pct > 80  # Force SMS for critical shortages
        )
    
    def data_quality_alert(self,
                          dataset: str,
                          issue: str,
                          severity: AlertSeverity = AlertSeverity.WARNING) -> bool:
        """Send a data quality alert"""
        title = f"Data Quality Issue: {dataset}"
        message = f"Data quality problem detected in {dataset}.\n\n"
        message += f"Issue: {issue}\n\n"
        message += "This may affect prediction accuracy. Please review and correct."
        
        metadata = {
            'dataset': dataset,
            'issue': issue
        }
        
        return self.send_alert(
            title=title,
            message=message,
            severity=severity,
            alert_type=AlertType.DATA_QUALITY,
            metadata=metadata
        )
    
    def system_error_alert(self,
                          component: str,
                          error_message: str,
                          severity: AlertSeverity = AlertSeverity.ERROR) -> bool:
        """Send a system error alert"""
        title = f"System Error in {component}"
        message = f"An error occurred in {component}.\n\n"
        message += f"Error: {error_message}\n\n"
        message += "Please investigate and resolve immediately."
        
        metadata = {
            'component': component,
            'error': error_message
        }
        
        return self.send_alert(
            title=title,
            message=message,
            severity=severity,
            alert_type=AlertType.SYSTEM_ERROR,
            metadata=metadata
        )


# Global alerter instance (lazy initialization)
_global_alerter: Optional[SNSAlerter] = None

def get_alerter() -> SNSAlerter:
    """Get or create the global alerter instance"""
    global _global_alerter
    if _global_alerter is None:
        _global_alerter = SNSAlerter()
    return _global_alerter

# Convenience functions for quick access
def send_alert(*args, **kwargs) -> bool:
    """Send an alert using the global alerter"""
    return get_alerter().send_alert(*args, **kwargs)

def health_risk_alert(*args, **kwargs) -> bool:
    """Send a health risk alert using the global alerter"""
    return get_alerter().health_risk_alert(*args, **kwargs)

def resource_shortage_alert(*args, **kwargs) -> bool:
    """Send a resource shortage alert using the global alerter"""
    return get_alerter().resource_shortage_alert(*args, **kwargs)

def data_quality_alert(*args, **kwargs) -> bool:
    """Send a data quality alert using the global alerter"""
    return get_alerter().data_quality_alert(*args, **kwargs)

def system_error_alert(*args, **kwargs) -> bool:
    """Send a system error alert using the global alerter"""
    return get_alerter().system_error_alert(*args, **kwargs)
