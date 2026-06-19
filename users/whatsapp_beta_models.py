# ─── WhatsApp Beta Testing Models ────────────────────────────────────────

from django.db import models, connection
from datetime import datetime, timedelta
import json


class WhatsAppBetaTester(models.Model):
    """Track who is allowed to use WhatsApp beta features"""
    
    ROLE_CHOICES = [
        ('admin', 'Administrator'),
        ('teacher', 'Teacher'),
        ('support', 'Support Staff'),
        ('test_user', 'Test User'),
    ]
    
    user_id = models.IntegerField(unique=True)
    email = models.EmailField(max_length=255)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    
    # Beta Testing Status
    is_approved = models.BooleanField(default=False)
    approval_date = models.DateTimeField(null=True, blank=True)
    approved_by_id = models.IntegerField(null=True, blank=True)
    
    # Limits
    daily_message_limit = models.IntegerField(default=100)
    messages_sent_today = models.IntegerField(default=0)
    last_reset_date = models.DateField(auto_now=True)
    
    # Status
    is_active = models.BooleanField(default=True)
    status_reason = models.TextField(blank=True, null=True)
    
    # Tracking
    date_joined_beta = models.DateTimeField(auto_now_add=True)
    last_used = models.DateTimeField(null=True, blank=True)
    total_messages_sent = models.IntegerField(default=0)
    
    class Meta:
        db_table = 'whatsapp_beta_testers'
        indexes = [
            models.Index(fields=['user_id']),
            models.Index(fields=['is_approved']),
            models.Index(fields=['is_active']),
        ]
    
    def __str__(self):
        return f"{self.email} ({self.role})"
    
    def reset_daily_limit(self):
        """Reset daily message count"""
        today = datetime.now().date()
        if self.last_reset_date != today:
            self.messages_sent_today = 0
            self.last_reset_date = today
            self.save()
    
    def can_send_message(self):
        """Check if user can send message"""
        self.reset_daily_limit()
        return (
            self.is_approved and 
            self.is_active and 
            self.messages_sent_today < self.daily_message_limit
        )
    
    def increment_message_count(self):
        """Increment message count"""
        self.messages_sent_today += 1
        self.total_messages_sent += 1
        self.last_used = datetime.now()
        self.save()


class WhatsAppBetaUsageLog(models.Model):
    """Log all WhatsApp beta feature usage"""
    
    STATUS_CHOICES = [
        ('success', 'Success'),
        ('failed', 'Failed'),
        ('rate_limit_exceeded', 'Rate Limit Exceeded'),
        ('feature_disabled', 'Feature Disabled'),
        ('unauthorized', 'Unauthorized'),
    ]
    
    user_id = models.IntegerField()
    action_type = models.CharField(max_length=50)  # send_pdf, send_notification, etc.
    message_type = models.CharField(max_length=50, default='student_pdf')
    recipient_phone = models.CharField(max_length=20)
    recipient_name = models.CharField(max_length=255, blank=True)
    
    # Status
    status = models.CharField(max_length=20, choices=STATUS_CHOICES)
    error_message = models.TextField(blank=True, null=True)
    
    # Message details
    message_preview = models.TextField(max_length=500)
    message_length = models.IntegerField()
    
    # Tracking
    timestamp = models.DateTimeField(auto_now_add=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    
    # Metadata
    metadata = models.JSONField(default=dict, blank=True)
    
    class Meta:
        db_table = 'whatsapp_beta_usage_logs'
        indexes = [
            models.Index(fields=['user_id', 'timestamp']),
            models.Index(fields=['status']),
            models.Index(fields=['timestamp']),
        ]
        ordering = ['-timestamp']
    
    def __str__(self):
        return f"{self.user_id} - {self.action_type} ({self.status})"


class WhatsAppBetaCompliance(models.Model):
    """Track compliance and regulatory requirements"""
    
    ALERT_TYPES = [
        ('high_usage', 'High Usage Alert'),
        ('rate_limit_violation', 'Rate Limit Violation'),
        ('suspicious_activity', 'Suspicious Activity'),
        ('message_failure', 'Message Failure'),
        ('policy_violation', 'Policy Violation'),
    ]
    
    user_id = models.IntegerField()
    alert_type = models.CharField(max_length=30, choices=ALERT_TYPES)
    severity = models.CharField(max_length=10, choices=[
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('critical', 'Critical'),
    ])
    
    message = models.TextField()
    is_resolved = models.BooleanField(default=False)
    resolved_by_id = models.IntegerField(null=True, blank=True)
    resolution_notes = models.TextField(blank=True, null=True)
    
    timestamp = models.DateTimeField(auto_now_add=True)
    resolved_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        db_table = 'whatsapp_beta_compliance'
        indexes = [
            models.Index(fields=['user_id', 'timestamp']),
            models.Index(fields=['is_resolved']),
            models.Index(fields=['severity']),
        ]
        ordering = ['-timestamp']
    
    def __str__(self):
        return f"{self.alert_type} - {self.user_id} ({self.severity})"


class WhatsAppBetaMessage(models.Model):
    """Store WhatsApp messages for audit trail"""
    
    MESSAGE_STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('sent', 'Sent'),
        ('failed', 'Failed'),
        ('blocked', 'Blocked'),
    ]
    
    user_id = models.IntegerField()
    recipient_phone = models.CharField(max_length=20)
    recipient_name = models.CharField(max_length=255, blank=True)
    
    message_content = models.TextField()
    message_type = models.CharField(max_length=50)  # student_pdf, notification, etc.
    
    status = models.CharField(max_length=20, choices=MESSAGE_STATUS_CHOICES, default='pending')
    sent_at = models.DateTimeField(null=True, blank=True)
    failed_reason = models.TextField(blank=True, null=True)
    
    # For tracking
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Metadata
    template_used = models.CharField(max_length=50, blank=True)
    attachments = models.JSONField(default=list, blank=True)
    metadata = models.JSONField(default=dict, blank=True)
    
    class Meta:
        db_table = 'whatsapp_beta_messages'
        indexes = [
            models.Index(fields=['user_id', 'created_at']),
            models.Index(fields=['status']),
            models.Index(fields=['recipient_phone']),
        ]
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Message to {self.recipient_phone} ({self.status})"
