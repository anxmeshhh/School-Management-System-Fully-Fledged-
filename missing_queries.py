import pandas as pd
import uuid

def esc(val):
    if pd.isna(val): return 'NULL'
    return "'" + str(val).replace("'", "''") + "'"

xl = pd.ExcelFile('DATABASE 26-27 (1).xlsx')
user_id = 31000
queries = []
for sheet_name in xl.sheet_names:
    df = pd.read_excel(xl, sheet_name=sheet_name)
    for index, row in df.iterrows():
        name_val = str(row.iloc[1]).strip()
        if name_val.lower() == 'name' or name_val == '' or name_val == 'nan': continue
        
        # Check if they were skipped previously
        if len(row) < 3 or pd.isna(row.iloc[1]) or pd.isna(row.iloc[2]):
            user_id += 1
            roll = row.iloc[0] if not pd.isna(row.iloc[0]) else 'NULL'
            name = row.iloc[1]
            adm_no = row.iloc[2] if len(row) > 2 else None
            cls = row.iloc[5] if len(row) > 5 else None
            
            # Use sheet name to deduce the melon type (class) if cls is missing or NaN
            if pd.isna(cls):
                if 'PREKG' in sheet_name:
                    cls = 'MINI MELLON'
                elif 'LKG' in sheet_name:
                    cls = 'JUNIOR MELLON'
                elif 'UKG' in sheet_name:
                    cls = 'MASTER MELLON'
                elif 'PLAY GRP' in sheet_name:
                    cls = 'TODDLER MELLON'
            
            base_username = str(name).strip()[:100]
            unique_id = str(uuid.uuid4())[:8]
            email = f"{base_username.lower().replace(' ', '.')}_{user_id}_{unique_id}@example.com"[:255]
            password = str(int(roll)) if not pd.isna(roll) and roll != 'NULL' else '123'
            
            q = f"INSERT INTO users (id, username, email, password) VALUES ({user_id}, {esc(base_username)}, {esc(email)}, {esc(password)});\n"
            q += f"INSERT INTO student_page1 (user_id, name, admission_number, class, roll_number) VALUES ({user_id}, {esc(name)}, {esc(adm_no)}, {esc(cls)}, {roll});\n"
            q += f"INSERT INTO school_students (id, name, roll_number) VALUES ({user_id}, {esc(name)}, {roll});\n"
            queries.append(q)

print('\n'.join(queries))
