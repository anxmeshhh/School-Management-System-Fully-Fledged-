import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'school_management.settings')
django.setup()

from django.db import connection

dob_updates = {
    'CMSRM25': '2023-07-15',
    'CMSRM26': '2022-10-01',
    'CMSRM27': '2023-11-15',
    'CMSRM28': '2023-10-07',
    'CMSRM29': '2023-10-09'
}

def update_dobs():
    with connection.cursor() as cursor:
        for adm_no, dob in dob_updates.items():
            cursor.execute("""
                UPDATE student_page2 sp2
                JOIN student_page1 sp1 ON sp1.user_id = sp2.user_id
                SET sp2.dob = %s
                WHERE sp1.admission_number = %s
            """, [dob, adm_no])
        
        # Verify updates
        cursor.execute("""
            SELECT sp1.admission_number, sp1.name, sp2.dob 
            FROM student_page1 sp1
            JOIN student_page2 sp2 ON sp1.user_id = sp2.user_id
            WHERE sp1.admission_number IN ('CMSRM25', 'CMSRM26', 'CMSRM27', 'CMSRM28', 'CMSRM29')
            ORDER BY sp1.admission_number ASC;
        """)
        rows = cursor.fetchall()
        print("\n--- UPDATED DATES OF BIRTH ---")
        for row in rows:
            print(f"{row[0]} | {row[1]:<15} | {row[2]}")

if __name__ == '__main__':
    update_dobs()
