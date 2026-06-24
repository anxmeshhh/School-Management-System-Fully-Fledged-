def bulk_upload(request):
    if not request.session.get('admin_id'):
        messages.error(request, 'You must be logged in to access this page.')
        return redirect('admin_login')

    if request.method == 'POST':
        if 'preview' in request.POST and 'excel_file' in request.FILES:
            excel_file = request.FILES['excel_file']
            if not excel_file.name.endswith(('.xlsx', '.xls')):
                messages.error(request, 'Please upload a valid Excel file (.xlsx or .xls).')
                return redirect('bulk_upload')

            if excel_file.size == 0:
                messages.error(request, 'The uploaded file is empty.')
                return redirect('bulk_upload')

            fs = FileSystemStorage(location=os.path.join(settings.MEDIA_ROOT, 'temp'))
            filename = f"temp_{uuid.uuid4()}_{excel_file.name}"
            fs.save(filename, excel_file)

            try:
                df = pd.read_excel(fs.path(filename))
                
                if df.empty:
                    messages.error(request, 'The Excel file contains no data.')
                    fs.delete(filename)
                    return redirect('bulk_upload')

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

                missing_columns = [col for col in expected_columns if col not in df.columns]
                if missing_columns:
                    messages.error(request, f'Missing columns in Excel file: {", ".join(missing_columns)}')
                    fs.delete(filename)
                    return redirect('bulk_upload')

                # Convert NaN, pd.NA, and None to None (MySQL NULL)
                df = df.replace([pd.NA, np.nan, None], None)

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
                    return redirect('bulk_upload')

                # Validate admission_number (now optional)
                # Convert to string, replacing literal 'nan', 'none' with None
                df['admission_number'] = df['admission_number'].apply(
                    lambda x: str(x).strip() if pd.notna(x) and str(x).strip().lower() not in ['nan', 'none', 'n/a', 'not-provided', ''] else None
                )

                if df['admission_number'].dropna().duplicated().any():
                    messages.error(request, 'The admission_number column contains duplicate values for non-empty records.')
                    fs.delete(filename)
                    return redirect('bulk_upload')

                # Validate roll_number
                if df['roll_number'].isna().any():
                    messages.error(request, 'The roll_number column contains null or missing values.')
                    fs.delete(filename)
                    return redirect('bulk_upload')

                try:
                    df['roll_number'] = df['roll_number'].astype(int)
                except (ValueError, TypeError):
                    messages.error(request, 'Invalid data in roll_number column. All values must be integers.')
                    fs.delete(filename)
                    return redirect('bulk_upload')

                # Validate name (for username)
                if df['name'].isna().any():
                    messages.error(request, 'The name column contains null or missing values.')
                    fs.delete(filename)
                    return redirect('bulk_upload')

                # Convert date fields
                if 'dob' in df.columns:
                    df['dob'] = pd.to_datetime(df['dob'], dayfirst=True, errors='coerce').dt.strftime('%Y-%m-%d')
                if 'admission_date' in df.columns:
                    df['admission_date'] = pd.to_datetime(df['admission_date'], dayfirst=True, errors='coerce').dt.strftime('%Y-%m-%d')

                preview_data = df.head(10).to_dict('records')
                preview_columns = df.columns.tolist()

                request.session['temp_excel_file'] = filename

                return render(request, 'users/bulk_upload.html', {
                    'preview_data': preview_data,
                    'preview_columns': preview_columns
                })

            except Exception as e:
                messages.error(request, f'Error processing Excel file: {str(e)}')
                fs.delete(filename)
                return redirect('bulk_upload')

        elif 'upload' in request.POST:
            filename = request.session.get('temp_excel_file')
            if not filename:
                messages.error(request, 'No file selected for upload. Please upload a file first.')
                return redirect('bulk_upload')

            fs = FileSystemStorage(location=os.path.join(settings.MEDIA_ROOT, 'temp'))
            try:
                df = pd.read_excel(fs.path(filename))

                # Convert NaN, pd.NA, and None to None (MySQL NULL)
                df = df.replace([pd.NA, np.nan, None], None)

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
                    return redirect('bulk_upload')

                # Validate admission_number (now optional)
                # Convert to string, replacing literal 'nan', 'none' with None
                df['admission_number'] = df['admission_number'].apply(
                    lambda x: str(x).strip() if pd.notna(x) and str(x).strip().lower() not in ['nan', 'none', 'n/a', 'not-provided', ''] else None
                )

                if df['admission_number'].dropna().duplicated().any():
                    messages.error(request, 'The admission_number column contains duplicate values for non-empty records.')
                    fs.delete(filename)
                    return redirect('bulk_upload')

                # Validate roll_number
                if df['roll_number'].isna().any():
                    messages.error(request, 'The roll_number column contains null or missing values.')
                    fs.delete(filename)
                    return redirect('bulk_upload')

                try:
                    df['roll_number'] = df['roll_number'].astype(int)
                except (ValueError, TypeError):
                    messages.error(request, 'Invalid data in roll_number column. All values must be integers.')
                    fs.delete(filename)
                    return redirect('bulk_upload')

                # Validate name (for username)
                if df['name'].isna().any():
                    messages.error(request, 'The name column contains null or missing values.')
                    fs.delete(filename)
                    return redirect('bulk_upload')

                # Convert date fields
                if 'dob' in df.columns:
                    df['dob'] = pd.to_datetime(df['dob'], dayfirst=True, errors='coerce').dt.strftime('%Y-%m-%d')
                if 'admission_date' in df.columns:
                    df['admission_date'] = pd.to_datetime(df['admission_date'], dayfirst=True, errors='coerce').dt.strftime('%Y-%m-%d')

                skipped_rows = []
                with connection.cursor() as cursor:
                    for index, row in df.iterrows():
                        try:
                            with transaction.atomic():
                                user_id = row['user_id']  # Use Excel-provided user_id (integer)
                                base_username = str(row.get('name', ''))[:100]  # Reserve space for suffix
                                contact = str(row.get('contact', '')) if row.get('contact') else None
                                alt_contact = str(row.get('alt_contact', '')) if row.get('alt_contact') else None
                                unique_id = str(uuid.uuid4())[:8]  # Short UUID for uniqueness
                                email = f"{base_username.lower().replace(' ', '.')}_{user_id}_{unique_id}@example.com"[:255]  # Unique email
                                password = str(row.get('roll_number', ''))[:255]  # Use roll_number as password

                                # Check if user_id exists in users
                                cursor.execute("SELECT id FROM users WHERE id = %s", [user_id])
                                user_exists = cursor.fetchone()

                                # Handle users table insertion
                                if not user_exists:
                                    # Check if username exists
                                    username = base_username
                                    cursor.execute("SELECT username, email FROM users WHERE username = %s", [username])
                                    existing_user = cursor.fetchone()

                                    if existing_user:
                                        # If username exists, check phone numbers
                                        cursor.execute("""
                                            SELECT u.id 
                                            FROM users u
                                            JOIN student_page3 sp3 ON u.id = sp3.user_id
                                            WHERE u.username = %s AND (sp3.contact = %s OR sp3.alt_contact = %s)
                                        """, [username, contact, alt_contact])
                                        matching_phone = cursor.fetchone()

                                        if matching_phone:
                                            # Same username and phone number; skip this user
                                            print(f"Skipped user_id: {user_id} (duplicate username '{username}' and phone match)")
                                            skipped_rows.append(f"Row {index + 2}: user_id {user_id} (duplicate username and phone)")
                                            continue

                                        # Different phone or no phone match; append user_id to username
                                        username = f"{base_username}_{user_id}"[:150]

                                    # Insert into users
                                    cursor.execute("""
                                        INSERT INTO users (id, username, email, password)
                                        VALUES (%s, %s, %s, %s)
                                    """, [user_id, username, email, password])
                                    print(f"Inserted user_id: {user_id} into users with username: {username}")

                                else:
                                    print(f"Skipped user_id: {user_id} (already exists in users)")

                                # Insert into student_page1 (update name if exists)
                                cursor.execute("""
                                    INSERT INTO student_page1 (
                                        user_id, name, admission_number, class, section, roll_number, emis
                                    ) VALUES (%s, %s, %s, %s, %s, %s, %s)
                                    ON DUPLICATE KEY UPDATE name = name
                                """, [
                                    user_id, row.get('name'), row.get('admission_number'), row.get('class'),
                                    row.get('section'), row.get('roll_number'), row.get('emis')
                                ])

                                # Insert into student_page2 (update gender if exists)
                                cursor.execute("""
                                    INSERT INTO student_page2 (
                                        user_id, gender, community, tamil_name, dob, nationality, blood_group,
                                        mother_tongue, caste, religion, place_of_birth, aadhaar, disability,
                                        id_mark1, id_mark2, current_class, admission_class, admission_year,
                                        admission_date
                                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                                    ON DUPLICATE KEY UPDATE gender = gender
                                """, [
                                    user_id, row.get('gender'), row.get('community'), row.get('tamil_name'), row.get('dob'),
                                    row.get('nationality'), row.get('blood_group'), row.get('mother_tongue'),
                                    row.get('caste'), row.get('religion'), row.get('place_of_birth'), row.get('aadhaar'),
                                    row.get('disability'), row.get('id_mark1'), row.get('id_mark2'), row.get('current_class'),
                                    row.get('admission_class'), row.get('admission_year'), row.get('admission_date')
                                ])

                                # Insert into student_page3 (update email if exists)
                                cursor.execute("""
                                    INSERT INTO student_page3 (
                                        user_id, email, address, contact, alt_contact, country, state, city, pincode,
                                        status, house, teacher_ward, rte, sports_quota, prev_school, prev_board
                                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                                    ON DUPLICATE KEY UPDATE email = email
                                """, [
                                    user_id, row.get('email'), row.get('address'), row.get('contact'), row.get('alt_contact'),
                                    row.get('country'), row.get('state'), row.get('city'), row.get('pincode'),
                                    row.get('status'), row.get('house'), row.get('teacher_ward'), row.get('rte'),
                                    row.get('sports_quota'), row.get('prev_school'), row.get('prev_board')
                                ])

                                # Insert into student_page4 (update father_name if exists)
                                cursor.execute("""
                                    INSERT INTO student_page4 (
                                        user_id, father_name, father_name_tamil, mother_name, mother_name_tamil,
                                        father_contact, mother_contact, father_email, mother_email, father_qualification,
                                        mother_qualification, father_occupation, mother_occupation, father_income,
                                        mother_income, guardian_name, guardian_contact, guardian_email, child_living,
                                        rights_on_child, med_blood_group, diseases, allergies, medicines, hospital, doctor
                                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                                    ON DUPLICATE KEY UPDATE father_name = father_name
                                """, [
                                    user_id, row.get('father_name'), row.get('father_name_tamil'), row.get('mother_name'),
                                    row.get('mother_name_tamil'), row.get('father_contact'), row.get('mother_contact'),
                                    row.get('father_email'), row.get('mother_email'), row.get('father_qualification'),
                                    row.get('mother_qualification'), row.get('father_occupation'), row.get('mother_occupation'),
                                    row.get('father_income'), row.get('mother_income'), row.get('guardian_name'),
                                    row.get('guardian_contact'), row.get('guardian_email'), row.get('child_living'),
                                    row.get('rights_on_child'), row.get('med_blood_group'), row.get('diseases'),
                                    row.get('allergies'), row.get('medicines'), row.get('hospital'), row.get('doctor')
                                ])

                        except IntegrityError as e:
                            error_msg = f"Row {index + 2}: user_id {user_id} failed due to {str(e)}"
                            print(error_msg)
                            skipped_rows.append(error_msg)
                            continue  # Continue with the next row

                if skipped_rows:
                    messages.warning(request, f"Some rows were skipped: {'; '.join(skipped_rows)}")
                messages.success(request, 'Data upload completed!')
                fs.delete(filename)
                if 'temp_excel_file' in request.session:
                    del request.session['temp_excel_file']
                return redirect('bulk_upload')

            except Exception as e:
                messages.error(request, f'Error uploading data: {str(e)}')
                fs.delete(filename)
                if 'temp_excel_file' in request.session:
                    del request.session['temp_excel_file']
                return redirect('bulk_upload')

    return render(request, 'users/bulk_upload.html')
