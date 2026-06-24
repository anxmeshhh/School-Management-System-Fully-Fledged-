import re
with open(r'd:\animesh\School-Management-System-Fully-Fledged-\users\views.py', 'r', encoding='utf-8', errors='ignore') as f:
    for i, line in enumerate(f):
        if 'admission_number' in line:
            print(f"L{i+1}: {line.strip()}")
