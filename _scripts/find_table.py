from django.db import connection
tables = connection.introspection.table_names()
cursor = connection.cursor()
for t in tables:
    cursor.execute(f'DESCRIBE {t}')
    cols = [c[0] for c in cursor.fetchall()]
    if any('admission' in c.lower() or 'father' in c.lower() or 'dob' in c.lower() for c in cols):
        print(f'Table: {t}, Columns: {cols}')
