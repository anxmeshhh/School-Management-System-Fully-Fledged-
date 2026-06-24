import os
import django
import pandas as pd

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'school_management.settings')
django.setup()

from django.db import connection

def check_db():
    print("\n--- RAISING MELLON: BASIC OVERVIEW ---")
    query1 = """
        SELECT admission_number, name, class 
        FROM student_page1 
        WHERE class = 'RAISING MELLON'
        ORDER BY name ASC LIMIT 10;
    """
    df1 = pd.read_sql(query1, connection)
    print(df1.to_string(index=False) if not df1.empty else "No students found.")

    print("\n--- RAISING MELLON: GENDERS & DOB ---")
    query2 = """
        SELECT sp1.name, sp1.admission_number, sp2.gender, sp2.dob 
        FROM student_page1 sp1
        JOIN student_page2 sp2 ON sp1.user_id = sp2.user_id
        WHERE sp1.class = 'RAISING MELLON'
        ORDER BY sp1.name ASC LIMIT 10;
    """
    df2 = pd.read_sql(query2, connection)
    print(df2.to_string(index=False) if not df2.empty else "No students found.")

    print("\n--- RAISING MELLON: PARENT CONTACTS ---")
    query3 = """
        SELECT sp1.name, sp4.father_name, sp4.father_contact, sp4.mother_name, sp4.mother_contact
        FROM student_page1 sp1
        JOIN student_page4 sp4 ON sp1.user_id = sp4.user_id
        WHERE sp1.class = 'RAISING MELLON'
        ORDER BY sp1.name ASC LIMIT 10;
    """
    df3 = pd.read_sql(query3, connection)
    print(df3.to_string(index=False) if not df3.empty else "No students found.")

if __name__ == '__main__':
    check_db()
