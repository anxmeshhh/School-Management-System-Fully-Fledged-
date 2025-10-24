import pandas as pd
from openpyxl import Workbook
from openpyxl.utils.dataframe import dataframe_to_rows

# Define the required columns
columns = [
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

# Create an empty DataFrame with these columns
df = pd.DataFrame(columns=columns)

# Create a workbook and worksheet
wb = Workbook()
ws = wb.active
ws.title = "Bulk Upload Template"

# Write the headers to the worksheet
for r in dataframe_to_rows(df, header=True, index=False):
    ws.append(r)

# Adjust column widths for better readability (optional)
for column in ws.columns:
    max_length = 0
    column_letter = column[0].column_letter
    for cell in column:
        try:
            if len(str(cell.value)) > max_length:
                max_length = len(str(cell.value))
        except:
            pass
    adjusted_width = min(max_length + 2, 50)  # Cap at 50 chars
    ws.column_dimensions[column_letter].width = adjusted_width

# Save the workbook to a file
output_file = 'bulk_upload_template.xlsx'
wb.save(output_file)
print(f"XLSX template saved as '{output_file}'. Open it in Excel to add your data!")