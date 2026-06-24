import re
import os

with open('users/views.py', 'r', encoding='utf-8') as f:
    text = f.read()

# Update 'preview' section expected_columns check
new_preview = r'''                # --- Normalize for Minimalist / New Excel Format ---
                df.columns = df.columns.astype(str).str.strip().str.upper()
                
                is_minimalist = 'S.NO' in df.columns and 'NAME' in df.columns and 'ADMISSION NUMBER' in df.columns
                
                if is_minimalist:
                    df['user_id'] = None 
                    df['roll_number'] = df['S.NO']
                    df['name'] = df['NAME']
                    df['gender'] = df['GENDER'] if 'GENDER' in df.columns else None
                    df['admission_number'] = df['ADMISSION NUMBER']
                    df['dob'] = df['DOB'] if 'DOB' in df.columns else None
                    df['mother_tongue'] = df.get('LINGUISTIC', df.get('LINGUSTIC', df.get('LINGUISTICS', df.get('LINGUSTICS', None))))
                    df['class'] = df['CLASS'] if 'CLASS' in df.columns else None
                    df['father_name'] = df.get('FATHER NAME', None)
                    df['father_contact'] = df.get('CONTACT', None)
                    df['contact'] = df.get('CONTACT', None)
                    df['mother_name'] = df.get('MOTHER NAME', None)
                    df['mother_contact'] = df.get('MOTHER CONTACT', df.get('CONTAC T', df.get('CONTACT T', None)))
                    df['address'] = df.get('ADDRESS', None)

                df.columns = df.columns.str.lower()
                expected_columns = [
                    'user_id', 'name', 'admission_number', 'class', 'section', 'roll_number', 'emis',
                    'gender', 'community', 'tamil_name', 'dob', 'nationality', 'blood_group',
                    'mother_tongue', 'caste', 'religion', 'place_of_birth', 'aadhaar',
                    'disability', 'id_mark1', 'id_mark2', 'current_class', 'admission_class',
                    'admission_year', 'admission_date', 'email', 'address', 'contact',
                    'alt_contact', 'country', 'state', 'city', 'pincode', 'status', 'house',
                    'teacher_ward', 'rte', 'sports_quota', 'prev_school', 'prev_board',
                    'father_name', 'father_name_tamil', 'mother_name', 'mother_name_tamil',
                    'father_contact', 'mother_contact', 'father_email', 'mother_email',
                    'father_qualification', 'mother_qualification', 'father_occupation',
                    'mother_occupation', 'father_income', 'mother_income', 'guardian_name',
                    'guardian_contact', 'guardian_email', 'child_living', 'rights_on_child',
                    'med_blood_group', 'diseases', 'allergies', 'medicines', 'hospital', 'doctor'
                ]
                
                if is_minimalist:
                    for col in expected_columns:
                        if col not in df.columns:
                            df[col] = None

                missing_columns = [col for col in expected_columns if col not in df.columns]
                if missing_columns:
                    messages.error(request, f'Missing columns in Excel file: {", ".join(missing_columns)}')
                    fs.delete(filename)
                    return redirect('bulk_upload')

                df = df.replace([pd.NA, np.nan, None], None)

                if not is_minimalist:
                    if df['user_id'].isna().any():
                        messages.error(request, 'The user_id column contains null or missing values.')
                        fs.delete(filename)
                        return redirect('bulk_upload')

                    try:
                        df['user_id'] = df['user_id'].astype(int)
                    except (ValueError, TypeError):
                        messages.error(request, 'Invalid data in user_id column. All values must be integers.')
                        fs.delete(filename)
                        return redirect('bulk_upload')

                    if df['user_id'].duplicated().any():
                        messages.error(request, 'The user_id column contains duplicate values.')
                        fs.delete(filename)
                        return redirect('bulk_upload')'''

old_preview = r'''                expected_columns = \[
                    'user_id', 'name', 'admission_number', 'class', 'section', 'roll_number', 'emis',
                    'gender', 'community', 'tamil_name', 'dob', 'nationality', 'blood_group',
                    'mother_tongue', 'caste', 'religion', 'place_of_birth', 'aadhaar',
                    'disability', 'id_mark1', 'id_mark2', 'current_class', 'admission_class',
                    'admission_year', 'admission_date', 'email', 'address', 'contact',
                    'alt_contact', 'country', 'state', 'city', 'pincode', 'status', 'house',
                    'teacher_ward', 'rte', 'sports_quota', 'prev_school', 'prev_board',
                    'father_name', 'father_name_tamil', 'mother_name', 'mother_name_tamil',
                    'father_contact', 'mother_contact', 'father_email', 'mother_email',
                    'father_qualification', 'mother_qualification', 'father_occupation',
                    'mother_occupation', 'father_income', 'mother_income', 'guardian_name',
                    'guardian_contact', 'guardian_email', 'child_living', 'rights_on_child',
                    'med_blood_group', 'diseases', 'allergies', 'medicines', 'hospital', 'doctor'
                \]

                missing_columns = \[col for col in expected_columns if col not in df\.columns\]
                if missing_columns:
                    messages\.error\(request, f'Missing columns in Excel file: \{{", "\.join\(missing_columns\)\}\}'\)
                    fs\.delete\(filename\)
                    return redirect\('bulk_upload'\)

                # Convert NaN, pd\.NA, and None to None \(MySQL NULL\)
                df = df\.replace\(\[pd\.NA, np\.nan, None\], None\)

                # Validate user_id
                if df\['user_id'\]\.isna\(\)\.any\(\):
                    messages\.error\(request, 'The user_id column contains null or missing values\.'\)
                    fs\.delete\(filename\)
                    return redirect\('bulk_upload'\)

                try:
                    df\['user_id'\] = df\['user_id'\]\.astype\(int\)
                except \(ValueError, TypeError\):
                    messages\.error\(request, 'Invalid data in user_id column\. All values must be integers\.'\)
                    fs\.delete\(filename\)
                    return redirect\('bulk_upload'\)

                if df\['user_id'\]\.duplicated\(\)\.any\(\):
                    messages\.error\(request, 'The user_id column contains duplicate values\.'\)
                    fs\.delete\(filename\)
                    return redirect\('bulk_upload'\)'''

text = re.sub(old_preview, new_preview, text, flags=re.DOTALL)


# Update the 'upload' section similarly
new_upload = r'''                # --- Normalize for Minimalist / New Excel Format ---
                df.columns = df.columns.astype(str).str.strip().str.upper()
                is_minimalist = 'S.NO' in df.columns and 'NAME' in df.columns and 'ADMISSION NUMBER' in df.columns
                
                if is_minimalist:
                    df['user_id'] = None
                    df['roll_number'] = df['S.NO']
                    df['name'] = df['NAME']
                    df['gender'] = df['GENDER'] if 'GENDER' in df.columns else None
                    df['admission_number'] = df['ADMISSION NUMBER']
                    df['dob'] = df['DOB'] if 'DOB' in df.columns else None
                    df['mother_tongue'] = df.get('LINGUISTIC', df.get('LINGUSTIC', df.get('LINGUISTICS', df.get('LINGUSTICS', None))))
                    df['class'] = df['CLASS'] if 'CLASS' in df.columns else None
                    df['father_name'] = df.get('FATHER NAME', None)
                    df['father_contact'] = df.get('CONTACT', None)
                    df['contact'] = df.get('CONTACT', None)
                    df['mother_name'] = df.get('MOTHER NAME', None)
                    df['mother_contact'] = df.get('MOTHER CONTACT', df.get('CONTAC T', df.get('CONTACT T', None)))
                    df['address'] = df.get('ADDRESS', None)
                    
                df.columns = df.columns.str.lower()
                
                # Convert NaN, pd.NA, and None to None (MySQL NULL)
                df = df.replace([pd.NA, np.nan, None], None)

                if not is_minimalist:
                    # Validate user_id
                    if df['user_id'].isna().any():
                        messages.error(request, 'The user_id column contains null or missing values.')
                        fs.delete(filename)
                        return redirect('bulk_upload')

                    try:
                        df['user_id'] = df['user_id'].astype(int)
                    except (ValueError, TypeError):
                        messages.error(request, 'Invalid data in user_id column. All values must be integers.')
                        fs.delete(filename)
                        return redirect('bulk_upload')

                    if df['user_id'].duplicated().any():
                        messages.error(request, 'The user_id column contains duplicate values.')
                        fs.delete(filename)
                        return redirect('bulk_upload')'''

old_upload = r'''                # Convert NaN, pd\.NA, and None to None \(MySQL NULL\)
                df = df\.replace\(\[pd\.NA, np\.nan, None\], None\)

                # Validate user_id
                if df\['user_id'\]\.isna\(\)\.any\(\):
                    messages\.error\(request, 'The user_id column contains null or missing values\.'\)
                    fs\.delete\(filename\)
                    return redirect\('bulk_upload'\)

                try:
                    df\['user_id'\] = df\['user_id'\]\.astype\(int\)
                except \(ValueError, TypeError\):
                    messages\.error\(request, 'Invalid data in user_id column\. All values must be integers\.'\)
                    fs\.delete\(filename\)
                    return redirect\('bulk_upload'\)

                if df\['user_id'\]\.duplicated\(\)\.any\(\):
                    messages\.error\(request, 'The user_id column contains duplicate values\.'\)
                    fs\.delete\(filename\)
                    return redirect\('bulk_upload'\)'''

text = re.sub(old_upload, new_upload, text, flags=re.DOTALL)

with open('users/views.py', 'w', encoding='utf-8') as f:
    f.write(text)
print('Replaced first two parts!')
