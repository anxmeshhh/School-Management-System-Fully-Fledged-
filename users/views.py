
from django.shortcuts import render
from django.contrib.auth import authenticate, login
from django.http import HttpResponseRedirect



from django.shortcuts import render, redirect
from django.contrib import messages

# Database connection
import pymysql


def get_db_connection():
    return pymysql.connect(
        host="yamabiko.proxy.rlwy.net",  # Host
        user="root",  # Username
        password="AaLqLCgRttNkiQlWmsVdhBFvaHvYpNHW",  # Password
        database="railway",  # Database name
        port=13364  # Port
    )




def signup_view(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]
        password = request.POST["password"]
        confirm_password = request.POST["confirm_password"]

        # Check if passwords match
        if password != confirm_password:
            messages.error(request, "Passwords do not match!")
            return render(request, "users/index.html")

        try:
            conn = get_db_connection()
            cursor = conn.cursor()

            # Insert user into database
            query = "INSERT INTO users (username, email, password) VALUES (%s, %s, %s)"
            cursor.execute(query, (username, email, password))
            conn.commit()

            cursor.close()
            conn.close()

            messages.success(request, "Account created successfully! Please log in.")
            return redirect("login")

        except pymysql.MySQLError as e:
            messages.error(request, f"Database error: {e}")
            return render(request, "users/index.html")

    return render(request, "users/index.html")


from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.db import connection

def login_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        # Check user credentials in MySQL
        with connection.cursor() as cursor:
            cursor.execute("SELECT id FROM users WHERE username = %s AND password = %s", (username, password))
            user = cursor.fetchone()

        if user:
            request.session["user_id"] = user[0]  # Store user ID in session
            return HttpResponse("Success")  
        
            

        return HttpResponse("Invalid credentials!")  

    return render(request, "users/login.html")


def dashboard_view(request):
    return render(request, "users/dashboard.html")




from django.shortcuts import render, redirect
from django.db import connection, transaction

def profile_view(request):
    if "user_id" not in request.session:
        return redirect("/login/")  # Redirect to login if not authenticated

    user_id = request.session["user_id"]  # Get logged-in user's ID

    if request.method == "POST":
        try:
            with transaction.atomic():  # Ensures all queries execute successfully or none at all
                # Fetch form data from POST request (Page 1)
                name = request.POST.get("name")
                admission_number = request.POST.get("admission_number")
                student_class = request.POST.get("class")
                section = request.POST.get("section")
                roll_number = request.POST.get("roll_number")
                emis = request.POST.get("emis")

                # Page 2 data
                gender = request.POST.get("gender")
                community = request.POST.get("community")
                tamil_name = request.POST.get("tamil_name")
                dob = request.POST.get("dob") or None
                nationality = request.POST.get("nationality")
                blood_group = request.POST.get("blood_group")
                mother_tongue = request.POST.get("mother_tongue")
                caste = request.POST.get("caste")
                religion = request.POST.get("religion")
                place_of_birth = request.POST.get("place_of_birth")
                aadhaar = request.POST.get("aadhaar")
                disability = request.POST.get("disability")
                id_mark1 = request.POST.get("id_mark1")
                id_mark2 = request.POST.get("id_mark2")
                current_class = request.POST.get("current_class")
                admission_class = request.POST.get("admission_class")
                admission_year = request.POST.get("admission_year")
                admission_date = request.POST.get("admission_date") or None

                # Page 3 data (Communication Details)
                email = request.POST.get("email")
                address = request.POST.get("address")
                contact = request.POST.get("contact")
                alt_contact = request.POST.get("alt_contact")
                country = request.POST.get("country")
                state = request.POST.get("state")
                city = request.POST.get("city")
                pincode = request.POST.get("pincode")
                status = request.POST.get("status")
                house = request.POST.get("house")
                teacher_ward = request.POST.get("teacher_ward")
                rte = request.POST.get("rte")
                sports_quota = request.POST.get("sports_quota")
                prev_school = request.POST.get("prev_school")
                prev_board = request.POST.get("prev_board")

                # Page 4 data (Parent & Medical Information)
                father_name = request.POST.get("father_name")
                father_name_tamil = request.POST.get("father_name_tamil")
                mother_name = request.POST.get("mother_name")
                mother_name_tamil = request.POST.get("mother_name_tamil")
                father_contact = request.POST.get("father_contact")
                mother_contact = request.POST.get("mother_contact")
                father_email = request.POST.get("father_email")
                mother_email = request.POST.get("mother_email")
                father_qualification = request.POST.get("father_qualification")
                mother_qualification = request.POST.get("mother_qualification")
                father_occupation = request.POST.get("father_occupation")
                mother_occupation = request.POST.get("mother_occupation")
                father_income = request.POST.get("father_income")
                mother_income = request.POST.get("mother_income")
                guardian_name = request.POST.get("guardian_name")
                guardian_contact = request.POST.get("guardian_contact")
                guardian_email = request.POST.get("guardian_email")
                child_living = request.POST.get("child_living")
                rights_on_child = request.POST.get("rights_on_child")
                med_blood_group = request.POST.get("med_blood_group")
                diseases = request.POST.get("diseases")
                allergies = request.POST.get("allergies")
                medicines = request.POST.get("medicines")
                hospital = request.POST.get("hospital")
                doctor = request.POST.get("doctor")

                with connection.cursor() as cursor:
                    # Insert or Update student_page1
                    cursor.execute("""
                        INSERT INTO student_page1 (user_id, name, admission_number, class, section, roll_number, emis)
                        VALUES (%s, %s, %s, %s, %s, %s, %s)
                        ON DUPLICATE KEY UPDATE 
                            name=VALUES(name), admission_number=VALUES(admission_number), 
                            class=VALUES(class), section=VALUES(section), 
                            roll_number=VALUES(roll_number), emis=VALUES(emis)
                    """, (user_id, name, admission_number, student_class, section, roll_number, emis))

                    # Insert or Update student_page2
                    cursor.execute("""
                        INSERT INTO student_page2 (user_id, gender, community, tamil_name, dob, nationality, blood_group, 
                                                   mother_tongue, caste, religion, place_of_birth, aadhaar, disability, 
                                                   id_mark1, id_mark2, current_class, admission_class, admission_year, admission_date)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                        ON DUPLICATE KEY UPDATE 
                            gender=VALUES(gender), community=VALUES(community), tamil_name=VALUES(tamil_name), dob=VALUES(dob),
                            nationality=VALUES(nationality), blood_group=VALUES(blood_group), mother_tongue=VALUES(mother_tongue),
                            caste=VALUES(caste), religion=VALUES(religion), place_of_birth=VALUES(place_of_birth), aadhaar=VALUES(aadhaar),
                            disability=VALUES(disability), id_mark1=VALUES(id_mark1), id_mark2=VALUES(id_mark2),
                            current_class=VALUES(current_class), admission_class=VALUES(admission_class),
                            admission_year=VALUES(admission_year), admission_date=VALUES(admission_date)
                    """, (user_id, gender, community, tamil_name, dob, nationality, blood_group, mother_tongue, 
                          caste, religion, place_of_birth, aadhaar, disability, id_mark1, id_mark2, current_class, 
                          admission_class, admission_year, admission_date))

                    # Insert or Update student_page3
                    cursor.execute("""
                        INSERT INTO student_page3 (user_id, email, address, contact, alt_contact, country, state, city, pincode, status, 
                                                   house, teacher_ward, rte, sports_quota, prev_school, prev_board)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                        ON DUPLICATE KEY UPDATE 
                            email=VALUES(email), address=VALUES(address), contact=VALUES(contact), alt_contact=VALUES(alt_contact),
                            country=VALUES(country), state=VALUES(state), city=VALUES(city), pincode=VALUES(pincode), 
                            status=VALUES(status), house=VALUES(house), teacher_ward=VALUES(teacher_ward), rte=VALUES(rte), 
                            sports_quota=VALUES(sports_quota), prev_school=VALUES(prev_school), prev_board=VALUES(prev_board)
                    """, (user_id, email, address, contact, alt_contact, country, state, city, pincode, status, 
                          house, teacher_ward, rte, sports_quota, prev_school, prev_board))

                    # Insert or Update student_page4 (Parent & Medical Information)
                    cursor.execute("""
                        INSERT INTO student_page4 (
                            user_id, father_name, father_name_tamil, mother_name, mother_name_tamil, father_contact, 
                            mother_contact, father_email, mother_email, father_qualification, mother_qualification, 
                            father_occupation, mother_occupation, father_income, mother_income, guardian_name, 
                            guardian_contact, guardian_email, child_living, rights_on_child, med_blood_group, 
                            diseases, allergies, medicines, hospital, doctor
                        ) 
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                        ON DUPLICATE KEY UPDATE 
                            father_name = VALUES(father_name), 
                            father_name_tamil = VALUES(father_name_tamil),
                            mother_name = VALUES(mother_name), 
                            mother_name_tamil = VALUES(mother_name_tamil), 
                            father_contact = VALUES(father_contact), 
                            mother_contact = VALUES(mother_contact), 
                            father_email = VALUES(father_email), 
                            mother_email = VALUES(mother_email), 
                            father_qualification = VALUES(father_qualification), 
                            mother_qualification = VALUES(mother_qualification), 
                            father_occupation = VALUES(father_occupation), 
                            mother_occupation = VALUES(mother_occupation), 
                            father_income = VALUES(father_income), 
                            mother_income = VALUES(mother_income), 
                            guardian_name = VALUES(guardian_name), 
                            guardian_contact = VALUES(guardian_contact), 
                            guardian_email = VALUES(guardian_email), 
                            child_living = VALUES(child_living), 
                            rights_on_child = VALUES(rights_on_child), 
                            med_blood_group = VALUES(med_blood_group), 
                            diseases = VALUES(diseases), 
                            allergies = VALUES(allergies), 
                            medicines = VALUES(medicines), 
                            hospital = VALUES(hospital), 
                            doctor = VALUES(doctor)
                    """, (
                        user_id, father_name, father_name_tamil, mother_name, mother_name_tamil, father_contact, 
                        mother_contact, father_email, mother_email, father_qualification, mother_qualification, 
                        father_occupation, mother_occupation, father_income, mother_income, guardian_name, 
                        guardian_contact, guardian_email, child_living, rights_on_child, med_blood_group, 
                        diseases, allergies, medicines, hospital, doctor
                    ))



                return redirect("/profile/")  # Redirect after saving

        except Exception as e:
            print("Error updating profile:", e)  # Log error
            return render(request, "users/profile.html", {"error": "Failed to update profile. Please try again."})

    # Fetch student details from all tables for logged-in user
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT 
                -- Student Details (student_page1)
                s1.name, s1.admission_number, s1.class, s1.section, s1.roll_number, s1.emis,
                
                -- Personal Details (student_page2)
                s2.gender, s2.community, s2.tamil_name, s2.dob, s2.nationality, s2.blood_group, 
                s2.mother_tongue, s2.caste, s2.religion, s2.place_of_birth, s2.aadhaar, s2.disability,
                s2.id_mark1, s2.id_mark2, s2.current_class, s2.admission_class, s2.admission_year, s2.admission_date,
                
                -- Contact Details (student_page3)
                s3.email, s3.address, s3.contact, s3.alt_contact, s3.country, s3.state, s3.city, s3.pincode,
                s3.status, s3.house, s3.teacher_ward, s3.rte, s3.sports_quota, s3.prev_school, s3.prev_board,
                
                -- Family Details (student_page4)
                s4.father_name, s4.father_name_tamil, s4.mother_name, s4.mother_name_tamil, 
                s4.father_contact, s4.mother_contact, s4.father_email, s4.mother_email,
                s4.father_qualification, s4.mother_qualification, s4.father_occupation, s4.mother_occupation,
                s4.father_income, s4.mother_income, s4.guardian_name, s4.guardian_contact,
                s4.guardian_email, s4.child_living, s4.rights_on_child,
                s4.med_blood_group, s4.diseases, s4.allergies, s4.medicines, 
                s4.hospital, s4.doctor
            FROM student_page1 s1
            LEFT JOIN student_page2 s2 ON s1.user_id = s2.user_id
            LEFT JOIN student_page3 s3 ON s1.user_id = s3.user_id
            LEFT JOIN student_page4 s4 ON s1.user_id = s4.user_id
            WHERE s1.user_id = %s
        """, [user_id])

        student_data = cursor.fetchone()
    
    if student_data is None:
        print(f"DEBUG: No data found for user_id = {user_id}")



    return render(request, "users/profile.html", {"student_data": student_data})

def attendence_view(request):
    return render(request, "users/attendance.html")

def circular_view(request):
    return render(request, "users/circular.html")
def parent_signup(request):
    return render(request, "users/parent_signup.html")
def parent_login(request):
    return render(request, "users/parent_login.html")

def homework_view(request):
    return render(request, "users/homework.html")

def teacher_view(request):
    return render(request, "users/teacher.html")

def fees(request):
    return render(request, "users/fees.html")

def mark_view(request):
    return render(request, "users/mark.html")
