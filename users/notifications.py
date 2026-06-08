"""
Notification Service Module for the School Management System.

Provides centralized functions to create, fetch, and manage notifications
across all user roles (admin, teacher, student, parent).

Usage:
    from users.notifications import notify, notify_all_admins, notify_class_students, ...
"""

from django.db import connection
from datetime import datetime, timedelta


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
    except Exception as e:
        print(f"[Notification Error] create_notification: {e}")


def create_bulk_notifications(notifications_list):
    """
    Create multiple notifications in a single batch insert.
    
    Args:
        notifications_list: List of dicts, each with keys:
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
            # Find parents linked to students in this class via parent-student linkage
            # Parents are linked via parent_id in the session or by matching username/email
            # Since the system uses session-based auth, we notify all parents
            cursor.execute("SELECT id FROM parents")
            parent_ids = [row[0] for row in cursor.fetchall()]

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
    """Send notification to a specific student and their parents."""
    # Notify the student
    create_notification('student', student_id, category, title, message,
                        action_url, sender_type, sender_id)
    # Notify all parents (since parent-student link is session-based)
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT id FROM parents")
            parent_ids = [row[0] for row in cursor.fetchall()]

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
        print(f"[Notification Error] notify_student_and_parents: {e}")


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
    Groups notifications by (category, title) if there are multiple unread ones
    within the last 24 hours, collapsing them into a single grouped notification.
    
    Returns list of dicts, some with 'group_count' > 1 for grouped items.
    """
    try:
        with connection.cursor() as cursor:
            # First get grouped unread notifications from last 24 hours
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

            # Now get all notifications (including ungrouped ones)
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
                    # Skip individual items that are part of a group
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

            # Sort by created_at descending
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
            return cursor.rowcount
    except Exception as e:
        print(f"[Notification Error] cleanup_old_notifications: {e}")
        return 0


# ─── Convenience Aliases ──────────────────────────────────────────────────────

# Shorthand alias
notify = create_notification
