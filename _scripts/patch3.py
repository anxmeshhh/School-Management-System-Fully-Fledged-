import re

with open('users/views.py', 'r', encoding='utf-8') as f:
    text = f.read()

# Replace the minimalist block in preview
old_preview = r'''                # --- Normalize for Minimalist / New Excel Format ---
                df.columns = df.columns.astype(str).str.strip().str.upper()
                
                is_minimalist = 'S.NO' in df.columns and 'NAME' in df.columns and 'ADMISSION NUMBER' in df.columns
                
                if is_minimalist:
                    df\['user_id'\] = None 
                    df\['roll_number'\] = df\['S.NO'\]
                    df\['name'\] = df\['NAME'\]
                    df\['gender'\] = df\['GENDER'\] if 'GENDER' in df.columns else None
                    df\['admission_number'\] = df\['ADMISSION NUMBER'\]
                    df\['dob'\] = df\['DOB'\] if 'DOB' in df.columns else None
                    df\['mother_tongue'\] = df.get\('LINGUISTIC', df.get\('LINGUSTIC', df.get\('LINGUISTICS', df.get\('LINGUSTICS', None\)\)\)\)
                    df\['class'\] = df\['CLASS'\] if 'CLASS' in df.columns else None
                    df\['father_name'\] = df.get\('FATHER NAME', None\)
                    df\['father_contact'\] = df.get\('CONTACT', None\)
                    df\['contact'\] = df.get\('CONTACT', None\)
                    df\['mother_name'\] = df.get\('MOTHER NAME', None\)
                    df\['mother_contact'\] = df.get\('MOTHER CONTACT', df.get\('CONTAC T', df.get\('CONTACT T', None\)\)\)
                    df\['address'\] = df.get\('ADDRESS', None\)

                df.columns = df.columns.str.lower\(\)'''

new_preview = r'''                # --- Normalize for Minimalist / New Excel Format ---
                df.columns = df.columns.astype(str).str.strip().str.upper()
                
                is_minimalist = 'S.NO' in df.columns and 'NAME' in df.columns and 'ADMISSION NUMBER' in df.columns
                
                if is_minimalist:
                    rename_map = {
                        'S.NO': 'roll_number',
                        'NAME': 'name',
                        'GENDER': 'gender',
                        'ADMISSION NUMBER': 'admission_number',
                        'DOB': 'dob',
                        'CLASS': 'class',
                        'FATHER NAME': 'father_name',
                        'CONTACT': 'contact',
                        'MOTHER NAME': 'mother_name',
                        'ADDRESS': 'address'
                    }
                    df = df.rename(columns=rename_map)
                    df['user_id'] = None
                    df['father_contact'] = df.get('contact', None)
                    df['mother_tongue'] = df.get('LINGUISTIC', df.get('LINGUSTIC', df.get('LINGUISTICS', df.get('LINGUSTICS', None))))
                    df['mother_contact'] = df.get('MOTHER CONTACT', df.get('CONTAC T', df.get('CONTACT T', None)))

                df.columns = df.columns.str.lower()
                # Remove any leftover duplicated columns safely
                df = df.loc[:, ~df.columns.duplicated()]'''

text = re.sub(old_preview, new_preview, text, flags=re.DOTALL)

# Replace the minimalist block in upload
old_upload = r'''                # --- Normalize for Minimalist / New Excel Format ---
                df.columns = df.columns.astype(str).str.strip().str.upper()
                is_minimalist = 'S.NO' in df.columns and 'NAME' in df.columns and 'ADMISSION NUMBER' in df.columns
                
                if is_minimalist:
                    df\['user_id'\] = None
                    df\['roll_number'\] = df\['S.NO'\]
                    df\['name'\] = df\['NAME'\]
                    df\['gender'\] = df\['GENDER'\] if 'GENDER' in df.columns else None
                    df\['admission_number'\] = df\['ADMISSION NUMBER'\]
                    df\['dob'\] = df\['DOB'\] if 'DOB' in df.columns else None
                    df\['mother_tongue'\] = df.get\('LINGUISTIC', df.get\('LINGUSTIC', df.get\('LINGUISTICS', df.get\('LINGUSTICS', None\)\)\)\)
                    df\['class'\] = df\['CLASS'\] if 'CLASS' in df.columns else None
                    df\['father_name'\] = df.get\('FATHER NAME', None\)
                    df\['father_contact'\] = df.get\('CONTACT', None\)
                    df\['contact'\] = df.get\('CONTACT', None\)
                    df\['mother_name'\] = df.get\('MOTHER NAME', None\)
                    df\['mother_contact'\] = df.get\('MOTHER CONTACT', df.get\('CONTAC T', df.get\('CONTACT T', None\)\)\)
                    df\['address'\] = df.get\('ADDRESS', None\)
                    
                df.columns = df.columns.str.lower\(\)'''

new_upload = r'''                # --- Normalize for Minimalist / New Excel Format ---
                df.columns = df.columns.astype(str).str.strip().str.upper()
                is_minimalist = 'S.NO' in df.columns and 'NAME' in df.columns and 'ADMISSION NUMBER' in df.columns
                
                if is_minimalist:
                    rename_map = {
                        'S.NO': 'roll_number',
                        'NAME': 'name',
                        'GENDER': 'gender',
                        'ADMISSION NUMBER': 'admission_number',
                        'DOB': 'dob',
                        'CLASS': 'class',
                        'FATHER NAME': 'father_name',
                        'CONTACT': 'contact',
                        'MOTHER NAME': 'mother_name',
                        'ADDRESS': 'address'
                    }
                    df = df.rename(columns=rename_map)
                    df['user_id'] = None
                    df['father_contact'] = df.get('contact', None)
                    df['mother_tongue'] = df.get('LINGUISTIC', df.get('LINGUSTIC', df.get('LINGUISTICS', df.get('LINGUSTICS', None))))
                    df['mother_contact'] = df.get('MOTHER CONTACT', df.get('CONTAC T', df.get('CONTACT T', None)))
                    
                df.columns = df.columns.str.lower()
                # Remove any leftover duplicated columns safely
                df = df.loc[:, ~df.columns.duplicated()]'''

text = re.sub(old_upload, new_upload, text, flags=re.DOTALL)

with open('users/views.py', 'w', encoding='utf-8') as f:
    f.write(text)
print('Fixed duplicate columns issue!')
