# ─── WhatsApp Beta Testing Regulation System - Implementation Guide ──────

## Overview

This is a comprehensive WhatsApp beta testing regulation system that ensures:
- ✅ **Controlled Access** - Only approved users can use beta features
- ✅ **Rate Limiting** - Prevent abuse with per-role message limits
- ✅ **Usage Tracking** - Complete audit trail of all messages
- ✅ **Compliance Monitoring** - Automatic alerts for suspicious activity
- ✅ **Feature Management** - Enable/disable features easily
- ✅ **Admin Dashboard** - Manage testers and alerts

---

## Architecture

### Components

1. **whatsapp_beta_config.py** - Centralized configuration
   - Beta status and version
   - Feature flags
   - Rate limits per role
   - Message templates

2. **whatsapp_beta_regulator.py** - Regulation & control layer
   - User access validation
   - Rate limit checking
   - Compliance monitoring
   - Usage logging

3. **whatsapp_beta_views.py** - Regulated API endpoints
   - WhatsApp link generation with full checks
   - Admin panel for sending PDFs
   - Automatic compliance alerts

4. **whatsapp_beta_admin_views.py** - Admin management
   - Dashboard with statistics
   - Approve/deactivate testers
   - View detailed reports
   - Resolve compliance alerts

5. **whatsapp_beta_models.py** - Database models
   - WhatsAppBetaTester - User access management
   - WhatsAppBetaUsageLog - Message history
   - WhatsAppBetaCompliance - Alert tracking
   - WhatsAppBetaMessage - Message audit trail

---

## Installation Steps

### Step 1: Create Database Tables

Run these SQL migrations:

```sql
-- Create WhatsApp Beta Testers table
CREATE TABLE whatsapp_beta_testers (
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
);

-- Create Usage Logs table
CREATE TABLE whatsapp_beta_usage_logs (
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
);

-- Create Compliance Alerts table
CREATE TABLE whatsapp_beta_compliance (
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
);

-- Create Messages Audit Trail table
CREATE TABLE whatsapp_beta_messages (
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
);
```

### Step 2: Update URLs

Add to `users/urls.py`:

```python
from users import whatsapp_beta_views, whatsapp_beta_admin_views

urlpatterns = [
    # ... existing URLs ...
    
    # WhatsApp Beta Testing
    path("admin/whatsapp-beta/", whatsapp_beta_views.admin_send_student_pdf_regulated, 
         name="whatsapp_beta_send"),
    path("admin/whatsapp-link/", whatsapp_beta_views.generate_whatsapp_link_regulated,
         name="generate_whatsapp_link_regulated"),
    
    # Admin Management
    path("admin/whatsapp-beta-dashboard/", whatsapp_beta_admin_views.admin_whatsapp_beta_dashboard,
         name="whatsapp_beta_dashboard"),
    path("admin/whatsapp-approve-tester/", whatsapp_beta_admin_views.approve_beta_tester,
         name="approve_beta_tester"),
    path("admin/whatsapp-deactivate-tester/", whatsapp_beta_admin_views.deactivate_beta_tester,
         name="deactivate_beta_tester"),
    path("admin/whatsapp-tester-details/", whatsapp_beta_admin_views.get_beta_tester_details,
         name="get_beta_tester_details"),
    path("admin/whatsapp-compliance-alerts/", whatsapp_beta_admin_views.get_compliance_alerts,
         name="get_compliance_alerts"),
    path("admin/whatsapp-resolve-alert/", whatsapp_beta_admin_views.resolve_compliance_alert,
         name="resolve_compliance_alert"),
]
```

### Step 3: Initialize Beta Testers

Add existing admins/teachers to beta testing:

```sql
-- Add admins as beta testers
INSERT INTO whatsapp_beta_testers (user_id, email, role, is_approved, approval_date)
SELECT id, email, 'admin', 1, NOW()
FROM auth_user
WHERE is_staff = 1
ON DUPLICATE KEY UPDATE is_approved = 1;
```

### Step 4: Configure Logging

Add to `school_management/settings.py`:

```python
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'whatsapp_file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': os.path.join(BASE_DIR, 'logs', 'whatsapp_beta.log'),
            'formatter': 'verbose',
        },
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'loggers': {
        'users.whatsapp_beta_regulator': {
            'handlers': ['whatsapp_file', 'console'],
            'level': 'INFO',
            'propagate': True,
        },
        'users.whatsapp_beta_views': {
            'handlers': ['whatsapp_file', 'console'],
            'level': 'INFO',
            'propagate': True,
        },
    },
}
```

---

## Configuration

### Rate Limits (per role)

Edit in `whatsapp_beta_config.py`:

```python
RATE_LIMITS = {
    "admin": 500,      # Administrators
    "teacher": 50,     # Teachers
    "support": 200,    # Support staff
}
```

### Features

Enable/disable features:

```python
FEATURES = {
    "send_student_pdfs": True,
    "send_notifications": False,  # Enable when ready
    "bulk_messaging": False,
    "scheduled_messages": False,
}
```

### Message Templates

Customize templates in config:

```python
MESSAGE_TEMPLATES = {
    "student_pdf": {
        "subject": "Student Document from {school_name}",
        "template": "Hello {name},\n\n..."
    }
}
```

---

## Usage Flow

### 1. Request WhatsApp Link

```
POST /admin/whatsapp-link/
Body: {
    mobile: "919876543210",
    name: "John Doe",
    admission_number: "A001",
    student_id: "123"
}

Response: {
    success: true,
    whatsapp_url: "https://wa.me/919876543210?text=...",
    rate_info: {
        messages_remaining: 49,
        reset_time: "2026-06-20T00:00:00"
    }
}
```

### 2. Approval Workflow

```
1. User signs up for beta (whatsapp_beta_testers.is_approved = 0)
2. Admin reviews in dashboard
3. Admin approves user → is_approved = 1
4. User can now send messages (within rate limit)
```

### 3. Compliance Monitoring

System automatically:
- ✓ Tracks all messages
- ✓ Monitors usage patterns
- ✓ Creates alerts for violations
- ✓ Admin resolves alerts

---

## Admin Dashboard

Access: `/admin/whatsapp-beta-dashboard/`

**Features:**
- Overview statistics
- Pending approvals
- Recent alerts
- Usage trends
- Tester management
- Compliance reports

---

## Rate Limit Strategy

### Daily Reset

```
- Timer resets at midnight (00:00 UTC)
- Per-user limits tracked
- Automatic alerts if limit exceeded
```

### Example

User has limit of 50 messages/day:
- Sent 45 messages today
- 5 messages remaining until reset
- Trying to send message 46 → ERROR: Rate limit exceeded

---

## Compliance Alerts

### Automatic Triggers

1. **High Usage Alert** (HIGH)
   - >50 messages in 1 hour
   
2. **Rate Limit Violation** (MEDIUM)
   - >5 violations in 7 days

3. **Message Failure** (MEDIUM)
   - >10 failures in 24 hours

4. **Suspicious Activity** (CRITICAL)
   - Pattern anomalies detected

### Resolution

Admin can:
1. View alert details
2. Review usage history
3. Add resolution notes
4. Mark as resolved

---

## Audit Trail

All operations logged in `whatsapp_beta_usage_logs`:

```
{
    user_id: 123,
    action_type: "send_pdf",
    recipient_phone: "919876543210",
    status: "success",
    timestamp: "2026-06-19T10:30:00",
    ip_address: "192.168.1.100",
    user_agent: "Mozilla/5.0...",
    metadata: { student_id: "456" }
}
```

---

## Security Features

✓ User authentication required
✓ IP address tracking
✓ User agent logging
✓ Phone number validation
✓ Message content audit
✓ Rate limiting
✓ Access control
✓ Compliance monitoring

---

## Testing

### Manual Testing

```bash
# Test 1: Unauthorized access
curl -X POST http://localhost:8000/admin/whatsapp-link/ \
  -d "mobile=919876543210&name=Test&student_id=1"
# Expected: 401 Unauthorized

# Test 2: Rate limit
# Send 51 messages as teacher (limit=50)
# Expected: 429 Rate Limit Exceeded on 51st message

# Test 3: Feature disabled
# Disable "send_student_pdfs" in config
# Expected: 400 Feature disabled
```

---

## Support & Monitoring

### View Logs

```bash
tail -f logs/whatsapp_beta.log
```

### Database Queries

```sql
-- All messages sent today
SELECT * FROM whatsapp_beta_usage_logs
WHERE DATE(timestamp) = CURDATE()
ORDER BY timestamp DESC;

-- Pending approvals
SELECT user_id, email FROM whatsapp_beta_testers
WHERE is_approved = 0;

-- Unresolved alerts
SELECT * FROM whatsapp_beta_compliance
WHERE is_resolved = 0
ORDER BY severity DESC, timestamp DESC;

-- User statistics
SELECT 
    user_id,
    total_messages_sent,
    messages_sent_today,
    last_used
FROM whatsapp_beta_testers
WHERE is_approved = 1
ORDER BY total_messages_sent DESC;
```

---

## Troubleshooting

### Issue: "User not registered for beta testing"
**Solution:** Approve user in admin dashboard first

### Issue: "Rate limit exceeded"
**Solution:** Wait until next day (00:00 UTC) or contact admin for higher limit

### Issue: "Invalid phone number"
**Solution:** Ensure phone includes country code (e.g., +91 for India)

### Issue: "PDF generation failed"
**Solution:** Check file permissions in media/student_pdfs directory

---

## Future Enhancements

- [ ] Scheduled messages
- [ ] Message templates library
- [ ] Bulk messaging
- [ ] WhatsApp API integration (for delivery receipts)
- [ ] Analytics dashboard
- [ ] User feedback collection
- [ ] A/B testing framework

---

## Version History

**v1.0 (Current)** - Initial beta testing framework
- Core regulation system
- Rate limiting
- Compliance monitoring
- Admin dashboard
