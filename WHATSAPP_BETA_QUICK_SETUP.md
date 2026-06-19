# ─── WhatsApp Beta Testing - Quick Setup Checklist ──────────────────────

## 📋 Pre-Implementation

- [ ] Backup database
- [ ] Review architecture in WHATSAPP_BETA_IMPLEMENTATION.md
- [ ] Ensure logging directory exists: `mkdir logs`

---

## 🔧 Implementation Steps

### Phase 1: Database Setup (⏱️ 5 minutes)

- [ ] Copy all SQL from WHATSAPP_BETA_IMPLEMENTATION.md > Installation Steps > Step 1
- [ ] Run migrations in MySQL/MariaDB
- [ ] Verify tables created: `SHOW TABLES LIKE 'whatsapp%'`
- [ ] Initialize admins:
  ```sql
  INSERT INTO whatsapp_beta_testers (user_id, email, role, is_approved, approval_date)
  SELECT id, email, 'admin', 1, NOW()
  FROM auth_user
  WHERE is_staff = 1
  ON DUPLICATE KEY UPDATE is_approved = 1;
  ```

### Phase 2: Python Imports (⏱️ 2 minutes)

- [ ] Copy 5 Python files to `users/`:
  1. `whatsapp_beta_config.py`
  2. `whatsapp_beta_models.py` 
  3. `whatsapp_beta_regulator.py`
  4. `whatsapp_beta_views.py`
  5. `whatsapp_beta_admin_views.py`

- [ ] Copy documentation:
  1. `WHATSAPP_BETA_IMPLEMENTATION.md`
  2. `WHATSAPP_BETA_QUICK_SETUP.md` (this file)

### Phase 3: URL Configuration (⏱️ 3 minutes)

- [ ] Open `users/urls.py`
- [ ] Add imports at top:
  ```python
  from users import whatsapp_beta_views, whatsapp_beta_admin_views
  ```

- [ ] Add URL patterns (from WHATSAPP_BETA_IMPLEMENTATION.md > Installation Steps > Step 2)

### Phase 4: Settings Configuration (⏱️ 3 minutes)

- [ ] Open `school_management/settings.py`
- [ ] Add logging config (from WHATSAPP_BETA_IMPLEMENTATION.md > Installation Steps > Step 4)
- [ ] Ensure `MEDIA_ROOT` is set correctly
- [ ] Create logs directory: `os.makedirs(os.path.join(BASE_DIR, 'logs'), exist_ok=True)`

### Phase 5: Configuration Tuning (⏱️ 2 minutes)

- [ ] Open `users/whatsapp_beta_config.py`
- [ ] Customize:
  - [ ] `BETA_VERSION` - Set your version
  - [ ] `RATE_LIMITS` - Adjust per role
  - [ ] `FEATURES` - Enable/disable features
  - [ ] `MESSAGE_TEMPLATES` - Customize messages
  - [ ] `BETA_ENABLED` - Set to True to enable

### Phase 6: Templates (⏱️ 10 minutes)

- [ ] Create `users/templates/users/whatsapp_beta_admin.html`
  - Dashboard with statistics
  - Pending approvals list
  - Recent alerts
  - User management

- [ ] Update `users/templates/users/send_pdf_whatsapp.html`
  - Show rate limit info
  - Display messages remaining
  - Add beta version badge

### Phase 7: Testing (⏱️ 5 minutes)

- [ ] Test unauthorized access
  ```bash
  curl -X POST http://localhost:8000/admin/whatsapp-link/ \
    -d "mobile=91..." 
  # Should return 401
  ```

- [ ] Test with approved user
  - Login as admin
  - Access `/admin/whatsapp-beta/`
  - Try generating WhatsApp link
  - Check database for log entry

- [ ] Test rate limit
  - Send 50 messages as teacher
  - 51st should fail with 429

- [ ] Test admin dashboard
  - Access `/admin/whatsapp-beta-dashboard/`
  - Check statistics

### Phase 8: Monitoring (⏱️ 5 minutes)

- [ ] Set up log rotation in `/logs/whatsapp_beta.log`
- [ ] Create cron job to check alerts:
  ```bash
  # Check every hour
  0 * * * * python manage.py shell -c "from users.whatsapp_beta_regulator import WhatsAppBetaRegulator; WhatsAppBetaRegulator.check_compliance_alerts(1)"
  ```

---

## 🧪 Testing Scenarios

### Test 1: New User Cannot Access
```
1. Create test user (non-staff)
2. Try to access /admin/whatsapp-beta/
✓ Should show "Not registered for beta testing"
```

### Test 2: Approval Flow
```
1. Create test user
2. Add to whatsapp_beta_testers (is_approved=0)
3. Admin approves in dashboard
✓ User can now send messages
```

### Test 3: Rate Limit
```
1. Set teacher rate limit to 5 (temporarily)
2. Try to send 6 messages
✓ 6th message fails with rate limit error
```

### Test 4: Compliance Alert
```
1. Send 51 messages in 1 hour
✓ High usage alert created
✓ Appears in admin dashboard
```

### Test 5: Feature Toggle
```
1. Set FEATURES["send_student_pdfs"] = False
2. Try to send message
✓ Should fail with "Feature not enabled"
```

---

## 📊 Monitoring & Maintenance

### Daily Checks
```bash
# View today's usage
mysql> SELECT DATE(timestamp), COUNT(*), SUM(CASE WHEN status='success' THEN 1 ELSE 0 END)
       FROM whatsapp_beta_usage_logs
       WHERE DATE(timestamp) = CURDATE()
       GROUP BY DATE(timestamp);

# Check for alerts
mysql> SELECT * FROM whatsapp_beta_compliance WHERE is_resolved = 0;
```

### Weekly Maintenance
```bash
# Deactivate suspicious users
python manage.py shell
>>> from users.whatsapp_beta_regulator import WhatsAppBetaRegulator
>>> WhatsAppBetaRegulator.deactivate_beta_tester(user_id, "Suspicious activity")

# Generate report
mysql> SELECT user_id, COUNT(*) as messages, COUNT(DISTINCT recipient_phone) as recipients
       FROM whatsapp_beta_usage_logs
       WHERE timestamp >= DATE_SUB(NOW(), INTERVAL 7 DAY)
       GROUP BY user_id;
```

### Monthly Review
- [ ] Review compliance alerts
- [ ] Analyze usage patterns
- [ ] Update rate limits if needed
- [ ] Archive old logs

---

## 🔒 Security Checklist

- [ ] All endpoints check `is_authenticated`
- [ ] Admin endpoints check `is_staff`
- [ ] Phone numbers validated
- [ ] IP addresses logged
- [ ] User agents logged
- [ ] All SQL uses parameterized queries
- [ ] CSRF tokens required for POST
- [ ] Rate limits enforced
- [ ] Compliance alerts auto-created

---

## 🐛 Troubleshooting

| Issue | Solution |
|-------|----------|
| Tables not found | Run SQL migrations again, verify database |
| Module not found | Check file names and locations |
| 404 on routes | Verify urls.py has all paths |
| Permission denied | Ensure user is_staff for admin views |
| PDF not generating | Check media/student_pdfs directory permissions |
| No logs created | Verify logs directory exists and is writable |

---

## 📱 API Reference

### Generate WhatsApp Link

**Endpoint:** `POST /admin/whatsapp-link/`

**Request:**
```json
{
  "mobile": "919876543210",
  "name": "Student Name",
  "admission_number": "A001",
  "student_id": "123"
}
```

**Success Response (200):**
```json
{
  "success": true,
  "whatsapp_url": "https://wa.me/919876543210?text=...",
  "rate_info": {
    "messages_remaining": 49,
    "reset_time": "2026-06-20T00:00:00"
  }
}
```

**Error Response (429 - Rate Limited):**
```json
{
  "error": "Rate limit exceeded. Resets at 2026-06-20T00:00:00",
  "rate_info": {
    "messages_remaining": 0,
    "reset_time": "2026-06-20T00:00:00"
  }
}
```

---

## 🎯 Success Criteria

- ✓ Database tables created and populated
- ✓ URLs routing correctly
- ✓ Rate limiting working (test with 50+ messages)
- ✓ Compliance alerts triggering
- ✓ Admin dashboard loading statistics
- ✓ Logs appearing in whatsapp_beta.log
- ✓ Unauthorized users blocked
- ✓ Approved users can send messages

---

## 📞 Support

For issues:
1. Check logs: `tail -f logs/whatsapp_beta.log`
2. Review database: Query whatsapp_beta_* tables
3. Test endpoints individually
4. Check Django debug toolbar

---

**Total Implementation Time: ~40 minutes**
