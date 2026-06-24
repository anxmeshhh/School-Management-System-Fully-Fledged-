import re

with open('users/views.py', 'r', encoding='utf-8') as f:
    text = f.read()

old_loop = r'''                            with transaction\.atomic\(\):
                                user_id = row\['user_id'\]  # Use Excel-provided user_id \(integer\)
                                base_username = str\(row\.get\('name', ''\)\)\[:100\]  # Reserve space for suffix
                                contact = str\(row\.get\('contact', ''\)\) if row\.get\('contact'\) else None
                                alt_contact = str\(row\.get\('alt_contact', ''\)\) if row\.get\('alt_contact'\) else None
                                unique_id = str\(uuid\.uuid4\(\)\)\[:8\]  # Short UUID for uniqueness
                                email = f"\{base_username\.lower\(\)\.replace\(' ', '\.'\)\}_\{user_id\}_\{unique_id\}@example\.com"\[:255\]  # Unique email
                                password = str\(row\.get\('roll_number', ''\)\)\[:255\]  # Use roll_number as password

                                # Check if user_id exists in users
                                cursor\.execute\("SELECT id FROM users WHERE id = %s", \[user_id\]\)
                                user_exists = cursor\.fetchone\(\)

                                # Handle users table insertion
                                if not user_exists:
                                    # Check if username exists
                                    username = base_username
                                    cursor\.execute\("SELECT username, email FROM users WHERE username = %s", \[username\]\)
                                    existing_user = cursor\.fetchone\(\)

                                    if existing_user:
                                        # If username exists, check phone numbers
                                        cursor\.execute\("""
                                            SELECT u\.id 
                                            FROM users u
                                            JOIN student_page3 sp3 ON u\.id = sp3\.user_id
                                            WHERE u\.username = %s AND \(sp3\.contact = %s OR sp3\.alt_contact = %s\)
                                        """, \[username, contact, alt_contact\]\)
                                        matching_phone = cursor\.fetchone\(\)

                                        if matching_phone:
                                            # Same username and phone number; skip this user
                                            print\(f"Skipped user_id: \{user_id\} \(duplicate username '\{username\}' and phone match\)"\)
                                            skipped_rows\.append\(f"Row \{index \+ 2\}: user_id \{user_id\} \(duplicate username and phone\)"\)
                                            continue

                                        # Different phone or no phone match; append user_id to username
                                        username = f"\{base_username\}_\{user_id\}"\[:150\]'''

new_loop = r'''                            with transaction.atomic():
                                user_id = row['user_id']
                                if user_id is None:
                                    cursor.execute("SELECT MAX(id) FROM users")
                                    max_id = cursor.fetchone()[0] or 0
                                    user_id = max_id + 1

                                base_username = str(row.get('name', ''))[:100]
                                contact = str(row.get('contact', '')) if row.get('contact') else None
                                alt_contact = str(row.get('alt_contact', '')) if row.get('alt_contact') else None
                                unique_id = str(uuid.uuid4())[:8]
                                email = f"{base_username.lower().replace(' ', '.')}_{user_id}_{unique_id}@example.com"[:255]
                                password = str(row.get('roll_number', ''))[:255]

                                cursor.execute("SELECT id FROM users WHERE id = %s", [user_id])
                                user_exists = cursor.fetchone()

                                if not user_exists:
                                    username = base_username
                                    cursor.execute("SELECT username FROM users WHERE username = %s", [username])
                                    existing_user = cursor.fetchone()

                                    if existing_user:
                                        # Force a unique username if it already exists to bypass skips
                                        username = f"{base_username}_{user_id}"[:150]'''

if re.search(old_loop, text):
    text = re.sub(old_loop, new_loop, text, count=1)
    with open('users/views.py', 'w', encoding='utf-8') as f:
        f.write(text)
    print('Replaced loop!')
else:
    print('Regex failed!')
