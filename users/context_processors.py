"""
Context processors for the users app.
Injects notification-related context into all templates.
"""


def notification_context(request):
    """
    Inject the current user's type and ID into every template context.
    This allows the notification JS client to know who to fetch notifications for.
    """
    user_type = None
    user_id = None

    if request.session.get('admin_id'):
        user_type = 'admin'
        user_id = request.session['admin_id']
    elif request.session.get('teacher_id'):
        user_type = 'teacher'
        user_id = request.session['teacher_id']
    elif request.session.get('parent_id'):
        user_type = 'parent'
        user_id = request.session['parent_id']
    elif request.session.get('user_id'):
        user_type = 'student'
        user_id = request.session['user_id']

    return {
        'notification_user_type': user_type,
        'notification_user_id': user_id,
    }
