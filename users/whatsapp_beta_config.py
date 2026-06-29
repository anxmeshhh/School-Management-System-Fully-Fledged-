# ─── WhatsApp Beta Testing Configuration & Regulation ────────────────────

from django.db import connection
from datetime import datetime, timedelta
import json
import re

class WhatsAppBetaConfig:
    """
    Centralized configuration and regulation for WhatsApp beta testing
    Ensures consistency across the system
    """
    
    # Beta Testing Status
    BETA_ENABLED = True
    BETA_VERSION = "1.1"
    
    # Rate Limiting (messages per day per user)
    RATE_LIMITS = {
        "admin": 500,  # Administrators
        "teacher": 50,  # Teachers
        "support": 200,  # Support staff
    }
    
    # Feature Flags
    FEATURES = {
        "send_student_pdfs": True,
        "send_notifications": True,
        "send_parent_circulars": True,
        "send_birthday_messages": True,
        "send_late_messages": True,
        "send_leave_messages": True,
        "bulk_messaging": True,
        "bulk_announcement": True,
        "scheduled_messages": False,  # Coming soon
    }
    
    # Allowed domains for WhatsApp links
    WHATSAPP_API_ENDPOINT = "https://wa.me/"
    
    # Message templates (for consistency)
    MESSAGE_TEMPLATES = {
        "student_pdf": {
            "subject": "Student Document from {school_name}",
            "template": "Hello {name},\n\nPlease find your student document below:\n\nName: {name}\nAdmission No: {admission_number}\n\nDownload PDF:\n{pdf_url}\n\nRegards,\n{school_name} Administration"
        },
        "parent_circular": {
            "subject": "Circular from {school_name}",
            "template": "Dear Parent,\n\nA new circular has been published.\n\nTitle: {title}\nClass/Section: {class_section}\nDate: {date}\n\nView circular:\n{circular_url}\n\nRegards,\n{school_name}"
        },
        "birthday": {
            "subject": "Birthday Wishes from {school_name}",
            "template": "Dear Parent,\n\nWishing {student_name} a very happy birthday from {school_name}.\n\nClass/Section: {class_section}\nDate of Birth: {dob}\n\nRegards,\n{school_name}"
        },
        "late": {
            "subject": "Late Arrival Notice from {school_name}",
            "template": "Dear Parent,\n\nThis is to inform you that {student_name} arrived late today.\n\nClass/Section: {class_section}\nDate: {date}\nTime: {time}\nReason/Note: {reason}\n\nRegards,\n{school_name}"
        },
        "leave": {
            "subject": "Leave Request Update from {school_name}",
            "template": "Dear Parent,\n\nLeave request update for {student_name}:\n\nStatus: {status}\nFrom: {start_date}\nTo: {end_date}\nDuration: {duration}\nReason: {reason}\n\nRegards,\n{school_name}"
        },
        "notification": {
            "subject": "Important Notification from {school_name}",
            "template": "Dear Parent,\n\n{message}\n\nRegards,\n{school_name}"
        },
        "system_announcement": {
            "subject": "Welcome to {school_name} Online Portal",
            "template": "Dear Parent,\n\nWe are pleased to inform you that {school_name} has launched an online School Management Portal.\n\nYou can now:\n- View your child's attendance\n- Check homework & study materials\n- Track progress cards\n- Apply for leave requests\n\nTo get started, please visit:\n{portal_url}\n\nFor login credentials or registration, please contact the school office.\n\nRegards,\n{school_name} Administration"
        },
        "credentials_share": {
            "subject": "Login Credentials from {school_name}",
            "template": "Dear Parent,\n\nWelcome to {school_name} School Management System!\n\nYour parent account has been created for your child *{student_name}*.\n\nHere are your login credentials:\n\n*Login Portal:*\n{portal_url}\n\n*Your Credentials:*\nRegistered Phone: {mobile}\nAdmission Number: {admission_number}\n\nPlease use your registered phone number and the password you set (or contact the school office for your password) to log in.\n\nRegards,\n{school_name} Administration"
        }
    }

    TEMPLATE_FEATURES = {
        "student_pdf": "send_student_pdfs",
        "parent_circular": "send_parent_circulars",
        "birthday": "send_birthday_messages",
        "late": "send_late_messages",
        "leave": "send_leave_messages",
        "notification": "send_notifications",
        "system_announcement": "bulk_announcement",
        "credentials_share": "send_notifications",
    }

    REQUIRED_TEMPLATE_FIELDS = {
        "student_pdf": ["name", "student_id"],
        "parent_circular": ["title", "circular_url"],
        "birthday": ["student_name"],
        "late": ["student_name", "date"],
        "leave": ["student_name", "status"],
        "notification": ["message"],
        "system_announcement": ["portal_url"],
        "credentials_share": ["student_name", "admission_number", "portal_url"],
    }
    
    # Logging configuration
    ENABLE_LOGGING = True
    LOG_LEVEL = "INFO"  # INFO, WARNING, ERROR
    
    @staticmethod
    def get_user_role(user_id):
        """Determine user role from database"""
        try:
            with connection.cursor() as cursor:
                cursor.execute("""
                    SELECT role FROM auth_user 
                    LEFT JOIN admin_profile ON auth_user.id = admin_profile.user_id
                    WHERE auth_user.id = %s
                """, [user_id])
                result = cursor.fetchone()
                
                if result:
                    role = result[0]
                    if role in ["admin", "superuser"]:
                        return "admin"
                    elif role == "teacher":
                        return "teacher"
                    else:
                        return "support"
                        
                return "support"
        except Exception as e:
            return "support"
    
    @staticmethod
    def get_rate_limit(user_id):
        """Get rate limit for user based on role"""
        role = WhatsAppBetaConfig.get_user_role(user_id)
        return WhatsAppBetaConfig.RATE_LIMITS.get(role, 50)
    
    @staticmethod
    def is_feature_enabled(feature_name):
        """Check if feature is enabled"""
        return WhatsAppBetaConfig.FEATURES.get(feature_name, False)
    
    @staticmethod
    def get_message_template(template_type, **kwargs):
        """Get formatted message template"""
        try:
            template = WhatsAppBetaConfig.MESSAGE_TEMPLATES[template_type]["template"]
            safe_kwargs = {
                key: WhatsAppBetaConfig.safe_display_value(value)
                for key, value in kwargs.items()
            }
            return template.format(**safe_kwargs)
        except KeyError:
            return None

    @staticmethod
    def safe_display_value(value, default="N/A"):
        """Render irregular or missing data consistently in parent messages."""
        if value is None:
            return default
        value = str(value).strip()
        return value if value else default

    @staticmethod
    def normalize_phone_number(phone, default_country_code="91"):
        """
        Normalize Indian parent/student phone values for wa.me links.
        Returns (normalized_phone, error).
        """
        raw_phone = WhatsAppBetaConfig.safe_display_value(phone, "")
        digits = re.sub(r"\D", "", raw_phone)

        if not digits:
            return "", "Missing WhatsApp number"

        if len(digits) == 10:
            digits = f"{default_country_code}{digits}"

        if len(digits) < 10 or len(digits) > 15:
            return "", "Invalid WhatsApp number"

        return digits, None

    @staticmethod
    def get_template_feature(template_type):
        """Map a message type to its feature flag."""
        return WhatsAppBetaConfig.TEMPLATE_FEATURES.get(template_type, "send_notifications")

    @staticmethod
    def validate_template_payload(template_type, payload):
        """Return missing required fields for a message type."""
        required_fields = WhatsAppBetaConfig.REQUIRED_TEMPLATE_FIELDS.get(template_type, [])
        return [
            field for field in required_fields
            if not WhatsAppBetaConfig.safe_display_value(payload.get(field), "")
        ]
