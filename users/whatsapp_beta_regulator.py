# ─── WhatsApp Beta Testing Regulation & Control Layer ────────────────────

from datetime import datetime, timedelta
from django.db import connection
import json
import logging

from users.whatsapp_beta_config import WhatsAppBetaConfig

logger = logging.getLogger(__name__)


class WhatsAppBetaRegulator:
    """
    Central regulation system for WhatsApp beta testing
    Ensures all operations follow policy and are logged
    """

    @staticmethod
    def ensure_schema():
        """Create beta tables if setup SQL has not been run yet."""
        try:
            with connection.cursor() as cursor:
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS whatsapp_beta_testers (
                        id INT AUTO_INCREMENT PRIMARY KEY,
                        user_id INT UNIQUE NOT NULL,
                        email VARCHAR(255) NOT NULL,
                        role VARCHAR(20),
                        is_approved BOOLEAN DEFAULT FALSE,
                        approval_date DATETIME,
                        approved_by_id INT,
                        daily_message_limit INT DEFAULT 100,
                        messages_sent_today INT DEFAULT 0,
                        last_reset_date DATE,
                        is_active BOOLEAN DEFAULT TRUE,
                        status_reason TEXT,
                        date_joined_beta DATETIME DEFAULT CURRENT_TIMESTAMP,
                        last_used DATETIME,
                        total_messages_sent INT DEFAULT 0,
                        INDEX idx_user_id (user_id),
                        INDEX idx_approved (is_approved),
                        INDEX idx_active (is_active)
                    )
                """)
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS whatsapp_beta_usage_logs (
                        id INT AUTO_INCREMENT PRIMARY KEY,
                        user_id INT NOT NULL,
                        action_type VARCHAR(50),
                        message_type VARCHAR(50),
                        recipient_phone VARCHAR(20),
                        recipient_name VARCHAR(255),
                        status VARCHAR(20),
                        error_message TEXT,
                        message_preview VARCHAR(500),
                        message_length INT,
                        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                        ip_address VARCHAR(45),
                        user_agent TEXT,
                        metadata JSON,
                        INDEX idx_user_timestamp (user_id, timestamp),
                        INDEX idx_status (status),
                        INDEX idx_timestamp (timestamp)
                    )
                """)
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS whatsapp_beta_compliance (
                        id INT AUTO_INCREMENT PRIMARY KEY,
                        user_id INT NOT NULL,
                        alert_type VARCHAR(30),
                        severity VARCHAR(10),
                        message TEXT,
                        is_resolved BOOLEAN DEFAULT FALSE,
                        resolved_by_id INT,
                        resolution_notes TEXT,
                        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                        resolved_at DATETIME,
                        INDEX idx_user_timestamp (user_id, timestamp),
                        INDEX idx_resolved (is_resolved),
                        INDEX idx_severity (severity)
                    )
                """)
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS whatsapp_beta_messages (
                        id INT AUTO_INCREMENT PRIMARY KEY,
                        user_id INT NOT NULL,
                        recipient_phone VARCHAR(20),
                        recipient_name VARCHAR(255),
                        message_content TEXT,
                        message_type VARCHAR(50),
                        status VARCHAR(20) DEFAULT 'pending',
                        sent_at DATETIME,
                        failed_reason TEXT,
                        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                        updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                        template_used VARCHAR(50),
                        attachments JSON,
                        metadata JSON,
                        INDEX idx_user_created (user_id, created_at),
                        INDEX idx_status (status),
                        INDEX idx_recipient_phone (recipient_phone)
                    )
                """)
            return True
        except Exception as e:
            logger.error(f"Error ensuring WhatsApp beta schema: {e}")
            return False

    @staticmethod
    def ensure_beta_tester(user_id, email="", role="support", auto_approve=False):
        """Register a local-system actor as a beta tester if missing."""
        WhatsAppBetaRegulator.ensure_schema()
        try:
            daily_limit = WhatsAppBetaConfig.RATE_LIMITS.get(role, 50)
            with connection.cursor() as cursor:
                cursor.execute("""
                    INSERT INTO whatsapp_beta_testers (
                        user_id, email, role, is_approved, approval_date,
                        daily_message_limit, last_reset_date, is_active
                    )
                    VALUES (%s, %s, %s, %s, CASE WHEN %s THEN NOW() ELSE NULL END, %s, CURDATE(), 1)
                    ON DUPLICATE KEY UPDATE
                        email = VALUES(email),
                        role = VALUES(role),
                        daily_message_limit = GREATEST(daily_message_limit, VALUES(daily_message_limit)),
                        last_reset_date = COALESCE(last_reset_date, CURDATE())
                """, [
                    user_id,
                    email or f"user-{user_id}@local",
                    role,
                    1 if auto_approve else 0,
                    1 if auto_approve else 0,
                    daily_limit,
                ])
            return True
        except Exception as e:
            logger.error(f"Error registering beta tester: {e}")
            return False
    
    @staticmethod
    def validate_user_access(user_id):
        """
        Validate if user has access to WhatsApp beta features
        Returns: (is_allowed, reason)
        """
        try:
            WhatsAppBetaRegulator.ensure_schema()
            # Check if beta is enabled globally
            if not WhatsAppBetaConfig.BETA_ENABLED:
                return False, "WhatsApp beta testing is currently disabled"
            
            # Check if user is approved beta tester
            with connection.cursor() as cursor:
                cursor.execute("""
                    SELECT is_approved, is_active, status_reason 
                    FROM whatsapp_beta_testers 
                    WHERE user_id = %s
                """, [user_id])
                result = cursor.fetchone()
                
                if not result:
                    return False, "User is not registered for WhatsApp beta testing"
                
                is_approved, is_active, reason = result
                
                if not is_active:
                    return False, f"Your access is inactive: {reason}"
                
                if not is_approved:
                    return False, "Your access is not yet approved"
                
            return True, "Access granted"
            
        except Exception as e:
            logger.error(f"Error validating user access: {e}")
            return False, "Error validating access"
    
    @staticmethod
    def check_rate_limit(user_id):
        """
        Check if user has exceeded rate limit
        Returns: (can_send, messages_remaining, reset_time)
        """
        try:
            WhatsAppBetaRegulator.ensure_schema()
            with connection.cursor() as cursor:
                cursor.execute("""
                    SELECT 
                        messages_sent_today, 
                        daily_message_limit,
                        last_reset_date,
                        role
                    FROM whatsapp_beta_testers 
                    WHERE user_id = %s
                """, [user_id])
                result = cursor.fetchone()
                
                if not result:
                    return False, 0, None
                
                sent, limit, last_reset, role = result
                
                # Reset if day changed
                today = datetime.now().date()
                if last_reset is None or last_reset < today:
                    with connection.cursor() as update_cursor:
                        update_cursor.execute("""
                            UPDATE whatsapp_beta_testers 
                            SET messages_sent_today = 0, last_reset_date = %s
                            WHERE user_id = %s
                        """, [today, user_id])
                    sent = 0
                
                can_send = sent < limit
                remaining = limit - sent
                reset_time = datetime.now().replace(hour=0, minute=0, second=0) + timedelta(days=1)
                
                return can_send, remaining, reset_time
                
        except Exception as e:
            logger.error(f"Error checking rate limit: {e}")
            return False, 0, None
    
    @staticmethod
    def validate_feature(feature_name, user_id=None):
        """
        Validate if a feature is enabled and allowed for user
        Returns: (is_enabled, reason)
        """
        # Check if feature is generally enabled
        if not WhatsAppBetaConfig.is_feature_enabled(feature_name):
            return False, f"Feature '{feature_name}' is not enabled in beta"
        
        # Feature-specific validation
        if feature_name == "scheduled_messages":
            return False, "Scheduled messages are coming soon"
        
        return True, "Feature is available"
    
    @staticmethod
    def log_usage(user_id, action_type, message_type, recipient_phone, 
                  recipient_name, status, message_preview, ip_address, 
                  user_agent, error_message=None, metadata=None):
        """
        Log WhatsApp beta usage for compliance and analytics
        """
        try:
            WhatsAppBetaRegulator.ensure_schema()
            with connection.cursor() as cursor:
                cursor.execute("""
                    INSERT INTO whatsapp_beta_usage_logs (
                        user_id, action_type, message_type, recipient_phone,
                        recipient_name, status, error_message, message_preview,
                        message_length, ip_address, user_agent, metadata
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """, [
                    user_id, action_type, message_type, recipient_phone,
                    recipient_name, status, error_message, message_preview,
                    len(message_preview), ip_address, user_agent,
                    json.dumps(metadata or {})
                ])
                
            logger.info(f"Logged WhatsApp usage: user={user_id}, action={action_type}, status={status}")
            
        except Exception as e:
            logger.error(f"Error logging usage: {e}")
    
    @staticmethod
    def check_compliance_alerts(user_id):
        """
        Check for compliance violations
        Returns: list of alert tuples (alert_type, severity, message)
        """
        alerts = []
        
        try:
            # Check for high usage
            with connection.cursor() as cursor:
                cursor.execute("""
                    SELECT COUNT(*) FROM whatsapp_beta_usage_logs
                    WHERE user_id = %s 
                    AND timestamp >= DATE_SUB(NOW(), INTERVAL 1 HOUR)
                    AND status = 'success'
                """, [user_id])
                
                recent_count = cursor.fetchone()[0]
                
                if recent_count > 50:
                    alerts.append(("high_usage", "high", 
                        f"User sent {recent_count} messages in last hour"))
            
            # Check for failures
            with connection.cursor() as cursor:
                cursor.execute("""
                    SELECT COUNT(*) FROM whatsapp_beta_usage_logs
                    WHERE user_id = %s 
                    AND timestamp >= DATE_SUB(NOW(), INTERVAL 24 HOUR)
                    AND status = 'failed'
                """, [user_id])
                
                failed_count = cursor.fetchone()[0]
                
                if failed_count > 10:
                    alerts.append(("message_failure", "medium",
                        f"User had {failed_count} failed messages in last 24 hours"))
            
            # Check for rate limit violations
            with connection.cursor() as cursor:
                cursor.execute("""
                    SELECT COUNT(*) FROM whatsapp_beta_usage_logs
                    WHERE user_id = %s 
                    AND timestamp >= DATE_SUB(NOW(), INTERVAL 7 DAY)
                    AND status = 'rate_limit_exceeded'
                """, [user_id])
                
                limit_violations = cursor.fetchone()[0]
                
                if limit_violations > 5:
                    alerts.append(("rate_limit_violation", "medium",
                        f"User exceeded rate limits {limit_violations} times"))
                        
        except Exception as e:
            logger.error(f"Error checking compliance alerts: {e}")
        
        return alerts
    
    @staticmethod
    def create_compliance_alert(user_id, alert_type, severity, message):
        """Create a compliance alert in database"""
        try:
            with connection.cursor() as cursor:
                cursor.execute("""
                    INSERT INTO whatsapp_beta_compliance (
                        user_id, alert_type, severity, message
                    ) VALUES (%s, %s, %s, %s)
                """, [user_id, alert_type, severity, message])
                
            logger.warning(f"Compliance alert created: user={user_id}, type={alert_type}")
            
        except Exception as e:
            logger.error(f"Error creating compliance alert: {e}")
    
    @staticmethod
    def approve_beta_tester(user_id, approved_by_id, daily_limit=100):
        """Approve a user for beta testing"""
        try:
            with connection.cursor() as cursor:
                cursor.execute("""
                    UPDATE whatsapp_beta_testers
                    SET is_approved = 1, 
                        approval_date = NOW(),
                        approved_by_id = %s,
                        daily_message_limit = %s,
                        is_active = 1
                    WHERE user_id = %s
                """, [approved_by_id, daily_limit, user_id])
                
            logger.info(f"Beta tester approved: user={user_id}")
            return True, "User approved for beta testing"
            
        except Exception as e:
            logger.error(f"Error approving beta tester: {e}")
            return False, f"Error: {str(e)}"
    
    @staticmethod
    def deactivate_beta_tester(user_id, reason):
        """Deactivate a user from beta testing"""
        try:
            with connection.cursor() as cursor:
                cursor.execute("""
                    UPDATE whatsapp_beta_testers
                    SET is_active = 0, status_reason = %s
                    WHERE user_id = %s
                """, [reason, user_id])
                
            logger.info(f"Beta tester deactivated: user={user_id}, reason={reason}")
            return True, "User deactivated from beta testing"
            
        except Exception as e:
            logger.error(f"Error deactivating beta tester: {e}")
            return False, f"Error: {str(e)}"
    
    @staticmethod
    def get_usage_statistics(user_id, days=7):
        """Get usage statistics for a user"""
        try:
            with connection.cursor() as cursor:
                cursor.execute("""
                    SELECT 
                        DATE(timestamp) as date,
                        COUNT(*) as total,
                        SUM(CASE WHEN status = 'success' THEN 1 ELSE 0 END) as successful,
                        SUM(CASE WHEN status = 'failed' THEN 1 ELSE 0 END) as failed,
                        SUM(CASE WHEN status = 'rate_limit_exceeded' THEN 1 ELSE 0 END) as rate_limited
                    FROM whatsapp_beta_usage_logs
                    WHERE user_id = %s AND timestamp >= DATE_SUB(NOW(), INTERVAL %s DAY)
                    GROUP BY DATE(timestamp)
                    ORDER BY date DESC
                """, [user_id, days])
                
                columns = ['date', 'total', 'successful', 'failed', 'rate_limited']
                stats = []
                for row in cursor.fetchall():
                    stats.append(dict(zip(columns, row)))
                
                return stats
                
        except Exception as e:
            logger.error(f"Error getting usage statistics: {e}")
            return []
