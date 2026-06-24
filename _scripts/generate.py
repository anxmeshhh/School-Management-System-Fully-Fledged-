import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random

# List of students with user_id and name (adjusted for Class 2A, user_ids starting from 27, exactly 26 students)
students = [
    (27, 'AARTHI.R'),
    (28, 'BHARATHI.S'),
    (29, 'CHANDRA.K'),
    (30, 'DHANYA.M'),
    (31, 'ESWARI.P'),
    (32, 'FATHIMA.B'),
    (33, 'GOWRI.N'),
    (34, 'HARINI.V'),
    (35, 'INDHUJA.A'),
    (36, 'JAYASHREE.D'),
    (37, 'KALAIARASI.T'),
    (38, 'LAKSHMI.S'),
    (39, 'MANJULA.R'),
    (40, 'ARJUN.R'),
    (41, 'BALAJI.K'),
    (42, 'CHANDRAN.M'),
    (43, 'DHANUSH.P'),
    (44, 'EKAMBARAN.N'),
    (45, 'FIRTHOUSE.V'),
    (46, 'GANESH.A'),
    (47, 'HARISH.D'),
    (48, 'INBAM.T'),
    (49, 'JAGAN.S'),
    (50, 'KIRAN.R'),
    (51, 'LOGANATHAN.K'),
    (52, 'MOHAN.M')
]

# Dummy data lists for cycling through values (similar to before, but adjusted for younger kids)
genders = ['Female'] * 13 + ['Male'] * 13  # 26 total
communities = ['OC', 'BC', 'SC', 'ST', 'OC', 'BC', 'SC', 'ST'] * 4
nationalities = ['Indian'] * len(students)
blood_groups = ['O+', 'A+', 'B+', 'AB+', 'O-', 'A-', 'B-', 'AB-'] * 4
mother_tongues = ['Tamil', 'Telugu', 'Malayalam', 'Kannada', 'Hindi', 'English'] * 5
castes = ['General', 'OBC', 'SC', 'ST'] * 7
religions = ['Hindu', 'Christian', 'Muslim', 'Sikh', 'Jain'] * 6
places_of_birth = ['Chennai', 'Coimbatore', 'Madurai', 'Salem', 'Tiruchirappalli', 'Erode'] * 5
aadhaars = [f"6789{str(i).zfill(4)}2345" for i in range(1, 1 + len(students))]  # Different dummy Aadhaar-like
disabilities = [None] * len(students)
id_marks1 = ['Mole on forehead', 'Dimple on chin', 'Freckles on nose', None, 'Tattoo-like mark'] * 6
id_marks2 = [None] * len(students)
current_classes = ['2'] * len(students)  # Class 2 (numeric)
admission_classes = ['2'] * len(students)
admission_years = ['2023'] * len(students)  # Recent admission
admission_dates = ['2023-06-01'] * len(students)
emails = [None] * len(students)  # Will be generated in upload
addresses = [
    '124 Main St, Chennai, TN',
    '457 Elm St, Coimbatore, TN',
    '790 Oak St, Madurai, TN',
    '102 Pine St, Salem, TN',
    '203 Birch St, Trichy, TN',
    '304 Cedar St, Erode, TN'
] * 5
contacts = [f"9{random.randint(100000000, 999999999)}" for _ in range(len(students))]
alt_contacts = [f"8{random.randint(100000000, 999999999)}" for _ in range(len(students))]
countries = ['India'] * len(students)
states = ['Tamil Nadu'] * len(students)
cities = ['Chennai', 'Coimbatore', 'Madurai', 'Salem', 'Tiruchirappalli', 'Erode'] * 5
pincodes = ['600002', '641002', '625002', '636002', '620002', '638002'] * 5
statuses = ['Active'] * len(students)
houses = ['Red', 'Blue', 'Green', 'Yellow'] * 7
teacher_wards = ['yes' if i % 2 == 0 else 'no' for i in range(len(students))]  # Alternate yes/no
rtes = ['yes' if i % 2 == 0 else 'no' for i in range(len(students))]  # Alternate yes/no for RTE
sports_quotas = ['yes' if i % 3 == 0 else 'no' for i in range(len(students))]  # Cycle yes/no for variety
prev_schools = ['Class 1 School', 'Primary School', None, 'Government School'] * 7
prev_boards = [None] * len(students)  # No boards for primary
father_names = [f'Father of {name.split(".")[0]}' for _, name in students]
father_names_tamil = [None] * len(students)
mother_names = [f'Mother of {name.split(".")[0]}' for _, name in students]
mother_names_tamil = [None] * len(students)
father_contacts = [f"7{random.randint(100000000, 999999999)}" for _ in range(len(students))]
mother_contacts = [f"9{random.randint(100000000, 999999999)}" for _ in range(len(students))]
father_emails = [f"father_{i}@example.com" for i in range(27, 27 + len(students))]
mother_emails = [f"mother_{i}@example.com" for i in range(27, 27 + len(students))]
father_qualifications = ['Graduate', 'Post Graduate', 'Diploma', 'High School'] * 7
mother_qualifications = ['Graduate', 'Post Graduate', 'Diploma', 'High School'] * 7
father_occupations = ['Engineer', 'Teacher', 'Doctor', 'Businessman'] * 7
mother_occupations = ['Housewife', 'Teacher', 'Nurse', 'Clerk'] * 7
father_incomes = [55000, 80000, 110000, 45000] * 7
mother_incomes = [0, 35000, 55000, 30000] * 7
guardian_names = [None] * len(students)
guardian_contacts = [None] * len(students)
guardian_emails = [None] * len(students)
child_livings = ['With Parents'] * len(students)
rights_on_childs = ['Both Parents'] * len(students)
med_blood_groups = [None] * len(students)
diseases = [None] * len(students)
allergies = ['Peanuts', None, 'Eggs', None] * 7  # Some common kid allergies
medicines = [None] * len(students)
hospitals = [None] * len(students)
doctors = [None] * len(students)

# Generate DOBs around 2018 (for Class 2 in 2025)
base_date = datetime(2018, 1, 1)
dobs = [(base_date + timedelta(days=random.randint(0, 365))).strftime('%Y-%m-%d') for _ in range(len(students))]

# Generate EMIS codes (dummy)
emises = [f"EMIS{random.randint(10000, 99999)}" for _ in range(len(students))]

# Generate roll_numbers (sequential 1 to 26)
roll_numbers = list(range(1, len(students) + 1))

# Generate tamil_names (dummy, set to None for simplicity)
tamil_names = [None] * len(students)

# Create rows
rows = []
for idx, (user_id, name) in enumerate(students):
    row = {
        'user_id': user_id,
        'name': name.strip(),
        'admission_number': str(user_id),  # Use user_id as admission_number
        'class': '2',
        'section': 'A',
        'roll_number': roll_numbers[idx],
        'emis': emises[idx],
        'gender': genders[idx],
        'community': communities[idx],
        'tamil_name': tamil_names[idx],
        'dob': dobs[idx],
        'nationality': nationalities[idx],
        'blood_group': blood_groups[idx],
        'mother_tongue': mother_tongues[idx],
        'caste': castes[idx],
        'religion': religions[idx],
        'place_of_birth': places_of_birth[idx],
        'aadhaar': aadhaars[idx],
        'disability': disabilities[idx],
        'id_mark1': id_marks1[idx],
        'id_mark2': id_marks2[idx],
        'current_class': current_classes[idx],
        'admission_class': admission_classes[idx],
        'admission_year': admission_years[idx],
        'admission_date': admission_dates[idx],
        'email': emails[idx],
        'address': addresses[idx],
        'contact': contacts[idx],
        'alt_contact': alt_contacts[idx],
        'country': countries[idx],
        'state': states[idx],
        'city': cities[idx],
        'pincode': pincodes[idx],
        'status': statuses[idx],
        'house': houses[idx],
        'teacher_ward': teacher_wards[idx],
        'rte': rtes[idx],
        'sports_quota': sports_quotas[idx],
        'prev_school': prev_schools[idx],
        'prev_board': prev_boards[idx],
        'father_name': father_names[idx],
        'father_name_tamil': father_names_tamil[idx],
        'mother_name': mother_names[idx],
        'mother_name_tamil': mother_names_tamil[idx],
        'father_contact': father_contacts[idx],
        'mother_contact': mother_contacts[idx],
        'father_email': father_emails[idx],
        'mother_email': mother_emails[idx],
        'father_qualification': father_qualifications[idx],
        'mother_qualification': mother_qualifications[idx],
        'father_occupation': father_occupations[idx],
        'mother_occupation': mother_occupations[idx],
        'father_income': father_incomes[idx],
        'mother_income': mother_incomes[idx],
        'guardian_name': guardian_names[idx],
        'guardian_contact': guardian_contacts[idx],
        'guardian_email': guardian_emails[idx],
        'child_living': child_livings[idx],
        'rights_on_child': rights_on_childs[idx],
        'med_blood_group': med_blood_groups[idx],
        'diseases': diseases[idx],
        'allergies': allergies[idx],
        'medicines': medicines[idx],
        'hospital': hospitals[idx],
        'doctor': doctors[idx]
    }
    rows.append(row)

# Create DataFrame
df = pd.DataFrame(rows)

# Reorder columns to match expected_columns
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
df = df.reindex(columns=expected_columns)

# Replace any remaining NaN with None
df = df.replace({np.nan: None})

# Save to Excel
df.to_excel('dummy_students_class2A_fixed.xlsx', index=False, engine='openpyxl')

print("Excel file 'dummy_students_class2A_fixed.xlsx' generated successfully with 'yes'/'no' values for rte.")