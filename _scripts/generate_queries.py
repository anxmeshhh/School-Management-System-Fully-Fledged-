import pandas as pd
import uuid

def esc(val):
    if pd.isna(val):
        return 'NULL'
    if isinstance(val, (int, float)):
        return str(int(val))
    return "'" + str(val).replace("'", "''") + "'"

df = pd.read_excel('DATABASE 26-27.xlsx')

user_id = 40000

for index, row in df.iterrows():
    if len(row) < 3 or pd.isna(row.iloc[1]) or pd.isna(row.iloc[3]):
        continue
    user_id += 1
    
    roll = row.iloc[0] # S.NO
    name = row.iloc[1] # NAME
    gender = row.iloc[2] # GENDER
    adm_no = row.iloc[3] # ADMISSION NUMBER
    
    dob = row.iloc[4] # DOB
    if isinstance(dob, pd.Timestamp):
        dob = dob.strftime('%d/%m/%Y')
    elif pd.isna(dob):
        dob = None
        
    lang = row.iloc[5] # LINGUSTIC
    cls = row.iloc[6] # CLASS
    fname = row.iloc[7] # FATHER NAME
    contact = row.iloc[8] # CONTACT
    mname = row.iloc[9] # MOTHER NAME
    mcontact = row.iloc[10] # CONTAC T
    address = row.iloc[11] # ADDRESS

    base_username = str(name).strip()[:100]
    unique_id = str(uuid.uuid4())[:8]
    email = f"{base_username.lower().replace(' ', '.')}_{user_id}_{unique_id}@example.com"[:255]
    password = str(int(roll)) if not pd.isna(roll) else '123'

    print(f"-- Inserting user: {name}")
    print(f"INSERT IGNORE INTO users (id, username, email, password) VALUES ({user_id}, {esc(base_username)}, {esc(email)}, {esc(password)});")
    print(f"INSERT IGNORE INTO student_page1 (user_id, name, admission_number, class, roll_number) VALUES ({user_id}, {esc(name)}, {esc(adm_no)}, {esc(cls)}, {esc(roll)});")
    
    dob_sql = f"STR_TO_DATE({esc(dob)}, '%d/%m/%Y')" if dob else "NULL"
    
    print(f"INSERT IGNORE INTO student_page2 (user_id, dob, mother_tongue, gender) VALUES ({user_id}, {dob_sql}, {esc(lang)}, {esc(gender)});")
    print(f"INSERT IGNORE INTO student_page3 (user_id, address, contact) VALUES ({user_id}, {esc(address)}, {esc(contact)});")
    print(f"INSERT IGNORE INTO student_page4 (user_id, father_name, mother_name, father_contact, mother_contact) VALUES ({user_id}, {esc(fname)}, {esc(mname)}, {esc(contact)}, {esc(mcontact)});")
    print(f"INSERT IGNORE INTO school_students (id, name, roll_number) VALUES ({user_id}, {esc(name)}, {esc(roll)});")
    print()
