"""
Notification Service Module for the School Management System.

Provides centralized functions to create, fetch, and manage notifications
across all user roles (admin, teacher, student, parent).

Usage:
    from users.notifications import notify, notify_all_admins, notify_class_students, ...
"""

from django.db import connection, close_old_connections
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta, date
import os
import json
import tempfile
import threading

from django.conf import settings

try:
    from pywebpush import webpush, WebPushException
    PYWEBPUSH_AVAILABLE = True
except ImportError:
    PYWEBPUSH_AVAILABLE = False
    print("pywebpush is not installed. Mobile push notifications are disabled.")


VAPID_PRIVATE_KEY = """-----BEGIN PRIVATE KEY-----
MIGHAgEAMBMGByqGSM49AgEGCCqGSM49AwEHBG0wawIBAQQgCeB/jtwYZpNFG8VU
1r1AAXNlGOF5h9S9lrfJsEthp+KhRANCAASzapswE75eBiab9ZIQJvFM9RaFwtdx
+/oBLg+F7WOSaakCKBny+IO/xpuTHNpHozYMuuy08lkES6Mx4aFoEO3y
-----END PRIVATE KEY-----"""

# ─── Write VAPID key to disk ONCE at startup, not on every push ──────────────
_VAPID_KEY_PATH = None
_VAPID_KEY_LOCK = threading.Lock()

# Global thread pool for handling push notifications without blocking
PUSH_EXECUTOR = ThreadPoolExecutor(max_workers=20)

def _get_vapid_key_path():
    global _VAPID_KEY_PATH
    if _VAPID_KEY_PATH and os.path.exists(_VAPID_KEY_PATH):
        return _VAPID_KEY_PATH
    with _VAPID_KEY_LOCK:
        if _VAPID_KEY_PATH and os.path.exists(_VAPID_KEY_PATH):
            return _VAPID_KEY_PATH
        tmp = tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.pem')
        tmp.write(VAPID_PRIVATE_KEY)
        tmp.close()
        _VAPID_KEY_PATH = tmp.name
    return _VAPID_KEY_PATH


def _send_single_push(endpoint, p256dh, auth, payload):
    """Send one web push. Cleans up expired subscriptions automatically."""
    subscription_info = {
        "endpoint": endpoint,
        "keys": {"p256dh": p256dh, "auth": auth}
    }
    try:
        webpush(
            subscription_info=subscription_info,
            data=payload,
            vapid_private_key=_get_vapid_key_path(),
            vapid_claims={"sub": "mailto:admin@manavargalsms.com"}
        )
    except WebPushException as ex:
        if ex.response and ex.response.status_code in [404, 410]:
            try:
                close_old_connections()
                with connection.cursor() as cursor:
                    cursor.execute(
                        'DELETE FROM push_subscriptions WHERE endpoint = %s', [endpoint]
                    )
                    connection.commit()
            except Exception:
                pass
            finally:
                close_old_connections()
        else:
            print(f"[Web Push Error] {repr(ex)}")
    except Exception as e:
        print(f"[Web Push Error] _send_single_push: {e}")


def trigger_web_push(recipient_type, recipient_id, title, message, action_url):
    """Fire push notifications to all devices of a user. Runs in background thread pool."""
    if not PYWEBPUSH_AVAILABLE:
        return

    def _push():
        try:
            close_old_connections()
            with connection.cursor() as cursor:
                cursor.execute(
                    'SELECT endpoint, p256dh, auth FROM push_subscriptions '
                    'WHERE user_type = %s AND user_id = %s',
                    [recipient_type, recipient_id]
                )
                subscriptions = cursor.fetchall()

            if not subscriptions:
                return

            payload = json.dumps({
                "title": title,
                "message": message,
                "action_url": action_url
            })

            # Submit to pool instead of spawning and joining threads
            for endpoint, p256dh, auth in subscriptions:
                PUSH_EXECUTOR.submit(_send_single_push, endpoint, p256dh, auth, payload)

        except Exception as e:
            print(f"[Push Error] trigger_web_push: {e}")
        finally:
            close_old_connections()

    PUSH_EXECUTOR.submit(_push)


def trigger_bulk_web_push(notifications_list):
    """
    Fire push notifications for a batch of notifications.
    Uses batched DB queries to avoid N+1 and a thread pool for fast sends.
    """
    if not PYWEBPUSH_AVAILABLE or not notifications_list:
        return

    def _bulk_push():
        try:
            close_old_connections()
            from collections import defaultdict
            
            # Map (user_type, user_id) -> payload
            payload_map = {}
            for n in notifications_list:
                key = (n['recipient_type'], n['recipient_id'])
                # Use the last notification for this recipient (most recent)
                payload_map[key] = json.dumps({
                    "title": n['title'],
                    "message": n['message'],
                    "action_url": n.get('action_url')
                })
            
            # Group keys by user_type so we can batch query per user_type
            type_to_ids = defaultdict(list)
            for rtype, rid in payload_map.keys():
                type_to_ids[rtype].append(rid)

            with connection.cursor() as cursor:
                for rtype, rids in type_to_ids.items():
                    if not rids: continue
                    # Max out at 500 per query just to be safe with DB limits
                    chunk_size = 500
                    for i in range(0, len(rids), chunk_size):
                        chunk_rids = rids[i:i + chunk_size]
                        placeholders = ','.join(['%s'] * len(chunk_rids))
                        query = f"SELECT user_id, endpoint, p256dh, auth FROM push_subscriptions WHERE user_type = %s AND user_id IN ({placeholders})"
                        cursor.execute(query, [rtype] + chunk_rids)
                        
                        for row in cursor.fetchall():
                            user_id, endpoint, p256dh, auth = row
                            payload = payload_map.get((rtype, user_id))
                            if payload:
                                PUSH_EXECUTOR.submit(_send_single_push, endpoint, p256dh, auth, payload)

        except Exception as e:
            print(f"[Push Error] trigger_bulk_web_push: {e}")
        finally:
            close_old_connections()

    PUSH_EXECUTOR.submit(_bulk_push)


# ─── Core CRUD Functions ──────────────────────────────────────────────────────

def create_notification(recipient_type, recipient_id, category, title, message,
                        action_url=None, sender_type='system', sender_id=None):
    """
    Create a single notification for a specific recipient.

    Args:
        recipient_type: 'admin' | 'teacher' | 'student' | 'parent'
        recipient_id: The ID of the recipient in their respective table
        category: Notification category (leave, attendance, circular, etc.)
        title: Short title for the notification
        message: Full notification message
        action_url: URL to navigate when clicked (optional)
        sender_type: 'admin' | 'teacher' | 'student' | 'parent' | 'system'
        sender_id: ID of the sender (optional)
    """
    try:
        with connection.cursor() as cursor:
            cursor.execute("""
                INSERT INTO notifications
                (recipient_type, recipient_id, category, title, message, action_url, sender_type, sender_id)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """, [recipient_type, recipient_id, category, title, message,
                  action_url, sender_type, sender_id])
            connection.commit()

        trigger_web_push(recipient_type, recipient_id, title, message, action_url)
        return True
    except Exception as e:
        print(f"[Notification Error] create_notification: {e}")
        return False


def create_bulk_notifications(notifications_list):
    """
    Create multiple notifications in a single batch insert, then fire all pushes
    in parallel background threads.

    Args:
        notifications_list: List of dicts with keys:
            recipient_type, recipient_id, category, title, message,
            action_url (optional), sender_type (optional), sender_id (optional)
    """
    if not notifications_list:
        return

    try:
        values = []
        params = []
        for n in notifications_list:
            values.append("(%s, %s, %s, %s, %s, %s, %s, %s)")
            params.extend([
                n['recipient_type'], n['recipient_id'], n['category'],
                n['title'], n['message'], n.get('action_url'),
                n.get('sender_type', 'system'), n.get('sender_id')
            ])

        query = """
            INSERT INTO notifications
            (recipient_type, recipient_id, category, title, message, action_url, sender_type, sender_id)
            VALUES {}
        """.format(', '.join(values))

        with connection.cursor() as cursor:
            cursor.execute(query, params)
            connection.commit()

        # Fire all pushes in parallel background threads
        trigger_bulk_web_push(notifications_list)

    except Exception as e:
        print(f"[Notification Error] create_bulk_notifications: {e}")


# ─── Broadcast Helpers ─────────────────────────────────────────────────────────

def notify_all_admins(category, title, message, action_url=None,
                      sender_type='system', sender_id=None):
    """Send a notification to ALL admins."""
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT id FROM admins")
            admin_ids = [row[0] for row in cursor.fetchall()]

        notifications = [{
            'recipient_type': 'admin',
            'recipient_id': aid,
            'category': category,
            'title': title,
            'message': message,
            'action_url': action_url,
            'sender_type': sender_type,
            'sender_id': sender_id,
        } for aid in admin_ids]

        create_bulk_notifications(notifications)
    except Exception as e:
        print(f"[Notification Error] notify_all_admins: {e}")


def notify_all_teachers(category, title, message, action_url=None,
                        sender_type='system', sender_id=None):
    """Send a notification to ALL teachers."""
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT id FROM teachers")
            teacher_ids = [row[0] for row in cursor.fetchall()]

        notifications = [{
            'recipient_type': 'teacher',
            'recipient_id': tid,
            'category': category,
            'title': title,
            'message': message,
            'action_url': action_url,
            'sender_type': sender_type,
            'sender_id': sender_id,
        } for tid in teacher_ids]

        create_bulk_notifications(notifications)
    except Exception as e:
        print(f"[Notification Error] notify_all_teachers: {e}")


def notify_class_students(class_name, section, category, title, message,
                          action_url=None, sender_type='system', sender_id=None):
    """Send a notification to all students in a specific class/section."""
    try:
        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT user_id FROM student_page1 WHERE class = %s AND section = %s",
                [class_name, section]
            )
            student_ids = [row[0] for row in cursor.fetchall()]

        notifications = [{
            'recipient_type': 'student',
            'recipient_id': sid,
            'category': category,
            'title': title,
            'message': message,
            'action_url': action_url,
            'sender_type': sender_type,
            'sender_id': sender_id,
        } for sid in student_ids]

        create_bulk_notifications(notifications)
    except Exception as e:
        print(f"[Notification Error] notify_class_students: {e}")


def notify_class_parents(class_name, section, category, title, message,
                         action_url=None, sender_type='system', sender_id=None):
    """Send a notification to parents of all students in a specific class/section."""
    try:
        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT user_id FROM student_page1 WHERE class = %s AND section = %s",
                [class_name, section]
            )
            parent_ids = [row[0] for row in cursor.fetchall() if row[0]]

        notifications = [{
            'recipient_type': 'parent',
            'recipient_id': pid,
            'category': category,
            'title': title,
            'message': message,
            'action_url': action_url,
            'sender_type': sender_type,
            'sender_id': sender_id,
        } for pid in parent_ids]

        create_bulk_notifications(notifications)
    except Exception as e:
        print(f"[Notification Error] notify_class_parents: {e}")


def notify_student_and_parents(student_id, category, title, message,
                               action_url=None, sender_type='system', sender_id=None):
    """Send notification to a specific student and their parent."""
    create_bulk_notifications([
        {
            'recipient_type': 'student',
            'recipient_id': student_id,
            'category': category,
            'title': title,
            'message': message,
            'action_url': action_url,
            'sender_type': sender_type,
            'sender_id': sender_id,
        },
        {
            'recipient_type': 'parent',
            'recipient_id': student_id,
            'category': category,
            'title': title,
            'message': message,
            'action_url': action_url,
            'sender_type': sender_type,
            'sender_id': sender_id,
        }
    ])


def notify_class_teacher(class_name, section, category, title, message,
                         action_url=None, sender_type='system', sender_id=None):
    """Send notification to the class teacher of a specific class/section."""
    try:
        class_section_key = f"{class_name}-{section}"
        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT id FROM teachers WHERE class_teacher_of = %s",
                [class_section_key]
            )
            result = cursor.fetchone()
            if result:
                create_notification('teacher', result[0], category, title, message,
                                    action_url, sender_type, sender_id)
    except Exception as e:
        print(f"[Notification Error] notify_class_teacher: {e}")


# ─── Read / Fetch Functions ───────────────────────────────────────────────────

def get_unread_count(recipient_type, recipient_id):
    """Get count of unread notifications for a user."""
    try:
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT COUNT(*) FROM notifications
                WHERE recipient_type = %s AND recipient_id = %s AND is_read = 0
            """, [recipient_type, recipient_id])
            result = cursor.fetchone()
            return result[0] if result else 0
    except Exception as e:
        print(f"[Notification Error] get_unread_count: {e}")
        return 0


def get_notifications(recipient_type, recipient_id, limit=20, offset=0):
    """
    Fetch notifications for a user, newest first.
    Returns list of dicts with notification data.
    """
    try:
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT id, category, title, message, action_url, is_read, created_at
                FROM notifications
                WHERE recipient_type = %s AND recipient_id = %s
                ORDER BY created_at DESC
                LIMIT %s OFFSET %s
            """, [recipient_type, recipient_id, limit, offset])

            notifications = []
            for row in cursor.fetchall():
                notifications.append({
                    'id': row[0],
                    'category': row[1],
                    'title': row[2],
                    'message': row[3],
                    'action_url': row[4],
                    'is_read': bool(row[5]),
                    'created_at': row[6].isoformat() if row[6] else None,
                })
            return notifications
    except Exception as e:
        print(f"[Notification Error] get_notifications: {e}")
        return []


def get_grouped_notifications(recipient_type, recipient_id, limit=20):
    """
    Fetch notifications with grouping of similar unread notifications.
    Groups by (category, title) if multiple unread exist within the last 24 hours.
    Returns list of dicts, some with 'group_count' > 1 for grouped items.
    """
    try:
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT category, title, COUNT(*) as cnt,
                       MAX(id) as latest_id, MAX(created_at) as latest_time,
                       GROUP_CONCAT(id ORDER BY id DESC) as all_ids,
                       MIN(action_url) as action_url
                FROM notifications
                WHERE recipient_type = %s AND recipient_id = %s AND is_read = 0
                  AND created_at >= NOW() - INTERVAL 24 HOUR
                GROUP BY category, title
                HAVING COUNT(*) > 1
                ORDER BY latest_time DESC
            """, [recipient_type, recipient_id])

            grouped = {}
            grouped_ids = set()
            for row in cursor.fetchall():
                cat, title, cnt, latest_id, latest_time, all_ids_str, action_url = row
                ids = [int(x) for x in all_ids_str.split(',')]
                grouped_ids.update(ids)
                grouped[(cat, title)] = {
                    'id': latest_id,
                    'category': cat,
                    'title': title,
                    'message': f"{cnt} notifications",
                    'action_url': action_url,
                    'is_read': False,
                    'created_at': latest_time.isoformat() if latest_time else None,
                    'group_count': cnt,
                    'group_ids': ids,
                }

            cursor.execute("""
                SELECT id, category, title, message, action_url, is_read, created_at
                FROM notifications
                WHERE recipient_type = %s AND recipient_id = %s
                ORDER BY created_at DESC
                LIMIT %s
            """, [recipient_type, recipient_id, limit + len(grouped_ids)])

            results = []
            seen_groups = set()
            for row in cursor.fetchall():
                nid, cat, title, msg, url, is_read, created_at = row

                if nid in grouped_ids:
                    key = (cat, title)
                    if key not in seen_groups and key in grouped:
                        seen_groups.add(key)
                        results.append(grouped[key])
                    continue

                results.append({
                    'id': nid,
                    'category': cat,
                    'title': title,
                    'message': msg,
                    'action_url': url,
                    'is_read': bool(is_read),
                    'created_at': created_at.isoformat() if created_at else None,
                    'group_count': 1,
                })

        results.sort(key=lambda x: x.get('created_at', ''), reverse=True)
        return results[:limit]

    except Exception as e:
        print(f"[Notification Error] get_grouped_notifications: {e}")
        return get_notifications(recipient_type, recipient_id, limit)


def mark_as_read(notification_id, recipient_type, recipient_id):
    """Mark a single notification as read (with ownership check)."""
    try:
        with connection.cursor() as cursor:
            cursor.execute("""
                UPDATE notifications SET is_read = 1
                WHERE id = %s AND recipient_type = %s AND recipient_id = %s
            """, [notification_id, recipient_type, recipient_id])
            connection.commit()
            return cursor.rowcount > 0
    except Exception as e:
        print(f"[Notification Error] mark_as_read: {e}")
        return False


def mark_group_as_read(notification_ids, recipient_type, recipient_id):
    """Mark a group of notifications as read."""
    if not notification_ids:
        return False
    try:
        placeholders = ','.join(['%s'] * len(notification_ids))
        with connection.cursor() as cursor:
            cursor.execute(f"""
                UPDATE notifications SET is_read = 1
                WHERE id IN ({placeholders}) AND recipient_type = %s AND recipient_id = %s
            """, notification_ids + [recipient_type, recipient_id])
            connection.commit()
            return cursor.rowcount > 0
    except Exception as e:
        print(f"[Notification Error] mark_group_as_read: {e}")
        return False


def mark_all_as_read(recipient_type, recipient_id):
    """Mark all notifications as read for a user."""
    try:
        with connection.cursor() as cursor:
            cursor.execute("""
                UPDATE notifications SET is_read = 1
                WHERE recipient_type = %s AND recipient_id = %s AND is_read = 0
            """, [recipient_type, recipient_id])
            connection.commit()
            return cursor.rowcount
    except Exception as e:
        print(f"[Notification Error] mark_all_as_read: {e}")
        return 0


def cleanup_old_notifications(days=30):
    """Delete notifications older than the specified number of days."""
    try:
        with connection.cursor() as cursor:
            cursor.execute("""
                DELETE FROM notifications
                WHERE created_at < NOW() - INTERVAL %s DAY
            """, [days])
            connection.commit()
            return cursor.rowcount
    except Exception as e:
        print(f"[Notification Error] cleanup_old_notifications: {e}")
        return 0


# ─── Convenience Aliases ──────────────────────────────────────────────────────

notify = create_notification


def generate_dynamic_reminders(user_type, user_id):
    """
    Dynamically generates reminder notifications for upcoming/pending tasks.
    Runs on notifications fetch to keep alerts real-time without background cron tasks.
    """
    try:
        with connection.cursor() as cursor:

            # ── Students & Parents ────────────────────────────────────────────
            if user_type in ('student', 'parent'):
                student_user_id = user_id  # parent user_id == student user_id

                cursor.execute(
                    "SELECT class, section FROM student_page1 WHERE user_id = %s",
                    [student_user_id]
                )
                stud_info = cursor.fetchone()
                if not stud_info:
                    return

                class_name, section = stud_info
                class_id = f"{class_name}{section}" if class_name and section else class_name

                # A. Upcoming Exam Reminders (Next 3 Days)
                if class_id:
                    today_str = date.today().strftime('%Y-%m-%d')
                    three_days_later_str = (date.today() + timedelta(days=3)).strftime('%Y-%m-%d')
                    cursor.execute("""
                        SELECT id, subject, exam_date, start_time
                        FROM exams
                        WHERE class_id = %s AND exam_date BETWEEN %s AND %s
                    """, [class_id, today_str, three_days_later_str])
                    exams = cursor.fetchall()

                    for exam in exams:
                        exam_db_id, subject, exam_date, start_time = exam
                        title = f"Upcoming Exam: {subject}"
                        cursor.execute("""
                            SELECT COUNT(*) FROM notifications
                            WHERE recipient_type = %s AND recipient_id = %s
                            AND category = 'exam' AND title = %s
                            AND created_at >= NOW() - INTERVAL 1 DAY
                        """, [user_type, user_id, title])
                        if cursor.fetchone()[0] == 0:
                            cursor.execute("""
                                INSERT INTO notifications
                                (recipient_type, recipient_id, category, title, message, action_url)
                                VALUES (%s, %s, 'exam', %s, %s, %s)
                            """, [
                                user_type, user_id, title,
                                f"Reminder: Your exam for {subject} is scheduled on {exam_date} at {start_time}.",
                                '/student_timetable/'
                            ])
                            # FIX: commit each insert immediately
                            connection.commit()

                # B. Upcoming Homework Due (Next 2 Days)
                homework_dir = os.path.join(settings.MEDIA_ROOT, 'teacher_homework')
                if os.path.exists(homework_dir):
                    for filename in os.listdir(homework_dir):
                        if not (filename.endswith('.txt') and not filename.endswith('_submission.txt')):
                            continue
                        txt_path = os.path.join(homework_dir, filename)
                        try:
                            with open(txt_path, 'r', encoding='utf-8') as f:
                                lines = [line.strip() for line in f.readlines()]
                            if len(lines) < 6:
                                continue

                            hw_title   = lines[0]
                            hw_subject = lines[2]
                            hw_due_date = lines[3]
                            hw_target  = lines[4]

                            target_match = False
                            if hw_target == 'all':
                                target_match = True
                            elif hw_target == 'specific' and len(lines) >= 8:
                                if lines[6] == class_name and lines[7] == section:
                                    target_match = True

                            if not target_match or not hw_due_date:
                                continue

                            try:
                                due_dt = datetime.strptime(hw_due_date, '%Y-%m-%d').date()
                            except ValueError:
                                continue

                            if not (date.today() <= due_dt <= date.today() + timedelta(days=2)):
                                continue

                            cursor.execute("""
                                SELECT COUNT(*) FROM homework
                                WHERE user_id = %s AND title = %s
                            """, [student_user_id, hw_title])
                            if cursor.fetchone()[0] != 0:
                                continue  # Already submitted

                            title = f"Homework Pending: {hw_title}"
                            cursor.execute("""
                                SELECT COUNT(*) FROM notifications
                                WHERE recipient_type = %s AND recipient_id = %s
                                AND category = 'homework' AND title = %s
                                AND created_at >= NOW() - INTERVAL 1 DAY
                            """, [user_type, user_id, title])
                            if cursor.fetchone()[0] == 0:
                                cursor.execute("""
                                    INSERT INTO notifications
                                    (recipient_type, recipient_id, category, title, message, action_url)
                                    VALUES (%s, %s, 'homework', %s, %s, %s)
                                """, [
                                    user_type, user_id, title,
                                    f"Reminder: Homework '{hw_title}' for {hw_subject} is due on {hw_due_date}.",
                                    '/homework/'
                                ])
                                # FIX: commit each insert immediately
                                connection.commit()
                        except Exception:
                            pass

            # ── Teachers ──────────────────────────────────────────────────────
            elif user_type == 'teacher':
                cursor.execute(
                    "SELECT COUNT(*) FROM student_leave_requests WHERE status = 'Pending'"
                )
                pending_count = cursor.fetchone()[0]
                if pending_count > 0:
                    title = "Pending Leave Requests"
                    cursor.execute("""
                        SELECT COUNT(*) FROM notifications
                        WHERE recipient_type = 'teacher' AND recipient_id = %s
                        AND category = 'leave' AND title = %s
                        AND created_at >= NOW() - INTERVAL 1 DAY
                    """, [user_id, title])
                    if cursor.fetchone()[0] == 0:
                        cursor.execute("""
                            INSERT INTO notifications
                            (recipient_type, recipient_id, category, title, message, action_url)
                            VALUES ('teacher', %s, 'leave', %s, %s, '/teacher_accept_portal/')
                        """, [
                            user_id, title,
                            f"You have {pending_count} pending student leave request(s) awaiting approval."
                        ])
                        # FIX: commit immediately
                        connection.commit()

            # ── Admins ────────────────────────────────────────────────────────
            elif user_type == 'admin':
                cursor.execute(
                    "SELECT COUNT(*) FROM student_leave_requests WHERE status = 'Pending'"
                )
                pending_count = cursor.fetchone()[0]
                if pending_count > 0:
                    title = "Pending Leave Requests"
                    cursor.execute("""
                        SELECT COUNT(*) FROM notifications
                        WHERE recipient_type = 'admin' AND recipient_id = %s
                        AND category = 'leave' AND title = %s
                        AND created_at >= NOW() - INTERVAL 1 DAY
                    """, [user_id, title])
                    if cursor.fetchone()[0] == 0:
                        cursor.execute("""
                            INSERT INTO notifications
                            (recipient_type, recipient_id, category, title, message, action_url)
                            VALUES ('admin', %s, 'leave', %s, %s, '/admin_accept_portal/')
                        """, [
                            user_id, title,
                            f"There are {pending_count} pending student leave request(s) awaiting approval."
                        ])
                        # FIX: commit immediately
                        connection.commit()

    except Exception as e:
        print(f"[Dynamic Notifications Error]: {e}")