
from django.shortcuts import render
from django.contrib.auth import authenticate, login
from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect
from django.contrib import messages

# Database connection
import pymysql
def get_db_connection():
    return pymysql.connect(
        host="localhost",  # Host
        user="root",  # Username
        password="theanimesh2005",  # Password
        database="school_db",  # Database name
        port=3306  # Port
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


from django.shortcuts import render
from django.http import HttpResponse
from django.db import connection

def login_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        # Check user credentials in MySQL
        with connection.cursor() as cursor:
            cursor.execute("SELECT id, username FROM users WHERE username = %s AND password = %s", (username, password))
            user = cursor.fetchone()

        if user:
            request.session["user_id"] = user[0]  # Store user ID in session
            request.session["username"] = user[1]  # Store username in session
            
            # Send success message with the username
            return HttpResponse("Success") 

        # If credentials are invalid, send error message
        return HttpResponse("Invalid credentials!")  

    return render(request, "users/login.html")


 

from django.shortcuts import render

def dashboard_view(request):
    # Get the username from the session
    username = request.session.get("username", "Guest")  # Default to "Guest" if not logged in

    # Pass the username to the template
    return render(request, "users/dashboard.html", {"username": username})





import uuid
from django.shortcuts import render, redirect
from django.contrib import messages
from django.db import transaction, connection
from django.utils import timezone
import os
from django.conf import settings
from django.contrib.auth.models import User
from django.http import JsonResponse

def profile_view(request):
    if "user_id" not in request.session:
        return redirect("/login/")  # Redirect to login if not authenticated

    user_id = request.session["user_id"]  # Get logged-in user's ID

    # Fetch profile picture
    profile_picture = None
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT image_path FROM profile_pics WHERE user_id = %s", [user_id])
            profile_picture_result = cursor.fetchone()
            if profile_picture_result:
                profile_picture = f"{settings.MEDIA_URL}{profile_picture_result[0]}"
                print(f"DEBUG: Found profile picture: {profile_picture}")
    except Exception as e:
        print("Error fetching profile picture:", e)

    if request.method == "POST":
        print(f"DEBUG: POST request received")
        print(f"DEBUG: FILES in request: {request.FILES}")
        print(f"DEBUG: POST data: {list(request.POST.keys())}")
        
        try:
            with transaction.atomic():
                # Handle ONLY profile picture upload
                if 'profile_picture' in request.FILES and request.FILES['profile_picture']:
                    print("DEBUG: Processing profile picture upload")
                    profile_picture_file = request.FILES['profile_picture']
                    print(f"DEBUG: File name: {profile_picture_file.name}, Size: {profile_picture_file.size}")
                    
                    # Validate file type
                    allowed_extensions = ['.png', '.jpg', '.jpeg']
                    file_ext = os.path.splitext(profile_picture_file.name)[1].lower()
                    if file_ext not in allowed_extensions:
                        messages.error(request, "Only PNG, JPG, or JPEG files are allowed.")
                        return redirect('profile_view')

                    # Validate file size (5MB limit)
                    if profile_picture_file.size > 5 * 1024 * 1024:
                        messages.error(request, "File size must be less than 5MB.")
                        return redirect('profile_view')

                    # Generate file path using UUID and user_id
                    filename = f"{uuid.uuid4().hex}_{user_id}{file_ext}"
                    
                    # Create pfpics directory in MEDIA_ROOT
                    pfpics_dir = os.path.join(settings.MEDIA_ROOT, 'pfpics')
                    os.makedirs(pfpics_dir, exist_ok=True)
                    
                    file_path = os.path.join(pfpics_dir, filename)
                    print(f"DEBUG: Saving file to: {file_path}")
                    
                    # Delete old profile picture if exists
                    try:
                        with connection.cursor() as cursor:
                            cursor.execute("SELECT image_path FROM profile_pics WHERE user_id = %s", [user_id])
                            old_pic = cursor.fetchone()
                            if old_pic:
                                old_file_path = os.path.join(settings.MEDIA_ROOT, old_pic[0])
                                if os.path.exists(old_file_path):
                                    os.remove(old_file_path)
                                    print(f"DEBUG: Deleted old file: {old_file_path}")
                    except Exception as e:
                        print(f"Error deleting old profile picture: {e}")

                    # Save new file
                    try:
                        with open(file_path, 'wb+') as destination:
                            for chunk in profile_picture_file.chunks():
                                destination.write(chunk)
                        print(f"DEBUG: File saved successfully to {file_path}")
                    except Exception as e:
                        print(f"ERROR: Failed to save file: {e}")
                        messages.error(request, "Failed to save file.")
                        return redirect('profile_view')

                    # Update or insert profile picture path in database
                    try:
                        with connection.cursor() as cursor:
                            cursor.execute("SELECT id FROM profile_pics WHERE user_id = %s", [user_id])
                            existing = cursor.fetchone()
                            
                            db_path = f"pfpics/{filename}"
                            if existing:
                                cursor.execute(
                                    "UPDATE profile_pics SET image_path = %s, uploaded_at = %s WHERE user_id = %s",
                                    [db_path, timezone.now(), user_id]
                                )
                                print(f"DEBUG: Updated existing record with path: {db_path}")
                            else:
                                cursor.execute(
                                    "INSERT INTO profile_pics (user_id, image_path, uploaded_at) VALUES (%s, %s, %s)",
                                    [user_id, db_path, timezone.now()]
                                )
                                print(f"DEBUG: Inserted new record with path: {db_path}")
                    except Exception as e:
                        print(f"ERROR: Database operation failed: {e}")
                        messages.error(request, "Failed to update database.")
                        return redirect('profile_view')
                    
                    messages.success(request, "Profile picture uploaded successfully!")
                    return redirect('profile_view')

                # Handle regular form submission (when no file is uploaded)
                else:
                    print("DEBUG: Processing regular form submission")
                    # Your existing form processing logic here
                    name = request.POST.get("name")
                    admission_number = request.POST.get("admission_number")
                    student_class = request.POST.get("class")
                    section = request.POST.get("section")
                    roll_number = request.POST.get("roll_number")
                    emis = request.POST.get("emis")

                    # Only process if we have actual form data
                    if name or admission_number:
                        # Validate required fields for Page 1
                        if not all([name, admission_number, student_class]):
                            messages.error(request, "Please fill in all required fields.")
                            return redirect('profile_view')

                        # Convert roll_number to integer if provided
                        if roll_number:
                            try:
                                roll_number = int(roll_number)
                            except (ValueError, TypeError):
                                messages.error(request, "Roll number must be a valid integer.")
                                return redirect('profile_view')

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
                                    nationality=VALUES(nationality), blood_group=VALUES(blood_group), 
                                    mother_tongue=VALUES(mother_tongue), caste=VALUES(caste), religion=VALUES(religion),
                                    place_of_birth=VALUES(place_of_birth), aadhaar=VALUES(aadhaar),
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
                                    father_name=VALUES(father_name), father_name_tamil=VALUES(father_name_tamil),
                                    mother_name=VALUES(mother_name), mother_name_tamil=VALUES(mother_name_tamil),
                                    father_contact=VALUES(father_contact), mother_contact=VALUES(mother_contact),
                                    father_email=VALUES(father_email), mother_email=VALUES(mother_email),
                                    father_qualification=VALUES(father_qualification), mother_qualification=VALUES(mother_qualification),
                                    father_occupation=VALUES(father_occupation), mother_occupation=VALUES(mother_occupation),
                                    father_income=VALUES(father_income), mother_income=VALUES(mother_income),
                                    guardian_name=VALUES(guardian_name), guardian_contact=VALUES(guardian_contact),
                                    guardian_email=VALUES(guardian_email), child_living=VALUES(child_living),
                                    rights_on_child=VALUES(rights_on_child), med_blood_group=VALUES(med_blood_group),
                                    diseases=VALUES(diseases), allergies=VALUES(allergies), medicines=VALUES(medicines),
                                    hospital=VALUES(hospital), doctor=VALUES(doctor)
                            """, (
                                user_id, father_name, father_name_tamil, mother_name, mother_name_tamil, father_contact,
                                mother_contact, father_email, mother_email, father_qualification, mother_qualification,
                                father_occupation, mother_occupation, father_income, mother_income, guardian_name,
                                guardian_contact, guardian_email, child_living, rights_on_child, med_blood_group,
                                diseases, allergies, medicines, hospital, doctor
                            ))

                        messages.success(request, "Profile updated successfully.")
                        return redirect('profile_view')

        except Exception as e:
            print(f"ERROR: Exception in POST processing: {e}")
            messages.error(request, f"Failed to process request: {str(e)}")
            return redirect('profile_view')

    # Fetch student details for display
    student_data = None
    try:
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT 
                    s1.name, s1.admission_number, s1.class, s1.section, s1.roll_number, s1.emis,
                    s2.gender, s2.community, s2.tamil_name, s2.dob, s2.nationality, s2.blood_group, 
                    s2.mother_tongue, s2.caste, s2.religion, s2.place_of_birth, s2.aadhaar, s2.disability,
                    s2.id_mark1, s2.id_mark2, s2.current_class, s2.admission_class, s2.admission_year, s2.admission_date,
                    s3.email, s3.address, s3.contact, s3.alt_contact, s3.country, s3.state, s3.city, s3.pincode,
                    s3.status, s3.house, s3.teacher_ward, s3.rte, s3.sports_quota, s3.prev_school, s3.prev_board,
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
    except Exception as e:
        print(f"DEBUG: Error fetching student data: {e}")

    print(f"DEBUG: Rendering template with profile_picture: {profile_picture}")
    return render(request, "users/profile.html", {
        "student_data": student_data,
        "profile_picture": profile_picture,
        "user_id": user_id
    })





from django.http import HttpResponse
from django.shortcuts import render, redirect
import PIL.Image
import PIL.ImageDraw
import PIL.ImageFont
from io import BytesIO
from django.db import connection
import qrcode
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import os
from django.conf import settings

def generate_id_card(request):
    if "user_id" not in request.session:
        return redirect("/login/")

    user_id = request.session["user_id"]

    # Fetch student data
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT 
                sp1.name, 
                sp1.class, 
                sp1.admission_number, 
                sp3.address
            FROM 
                student_page1 sp1
            JOIN 
                student_page3 sp3 ON sp1.user_id = sp3.user_id
            WHERE 
                sp1.user_id = %s
        """, [user_id])
        student_data = cursor.fetchone()

    if not student_data:
        return render(request, "users/profile.html", {"error": "Student data not found."})

    name, student_class, admission_number, address = student_data

    # Fetch profile picture
    profile_picture = None
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT image_path FROM profile_pics WHERE user_id = %s", [user_id])
            profile_picture_result = cursor.fetchone()
            if profile_picture_result:
                profile_picture_path = os.path.join(settings.MEDIA_ROOT, profile_picture_result[0])
                if os.path.exists(profile_picture_path):
                    profile_picture = PIL.Image.open(profile_picture_path).convert("RGB")
                else:
                    print(f"Profile picture file not found at: {profile_picture_path}")
    except Exception as e:
        print(f"Error fetching profile picture: {e}")

    # Load ID card template
    template_path = "users/static/users/images/id_card.jpg"
    template_image = PIL.Image.open(template_path).convert("RGB")
    draw = PIL.ImageDraw.Draw(template_image)

    # Get image dimensions for centering
    img_width, img_height = template_image.size

    # Place profile picture on the ID card (if available)
    if profile_picture:
        # Resize profile picture to fit the placeholder
        photo_size = (250, 250)
        profile_picture = profile_picture.resize(photo_size, PIL.Image.Resampling.LANCZOS)
        photo_x = (img_width - photo_size[0]) // 2  # Center horizontally
        photo_y = 251
        template_image.paste(profile_picture, (photo_x, photo_y))
        start_y = 569  # Adjusted Y position below the photo if image is present
    else:
        start_y = 569  # Adjusted Y position if no image is present (start earlier)

    # Load fonts with larger sizes
    font_path = os.path.join("users", "static", "users", "fonts", "arial.ttf")
    try:
        title_font = PIL.ImageFont.truetype(font_path, 36)  # For "IDENTITY CARD" text
        name_font = PIL.ImageFont.truetype(font_path, 32)  # For student name
        detail_font = PIL.ImageFont.truetype(font_path, 28)  # For other details
    except Exception as e:
        print(f"Font loading error: {e}")
        title_font = PIL.ImageFont.load_default()
        name_font = PIL.ImageFont.load_default()
        detail_font = PIL.ImageFont.load_default()

    # Function to calculate centered text position (pass img_width as parameter)
    def get_centered_x(text, font, img_width):
        text_width = draw.textlength(text, font=font)
        return (img_width - text_width) / 2

    # Position parameters
    line_spacing = 40  # Space between lines

    # Draw centered text, handle None values by defaulting to empty string
    current_y = start_y
    
    # Name (larger font)
    name_text = f"NAME: {(name or '').upper()}"  # Default to empty string if None
    draw.text((get_centered_x(name_text, name_font, img_width), current_y), 
              name_text, font=name_font, fill="black")
    current_y += line_spacing + 10
    
    # Class
    class_text = f"CLASS: {(student_class or '').upper()}"  # Default to empty string if None
    draw.text((get_centered_x(class_text, detail_font, img_width), current_y), 
              class_text, font=detail_font, fill="black")
    current_y += line_spacing + 10
    
    # Admission Number
    adm_text = f"ADMISSION NO: {(admission_number or '').upper()}"  # Default to empty string if None
    draw.text((get_centered_x(adm_text, detail_font, img_width), current_y), 
              adm_text, font=detail_font, fill="black")
    current_y += line_spacing + 10
    
    # Address (might need to handle multiline if too long)
    addr_text = f"ADDRESS: {(address or '').upper()}"  # Default to empty string if None
    draw.text((get_centered_x(addr_text, detail_font, img_width), current_y), 
              addr_text, font=detail_font, fill="black")

    # Generate QR code
    qr = qrcode.make(f"http://yourdomain.com/id_card/{admission_number or 'unknown'}/")  # Fallback for None
    qr_buffer = BytesIO()
    qr.save(qr_buffer, format="PNG")
    qr_buffer.seek(0)
    qr_image = PIL.Image.open(qr_buffer)

    # Resize QR code
    qr_size = (175, 175)
    qr_image = qr_image.resize(qr_size, PIL.Image.Resampling.LANCZOS)

    # Position QR code at the top center
    qr_x = (img_width - qr_size[0]) // 2  # Center horizontally
    qr_y = 800  # Adjusted to top center as in the attached image
    template_image.paste(qr_image, (qr_x, qr_y))

    # Save image to memory buffer
    id_card_buffer = BytesIO()
    template_image.save(id_card_buffer, format="JPEG")
    id_card_buffer.seek(0)

    # Create PDF
    pdf_buffer = BytesIO()
    c = canvas.Canvas(pdf_buffer, pagesize=letter)

    # Get original dimensions of the ID card
    id_image = PIL.Image.open(id_card_buffer)
    orig_width, orig_height = id_image.size

    # Calculate available space on PDF
    margin = 50
    max_width = 612 - 2 * margin
    max_height = 792 - 2 * margin

    # Calculate scaling factor while maintaining aspect ratio
    scale = min(max_width / orig_width, max_height / orig_height)
    scaled_width = orig_width * scale
    scaled_height = orig_height * scale

    # Center the image on the page
    x_pos = (612 - scaled_width) / 2
    y_pos = (792 - scaled_height) / 2

    # Draw ID card with original aspect ratio
    c.drawInlineImage(id_image, x_pos, y_pos, width=scaled_width, height=scaled_height)

    c.showPage()
    c.save()
    pdf_buffer.seek(0)

    # Return PDF response
    response = HttpResponse(pdf_buffer, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="ID_Card_{admission_number or "unknown"}.pdf"'
    return response



from django.shortcuts import render, redirect
from django.db import connection
import qrcode
from io import BytesIO
import base64
from datetime import datetime


def qr_page(request):
    if "user_id" not in request.session:
        return redirect("/login/")  # Redirect to login if not authenticated

    user_id = request.session["user_id"]  # Get logged-in user's ID

    # Fetch student data from the database using a JOIN for both tables
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT 
                sp1.name, 
                sp1.class, 
                sp1.admission_number, 
                sp3.address
            FROM 
                student_page1 sp1
            JOIN 
                student_page3 sp3 ON sp1.user_id = sp3.user_id
            WHERE 
                sp1.user_id = %s
        """, [user_id])
        student_data = cursor.fetchone()

    if not student_data:
        return render(request, "users/profile.html", {"error": "Student data not found."})

    # Extract the student data
    name, student_class, admission_number, address = student_data

    # Generate QR code for the ID card URL
    qr = qrcode.QRCode(version=1, error_correction=qrcode.constants.ERROR_CORRECT_L,
                       box_size=10, border=4)
    qr.add_data(f"http://yourdomain.com/id_card/{admission_number}/")  # Replace with actual URL
    qr.make(fit=True)

    # Create an in-memory image for the QR code
    img = qr.make_image(fill="black", back_color="white")
    img_io = BytesIO()
    img.save(img_io, 'PNG')
    img_io.seek(0)

    # Convert QR code to base64
    qr_code_base64 = base64.b64encode(img_io.read()).decode('utf-8')

    # Get current date for footer
    current_date = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')


    # Pass data to template
    context = {
        "name": name,
        "student_class": student_class,
        "address": address,
        "admission_number": admission_number,
        "qr_code_image": qr_code_base64,
        "date": current_date
    }

    return render(request, 'users/qr_page.html', context)






from django.http import HttpResponse
from django.shortcuts import render, redirect
import PIL.Image
import PIL.ImageDraw
import PIL.ImageFont
from io import BytesIO
from django.db import connection
import qrcode
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import os
from django.conf import settings

def bulk_id_card(request):
    if "user_id" not in request.session:
        return redirect("/login/")

    user_id = request.session["user_id"]

    if request.method == 'POST':
        student_class = request.POST.get('class')
        section = request.POST.get('section')

        # Fetch students data based on class and section, including user_id for profile picture lookup
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT 
                    sp1.user_id, 
                    sp1.name, 
                    sp1.class, 
                    sp1.admission_number, 
                    sp3.address
                FROM 
                    student_page1 sp1
                JOIN 
                    student_page3 sp3 ON sp1.user_id = sp3.user_id
                WHERE 
                    sp1.class = %s AND sp1.section = %s
            """, [student_class, section])
            students_data = cursor.fetchall()

        if not students_data:
            return render(request, "users/bulk_id_card.html", {"error": "No students found for the selected class and section."})

        # Create PDF buffer to store all ID cards
        pdf_buffer = BytesIO()
        c = canvas.Canvas(pdf_buffer, pagesize=letter)

        for student_data in students_data:
            student_user_id, name, student_class, admission_number, address = student_data

            # Fetch profile picture for the current student
            profile_picture = None
            try:
                with connection.cursor() as cursor:
                    cursor.execute("SELECT image_path FROM profile_pics WHERE user_id = %s", [student_user_id])
                    profile_picture_result = cursor.fetchone()
                    if profile_picture_result:
                        profile_picture_path = os.path.join(settings.MEDIA_ROOT, profile_picture_result[0])
                        if os.path.exists(profile_picture_path):
                            profile_picture = PIL.Image.open(profile_picture_path).convert("RGB")
                        else:
                            print(f"Profile picture file not found at: {profile_picture_path}")
            except Exception as e:
                print(f"Error fetching profile picture for user {student_user_id}: {e}")

            # Load ID card template
            template_path = "users/static/users/images/id_card.jpg"
            template_image = PIL.Image.open(template_path).convert("RGB")
            draw = PIL.ImageDraw.Draw(template_image)

            # Get image dimensions for centering
            img_width, img_height = template_image.size

            # Place profile picture on the ID card (if available)
            if profile_picture:
                # Resize profile picture to fit the placeholder
                photo_size = (250, 250)
                profile_picture = profile_picture.resize(photo_size, PIL.Image.Resampling.LANCZOS)
                photo_x = (img_width - photo_size[0]) // 2  # Center horizontally
                photo_y = 251  # Same Y position as in generate_id_card
                template_image.paste(profile_picture, (photo_x, photo_y))
                start_y = 569  # Adjusted Y position below the photo if image is present
            else:
                start_y = 569  # Adjusted Y position if no image is present (start earlier)

            # Load fonts with larger sizes
            font_path = os.path.join("users", "static", "users", "fonts", "arial.ttf")
            try:
                title_font = PIL.ImageFont.truetype(font_path, 36)  # For "IDENTITY CARD" text
                name_font = PIL.ImageFont.truetype(font_path, 32)  # For student name
                detail_font = PIL.ImageFont.truetype(font_path, 28)  # For other details
            except Exception as e:
                print(f"Font loading error: {e}")
                title_font = PIL.ImageFont.load_default()
                name_font = PIL.ImageFont.load_default()
                detail_font = PIL.ImageFont.load_default()

            # Function to calculate centered text position (pass img_width as parameter)
            def get_centered_x(text, font, img_width):
                text_width = draw.textlength(text, font=font)
                return (img_width - text_width) / 2

            # Position parameters
            line_spacing = 40  # Space between lines

            # Draw centered text, handle None values by defaulting to empty string
            current_y = start_y
            
            # Name (larger font)
            name_text = f"NAME: {(name or '').upper()}"  # Default to empty string if None
            draw.text((get_centered_x(name_text, name_font, img_width), current_y), 
                      name_text, font=name_font, fill="black")
            current_y += line_spacing + 10
            
            # Class
            class_text = f"CLASS: {(student_class or '').upper()}"  # Default to empty string if None
            draw.text((get_centered_x(class_text, detail_font, img_width), current_y), 
                      class_text, font=detail_font, fill="black")
            current_y += line_spacing + 10
            
            # Admission Number
            adm_text = f"ADMISSION NO: {(admission_number or '').upper()}"  # Default to empty string if None
            draw.text((get_centered_x(adm_text, detail_font, img_width), current_y), 
                      adm_text, font=detail_font, fill="black")
            current_y += line_spacing + 10
            
            # Address (might need to handle multiline if too long)
            addr_text = f"ADDRESS: {(address or '').upper()}"  # Default to empty string if None
            draw.text((get_centered_x(addr_text, detail_font, img_width), current_y), 
                      addr_text, font=detail_font, fill="black")

            # Generate QR code
            qr = qrcode.make(f"http://yourdomain.com/id_card/{admission_number or 'unknown'}/")  # Fallback for None
            qr_buffer = BytesIO()
            qr.save(qr_buffer, format="PNG")
            qr_buffer.seek(0)
            qr_image = PIL.Image.open(qr_buffer)

            # Resize QR code
            qr_size = (175, 175)
            qr_image = qr_image.resize(qr_size, PIL.Image.Resampling.LANCZOS)

            # Position QR code at the top center
            qr_x = (img_width - qr_size[0]) // 2  # Center horizontally
            qr_y = 800  # Adjusted to top center as in the attached image
            template_image.paste(qr_image, (qr_x, qr_y))

            # Save image to memory buffer
            id_card_buffer = BytesIO()
            template_image.save(id_card_buffer, format="JPEG")
            id_card_buffer.seek(0)

            # Get original dimensions of the ID card
            id_image = PIL.Image.open(id_card_buffer)
            orig_width, orig_height = id_image.size

            # Calculate available space on PDF
            margin = 50
            max_width = 612 - 2 * margin
            max_height = 792 - 2 * margin

            # Calculate scaling factor while maintaining aspect ratio
            scale = min(max_width / orig_width, max_height / orig_height)
            scaled_width = orig_width * scale
            scaled_height = orig_height * scale

            # Center the image on the page
            x_pos = (612 - scaled_width) / 2
            y_pos = (792 - scaled_height) / 2

            # Draw ID card with original aspect ratio
            c.drawInlineImage(id_image, x_pos, y_pos, width=scaled_width, height=scaled_height)

            c.showPage()

        c.save()
        pdf_buffer.seek(0)

        # Return the generated PDF as an HttpResponse
        response = HttpResponse(pdf_buffer, content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename="bulk_id_cards.pdf"'
        return response

    return render(request, "users/bulk_id_card.html")


def admin_login(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')

        with connection.cursor() as cursor:
            cursor.execute("SELECT id, full_name, email, password FROM admins WHERE email = %s", [email])
            admin = cursor.fetchone()

        if admin and admin[3] == password:
            request.session['admin_id'] = admin[0]
            request.session['admin_name'] = admin[1]
            messages.success(request, 'Login successful!')
            return redirect('admin_page')  # Replace with your dashboard URL
        else:
            messages.error(request, 'Invalid email or password.')

    return render(request, 'users/admin_login.html')

def admin_signup(request):
    if request.method == 'POST':
        full_name = request.POST.get('name')
        email = request.POST.get('email')
        password = request.POST.get('password')

        try:
            with connection.cursor() as cursor:
                cursor.execute(
                    "INSERT INTO admins (full_name, email, password) VALUES (%s, %s, %s)",
                    [full_name, email, password]
                )
            messages.success(request, 'Signup successful! Please login.')
            return redirect('admin_login')
        except Exception as e:
            messages.error(request, 'Error: Email already exists or invalid data.')

    return render(request, 'users/admin_signup.html')

def admin_page(request):
    return render(request, 'users/admin_page.html')





import os
from datetime import datetime
from django.shortcuts import render, redirect
from django.conf import settings
from django.core.files.storage import FileSystemStorage
import uuid
from django.db import connection
from django.contrib import messages

# Upload folder path (adjusted to your project structure)
UPLOAD_DIR = os.path.join(settings.BASE_DIR, 'users', 'static', 'uploads')

# Ensure uploads folder exists
if not os.path.exists(UPLOAD_DIR):
    os.makedirs(UPLOAD_DIR)

# Normalize string function to handle None and special cases
def normalize_value(value):
    if value is None:
        return ''
    return str(value).strip().lower()

# Admin uploads circular
def admin_circular_upload(request):
    if request.method == 'POST':
        title = request.POST.get('title')
        image = request.FILES.get('image')
        target = request.POST.get('target', 'all')
        class_name = request.POST.get('class') if target == 'specific' else None
        section = request.POST.get('section') if target == 'specific' else None

        if title and image:
            # Validate class and section if specific
            if target == 'specific' and (not class_name or not section):
                messages.error(request, 'Please select both class and section for specific target.')
                return redirect('admin_circular_upload')

            # Normalize class and section
            class_name = normalize_value(class_name)
            section = normalize_value(section)

            # Generate a unique filename to avoid conflicts
            filename = f"{uuid.uuid4().hex}_{image.name}"
            fs = FileSystemStorage(location=UPLOAD_DIR, base_url='/static/uploads/')
            try:
                filename = fs.save(filename, image)
                full_path = os.path.join(UPLOAD_DIR, filename)
                if os.path.exists(full_path):
                    print(f"Image saved successfully: {full_path}")
                else:
                    print(f"Image save failed: {full_path}")
                    messages.error(request, 'Failed to save the image.')
                    return redirect('admin_circular_upload')
                image_url = f"/static/uploads/{filename}"  # Use consistent path
                print(f"Generated image_url: {image_url}")
            except Exception as e:
                print(f"Error saving image {filename}: {e}")
                messages.error(request, 'Error saving the image.')
                return redirect('admin_circular_upload')

            # Save circular metadata (title and target) in a unique file
            metadata_file_path = os.path.join(UPLOAD_DIR, f"{filename}.txt")
            try:
                with open(metadata_file_path, 'w') as f:
                    f.write(f"{title}\n{target}")
                    if target == 'specific':
                        f.write(f"\n{class_name}\n{section}")
                print(f"Saved metadata for {filename}: title={title}, target={target}, class={class_name}, section={section}")
            except Exception as e:
                print(f"Error saving metadata for {filename}: {e}")
                messages.error(request, 'Error saving circular metadata.')
                return redirect('admin_circular_upload')

            messages.success(request, 'Circular uploaded successfully.')
            return redirect('admin_circular_upload')

    # Prepare circulars list for display
    circulars = []
    for file in os.listdir(UPLOAD_DIR):
        if file.endswith(('.jpg', '.png', '.jpeg', '.webp', '.gif')):
            full_path = os.path.join(UPLOAD_DIR, file)
            if not os.path.exists(full_path):
                print(f"Image file missing: {full_path}")
                continue

            title_file = f"{file}.txt"
            title_path = os.path.join(UPLOAD_DIR, title_file)
            title = "Untitled"
            target = "All"
            class_name = ""
            section = ""

            if os.path.exists(title_path):
                try:
                    with open(title_path, 'r') as f:
                        lines = f.readlines()
                        title = lines[0].strip() if lines else "Untitled"
                        target = lines[1].strip() if len(lines) > 1 else "All"
                        if target == 'specific' and len(lines) >= 4:
                            class_name = normalize_value(lines[2])
                            section = normalize_value(lines[3])
                            target = f"Class: {class_name.capitalize()}, Section: {section.capitalize()}"
                except Exception as e:
                    print(f"Error reading metadata from {title_path}: {e}")

            try:
                created_at = datetime.datetime.fromtimestamp(os.path.getctime(full_path)).strftime('%Y-%m-%d %H:%M:%S')
                image_url = f"/static/uploads/{file}"  # Consistent path
                print(f"Listing circular: {file}, image_url: {image_url}, full_path: {full_path}")
                circulars.append({
                    'title': title,
                    'image_url': image_url,
                    'date': created_at,
                    'target': target
                })
            except Exception as e:
                print(f"Error processing file {file}: {e}")

    # Sort by newest first
    circulars = sorted(circulars, key=lambda x: x['date'], reverse=True)

    # Fetch classes and sections from student_page1
    with connection.cursor() as cursor:
        cursor.execute("SELECT DISTINCT class FROM student_page1")
        classes = [normalize_value(row[0]) for row in cursor.fetchall()]
        cursor.execute("SELECT DISTINCT section FROM student_page1 WHERE section IS NOT NULL")
        sections = [normalize_value(row[0]) for row in cursor.fetchall()]

    return render(request, 'users/admin_circular_upload.html', {
        'circulars': circulars,
        'classes': classes,
        'sections': sections
    })

# Student view of circulars
def student_circular(request):
    # Get the logged-in user's user_id from session and fetch class/section from student_page1
    student_class = None
    student_section = None
    error_message = None

    if "user_id" not in request.session:
        error_message = "Please log in to view circulars."
        print("No user_id found in session")
    else:
        user_id = request.session['user_id']
        print(f"Session user_id: {user_id}")
        try:
            with connection.cursor() as cursor:
                cursor.execute(
                    "SELECT class, section FROM student_page1 WHERE user_id = %s",
                    [user_id]
                )
                result = cursor.fetchone()
                if result:
                    student_class, student_section = [normalize_value(r) for r in result]
                    print(f"Student user_id={user_id}: class={student_class}, section={student_section}")
                else:
                    error_message = "No class or section found for your account. Please contact the admin."
                    print(f"No student record found for user_id: {user_id}")
        except Exception as e:
            error_message = "Error fetching your class/section. Please try again later."
            print(f"Error fetching student class/section for user_id={user_id}: {e}")

    # Get filter type from POST request (default to 'all')
    filter_type = request.POST.get('filter_type', 'all')
    print(f"Filter type: {filter_type}")

    circulars = []
    for file in os.listdir(UPLOAD_DIR):
        if file.endswith(('.jpg', '.png', '.jpeg', '.webp', '.gif')):
            full_path = os.path.join(UPLOAD_DIR, file)
            if not os.path.exists(full_path):
                print(f"Image file missing in student view: {full_path}")
                continue

            title_file = f"{file}.txt"
            title_path = os.path.join(UPLOAD_DIR, title_file)
            title = "Untitled"
            target = "all"
            class_name = ""
            section = ""

            if os.path.exists(title_path):
                try:
                    with open(title_path, 'r') as f:
                        lines = f.readlines()
                        title = lines[0].strip() if lines else "Untitled"
                        target = lines[1].strip().lower() if len(lines) > 1 else "all"
                        if target == 'specific' and len(lines) >= 4:
                            class_name = normalize_value(lines[2])
                            section = normalize_value(lines[3])
                        print(f"Circular {file}: title={title}, target={target}, class={class_name}, section={section}")
                except Exception as e:
                    print(f"Error reading metadata from {title_path}: {e}")
                    continue

            # Filter circulars based on filter_type
            include_circular = False
            if filter_type == 'all':
                if target == "all" or (
                    target == "specific" and
                    student_class and student_section and
                    class_name == student_class and section == student_section
                ):
                    include_circular = True
            elif filter_type == 'specific':
                if target == "specific" and student_class and student_section and class_name == student_class and section == student_section:
                    include_circular = True

            if include_circular:
                try:
                    created_at = datetime.datetime.fromtimestamp(os.path.getctime(full_path)).strftime('%Y-%m-%d %H:%M:%S')
                    image_url = f"/static/uploads/{file}"  # Consistent path
                    print(f"Included circular: {file}, image_url: {image_url}, full_path: {full_path}")
                    display_target = "All" if target == "all" else f"Class: {class_name.capitalize()}, Section: {section.capitalize()}"
                    circulars.append({
                        'title': title,
                        'image_url': image_url,
                        'date': created_at,
                        'target': display_target
                    })
                except Exception as e:
                    print(f"Error processing file {file}: {e}")

    # Sort by newest first
    circulars = sorted(circulars, key=lambda x: x['date'], reverse=True)
    print(f"Total circulars displayed: {len(circulars)}")

    return render(request, 'users/student_circular.html', {
        'circulars': circulars,
        'student_class': student_class,
        'student_section': student_section,
        'filter_type': filter_type,
        'error_message': error_message
    })

# Teacher uploads circular
def teacher_circular_upload(request):
    if request.method == 'POST':
        title = request.POST.get('title')
        image = request.FILES.get('image')
        class_name = request.POST.get('class')
        section = request.POST.get('section')

        # Validate inputs
        if not title or not image or not class_name or not section:
            messages.error(request, 'Please provide title, image, class, and section.')
            return redirect('teacher_circular_upload')

        # Normalize class and section
        class_name = normalize_value(class_name)
        section = normalize_value(section)

        # Generate a unique filename to avoid conflicts
        filename = f"{uuid.uuid4().hex}_{image.name}"
        fs = FileSystemStorage(location=UPLOAD_DIR, base_url='/static/uploads/')
        try:
            filename = fs.save(filename, image)
            full_path = os.path.join(UPLOAD_DIR, filename)
            if os.path.exists(full_path):
                print(f"Image saved successfully: {full_path}")
            else:
                print(f"Image save failed: {full_path}")
                messages.error(request, 'Failed to save the image.')
                return redirect('teacher_circular_upload')
            image_url = f"/static/uploads/{filename}"  # Consistent path
            print(f"Generated image_url: {image_url}")
        except Exception as e:
            print(f"Error saving image {filename}: {e}")
            messages.error(request, 'Error saving the image.')
            return redirect('teacher_circular_upload')

        # Save circular metadata (title, target, class, section) in a unique file
        metadata_file_path = os.path.join(UPLOAD_DIR, f"{filename}.txt")
        try:
            with open(metadata_file_path, 'w') as f:
                f.write(f"{title}\nspecific\n{class_name}\n{section}")
            print(f"Saved metadata for {filename}: title={title}, target=specific, class={class_name}, section={section}")
        except Exception as e:
            print(f"Error saving metadata for {filename}: {e}")
            messages.error(request, 'Error saving circular metadata.')
            return redirect('teacher_circular_upload')

        messages.success(request, 'Circular uploaded successfully.')
        return redirect('teacher_circular_upload')

    # Prepare circulars list for display
    circulars = []
    for file in os.listdir(UPLOAD_DIR):
        if file.endswith(('.jpg', '.png', '.jpeg', '.webp', '.gif')):
            full_path = os.path.join(UPLOAD_DIR, file)
            if not os.path.exists(full_path):
                print(f"Image file missing: {full_path}")
                continue

            title_file = f"{file}.txt"
            title_path = os.path.join(UPLOAD_DIR, title_file)
            title = "Untitled"
            target = "All"
            class_name = ""
            section = ""

            if os.path.exists(title_path):
                try:
                    with open(title_path, 'r') as f:
                        lines = f.readlines()
                        title = lines[0].strip() if lines else "Untitled"
                        target = lines[1].strip() if len(lines) > 1 else "All"
                        if target == 'specific' and len(lines) >= 4:
                            class_name = normalize_value(lines[2])
                            section = normalize_value(lines[3])
                            target = f"Class: {class_name.capitalize()}, Section: {section.capitalize()}"
                except Exception as e:
                    print(f"Error reading title from {title_path}: {e}")

            try:
                created_at = datetime.datetime.fromtimestamp(os.path.getctime(full_path)).strftime('%Y-%m-%d %H:%M:%S')
                image_url = f"/static/uploads/{file}"  # Consistent path
                print(f"Listing circular: {file}, image_url: {image_url}, full_path: {full_path}")
                circulars.append({
                    'title': title,
                    'image_url': image_url,
                    'date': created_at,
                    'target': target
                })
            except Exception as e:
                print(f"Error processing file {file}: {e}")

    # Sort by newest first
    circulars = sorted(circulars, key=lambda x: x['date'], reverse=True)

    # Fetch classes and sections from student_page1
    with connection.cursor() as cursor:
        cursor.execute("SELECT DISTINCT class FROM student_page1")
        classes = [normalize_value(row[0]) for row in cursor.fetchall()]
        cursor.execute("SELECT DISTINCT section FROM student_page1 WHERE section IS NOT NULL")
        sections = [normalize_value(row[0]) for row in cursor.fetchall()]

    return render(request, 'users/teacher_circular_upload.html', {
        'circulars': circulars,
        'classes': classes,
        'sections': sections
    })



from datetime import datetime  # Add this import at the top of your file
import io
from django.shortcuts import render, redirect
from django.contrib import messages
from django.db import connection
from django.http import HttpResponse
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors

def student_leave(request):
    """Handle student leave request submission and viewing."""
    if "user_id" not in request.session:
        messages.error(request, "Please log in to access the student portal.")
        return redirect("/login/")

    user_id = request.session["user_id"]
    
    if request.method == "POST":
        try:
            form_data = {
                "student_name": request.POST.get("student_name", "").strip(),
                "reg_number": request.POST.get("reg_number", "").strip(),
                "class_number": request.POST.get("class", "").strip(),
                "leave_reason": request.POST.get("leave_reason", "").strip(),
                "leave_start_date": request.POST.get("leave_start_date", ""),
                "leave_end_date": request.POST.get("leave_end_date", ""),
                "leave_duration": request.POST.get("leave_duration", ""),
                "half_day_type": request.POST.get("half_day_type", "")
            }


            required_fields = ["student_name", "reg_number", "class_number", "leave_reason", 
                             "leave_start_date", "leave_end_date", "leave_duration"]
            missing_fields = [field for field in required_fields if not form_data[field]]
            if missing_fields:
                messages.error(request, f"Missing required fields: {', '.join(missing_fields)}")
                return redirect("student_leave")
            
            if form_data["leave_duration"] not in ["full", "half"]:
                messages.error(request, "Invalid leave duration.")
                return redirect("student_leave")
                
            if form_data["leave_duration"] == "half" and not form_data["half_day_type"]:
                messages.error(request, "Please select half day type for half-day leave.")
                return redirect("student_leave")

            try:
                start_date = datetime.datetime.strptime(form_data["leave_start_date"], "%Y-%m-%d")
                end_date = datetime.datetime.strptime(form_data["leave_end_date"], "%Y-%m-%d")
                if start_date > end_date:
                    messages.error(request, "End date must be on or after start date.")
                    return redirect("student_leave")
            except ValueError:
                messages.error(request, "Invalid date format.")
                return redirect("student_leave")

            with connection.cursor() as cursor:
                cursor.execute("""
                    INSERT INTO student_leave_requests 
                    (user_id, student_name, reg_number, class_number, leave_reason,
                    leave_start_date, leave_end_date, leave_duration, half_day_type, status)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """, [user_id, form_data["student_name"], form_data["reg_number"], 
                      form_data["class_number"], form_data["leave_reason"], 
                      form_data["leave_start_date"], form_data["leave_end_date"],
                      form_data["leave_duration"], 
                      form_data["half_day_type"] if form_data["leave_duration"] == "half" else None,
                      "Pending"])
                connection.commit()
            messages.success(request, "Leave request submitted successfully.")
        except Exception as e:
            connection.rollback()
            messages.error(request, f"Error submitting leave request: {str(e)}")
        return redirect("student_leave")

    # Fetch leave requests for this student
    leave_requests = []
    with connection.cursor() as cursor:
        try:
            cursor.execute("""
                SELECT id, student_name, reg_number, class_number, leave_reason, 
                leave_start_date, leave_end_date, leave_duration, half_day_type, status
                FROM student_leave_requests WHERE user_id = %s
                ORDER BY leave_start_date DESC
            """, [user_id])
            leave_requests = cursor.fetchall()
        except Exception as e:
            messages.error(request, f"Error fetching leave requests: {str(e)}")

    return render(request, "users/student_leave.html", {
        "leave_requests": leave_requests
    })

def download_leave_pdf(request):
    """Generate and download leave request PDF."""
    if "user_id" not in request.session:
        messages.error(request, "Please log in to access this page.")
        return redirect("/login/")

    user_id = request.session["user_id"]
    
    if request.method == "POST":
        try:
            leave_id = request.POST["leave_id"]
            with connection.cursor() as cursor:
                cursor.execute("""
                    SELECT student_name, reg_number, class_number, leave_reason, leave_start_date,
                    leave_end_date, leave_duration, half_day_type, status
                    FROM student_leave_requests WHERE id = %s AND user_id = %s
                """, [leave_id, user_id])
                record = cursor.fetchone()
            if not record:
                messages.error(request, "Leave request not found.")
                return redirect("student_leave")

            buffer = io.BytesIO()
            doc = SimpleDocTemplate(buffer, pagesize=letter)
            elements = []
            styles = getSampleStyleSheet()
            elements.append(Paragraph("Leave Request Details", styles["Title"]))
            data = [
                ["Field", "Details"],
                ["Student Name", record[0]],
                ["Registration Number", record[1]],
                ["Class", record[2]],
                ["Leave Reason", record[3]],
                ["Start Date", str(record[4])],
                ["End Date", str(record[5])],
                ["Duration", f"{record[6]}{' (' + record[7] + ')' if record[6] == 'half' and record[7] else ''}"],
                ["Status", record[8]]
            ]
            table = Table(data)
            table.setStyle(TableStyle([
                ("BACKGROUND", (0, 0), (-1, 0), colors.grey),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
                ("ALIGN", (0, 0), (-1, -1), "LEFT"),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, 0), 14),
                ("BOTTOMPADDING", (0, 0), (-1, 0), 12),
                ("BACKGROUND", (0, 1), (-1, -1), colors.beige),
                ("GRID", (0, 0), (-1, -1), 1, colors.black)
            ]))
            elements.append(table)
            doc.build(elements)
            buffer.seek(0)
            return HttpResponse(buffer, content_type="application/pdf", headers={
                "Content-Disposition": f"attachment;filename=leave_request_{leave_id}.pdf"
            })
        except Exception as e:
            messages.error(request, f"Error generating PDF: {str(e)}")
            return redirect("student_leave")
    return redirect("student_leave")





from django.shortcuts import render, redirect
from django.contrib import messages
from django.db import connection

def admin_accept_portal(request):
    if not request.session.get('admin_id'):
        messages.error(request, 'You must be logged in to access this page.')
        return redirect('admin_login')  # Redirect to login page if not logged in

    if request.method == 'POST':
        action = request.POST.get('action')
        leave_id = request.POST.get('leave_id')

        if action and leave_id:
            # Update leave status based on action
            if action == 'approve':
                new_status = 'Approved'
            elif action == 'reject':
                new_status = 'Rejected'
            else:
                messages.error(request, 'Invalid action')
                return redirect('admin_accept_portal')  # Redirect back to the portal if action is invalid

            with connection.cursor() as cursor:
                # Update the leave request status
                cursor.execute("""
                    UPDATE student_leave_requests
                    SET status = %s
                    WHERE id = %s
                """, [new_status, leave_id])

            messages.success(request, f'Leave request {new_status.lower()} successfully.')
        else:
            messages.error(request, 'Leave ID or action missing.')

        return redirect('admin_accept_portal')  # Redirect back to the leave requests page

    # Fetch leave requests to display on the page
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT id, student_name, reg_number, class_number, leave_reason, leave_start_date, leave_end_date, leave_duration, status
            FROM student_leave_requests
            WHERE status = 'Pending'
        """)
        leave_requests = cursor.fetchall()

    return render(request, 'users/admin_accept_portal.html', {'leave_requests': leave_requests})




from django.shortcuts import render, redirect
from django.contrib import messages
from django.db import connection

def teacher_accept_portal(request):
    if not request.session.get('teacher_id'):
        messages.error(request, 'You must be logged in to access this page.')
        return redirect('teacher_login')  # Redirect to login page if not logged in

    if request.method == 'POST':
        action = request.POST.get('action')
        leave_id = request.POST.get('leave_id')

        if action and leave_id:
            # Update leave status based on action
            if action == 'approve':
                new_status = 'Approved'
            elif action == 'reject':
                new_status = 'Rejected'
            else:
                messages.error(request, 'Invalid action')
                return redirect('admin_accept_portal')  # Redirect back to the portal if action is invalid

            with connection.cursor() as cursor:
                # Update the leave request status
                cursor.execute("""
                    UPDATE student_leave_requests
                    SET status = %s
                    WHERE id = %s
                """, [new_status, leave_id])

            messages.success(request, f'Leave request {new_status.lower()} successfully.')
        else:
            messages.error(request, 'Leave ID or action missing.')

        return redirect('teacher_accept_portal')  # Redirect back to the leave requests page

    # Fetch leave requests to display on the page
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT id, student_name, reg_number, class_number, leave_reason, leave_start_date, leave_end_date, leave_duration, status
            FROM student_leave_requests
            WHERE status = 'Pending'
        """)
        leave_requests = cursor.fetchall()

    return render(request, 'users/teacher_accept_portal.html', {'leave_requests': leave_requests})







import os
import uuid
from django.shortcuts import render, redirect
from django.conf import settings
from django.contrib import messages
from django.db import connection
from datetime import datetime
from django.http import FileResponse, Http404
from django.views.decorators.csrf import csrf_exempt
from django.core.validators import FileExtensionValidator
from django.core.exceptions import ValidationError
from django.core.files.storage import FileSystemStorage

# Admin uploads study material
@csrf_exempt
def admin_study_materials_upload(request):
    if not request.session.get('admin_id'):
        messages.error(request, 'You must be logged in to access this page.')
        return redirect('admin_login')

    # Fetch distinct classes and sections for dropdowns
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT DISTINCT class FROM student_page1")
            classes = [row[0] for row in cursor.fetchall()]
            cursor.execute("SELECT DISTINCT section FROM student_page1 WHERE section IS NOT NULL")
            sections = [row[0] for row in cursor.fetchall()]
    except Exception as e:
        messages.error(request, f"Error fetching classes/sections: {str(e)}")
        classes = []
        sections = []

    if request.method == 'POST':
        title = request.POST.get("title")
        uploaded_file = request.FILES.get("file")
        selected_class = request.POST.get("class")
        selected_section = request.POST.get("section")

        if not all([title, uploaded_file, selected_class, selected_section]):
            messages.error(request, "Title, file, class, and section are required.")
            return redirect("admin_study_materials_upload")

        validator = FileExtensionValidator(allowed_extensions=['pdf'])
        try:
            validator(uploaded_file)
        except ValidationError:
            messages.error(request, "Only PDF files are allowed.")
            return redirect("admin_study_materials_upload")

        filename = f"{uuid.uuid4().hex}_{uploaded_file.name}"
        file_path = os.path.join(settings.MEDIA_ROOT, 'study_materials', filename)

        os.makedirs(os.path.dirname(file_path), exist_ok=True)

        try:
            with open(file_path, 'wb+') as f:
                for chunk in uploaded_file.chunks():
                    f.write(chunk)
        except Exception as e:
            messages.error(request, f"Error saving file: {str(e)}")
            return redirect("admin_study_materials_upload")

        try:
            with connection.cursor() as cursor:
                cursor.execute(
                    """
                    INSERT INTO study_materials (title, file_path, upload_date, class, section)
                    VALUES (%s, %s, %s, %s, %s)
                    """,
                    [title, f"study_materials/{filename}", datetime.datetime.now(), selected_class, selected_section]
                )
            messages.success(request, "Study material uploaded successfully!")
        except Exception as e:
            messages.error(request, f"Error saving to database: {str(e)}")
            if os.path.exists(file_path):
                os.remove(file_path)
            return redirect("admin_study_materials_upload")

        return redirect("admin_study_materials_upload")

    # Get filter values
    selected_class = request.GET.get('class', '')
    selected_section = request.GET.get('section', '')

    try:
        with connection.cursor() as cursor:
            query = """
                SELECT title, file_path, upload_date, class, section
                FROM study_materials
                {where_clause}
                ORDER BY upload_date DESC
            """
            params = []
            where_clause = ""
            if selected_class and selected_section:
                where_clause = "WHERE class = %s AND section = %s"
                params = [selected_class, selected_section]

            cursor.execute(query.format(where_clause=where_clause), params)
            study_materials = [
                {
                    "title": r[0],
                    "file_path": r[1],
                    "upload_date": r[2],
                    "class": r[3],
                    "section": r[4]
                } for r in cursor.fetchall()
            ]
    except Exception as e:
        messages.error(request, f"Error retrieving study materials: {str(e)}")
        study_materials = []

    return render(request, "users/admin_study_materials.html", {
        "study_materials": study_materials,
        "media_url": settings.MEDIA_URL,
        "classes": classes,
        "sections": sections,
        "selected_class": selected_class,
        "selected_section": selected_section
    })

# Teacher uploads study material
@csrf_exempt
def teacher_study_materials_upload(request):
    if not request.session.get('teacher_id'):
        messages.error(request, 'You must be logged in to access this page.')
        return redirect('teacher_login')

    # Fetch distinct classes and sections for dropdowns
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT DISTINCT class FROM student_page1")
            classes = [row[0] for row in cursor.fetchall()]
            cursor.execute("SELECT DISTINCT section FROM student_page1 WHERE section IS NOT NULL")
            sections = [row[0] for row in cursor.fetchall()]
    except Exception as e:
        messages.error(request, f"Error fetching classes/sections: {str(e)}")
        classes = []
        sections = []

    if request.method == 'POST':
        title = request.POST.get("title")
        uploaded_file = request.FILES.get("file")
        selected_class = request.POST.get("class")
        selected_section = request.POST.get("section")

        if not all([title, uploaded_file, selected_class, selected_section]):
            messages.error(request, "Title, file, class, and section are required.")
            return redirect("teacher_study_materials_upload")

        validator = FileExtensionValidator(allowed_extensions=['pdf'])
        try:
            validator(uploaded_file)
        except ValidationError:
            messages.error(request, "Only PDF files are allowed.")
            return redirect("teacher_study_materials_upload")

        filename = f"{uuid.uuid4().hex}_{uploaded_file.name}"
        file_path = os.path.join(settings.MEDIA_ROOT, 'study_materials', filename)

        os.makedirs(os.path.dirname(file_path), exist_ok=True)

        try:
            with open(file_path, 'wb+') as f:
                for chunk in uploaded_file.chunks():
                    f.write(chunk)
        except Exception as e:
            messages.error(request, f"Error saving file: {str(e)}")
            return redirect("teacher_study_materials_upload")

        try:
            with connection.cursor() as cursor:
                cursor.execute(
                    """
                    INSERT INTO study_materials (title, file_path, upload_date, class, section)
                    VALUES (%s, %s, %s, %s, %s)
                    """,
                    [title, f"study_materials/{filename}", datetime.datetime.now(), selected_class, selected_section]
                )
            messages.success(request, "Study material uploaded successfully!")
        except Exception as e:
            messages.error(request, f"Error saving to database: {str(e)}")
            if os.path.exists(file_path):
                os.remove(file_path)
            return redirect("teacher_study_materials_upload")

        return redirect("teacher_study_materials_upload")

    # Get filter values
    selected_class = request.GET.get('class', '')
    selected_section = request.GET.get('section', '')

    try:
        with connection.cursor() as cursor:
            query = """
                SELECT title, file_path, upload_date, class, section
                FROM study_materials
                {where_clause}
                ORDER BY upload_date DESC
            """
            params = []
            where_clause = ""
            if selected_class and selected_section:
                where_clause = "WHERE class = %s AND section = %s"
                params = [selected_class, selected_section]

            cursor.execute(query.format(where_clause=where_clause), params)
            study_materials = [
                {
                    "title": r[0],
                    "file_path": r[1],
                    "upload_date": r[2],
                    "class": r[3],
                    "section": r[4]
                } for r in cursor.fetchall()
            ]
    except Exception as e:
        messages.error(request, f"Error retrieving study materials: {str(e)}")
        study_materials = []

    return render(request, "users/teacher_study_materials.html", {
        "study_materials": study_materials,
        "media_url": settings.MEDIA_URL,
        "classes": classes,
        "sections": sections,
        "selected_class": selected_class,
        "selected_section": selected_section
    })

# Display study materials to students
def study_materials(request):
    if "user_id" not in request.session:
        messages.error(request, "Please log in to access the student portal.")
        return redirect("/login/")

    user_id = request.session["user_id"]
    student_class = None
    student_section = None

    # Fetch student's class and section
    try:
        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT class, section FROM student_page1 WHERE user_id = %s",
                [user_id]
            )
            result = cursor.fetchone()
            if result:
                student_class, student_section = result
            else:
                messages.error(request, "No class or section found for your account. Please contact the admin.")
                return redirect("/homework/")
    except Exception as e:
        messages.error(request, f"Error fetching class/section: {str(e)}")
        return redirect("/homework/")

    try:
        with connection.cursor() as cursor:
            query = """
                SELECT title, file_path, upload_date, class, section
                FROM study_materials
                WHERE class = %s AND section = %s
                ORDER BY upload_date DESC
            """
            cursor.execute(query, [student_class, student_section])
            study_materials = [
                {
                    "title": r[0],
                    "file_path": r[1],
                    "upload_date": r[2],
                    "class": r[3],
                    "section": r[4]
                } for r in cursor.fetchall()
            ]
    except Exception as e:
        messages.error(request, f"Error retrieving study materials: {str(e)}")
        study_materials = []

    return render(request, "users/study_materials.html", {
        "study_materials": study_materials,
        "media_url": settings.MEDIA_URL,
        "student_class": student_class,
        "student_section": student_section
    })

# Serve PDF files
def serve_pdf(request, file_path):
    full_path = os.path.join(settings.MEDIA_ROOT, file_path.lstrip('/media/'))
    if not os.path.exists(full_path):
        raise Http404("File not found")
    
    try:
        response = FileResponse(open(full_path, 'rb'), content_type='application/pdf')
        if request.GET.get('download') == 'true':
            response['Content-Disposition'] = f'attachment; filename="{os.path.basename(full_path)}"'
        return response
    except Exception as e:
        raise Http404(f"Error serving file: {str(e)}")

# Student homework submission
import os
import uuid
from django.shortcuts import render, redirect
from django.conf import settings
from django.core.files.storage import FileSystemStorage
from django.db import connection
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt
from django.core.validators import FileExtensionValidator
from django.core.exceptions import ValidationError

# Student homework submission view
def homework_view(request):
    if "user_id" not in request.session:
        messages.error(request, "Please log in to access the student portal.")
        return redirect("/login/")

    user_id = request.session["user_id"]
    student_class = None
    student_section = None

    # Fetch student's class and section
    try:
        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT class, section FROM student_page1 WHERE user_id = %s",
                [user_id]
            )
            result = cursor.fetchone()
            if result:
                student_class, student_section = result
            else:
                messages.error(request, "No class or section found for your account. Please contact the admin.")
                return redirect("/homework/")
    except Exception as e:
        messages.error(request, f"Error fetching class/section: {str(e)}")
        return redirect("/homework/")

    if request.method == "POST":
        title = request.POST.get("title")
        submission_date = request.POST.get("submission_date")
        uploaded_file = request.FILES.get("file")

        if not all([title, submission_date, uploaded_file]):
            messages.error(request, "All fields are required.")
            return redirect("/homework/")

        # Validate file is a PDF
        validator = FileExtensionValidator(allowed_extensions=['pdf'])
        try:
            validator(uploaded_file)
        except ValidationError:
            messages.error(request, "Only PDF files are allowed.")
            return redirect("/homework/")

        try:
            # Save file with unique filename
            fs = FileSystemStorage(location=os.path.join(settings.MEDIA_ROOT, 'uploads'))
            filename = f"{uuid.uuid4().hex}_{uploaded_file.name}"
            filename = fs.save(filename, uploaded_file)
            file_path = f"uploads/{filename}"

            with connection.cursor() as cursor:
                cursor.execute(
                    """
                    INSERT INTO homework (user_id, title, submission_date, file_path, class, section)
                    VALUES (%s, %s, %s, %s, %s, %s)
                    """,
                    [user_id, title, submission_date, file_path, student_class, student_section]
                )
            messages.success(request, "Homework submitted successfully!")
        except Exception as e:
            messages.error(request, f"Error submitting homework: {str(e)}")
        return redirect("/homework/")

    try:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT h.title, h.submission_date, h.file_path
                FROM homework h
                WHERE h.user_id = %s
                ORDER BY h.submission_date DESC
                """,
                [user_id]
            )
            homework_list = [
                {"title": r[0], "submission_date": r[1], "file_path": r[2]}
                for r in cursor.fetchall()
            ]
    except Exception as e:
        messages.error(request, f"Error retrieving homework: {str(e)}")
        homework_list = []

    return render(request, "users/homework.html", {
        "homework_list": homework_list,
        "student_class": student_class,
        "student_section": student_section
    })

# Admin homework panel
@csrf_exempt
def admin_homework_panel(request):
    if not request.session.get('admin_id'):
        messages.error(request, 'You must be logged in to access this page.')
        return redirect('admin_login')

    # Fetch distinct classes and sections
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT DISTINCT class FROM student_page1")
            classes = [row[0] for row in cursor.fetchall()]
            cursor.execute("SELECT DISTINCT section FROM student_page1 WHERE section IS NOT NULL")
            sections = [row[0] for row in cursor.fetchall()]
    except Exception as e:
        messages.error(request, f"Error fetching classes/sections: {str(e)}")
        classes = []
        sections = []

    # Get filter values
    selected_class = request.POST.get('class', '')
    selected_section = request.POST.get('section', '')

    try:
        with connection.cursor() as cursor:
            query = """
                SELECT h.user_id, h.title, h.submission_date, h.file_path, h.class, h.section, s.name
                FROM homework h
                JOIN student_page1 s ON h.user_id = s.user_id
                {where_clause}
                ORDER BY h.submission_date DESC
            """
            params = []
            where_clause = ""
            if selected_class and selected_section:
                where_clause = "WHERE h.class = %s AND h.section = %s"
                params = [selected_class, selected_section]

            cursor.execute(query.format(where_clause=where_clause), params)
            homework_list = [
                {
                    "user_id": r[0],
                    "title": r[1],
                    "submission_date": r[2],
                    "file_path": r[3],
                    "class": r[4],
                    "section": r[5],
                    "student_name": r[6]
                } for r in cursor.fetchall()
            ]
    except Exception as e:
        messages.error(request, f"Error retrieving homework submissions: {str(e)}")
        homework_list = []

    return render(request, "users/admin_homework_panel.html", {
        "homework_list": homework_list,
        "media_url": settings.MEDIA_URL,
        "classes": classes,
        "sections": sections,
        "selected_class": selected_class,
        "selected_section": selected_section
    })

# Teacher homework panel
@csrf_exempt
def teacher_homework_panel(request):
    if not request.session.get('teacher_id'):
        messages.error(request, 'You must be logged in to access this page.')
        return redirect('teacher_login')

    # Fetch distinct classes and sections
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT DISTINCT class FROM student_page1")
            classes = [row[0] for row in cursor.fetchall()]
            cursor.execute("SELECT DISTINCT section FROM student_page1 WHERE section IS NOT NULL")
            sections = [row[0] for row in cursor.fetchall()]
    except Exception as e:
        messages.error(request, f"Error fetching classes/sections: {str(e)}")
        classes = []
        sections = []

    # Get filter values
    selected_class = request.POST.get('class', '')
    selected_section = request.POST.get('section', '')

    try:
        with connection.cursor() as cursor:
            query = """
                SELECT h.user_id, h.title, h.submission_date, h.file_path, h.class, h.section, s.name
                FROM homework h
                JOIN student_page1 s ON h.user_id = s.user_id
                {where_clause}
                ORDER BY h.submission_date DESC
            """
            params = []
            where_clause = ""
            if selected_class and selected_section:
                where_clause = "WHERE h.class = %s AND h.section = %s"
                params = [selected_class, selected_section]

            cursor.execute(query.format(where_clause=where_clause), params)
            homework_list = [
                {
                    "user_id": r[0],
                    "title": r[1],
                    "submission_date": r[2],
                    "file_path": r[3],
                    "class": r[4],
                    "section": r[5],
                    "student_name": r[6]
                } for r in cursor.fetchall()
            ]
    except Exception as e:
        messages.error(request, f"Error retrieving homework submissions: {str(e)}")
        homework_list = []

    return render(request, "users/teacher_homework_panel.html", {
        "homework_list": homework_list,
        "media_url": settings.MEDIA_URL,
        "classes": classes,
        "sections": sections,
        "selected_class": selected_class,
        "selected_section": selected_section
    })

def teacher_view(request):
    return render(request, "users/teacher.html")

def fees(request):
    return render(request, "users/fees.html")

def mark_view(request):
    return render(request, "users/mark.html")











from django.shortcuts import render, redirect
from django.contrib import messages
from django.db import connection

def view_edit_class(request):
    if not request.session.get('admin_id'):
        messages.error(request, 'You must be logged in to access this page.')
        return redirect('admin_login')

    admin_id = request.session['admin_id']

    # Fetch all class-section pairs from admin_student_classes for current admin
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT id, class, section 
            FROM admin_student_classes 
            WHERE admin_id = %s
            ORDER BY class DESC, section DESC
        """, [admin_id])
        classes = cursor.fetchall()

    # Format as "class-section" for display
    class_list = [{'id': row[0], 'class_name': f"{row[1]}-{row[2]}"} for row in classes]

    return render(request, 'users/view_edit_class.html', {
        'classes': class_list,
        'total_classes': len(class_list)
    })

def add_class(request):
    if not request.session.get('admin_id'):
        messages.error(request, 'You must be logged in to access this page.')
        return redirect('admin_login')

    admin_id = request.session['admin_id']

    if request.method == 'POST':
        class_name = request.POST.get('class_name')
        if class_name:
            try:
                class_part, section = class_name.split('-')
                
                with connection.cursor() as cursor:
                    # Check if this exact class-section combo already exists for this admin
                    cursor.execute("""
                        SELECT COUNT(*) FROM admin_student_classes
                        WHERE admin_id = %s AND class = %s AND section = %s
                    """, [admin_id, class_part, section])
                    exists = cursor.fetchone()[0]

                    if exists:
                        messages.error(request, f'You already created class {class_name}.')
                    else:
                        # Insert new class-section for this admin
                        cursor.execute("""
                            INSERT INTO admin_student_classes (admin_id, class, section)
                            VALUES (%s, %s, %s)
                        """, [admin_id, class_part, section])
                        
                        messages.success(request, f'Class {class_name} added successfully.')
                        return redirect('view_edit_class')
                        
            except ValueError:
                messages.error(request, 'Class name must be in format "Class-Section" (e.g., 2-A).')
            except Exception as e:
                messages.error(request, f'Error adding class: {str(e)}')
        else:
            messages.error(request, 'Class name cannot be empty.')
    
    return render(request, 'users/add_update_class.html', {'title': 'Add New Class'})

def update_class(request, class_id):
    if not request.session.get('admin_id'):
        messages.error(request, 'You must be logged in to access this page.')
        return redirect('admin_login')

    admin_id = request.session['admin_id']

    # Fetch the class-section pair from admin_student_classes
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT id, class, section 
            FROM admin_student_classes 
            WHERE id = %s AND admin_id = %s
        """, [class_id, admin_id])
        class_data = cursor.fetchone()
        if not class_data:
            messages.error(request, 'Class not found or you don\'t have permission.')
            return redirect('view_edit_class')

    if request.method == 'POST':
        new_class_name = request.POST.get('class_name')
        if new_class_name:
            try:
                new_class, new_section = new_class_name.split('-')
                with connection.cursor() as cursor:
                    # Check if the new class-section combo already exists for this admin
                    cursor.execute("""
                        SELECT COUNT(*) FROM admin_student_classes
                        WHERE admin_id = %s AND class = %s AND section = %s AND id != %s
                    """, [admin_id, new_class, new_section, class_id])
                    exists = cursor.fetchone()[0]

                    if exists:
                        messages.error(request, f'You already have class {new_class_name}.')
                    else:
                        # Update the record in admin_student_classes
                        cursor.execute("""
                            UPDATE admin_student_classes
                            SET class = %s, section = %s
                            WHERE id = %s AND admin_id = %s
                        """, [new_class, new_section, class_id, admin_id])
                        messages.success(request, f'Class updated to {new_class_name} successfully.')
                        return redirect('view_edit_class')
            except ValueError:
                messages.error(request, 'Class name must be in format "Class-Section" (e.g., 2-A).')
            except Exception as e:
                messages.error(request, f'Error updating class: {str(e)}')
        else:
            messages.error(request, 'Class name cannot be empty.')
    return render(request, 'users/add_update_class.html', {
        'title': 'Update Class',
        'class_name': f"{class_data[1]}-{class_data[2]}"
    })

def delete_class(request, class_id):
    if not request.session.get('admin_id'):
        messages.error(request, 'You must be logged in to access this page.')
        return redirect('admin_login')

    admin_id = request.session['admin_id']

    try:
        with connection.cursor() as cursor:
            # Delete the record from admin_student_classes
            cursor.execute("""
                DELETE FROM admin_student_classes 
                WHERE id = %s AND admin_id = %s
            """, [class_id, admin_id])
        messages.success(request, 'Class deleted successfully.')
    except Exception as e:
        messages.error(request, f'Error deleting class: {str(e)}')
    return redirect('view_edit_class')







from django.shortcuts import render, redirect
from django.contrib import messages
from django.db import connection

def student_info(request):
    if not request.session.get('admin_id'):
        messages.error(request, 'You must be logged in to access this page.')
        return redirect('admin_login')

    # Get filter parameters
    class_filter = request.GET.get('class', 'All')
    section_filter = request.GET.get('section', 'All')
    gender_filter = request.GET.get('gender', 'All')

    with connection.cursor() as cursor:
        # Get all unique class-section combinations
        cursor.execute("""
            SELECT DISTINCT class, section 
            FROM student_page1 
            ORDER BY class, section
        """)
        class_sections = cursor.fetchall()

        # Get total count of students
        cursor.execute("SELECT COUNT(*) FROM student_page1")
        total_students = cursor.fetchone()[0]

        # Get student data with filters, including profile picture path
        query = """
            SELECT sp1.id, sp1.name, sp1.admission_number, sp1.class, sp1.section, sp1.roll_number, sp2.gender, pp.image_path
            FROM student_page1 sp1
            LEFT JOIN student_page2 sp2 ON sp1.user_id = sp2.user_id
            LEFT JOIN profile_pics pp ON sp1.user_id = pp.user_id
            WHERE 1=1
        """
        params = []
        
        if class_filter != 'All':
            query += " AND sp1.class = %s"
            params.append(class_filter)
        if section_filter != 'All':
            query += " AND sp1.section = %s"
            params.append(section_filter)
        if gender_filter != 'All':
            query += " AND sp2.gender = %s"
            params.append(gender_filter)
        
        query += " ORDER BY sp1.class, sp1.section, sp1.name"
        cursor.execute(query, params)
        students = cursor.fetchall()

        # Get gender statistics for each class-section
        gender_stats_query = """
            SELECT sp1.class, sp1.section, 
                   COUNT(*) as total,
                   SUM(CASE WHEN sp2.gender = 'Male' THEN 1 ELSE 0 END) as male_count,
                   SUM(CASE WHEN sp2.gender = 'Female' THEN 1 ELSE 0 END) as female_count
            FROM student_page1 sp1
            LEFT JOIN student_page2 sp2 ON sp1.user_id = sp2.user_id
            GROUP BY sp1.class, sp1.section
            ORDER BY sp1.class, sp1.section
        """
        cursor.execute(gender_stats_query)
        gender_stats = cursor.fetchall()
        
        # Convert to dictionary for easy access
        gender_stats_dict = {}
        for stat in gender_stats:
            key = f"{stat[0]}-{stat[1]}"
            gender_stats_dict[key] = {
                'total': stat[2],
                'male': stat[3],
                'female': stat[4]
            }

    # Organize students by class-section
    class_section_groups = {}
    for student in students:
        class_section = f"{student[3]}-{student[4]}"
        if class_section not in class_section_groups:
            class_section_groups[class_section] = {
                'count': 0,
                'male_count': 0,
                'female_count': 0,
                'students': []
            }
        class_section_groups[class_section]['count'] += 1
        if student[6] == 'Male':
            class_section_groups[class_section]['male_count'] += 1
        elif student[6] == 'Female':
            class_section_groups[class_section]['female_count'] += 1
            
        class_section_groups[class_section]['students'].append({
            'id': student[0],
            'name': student[1],
            'admission_number': student[2],
            'class': student[3],
            'section': student[4],
            'roll_number': student[5],
            'gender': student[6],
            'image_path': student[7]  # Add image path to student data
        })

    context = {
        'class_section_groups': class_section_groups,
        'total_students': total_students,
        'class_options': sorted(list(set([cs[0] for cs in class_sections]))) + ['All'],
        'section_options': sorted(list(set([cs[1] for cs in class_sections]))) + ['All'],
        'gender_options': ['All', 'Male', 'Female'],
        'selected_class': class_filter,
        'selected_section': section_filter,
        'selected_gender': gender_filter,
        'gender_stats': gender_stats_dict
    }

    return render(request, 'users/student_info.html', context)


from django.contrib import messages
from django.db import connection
from django.shortcuts import render, redirect

def add_student(request):
    if not request.session.get('admin_id'):
        messages.error(request, 'You must be logged in to access this page.')
        return redirect('admin_login')

    if request.method == 'POST':
        try:
            # Required fields
            name = request.POST.get('name', '').strip()
            admission_number = request.POST.get('admission_number', '').strip()
            class_section = request.POST.get('class_section', '').strip()
            roll_number = request.POST.get('roll_number', '').strip()
            emis = request.POST.get('emis', '').strip()
            email = request.POST.get('email', '').strip()

            # Validate required fields
            if not all([name, admission_number, class_section, roll_number, emis, email]):
                missing = [field for field, value in [
                    ('name', name),
                    ('admission_number', admission_number),
                    ('class_section', class_section),
                    ('roll_number', roll_number),
                    ('emis', emis),
                    ('email', email)
                ] if not value]
                messages.error(request, f'Missing required fields: {", ".join(missing)}')
                return render(request, 'users/add_student.html', {
                    'title': 'Add New Student',
                    # Pass all POST data to pre-populate form
                    **request.POST.dict(),
                    'gender_options': ['Male', 'Female', 'Other'],
                    'community_options': ['General', 'OBC', 'SC', 'ST', 'Other'],
                    'blood_group_options': ['A+', 'A-', 'B+', 'B-', 'AB+', 'AB-', 'O+', 'O-', 'Unknown'],
                    'teacher_ward_options': ['yes', 'no'],
                    'rte_options': ['yes', 'no'],
                    'sports_quota_options': ['yes', 'no']
                })

            # Split class and section
            try:
                class_part, section = class_section.split('-')
            except ValueError:
                messages.error(request, 'Class-Section must be in format "Class-Section" (e.g., 2-A)')
                return render(request, 'users/add_student.html', {
                    'title': 'Add New Student',
                    **request.POST.dict(),
                    'gender_options': ['Male', 'Female', 'Other'],
                    'community_options': ['General', 'OBC', 'SC', 'ST', 'Other'],
                    'blood_group_options': ['A+', 'A-', 'B+', 'B-', 'AB+', 'AB-', 'O+', 'O-', 'Unknown'],
                    'teacher_ward_options': ['yes', 'no'],
                    'rte_options': ['yes', 'no'],
                    'sports_quota_options': ['yes', 'no']
                })

            with connection.cursor() as cursor:
                # Check if admission number already exists
                cursor.execute("SELECT admission_number FROM student_page1 WHERE admission_number = %s", [admission_number])
                if cursor.fetchone():
                    messages.error(request, f'Admission number {admission_number} already exists.')
                    return render(request, 'users/add_student.html', {
                        'title': 'Add New Student',
                        **request.POST.dict(),
                        'gender_options': ['Male', 'Female', 'Other'],
                        'community_options': ['General', 'OBC', 'SC', 'ST', 'Other'],
                        'blood_group_options': ['A+', 'A-', 'B+', 'B-', 'AB+', 'AB-', 'O+', 'O-', 'Unknown'],
                        'teacher_ward_options': ['yes', 'no'],
                        'rte_options': ['yes', 'no'],
                        'sports_quota_options': ['yes', 'no']
                    })

                # Create a user account
                username = f"student_{admission_number}"
                password = admission_number  # Default password (Note: Not hashed for simplicity as per original code)

                cursor.execute("""
                    INSERT INTO users (username, email, password)
                    VALUES (%s, %s, %s)
                """, [username, email, password])

                # Get the new user_id
                cursor.execute("SELECT LAST_INSERT_ID()")
                new_user_id = cursor.fetchone()[0]

                # Insert into student_page1
                cursor.execute("""
                    INSERT INTO student_page1 
                    (user_id, name, admission_number, class, section, roll_number, emis)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                """, [new_user_id, name, admission_number, class_part, section, roll_number, emis])

                # Insert into student_page2
                cursor.execute("""
                    INSERT INTO student_page2 
                    (user_id, gender, community, tamil_name, dob, nationality, 
                     blood_group, mother_tongue, caste, religion, place_of_birth, 
                     aadhaar, disability, id_mark1, id_mark2, current_class, 
                     admission_class, admission_year, admission_date)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, 
                            %s, %s, %s, %s, %s, %s, %s, %s)
                """, [
                    new_user_id,
                    request.POST.get('gender', ''),
                    request.POST.get('community', ''),
                    request.POST.get('tamil_name', ''),
                    request.POST.get('dob', None) or None,
                    request.POST.get('nationality', ''),
                    request.POST.get('blood_group', ''),
                    request.POST.get('mother_tongue', ''),
                    request.POST.get('caste', ''),
                    request.POST.get('religion', ''),
                    request.POST.get('place_of_birth', ''),
                    request.POST.get('aadhaar', ''),
                    request.POST.get('disability', ''),
                    request.POST.get('id_mark1', ''),
                    request.POST.get('id_mark2', ''),
                    class_part,
                    request.POST.get('admission_class', class_part),
                    request.POST.get('admission_year', ''),
                    request.POST.get('admission_date', None) or None
                ])

                # Insert into student_page3
                cursor.execute("""
                    INSERT INTO student_page3 
                    (user_id, email, address, contact, alt_contact, country, 
                     state, city, pincode, status, house, teacher_ward, 
                     rte, sports_quota, prev_school, prev_board)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, 
                            %s, %s, %s, %s, %s)
                """, [
                    new_user_id,
                    email,
                    request.POST.get('address', ''),
                    request.POST.get('contact', ''),
                    request.POST.get('alt_contact', ''),
                    request.POST.get('country', ''),
                    request.POST.get('state', ''),
                    request.POST.get('city', ''),
                    request.POST.get('pincode', ''),
                    request.POST.get('status', ''),
                    request.POST.get('house', ''),
                    request.POST.get('teacher_ward', 'no'),
                    request.POST.get('rte', 'no'),
                    request.POST.get('sports_quota', 'no'),
                    request.POST.get('prev_school', ''),
                    request.POST.get('prev_board', '')
                ])

                # Insert into student_page4
                cursor.execute("""
                    INSERT INTO student_page4 
                    (user_id, father_name, father_name_tamil, mother_name, mother_name_tamil,
                     father_contact, mother_contact, father_email, mother_email,
                     father_qualification, mother_qualification, father_occupation,
                     mother_occupation, father_income, mother_income, guardian_name,
                     guardian_contact, guardian_email, child_living, rights_on_child,
                     med_blood_group, diseases, allergies, medicines, hospital, doctor)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, 
                            %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, 
                            %s, %s, %s, %s)
                """, [
                    new_user_id,
                    request.POST.get('father_name', ''),
                    request.POST.get('father_name_tamil', ''),
                    request.POST.get('mother_name', ''),
                    request.POST.get('mother_name_tamil', ''),
                    request.POST.get('father_contact', ''),
                    request.POST.get('mother_contact', ''),
                    request.POST.get('father_email', ''),
                    request.POST.get('mother_email', ''),
                    request.POST.get('father_qualification', ''),
                    request.POST.get('mother_qualification', ''),
                    request.POST.get('father_occupation', ''),
                    request.POST.get('mother_occupation', ''),
                    request.POST.get('father_income', ''),
                    request.POST.get('mother_income', ''),
                    request.POST.get('guardian_name', ''),
                    request.POST.get('guardian_contact', ''),
                    request.POST.get('guardian_email', ''),
                    request.POST.get('child_living', ''),
                    request.POST.get('rights_on_child', ''),
                    request.POST.get('med_blood_group', ''),
                    request.POST.get('diseases', ''),
                    request.POST.get('allergies', ''),
                    request.POST.get('medicines', ''),
                    request.POST.get('hospital', ''),
                    request.POST.get('doctor', '')
                ])

                # Insert into admin_student_classes
                cursor.execute("""
                    INSERT INTO admin_student_classes
                    (admin_id, class, section)
                    VALUES (%s, %s, %s)
                """, [new_user_id, class_part, section])

            messages.success(request, f'Student {name} added successfully with Admission Number: {admission_number}')
            return redirect('student_info')

        except Exception as e:
            messages.error(request, f'Error adding student: {str(e)}')
            return render(request, 'users/add_student.html', {
                'title': 'Add New Student',
                **request.POST.dict(),
                'gender_options': ['Male', 'Female', 'Other'],
                'community_options': ['General', 'OBC', 'SC', 'ST', 'Other'],
                'blood_group_options': ['A+', 'A-', 'B+', 'B-', 'AB+', 'AB-', 'O+', 'O-', 'Unknown'],
                'teacher_ward_options': ['yes', 'no'],
                'rte_options': ['yes', 'no'],
                'sports_quota_options': ['yes', 'no']
            })

    # GET request - show empty form
    return render(request, 'users/add_student.html', {
        'title': 'Add New Student',
        'gender_options': ['Male', 'Female', 'Other'],
        'community_options': ['General', 'OBC', 'SC', 'ST', 'Other'],
        'blood_group_options': ['A+', 'A-', 'B+', 'B-', 'AB+', 'AB-', 'O+', 'O-', 'Unknown'],
        'teacher_ward_options': ['yes', 'no'],
        'rte_options': ['yes', 'no'],
        'sports_quota_options': ['yes', 'no']
    })

def update_student(request, admission_number):
    if not request.session.get('admin_id'):
        messages.error(request, 'You must be logged in to access this page.')
        return redirect('admin_login')

    try:
        with connection.cursor() as cursor:
            # Get student data from multiple tables
            cursor.execute("""
                SELECT 
                    sp1.id, sp1.user_id, sp1.name, sp1.admission_number, sp1.class, sp1.section, 
                    sp1.roll_number, sp1.emis, sp3.email,
                    sp2.gender, sp2.community, sp2.tamil_name, sp2.dob, sp2.nationality,
                    sp2.blood_group, sp2.mother_tongue, sp2.caste, sp2.religion,
                    sp2.place_of_birth, sp2.aadhaar, sp2.disability, sp2.id_mark1,
                    sp2.id_mark2, sp2.current_class, sp2.admission_class, sp2.admission_year, sp2.admission_date,
                    sp3.address, sp3.contact, sp3.alt_contact, sp3.country, sp3.state,
                    sp3.city, sp3.pincode, sp3.status, sp3.house, sp3.teacher_ward,
                    sp3.rte, sp3.sports_quota, sp3.prev_school, sp3.prev_board,
                    sp4.father_name, sp4.father_name_tamil, sp4.mother_name, 
                    sp4.mother_name_tamil, sp4.father_contact, sp4.mother_contact,
                    sp4.father_email, sp4.mother_email, sp4.father_qualification,
                    sp4.mother_qualification, sp4.father_occupation, sp4.mother_occupation,
                    sp4.father_income, sp4.mother_income, sp4.guardian_name,
                    sp4.guardian_contact, sp4.guardian_email, sp4.child_living,
                    sp4.rights_on_child, sp4.med_blood_group, sp4.diseases,
                    sp4.allergies, sp4.medicines, sp4.hospital, sp4.doctor
                FROM student_page1 sp1
                LEFT JOIN student_page2 sp2 ON sp1.user_id = sp2.user_id
                LEFT JOIN student_page3 sp3 ON sp1.user_id = sp3.user_id
                LEFT JOIN student_page4 sp4 ON sp1.user_id = sp4.user_id
                WHERE sp1.admission_number = %s
            """, [admission_number])
            student_data = cursor.fetchone()

            if not student_data:
                messages.error(request, 'Student not found.')
                return redirect('student_info')

    except Exception as e:
        messages.error(request, f'Error fetching student data: {str(e)}')
        return redirect('student_info')

    if request.method == 'POST':
        try:
            # Required fields
            name = request.POST.get('name', '').strip()
            new_admission_number = request.POST.get('admission_number', '').strip()
            class_section = request.POST.get('class_section', '').strip()
            roll_number = request.POST.get('roll_number', '').strip()
            emis = request.POST.get('emis', '').strip()
            email = request.POST.get('email', '').strip()

            # Validate required fields
            if not all([name, new_admission_number, class_section, roll_number, emis, email]):
                missing = [field for field, value in [
                    ('name', name),
                    ('admission_number', new_admission_number),
                    ('class_section', class_section),
                    ('roll_number', roll_number),
                    ('emis', emis),
                    ('email', email)
                ] if not value]
                messages.error(request, f'Missing required fields: {", ".join(missing)}')
                return redirect('update_student', admission_number=admission_number)

            # Split class and section
            try:
                class_part, section = class_section.split('-')
            except ValueError:
                messages.error(request, 'Class-Section must be in format "Class-Section" (e.g., 2-A)')
                return redirect('update_student', admission_number=admission_number)

            user_id = student_data[1]  # user_id is at index 1 in the query result
            with connection.cursor() as cursor:
                # Check if new admission number already exists (if changed)
                if new_admission_number != admission_number:
                    cursor.execute("SELECT admission_number FROM student_page1 WHERE admission_number = %s", [new_admission_number])
                    if cursor.fetchone():
                        messages.error(request, f'Admission number {new_admission_number} already exists.')
                        return redirect('update_student', admission_number=admission_number)

                # 1. Update student_page1 (basic info)
                cursor.execute("""
                    UPDATE student_page1
                    SET name = %s, admission_number = %s, class = %s, section = %s, 
                        roll_number = %s, emis = %s
                    WHERE admission_number = %s
                """, [name, new_admission_number, class_part, section, roll_number, emis, admission_number])

                # 2. Update student_page2 (personal info)
                cursor.execute("""
                    UPDATE student_page2
                    SET 
                        gender = %s, community = %s, tamil_name = %s, dob = %s,
                        nationality = %s, blood_group = %s, mother_tongue = %s,
                        caste = %s, religion = %s, place_of_birth = %s, aadhaar = %s,
                        disability = %s, id_mark1 = %s, id_mark2 = %s,
                        current_class = %s, admission_class = %s, admission_year = %s,
                        admission_date = %s
                    WHERE user_id = %s
                """, [
                    request.POST.get('gender'),
                    request.POST.get('community'),
                    request.POST.get('tamil_name'),
                    request.POST.get('dob'),
                    request.POST.get('nationality'),
                    request.POST.get('blood_group'),
                    request.POST.get('mother_tongue'),
                    request.POST.get('caste'),
                    request.POST.get('religion'),
                    request.POST.get('place_of_birth'),
                    request.POST.get('aadhaar'),
                    request.POST.get('disability'),
                    request.POST.get('id_mark1'),
                    request.POST.get('id_mark2'),
                    class_part,  # current_class
                    request.POST.get('admission_class', class_part),
                    request.POST.get('admission_year'),
                    request.POST.get('admission_date'),
                    user_id
                ])

                # 3. Update student_page3 (contact info)
                cursor.execute("""
                    UPDATE student_page3
                    SET 
                        email = %s, address = %s, contact = %s, alt_contact = %s,
                        country = %s, state = %s, city = %s, pincode = %s,
                        status = %s, house = %s, teacher_ward = %s, rte = %s,
                        sports_quota = %s, prev_school = %s, prev_board = %s
                    WHERE user_id = %s
                """, [
                    email,
                    request.POST.get('address', ''),
                    request.POST.get('contact', ''),
                    request.POST.get('alt_contact', ''),
                    request.POST.get('country', ''),
                    request.POST.get('state', ''),
                    request.POST.get('city', ''),
                    request.POST.get('pincode', ''),
                    request.POST.get('status', ''),
                    request.POST.get('house', ''),
                    request.POST.get('teacher_ward', 'no'),
                    request.POST.get('rte', 'no'),
                    request.POST.get('sports_quota', 'no'),
                    request.POST.get('prev_school', ''),
                    request.POST.get('prev_board', ''),
                    user_id
                ])

                # 4. Update student_page4 (family info)
                cursor.execute("""
                    UPDATE student_page4
                    SET 
                        father_name = %s, father_name_tamil = %s, mother_name = %s,
                        mother_name_tamil = %s, father_contact = %s, mother_contact = %s,
                        father_email = %s, mother_email = %s, father_qualification = %s,
                        mother_qualification = %s, father_occupation = %s,
                        mother_occupation = %s, father_income = %s, mother_income = %s,
                        guardian_name = %s, guardian_contact = %s, guardian_email = %s,
                        child_living = %s, rights_on_child = %s, med_blood_group = %s,
                        diseases = %s, allergies = %s, medicines = %s, hospital = %s,
                        doctor = %s
                    WHERE user_id = %s
                """, [
                    request.POST.get('father_name', ''),
                    request.POST.get('father_name_tamil', ''),
                    request.POST.get('mother_name', ''),
                    request.POST.get('mother_name_tamil', ''),
                    request.POST.get('father_contact', ''),
                    request.POST.get('mother_contact', ''),
                    request.POST.get('father_email', ''),
                    request.POST.get('mother_email', ''),
                    request.POST.get('father_qualification', ''),
                    request.POST.get('mother_qualification', ''),
                    request.POST.get('father_occupation', ''),
                    request.POST.get('mother_occupation', ''),
                    request.POST.get('father_income', ''),
                    request.POST.get('mother_income', ''),
                    request.POST.get('guardian_name', ''),
                    request.POST.get('guardian_contact', ''),
                    request.POST.get('guardian_email', ''),
                    request.POST.get('child_living', ''),
                    request.POST.get('rights_on_child', ''),
                    request.POST.get('med_blood_group', ''),
                    request.POST.get('diseases', ''),
                    request.POST.get('allergies', ''),
                    request.POST.get('medicines', ''),
                    request.POST.get('hospital', ''),
                    request.POST.get('doctor', ''),
                    user_id
                ])

                # Update username if admission number changed
                if new_admission_number != admission_number:
                    new_username = f"student_{new_admission_number}"
                    cursor.execute("""
                        UPDATE users
                        SET username = %s
                        WHERE id = %s
                    """, [new_username, user_id])

            messages.success(request, f'Student {name} updated successfully.')
            return redirect('student_info')

        except Exception as e:
            messages.error(request, f'Error updating student: {str(e)}')
            return redirect('update_student', admission_number=admission_number)

    # Prepare context with all student data
    context = {
        'title': 'Update Student',
        'admission_number': admission_number,
        'id': student_data[0] if len(student_data) > 0 else '',
        'user_id': student_data[1] if len(student_data) > 1 else '',
        'name': student_data[2] if len(student_data) > 2 else '',
        'class_section': f"{student_data[4]}-{student_data[5]}" if len(student_data) > 5 else '',
        'roll_number': student_data[6] if len(student_data) > 6 else '',
        'emis': student_data[7] if len(student_data) > 7 else '',
        'email': student_data[8] if len(student_data) > 8 else '',
        'gender': student_data[9] if len(student_data) > 9 else '',
        'community': student_data[10] if len(student_data) > 10 else '',
        'tamil_name': student_data[11] if len(student_data) > 11 else '',
        'dob': student_data[12] if len(student_data) > 12 else '',
        'nationality': student_data[13] if len(student_data) > 13 else '',
        'blood_group': student_data[14] if len(student_data) > 14 else '',
        'mother_tongue': student_data[15] if len(student_data) > 15 else '',
        'caste': student_data[16] if len(student_data) > 16 else '',
        'religion': student_data[17] if len(student_data) > 17 else '',
        'place_of_birth': student_data[18] if len(student_data) > 18 else '',
        'aadhaar': student_data[19] if len(student_data) > 19 else '',
        'disability': student_data[20] if len(student_data) > 20 else '',
        'id_mark1': student_data[21] if len(student_data) > 21 else '',
        'id_mark2': student_data[22] if len(student_data) > 22 else '',
        'current_class': student_data[23] if len(student_data) > 23 else '',
        'admission_class': student_data[24] if len(student_data) > 24 else '',
        'admission_year': student_data[25] if len(student_data) > 25 else '',
        'admission_date': student_data[26] if len(student_data) > 26 else '',
        'address': student_data[27] if len(student_data) > 27 else '',
        'contact': student_data[28] if len(student_data) > 28 else '',
        'alt_contact': student_data[29] if len(student_data) > 29 else '',
        'country': student_data[30] if len(student_data) > 30 else '',
        'state': student_data[31] if len(student_data) > 31 else '',
        'city': student_data[32] if len(student_data) > 32 else '',
        'pincode': student_data[33] if len(student_data) > 33 else '',
        'status': student_data[34] if len(student_data) > 34 else '',
        'house': student_data[35] if len(student_data) > 35 else '',
        'teacher_ward': student_data[36] if len(student_data) > 36 else '',
        'rte': student_data[37] if len(student_data) > 37 else '',
        'sports_quota': student_data[38] if len(student_data) > 38 else '',
        'prev_school': student_data[39] if len(student_data) > 39 else '',
        'prev_board': student_data[40] if len(student_data) > 40 else '',
        'father_name': student_data[41] if len(student_data) > 41 else '',
        'father_name_tamil': student_data[42] if len(student_data) > 42 else '',
        'mother_name': student_data[43] if len(student_data) > 43 else '',
        'mother_name_tamil': student_data[44] if len(student_data) > 44 else '',
        'father_contact': student_data[45] if len(student_data) > 45 else '',
        'mother_contact': student_data[46] if len(student_data) > 46 else '',
        'father_email': student_data[47] if len(student_data) > 47 else '',
        'mother_email': student_data[48] if len(student_data) > 48 else '',
        'father_qualification': student_data[49] if len(student_data) > 49 else '',
        'mother_qualification': student_data[50] if len(student_data) > 50 else '',
        'father_occupation': student_data[51] if len(student_data) > 51 else '',
        'mother_occupation': student_data[52] if len(student_data) > 52 else '',
        'father_income': student_data[53] if len(student_data) > 53 else '',
        'mother_income': student_data[54] if len(student_data) > 54 else '',
        'guardian_name': student_data[55] if len(student_data) > 55 else '',
        'guardian_contact': student_data[56] if len(student_data) > 56 else '',
        'guardian_email': student_data[57] if len(student_data) > 57 else '',
        'child_living': student_data[58] if len(student_data) > 58 else '',
        'rights_on_child': student_data[59] if len(student_data) > 59 else '',
        'med_blood_group': student_data[60] if len(student_data) > 60 else '',
        'diseases': student_data[61] if len(student_data) > 61 else '',
        'allergies': student_data[62] if len(student_data) > 62 else '',
        'medicines': student_data[63] if len(student_data) > 63 else '',
        'hospital': student_data[64] if len(student_data) > 64 else '',
        'doctor': student_data[65] if len(student_data) > 65 else '',
        'gender_options': ['Male', 'Female', 'Other'],
        'community_options': ['General', 'OBC', 'SC', 'ST', 'Other'],
        'blood_group_options': ['A+', 'A-', 'B+', 'B-', 'AB+', 'AB-', 'O+', 'O-', 'Unknown'],
        'teacher_ward_options': ['yes', 'no'],
        'rte_options': ['yes', 'no'],
        'sports_quota_options': ['yes', 'no']
    }

    return render(request, 'users/add_update_student.html', context)

from django.db import connection, transaction
from django.shortcuts import redirect
from django.contrib import messages
from django.db import IntegrityError

def delete_student(request, admission_number):
    if not request.session.get('admin_id'):
        messages.error(request, 'You must be logged in to access this page.')
        return redirect('admin_login')

    try:
        with transaction.atomic():
            with connection.cursor() as cursor:
                # Get student info
                cursor.execute("""
                    SELECT user_id, name 
                    FROM student_page1 
                    WHERE admission_number = %s
                """, [admission_number])
                student_info = cursor.fetchone()
                
                if not student_info:
                    messages.error(request, 'Student not found.')
                    return redirect('student_info')

                user_id, student_name = student_info

                # Delete from all child tables referencing student_page1.user_id
                cursor.execute("DELETE FROM admin_attendance WHERE student_id = %s", [user_id])
                cursor.execute("DELETE FROM attendance WHERE student_id = %s", [user_id])
                cursor.execute("DELETE FROM school_marks WHERE student_id = %s", [user_id])
                cursor.execute("DELETE FROM student_page2 WHERE user_id = %s", [user_id])
                cursor.execute("DELETE FROM student_page4 WHERE user_id = %s", [user_id])
                
                # Delete from student_page1
                cursor.execute("DELETE FROM student_page1 WHERE admission_number = %s", [admission_number])
                
                # Delete from users table
                cursor.execute("DELETE FROM users WHERE id = %s", [user_id])

        messages.success(request, f'Student {student_name} deleted successfully.')
    except IntegrityError as e:
        error_code, error_message = e.args
        if error_code == 1451:
            messages.error(request, f'Cannot delete student {student_name} due to related records in an unknown table. Contact the administrator.')
        else:
            messages.error(request, f'Error deleting student: {str(e)}')
    except Exception as e:
        messages.error(request, f'Unexpected error deleting student: {str(e)}')
    
    return redirect('student_info')



from django.shortcuts import render, redirect
from django.contrib import messages
from django.db import connection

def add_batch(request):
    # Check admin authentication
    if not request.session.get('admin_id'):
        messages.error(request, 'You must be logged in to access this page.')
        return redirect('admin_login')

    if request.method == 'POST':
        academic_year = request.POST.get('academic_year')
        
        if not academic_year:
            messages.error(request, 'Please select an academic year')
            return redirect('view_batches')
        
        try:
            with connection.cursor() as cursor:
                # Check if batch already exists
                cursor.execute(
                    "SELECT id FROM admin_student_batch WHERE academic_year = %s",
                    [academic_year]
                )
                if cursor.fetchone():
                    messages.error(request, 'This academic year already exists')
                    return redirect('view_batches')
                
                # Insert new batch
                cursor.execute(
                    "INSERT INTO admin_student_batch (academic_year, created_at) VALUES (%s, NOW())",
                    [academic_year]
                )
                
                messages.success(request, 'Academic year added successfully')
                return redirect('view_batches')
                
        except Exception as e:
            messages.error(request, f'Error adding academic year: {str(e)}')
            return redirect('view_batches')
    
    return redirect('view_batches')

def view_batches(request):
    # Check admin authentication
    if not request.session.get('admin_id'):
        messages.error(request, 'You must be logged in to access this page.')
        return redirect('admin_login')

    try:
        with connection.cursor() as cursor:
            # Get all batches ordered by academic_year in descending order
            cursor.execute(
                "SELECT id, academic_year FROM admin_student_batch ORDER BY academic_year DESC"
            )
            batches = cursor.fetchall()
            
            # Convert to list of dictionaries for easier template handling
            batch_list = [{'id': row[0], 'academic_year': row[1]} for row in batches]
            
        return render(request, 'users/view_batches.html', {
            'batches': batch_list
        })
        
    except Exception as e:
        messages.error(request, f'Error fetching batches: {str(e)}')
        return render(request, 'users/view_batches.html', {
            'batches': []
        })

def update_batch(request, batch_id):
    # Check admin authentication
    if not request.session.get('admin_id'):
        messages.error(request, 'You must be logged in to access this page.')
        return redirect('admin_login')

    if request.method == 'POST':
        new_academic_year = request.POST.get('academic_year')
        
        if not new_academic_year:
            messages.error(request, 'Please select an academic year')
            return redirect('view_batches')
        
        try:
            with connection.cursor() as cursor:
                # Check if the new academic year already exists (excluding the current batch)
                cursor.execute(
                    "SELECT id FROM admin_student_batch WHERE academic_year = %s AND id != %s",
                    [new_academic_year, batch_id]
                )
                if cursor.fetchone():
                    messages.error(request, 'This academic year already exists')
                    return redirect('view_batches')
                
                # Check if batch exists
                cursor.execute(
                    "SELECT id FROM admin_student_batch WHERE id = %s",
                    [batch_id]
                )
                if not cursor.fetchone():
                    messages.error(request, 'Batch not found')
                    return redirect('view_batches')
                
                # Update the batch
                cursor.execute(
                    "UPDATE admin_student_batch SET academic_year = %s WHERE id = %s",
                    [new_academic_year, batch_id]
                )
                
                messages.success(request, 'Batch updated successfully')
                return redirect('view_batches')
                
        except Exception as e:
            messages.error(request, f'Error updating batch: {str(e)}')
            return redirect('view_batches')
    
    return redirect('view_batches')

def delete_batch(request, batch_id):
    # Check admin authentication
    if not request.session.get('admin_id'):
        messages.error(request, 'You must be logged in to access this page.')
        return redirect('admin_login')

    try:
        with connection.cursor() as cursor:
            # Check if batch exists
            cursor.execute(
                "SELECT id FROM admin_student_batch WHERE id = %s",
                [batch_id]
            )
            if not cursor.fetchone():
                messages.error(request, 'Batch not found')
                return redirect('view_batches')
            
            # Delete the batch
            cursor.execute(
                "DELETE FROM admin_student_batch WHERE id = %s",
                [batch_id]
            )
            
            messages.success(request, 'Batch deleted successfully')
            return redirect('view_batches')
            
    except Exception as e:
        messages.error(request, f'Error deleting batch: {str(e)}')
        return redirect('view_batches')






from django.shortcuts import render, redirect
from django.contrib import messages
from django.db import connection, transaction
from django.conf import settings
import os
import uuid

def manage_users(request):
    if not request.session.get('admin_id'):
        messages.error(request, 'You must be logged in to access this page.')
        return redirect('admin_login')

    try:
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT id, name, email, username, password, role, created_at, updated_at
                FROM admin_manage_users
                ORDER BY name
            """)
            users = cursor.fetchall()
            
            user_list = []
            for row in users:
                user_id, name, email, username, password, role, created_at, updated_at = row
                # Fetch profile picture based on role
                profile_pic_url = None
                if role == 'teacher':
                    cursor.execute("SELECT profile_pic_url FROM profile_pics_teachers WHERE teacher_id = %s", [user_id])
                    pic_result = cursor.fetchone()
                    profile_pic_url = f"{settings.MEDIA_URL}{pic_result[0]}" if pic_result else f"{settings.MEDIA_URL}pfpicsteacher/default.jpg"
                else:
                    cursor.execute("SELECT profile_pic_url FROM otherusers_profile_pic WHERE user_id = %s", [user_id])
                    pic_result = cursor.fetchone()
                    profile_pic_url = f"{settings.MEDIA_URL}{pic_result[0]}" if pic_result else f"{settings.MEDIA_URL}pfpicsusers/default.jpg"
                
                user_list.append({
                    'id': user_id,
                    'name': name,
                    'email': email,
                    'username': username,
                    'password': password,
                    'role': role,
                    'created_at': created_at,
                    'updated_at': updated_at,
                    'profile_pic_url': profile_pic_url
                })
            
        return render(request, 'users/manage_users.html', {
            'users': user_list
        })
        
    except Exception as e:
        messages.error(request, f'Error fetching users: {str(e)}')
        return render(request, 'users/manage_users.html', {
            'users': []
        })

def add_user(request):
    if not request.session.get('admin_id'):
        messages.error(request, 'You must be logged in to access this page.')
        return redirect('admin_login')

    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        username = request.POST.get('username')
        password = request.POST.get('password')
        role = request.POST.get('role')
        
        if not all([name, email, username, password, role]):
            messages.error(request, 'All fields are required')
            return redirect('manage_users')
        
        try:
            with transaction.atomic():
                with connection.cursor() as cursor:
                    # Check for duplicate username or email
                    cursor.execute(
                        "SELECT id FROM admin_manage_users WHERE username = %s OR email = %s",
                        [username, email]
                    )
                    if cursor.fetchone():
                        messages.error(request, 'Username or email already exists')
                        return redirect('manage_users')
                    
                    # Insert into admin_manage_users
                    cursor.execute(
                        """INSERT INTO admin_manage_users 
                        (name, email, username, password, role, created_at) 
                        VALUES (%s, %s, %s, %s, %s, NOW())""",
                        [name, email, username, password, role]
                    )
                    user_id = cursor.lastrowid

                    # Handle teacher-specific initialization
                    if role == 'teacher':
                        cursor.execute(
                            """INSERT INTO teachers (id, name, email, password, subject, created_at)
                            VALUES (%s, %s, %s, %s, %s, NOW())""",
                            [user_id, name, email, password, '']
                        )

                    # Handle profile picture
                    if 'profile_pic' in request.FILES:
                        profile_pic = request.FILES['profile_pic']
                        allowed_extensions = ['.png', '.jpg', '.jpeg']
                        file_ext = os.path.splitext(profile_pic.name)[1].lower()
                        if file_ext not in allowed_extensions:
                            messages.error(request, "Only PNG, JPG, or JPEG files are allowed.")
                            return redirect('manage_users')
                        if profile_pic.size > 5 * 1024 * 1024:
                            messages.error(request, "File size must be less than 5MB.")
                            return redirect('manage_users')

                        filename = f"{uuid.uuid4().hex}_{user_id}{file_ext}"
                        pfpics_dir = os.path.join(settings.MEDIA_ROOT, 'pfpicsteacher' if role == 'teacher' else 'pfpicsusers')
                        os.makedirs(pfpics_dir, exist_ok=True)
                        file_path = os.path.join(pfpics_dir, filename)

                        with open(file_path, 'wb+') as destination:
                            for chunk in profile_pic.chunks():
                                destination.write(chunk)

                        table = 'profile_pics_teachers' if role == 'teacher' else 'otherusers_profile_pic'
                        id_column = 'teacher_id' if role == 'teacher' else 'user_id'
                        pic_path = f"{'pfpicsteacher' if role == 'teacher' else 'pfpicsusers'}/{filename}"
                        cursor.execute(
                            f"INSERT INTO {table} ({id_column}, profile_pic_url, created_at) VALUES (%s, %s, NOW())",
                            [user_id, pic_path]
                        )

                messages.success(request, 'User created successfully')
                return redirect(f'/manage_users/?t={uuid.uuid4().hex}')
                
        except Exception as e:
            messages.error(request, f'Error creating user: {str(e)}')
            return redirect('manage_users')
    
    return redirect('manage_users')

def update_user(request, user_id):
    if not request.session.get('admin_id'):
        messages.error(request, 'You must be logged in to access this page.')
        return redirect('admin_login')

    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        username = request.POST.get('username')
        password = request.POST.get('password')
        role = request.POST.get('role')
        
        if not all([name, email, username, role]):
            messages.error(request, 'Name, email, username, and role are required')
            return redirect('manage_users')
        
        try:
            with transaction.atomic():
                with connection.cursor() as cursor:
                    # Check if user exists
                    cursor.execute("SELECT id, role, password FROM admin_manage_users WHERE id = %s", [user_id])
                    user_data = cursor.fetchone()
                    if not user_data:
                        messages.error(request, 'User not found')
                        return redirect('manage_users')
                    
                    current_role = user_data[1]
                    current_password = user_data[2]

                    # Check for duplicate username or email
                    cursor.execute(
                        "SELECT id FROM admin_manage_users WHERE (username = %s OR email = %s) AND id != %s",
                        [username, email, user_id]
                    )
                    if cursor.fetchone():
                        messages.error(request, 'Username or email already exists')
                        return redirect('manage_users')

                    # Update admin_manage_users
                    new_password = password if password else current_password
                    cursor.execute(
                        """UPDATE admin_manage_users 
                        SET name = %s, email = %s, username = %s, password = %s, role = %s, updated_at = NOW()
                        WHERE id = %s""",
                        [name, email, username, new_password, role, user_id]
                    )

                    # Handle role changes
                    if current_role == 'teacher' and role != 'teacher':
                        # Delete teacher record and profile picture
                        cursor.execute("SELECT profile_pic_url FROM profile_pics_teachers WHERE teacher_id = %s", [user_id])
                        old_pic = cursor.fetchone()
                        if old_pic:
                            old_file_path = os.path.join(settings.MEDIA_ROOT, old_pic[0])
                            if os.path.exists(old_file_path):
                                os.remove(old_file_path)
                            cursor.execute("DELETE FROM profile_pics_teachers WHERE teacher_id = %s", [user_id])
                        cursor.execute("DELETE FROM teachers WHERE id = %s", [user_id])

                    elif role == 'teacher':
                        # Update or insert teacher record
                        cursor.execute("SELECT id FROM teachers WHERE id = %s", [user_id])
                        if not cursor.fetchone():
                            cursor.execute(
                                """INSERT INTO teachers (id, name, email, password, subject, created_at)
                                VALUES (%s, %s, %s, %s, %s, NOW())""",
                                [user_id, name, email, new_password, '']
                            )
                        else:
                            cursor.execute(
                                """UPDATE teachers 
                                SET name = %s, email = %s, password = %s, subject = %s
                                WHERE id = %s""",
                                [name, email, new_password, '', user_id]
                            )

                    # Handle profile picture
                    if 'profile_pic' in request.FILES:
                        profile_pic = request.FILES['profile_pic']
                        allowed_extensions = ['.png', '.jpg', '.jpeg']
                        file_ext = os.path.splitext(profile_pic.name)[1].lower()
                        if file_ext not in allowed_extensions:
                            messages.error(request, "Only PNG, JPG, or JPEG files are allowed.")
                            return redirect('manage_users')
                        if profile_pic.size > 5 * 1024 * 1024:
                            messages.error(request, "File size must be less than 5MB.")
                            return redirect('manage_users')

                        filename = f"{uuid.uuid4().hex}_{user_id}{file_ext}"
                        pfpics_dir = os.path.join(settings.MEDIA_ROOT, 'pfpicsteacher' if role == 'teacher' else 'pfpicsusers')
                        os.makedirs(pfpics_dir, exist_ok=True)
                        file_path = os.path.join(pfpics_dir, filename)

                        # Delete old profile picture
                        table = 'profile_pics_teachers' if role == 'teacher' else 'otherusers_profile_pic'
                        id_column = 'teacher_id' if role == 'teacher' else 'user_id'
                        cursor.execute(f"SELECT profile_pic_url FROM {table} WHERE {id_column} = %s", [user_id])
                        old_pic = cursor.fetchone()
                        if old_pic:
                            old_file_path = os.path.join(settings.MEDIA_ROOT, old_pic[0])
                            if os.path.exists(old_file_path):
                                os.remove(old_file_path)
                            cursor.execute(f"DELETE FROM {table} WHERE {id_column} = %s", [user_id])

                        with open(file_path, 'wb+') as destination:
                            for chunk in profile_pic.chunks():
                                destination.write(chunk)

                        pic_path = f"{'pfpicsteacher' if role == 'teacher' else 'pfpicsusers'}/{filename}"
                        cursor.execute(
                            f"INSERT INTO {table} ({id_column}, profile_pic_url, created_at) VALUES (%s, %s, NOW())",
                            [user_id, pic_path]
                        )

                messages.success(request, 'User updated successfully')
                return redirect(f'/manage_users/?t={uuid.uuid4().hex}')

        except Exception as e:
            messages.error(request, f'Error updating user: {str(e)}')
            return redirect('manage_users')
    
    return redirect('manage_users')

def delete_user(request, user_id):
    if not request.session.get('admin_id'):
        messages.error(request, 'You must be logged in to access this page.')
        return redirect('admin_login')

    try:
        with transaction.atomic():
            with connection.cursor() as cursor:
                # Check user and role
                cursor.execute("SELECT role FROM admin_manage_users WHERE id = %s", [user_id])
                user_data = cursor.fetchone()
                if not user_data:
                    messages.error(request, 'User not found.')
                    return redirect('manage_users')
                role = user_data[0]

                # Delete profile picture
                table = 'profile_pics_teachers' if role == 'teacher' else 'otherusers_profile_pic'
                id_column = 'teacher_id' if role == 'teacher' else 'user_id'
                cursor.execute(f"SELECT profile_pic_url FROM {table} WHERE {id_column} = %s", [user_id])
                old_pic = cursor.fetchone()
                if old_pic:
                    old_file_path = os.path.join(settings.MEDIA_ROOT, old_pic[0])
                    if os.path.exists(old_file_path):
                        os.remove(old_file_path)
                    cursor.execute(f"DELETE FROM {table} WHERE {id_column} = %s", [user_id])

                # Delete from teachers if applicable
                if role == 'teacher':
                    cursor.execute("DELETE FROM teachers WHERE id = %s", [user_id])

                # Delete from admin_manage_users
                cursor.execute("DELETE FROM admin_manage_users WHERE id = %s", [user_id])
                if cursor.rowcount == 0:
                    messages.error(request, 'User not found.')
                    return redirect('manage_users')

        messages.success(request, 'User deleted successfully!')
        return redirect(f'/manage_users/?t={uuid.uuid4().hex}')

    except Exception as e:
        messages.error(request, f'Error deleting user: {str(e)}')
        return redirect('manage_users')




from django.shortcuts import render, redirect

def admin_page(request):
    admin_name = request.session.get('admin_name')
    if not admin_name:
        return redirect('admin_login')  # If not logged in, redirect to login

    return render(request, 'users/admin_page.html', {'admin_name': admin_name})



from django.shortcuts import render, redirect
from django.contrib import messages
from django.db import connection

def view_edit_class(request):
    if not request.session.get('admin_id'):
        messages.error(request, 'You must be logged in to access this page.')
        return redirect('admin_login')

    admin_id = request.session['admin_id']

    # Fetch all class-section pairs from admin_student_classes for current admin
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT id, class, section 
            FROM admin_student_classes 
            WHERE admin_id = %s
            ORDER BY class DESC, section DESC
        """, [admin_id])
        classes = cursor.fetchall()

    # Format as "class-section" for display
    class_list = [{'id': row[0], 'class_name': f"{row[1]}-{row[2]}"} for row in classes]

    return render(request, 'users/view_edit_class.html', {
        'classes': class_list,
        'total_classes': len(class_list)
    })

def add_class(request):
    if not request.session.get('admin_id'):
        messages.error(request, 'You must be logged in to access this page.')
        return redirect('admin_login')

    admin_id = request.session['admin_id']

    if request.method == 'POST':
        class_name = request.POST.get('class_name')
        if class_name:
            try:
                class_part, section = class_name.split('-')
                
                with connection.cursor() as cursor:
                    # Check if this exact class-section combo already exists for this admin
                    cursor.execute("""
                        SELECT COUNT(*) FROM admin_student_classes
                        WHERE admin_id = %s AND class = %s AND section = %s
                    """, [admin_id, class_part, section])
                    exists = cursor.fetchone()[0]

                    if exists:
                        messages.error(request, f'You already created class {class_name}.')
                    else:
                        # Insert new class-section for this admin
                        cursor.execute("""
                            INSERT INTO admin_student_classes (admin_id, class, section)
                            VALUES (%s, %s, %s)
                        """, [admin_id, class_part, section])
                        
                        messages.success(request, f'Class {class_name} added successfully.')
                        return redirect('view_edit_class')
                        
            except ValueError:
                messages.error(request, 'Class name must be in format "Class-Section" (e.g., 2-A).')
            except Exception as e:
                messages.error(request, f'Error adding class: {str(e)}')
        else:
            messages.error(request, 'Class name cannot be empty.')
    
    return render(request, 'users/add_update_class.html', {'title': 'Add New Class'})

def update_class(request, class_id):
    if not request.session.get('admin_id'):
        messages.error(request, 'You must be logged in to access this page.')
        return redirect('admin_login')

    admin_id = request.session['admin_id']

    # Fetch the class-section pair from admin_student_classes
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT id, class, section 
            FROM admin_student_classes 
            WHERE id = %s AND admin_id = %s
        """, [class_id, admin_id])
        class_data = cursor.fetchone()
        if not class_data:
            messages.error(request, 'Class not found or you don\'t have permission.')
            return redirect('view_edit_class')

    if request.method == 'POST':
        new_class_name = request.POST.get('class_name')
        if new_class_name:
            try:
                new_class, new_section = new_class_name.split('-')
                with connection.cursor() as cursor:
                    # Check if the new class-section combo already exists for this admin
                    cursor.execute("""
                        SELECT COUNT(*) FROM admin_student_classes
                        WHERE admin_id = %s AND class = %s AND section = %s AND id != %s
                    """, [admin_id, new_class, new_section, class_id])
                    exists = cursor.fetchone()[0]

                    if exists:
                        messages.error(request, f'You already have class {new_class_name}.')
                    else:
                        # Update the record in admin_student_classes
                        cursor.execute("""
                            UPDATE admin_student_classes
                            SET class = %s, section = %s
                            WHERE id = %s AND admin_id = %s
                        """, [new_class, new_section, class_id, admin_id])
                        messages.success(request, f'Class updated to {new_class_name} successfully.')
                        return redirect('view_edit_class')
            except ValueError:
                messages.error(request, 'Class name must be in format "Class-Section" (e.g., 2-A).')
            except Exception as e:
                messages.error(request, f'Error updating class: {str(e)}')
        else:
            messages.error(request, 'Class name cannot be empty.')
    return render(request, 'users/add_update_class.html', {
        'title': 'Update Class',
        'class_name': f"{class_data[1]}-{class_data[2]}"
    })

def delete_class(request, class_id):
    if not request.session.get('admin_id'):
        messages.error(request, 'You must be logged in to access this page.')
        return redirect('admin_login')

    admin_id = request.session['admin_id']

    try:
        with connection.cursor() as cursor:
            # Delete the record from admin_student_classes
            cursor.execute("""
                DELETE FROM admin_student_classes 
                WHERE id = %s AND admin_id = %s
            """, [class_id, admin_id])
        messages.success(request, 'Class deleted successfully.')
    except Exception as e:
        messages.error(request, f'Error deleting class: {str(e)}')
    return redirect('view_edit_class')




from django.shortcuts import render, redirect
from django.contrib import messages
from django.core.files.storage import FileSystemStorage
from django.db import transaction, connection, IntegrityError
import pandas as pd
import numpy as np
import os
import uuid
from django.conf import settings

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

                # Validate admission_number
                if df['admission_number'].isna().any():
                    messages.error(request, 'The admission_number column contains null or missing values.')
                    fs.delete(filename)
                    return redirect('bulk_upload')

                try:
                    df['admission_number'] = df['admission_number'].astype(int)
                except (ValueError, TypeError):
                    messages.error(request, 'Invalid data in admission_number column. All values must be integers.')
                    fs.delete(filename)
                    return redirect('bulk_upload')

                if df['admission_number'].duplicated().any():
                    messages.error(request, 'The admission_number column contains duplicate values.')
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
                    df['dob'] = pd.to_datetime(df['dob'], errors='coerce').dt.strftime('%Y-%m-%d')
                if 'admission_date' in df.columns:
                    df['admission_date'] = pd.to_datetime(df['admission_date'], errors='coerce').dt.strftime('%Y-%m-%d')

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

                # Validate admission_number
                if df['admission_number'].isna().any():
                    messages.error(request, 'The admission_number column contains null or missing values.')
                    fs.delete(filename)
                    return redirect('bulk_upload')

                try:
                    df['admission_number'] = df['admission_number'].astype(int)
                except (ValueError, TypeError):
                    messages.error(request, 'Invalid data in admission_number column. All values must be integers.')
                    fs.delete(filename)
                    return redirect('bulk_upload')

                if df['admission_number'].duplicated().any():
                    messages.error(request, 'The admission_number column contains duplicate values.')
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
                    df['dob'] = pd.to_datetime(df['dob'], errors='coerce').dt.strftime('%Y-%m-%d')
                if 'admission_date' in df.columns:
                    df['admission_date'] = pd.to_datetime(df['admission_date'], errors='coerce').dt.strftime('%Y-%m-%d')

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










# users/views.py
from django.shortcuts import render, redirect
from django.contrib import messages
from django.db import connection, transaction
from mysql.connector import Error

def manage_teachers(request):
    """
    Displays the teacher management page with a list of teachers, including passwords and profile pictures.
    """
    if not request.session.get('admin_id'):
        messages.error(request, 'Please log in to access this page.')
        return redirect('admin_login')

    try:
        with connection.cursor() as cursor:
            # Join teachers and profile_pics_teachers to get profile pictures
            cursor.execute("""
                SELECT t.id, t.name, t.email, t.subject, t.class_teacher_of, t.password, p.profile_pic_url
                FROM teachers t
                LEFT JOIN profile_pics_teachers p ON t.id = p.teacher_id
            """)
            teachers = [
                {
                    'id': row[0],
                    'name': row[1],
                    'email': row[2],
                    'subject': row[3],
                    'class_teacher_of': row[4] if row[4] else 'Not Assigned',
                    'password': row[5],
                    'profile_pic_url': f"{settings.MEDIA_URL}{row[6]}" if row[6] else f"{settings.MEDIA_URL}pfpicsteacher/default.jpg"
                } for row in cursor.fetchall()
            ]
        return render(request, 'users/manage_teachers.html', {'teachers': teachers})
    except Error as e:
        messages.error(request, f'Error fetching teachers: {e}')
        return redirect('manage_teachers')

def add_teacher(request):
    """
    Handles adding a new teacher via POST request, with a password.
    """
    if request.method != 'POST':
        return redirect('manage_teachers')

    name = request.POST.get('name')
    email = request.POST.get('email')
    subject = request.POST.get('subject')
    class_teacher_of = request.POST.get('class_teacher_of') or None
    password = request.POST.get('password')

    # Validation
    if not all([name, email, subject, password]):
        messages.error(request, 'Name, email, subject, and password are required.')
        return redirect('manage_teachers')

    if len(name) > 100 or len(email) > 100 or len(subject) > 50 or (class_teacher_of and len(class_teacher_of) > 20) or len(password) > 255:
        messages.error(request, 'Input exceeds maximum length.')
        return redirect('manage_teachers')

    try:
        with transaction.atomic():
            with connection.cursor() as cursor:
                cursor.execute("SELECT email FROM teachers WHERE email = %s", [email])
                if cursor.fetchone():
                    messages.error(request, 'Email already exists.')
                    return redirect('manage_teachers')

                cursor.execute(
                    "INSERT INTO teachers (name, email, subject, class_teacher_of, password) VALUES (%s, %s, %s, %s, %s)",
                    [name, email, subject, class_teacher_of, password]
                )
                # Insert into admin_manage_users
                cursor.execute(
                    "INSERT INTO admin_manage_users (name, email, username, password, role, created_at, updated_at) VALUES (%s, %s, %s, %s, %s, NOW(), NOW())",
                    [name, email, f"{name.lower().replace(' ', '')}_{cursor.lastrowid}", password, 'teacher']
                )
        messages.success(request, 'Teacher added successfully.')
    except Error as e:
        messages.error(request, f'Error adding teacher: {e}')
    return redirect('manage_teachers')

def update_teacher(request):
    """
    Handles updating an existing teacher's details, including password, via POST request.
    """
    if request.method != 'POST':
        return redirect('manage_teachers')

    teacher_id = request.POST.get('teacher_id')
    name = request.POST.get('name')
    email = request.POST.get('email')
    subject = request.POST.get('subject')
    class_teacher_of = request.POST.get('class_teacher_of') or None
    password = request.POST.get('password')

    # Validation
    if not all([teacher_id, name, email, subject, password]):
        messages.error(request, 'All required fields are mandatory.')
        return redirect('manage_teachers')

    if len(name) > 100 or len(email) > 100 or len(subject) > 50 or (class_teacher_of and len(class_teacher_of) > 20) or len(password) > 255:
        messages.error(request, 'Input exceeds maximum length.')
        return redirect('manage_teachers')

    try:
        with transaction.atomic():
            with connection.cursor() as cursor:
                cursor.execute("SELECT id, email FROM teachers WHERE id = %s", [teacher_id])
                teacher = cursor.fetchone()
                if not teacher:
                    messages.error(request, 'Teacher not found.')
                    return redirect('manage_teachers')

                old_email = teacher[1]
                cursor.execute(
                    "SELECT email FROM teachers WHERE email = %s AND id != %s",
                    [email, teacher_id]
                )
                if cursor.fetchone():
                    messages.error(request, 'Email already exists.')
                    return redirect('manage_teachers')

                cursor.execute(
                    "UPDATE teachers SET name = %s, email = %s, subject = %s, class_teacher_of = %s, password = %s WHERE id = %s",
                    [name, email, subject, class_teacher_of, password, teacher_id]
                )
                cursor.execute(
                    "UPDATE admin_manage_users SET name = %s, email = %s, password = %s, updated_at = NOW() WHERE email = %s AND role = %s",
                    [name, email, password, old_email, 'teacher']
                )
        messages.success(request, 'Teacher updated successfully.')
    except Error as e:
        messages.error(request, f'Error updating teacher: {e}')
    return redirect('manage_teachers')

def delete_teacher(request, teacher_id):
    """
    Handles deleting a teacher by ID from both teachers and admin_manage_users.
    """
    try:
        with transaction.atomic():
            with connection.cursor() as cursor:
                cursor.execute("SELECT id, email FROM teachers WHERE id = %s", [teacher_id])
                teacher = cursor.fetchone()
                if not teacher:
                    messages.error(request, 'Teacher not found.')
                    return redirect('manage_teachers')

                email = teacher[1]
                cursor.execute("DELETE FROM teachers WHERE id = %s", [teacher_id])
                cursor.execute("DELETE FROM admin_manage_users WHERE email = %s AND role = %s", [email, 'teacher'])
        messages.success(request, 'Teacher deleted successfully.')
    except Error as e:
        messages.error(request, f'Error deleting teacher: {e}')
    return redirect('manage_teachers')

def delete_user(request, user_id):
    """
    Handles deleting a user by ID from admin_manage_users and, if teacher, from teachers.
    """
    try:
        with transaction.atomic():
            with connection.cursor() as cursor:
                cursor.execute("SELECT email, role FROM admin_manage_users WHERE id = %s", [user_id])
                user = cursor.fetchone()
                if not user:
                    messages.error(request, 'User not found.')
                    return redirect('manage_users')  # Assumes a manage_users view exists

                email, role = user
                cursor.execute("DELETE FROM admin_manage_users WHERE id = %s", [user_id])
                if role == 'teacher':
                    cursor.execute("DELETE FROM teachers WHERE email = %s", [email])
        messages.success(request, 'User deleted successfully.')
    except Error as e:
        messages.error(request, f'Error deleting user: {e}')
    return redirect('manage_users')

from django.shortcuts import render, redirect
from django.contrib import messages
from django.db import connection, transaction
from django.db import connection, transaction
from django.db.utils import IntegrityError, DatabaseError
from django.contrib import messages
from django.shortcuts import redirect, render

from django.db import connection, transaction
from django.db.utils import IntegrityError
from django.contrib import messages
from django.shortcuts import redirect, render
from django.urls import reverse

def teacher_signup(request):
    """Final robust teacher signup with raw SQL"""
    if request.method != 'POST':
        return render(request, 'users/teacher_signup.html', {'form_cleared': request.GET.get('clear')})

    # Sanitize and validate inputs
    name = request.POST.get('name', '').strip()
    email = request.POST.get('email', '').lower().strip()
    subject = request.POST.get('subject', '').strip()
    password = request.POST.get('password', '').strip()

    # Clear existing messages
    storage = messages.get_messages(request)
    storage.used = True

    if not all([name, email, subject, password]):
        messages.error(request, 'All fields are required')
        return redirect(reverse('teacher_signup') + '?clear=1')

    if len(name) > 100 or len(email) > 100 or len(subject) > 50 or len(password) > 255:
        messages.error(request, 'Input exceeds maximum length')
        return redirect(reverse('teacher_signup') + '?clear=1')

    try:
        with transaction.atomic():
            with connection.cursor() as cursor:
                # Check BOTH tables for existing email
                cursor.execute("""
                    SELECT 'teachers' as source FROM teachers WHERE email = %s
                    UNION ALL
                    SELECT 'admin' as source FROM admin_manage_users WHERE email = %s
                    LIMIT 1
                """, [email, email])
                
                existing = cursor.fetchone()
                if existing:
                    print(f"Duplicate email detected: {email} in {existing[0]}")  # Debug
                    messages.error(request, f'Email "{email}" already exists in our system')
                    return redirect(reverse('teacher_signup') + '?clear=1')

                # Insert into teachers
                cursor.execute(
                    """INSERT INTO teachers (name, email, subject, password)
                    VALUES (%s, %s, %s, %s)""",
                    [name, email, subject, password]
                )
                teacher_id = cursor.lastrowid

                # Generate unique username (fit varchar(50))
                base_username = name.lower().replace(' ', '_')[:40]  # Reserve space for _id
                username = f"{base_username}_{teacher_id}"[:50]

                # Insert into admin_manage_users
                cursor.execute(
                    """INSERT INTO admin_manage_users
                    (name, email, username, password, role, created_at, updated_at)
                    VALUES (%s, %s, %s, %s, %s, NOW(), NOW())""",
                    [name, email, username, password, 'Teacher']
                )

        messages.success(request, 'Registration successful! Please login.')
        return redirect('teacher_login')

    except IntegrityError as e:
        print(f"IntegrityError: {str(e)}")  # Debug
        messages.error(request, f'Email "{email}" already exists in our system')
        return redirect(reverse('teacher_signup') + '?clear=1')
    except Exception as e:
        print(f"Exception: {str(e)}")  # Debug
        messages.error(request, 'System error during registration')
        return redirect(reverse('teacher_signup') + '?clear=1')


from django.shortcuts import render, redirect
from django.contrib import messages
from django.db import connection
from mysql.connector import Error

def teacher_login(request):
    """
    Handles teacher login via POST request, checking plain text password.
    """
    if request.method != 'POST':
        return render(request, 'users/teacher_login.html')

    email = request.POST.get('email')
    password = request.POST.get('password')

    # Validation
    if not all([email, password]):
        messages.error(request, 'Email and password are required.')
        return redirect('teacher_login')

    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT id, name, password FROM teachers WHERE email = %s", [email])
            result = cursor.fetchone()
            if result and result[2] == password:
                request.session['teacher_id'] = result[0]
                request.session['username'] = result[1]  # Store teacher's name as username
                messages.success(request, 'Login successful!')
                return redirect('teacher_dashboard')
            else:
                messages.error(request, 'Invalid email or password.')
                return redirect('teacher_login')
    except Error as e:
        messages.error(request, f'Error during login: {e}')
        return redirect('teacher_login')

def teacher_dashboard(request):
    username = request.session.get('username')
    if not username:
        messages.error(request, 'Please log in to access the mark entry system.')
        return redirect('teacher_login')
    
    return render(request, 'users/teacher_dashboard.html', {'username': username})






from django.shortcuts import render, redirect
from django.contrib import messages
from django.db import connection, IntegrityError
from django.http import HttpResponse
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from io import BytesIO
import datetime
import requests
import json

def teacher_portal(request):
    if not request.session.get('teacher_id'):
        messages.error(request, 'Please log in to access this page.')
        return redirect('teacher_login')

    today_date = datetime.date.today().strftime('%Y-%m-%d')
    selected_date = request.GET.get('date', today_date)
    
    with connection.cursor() as cursor:
        cursor.execute("SELECT DISTINCT class, section FROM student_page1 WHERE section IS NOT NULL AND section != '' ORDER BY class, section")
        class_sections = [(row[0], row[1]) for row in cursor.fetchall()]
        classes = sorted(set(row[0] for row in class_sections)) or []

    selected_class = request.GET.get('class', '')
    selected_section = request.GET.get('section', '')
    students = []
    
    if selected_class and selected_section:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT user_id, name, admission_number, class, section
                FROM student_page1 
                WHERE class = %s AND section = %s 
                ORDER BY name, admission_number
                """, 
                [selected_class, selected_section]
            )
            students = [
                {
                    'user_id': row[0],
                    'name': row[1],
                    'admission_number': row[2],
                    'class': row[3],
                    'section': row[4] if row[4] else 'N/A'
                } for row in cursor.fetchall()
            ]
            
            cursor.execute(
                """
                SELECT student_id, status 
                FROM attendance 
                WHERE class = %s AND section = %s AND date = %s
                """, 
                [selected_class, selected_section, selected_date]
            )
            attendance_records = {row[0]: row[1] for row in cursor.fetchall()}
            
            for student in students:
                student['status'] = attendance_records.get(student['user_id'], '')

    return render(request, 'users/teacher_portal.html', {
        'classes': classes,
        'class_sections': json.dumps(class_sections),
        'selected_class': selected_class,
        'selected_section': selected_section,
        'selected_date': selected_date,
        'students': students,
    })

def mark_attendance(request):
    if not request.session.get('teacher_id'):
        messages.error(request, 'Please log in to access this page.')
        return redirect('teacher_login')

    if request.method == 'POST':
        selected_class = request.POST.get('class')
        selected_section = request.POST.get('section')
        selected_date = request.POST.get('date')
        with connection.cursor() as cursor:
            for key, value in request.POST.items():
                if key.startswith('student_'):
                    student_id = int(key.split('_')[1])
                    status = value
                    cursor.execute(
                        """
                        SELECT name, admission_number, section
                        FROM student_page1 
                        WHERE user_id = %s
                        """,
                        [student_id]
                    )
                    student_info = cursor.fetchone()
                    if not student_info:
                        messages.error(request, f"Student ID {student_id} not found.")
                        continue
                    name, admission_number, section = student_info
                    
                    try:
                        # Check if attendance record already exists
                        cursor.execute(
                            """
                            SELECT id FROM attendance 
                            WHERE student_id = %s AND class = %s AND section = %s AND date = %s
                            """,
                            [student_id, selected_class, selected_section, selected_date]
                        )
                        existing = cursor.fetchone()
                        if existing:
                            messages.warning(request, f"Attendance for student ID {student_id} on {selected_date} already exists. Teachers cannot update records.")
                            continue
                            
                        # Insert new record in attendance
                        cursor.execute(
                            """
                            INSERT INTO attendance (student_id, class, section, date, status)
                            VALUES (%s, %s, %s, %s, %s)
                            """,
                            [student_id, selected_class, selected_section, selected_date, status]
                        )
                        # Insert in admin_attendance to keep sync
                        cursor.execute(
                            """
                            INSERT INTO admin_attendance (student_id, name, admission_number, class, section, date, status)
                            VALUES (%s, %s, %s, %s, %s, %s, %s)
                            """,
                            [student_id, name, admission_number, selected_class, section, selected_date, status]
                        )
                    except IntegrityError:
                        messages.error(request, f"Duplicate attendance record for student ID {student_id} on {selected_date}.")
                        continue
        messages.success(request, f'Attendance recorded for {selected_class} - {selected_section} on {selected_date}')
        return redirect(f"/teacher_portal/?class={selected_class}&section={selected_section}&date={selected_date}")
    return redirect('teacher_portal')

def admin_attendance_portal(request):
    if not request.session.get('admin_id'):
        messages.error(request, 'Please log in to access this page.')
        return redirect('admin_login')

    today_date = datetime.date.today().strftime('%Y-%m-%d')
    selected_date = request.GET.get('date', today_date)
    
    with connection.cursor() as cursor:
        cursor.execute("SELECT DISTINCT class, section FROM student_page1 WHERE section IS NOT NULL AND section != '' ORDER BY class, section")
        class_sections = [(row[0], row[1]) for row in cursor.fetchall()]
        classes = sorted(set(row[0] for row in class_sections)) or []

    selected_class = request.GET.get('class', '')
    selected_section = request.GET.get('section', '')
    students = []
    
    if selected_class and selected_section:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT user_id, name, admission_number, class, section
                FROM student_page1 
                WHERE class = %s AND section = %s 
                ORDER BY name, admission_number
                """, 
                [selected_class, selected_section]
            )
            students = [
                {
                    'user_id': row[0],
                    'name': row[1],
                    'admission_number': row[2],
                    'class': row[3],
                    'section': row[4] if row[4] else 'N/A'
                } for row in cursor.fetchall()
            ]
            
            cursor.execute(
                """
                SELECT student_id, status 
                FROM admin_attendance 
                WHERE class = %s AND section = %s AND date = %s
                """, 
                [selected_class, selected_section, selected_date]
            )
            attendance_records = {row[0]: row[1] for row in cursor.fetchall()}
            
            for student in students:
                student['status'] = attendance_records.get(student['user_id'], '')

    return render(request, 'users/admin_attendance.html', {
        'classes': classes,
        'class_sections': json.dumps(class_sections),
        'selected_class': selected_class,
        'selected_section': selected_section,
        'selected_date': selected_date,
        'students': students,
    })

def admin_mark_attendance(request):
    if not request.session.get('admin_id'):
        messages.error(request, 'Please log in to access this page.')
        return redirect('admin_login')

    if request.method == 'POST':
        selected_class = request.POST.get('class')
        selected_section = request.POST.get('section')
        selected_date = request.POST.get('date')
        with connection.cursor() as cursor:
            for key, value in request.POST.items():
                if key.startswith('student_'):
                    student_id = int(key.split('_')[1])
                    status = value
                    cursor.execute(
                        """
                        SELECT name, admission_number, section
                        FROM student_page1 
                        WHERE user_id = %s
                        """,
                        [student_id]
                    )
                    student_info = cursor.fetchone()
                    if not student_info:
                        messages.error(request, f"Student ID {student_id} not found.")
                        continue
                    name, admission_number, section = student_info
                    
                    try:
                        cursor.execute(
                            """
                            SELECT id FROM admin_attendance 
                            WHERE student_id = %s AND class = %s AND section = %s AND date = %s
                            """,
                            [student_id, selected_class, selected_section, selected_date]
                        )
                        admin_exists = cursor.fetchone()
                        if admin_exists:
                            cursor.execute(
                                """
                                UPDATE admin_attendance 
                                SET status = %s, name = %s, admission_number = %s, section = %s
                                WHERE student_id = %s AND class = %s AND section = %s AND date = %s
                                """,
                                [status, name, admission_number, section, student_id, selected_class, selected_section, selected_date]
                            )
                            cursor.execute(
                                """
                                SELECT id FROM attendance 
                                WHERE student_id = %s AND class = %s AND section = %s AND date = %s
                                """,
                                [student_id, selected_class, selected_section, selected_date]
                            )
                            att_exists = cursor.fetchone()
                            if att_exists:
                                cursor.execute(
                                    """
                                    UPDATE attendance 
                                    SET status = %s
                                    WHERE student_id = %s AND class = %s AND section = %s AND date = %s
                                    """,
                                    [status, student_id, selected_class, selected_section, selected_date]
                                )
                            else:
                                cursor.execute(
                                    """
                                    INSERT INTO attendance (student_id, class, section, date, status)
                                    VALUES (%s, %s, %s, %s, %s)
                                    """,
                                    [student_id, selected_class, selected_section, selected_date, status]
                                )
                        else:
                            cursor.execute(
                                """
                                INSERT INTO admin_attendance (student_id, name, admission_number, class, section, date, status)
                                VALUES (%s, %s, %s, %s, %s, %s, %s)
                                """,
                                [student_id, name, admission_number, selected_class, section, selected_date, status]
                            )
                            cursor.execute(
                                """
                                INSERT INTO attendance (student_id, class, section, date, status)
                                VALUES (%s, %s, %s, %s, %s)
                                """,
                                [student_id, selected_class, selected_section, selected_date, status]
                            )
                    except IntegrityError:
                        messages.error(request, f"Duplicate attendance record for student ID {student_id} on {selected_date}.")
                        continue
        messages.success(request, f'Attendance updated for {selected_class} - {selected_section} on {selected_date}')
        return redirect(f"/admin_attendance/?class={selected_class}&section={selected_section}&date={selected_date}")
    return redirect('admin_attendance_portal')

def admin_generate_attendance_pdf(request):
    if not request.session.get('admin_id'):
        messages.error(request, 'Please log in to access this page.')
        return redirect('admin_login')

    selected_class = request.GET.get('class')
    selected_section = request.GET.get('section')
    selected_date = request.GET.get('date')

    # Input validation
    if not all([selected_class, selected_section, selected_date]):
        messages.error(request, 'Please select class, section, and date to generate the PDF.')
        return redirect('admin_attendance_portal')

    # Debugging logs
    print(f"Generating PDF - Class: {selected_class}, Section: {selected_section}, Date: {selected_date}")

    with connection.cursor() as cursor:
        cursor.execute(
            """
            SELECT s.user_id, s.name, s.admission_number, s.section, a.status 
            FROM student_page1 s
            LEFT JOIN admin_attendance a ON s.user_id = a.student_id 
                AND a.class = %s AND a.section = %s AND a.date = %s
            WHERE s.class = %s AND COALESCE(s.section, '') = COALESCE(%s, '')
            ORDER BY s.name, s.admission_number
            """,
            [selected_class, selected_section, selected_date, selected_class, selected_section]
        )
        data = cursor.fetchall()
        print(f"Fetched {len(data)} records: {data}")

    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, topMargin=0.5*inch, bottomMargin=0.5*inch)
    elements = []
    styles = getSampleStyleSheet()
    
    header_style = ParagraphStyle(
        name='Header',
        parent=styles['Heading2'],
        fontSize=16,
        alignment=1,
        textColor=colors.HexColor('#1e40af'),
        spaceAfter=10
    )
    subheader_style = ParagraphStyle(
        name='Subheader',
        parent=styles['Normal'],
        fontSize=12,
        alignment=1,
        textColor=colors.HexColor('#1f2937'),
        spaceAfter=10
    )
    no_data_style = ParagraphStyle(
        name='NoData',
        parent=styles['Normal'],
        fontSize=12,
        alignment=1,
        textColor=colors.HexColor('#dc2626'),
        spaceAfter=10
    )
    
    logo_url = "https://via.placeholder.com/80"
    logo_img = None
    try:
        response = requests.get(logo_url, stream=True)
        if response.status_code == 200:
            logo_data = BytesIO(response.content)
            logo_img = Image(logo_data, width=0.8*inch, height=0.8*inch)
            logo_img.hAlign = 'LEFT'
            elements.append(logo_img)
    except Exception as e:
        print(f"Failed to load logo: {e}")
    
    elements.append(Paragraph("Manavargal School Management System", header_style))
    elements.append(Paragraph("Admin Attendance Report", header_style))
    elements.append(Paragraph(f"Class: {selected_class} | Section: {selected_section} | Date: {selected_date}", subheader_style))
    elements.append(Paragraph(f"Generated on: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", subheader_style))
    elements.append(Spacer(1, 0.25*inch))
    
    if data:
        table_data = [['Student ID', 'Name', 'Admission Number', 'Class', 'Section', 'Status']]
        for row in data:
            status = row[4] if row[4] else 'Not Marked'
            table_data.append([
                str(row[0]),
                row[1] if row[1] else 'N/A',
                row[2] if row[2] else 'N/A',
                selected_class,
                row[3] if row[3] else 'N/A',
                status.capitalize()
            ])
        table = Table(table_data, colWidths=[0.75*inch, 1.5*inch, 1.75*inch, 1*inch, 1*inch, 1*inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1e40af')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
            ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#f8fafd')),
            ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#bfdbfe')),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 10),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ]))
        elements.append(table)
    else:
        elements.append(Paragraph("No attendance records found for the selected class, section, and date.", no_data_style))
    
    doc.build(elements)
    pdf = buffer.getvalue()
    buffer.close()
    
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="Admin_Attendance_{selected_class}_{selected_section}_{selected_date}.pdf"'
    response.write(pdf)
    return response



def student_portal(request):
    if "user_id" not in request.session:
        return redirect("/")
    
    user_id = request.session['user_id']
    selected_date = request.GET.get('date', '')
    
    with connection.cursor() as cursor:
        if selected_date:
            cursor.execute(
                """
                SELECT a.date, s.admission_number, s.name, a.class, a.section, a.status 
                FROM attendance a
                JOIN student_page1 s ON a.student_id = s.user_id
                WHERE s.user_id = %s AND a.date = %s
                ORDER BY a.date DESC
                """,
                [user_id, selected_date]
            )
        else:
            cursor.execute(
                """
                SELECT a.date, s.admission_number, s.name, a.class, a.section, a.status
                FROM attendance a
                JOIN student_page1 s ON a.student_id = s.user_id
                WHERE s.user_id = %s
                ORDER BY a.date DESC
                """,
                [user_id]
            )
        attendance_records = [
            {
                'date': row[0],
                'admission_number': row[1],
                'name': row[2],
                'class': row[3],
                'section': row[4] if row[4] else 'N/A',
                'status': row[5]
            } for row in cursor.fetchall()
        ]

    return render(request, 'users/student_attendance.html', {
        'attendance_records': attendance_records,
        'selected_date': selected_date
    })


from django.shortcuts import render, redirect
from django.contrib import messages
from django.db import connection

def parent_signup(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')

        # Validate inputs
        if not all([username, email, password, confirm_password]):
            return render(request, 'users/parent_signup.html', {'error': 'All fields are required'})

        # Check if passwords match
        if password != confirm_password:
            return render(request, 'users/parent_signup.html', {'error': 'Passwords do not match'})

        # Check if username or email already exists
        with connection.cursor() as cursor:
            cursor.execute("SELECT COUNT(*) FROM users WHERE username = %s", [username])
            if cursor.fetchone()[0] > 0:
                return render(request, 'users/parent_signup.html', {'error': 'Username already exists'})
            
            cursor.execute("SELECT COUNT(*) FROM users WHERE email = %s", [email])
            if cursor.fetchone()[0] > 0:
                return render(request, 'users/parent_signup.html', {'error': 'Email already exists'})

            # Insert new user with plain text password
            try:
                cursor.execute(
                    "INSERT INTO users (username, email, password) VALUES (%s, %s, %s)",
                    [username, email, password]
                )
                connection.commit()
                messages.success(request, 'Account created successfully! Please log in.')
                return redirect('parent_login')
            except Exception as e:
                connection.rollback()
                return render(request, 'users/parent_signup.html', {'error': 'An error occurred during signup: ' + str(e)})
    
    return render(request, 'users/parent_signup.html')

from django.shortcuts import render, redirect
from django.contrib import messages
from django.db import connection

def parent_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        # Validate inputs
        if not all([username, password]):
            return render(request, 'users/parent_login.html', {'error': 'All fields are required'})

        # Authenticate user by comparing plain text password
        with connection.cursor() as cursor:
            cursor.execute("SELECT id, password FROM users WHERE username = %s", [username])
            result = cursor.fetchone()
            if result and result[1] == password:
                # Set session for authenticated user
                request.session['user_id'] = result[0]
                messages.success(request, 'Logged in successfully!')
                return redirect('parent_dashboard')
            else:
                return render(request, 'users/parent_login.html', {'error': 'Invalid username or password'})

    return render(request, 'users/parent_login.html')

from django.shortcuts import render, redirect
from django.contrib import messages
from django.db import connection

def parent_dashboard(request):
    if 'user_id' not in request.session:
        messages.error(request, 'Please log in to access the dashboard.')
        return redirect('parent_login')

    # Fetch username from users table
    admin_name = "Guest"
    with connection.cursor() as cursor:
        cursor.execute("SELECT username FROM users WHERE id = %s", [request.session['user_id']])
        result = cursor.fetchone()
        if result:
            admin_name = result[0]

    return render(request, 'users/parent_dashboard.html', {'admin_name': admin_name})




from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.contrib import messages
from django.db import connection
import json

def mark_entry(request):
    if 'teacher_id' not in request.session:
        messages.error(request, 'Please log in to access the mark entry system.')
        return redirect('teacher_login')

    with connection.cursor() as cursor:
        # Get teacher details
        cursor.execute(
            "SELECT subject, class_teacher_of, name FROM teachers WHERE id = %s",
            [request.session['teacher_id']]
        )
        teacher = cursor.fetchone()
        if not teacher:
            messages.error(request, 'Teacher not found.')
            return redirect('teacher_login')

        role = 'classTeacher' if teacher[1] else 'subjectTeacher'
        teacher_subject = teacher[0] if role == 'subjectTeacher' else None
        teacher_name = teacher[2]

        # Get distinct classes and sections
        cursor.execute("SELECT DISTINCT class FROM student_page1 ORDER BY class")
        classes = [row[0] for row in cursor.fetchall()]
        cursor.execute("SELECT DISTINCT section FROM student_page1 WHERE section IS NOT NULL ORDER BY section")
        sections = [row[0] for row in cursor.fetchall()]

        # Default class and section
        default_class = ''
        default_section = ''
        if teacher[1]:
            try:
                class_section = teacher[1].split('-')
                if len(class_section) == 2:
                    default_class, default_section = class_section
                else:
                    messages.warning(request, 'Invalid class_teacher_of format.')
            except Exception as e:
                messages.error(request, f'Error parsing class_teacher_of: {str(e)}')

        selected_class = request.GET.get('class', default_class or (classes[0] if classes else ''))
        selected_section = request.GET.get('section', default_section or (sections[0] if sections else ''))

        # Validate class and section
        if selected_class not in classes or selected_section not in sections:
            selected_class = classes[0] if classes else ''
            selected_section = sections[0] if sections else ''
            if not classes or not sections:
                messages.warning(request, 'No classes or sections found.')

        # Get subjects for selected class
        subjects = []
        if selected_class:
            cursor.execute(
                "SELECT id, name, max_marks FROM school_subjects WHERE class = %s ORDER BY name",
                [selected_class]
            )
            subjects = [{'id': row[0], 'name': row[1], 'max_marks': row[2]} for row in cursor.fetchall()]

        # Get students for selected class and section
        students = []
        if selected_class and selected_section:
            cursor.execute(
                "SELECT id, name, roll_number FROM student_page1 WHERE class = %s AND section = %s ORDER BY name",
                [selected_class, selected_section]
            )
            students = [{'id': row[0], 'name': row[1], 'roll_number': row[2]} for row in cursor.fetchall()]

    return render(request, 'users/mark.html', {
        'subjects': subjects,
        'students': students,
        'teacher_name': teacher_name,
        'role': role,
        'teacher_subject': teacher_subject,
        'classes': classes,
        'sections': sections,
        'selected_class': selected_class,
        'selected_section': selected_section
    })

def save_marks(request):
    if 'teacher_id' not in request.session:
        return JsonResponse({'success': False, 'message': 'Please log in.'}, status=403)

    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            role = data.get('role')
            student_id = data.get('studentId')
            marks_data = data.get('marks')
            class_name = data.get('class')
            section = data.get('section')

            if not all([student_id, role, marks_data, class_name, section]):
                return JsonResponse({'success': False, 'message': 'Missing required fields.'}, status=400)

            with connection.cursor() as cursor:
                # Verify teacher role
                cursor.execute(
                    "SELECT subject, class_teacher_of FROM teachers WHERE id = %s",
                    [request.session['teacher_id']]
                )
                teacher = cursor.fetchone()
                expected_role = 'classTeacher' if teacher[1] else 'subjectTeacher'
                if role != expected_role:
                    return JsonResponse({'success': False, 'message': 'Invalid role.'}, status=403)

                # Verify student, class, and section
                cursor.execute(
                    "SELECT user_id FROM student_page1 WHERE user_id = %s AND class = %s AND section = %s",
                    [student_id, class_name, section]
                )
                if not cursor.fetchone():
                    return JsonResponse({'success': False, 'message': 'Invalid student, class, or section.'}, status=400)

                # Store signature
                signature = marks_data[0].get('signature') if isinstance(marks_data, list) else marks_data.get('signature')
                if not signature:
                    return JsonResponse({'success': False, 'message': 'Signature is required.'}, status=400)
                cursor.execute(
                    "INSERT INTO teacher_signature (teacher_id, signature) VALUES (%s, %s) ON DUPLICATE KEY UPDATE signature=%s",
                    [request.session['teacher_id'], signature, signature]
                )

                def calculate_grade(marks, max_marks):
                    percentage = (marks / max_marks * 100) if max_marks > 0 else 0
                    return 'A' if percentage >= 80 else 'B' if percentage >= 60 else 'C' if percentage >= 40 else 'D' if percentage >= 33 else 'E'

                if role == 'subjectTeacher':
                    subject_id = marks_data.get('subjectId')
                    marks = marks_data.get('marks')
                    max_marks = marks_data.get('maxMarks')

                    if not all([subject_id, marks is not None, max_marks]):
                        return JsonResponse({'success': False, 'message': 'Invalid subject or marks.'}, status=400)

                    cursor.execute(
                        "SELECT name FROM school_subjects WHERE id = %s AND class = %s",
                        [subject_id, class_name]
                    )
                    subject_name = cursor.fetchone()
                    if not subject_name or subject_name[0] != teacher[0]:
                        return JsonResponse({'success': False, 'message': 'Unauthorized subject or class.'}, status=403)

                    marks = int(marks)
                    max_marks = int(max_marks)
                    if marks < 0 or max_marks < 1 or marks > max_marks:
                        return JsonResponse({'success': False, 'message': 'Invalid marks or max marks.'}, status=400)

                    grade = calculate_grade(marks, max_marks)
                    cursor.execute(
                        "INSERT INTO school_marks (student_id, subject_id, marks, max_marks, grade) VALUES (%s, %s, %s, %s, %s) ON DUPLICATE KEY UPDATE marks=%s, max_marks=%s, grade=%s",
                        [student_id, subject_id, marks, max_marks, grade, marks, max_marks, grade]
                    )
                else:
                    for subject in marks_data:
                        subject_id = subject.get('subjectId')
                        marks = subject.get('marks')
                        max_marks = subject.get('maxMarks')

                        if not all([subject_id, marks is not None, max_marks]):
                            return JsonResponse({'success': False, 'message': 'Invalid subject or marks.'}, status=400)

                        cursor.execute(
                            "SELECT name FROM school_subjects WHERE id = %s AND class = %s",
                            [subject_id, class_name]
                        )
                        if not cursor.fetchone():
                            return JsonResponse({'success': False, 'message': 'Subject not found for this class.'}, status=404)

                        marks = int(marks)
                        max_marks = int(max_marks)
                        if marks < 0 or max_marks < 1 or marks > max_marks:
                            return JsonResponse({'success': False, 'message': 'Invalid marks or max marks.'}, status=400)

                        grade = calculate_grade(marks, max_marks)
                        cursor.execute(
                            "INSERT INTO school_marks (student_id, subject_id, marks, max_marks, grade) VALUES (%s, %s, %s, %s, %s) ON DUPLICATE KEY UPDATE marks=%s, max_marks=%s, grade=%s",
                            [student_id, subject_id, marks, max_marks, grade, marks, max_marks, grade]
                        )

                connection.commit()
                return JsonResponse({'success': True, 'message': 'Marks saved successfully.'})

        except Exception as e:
            connection.rollback()
            return JsonResponse({'success': False, 'message': f'Error saving marks: {str(e)}'}, status=500)

    return JsonResponse({'success': False, 'message': 'Invalid request method.'}, status=405)

def add_subject(request):
    if 'teacher_id' not in request.session:
        return JsonResponse({'success': False, 'message': 'Please log in.'}, status=403)

    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            subject_name = data.get('subjectName')
            max_marks = data.get('maxMarks')
            class_name = data.get('class')

            if not all([subject_name, max_marks, class_name]):
                return JsonResponse({'success': False, 'message': 'Subject name, max marks, and class required.'}, status=400)

            max_marks = int(max_marks)
            if max_marks < 1:
                return JsonResponse({'success': False, 'message': 'Max marks must be positive.'}, status=400)

            with connection.cursor() as cursor:
                cursor.execute("SELECT COUNT(*) FROM student_page1 WHERE class = %s", [class_name])
                if cursor.fetchone()[0] == 0:
                    return JsonResponse({'success': False, 'message': 'Invalid class.'}, status=400)

                cursor.execute(
                    "SELECT COUNT(*) FROM school_subjects WHERE name = %s AND class = %s",
                    [subject_name, class_name]
                )
                if cursor.fetchone()[0] > 0:
                    return JsonResponse({'success': False, 'message': 'Subject already exists for this class.'}, status=400)

                cursor.execute(
                    "INSERT INTO school_subjects (name, max_marks, class) VALUES (%s, %s, %s)",
                    [subject_name, max_marks, class_name]
                )
                connection.commit()

                cursor.execute(
                    "SELECT id, name, max_marks FROM school_subjects WHERE class = %s ORDER BY name",
                    [class_name]
                )
                subjects = [{'id': row[0], 'name': row[1], 'max_marks': row[2]} for row in cursor.fetchall()]

                return JsonResponse({'success': True, 'message': f'Subject {subject_name} added for class {class_name}.', 'subjects': subjects})

        except Exception as e:
            connection.rollback()
            return JsonResponse({'success': False, 'message': f'Error adding subject: {str(e)}'}, status=500)

    return JsonResponse({'success': False, 'message': 'Invalid request method.'}, status=405)

def delete_subject(request):
    if 'teacher_id' not in request.session:
        return JsonResponse({'success': False, 'message': 'Please log in.'}, status=403)

    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            subject_id = data.get('subjectId')
            class_name = data.get('class')

            if not all([subject_id, class_name]):
                return JsonResponse({'success': False, 'message': 'Subject ID and class required.'}, status=400)

            with connection.cursor() as cursor:
                cursor.execute("SELECT COUNT(*) FROM student_page1 WHERE class = %s", [class_name])
                if cursor.fetchone()[0] == 0:
                    return JsonResponse({'success': False, 'message': 'Invalid class.'}, status=400)

                cursor.execute(
                    "SELECT name FROM school_subjects WHERE id = %s AND class = %s",
                    [subject_id, class_name]
                )
                subject = cursor.fetchone()
                if not subject:
                    return JsonResponse({'success': False, 'message': 'Subject not found for this class.'}, status=404)

                cursor.execute("DELETE FROM school_marks WHERE subject_id = %s", [subject_id])
                cursor.execute("DELETE FROM school_subjects WHERE id = %s", [subject_id])
                connection.commit()

                cursor.execute(
                    "SELECT id, name, max_marks FROM school_subjects WHERE class = %s ORDER BY name",
                    [class_name]
                )
                subjects = [{'id': row[0], 'name': row[1], 'max_marks': row[2]} for row in cursor.fetchall()]

                return JsonResponse({'success': True, 'message': f'Subject {subject[0]} deleted for class {class_name}.', 'subjects': subjects})

        except Exception as e:
            connection.rollback()
            return JsonResponse({'success': False, 'message': f'Error deleting subject: {str(e)}'}, status=500)

    return JsonResponse({'success': False, 'message': 'Invalid request method.'}, status=405)

from django.http import JsonResponse
from django.db import connection
import json

def progress_card(request):
    if 'teacher_id' not in request.session:
        return JsonResponse({'success': False, 'message': 'Please log in.'}, status=403)

    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            student_id = data.get('studentId')

            if not student_id:
                return JsonResponse({'success': False, 'message': 'Student ID required.'}, status=400)

            with connection.cursor() as cursor:
                # Fetch student details including profile picture
                cursor.execute(
                    """
                    SELECT s.name, s.roll_number, s.class, s.section, p.image_path
                    FROM student_page1 s
                    LEFT JOIN profile_pics p ON s.user_id = p.user_id
                    WHERE s.user_id = %s
                    """,
                    [student_id]
                )
                student = cursor.fetchone()
                if not student:
                    return JsonResponse({'success': False, 'message': 'Student not found.'}, status=404)

                # Fetch marks
                cursor.execute(
                    """
                    SELECT s.name, m.marks, m.max_marks, m.grade
                    FROM school_marks m
                    JOIN school_subjects s ON m.subject_id = s.id
                    WHERE m.student_id = %s AND s.class = %s
                    """,
                    [student_id, student[2]]
                )
                marks = [{'subject': row[0], 'marks': row[1], 'max_marks': row[2], 'grade': row[3]} for row in cursor.fetchall()]

                # Fetch teacher signature
                cursor.execute(
                    "SELECT signature FROM teacher_signature WHERE teacher_id = %s",
                    [request.session['teacher_id']]
                )
                signature_row = cursor.fetchone()
                signature = signature_row[0] if signature_row else None

                # Fetch teacher name
                cursor.execute("SELECT name FROM teachers WHERE id = %s", [request.session['teacher_id']])
                teacher_name = cursor.fetchone()[0]

                # Calculate totals and grade
                total_marks = sum(mark['marks'] for mark in marks)
                total_max_marks = sum(mark['max_marks'] for mark in marks)
                percentage = (total_marks / total_max_marks * 100) if total_max_marks > 0 else 0
                grade = 'A' if percentage >= 80 else 'B' if percentage >= 60 else 'C' if percentage >= 40 else 'D' if percentage >= 33 else 'E'
                passed = all(mark['marks'] >= 0.33 * mark['max_marks'] for mark in marks) and marks

                # Prepare response
                response_data = {
                    'success': True,
                    'student': {
                        'name': student[0],
                        'roll_number': student[1],
                        'class': student[2],
                        'section': student[3],
                        'image_path': student[4] or 'pfpics/default_profile.jpg'  # Fallback to default
                    },
                    'marks': marks,
                    'total_marks': total_marks,
                    'total_max_marks': total_max_marks,
                    'percentage': round(percentage, 2),
                    'grade': grade,
                    'status': 'Pass' if passed else 'Fail',
                    'teacher_name': teacher_name
                }
                if signature:
                    response_data['signature'] = signature
                return JsonResponse(response_data)

        except Exception as e:
            return JsonResponse({'success': False, 'message': f'Error fetching progress card: {str(e)}'}, status=500)

    return JsonResponse({'success': False, 'message': 'Invalid request method.'}, status=405)

def get_students(request):
    if 'teacher_id' not in request.session:
        return JsonResponse({'success': False, 'message': 'Please log in.'}, status=403)

    try:
        class_name = request.GET.get('class')
        section = request.GET.get('section')

        if not class_name or not section:
            return JsonResponse({'success': False, 'message': 'Class and section required.'}, status=400)

        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT user_id AS id, name, roll_number FROM student_page1 WHERE class = %s AND section = %s ORDER BY name",
                [class_name, section]
            )
            students = [{'id': row[0], 'name': row[1], 'roll_number': row[2]} for row in cursor.fetchall()]
            return JsonResponse({'success': True, 'students': students})
    except Exception as e:
        return JsonResponse({'success': False, 'message': f'Error fetching students: {str(e)}'}, status=500)


def get_subjects(request):
    if 'teacher_id' not in request.session:
        return JsonResponse({'success': False, 'message': 'Please log in.'}, status=403)

    try:
        class_name = request.GET.get('class')
        if not class_name:
            return JsonResponse({'success': False, 'message': 'Class required.'}, status=400)

        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT id, name, max_marks FROM school_subjects WHERE class = %s ORDER BY name",
                [class_name]
            )
            subjects = [{'id': row[0], 'name': row[1], 'max_marks': row[2]} for row in cursor.fetchall()]
            return JsonResponse({'success': True, 'subjects': subjects})
    except Exception as e:
        return JsonResponse({'success': False, 'message': f'Error fetching subjects: {str(e)}'}, status=500)





from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.contrib import messages
from django.db import connection
import json

def teacher_mark_entry(request):
    if 'teacher_id' not in request.session:
        messages.error(request, 'Please log in to access the mark entry system.')
        return redirect('teacher_login')

    with connection.cursor() as cursor:
        # Get teacher details
        cursor.execute(
            "SELECT subject, class_teacher_of, name FROM teachers WHERE id = %s",
            [request.session['teacher_id']]
        )
        teacher = cursor.fetchone()
        if not teacher:
            messages.error(request, 'Teacher not found.')
            return redirect('teacher_login')

        role = 'classTeacher' if teacher[1] else 'subjectTeacher'
        teacher_subject = teacher[0] if role == 'subjectTeacher' else None
        teacher_name = teacher[2]

        # Get distinct classes and sections
        cursor.execute("SELECT DISTINCT class FROM student_page1 ORDER BY class")
        classes = [row[0] for row in cursor.fetchall()]
        cursor.execute("SELECT DISTINCT section FROM student_page1 WHERE section IS NOT NULL ORDER BY section")
        sections = [row[0] for row in cursor.fetchall()]

        # Default class and section
        default_class = ''
        default_section = ''
        if teacher[1]:
            try:
                class_section = teacher[1].split('-')
                if len(class_section) == 2:
                    default_class, default_section = class_section
                else:
                    messages.warning(request, 'Invalid class_teacher_of format.')
            except Exception as e:
                messages.error(request, f'Error parsing class_teacher_of: {str(e)}')

        selected_class = request.GET.get('class', default_class or (classes[0] if classes else ''))
        selected_section = request.GET.get('section', default_section or (sections[0] if sections else ''))

        # Validate class and section
        if selected_class not in classes or selected_section not in sections:
            selected_class = classes[0] if classes else ''
            selected_section = sections[0] if sections else ''
            if not classes or not sections:
                messages.warning(request, 'No classes or sections found.')

        # Get subjects for selected class
        subjects = []
        if selected_class:
            cursor.execute(
                "SELECT id, name, max_marks FROM school_subjects WHERE class = %s ORDER BY name",
                [selected_class]
            )
            subjects = [{'id': row[0], 'name': row[1], 'max_marks': row[2]} for row in cursor.fetchall()]

        # Get students for selected class and section
        students = []
        if selected_class and selected_section:
            cursor.execute(
                "SELECT id, name, roll_number FROM student_page1 WHERE class = %s AND section = %s ORDER BY name",
                [selected_class, selected_section]
            )
            students = [{'id': row[0], 'name': row[1], 'roll_number': row[2]} for row in cursor.fetchall()]

    return render(request, 'users/teacher_mark_entry.html', {
        'subjects': subjects,
        'students': students,
        'teacher_name': teacher_name,
        'role': role,
        'teacher_subject': teacher_subject,
        'classes': classes,
        'sections': sections,
        'selected_class': selected_class,
        'selected_section': selected_section
    })

def teacher_save_marks(request):
    if 'teacher_id' not in request.session:
        return JsonResponse({'success': False, 'message': 'Please log in.'}, status=403)

    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            role = data.get('role')
            student_id = data.get('studentId')
            marks_data = data.get('marks')
            class_name = data.get('class')
            section = data.get('section')

            if not all([student_id, role, marks_data, class_name, section]):
                return JsonResponse({'success': False, 'message': 'Missing required fields.'}, status=400)

            with connection.cursor() as cursor:
                # Verify teacher role
                cursor.execute(
                    "SELECT subject, class_teacher_of FROM teachers WHERE id = %s",
                    [request.session['teacher_id']]
                )
                teacher = cursor.fetchone()
                expected_role = 'classTeacher' if teacher[1] else 'subjectTeacher'
                if role != expected_role:
                    return JsonResponse({'success': False, 'message': 'Invalid role.'}, status=403)

                # Verify student, class, and section
                cursor.execute(
                    "SELECT user_id FROM student_page1 WHERE user_id = %s AND class = %s AND section = %s",
                    [student_id, class_name, section]
                )
                if not cursor.fetchone():
                    return JsonResponse({'success': False, 'message': 'Invalid student, class, or section.'}, status=400)

                # Store signature
                signature = marks_data[0].get('signature') if isinstance(marks_data, list) else marks_data.get('signature')
                if not signature:
                    return JsonResponse({'success': False, 'message': 'Signature is required.'}, status=400)
                cursor.execute(
                    "INSERT INTO teacher_signature (teacher_id, signature) VALUES (%s, %s) ON DUPLICATE KEY UPDATE signature=%s",
                    [request.session['teacher_id'], signature, signature]
                )

                def calculate_grade(marks, max_marks):
                    percentage = (marks / max_marks * 100) if max_marks > 0 else 0
                    return 'A' if percentage >= 80 else 'B' if percentage >= 60 else 'C' if percentage >= 40 else 'D' if percentage >= 33 else 'E'

                if role == 'subjectTeacher':
                    subject_id = marks_data.get('subjectId')
                    marks = marks_data.get('marks')
                    max_marks = marks_data.get('maxMarks')

                    if not all([subject_id, marks is not None, max_marks]):
                        return JsonResponse({'success': False, 'message': 'Invalid subject or marks.'}, status=400)

                    cursor.execute(
                        "SELECT name FROM school_subjects WHERE id = %s AND class = %s",
                        [subject_id, class_name]
                    )
                    subject_name = cursor.fetchone()
                    if not subject_name or subject_name[0] != teacher[0]:
                        return JsonResponse({'success': False, 'message': 'Unauthorized subject or class.'}, status=403)

                    marks = int(marks)
                    max_marks = int(max_marks)
                    if marks < 0 or max_marks < 1 or marks > max_marks:
                        return JsonResponse({'success': False, 'message': 'Invalid marks or max marks.'}, status=400)

                    grade = calculate_grade(marks, max_marks)
                    cursor.execute(
                        "INSERT INTO school_marks (student_id, subject_id, marks, max_marks, grade) VALUES (%s, %s, %s, %s, %s) ON DUPLICATE KEY UPDATE marks=%s, max_marks=%s, grade=%s",
                        [student_id, subject_id, marks, max_marks, grade, marks, max_marks, grade]
                    )
                else:
                    for subject in marks_data:
                        subject_id = subject.get('subjectId')
                        marks = subject.get('marks')
                        max_marks = subject.get('maxMarks')

                        if not all([subject_id, marks is not None, max_marks]):
                            return JsonResponse({'success': False, 'message': 'Invalid subject or marks.'}, status=400)

                        cursor.execute(
                            "SELECT name FROM school_subjects WHERE id = %s AND class = %s",
                            [subject_id, class_name]
                        )
                        if not cursor.fetchone():
                            return JsonResponse({'success': False, 'message': 'Subject not found for this class.'}, status=404)

                        marks = int(marks)
                        max_marks = int(max_marks)
                        if marks < 0 or max_marks < 1 or marks > max_marks:
                            return JsonResponse({'success': False, 'message': 'Invalid marks or max marks.'}, status=400)

                        grade = calculate_grade(marks, max_marks)
                        cursor.execute(
                            "INSERT INTO school_marks (student_id, subject_id, marks, max_marks, grade) VALUES (%s, %s, %s, %s, %s) ON DUPLICATE KEY UPDATE marks=%s, max_marks=%s, grade=%s",
                            [student_id, subject_id, marks, max_marks, grade, marks, max_marks, grade]
                        )

                connection.commit()
                return JsonResponse({'success': True, 'message': 'Marks saved successfully.'})

        except Exception as e:
            connection.rollback()
            return JsonResponse({'success': False, 'message': f'Error saving marks: {str(e)}'}, status=500)

    return JsonResponse({'success': False, 'message': 'Invalid request method.'}, status=405)

def teacher_add_subject(request):
    if 'teacher_id' not in request.session:
        return JsonResponse({'success': False, 'message': 'Please log in.'}, status=403)

    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            subject_name = data.get('subjectName')
            max_marks = data.get('maxMarks')
            class_name = data.get('class')

            if not all([subject_name, max_marks, class_name]):
                return JsonResponse({'success': False, 'message': 'Subject name, max marks, and class required.'}, status=400)

            max_marks = int(max_marks)
            if max_marks < 1:
                return JsonResponse({'success': False, 'message': 'Max marks must be positive.'}, status=400)

            with connection.cursor() as cursor:
                cursor.execute("SELECT COUNT(*) FROM student_page1 WHERE class = %s", [class_name])
                if cursor.fetchone()[0] == 0:
                    return JsonResponse({'success': False, 'message': 'Invalid class.'}, status=400)

                cursor.execute(
                    "SELECT COUNT(*) FROM school_subjects WHERE name = %s AND class = %s",
                    [subject_name, class_name]
                )
                if cursor.fetchone()[0] > 0:
                    return JsonResponse({'success': False, 'message': 'Subject already exists for this class.'}, status=400)

                cursor.execute(
                    "INSERT INTO school_subjects (name, max_marks, class) VALUES (%s, %s, %s)",
                    [subject_name, max_marks, class_name]
                )
                connection.commit()

                cursor.execute(
                    "SELECT id, name, max_marks FROM school_subjects WHERE class = %s ORDER BY name",
                    [class_name]
                )
                subjects = [{'id': row[0], 'name': row[1], 'max_marks': row[2]} for row in cursor.fetchall()]

                return JsonResponse({'success': True, 'message': f'Subject {subject_name} added for class {class_name}.', 'subjects': subjects})

        except Exception as e:
            connection.rollback()
            return JsonResponse({'success': False, 'message': f'Error adding subject: {str(e)}'}, status=500)

    return JsonResponse({'success': False, 'message': 'Invalid request method.'}, status=405)

def teacher_delete_subject(request):
    if 'teacher_id' not in request.session:
        return JsonResponse({'success': False, 'message': 'Please log in.'}, status=403)

    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            subject_id = data.get('subjectId')
            class_name = data.get('class')

            if not all([subject_id, class_name]):
                return JsonResponse({'success': False, 'message': 'Subject ID and class required.'}, status=400)

            with connection.cursor() as cursor:
                cursor.execute("SELECT COUNT(*) FROM student_page1 WHERE class = %s", [class_name])
                if cursor.fetchone()[0] == 0:
                    return JsonResponse({'success': False, 'message': 'Invalid class.'}, status=400)

                cursor.execute(
                    "SELECT name FROM school_subjects WHERE id = %s AND class = %s",
                    [subject_id, class_name]
                )
                subject = cursor.fetchone()
                if not subject:
                    return JsonResponse({'success': False, 'message': 'Subject not found for this class.'}, status=404)

                cursor.execute("DELETE FROM school_marks WHERE subject_id = %s", [subject_id])
                cursor.execute("DELETE FROM school_subjects WHERE id = %s", [subject_id])
                connection.commit()

                cursor.execute(
                    "SELECT id, name, max_marks FROM school_subjects WHERE class = %s ORDER BY name",
                    [class_name]
                )
                subjects = [{'id': row[0], 'name': row[1], 'max_marks': row[2]} for row in cursor.fetchall()]

                return JsonResponse({'success': True, 'message': f'Subject {subject[0]} deleted for class {class_name}.', 'subjects': subjects})

        except Exception as e:
            connection.rollback()
            return JsonResponse({'success': False, 'message': f'Error deleting subject: {str(e)}'}, status=500)

    return JsonResponse({'success': False, 'message': 'Invalid request method.'}, status=405)

def teacher_progress_card(request):
    if 'teacher_id' not in request.session:
        return JsonResponse({'success': False, 'message': 'Please log in.'}, status=403)

    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            student_id = data.get('studentId')

            if not student_id:
                return JsonResponse({'success': False, 'message': 'Student ID required.'}, status=400)

            with connection.cursor() as cursor:
                # Fetch student details including profile picture
                cursor.execute(
                    """
                    SELECT s.name, s.roll_number, s.class, s.section, p.image_path
                    FROM student_page1 s
                    LEFT JOIN profile_pics p ON s.user_id = p.user_id
                    WHERE s.user_id = %s
                    """,
                    [student_id]
                )
                student = cursor.fetchone()
                if not student:
                    return JsonResponse({'success': False, 'message': 'Student not found.'}, status=404)

                # Fetch marks
                cursor.execute(
                    """
                    SELECT s.name, m.marks, m.max_marks, m.grade
                    FROM school_marks m
                    JOIN school_subjects s ON m.subject_id = s.id
                    WHERE m.student_id = %s AND s.class = %s
                    """,
                    [student_id, student[2]]
                )
                marks = [{'subject': row[0], 'marks': row[1], 'max_marks': row[2], 'grade': row[3]} for row in cursor.fetchall()]

                # Fetch teacher signature
                cursor.execute(
                    "SELECT signature FROM teacher_signature WHERE teacher_id = %s",
                    [request.session['teacher_id']]
                )
                signature_row = cursor.fetchone()
                signature = signature_row[0] if signature_row else None

                # Fetch teacher name
                cursor.execute("SELECT name FROM teachers WHERE id = %s", [request.session['teacher_id']])
                teacher_name = cursor.fetchone()[0]

                # Calculate totals and grade
                total_marks = sum(mark['marks'] for mark in marks)
                total_max_marks = sum(mark['max_marks'] for mark in marks)
                percentage = (total_marks / total_max_marks * 100) if total_max_marks > 0 else 0
                grade = 'A' if percentage >= 80 else 'B' if percentage >= 60 else 'C' if percentage >= 40 else 'D' if percentage >= 33 else 'E'
                passed = all(mark['marks'] >= 0.33 * mark['max_marks'] for mark in marks) and marks

                # Prepare response
                response_data = {
                    'success': True,
                    'student': {
                        'name': student[0],
                        'roll_number': student[1],
                        'class': student[2],
                        'section': student[3],
                        'image_path': student[4] or 'pfpics/default_profile.jpg'  # Fallback to default
                    },
                    'marks': marks,
                    'total_marks': total_marks,
                    'total_max_marks': total_max_marks,
                    'percentage': round(percentage, 2),
                    'grade': grade,
                    'status': 'Pass' if passed else 'Fail',
                    'teacher_name': teacher_name
                }
                if signature:
                    response_data['signature'] = signature
                return JsonResponse(response_data)

        except Exception as e:
            return JsonResponse({'success': False, 'message': f'Error fetching progress card: {str(e)}'}, status=500)

    return JsonResponse({'success': False, 'message': 'Invalid request method.'}, status=405)

def teacher_get_students(request):
    if 'teacher_id' not in request.session:
        return JsonResponse({'success': False, 'message': 'Please log in.'}, status=403)

    try:
        class_name = request.GET.get('class')
        section = request.GET.get('section')

        if not class_name or not section:
            return JsonResponse({'success': False, 'message': 'Class and section required.'}, status=400)

        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT user_id AS id, name, roll_number FROM student_page1 WHERE class = %s AND section = %s ORDER BY name",
                [class_name, section]
            )
            students = [{'id': row[0], 'name': row[1], 'roll_number': row[2]} for row in cursor.fetchall()]
            return JsonResponse({'success': True, 'students': students})
    except Exception as e:
        return JsonResponse({'success': False, 'message': f'Error fetching students: {str(e)}'}, status=500)

def teacher_get_subjects(request):
    if 'teacher_id' not in request.session:
        return JsonResponse({'success': False, 'message': 'Please log in.'}, status=403)

    try:
        class_name = request.GET.get('class')
        if not class_name:
            return JsonResponse({'success': False, 'message': 'Class required.'}, status=400)

        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT id, name, max_marks FROM school_subjects WHERE class = %s ORDER BY name",
                [class_name]
            )
            subjects = [{'id': row[0], 'name': row[1], 'max_marks': row[2]} for row in cursor.fetchall()]
            return JsonResponse({'success': True, 'subjects': subjects})
    except Exception as e:
        return JsonResponse({'success': False, 'message': f'Error fetching subjects: {str(e)}'}, status=500)




from django.shortcuts import render, redirect
from django.contrib import messages
from django.http import JsonResponse
from django.db import connection

# Helper function to fetch timetable data
def fetch_timetable_data(query, params):
    with connection.cursor() as cursor:
        cursor.execute(query, params)
        rows = cursor.fetchall()
        return [
            {
                'id': row[0], 'class_id': row[1], 'subject': row[2], 
                'teacher_name': row[3] if len(row) > 3 else None, 
                'day_of_week': row[4], 'start_time': row[5], 
                'end_time': row[6], 'room': row[7] if len(row) > 7 else None
            } for row in rows
        ]

# Admin Timetable Dashboard (with filters)
def admin_timetable_view(request):
    if not request.session.get('admin_id'):
        messages.error(request, 'You must be logged in to access this page.')
        return redirect('admin_login')
    
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT DISTINCT class FROM student_page1
        """)
        classes = [row[0] for row in cursor.fetchall()]
        cursor.execute("""
            SELECT DISTINCT section FROM student_page1 WHERE section IS NOT NULL
        """)
        sections = [row[0] for row in cursor.fetchall()]
        cursor.execute("SELECT id, name FROM teachers")
        teachers = [{'id': row[0], 'name': row[1]} for row in cursor.fetchall()]
    
    return render(request, 'users/admin_timetable.html', {
        'classes': classes, 'sections': sections, 'teachers': teachers
    })

# Admin Filtered Timetable View
def admin_timetable_filter(request):
    if not request.session.get('admin_id'):
        messages.error(request, 'You must be logged in to access this page.')
        return redirect('admin_login')
    
    class_filter = request.GET.get('class', '')
    section_filter = request.GET.get('section', '')
    teacher_id = request.GET.get('teacher_id', '')
    day_filter = request.GET.get('day', '')
    
    query = """
        SELECT t.id, t.class_id, t.subject, tch.name, t.day_of_week, 
               t.start_time, t.end_time, t.room
        FROM timetable t
        JOIN teachers tch ON t.teacher_id = tch.id
        WHERE 1=1
    """
    params = []
    
    if class_filter and section_filter:
        class_id = f"{class_filter}{section_filter}"
        query += " AND t.class_id = %s"
        params.append(class_id)
    elif class_filter:
        query += " AND t.class_id LIKE %s"
        params.append(f"{class_filter}%")
    if teacher_id:
        query += " AND t.teacher_id = %s"
        params.append(teacher_id)
    if day_filter:
        query += " AND t.day_of_week = %s"
        params.append(day_filter)
    
    timetables = fetch_timetable_data(query, params)
    
    with connection.cursor() as cursor:
        cursor.execute("SELECT DISTINCT class FROM student_page1")
        classes = [row[0] for row in cursor.fetchall()]
        cursor.execute("SELECT DISTINCT section FROM student_page1 WHERE section IS NOT NULL")
        sections = [row[0] for row in cursor.fetchall()]
        cursor.execute("SELECT id, name FROM teachers")
        teachers = [{'id': row[0], 'name': row[1]} for row in cursor.fetchall()]
    
    return render(request, 'users/admin_timetable.html', {
        'timetables': timetables, 'classes': classes, 'sections': sections, 
        'teachers': teachers, 'selected_class': class_filter, 
        'selected_section': section_filter, 'selected_teacher': teacher_id, 
        'selected_day': day_filter
    })

# Admin Add Timetable Entry
def admin_timetable_add(request):
    if not request.session.get('admin_id'):
        messages.error(request, 'You must be logged in to access this page.')
        return redirect('admin_login')
    
    if request.method == 'POST':
        class_name = request.POST.get('class')
        section = request.POST.get('section')
        subject = request.POST.get('subject')
        teacher_id = request.POST.get('teacher_id')
        day_of_week = request.POST.get('day_of_week')
        start_time = request.POST.get('start_time')
        end_time = request.POST.get('end_time')
        room = request.POST.get('room')

        # Construct class_id
        class_id = f"{class_name}{section}" if section else class_name

        # Validate inputs
        if not class_name or not class_id:
            messages.error(request, 'Please select a valid class.')
            return redirect('admin_timetable_add')
        if not subject or not teacher_id or not day_of_week or not start_time or not end_time:
            messages.error(request, 'Please fill in all required fields.')
            return redirect('admin_timetable_add')

        with connection.cursor() as cursor:
            # Check for conflicts
            cursor.execute("""
                SELECT id FROM timetable 
                WHERE (class_id = %s OR teacher_id = %s)
                AND day_of_week = %s
                AND start_time <= %s AND end_time >= %s
            """, [class_id, teacher_id, day_of_week, end_time, start_time])
            conflict = cursor.fetchone()
            
            if conflict:
                messages.error(request, 'Scheduling conflict detected.')
                return redirect('admin_timetable')
            
            # Insert into timetable
            cursor.execute("""
                INSERT INTO timetable (class_id, subject, teacher_id, day_of_week, 
                                     start_time, end_time, room)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, [class_id, subject, teacher_id, day_of_week, start_time, end_time, room or None])
        
        messages.success(request, 'Timetable entry added successfully.')
        return redirect('admin_timetable')
    
    with connection.cursor() as cursor:
        cursor.execute("SELECT id, name, subject FROM teachers")
        teachers = [{'id': row[0], 'name': row[1], 'subject': row[2]} for row in cursor.fetchall()]
        cursor.execute("SELECT DISTINCT class FROM student_page1")
        classes = [row[0] for row in cursor.fetchall()]
        cursor.execute("SELECT DISTINCT section FROM student_page1 WHERE section IS NOT NULL")
        sections = [row[0] for row in cursor.fetchall()]
    
    return render(request, 'users/admin_timetable_add.html', {
        'teachers': teachers, 'classes': classes, 'sections': sections
    })

# Admin Edit Timetable Entry
def admin_timetable_edit(request, id):
    if not request.session.get('admin_id'):
        messages.error(request, 'You must be logged in to access this page.')
        return redirect('admin_login')
    
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT id, class_id, subject, teacher_id, day_of_week, 
                   start_time, end_time, room
            FROM timetable WHERE id = %s
        """, [id])
        timetable = cursor.fetchone()
        if not timetable:
            messages.error(request, 'Timetable entry not found.')
            return redirect('admin_timetable')
        
        class_id = timetable[1]
        class_name = class_id[:-1] if class_id[-1].isalpha() else class_id
        section = class_id[-1] if class_id[-1].isalpha() else ''
        
        timetable_data = {
            'id': timetable[0], 'class_id': timetable[1], 'subject': timetable[2],
            'teacher_id': timetable[3], 'day_of_week': timetable[4],
            'start_time': timetable[5], 'end_time': timetable[6], 'room': timetable[7],
            'class': class_name, 'section': section
        }
        
        if request.method == 'POST':
            class_name = request.POST.get('class')
            section = request.POST.get('section')
            class_id = f"{class_name}{section}" if section else class_name
            subject = request.POST.get('subject')
            teacher_id = request.POST.get('teacher_id')
            day_of_week = request.POST.get('day_of_week')
            start_time = request.POST.get('start_time')
            end_time = request.POST.get('end_time')
            room = request.POST.get('room')
            
            # Validate inputs
            if not class_name or not class_id:
                messages.error(request, 'Please select a valid class.')
                return redirect('admin_timetable_edit', id=id)
            if not subject or not teacher_id or not day_of_week or not start_time or not end_time:
                messages.error(request, 'Please fill in all required fields.')
                return redirect('admin_timetable_edit', id=id)
            
            # Check for conflicts
            cursor.execute("""
                SELECT id FROM timetable 
                WHERE (class_id = %s OR teacher_id = %s)
                AND day_of_week = %s
                AND start_time <= %s AND end_time >= %s
                AND id != %s
            """, [class_id, teacher_id, day_of_week, end_time, start_time, id])
            conflict = cursor.fetchone()
            
            if conflict:
                messages.error(request, 'Scheduling conflict detected.')
                return redirect('admin_timetable_edit', id=id)
            
            # Update timetable
            try:
                cursor.execute("""
                    UPDATE timetable 
                    SET class_id = %s, subject = %s, teacher_id = %s, 
                        day_of_week = %s, start_time = %s, end_time = %s, room = %s
                    WHERE id = %s
                """, [class_id, subject, teacher_id, day_of_week, start_time, end_time, room or None, id])
            except IntegrityError as e:
                messages.error(request, f'Error updating timetable entry: {str(e)}')
                return redirect('admin_timetable_edit', id=id)
            
            messages.success(request, 'Timetable entry updated successfully.')
            return redirect('admin_timetable')
        
        cursor.execute("SELECT id, name, subject FROM teachers")
        teachers = [{'id': row[0], 'name': row[1], 'subject': row[2]} for row in cursor.fetchall()]
        cursor.execute("SELECT DISTINCT class FROM student_page1")
        classes = [row[0] for row in cursor.fetchall()]
        cursor.execute("SELECT DISTINCT section FROM student_page1 WHERE section IS NOT NULL")
        sections = [row[0] for row in cursor.fetchall()]
    
    return render(request, 'users/admin_timetable_edit.html', {
        'timetable': timetable_data, 'teachers': teachers, 
        'classes': classes, 'sections': sections
    })

# Admin Delete Timetable Entry
def admin_timetable_delete(request, id):
    if not request.session.get('admin_id'):
        messages.error(request, 'You must be logged in to access this page.')
        return redirect('admin_login')
    
    with connection.cursor() as cursor:
        cursor.execute("DELETE FROM timetable WHERE id = %s", [id])
    
    messages.success(request, 'Timetable entry deleted successfully.')
    return redirect('admin_timetable')

# Admin Weekly Timetable Creation
def admin_timetable_weekly(request):
    if not request.session.get('admin_id'):
        messages.error(request, 'You must be logged in to access this page.')
        return redirect('admin_login')
    
    days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday']
    # Store number of periods in session to persist across requests
    if 'num_periods' not in request.session:
        request.session['num_periods'] = 6
    
    # Handle add/delete period actions
    if request.method == 'POST' and 'action' in request.POST:
        action = request.POST.get('action')
        current_periods = request.session['num_periods']
        if action == 'add' and current_periods < 10:
            request.session['num_periods'] = current_periods + 1
        elif action == 'delete' and current_periods > 1:
            request.session['num_periods'] = current_periods - 1
        request.session.modified = True
        return redirect('admin_timetable_weekly')
    
    num_periods = request.session['num_periods']
    periods = list(range(1, num_periods + 1))
    
    if request.method == 'POST' and 'create_timetable' in request.POST:
        class_name = request.POST.get('class')
        section = request.POST.get('section')
        class_id = f"{class_name}{section}" if section else class_name
        
        # Validate class_id
        if not class_name or not class_id:
            messages.error(request, 'Please select a valid class.')
            return redirect('admin_timetable_weekly')
        
        with connection.cursor() as cursor:
            for day in days:
                for period in periods:
                    subject = request.POST.get(f'subject_{day}_{period}')
                    teacher_id = request.POST.get(f'teacher_{day}_{period}')
                    start_time = request.POST.get(f'start_time_{day}_{period}')
                    end_time = request.POST.get(f'end_time_{day}_{period}')
                    room = request.POST.get(f'room_{day}_{period}')
                    
                    # Skip if required fields are missing
                    if not (subject and teacher_id and start_time and end_time):
                        continue
                        
                    # Check for conflicts
                    cursor.execute("""
                        SELECT id FROM timetable 
                        WHERE (class_id = %s OR teacher_id = %s)
                        AND day_of_week = %s
                        AND start_time <= %s AND end_time >= %s
                    """, [class_id, teacher_id, day, end_time, start_time])
                    conflict = cursor.fetchone()
                    
                    if conflict:
                        messages.error(request, f'Conflict detected for {day} period {period}.')
                        continue
                    
                    # Insert into timetable
                    try:
                        cursor.execute("""
                            INSERT INTO timetable (class_id, subject, teacher_id, day_of_week, 
                                                 start_time, end_time, room)
                            VALUES (%s, %s, %s, %s, %s, %s, %s)
                        """, [class_id, subject, teacher_id, day, start_time, end_time, room or None])
                    except IntegrityError as e:
                        messages.error(request, f'Error adding timetable entry for {day} period {period}: {str(e)}')
                        continue
        
        messages.success(request, 'Weekly timetable created successfully.')
        return redirect('admin_timetable')
    
    with connection.cursor() as cursor:
        cursor.execute("SELECT id, name, subject FROM teachers")
        teachers = [{'id': row[0], 'name': row[1], 'subject': row[2]} for row in cursor.fetchall()]
        cursor.execute("SELECT DISTINCT class FROM student_page1")
        classes = [row[0] for row in cursor.fetchall()]
        cursor.execute("SELECT DISTINCT section FROM student_page1 WHERE section IS NOT NULL")
        sections = [row[0] for row in cursor.fetchall()]
    
    return render(request, 'users/admin_timetable_weekly.html', {
        'days': days, 'periods': periods, 'teachers': teachers, 
        'classes': classes, 'sections': sections, 'num_periods': num_periods
    })

# Teacher Timetable View
def teacher_timetable_view(request):
    if 'teacher_id' not in request.session:
        messages.error(request, 'Please log in to access the teacher portal.')
        return redirect('/teacher_login/')  # Adjust to your login URL
    
    teacher_id = request.session['teacher_id']
    with connection.cursor() as cursor:
        # Check if timetable entries exist for the teacher
        cursor.execute("SELECT COUNT(*) FROM timetable WHERE teacher_id = %s", [teacher_id])
        timetable_count = cursor.fetchone()[0]
        if timetable_count == 0:
            messages.warning(request, 'No timetable entries found for you.')
            return render(request, 'users/teacher_timetable.html', {
                'timetable_data': [], 'teacher_id': teacher_id
            })
        
        # Fetch timetable with teacher details
        query = """
            SELECT t.id, t.class_id, t.subject, t.day_of_week, 
                   t.start_time, t.end_time, t.room
            FROM timetable t
            WHERE t.teacher_id = %s
            ORDER BY FIELD(t.day_of_week, 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday')
        """
        cursor.execute(query, [teacher_id])
        timetables = [
            {
                'id': row[0],
                'class_id': row[1],
                'subject': row[2],
                'day_of_week': row[3],
                'start_time': row[4],
                'end_time': row[5],
                'room': row[6]
            } for row in cursor.fetchall()
        ]
    
    # Organize by day as a list of (day, entries)
    days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday']
    timetable_data = []
    for day in days:
        entries = [entry for entry in timetables if entry['day_of_week'] == day]
        timetable_data.append((day, entries))
    
    return render(request, 'users/teacher_timetable.html', {
        'timetable_data': timetable_data, 'teacher_id': teacher_id
    })

# Student Timetable View
def student_timetable_view(request):
    if 'user_id' not in request.session:
        messages.error(request, 'Please log in to access the student portal.')
        return redirect('/login/')
    
    user_id = request.session['user_id']
    with connection.cursor() as cursor:
        # Fetch class and section for the student
        cursor.execute("SELECT class, section FROM student_page1 WHERE user_id = %s", [user_id])
        student = cursor.fetchone()
        if not student:
            messages.error(request, 'Student class information not found.')
            return redirect('student_timetable')
        
        class_name, section = student
        if not class_name:
            messages.error(request, 'Invalid class information for the student.')
            return redirect('student_timetable')
        
        # Construct class_id
        class_id = f"{class_name}{section}" if section else class_name
        
        # Check if timetable entries exist
        cursor.execute("SELECT COUNT(*) FROM timetable WHERE class_id = %s", [class_id])
        timetable_count = cursor.fetchone()[0]
        if timetable_count == 0:
            messages.warning(request, f'No timetable entries found for class {class_id}.')
            return render(request, 'users/student_timetable.html', {
                'timetable_data': [], 'class_id': class_id
            })
        
        # Fetch timetable with teacher details
        query = """
            SELECT t.id, t.class_id, t.subject, tch.name, t.day_of_week, 
                   t.start_time, t.end_time, t.room
            FROM timetable t
            JOIN teachers tch ON t.teacher_id = tch.id
            WHERE t.class_id = %s
            ORDER BY FIELD(t.day_of_week, 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday')
        """
        cursor.execute(query, [class_id])
        timetables = [
            {
                'id': row[0],
                'class_id': row[1],
                'subject': row[2],
                'name': row[3],
                'day_of_week': row[4],
                'start_time': row[5],
                'end_time': row[6],
                'room': row[7]
            } for row in cursor.fetchall()
        ]
    
    # Organize by day as a list of (day, entries)
    days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday']
    timetable_data = []
    for day in days:
        entries = [entry for entry in timetables if entry['day_of_week'] == day]
        timetable_data.append((day, entries))
    
    return render(request, 'users/student_timetable.html', {
        'timetable_data': timetable_data, 'class_id': class_id
    })




# users/views.py
from django.shortcuts import render, redirect
from django.contrib import messages
from django.conf import settings
from django.db import connection, transaction
import os
import uuid
from django.utils import timezone

def teacher_profile(request):
    if 'teacher_id' not in request.session:
        messages.error(request, "Please log in to view your profile.")
        return redirect('login')  # Redirect to login page if not authenticated

    teacher_id = request.session['teacher_id']
    
    # Fetch profile picture
    profile_picture = None
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT profile_pic_url FROM profile_pics_teachers WHERE teacher_id = %s", [teacher_id])
            profile_picture_result = cursor.fetchone()
            if profile_picture_result:
                profile_picture = f"{settings.MEDIA_URL}{profile_picture_result[0]}"
                print(f"DEBUG: Found profile picture: {profile_picture}")
    except Exception as e:
        print("Error fetching profile picture:", e)

    if request.method == "POST":
        print(f"DEBUG: POST request received")
        print(f"DEBUG: FILES in request: {request.FILES}")
        print(f"DEBUG: POST data: {list(request.POST.keys())}")
        
        try:
            with transaction.atomic():
                # Handle ONLY profile picture upload
                if 'profile_pic' in request.FILES and request.FILES['profile_pic']:
                    print("DEBUG: Processing profile picture upload")
                    profile_pic_file = request.FILES['profile_pic']
                    print(f"DEBUG: File name: {profile_pic_file.name}, Size: {profile_pic_file.size}")
                    
                    # Validate file type
                    allowed_extensions = ['.png', '.jpg', '.jpeg']
                    file_ext = os.path.splitext(profile_pic_file.name)[1].lower()
                    if file_ext not in allowed_extensions:
                        messages.error(request, "Only PNG, JPG, or JPEG files are allowed.")
                        return redirect('teacher_profile')

                    # Validate file size (5MB limit)
                    if profile_pic_file.size > 5 * 1024 * 1024:
                        messages.error(request, "File size must be less than 5MB.")
                        return redirect('teacher_profile')

                    # Generate file path using UUID and teacher_id
                    filename = f"{uuid.uuid4().hex}_{teacher_id}{file_ext}"
                    
                    # Create pfpicsteacher directory in MEDIA_ROOT
                    pfpics_dir = os.path.join(settings.MEDIA_ROOT, 'pfpicsteacher')
                    os.makedirs(pfpics_dir, exist_ok=True)
                    
                    file_path = os.path.join(pfpics_dir, filename)
                    print(f"DEBUG: Saving file to: {file_path}")
                    
                    # Delete old profile picture if exists
                    try:
                        with connection.cursor() as cursor:
                            cursor.execute("SELECT profile_pic_url FROM profile_pics_teachers WHERE teacher_id = %s", [teacher_id])
                            old_pic = cursor.fetchone()
                            if old_pic:
                                old_file_path = os.path.join(settings.MEDIA_ROOT, old_pic[0])
                                if os.path.exists(old_file_path):
                                    os.remove(old_file_path)
                                    print(f"DEBUG: Deleted old file: {old_file_path}")
                    except Exception as e:
                        print(f"Error deleting old profile picture: {e}")

                    # Save new file
                    try:
                        with open(file_path, 'wb+') as destination:
                            for chunk in profile_pic_file.chunks():
                                destination.write(chunk)
                        print(f"DEBUG: File saved successfully to {file_path}")
                    except Exception as e:
                        print(f"ERROR: Failed to save file: {e}")
                        messages.error(request, "Failed to save file.")
                        return redirect('teacher_profile')

                    # Update database: delete existing and insert new record
                    try:
                        with connection.cursor() as cursor:
                            cursor.execute("DELETE FROM profile_pics_teachers WHERE teacher_id = %s", [teacher_id])
                            cursor.execute("""
                                INSERT INTO profile_pics_teachers (teacher_id, profile_pic_url, created_at)
                                VALUES (%s, %s, %s)
                            """, [teacher_id, f"pfpicsteacher/{filename}", timezone.now()])
                        print(f"DEBUG: Updated database with new path: pfpicsteacher/{filename}")
                    except Exception as e:
                        print(f"ERROR: Database operation failed: {e}")
                        messages.error(request, "Failed to update database.")
                        return redirect('teacher_profile')
                    
                    messages.success(request, "Profile picture uploaded successfully!")
                    return redirect('teacher_profile')
        except Exception as e:
            print(f"ERROR: Transaction failed: {e}")
            messages.error(request, "An error occurred during upload.")
            return redirect('teacher_profile')

    # Fetch teacher details
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM teachers WHERE id = %s", [teacher_id])
            teacher = cursor.fetchone()
            
            if not teacher:
                messages.error(request, "Teacher not found.")
                return redirect('login')

            # Convert tuple to dictionary for template
            teacher_data = {
                'id': teacher[0],
                'name': teacher[1],
                'email': teacher[2],
                'subject': teacher[3],
                'class_teacher_of': teacher[4],
                'created_at': teacher[5],
            }
            profile_pic_url = profile_picture if profile_picture else f"{settings.MEDIA_URL}pfpicsteacher/default.jpg"
    except Exception as e:
        print(f"Error fetching teacher details: {e}")
        messages.error(request, "Failed to load profile.")
        return redirect('login')

    context = {
        'teacher': teacher_data,
        'profile_pic_url': profile_pic_url,
    }
    return render(request, 'users/teacher_profile.html', context)






def parent_profile_view(request):
    if "user_id" not in request.session:
        return redirect("/parent_login/")  # Redirect to login if not authenticated

    user_id = request.session["user_id"]  # Get logged-in user's ID

    # Fetch profile picture
    profile_picture = None
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT image_path FROM profile_pics WHERE user_id = %s", [user_id])
            profile_picture_result = cursor.fetchone()
            if profile_picture_result:
                profile_picture = f"{settings.MEDIA_URL}{profile_picture_result[0]}"
                print(f"DEBUG: Found profile picture: {profile_picture}")
    except Exception as e:
        print("Error fetching profile picture:", e)

    if request.method == "POST":
        print(f"DEBUG: POST request received")
        print(f"DEBUG: FILES in request: {request.FILES}")
        print(f"DEBUG: POST data: {list(request.POST.keys())}")
        
        try:
            with transaction.atomic():
                # Handle ONLY profile picture upload
                if 'profile_picture' in request.FILES and request.FILES['profile_picture']:
                    print("DEBUG: Processing profile picture upload")
                    profile_picture_file = request.FILES['profile_picture']
                    print(f"DEBUG: File name: {profile_picture_file.name}, Size: {profile_picture_file.size}")
                    
                    # Validate file type
                    allowed_extensions = ['.png', '.jpg', '.jpeg']
                    file_ext = os.path.splitext(profile_picture_file.name)[1].lower()
                    if file_ext not in allowed_extensions:
                        messages.error(request, "Only PNG, JPG, or JPEG files are allowed.")
                        return redirect('parent_profile_view')

                    # Validate file size (5MB limit)
                    if profile_picture_file.size > 5 * 1024 * 1024:
                        messages.error(request, "File size must be less than 5MB.")
                        return redirect('parent_profile_view')

                    # Generate file path using UUID and user_id
                    filename = f"{uuid.uuid4().hex}_{user_id}{file_ext}"
                    
                    # Create pfpics directory in MEDIA_ROOT
                    pfpics_dir = os.path.join(settings.MEDIA_ROOT, 'pfpics')
                    os.makedirs(pfpics_dir, exist_ok=True)
                    
                    file_path = os.path.join(pfpics_dir, filename)
                    print(f"DEBUG: Saving file to: {file_path}")
                    
                    # Delete old profile picture if exists
                    try:
                        with connection.cursor() as cursor:
                            cursor.execute("SELECT image_path FROM profile_pics WHERE user_id = %s", [user_id])
                            old_pic = cursor.fetchone()
                            if old_pic:
                                old_file_path = os.path.join(settings.MEDIA_ROOT, old_pic[0])
                                if os.path.exists(old_file_path):
                                    os.remove(old_file_path)
                                    print(f"DEBUG: Deleted old file: {old_file_path}")
                    except Exception as e:
                        print(f"Error deleting old profile picture: {e}")

                    # Save new file
                    try:
                        with open(file_path, 'wb+') as destination:
                            for chunk in profile_picture_file.chunks():
                                destination.write(chunk)
                        print(f"DEBUG: File saved successfully to {file_path}")
                    except Exception as e:
                        print(f"ERROR: Failed to save file: {e}")
                        messages.error(request, "Failed to save file.")
                        return redirect('parent_profile_view')

                    # Update or insert profile picture path in database
                    try:
                        with connection.cursor() as cursor:
                            cursor.execute("SELECT id FROM profile_pics WHERE user_id = %s", [user_id])
                            existing = cursor.fetchone()
                            
                            db_path = f"pfpics/{filename}"
                            if existing:
                                cursor.execute(
                                    "UPDATE profile_pics SET image_path = %s, uploaded_at = %s WHERE user_id = %s",
                                    [db_path, timezone.now(), user_id]
                                )
                                print(f"DEBUG: Updated existing record with path: {db_path}")
                            else:
                                cursor.execute(
                                    "INSERT INTO profile_pics (user_id, image_path, uploaded_at) VALUES (%s, %s, %s)",
                                    [user_id, db_path, timezone.now()]
                                )
                                print(f"DEBUG: Inserted new record with path: {db_path}")
                    except Exception as e:
                        print(f"ERROR: Database operation failed: {e}")
                        messages.error(request, "Failed to update database.")
                        return redirect('parent_profile_view')
                    
                    messages.success(request, "Profile picture uploaded successfully!")
                    return redirect('parent_profile_view')

                # Handle regular form submission (when no file is uploaded)
                else:
                    print("DEBUG: Processing regular form submission")
                    # Your existing form processing logic here
                    name = request.POST.get("name")
                    admission_number = request.POST.get("admission_number")
                    student_class = request.POST.get("class")
                    section = request.POST.get("section")
                    roll_number = request.POST.get("roll_number")
                    emis = request.POST.get("emis")

                    # Only process if we have actual form data
                    if name or admission_number:
                        # Validate required fields for Page 1
                        if not all([name, admission_number, student_class]):
                            messages.error(request, "Please fill in all required fields.")
                            return redirect('parent_profile_view')

                        # Convert roll_number to integer if provided
                        if roll_number:
                            try:
                                roll_number = int(roll_number)
                            except (ValueError, TypeError):
                                messages.error(request, "Roll number must be a valid integer.")
                                return redirect('parent_profile_view')

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
                                    nationality=VALUES(nationality), blood_group=VALUES(blood_group), 
                                    mother_tongue=VALUES(mother_tongue), caste=VALUES(caste), religion=VALUES(religion),
                                    place_of_birth=VALUES(place_of_birth), aadhaar=VALUES(aadhaar),
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
                                    father_name=VALUES(father_name), father_name_tamil=VALUES(father_name_tamil),
                                    mother_name=VALUES(mother_name), mother_name_tamil=VALUES(mother_name_tamil),
                                    father_contact=VALUES(father_contact), mother_contact=VALUES(mother_contact),
                                    father_email=VALUES(father_email), mother_email=VALUES(mother_email),
                                    father_qualification=VALUES(father_qualification), mother_qualification=VALUES(mother_qualification),
                                    father_occupation=VALUES(father_occupation), mother_occupation=VALUES(mother_occupation),
                                    father_income=VALUES(father_income), mother_income=VALUES(mother_income),
                                    guardian_name=VALUES(guardian_name), guardian_contact=VALUES(guardian_contact),
                                    guardian_email=VALUES(guardian_email), child_living=VALUES(child_living),
                                    rights_on_child=VALUES(rights_on_child), med_blood_group=VALUES(med_blood_group),
                                    diseases=VALUES(diseases), allergies=VALUES(allergies), medicines=VALUES(medicines),
                                    hospital=VALUES(hospital), doctor=VALUES(doctor)
                            """, (
                                user_id, father_name, father_name_tamil, mother_name, mother_name_tamil, father_contact,
                                mother_contact, father_email, mother_email, father_qualification, mother_qualification,
                                father_occupation, mother_occupation, father_income, mother_income, guardian_name,
                                guardian_contact, guardian_email, child_living, rights_on_child, med_blood_group,
                                diseases, allergies, medicines, hospital, doctor
                            ))

                        messages.success(request, "Profile updated successfully.")
                        return redirect('parent_profile_view')

        except Exception as e:
            print(f"ERROR: Exception in POST processing: {e}")
            messages.error(request, f"Failed to process request: {str(e)}")
            return redirect('parent_profile_view')

    # Fetch student details for display
    student_data = None
    try:
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT 
                    s1.name, s1.admission_number, s1.class, s1.section, s1.roll_number, s1.emis,
                    s2.gender, s2.community, s2.tamil_name, s2.dob, s2.nationality, s2.blood_group, 
                    s2.mother_tongue, s2.caste, s2.religion, s2.place_of_birth, s2.aadhaar, s2.disability,
                    s2.id_mark1, s2.id_mark2, s2.current_class, s2.admission_class, s2.admission_year, s2.admission_date,
                    s3.email, s3.address, s3.contact, s3.alt_contact, s3.country, s3.state, s3.city, s3.pincode,
                    s3.status, s3.house, s3.teacher_ward, s3.rte, s3.sports_quota, s3.prev_school, s3.prev_board,
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
    except Exception as e:
        print(f"DEBUG: Error fetching student data: {e}")

    print(f"DEBUG: Rendering template with profile_picture: {profile_picture}")
    return render(request, "users/parent_profile_view.html", {
        "student_data": student_data,
        "profile_picture": profile_picture,
        "user_id": user_id
    })




def parent_student_portal(request):
    if "user_id" not in request.session:
        return redirect("/")
    
    user_id = request.session['user_id']
    selected_date = request.GET.get('date', '')
    
    with connection.cursor() as cursor:
        if selected_date:
            cursor.execute(
                """
                SELECT a.date, s.admission_number, s.name, a.class, a.section, a.status 
                FROM attendance a
                JOIN student_page1 s ON a.student_id = s.user_id
                WHERE s.user_id = %s AND a.date = %s
                ORDER BY a.date DESC
                """,
                [user_id, selected_date]
            )
        else:
            cursor.execute(
                """
                SELECT a.date, s.admission_number, s.name, a.class, a.section, a.status
                FROM attendance a
                JOIN student_page1 s ON a.student_id = s.user_id
                WHERE s.user_id = %s
                ORDER BY a.date DESC
                """,
                [user_id]
            )
        attendance_records = [
            {
                'date': row[0],
                'admission_number': row[1],
                'name': row[2],
                'class': row[3],
                'section': row[4] if row[4] else 'N/A',
                'status': row[5]
            } for row in cursor.fetchall()
        ]

    return render(request, 'users/parent_student_portal.html', {
        'attendance_records': attendance_records,
        'selected_date': selected_date
    })



def parent_student_leave(request):
    """Handle parent student leave request submission and viewing."""
    if "user_id" not in request.session:
        messages.error(request, "Please log in to access the parent student portal.")
        return redirect("/parent_login/")

    user_id = request.session["user_id"]
    
    if request.method == "POST":
        try:
            form_data = {
                "student_name": request.POST.get("student_name", "").strip(),
                "reg_number": request.POST.get("reg_number", "").strip(),
                "class_number": request.POST.get("class", "").strip(),
                "leave_reason": request.POST.get("leave_reason", "").strip(),
                "leave_start_date": request.POST.get("leave_start_date", ""),
                "leave_end_date": request.POST.get("leave_end_date", ""),
                "leave_duration": request.POST.get("leave_duration", ""),
                "half_day_type": request.POST.get("half_day_type", "")
            }

            required_fields = ["student_name", "reg_number", "class_number", "leave_reason", 
                             "leave_start_date", "leave_end_date", "leave_duration"]
            missing_fields = [field for field in required_fields if not form_data[field]]
            if missing_fields:
                messages.error(request, f"Missing required fields: {', '.join(missing_fields)}")
                return redirect("parent_student_leave")
            
            if form_data["leave_duration"] not in ["full", "half"]:
                messages.error(request, "Invalid leave duration.")
                return redirect("parent_student_leave")
                
            if form_data["leave_duration"] == "half" and not form_data["half_day_type"]:
                messages.error(request, "Please select half day type for half-day leave.")
                return redirect("parent_student_leave")

            try:
                start_date = datetime.datetime.strptime(form_data["leave_start_date"], "%Y-%m-%d")
                end_date = datetime.datetime.strptime(form_data["leave_end_date"], "%Y-%m-%d")
                if start_date > end_date:
                    messages.error(request, "End date must be on or after start date.")
                    return redirect("parent_student_leave")
            except ValueError:
                messages.error(request, "Invalid date format.")
                return redirect("parent_student_leave")

            with connection.cursor() as cursor:
                cursor.execute("""
                    INSERT INTO student_leave_requests 
                    (user_id, student_name, reg_number, class_number, leave_reason,
                    leave_start_date, leave_end_date, leave_duration, half_day_type, status)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """, [user_id, form_data["student_name"], form_data["reg_number"], 
                      form_data["class_number"], form_data["leave_reason"], 
                      form_data["leave_start_date"], form_data["leave_end_date"],
                      form_data["leave_duration"], 
                      form_data["half_day_type"] if form_data["leave_duration"] == "half" else None,
                      "Pending"])
                connection.commit()
            messages.success(request, "Leave request submitted successfully.")
        except Exception as e:
            connection.rollback()
            messages.error(request, f"Error submitting leave request: {str(e)}")
        return redirect("parent_student_leave")

    # Fetch leave requests for this parent student
    leave_requests = []
    with connection.cursor() as cursor:
        try:
            cursor.execute("""
                SELECT id, student_name, reg_number, class_number, leave_reason, 
                leave_start_date, leave_end_date, leave_duration, half_day_type, status
                FROM student_leave_requests WHERE user_id = %s
                ORDER BY leave_start_date DESC
            """, [user_id])
            leave_requests = cursor.fetchall()
        except Exception as e:
            messages.error(request, f"Error fetching leave requests: {str(e)}")

    return render(request, "users/parent_student_leave.html", {
        "leave_requests": leave_requests
    })




def parent_student_circular(request):
    # Get the logged-in user's user_id from session and fetch class/section from student_page1
    student_class = None
    student_section = None
    error_message = None

    if "user_id" not in request.session:
        error_message = "Please log in to view circulars."
        print("No user_id found in session")
    else:
        user_id = request.session['user_id']
        print(f"Session user_id: {user_id}")
        try:
            with connection.cursor() as cursor:
                cursor.execute(
                    "SELECT class, section FROM student_page1 WHERE user_id = %s",
                    [user_id]
                )
                result = cursor.fetchone()
                if result:
                    student_class, student_section = [normalize_value(r) for r in result]
                    print(f"Parent student user_id={user_id}: class={student_class}, section={student_section}")
                else:
                    error_message = "No class or section found for your account. Please contact the admin."
                    print(f"No student record found for user_id: {user_id}")
        except Exception as e:
            error_message = "Error fetching your class/section. Please try again later."
            print(f"Error fetching parent student class/section for user_id={user_id}: {e}")

    # Get filter type from POST request (default to 'all')
    filter_type = request.POST.get('filter_type', 'all')
    print(f"Filter type: {filter_type}")

    circulars = []
    for file in os.listdir(UPLOAD_DIR):
        if file.endswith(('.jpg', '.png', '.jpeg', '.webp', '.gif')):
            full_path = os.path.join(UPLOAD_DIR, file)
            if not os.path.exists(full_path):
                print(f"Image file missing in parent student view: {full_path}")
                continue

            title_file = f"{file}.txt"
            title_path = os.path.join(UPLOAD_DIR, title_file)
            title = "Untitled"
            target = "all"
            class_name = ""
            section = ""

            if os.path.exists(title_path):
                try:
                    with open(title_path, 'r') as f:
                        lines = f.readlines()
                        title = lines[0].strip() if lines else "Untitled"
                        target = lines[1].strip().lower() if len(lines) > 1 else "all"
                        if target == 'specific' and len(lines) >= 4:
                            class_name = normalize_value(lines[2])
                            section = normalize_value(lines[3])
                        print(f"Circular {file}: title={title}, target={target}, class={class_name}, section={section}")
                except Exception as e:
                    print(f"Error reading metadata from {title_path}: {e}")
                    continue

            # Filter circulars based on filter_type
            include_circular = False
            if filter_type == 'all':
                if target == "all" or (
                    target == "specific" and
                    student_class and student_section and
                    class_name == student_class and section == student_section
                ):
                    include_circular = True
            elif filter_type == 'specific':
                if target == "specific" and student_class and student_section and class_name == student_class and section == student_section:
                    include_circular = True

            if include_circular:
                try:
                    created_at = datetime.datetime.fromtimestamp(os.path.getctime(full_path)).strftime('%Y-%m-%d %H:%M:%S')
                    image_url = f"/static/uploads/{file}"  # Consistent path
                    print(f"Included circular: {file}, image_url: {image_url}, full_path: {full_path}")
                    display_target = "All" if target == "all" else f"Class: {class_name.capitalize()}, Section: {section.capitalize()}"
                    circulars.append({
                        'title': title,
                        'image_url': image_url,
                        'date': created_at,
                        'target': display_target
                    })
                except Exception as e:
                    print(f"Error processing file {file}: {e}")

    # Sort by newest first
    circulars = sorted(circulars, key=lambda x: x['date'], reverse=True)
    print(f"Total circulars displayed: {len(circulars)}")

    return render(request, 'users/parent_student_circular.html', {
        'circulars': circulars,
        'student_class': student_class,
        'student_section': student_section,
        'filter_type': filter_type,
        'error_message': error_message
    })


def parent_study_materials(request):
    if "user_id" not in request.session:
        messages.error(request, "Please log in to access the parent student portal.")
        return redirect("/parent_login/")

    user_id = request.session["user_id"]
    student_class = None
    student_section = None

    # Fetch student's class and section
    try:
        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT class, section FROM student_page1 WHERE user_id = %s",
                [user_id]
            )
            result = cursor.fetchone()
            if result:
                student_class, student_section = result
            else:
                messages.error(request, "No class or section found for your account. Please contact the admin.")
                return redirect("/parent-study-materials/")
    except Exception as e:
        messages.error(request, f"Error fetching class/section: {str(e)}")
        return redirect("/parent-study-materials/")

    try:
        with connection.cursor() as cursor:
            query = """
                SELECT title, file_path, upload_date, class, section
                FROM study_materials
                WHERE class = %s AND section = %s
                ORDER BY upload_date DESC
            """
            cursor.execute(query, [student_class, student_section])
            study_materials = [
                {
                    "title": r[0],
                    "file_path": r[1],
                    "upload_date": r[2],
                    "class": r[3],
                    "section": r[4]
                } for r in cursor.fetchall()
            ]
    except Exception as e:
        messages.error(request, f"Error retrieving study materials: {str(e)}")
        study_materials = []

    return render(request, "users/parent_study_materials.html", {
        "study_materials": study_materials,
        "media_url": settings.MEDIA_URL,
        "student_class": student_class,
        "student_section": student_section
    })



def parent_homework(request):
    if "user_id" not in request.session:
        messages.error(request, "Please log in to access the parent student portal.")
        return redirect("/parent_login/")

    user_id = request.session["user_id"]
    student_class = None
    student_section = None

    # Fetch student's class and section
    try:
        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT class, section FROM student_page1 WHERE user_id = %s",
                [user_id]
            )
            result = cursor.fetchone()
            if result:
                student_class, student_section = result
            else:
                messages.error(request, "No class or section found for your account. Please contact the admin.")
                return redirect("/parent-homework/")
    except Exception as e:
        messages.error(request, f"Error fetching class/section: {str(e)}")
        return redirect("/parent-homework/")

    if request.method == "POST":
        title = request.POST.get("title")
        submission_date = request.POST.get("submission_date")
        uploaded_file = request.FILES.get("file")

        if not all([title, submission_date, uploaded_file]):
            messages.error(request, "All fields are required.")
            return redirect("/parent-homework/")

        # Validate file is a PDF
        validator = FileExtensionValidator(allowed_extensions=['pdf'])
        try:
            validator(uploaded_file)
        except ValidationError:
            messages.error(request, "Only PDF files are allowed.")
            return redirect("/parent-homework/")

        try:
            # Save file with unique filename
            fs = FileSystemStorage(location=os.path.join(settings.MEDIA_ROOT, 'Uploads'))
            filename = f"{uuid.uuid4().hex}_{uploaded_file.name}"
            filename = fs.save(filename, uploaded_file)
            file_path = f"Uploads/{filename}"

            with connection.cursor() as cursor:
                cursor.execute(
                    """
                    INSERT INTO homework (user_id, title, submission_date, file_path, class, section)
                    VALUES (%s, %s, %s, %s, %s, %s)
                    """,
                    [user_id, title, submission_date, file_path, student_class, student_section]
                )
            messages.success(request, "Homework submitted successfully!")
        except Exception as e:
            messages.error(request, f"Error submitting homework: {str(e)}")
        return redirect("/parent-homework/")

    try:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT h.title, h.submission_date, h.file_path
                FROM homework h
                WHERE h.user_id = %s
                ORDER BY h.submission_date DESC
                """,
                [user_id]
            )
            homework_list = [
                {"title": r[0], "submission_date": r[1], "file_path": r[2]}
                for r in cursor.fetchall()
            ]
    except Exception as e:
        messages.error(request, f"Error retrieving homework: {str(e)}")
        homework_list = []

    return render(request, "users/parent_homework.html", {
        "homework_list": homework_list,
        "student_class": student_class,
        "student_section": student_section
    })



def parent_student_timetable(request):
    if 'user_id' not in request.session:
        messages.error(request, 'Please log in to access the parent student portal.')
        return redirect('/parent_login/')
    
    user_id = request.session['user_id']
    with connection.cursor() as cursor:
        # Fetch class and section for the student
        cursor.execute("SELECT class, section FROM student_page1 WHERE user_id = %s", [user_id])
        student = cursor.fetchone()
        if not student:
            messages.error(request, 'Student class information not found.')
            return redirect('parent_student_timetable')
        
        class_name, section = student
        if not class_name:
            messages.error(request, 'Invalid class information for the student.')
            return redirect('parent_student_timetable')
        
        # Construct class_id
        class_id = f"{class_name}{section}" if section else class_name
        
        # Check if timetable entries exist
        cursor.execute("SELECT COUNT(*) FROM timetable WHERE class_id = %s", [class_id])
        timetable_count = cursor.fetchone()[0]
        if timetable_count == 0:
            messages.warning(request, f'No timetable entries found for class {class_id}.')
            return render(request, 'users/parent_student_timetable.html', {
                'timetable_data': [], 'class_id': class_id
            })
        
        # Fetch timetable with teacher details
        query = """
            SELECT t.id, t.class_id, t.subject, tch.name, t.day_of_week, 
                   t.start_time, t.end_time, t.room
            FROM timetable t
            JOIN teachers tch ON t.teacher_id = tch.id
            WHERE t.class_id = %s
            ORDER BY FIELD(t.day_of_week, 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday')
        """
        cursor.execute(query, [class_id])
        timetables = [
            {
                'id': row[0],
                'class_id': row[1],
                'subject': row[2],
                'name': row[3],
                'day_of_week': row[4],
                'start_time': row[5],
                'end_time': row[6],
                'room': row[7]
            } for row in cursor.fetchall()
        ]
    
    # Organize by day as a list of (day, entries)
    days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday']
    timetable_data = []
    for day in days:
        entries = [entry for entry in timetables if entry['day_of_week'] == day]
        timetable_data.append((day, entries))
    
    return render(request, 'users/parent_student_timetable.html', {
        'timetable_data': timetable_data, 'class_id': class_id
    })


def student_progress_card(request):
    if 'user_id' not in request.session:
        messages.error(request, 'Please log in to access the student portal.')
        return redirect('/login/')
    
    user_id = request.session['user_id']
    with connection.cursor() as cursor:
        # Fetch class and section for the student
        cursor.execute("SELECT class, section FROM student_page1 WHERE user_id = %s", [user_id])
        student = cursor.fetchone()
        if not student:
            messages.error(request, 'Student class information not found.')
            return redirect('student_progress_card')
        
        class_name, section = student
        if not class_name:
            messages.error(request, 'Invalid class information for the student.')
            return redirect('student_progress_card')
        
        # Placeholder for progress card data (since results are not yet available)
        progress_card_data = []

    return render(request, 'users/student_progress_card.html', {
        'progress_card_data': progress_card_data,
        'class_name': class_name,
        'section': section
    })


def parent_student_progress_card(request):
    if 'user_id' not in request.session:
        messages.error(request, 'Please log in to access the parent student portal.')
        return redirect('/login/')
    
    user_id = request.session['user_id']
    with connection.cursor() as cursor:
        # Fetch class and section for the student
        cursor.execute("SELECT class, section FROM student_page1 WHERE user_id = %s", [user_id])
        student = cursor.fetchone()
        if not student:
            messages.error(request, 'Student class information not found.')
            return redirect('parent_student_progress_card')
        
        class_name, section = student
        if not class_name:
            messages.error(request, 'Invalid class information for the student.')
            return redirect('parent_student_progress_card')
        
        # Placeholder for progress card data (since results are not yet available)
        progress_card_data = []

    return render(request, 'users/parent_student_progress_card.html', {
        'progress_card_data': progress_card_data,
        'class_name': class_name,
        'section': section
    })


    


from django.shortcuts import render, redirect
from django.http import JsonResponse, HttpResponse
from django.db import connection
from django.conf import settings
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.lib.enums import TA_CENTER, TA_LEFT
import json
import os
from io import BytesIO

def render_qr_scan(request):
    if "admin_id" not in request.session:
        return redirect("/admin_login/")
    return render(request, 'users/qr_scan.html')

def scan_qr_code(request):
    if "admin_id" not in request.session:
        return JsonResponse({"error": "Admin not authenticated."}, status=401)

    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            qr_url = data.get('url', '')
            
            # Extract admission number from URL
            admission_number = qr_url.split('/')[-2] if qr_url.endswith('/') else qr_url.split('/')[-1]
            
            # Remove any query parameters or fragments
            admission_number = admission_number.split('?')[0].split('#')[0]

            with connection.cursor() as cursor:
                # Fetch student data with better error handling
                cursor.execute("""
                    SELECT 
                        sp1.user_id, sp1.name, sp1.admission_number, sp1.class, sp1.section, 
                        sp1.roll_number, sp1.emis, 
                        sp2.gender, sp2.community, sp2.tamil_name, sp2.dob, 
                        sp2.nationality, sp2.blood_group, sp2.mother_tongue, 
                        sp2.caste, sp2.religion, sp2.place_of_birth, sp2.aadhaar, 
                        sp2.disability, sp2.id_mark1, sp2.id_mark2, sp2.current_class, 
                        sp2.admission_class, sp2.admission_year, sp2.admission_date,
                        sp3.email, sp3.address, sp3.contact, sp3.alt_contact, 
                        sp3.country, sp3.state, sp3.city, sp3.pincode, sp3.status, 
                        sp3.house, sp3.teacher_ward, sp3.rte, sp3.sports_quota, 
                        sp3.prev_school, sp3.prev_board,
                        sp4.father_name, sp4.father_name_tamil, sp4.mother_name, 
                        sp4.mother_name_tamil, sp4.father_contact, sp4.mother_contact, 
                        sp4.father_email, sp4.mother_email, sp4.father_qualification, 
                        sp4.mother_qualification, sp4.father_occupation, 
                        sp4.mother_occupation, sp4.father_income, sp4.mother_income, 
                        sp4.guardian_name, sp4.guardian_contact, sp4.guardian_email, 
                        sp4.child_living, sp4.rights_on_child, sp4.med_blood_group, 
                        sp4.diseases, sp4.allergies, sp4.medicines, sp4.hospital, 
                        sp4.doctor
                    FROM 
                        student_page1 sp1
                    LEFT JOIN 
                        student_page2 sp2 ON sp1.user_id = sp2.user_id
                    LEFT JOIN 
                        student_page3 sp3 ON sp1.user_id = sp3.user_id
                    LEFT JOIN 
                        student_page4 sp4 ON sp1.user_id = sp4.user_id
                    WHERE 
                        sp1.admission_number = %s
                """, [admission_number])
                
                student_data = cursor.fetchone()

                if not student_data:
                    return JsonResponse({"error": f"Student not found with admission number: {admission_number}"}, status=404)

                user_id = student_data[0]
                profile_picture = None
                
                # Fetch profile picture with better error handling
                try:
                    cursor.execute("SELECT image_path FROM profile_pics WHERE user_id = %s", [user_id])
                    profile_picture_result = cursor.fetchone()
                    if profile_picture_result and profile_picture_result[0]:
                        # For HTML display, use MEDIA_URL; for PDF, use full path
                        profile_picture_web = f"{settings.MEDIA_URL}{profile_picture_result[0]}"
                        profile_picture_path = os.path.join(settings.MEDIA_ROOT, profile_picture_result[0])
                    else:
                        profile_picture_web = None
                        profile_picture_path = None
                except Exception as e:
                    print(f"Error fetching profile picture: {str(e)}")
                    profile_picture_web = None
                    profile_picture_path = None

                # Helper function to safely convert values
                def safe_str(value):
                    if value is None:
                        return "N/A"
                    return str(value)

                response_data = {
                    "user_id": user_id,
                    "profile_picture": profile_picture_web,  # For HTML display
                    "profile_picture_path": profile_picture_path,  # For PDF generation
                    "name": safe_str(student_data[1]),
                    "admission_number": safe_str(student_data[2]),
                    "class": safe_str(student_data[3]),
                    "section": safe_str(student_data[4]),
                    "roll_number": safe_str(student_data[5]),
                    "emis": safe_str(student_data[6]),
                    "gender": safe_str(student_data[7]),
                    "community": safe_str(student_data[8]),
                    "tamil_name": safe_str(student_data[9]),
                    "dob": safe_str(student_data[10]) if student_data[10] else "N/A",
                    "nationality": safe_str(student_data[11]),
                    "blood_group": safe_str(student_data[12]),
                    "mother_tongue": safe_str(student_data[13]),
                    "caste": safe_str(student_data[14]),
                    "religion": safe_str(student_data[15]),
                    "place_of_birth": safe_str(student_data[16]),
                    "aadhaar": safe_str(student_data[17]),
                    "disability": safe_str(student_data[18]),
                    "id_mark1": safe_str(student_data[19]),
                    "id_mark2": safe_str(student_data[20]),
                    "current_class": safe_str(student_data[21]),
                    "admission_class": safe_str(student_data[22]),
                    "admission_year": safe_str(student_data[23]),
                    "admission_date": safe_str(student_data[24]) if student_data[24] else "N/A",
                    "email": safe_str(student_data[25]),
                    "address": safe_str(student_data[26]),
                    "contact": safe_str(student_data[27]),
                    "alt_contact": safe_str(student_data[28]),
                    "country": safe_str(student_data[29]),
                    "state": safe_str(student_data[30]),
                    "city": safe_str(student_data[31]),
                    "pincode": safe_str(student_data[32]),
                    "status": safe_str(student_data[33]),
                    "house": safe_str(student_data[34]),
                    "teacher_ward": safe_str(student_data[35]),
                    "rte": safe_str(student_data[36]),
                    "sports_quota": safe_str(student_data[37]),
                    "prev_school": safe_str(student_data[38]),
                    "prev_board": safe_str(student_data[39]),
                    "father_name": safe_str(student_data[40]),
                    "father_name_tamil": safe_str(student_data[41]),
                    "mother_name": safe_str(student_data[42]),
                    "mother_name_tamil": safe_str(student_data[43]),
                    "father_contact": safe_str(student_data[44]),
                    "mother_contact": safe_str(student_data[45]),
                    "father_email": safe_str(student_data[46]),
                    "mother_email": safe_str(student_data[47]),
                    "father_qualification": safe_str(student_data[48]),
                    "mother_qualification": safe_str(student_data[49]),
                    "father_occupation": safe_str(student_data[50]),
                    "mother_occupation": safe_str(student_data[51]),
                    "father_income": safe_str(student_data[52]),
                    "mother_income": safe_str(student_data[53]),
                    "guardian_name": safe_str(student_data[54]),
                    "guardian_contact": safe_str(student_data[55]),
                    "guardian_email": safe_str(student_data[56]),
                    "child_living": safe_str(student_data[57]),
                    "rights_on_child": safe_str(student_data[58]),
                    "med_blood_group": safe_str(student_data[59]),
                    "diseases": safe_str(student_data[60]),
                    "allergies": safe_str(student_data[61]),
                    "medicines": safe_str(student_data[62]),
                    "hospital": safe_str(student_data[63]),
                    "doctor": safe_str(student_data[64])
                }

                # Store student data in session for PDF generation
                request.session['student_data'] = response_data

                return JsonResponse(response_data)

        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON data."}, status=400)
        except Exception as e:
            return JsonResponse({"error": f"Error processing request: {str(e)}"}, status=500)
    
    return JsonResponse({"error": "POST request required with QR code URL."}, status=400)

def download_student_pdf(request):
    if "admin_id" not in request.session:
        return JsonResponse({"error": "Admin not authenticated."}, status=401)
    
    if 'student_data' not in request.session:
        return JsonResponse({"error": "No student data found. Please scan QR code first."}, status=400)
    
    try:
        student_data = request.session['student_data']
        
        # Create PDF
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=72, leftMargin=72, topMargin=72, bottomMargin=18)
        
        # Container for the 'Flowable' objects
        elements = []
        
        # Define styles
        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=18,
            spaceAfter=30,
            alignment=TA_CENTER,
            textColor=colors.HexColor('#0052cc')
        )
        
        heading_style = ParagraphStyle(
            'CustomHeading',
            parent=styles['Heading2'],
            fontSize=14,
            spaceAfter=12,
            spaceBefore=20,
            textColor=colors.HexColor('#0052cc'),
            backColor=colors.HexColor('#f0f8ff'),
            borderPadding=8
        )
        
        normal_style = ParagraphStyle(
            'CustomNormal',
            parent=styles['Normal'],
            fontSize=10,
            spaceAfter=6,
            textColor=colors.black
        )
        
        # Add title
        title = Paragraph("Student Information Report", title_style)
        elements.append(title)
        
        subtitle = Paragraph("Manavargal School Management System", normal_style)
        elements.append(subtitle)
        
        from datetime import datetime
        date_para = Paragraph(f"Generated on: {datetime.now().strftime('%B %d, %Y')}", normal_style)
        elements.append(date_para)
        elements.append(Spacer(1, 20))
        
        # Add profile picture if available
        profile_picture = student_data.get('profile_picture_path')
        if profile_picture and os.path.exists(profile_picture):
            try:
                img = Image(profile_picture, width=2*inch, height=2*inch)
                img.hAlign = 'CENTER'
                elements.append(img)
                elements.append(Spacer(1, 20))
            except:
                pass
        
        # Basic Information Section
        elements.append(Paragraph("Basic Information", heading_style))
        basic_data = [
            ['Name:', student_data.get('name', 'N/A')],
            ['Admission Number:', student_data.get('admission_number', 'N/A')],
            ['Class:', f"{student_data.get('class', 'N/A')}-{student_data.get('section', 'N/A')}"],
            ['Roll Number:', student_data.get('roll_number', 'N/A')],
            ['EMIS:', student_data.get('emis', 'N/A')],
            ['Email:', student_data.get('email', 'N/A')]
        ]
        basic_table = Table(basic_data, colWidths=[2*inch, 4*inch])
        basic_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#e6f0ff')),
            ('TEXTCOLOR', (0, 0), (0, -1), colors.HexColor('#0052cc')),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#cccccc')),
            ('ROWBACKGROUNDS', (0, 0), (-1, -1), [colors.white, colors.HexColor('#f9f9f9')])
        ]))
        elements.append(basic_table)
        elements.append(Spacer(1, 15))
        
        # Personal Details Section
        elements.append(Paragraph("Personal Details", heading_style))
        personal_data = [
            ['Gender:', student_data.get('gender', 'N/A')],
            ['Date of Birth:', student_data.get('dob', 'N/A')],
            ['Tamil Name:', student_data.get('tamil_name', 'N/A')],
            ['Nationality:', student_data.get('nationality', 'N/A')],
            ['Blood Group:', student_data.get('blood_group', 'N/A')],
            ['Mother Tongue:', student_data.get('mother_tongue', 'N/A')],
            ['Community:', student_data.get('community', 'N/A')],
            ['Caste:', student_data.get('caste', 'N/A')],
            ['Religion:', student_data.get('religion', 'N/A')],
            ['Place of Birth:', student_data.get('place_of_birth', 'N/A')],
            ['Aadhaar:', student_data.get('aadhaar', 'N/A')],
            ['Disability:', student_data.get('disability', 'N/A')]
        ]
        personal_table = Table(personal_data, colWidths=[2*inch, 4*inch])
        personal_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#e6f0ff')),
            ('TEXTCOLOR', (0, 0), (0, -1), colors.HexColor('#0052cc')),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#cccccc')),
            ('ROWBACKGROUNDS', (0, 0), (-1, -1), [colors.white, colors.HexColor('#f9f9f9')])
        ]))
        elements.append(personal_table)
        elements.append(Spacer(1, 15))
        
        # Academic Information Section
        elements.append(Paragraph("Academic Information", heading_style))
        academic_data = [
            ['Current Class:', student_data.get('current_class', 'N/A')],
            ['Admission Class:', student_data.get('admission_class', 'N/A')],
            ['Admission Year:', student_data.get('admission_year', 'N/A')],
            ['Admission Date:', student_data.get('admission_date', 'N/A')],
            ['House:', student_data.get('house', 'N/A')],
            ['Teacher Ward:', student_data.get('teacher_ward', 'N/A')],
            ['RTE:', student_data.get('rte', 'N/A')],
            ['Sports Quota:', student_data.get('sports_quota', 'N/A')],
            ['Previous School:', student_data.get('prev_school', 'N/A')],
            ['Previous Board:', student_data.get('prev_board', 'N/A')]
        ]
        academic_table = Table(academic_data, colWidths=[2*inch, 4*inch])
        academic_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#e6f0ff')),
            ('TEXTCOLOR', (0, 0), (0, -1), colors.HexColor('#0052cc')),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#cccccc')),
            ('ROWBACKGROUNDS', (0, 0), (-1, -1), [colors.white, colors.HexColor('#f9f9f9')])
        ]))
        elements.append(academic_table)
        elements.append(Spacer(1, 15))
        
        # Contact Information Section
        elements.append(Paragraph("Contact Information", heading_style))
        contact_data = [
            ['Address:', student_data.get('address', 'N/A')],
            ['Contact:', student_data.get('contact', 'N/A')],
            ['Alternate Contact:', student_data.get('alt_contact', 'N/A')],
            ['Country:', student_data.get('country', 'N/A')],
            ['State:', student_data.get('state', 'N/A')],
            ['City:', student_data.get('city', 'N/A')],
            ['Pincode:', student_data.get('pincode', 'N/A')],
            ['Status:', student_data.get('status', 'N/A')]
        ]
        contact_table = Table(contact_data, colWidths=[2*inch, 4*inch])
        contact_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#e6f0ff')),
            ('TEXTCOLOR', (0, 0), (0, -1), colors.HexColor('#0052cc')),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#cccccc')),
            ('ROWBACKGROUNDS', (0, 0), (-1, -1), [colors.white, colors.HexColor('#f9f9f9')])
        ]))
        elements.append(contact_table)
        elements.append(Spacer(1, 15))
        
        # Father's Information Section
        elements.append(Paragraph("Father's Information", heading_style))
        father_data = [
            ['Father\'s Name:', student_data.get('father_name', 'N/A')],
            ['Father\'s Tamil Name:', student_data.get('father_name_tamil', 'N/A')],
            ['Father\'s Contact:', student_data.get('father_contact', 'N/A')],
            ['Father\'s Email:', student_data.get('father_email', 'N/A')],
            ['Father\'s Qualification:', student_data.get('father_qualification', 'N/A')],
            ['Father\'s Occupation:', student_data.get('father_occupation', 'N/A')],
            ['Father\'s Income:', student_data.get('father_income', 'N/A')]
        ]
        father_table = Table(father_data, colWidths=[2*inch, 4*inch])
        father_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#e6f0ff')),
            ('TEXTCOLOR', (0, 0), (0, -1), colors.HexColor('#0052cc')),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#cccccc')),
            ('ROWBACKGROUNDS', (0, 0), (-1, -1), [colors.white, colors.HexColor('#f9f9f9')])
        ]))
        elements.append(father_table)
        elements.append(Spacer(1, 15))
        
        # Mother's Information Section
        elements.append(Paragraph("Mother's Information", heading_style))
        mother_data = [
            ['Mother\'s Name:', student_data.get('mother_name', 'N/A')],
            ['Mother\'s Tamil Name:', student_data.get('mother_name_tamil', 'N/A')],
            ['Mother\'s Contact:', student_data.get('mother_contact', 'N/A')],
            ['Mother\'s Email:', student_data.get('mother_email', 'N/A')],
            ['Mother\'s Qualification:', student_data.get('mother_qualification', 'N/A')],
            ['Mother\'s Occupation:', student_data.get('mother_occupation', 'N/A')],
            ['Mother\'s Income:', student_data.get('mother_income', 'N/A')]
        ]
        mother_table = Table(mother_data, colWidths=[2*inch, 4*inch])
        mother_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#e6f0ff')),
            ('TEXTCOLOR', (0, 0), (0, -1), colors.HexColor('#0052cc')),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#cccccc')),
            ('ROWBACKGROUNDS', (0, 0), (-1, -1), [colors.white, colors.HexColor('#f9f9f9')])
        ]))
        elements.append(mother_table)
        elements.append(Spacer(1, 15))
        
        # Guardian Information Section
        elements.append(Paragraph("Guardian Information", heading_style))
        guardian_data = [
            ['Guardian\'s Name:', student_data.get('guardian_name', 'N/A')],
            ['Guardian\'s Contact:', student_data.get('guardian_contact', 'N/A')],
            ['Guardian\'s Email:', student_data.get('guardian_email', 'N/A')],
            ['Child Living With:', student_data.get('child_living', 'N/A')],
            ['Rights on Child:', student_data.get('rights_on_child', 'N/A')]
        ]
        guardian_table = Table(guardian_data, colWidths=[2*inch, 4*inch])
        guardian_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#e6f0ff')),
            ('TEXTCOLOR', (0, 0), (0, -1), colors.HexColor('#0052cc')),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#cccccc')),
            ('ROWBACKGROUNDS', (0, 0), (-1, -1), [colors.white, colors.HexColor('#f9f9f9')])
        ]))
        elements.append(guardian_table)
        elements.append(Spacer(1, 15))
        
        # Medical Information Section
        elements.append(Paragraph("Medical Information", heading_style))
        medical_data = [
            ['Medical Blood Group:', student_data.get('med_blood_group', 'N/A')],
            ['Diseases:', student_data.get('diseases', 'N/A')],
            ['Allergies:', student_data.get('allergies', 'N/A')],
            ['Medicines:', student_data.get('medicines', 'N/A')],
            ['Hospital:', student_data.get('hospital', 'N/A')],
            ['Doctor:', student_data.get('doctor', 'N/A')]
        ]
        medical_table = Table(medical_data, colWidths=[2*inch, 4*inch])
        medical_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#e6f0ff')),
            ('TEXTCOLOR', (0, 0), (0, -1), colors.HexColor('#0052cc')),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#cccccc')),
            ('ROWBACKGROUNDS', (0, 0), (-1, -1), [colors.white, colors.HexColor('#f9f9f9')])
        ]))
        elements.append(medical_table)
        
        # Build PDF
        doc.build(elements)
        
        # Get the value of the BytesIO buffer and write it to the response
        pdf = buffer.getvalue()
        buffer.close()
        
        # Create filename as requested: <name> <class and section> details.pdf
        name = student_data.get('name', 'Student').replace(' ', '_')
        class_section = f"{student_data.get('class', 'N/A')}{student_data.get('section', 'N/A')}"
        filename = f"{name}_{class_section}_details.pdf"
        
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        response.write(pdf)
        
        return response
        
    except Exception as e:
        return JsonResponse({"error": f"Error generating PDF: {str(e)}"}, status=500)
