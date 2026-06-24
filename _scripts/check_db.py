import os, django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'school_management.settings')
django.setup()
from django.db import connection
with connection.cursor() as cursor:
    cursor.execute("SELECT admission_number FROM student_page1 WHERE admission_number LIKE 'CMSTDM%'")
    print(cursor.fetchall())
