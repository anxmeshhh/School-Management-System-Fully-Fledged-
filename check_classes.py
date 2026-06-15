import pymysql

try:
    connection = pymysql.connect(
        host='localhost',
        user='root',
        password='theanimesh2005',
        database='school_db',
        cursorclass=pymysql.cursors.DictCursor
    )
    with connection.cursor() as cursor:
        cursor.execute("DESCRIBE admin_student_classes")
        print("\nadmin_student_classes schema:")
        for row in cursor.fetchall():
            print(row)
            
        cursor.execute("SELECT * FROM admin_student_classes LIMIT 10")
        print("\nCurrent classes in DB:")
        for row in cursor.fetchall():
            print(row)
            
except Exception as e:
    print("Error connecting to DB:", e)
