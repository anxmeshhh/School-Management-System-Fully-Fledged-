import pandas as pd
import uuid

def esc(val):
    if pd.isna(val):
        return 'NULL'
    if isinstance(val, (int, float)):
        return str(int(val))
    return "'" + str(val).replace("'", "''") + "'"

def process_excel():
    xl = pd.ExcelFile('DATABASE 26-27 (1).xlsx')
    
    with open("excel_sql_commands.txt", "w", encoding='utf-8') as f:
        user_id = 30000
        for sheet_name in xl.sheet_names:
            df = pd.read_excel(xl, sheet_name=sheet_name)
            # Find the header row if it's not the first one. Let's assume standard first row is header.
            # We want to skip empty rows.
            for index, row in df.iterrows():
                # Assume standard format based on columns
                # 0: S.NO, 1: NAME, 2: ADMISSION NUMBER, 3: DOB, 4: LINGUISTIC, 5: CLASS
                # 6: FATHER NAME, 7: CONTACT, 8: MOTHER NAME, 9: CONTACT, 10: ADDRESS
                
                if len(row) < 3 or pd.isna(row.iloc[1]) or pd.isna(row.iloc[2]):
                    continue
                    
                name_val = str(row.iloc[1]).strip()
                if name_val.lower() == 'name' or name_val == '':
                    continue # Skip header or empty
                    
                user_id += 1
                try:
                    roll = row.iloc[0] # S.NO
                except IndexError:
                    roll = None
                    
                name = row.iloc[1]
                adm_no = row.iloc[2]
                
                try:
                    dob = row.iloc[3]
                    if isinstance(dob, pd.Timestamp):
                        dob = dob.strftime('%Y-%m-%d')
                    elif pd.isna(dob):
                        dob = None
                except IndexError:
                    dob = None
                    
                try:
                    lang = row.iloc[4]
                except IndexError:
                    lang = None
                    
                try:
                    cls = row.iloc[5]
                except IndexError:
                    cls = None
                    
                try:
                    fname = row.iloc[6]
                except IndexError:
                    fname = None
                    
                try:
                    contact = row.iloc[7]
                except IndexError:
                    contact = None
                    
                try:
                    mname = row.iloc[8]
                except IndexError:
                    mname = None
                    
                try:
                    mcontact = row.iloc[9]
                except IndexError:
                    mcontact = None
                    
                try:
                    address = row.iloc[10]
                except IndexError:
                    address = None

                base_username = str(name).strip()[:100]
                unique_id = str(uuid.uuid4())[:8]
                email = f"{base_username.lower().replace(' ', '.')}_{user_id}_{unique_id}@example.com"[:255]
                password = str(int(roll)) if not pd.isna(roll) else '123'
                username = base_username

                f.write(f"INSERT INTO users (id, username, email, password) VALUES ({user_id}, {esc(username)}, {esc(email)}, {esc(password)});\n")
                f.write(f"INSERT INTO student_page1 (user_id, name, admission_number, class, roll_number) VALUES ({user_id}, {esc(name)}, {esc(adm_no)}, {esc(cls)}, {esc(roll)});\n")
                f.write(f"INSERT INTO student_page2 (user_id, dob, mother_tongue) VALUES ({user_id}, {esc(dob)}, {esc(lang)});\n")
                f.write(f"INSERT INTO student_page3 (user_id, address, contact) VALUES ({user_id}, {esc(address)}, {esc(contact)});\n")
                f.write(f"INSERT INTO student_page4 (user_id, father_name, mother_name, father_contact, mother_contact) VALUES ({user_id}, {esc(fname)}, {esc(mname)}, {esc(contact)}, {esc(mcontact)});\n")
                f.write(f"INSERT INTO school_students (id, name, roll_number) VALUES ({user_id}, {esc(name)}, {esc(roll)});\n")
                f.write("\n")
            
    print("Queries successfully written to excel_sql_commands.txt")

if __name__ == "__main__":
    process_excel()
