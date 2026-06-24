import sqlite3

def push_data():
    try:
        with open('excel_sql_commands.txt', 'r', encoding='utf-8') as f:
            sql_script = f.read()

        conn = sqlite3.connect('db.sqlite3')
        conn.executescript(sql_script)
        conn.commit()
        print("Data successfully pushed into the local database (db.sqlite3)!")
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        if 'conn' in locals():
            conn.close()

if __name__ == '__main__':
    push_data()
