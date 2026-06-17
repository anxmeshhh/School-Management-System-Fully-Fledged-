import pandas as pd
import uuid

def esc(val):
    if pd.isna(val): return 'NULL'
    return "'" + str(val).replace("'", "''") + "'"

df = pd.read_excel('DATABASE 26-27 (1).xlsx', sheet_name='PREKG DB 26-27')

user_id = 32000
queries = []

for index, row in df.iterrows():
    name = str(row.get('NAME', '')).strip()
    if name.lower() == 'name' or name == '' or name == 'nan' or pd.isna(row.get('NAME')): 
        continue
    
    user_id += 1
    roll = row.get('S.NO')
    roll = roll if not pd.isna(roll) else 'NULL'
    
    adm_no = row.get('ADMISSION NUMBER')
    cls = row.get('CLASS', 'RAISING MELLON')
    if pd.isna(cls): cls = 'RAISING MELLON'
    
    dob = row.get('DOB')
    mother_tongue = row.get('LINGUSTIC ')
    father_name = row.get('FATHER NAME ')
    mother_name = row.get('MOTHER NAME')
    contact = row.get('CONTACT ')
    mother_contact = row.get('CONTAC T')
    address = row.get('ADDRESS')
    
    base_username = str(name).strip()[:100]
    unique_id = str(uuid.uuid4())[:8]
    email = f"{base_username.lower().replace(' ', '.')}_{user_id}_{unique_id}@example.com"[:255]
    password = str(int(roll)) if not pd.isna(roll) and roll != 'NULL' else '123'
    
    q = f"-- Student: {name}\n"
    q += f"INSERT INTO users (id, username, email, password) VALUES ({user_id}, {esc(base_username)}, {esc(email)}, {esc(password)});\n"
    q += f"INSERT INTO student_page1 (user_id, name, admission_number, class, roll_number) VALUES ({user_id}, {esc(name)}, {esc(adm_no)}, {esc(cls)}, {roll});\n"
    q += f"INSERT INTO school_students (id, name, roll_number) VALUES ({user_id}, {esc(name)}, {roll});\n"
    
    # Check if other fields are missing
    other_fields_missing = pd.isna(dob) and pd.isna(mother_tongue) and pd.isna(father_name) and pd.isna(mother_name) and pd.isna(address)
    
    if not other_fields_missing:
        q += f"INSERT INTO student_page2 (user_id, dob, mother_tongue) VALUES ({user_id}, {esc(dob)}, {esc(mother_tongue)});\n"
        q += f"INSERT INTO student_page3 (user_id, address, contact) VALUES ({user_id}, {esc(address)}, {esc(contact)});\n"
        q += f"INSERT INTO student_page4 (user_id, father_name, mother_name, father_contact, mother_contact) VALUES ({user_id}, {esc(father_name)}, {esc(mother_name)}, {esc(contact)}, {esc(mother_contact)});\n"
    
    queries.append(q)

with open('raising_mellon_queries.txt', 'w', encoding='utf-8') as f:
    f.write('\n'.join(queries))
print(f'Generated {len(queries)} students queries.')
