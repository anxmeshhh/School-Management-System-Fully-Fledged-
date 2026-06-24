import os, django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'school_management.settings')
django.setup()
from django.db import connection
with connection.cursor() as cursor:
    cursor.execute("SHOW COLUMNS FROM student_page2 LIKE 'dob'")
    print(cursor.fetchone())
