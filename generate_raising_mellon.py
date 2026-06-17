import uuid

data = [
    (1, 'AARAV PUROHIT', '03-09-2023', 'CMSRM01', 'HINDI', 'RAISING MELLON', 'NITESH KUMAR', '7010577064', 'PINKI', '9080695391', 'NO 6, FIRST FLOOR, KUMARAPPA STREET, SEVENWELLS, CHENNAI-01'),
    (2, 'AVIYUKTH (PP)', None, 'CMSRM02', None, 'RAISING MELLON', None, None, None, None, None),
    (3, 'CHIRAG PATEL', None, 'CMSRM03', None, 'RAISING MELLON', None, None, None, None, None),
    (4, 'DHANISHKA KEDIA', '10-05-2023', 'CMSRM04', 'HINDI', 'RAISING MELLON', 'ARUN KEDIA', '9840017055', 'NIDHI KEDIA', '9385517055', 'OLD NO 56, NEW NO 69 MINT ST 4TH FLOOR, NEAR RAJA RANI STORE CHENNAI 01'),
    (5, 'DHANVIKASRI.M', '16-03-2023', 'CMSRM05', 'TELUGU', 'RAISING MELLON', 'GIRI', '9884388756', 'GOMATHI', '6374850493', '3/5, KUMARAPPAN STREET, SEVEN WELLS MINT , CHENNAI 01'),
    (6, 'DHANVINE .M', '16-03-2023', 'CMSRM06', 'TELUGU', 'RAISING MELLON', 'GIRI', '9884388756', 'GOMATHI', '6374850493', '3/5, KUMARAPPAN STREET, SEVEN WELLS MINT , CHENNAI 01'),
    (7, 'HARSHITH.R', '10-04-2023', 'CMSRM07', 'TAMIL', 'RAISING MELLON', 'RAJASEKAR', '9789946985', 'DR.T.PRIYA', '8667031685', 'FRANCIS TURIN STREET 7WELLS CH01'),
    (8, 'HITANSH . M. JAIN', '17-07-2023', 'CMSRM08', 'HINDI', 'RAISING MELLON', 'MUKESH', '7010041690', 'SWATI', '7397498044', '9A/15, TEYNAMPET RAMASWAMY STREET KONDITHOPE CHENNAI 01'),
    (9, 'KANISHK AYYAN.T', '20-11-2023', 'CMSRM09', 'TAMIL', 'RAISING MELLON', 'N.THANGAVEL', '8056160692', 'T.SOUNDARYA', '6382518965', '25/55 1ST FLOOR, MUNIAPPAN STREET KONDITHOPE CHENNAI 01'),
    (10, 'KATHIRVELAN', '21-01-2023', 'CMSRM10', 'TAMIL', 'RAISING MELLON', 'RAJENDRAN.V', '9498136606', 'MAHALAKSHMI.S', '9444506106', 'M BLOCK 16 NO KONDITHOPE POLICE QUARTERS'),
    (11, 'MAFAZ MOHAMED.M', '07-05-2023', 'CMSRM11', 'TAMIL', 'RAISING MELLON', 'MOHAMED WASIM AKRAM', '9789011661', 'MOHAMED MALIHA BEEVI', '9940205199', '266, THAMBU CHETTY STREET, MANNADY, CHENNAI 01'),
    (12, 'MALLAPU HIMANI', '20-06-2023', 'CMSRM12', 'TELUGU', 'RAISING MELLON', 'MALLAPU BALAJI', '9940385572', 'POKKALI MEENAKSHI BALAJI', '9445725555', '30, MUNIYAPPAN STREET KONDITHOPE CHENNAI 01'),
    (13, 'MOKSHITHA .Y', '01-05-2023', 'CMSRM13', 'TAMIL', 'RAISING MELLON', 'YUVARAJM', '9500160072', 'REVATHY', '9789971682', '22, AMBEDKAR NAGAR 6TH STREET KORUKKUPET CHENNAI 21'),
    (14, 'MUHAMMAD IZYAN', '19-01-2023', 'CMSRM14', 'TAMIL', 'RAISING MELLON', 'SEYED MOHAMMED BUHARI', '9566826288', 'S.V.AYSHA RIFCA', '9652969285', '24/25, MUTHU NAICKEN STREET MANNADY BROADWAY CHENNAI 1'),
    (15, 'NITHYASREE', '08-01-2024', 'CMSRM15', 'TAMIL', 'RAISING MELLON', 'K.KARTHIKEYAN', '8840375661', 'S.BHUVANESHWARI', '9094733307', '22/24 RIAINBOW APARTMENT ,KUMARAPPA STREET, SEVENWELLS CHENNAI 01.'),
    (16, 'NIVANSHI', None, 'CMSRM16', None, 'RAISING MELLON', None, None, None, None, None),
    (17, 'PAWAN SAI .R', '05-04-2023', 'CMSRM17', 'TAMIL', 'RAISING MELLON', 'RAJESH', '9940504461', 'GEETHA', '6381839019', '7/19, KUTTY MAISTRY STREET SEVEN WELLS CHENNAI 01'),
    (18, 'PON NITHIRAN.M.M', '11-02-2023', 'CMSRM18', 'TAMIL', 'RAISING MELLON', 'MADHIARASAN', '8098344005', 'PRIYADARSHINI', '9840851211', '7/2,RATHINAM STREET KONDITHOPE CHENNAI 01'),
    (19, 'RIDHIMA MAJI', '13-03-2022', 'CMSRM19', 'BENGALI', 'RAISING MELLON', 'RADHE SHYAM MAJI', '8838119102', 'MANDIRA MAJI', '9962035809', '15/17, VADAMALAI MAISTRY STREET KONDITHOPE CHENNAI 01'),
    (20, 'RIDIT DEWASI', None, 'CMSRM20', None, 'RAISING MELLON', None, None, None, None, None),
    (21, 'SARA IZNA', '15-10-2023', 'CMSRM21', 'TAMIL', 'RAISING MELLON', 'KAMAAL KHAN A', '8941196144', 'EZRA MUSHIRA M S', '8788801932', '88/64 SEVENWELLS STREET.SEVENWELLS GEORGE TOWN CHENNAI 01'),
    (22, 'SHRISTIKA.P', '08-07-2023', 'CMSRM22', 'TAMIL', 'RAISING MELLON', 'K.PRABHU', '9581071440', 'T. MEENA', '8838810364', 'NO.8, AMMAN KOIL STREET PARK TOWN CHENNAI - 600003'),
    (23, 'SRI VARAHI .R', '10-04-2023', 'CMSRM23', 'TAMIL', 'RAISING MELLON', 'RAJESH', '9940212785', 'JAGADEESHWARI', '7305618408', '75/36,PERIYANNA MUDALI STREET SEVEN WELLS CHENNAI 01'),
    (24, 'TAQIYAH THANZIL', '18-06-2023', 'CMSRM24', 'TAMIL', 'RAISING MELLON', 'THANZILUR REHMAN SHAHUL H', '9003358444', 'THASNEEM KALANJIAM Z', '9003358444', 'NO 266/201 THAMBU CHETTY STREET, MANNADY CHENNAI 01'),
    (25, 'VEDHA SREE.R', '15-07-2023', 'CMSRM25', 'TAMIL', 'RAISING MELLON', 'S.RAJESH', '9176734060', 'R.PREETHI', '8056273355', 'NO 25/9 PERUMAL STREET, KONDITHOPE ,CHENNAI 01'),
    (26, 'YASHMIKA.D', '01-10-2022', 'CMSRM26', 'TELUGU', 'RAISING MELLON', 'DINESH D', '8939145981', 'D PRIYANKA', '8428713575', '23/12 PERUMAL KOIL GARDEN STREET,SOWCARPET,CHENNAI 01'),
    (27, 'YATHVIKA SRI .V', '15-11-2023', 'CMSRM27', 'TAMIL', 'RAISING MELLON', 'VIGNESH', '9841093551', 'PRIYA', '9150260817', '35, NEW STREET MANNADY CHENNAI 01')
]

def format_date(d):
    if d is None:
        return None
    # convert DD-MM-YYYY to YYYY-MM-DD
    parts = d.split('-')
    if len(parts) == 3:
        return f"{parts[2]}-{parts[1]}-{parts[0]}"
    return d

def esc(val):
    if val is None:
        return 'NULL'
    if isinstance(val, int):
        return str(val)
    return "'" + str(val).replace("'", "''") + "'"

with open("raising_mellon_sql_commands.txt", "w") as f:
    for row in data:
        # Starting from 60000 for RAISING MELLON to avoid conflicts
        user_id = 60000 + row[0]
        
        name = row[1] if row[1] is not None else ''
        dob = format_date(row[2])
        adm_no = row[3] if row[3] is not None else ''
        lang = row[4] if row[4] is not None else ''
        cls = row[5] if row[5] is not None else ''
        fname = row[6] if row[6] is not None else ''
        contact = row[7] if row[7] is not None else ''
        mname = row[8] if row[8] is not None else ''
        mcontact = row[9] if row[9] is not None else ''
        address = row[10] if row[10] is not None else ''
        roll = row[0] # Use S.No. as roll number since there is no separate roll col
        
        base_username = str(name)[:100]
        unique_id = str(uuid.uuid4())[:8]
        email = f"{base_username.lower().replace(' ', '.')}_{user_id}_{unique_id}@example.com"[:255]
        password = str(roll)[:255]
        username = base_username

        f.write(f"INSERT IGNORE INTO users (id, username, email, password) VALUES ({user_id}, {esc(username)}, {esc(email)}, {esc(password)});\n")
        f.write(f"INSERT IGNORE INTO student_page1 (user_id, name, admission_number, class, section, roll_number) VALUES ({user_id}, {esc(name)}, {esc(adm_no)}, {esc(cls)}, NULL, {roll});\n")
        f.write(f"INSERT IGNORE INTO student_page2 (user_id, dob, mother_tongue) VALUES ({user_id}, {esc(dob)}, {esc(lang)});\n")
        f.write(f"INSERT IGNORE INTO student_page3 (user_id, address, contact) VALUES ({user_id}, {esc(address)}, {esc(contact)});\n")
        f.write(f"INSERT IGNORE INTO student_page4 (user_id, father_name, mother_name, father_contact, mother_contact) VALUES ({user_id}, {esc(fname)}, {esc(mname)}, {esc(contact)}, {esc(mcontact)});\n")
        f.write(f"INSERT IGNORE INTO school_students (id, name, roll_number) VALUES ({user_id}, {esc(name)}, {roll});\n")
        f.write("\n")
