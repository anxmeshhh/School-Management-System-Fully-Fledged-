import uuid

data = [
    (10001, 'ABDUL AZEEZ ZAYYAN', 'CMSTDM01', '2023-10-13', 'HINDI', 'TODDLER MELLON', 'MOHAMED ZAID', '9840452376', 'NAILA FARHEEN', '9940688593', '56/55, IBRAHIM 3RD LANE NORTH BEACH ROYAPURAM', 1),
    (10002, 'FATHIMAH ZUHURIAH', 'CMSTDM02', '2023-10-13', 'HINDI', 'TODDLER MELLON', 'MOHAMED ZAID', '9840452376', 'NAILA FARHEEN', '9940688593', '56/55, IBRAHIM 3RD LANE NORTH BEACH ROYAPURAM', 2),
    (10003, 'NEKHIL RANGESH', 'CMSTDM03', '2024-07-17', 'TAMIL', 'TODDLER MELLON', 'RANGESH', '9094544924', 'PAVITRA', '9791199752', '129/4 RAMASWAMY STREET MANNADY CHENNAI 01', 3),
    (10004, 'PRISHA JAIN.J', 'CMSTDM04', '2024-03-26', 'HINDI', 'TODDLER MELLON', 'P.JITHENDAR KUMAR', '9003180550', 'PRIYANKA', '8939476324', 'NO 483, 1ST FLOOR , MINT STREET, SOWCARPET CHENNAI - 01', 4),
    (10005, 'SANVI MALI', 'CMSTDM05', '2024-02-11', 'HINDI', 'TODDLER MELLON', 'ESWAR.H.SOLANKI', '9566070523', 'KAVITHA KUMARI', '6369049986', 'NO 17/9 FIRST NARAYANA STREET, SEVENWELLS CHENNAI 01', 5),
    (10006, 'YUVASHREE', 'CMSTDM06', None, None, None, None, None, None, None, None, 6)
]

def esc(val):
    if val is None:
        return 'NULL'
    if isinstance(val, int):
        return str(val)
    return "'" + str(val).replace("'", "''") + "'"

with open("sql_commands.txt", "w") as f:
    for row in data:
        user_id = row[0]
        name = row[1] if row[1] is not None else ''
        adm_no = row[2] if row[2] is not None else ''
        dob = row[3] if row[3] else None
        lang = row[4] if row[4] is not None else ''
        cls = row[5] if row[5] is not None else ''
        fname = row[6] if row[6] is not None else ''
        contact = row[7] if row[7] is not None else ''
        mname = row[8] if row[8] is not None else ''
        mcontact = row[9] if row[9] is not None else ''
        address = row[10] if row[10] is not None else ''
        roll = row[11]
        
        base_username = str(name)[:100]
        unique_id = str(uuid.uuid4())[:8]
        email = f"{base_username.lower().replace(' ', '.')}_{user_id}_{unique_id}@example.com"[:255]
        password = str(roll)[:255]
        username = base_username

        f.write(f"DELETE FROM users WHERE id = {user_id};\n")
        f.write(f"DELETE FROM student_page1 WHERE user_id = {user_id};\n")
        f.write(f"DELETE FROM student_page2 WHERE user_id = {user_id};\n")
        f.write(f"DELETE FROM student_page3 WHERE user_id = {user_id};\n")
        f.write(f"DELETE FROM student_page4 WHERE user_id = {user_id};\n")
        f.write(f"DELETE FROM school_students WHERE id = {user_id};\n")
        
        f.write(f"INSERT INTO users (id, username, email, password) VALUES ({user_id}, {esc(username)}, {esc(email)}, {esc(password)});\n")
        f.write(f"INSERT INTO student_page1 (user_id, name, admission_number, class, roll_number) VALUES ({user_id}, {esc(name)}, {esc(adm_no)}, {esc(cls)}, {roll});\n")
        f.write(f"INSERT INTO student_page2 (user_id, dob, mother_tongue) VALUES ({user_id}, {esc(dob)}, {esc(lang)});\n")
        f.write(f"INSERT INTO student_page3 (user_id, address, contact) VALUES ({user_id}, {esc(address)}, {esc(contact)});\n")
        f.write(f"INSERT INTO student_page4 (user_id, father_name, mother_name, father_contact, mother_contact) VALUES ({user_id}, {esc(fname)}, {esc(mname)}, {esc(contact)}, {esc(mcontact)});\n")
        f.write(f"INSERT INTO school_students (id, name, roll_number) VALUES ({user_id}, {esc(name)}, {roll});\n")
        f.write("\n")
