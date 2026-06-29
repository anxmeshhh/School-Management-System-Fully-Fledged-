import json
import logging
import os
import urllib.parse
from datetime import datetime

from django.conf import settings
from django.db import connection
from django.http import FileResponse, Http404, JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt

from users.whatsapp_beta_config import WhatsAppBetaConfig
from users.whatsapp_beta_regulator import WhatsAppBetaRegulator

logger = logging.getLogger(__name__)


def get_client_ip(request):
    x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
    if x_forwarded_for:
        return x_forwarded_for.split(",")[0]
    return request.META.get("REMOTE_ADDR")


def get_user_agent(request):
    return request.META.get("HTTP_USER_AGENT", "")


def get_request_actor(request):
    """Resolve Django auth and the app's custom admin/teacher sessions."""
    if getattr(request, "user", None) and request.user.is_authenticated:
        role = "admin" if request.user.is_staff else "support"
        return {
            "user_id": request.user.id,
            "email": getattr(request.user, "email", "") or getattr(request.user, "username", ""),
            "role": role,
            "auto_approve": request.user.is_staff,
        }

    if request.session.get("admin_id"):
        return {
            "user_id": int(request.session["admin_id"]),
            "email": request.session.get("admin_email", ""),
            "role": "admin",
            "auto_approve": True,
        }

    if request.session.get("teacher_id"):
        return {
            "user_id": int(request.session["teacher_id"]),
            "email": request.session.get("teacher_email", ""),
            "role": "teacher",
            "auto_approve": True,
        }

    return None


def build_class_section(student_class, section):
    student_class = WhatsAppBetaConfig.safe_display_value(student_class, "")
    section = WhatsAppBetaConfig.safe_display_value(section, "")
    if student_class and section:
        return f"{student_class}-{section}"
    if student_class:
        return student_class
    return "N/A"


def get_student_context(student_id=None, admission_number=None):
    if not student_id and not admission_number:
        return {}

    try:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT
                    s1.id, s1.user_id, s1.name, s1.admission_number, s1.class, s1.section,
                    s2.dob, s3.contact, s3.alt_contact,
                    s4.father_name, s4.father_contact, s4.mother_name, s4.mother_contact,
                    s4.guardian_name, s4.guardian_contact
                FROM student_page1 s1
                LEFT JOIN student_page2 s2 ON s1.user_id = s2.user_id
                LEFT JOIN student_page3 s3 ON s1.user_id = s3.user_id
                LEFT JOIN student_page4 s4 ON s1.user_id = s4.user_id
                WHERE (%s IS NOT NULL AND s1.id = %s)
                   OR (%s IS NOT NULL AND s1.user_id = %s)
                   OR (%s IS NOT NULL AND s1.admission_number = %s)
                LIMIT 1
                """,
                [student_id, student_id, student_id, student_id, admission_number, admission_number],
            )
            row = cursor.fetchone()
    except Exception as exc:
        logger.error("Error fetching student context: %s", exc)
        return {}

    if not row:
        return {}

    return {
        "student_row_id": row[0],
        "student_user_id": row[1],
        "student_id": row[0],
        "student_name": row[2],
        "name": row[2],
        "admission_number": row[3],
        "student_class": row[4],
        "section": row[5],
        "class_section": build_class_section(row[4], row[5]),
        "dob": row[6],
        "student_contact": row[7],
        "alt_contact": row[8],
        "father_name": row[9],
        "father_contact": row[10],
        "mother_name": row[11],
        "mother_contact": row[12],
        "guardian_name": row[13],
        "guardian_contact": row[14],
    }


def choose_recipient_phone(payload, student_context):
    candidates = [
        payload.get("mobile"),
        payload.get("phone"),
        payload.get("father_contact"),
        payload.get("mother_contact"),
        payload.get("guardian_contact"),
        student_context.get("father_contact"),
        student_context.get("mother_contact"),
        student_context.get("guardian_contact"),
        student_context.get("student_contact"),
        student_context.get("alt_contact"),
    ]

    for candidate in candidates:
        phone, error = WhatsAppBetaConfig.normalize_phone_number(candidate)
        if not error:
            return phone, None

    return "", "Missing valid parent/student WhatsApp number"


def build_message_payload(request, template_type):
    payload = request.POST.dict()
    student_context = get_student_context(payload.get("student_id"), payload.get("admission_number"))
    merged = {**student_context, **payload}

    merged["school_name"] = payload.get("school_name") or "School Administration"
    merged["student_name"] = WhatsAppBetaConfig.safe_display_value(
        merged.get("student_name") or merged.get("name"),
        "Student",
    )
    merged["name"] = WhatsAppBetaConfig.safe_display_value(merged.get("name"), merged["student_name"])
    merged["class_section"] = payload.get("class_section") or build_class_section(
        merged.get("student_class") or merged.get("class"),
        merged.get("section"),
    )
    merged["date"] = payload.get("date") or datetime.now().strftime("%Y-%m-%d")
    merged["time"] = WhatsAppBetaConfig.safe_display_value(merged.get("time"))
    merged["reason"] = WhatsAppBetaConfig.safe_display_value(merged.get("reason"))
    merged["title"] = WhatsAppBetaConfig.safe_display_value(merged.get("title"))
    merged["status"] = WhatsAppBetaConfig.safe_display_value(merged.get("status"))
    merged["duration"] = WhatsAppBetaConfig.safe_display_value(merged.get("duration"))
    merged["start_date"] = payload.get("start_date") or payload.get("leave_start_date") or "N/A"
    merged["end_date"] = payload.get("end_date") or payload.get("leave_end_date") or "N/A"
    merged["circular_url"] = payload.get("circular_url") or payload.get("file_url") or "N/A"
    merged["message"] = WhatsAppBetaConfig.safe_display_value(merged.get("message"))
    merged["portal_url"] = WhatsAppBetaConfig.safe_display_value(merged.get("portal_url"))
    merged["mobile"] = WhatsAppBetaConfig.safe_display_value(merged.get("mobile"))

    return merged


def regulated_actor_or_response(request, response_data, client_ip, user_agent, action_type, message_type):
    actor = get_request_actor(request)
    if not actor:
        response_data["error"] = "User must be authenticated"
        WhatsAppBetaRegulator.log_usage(
            0, action_type, message_type, "", "", "unauthorized", "",
            client_ip, user_agent, error_message="Not authenticated",
        )
        return None, JsonResponse(response_data, status=401)

    WhatsAppBetaRegulator.ensure_beta_tester(
        actor["user_id"], actor["email"], actor["role"], actor["auto_approve"]
    )
    is_allowed, access_reason = WhatsAppBetaRegulator.validate_user_access(actor["user_id"])
    if not is_allowed:
        response_data["error"] = access_reason
        WhatsAppBetaRegulator.log_usage(
            actor["user_id"], action_type, message_type, "", "", "unauthorized", "",
            client_ip, user_agent, error_message=access_reason,
        )
        return None, JsonResponse(response_data, status=403)

    return actor, None


def generate_student_pdf_regulated(student_id, admission_number, name):
    pdf_dir = os.path.join(settings.MEDIA_ROOT, "student_pdfs")
    os.makedirs(pdf_dir, exist_ok=True)
    file_path = os.path.join(pdf_dir, f"{student_id}_{name.replace(' ', '_')}.pdf")

    try:
        from reportlab.pdfgen import canvas

        c = canvas.Canvas(file_path)
        c.setFont("Helvetica-Bold", 16)
        c.drawString(180, 780, "STUDENT INFORMATION")
        c.setFont("Helvetica", 12)
        c.drawString(100, 740, f"Name : {name}")
        c.drawString(100, 720, f"Admission No : {admission_number}")
        c.setFont("Helvetica", 10)
        c.drawString(100, 680, "This document is auto-generated by the school system.")
        c.drawString(100, 665, "Issued by School Administration.")
        c.setFont("Helvetica", 8)
        c.drawString(100, 630, f"[BETA TESTING - v{WhatsAppBetaConfig.BETA_VERSION}]")
        c.save()
        return file_path, True, "PDF generated successfully"
    except Exception as exc:
        logger.error("Error generating PDF: %s", exc)
        return None, False, str(exc)


@csrf_exempt
def generate_whatsapp_link_regulated(request):
    client_ip = get_client_ip(request)
    user_agent = get_user_agent(request)
    response_data = {
        "success": False,
        "error": None,
        "whatsapp_url": None,
        "warning": None,
        "rate_info": None,
    }

    try:
        actor, error_response = regulated_actor_or_response(
            request, response_data, client_ip, user_agent, "send_pdf", "student_pdf"
        )
        if error_response:
            return error_response
        user_id = actor["user_id"]

        can_send, remaining, reset_time = WhatsAppBetaRegulator.check_rate_limit(user_id)
        response_data["rate_info"] = {
            "messages_remaining": remaining,
            "reset_time": reset_time.isoformat() if reset_time else None,
        }
        if not can_send:
            response_data["error"] = f"Rate limit exceeded. Resets at {reset_time}"
            WhatsAppBetaRegulator.log_usage(
                user_id, "send_pdf", "student_pdf", "", "", "rate_limit_exceeded", "",
                client_ip, user_agent, error_message="Rate limit exceeded",
            )
            return JsonResponse(response_data, status=429)

        feature_enabled, feature_reason = WhatsAppBetaRegulator.validate_feature("send_student_pdfs", user_id)
        if not feature_enabled:
            response_data["error"] = feature_reason
            return JsonResponse(response_data, status=400)

        mobile = request.POST.get("mobile", "").strip()
        name = request.POST.get("name", "").strip()
        admission_number = request.POST.get("admission_number", "").strip()
        student_id = request.POST.get("student_id", "").strip()

        if not all([mobile, name, student_id]):
            response_data["error"] = "Missing required fields (mobile, name, student_id)"
            return JsonResponse(response_data, status=400)

        mobile, phone_error = WhatsAppBetaConfig.normalize_phone_number(mobile)
        if phone_error:
            response_data["error"] = phone_error
            WhatsAppBetaRegulator.log_usage(
                user_id, "send_pdf", "student_pdf", mobile, name, "failed", "",
                client_ip, user_agent, error_message=phone_error,
                metadata={"student_id": student_id, "admission_number": admission_number},
            )
            return JsonResponse(response_data, status=400)

        _, pdf_success, pdf_message = generate_student_pdf_regulated(student_id, admission_number, name)
        if not pdf_success:
            response_data["error"] = f"PDF generation failed: {pdf_message}"
            WhatsAppBetaRegulator.log_usage(
                user_id, "send_pdf", "student_pdf", mobile, name, "failed", "",
                client_ip, user_agent, error_message=response_data["error"],
            )
            return JsonResponse(response_data, status=500)

        pdf_url = request.build_absolute_uri(f"/media/student_pdfs/{student_id}_{name.replace(' ', '_')}.pdf")
        message = WhatsAppBetaConfig.get_message_template(
            "student_pdf",
            school_name="School Administration",
            name=name,
            admission_number=admission_number,
            pdf_url=pdf_url,
        )
        whatsapp_url = WhatsAppBetaConfig.WHATSAPP_API_ENDPOINT + mobile + "?text=" + urllib.parse.quote(message)

        WhatsAppBetaRegulator.log_usage(
            user_id, "send_pdf", "student_pdf", mobile, name, "success", message[:500],
            client_ip, user_agent,
            metadata={"student_id": student_id, "admission_number": admission_number},
        )
        _increment_beta_usage(user_id)
        _create_message_audit(user_id, mobile, name, message, "student_pdf", {"student_id": student_id})

        response_data["success"] = True
        response_data["whatsapp_url"] = whatsapp_url
        response_data["rate_info"]["messages_remaining"] = remaining - 1
        return JsonResponse(response_data)
    except Exception as exc:
        logger.error("Error generating WhatsApp link: %s", exc, exc_info=True)
        response_data["error"] = "Internal server error"
        return JsonResponse(response_data, status=500)


@csrf_exempt
def generate_whatsapp_message_link_regulated(request):
    client_ip = get_client_ip(request)
    user_agent = get_user_agent(request)
    template_type = request.POST.get("message_type", "notification").strip()
    action_type = f"send_{template_type}"

    response_data = {
        "success": False,
        "error": None,
        "whatsapp_url": None,
        "message": None,
        "missing_optional_fields": [],
        "rate_info": None,
    }

    if template_type not in WhatsAppBetaConfig.MESSAGE_TEMPLATES:
        response_data["error"] = "Unsupported WhatsApp message type"
        return JsonResponse(response_data, status=400)

    try:
        actor, error_response = regulated_actor_or_response(
            request, response_data, client_ip, user_agent, action_type, template_type
        )
        if error_response:
            return error_response
        user_id = actor["user_id"]

        can_send, remaining, reset_time = WhatsAppBetaRegulator.check_rate_limit(user_id)
        response_data["rate_info"] = {
            "messages_remaining": remaining,
            "reset_time": reset_time.isoformat() if reset_time else None,
        }
        if not can_send:
            response_data["error"] = f"Rate limit exceeded. Resets at {reset_time}"
            WhatsAppBetaRegulator.log_usage(
                user_id, action_type, template_type, "", "", "rate_limit_exceeded", "",
                client_ip, user_agent, error_message="Rate limit exceeded",
            )
            return JsonResponse(response_data, status=429)

        feature_name = WhatsAppBetaConfig.get_template_feature(template_type)
        feature_enabled, feature_reason = WhatsAppBetaRegulator.validate_feature(feature_name, user_id)
        if not feature_enabled:
            response_data["error"] = feature_reason
            WhatsAppBetaRegulator.log_usage(
                user_id, action_type, template_type, "", "", "feature_disabled", "",
                client_ip, user_agent, error_message=feature_reason,
            )
            return JsonResponse(response_data, status=400)

        payload = build_message_payload(request, template_type)
        missing_required = WhatsAppBetaConfig.validate_template_payload(template_type, payload)
        if missing_required:
            response_data["error"] = f"Missing required fields: {', '.join(missing_required)}"
            WhatsAppBetaRegulator.log_usage(
                user_id, action_type, template_type, "", payload.get("student_name", ""),
                "failed", "", client_ip, user_agent,
                error_message=response_data["error"],
                metadata={"missing_required": missing_required},
            )
            return JsonResponse(response_data, status=400)

        mobile, phone_error = choose_recipient_phone(request.POST, payload)
        recipient_name = (
            request.POST.get("recipient_name")
            or payload.get("father_name")
            or payload.get("mother_name")
            or payload.get("guardian_name")
            or payload.get("student_name")
            or "Parent"
        )
        if phone_error:
            response_data["error"] = phone_error
            WhatsAppBetaRegulator.log_usage(
                user_id, action_type, template_type, "", recipient_name, "failed", "",
                client_ip, user_agent, error_message=phone_error,
                metadata={"student_id": request.POST.get("student_id")},
            )
            return JsonResponse(response_data, status=400)

        optional_fields = {
            "parent_circular": ["class_section", "date"],
            "birthday": ["dob", "class_section"],
            "late": ["time", "reason"],
            "leave": ["start_date", "end_date", "duration", "reason"],
        }.get(template_type, [])
        response_data["missing_optional_fields"] = [
            field for field in optional_fields
            if WhatsAppBetaConfig.safe_display_value(payload.get(field), "") == ""
        ]

        message = WhatsAppBetaConfig.get_message_template(template_type, **payload)
        if not message:
            response_data["error"] = "Could not build WhatsApp message"
            return JsonResponse(response_data, status=400)

        whatsapp_url = WhatsAppBetaConfig.WHATSAPP_API_ENDPOINT + mobile + "?text=" + urllib.parse.quote(message)

        WhatsAppBetaRegulator.log_usage(
            user_id, action_type, template_type, mobile, recipient_name, "success", message[:500],
            client_ip, user_agent,
            metadata={
                "student_id": request.POST.get("student_id"),
                "admission_number": payload.get("admission_number"),
                "missing_optional_fields": response_data["missing_optional_fields"],
            },
        )
        _increment_beta_usage(user_id)
        _create_message_audit(
            user_id,
            mobile,
            recipient_name,
            message,
            template_type,
            {
                "manual_send_required": True,
                "student_id": request.POST.get("student_id"),
                "missing_optional_fields": response_data["missing_optional_fields"],
            },
        )

        for alert_type, severity, alert_msg in WhatsAppBetaRegulator.check_compliance_alerts(user_id):
            WhatsAppBetaRegulator.create_compliance_alert(user_id, alert_type, severity, alert_msg)

        response_data["success"] = True
        response_data["whatsapp_url"] = whatsapp_url
        response_data["message"] = message
        response_data["rate_info"]["messages_remaining"] = remaining - 1
        return JsonResponse(response_data)
    except Exception as exc:
        logger.error("Error generating regulated WhatsApp message: %s", exc, exc_info=True)
        response_data["error"] = "Internal server error"
        return JsonResponse(response_data, status=500)


def _increment_beta_usage(user_id):
    with connection.cursor() as cursor:
        cursor.execute(
            """
            UPDATE whatsapp_beta_testers
            SET messages_sent_today = messages_sent_today + 1,
                total_messages_sent = total_messages_sent + 1,
                last_used = NOW()
            WHERE user_id = %s
            """,
            [user_id],
        )


def _create_message_audit(user_id, mobile, recipient_name, message, message_type, metadata):
    with connection.cursor() as cursor:
        cursor.execute(
            """
            INSERT INTO whatsapp_beta_messages (
                user_id, recipient_phone, recipient_name, message_content,
                message_type, status, sent_at, template_used, metadata
            )
            VALUES (%s, %s, %s, %s, %s, 'pending', NOW(), %s, %s)
            """,
            [user_id, mobile, recipient_name, message, message_type, message_type, json.dumps(metadata or {})],
        )


def admin_send_student_pdf_regulated(request):
    actor = get_request_actor(request)
    if not actor:
        return render(
            request,
            "users/error.html",
            {"error": "Please log in before using WhatsApp beta.", "title": "WhatsApp Beta Access Denied"},
        )

    user_id = actor["user_id"]
    WhatsAppBetaRegulator.ensure_beta_tester(user_id, actor["email"], actor["role"], actor["auto_approve"])
    is_allowed, reason = WhatsAppBetaRegulator.validate_user_access(user_id)
    if not is_allowed:
        return render(request, "users/error.html", {"error": reason, "title": "WhatsApp Beta Access Denied"})

    try:
        can_send, remaining, reset_time = WhatsAppBetaRegulator.check_rate_limit(user_id)

        # Pass admin session context for the template header
        admin_name = request.session.get("admin_name", actor.get("email", "Admin"))

        return render(
            request,
            "users/send_pdf_whatsapp.html",
            {
                "can_send": can_send,
                "messages_remaining": remaining,
                "reset_time": reset_time,
                "beta_version": WhatsAppBetaConfig.BETA_VERSION,
                "feature_enabled": WhatsAppBetaConfig.is_feature_enabled("send_student_pdfs"),
                "admin_name": admin_name,
                "notification_user_id": user_id,
                "message_types": list(WhatsAppBetaConfig.MESSAGE_TEMPLATES.keys()),
                "features": WhatsAppBetaConfig.FEATURES,
            },
        )
    except Exception as exc:
        logger.error("Error loading admin panel: %s", exc)
        return render(request, "users/error.html", {"error": "Error loading student data", "title": "Error"})


def serve_student_pdf_regulated(request, filename):
    file_path = os.path.join(settings.MEDIA_ROOT, "student_pdfs", filename)
    if not os.path.exists(file_path):
        raise Http404("PDF not found")
    return FileResponse(open(file_path, "rb"), content_type="application/pdf")


# ─── Dynamic Data APIs for WhatsApp Frontend ─────────────────────────────


def admin_bulk_announce(request):
    """Bulk announcement page — message all parents about the school portal."""
    actor = get_request_actor(request)
    if not actor:
        return render(request, "users/error.html", {"error": "Please log in first.", "title": "Access Denied"})

    user_id = actor["user_id"]
    WhatsAppBetaRegulator.ensure_beta_tester(user_id, actor["email"], actor["role"], actor["auto_approve"])
    is_allowed, reason = WhatsAppBetaRegulator.validate_user_access(user_id)
    if not is_allowed:
        return render(request, "users/error.html", {"error": reason, "title": "Access Denied"})

    admin_name = request.session.get("admin_name", actor.get("email", "Admin"))
    school_name = request.session.get("school_name", "School Administration")
    portal_url = request.build_absolute_uri("/parent/")

    return render(request, "users/bulk_announce_whatsapp.html", {
        "admin_name": admin_name,
        "school_name": school_name,
        "portal_url": portal_url,
        "notification_user_id": user_id,
    })


def api_all_parent_contacts(request):
    """Return all unique parent contacts for bulk announcement."""
    actor = get_request_actor(request)
    if not actor:
        return JsonResponse({"error": "Unauthorized"}, status=401)

    try:
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT
                    s1.id,
                    s1.name,
                    s1.admission_number,
                    s1.class,
                    s1.section,
                    COALESCE(s4.father_name, s4.mother_name, s4.guardian_name, '') AS parent_name,
                    COALESCE(s4.father_contact, s4.mother_contact, s4.guardian_contact, s3.contact, '') AS contact,
                    s4.father_contact,
                    s4.mother_contact,
                    s4.guardian_contact
                FROM student_page1 s1
                LEFT JOIN student_page3 s3 ON s1.user_id = s3.user_id
                LEFT JOIN student_page4 s4 ON s1.user_id = s4.user_id
                ORDER BY s1.class, s1.name
            """)
            rows = cursor.fetchall()

        seen_phones = set()
        parents = []
        for r in rows:
            contact = r[6] or ""
            phone, err = WhatsAppBetaConfig.normalize_phone_number(contact)
            if err or not phone:
                # No valid number — still include so admin sees missing data
                parents.append({
                    "student_id": r[0],
                    "student_name": r[1] or "",
                    "admission_number": r[2] or "",
                    "class": r[3] or "",
                    "section": r[4] or "",
                    "parent_name": r[5] or "",
                    "contact": contact,
                    "normalized_phone": "",
                    "has_number": False,
                    "father_contact": r[7] or "",
                    "mother_contact": r[8] or "",
                    "guardian_contact": r[9] or "",
                })
            else:
                is_duplicate = phone in seen_phones
                seen_phones.add(phone)
                parents.append({
                    "student_id": r[0],
                    "student_name": r[1] or "",
                    "admission_number": r[2] or "",
                    "class": r[3] or "",
                    "section": r[4] or "",
                    "parent_name": r[5] or "",
                    "contact": contact,
                    "normalized_phone": phone,
                    "has_number": True,
                    "is_duplicate": is_duplicate,
                    "father_contact": r[7] or "",
                    "mother_contact": r[8] or "",
                    "guardian_contact": r[9] or "",
                })

        total = len(parents)
        with_number = sum(1 for p in parents if p["has_number"])
        unique_numbers = len(seen_phones)

        return JsonResponse({
            "parents": parents,
            "stats": {
                "total": total,
                "with_number": with_number,
                "unique_numbers": unique_numbers,
                "missing_number": total - with_number,
            }
        })
    except Exception as exc:
        logger.error("Error fetching parent contacts: %s", exc)
        return JsonResponse({"error": "Failed to load contacts"}, status=500)


def api_whatsapp_classes(request):
    """Return all distinct classes from admin_student_classes for the WhatsApp panel."""
    actor = get_request_actor(request)
    if not actor:
        return JsonResponse({"error": "Unauthorized"}, status=401)

    try:
        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT DISTINCT class FROM admin_student_classes ORDER BY class"
            )
            classes = [row[0] for row in cursor.fetchall() if row[0]]
        return JsonResponse({"classes": classes})
    except Exception as exc:
        logger.error("Error fetching classes: %s", exc)
        return JsonResponse({"error": "Failed to load classes"}, status=500)


def api_whatsapp_sections(request):
    """Return sections for a given class from admin_student_classes."""
    actor = get_request_actor(request)
    if not actor:
        return JsonResponse({"error": "Unauthorized"}, status=401)

    student_class = request.GET.get("class", "").strip()
    if not student_class:
        return JsonResponse({"sections": []})

    try:
        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT DISTINCT section FROM admin_student_classes WHERE class = %s ORDER BY section",
                [student_class],
            )
            sections = [row[0].strip() for row in cursor.fetchall() if row[0] and row[0].strip()]
        return JsonResponse({"sections": sections})
    except Exception as exc:
        logger.error("Error fetching sections: %s", exc)
        return JsonResponse({"error": "Failed to load sections"}, status=500)


def api_whatsapp_students(request):
    """Return students with contact details for a given class + section."""
    actor = get_request_actor(request)
    if not actor:
        return JsonResponse({"error": "Unauthorized"}, status=401)

    student_class = request.GET.get("class", "").strip()
    section = request.GET.get("section", "").strip()

    try:
        with connection.cursor() as cursor:
            query = """
                SELECT
                    s1.id,
                    s1.user_id,
                    s1.name,
                    s1.admission_number,
                    s1.class,
                    s1.section,
                    s3.contact,
                    s3.alt_contact,
                    s4.father_name,
                    s4.father_contact,
                    s4.mother_name,
                    s4.mother_contact,
                    s4.guardian_name,
                    s4.guardian_contact
                FROM student_page1 s1
                LEFT JOIN student_page3 s3 ON s1.user_id = s3.user_id
                LEFT JOIN student_page4 s4 ON s1.user_id = s4.user_id
            """
            
            params = []
            if student_class and section:
                query += " WHERE s1.class = %s AND s1.section = %s"
                params.extend([student_class, section])
            elif student_class:
                query += " WHERE s1.class = %s"
                params.append(student_class)
                
            query += " ORDER BY s1.class, s1.section, s1.name"
            
            cursor.execute(query, params)
            rows = cursor.fetchall()

        students = []
        for r in rows:
            # Pick best available contact number
            contact = r[6] or r[9] or r[11] or r[13] or r[7] or ""
            parent_name = r[8] or r[10] or r[12] or ""
            students.append({
                "id": r[0],
                "user_id": r[1],
                "name": r[2] or "",
                "admission_number": r[3] or "",
                "class": r[4] or "",
                "section": r[5] or "",
                "contact": contact,
                "alt_contact": r[7] or "",
                "father_name": r[8] or "",
                "father_contact": r[9] or "",
                "mother_name": r[10] or "",
                "mother_contact": r[11] or "",
                "guardian_name": r[12] or "",
                "guardian_contact": r[13] or "",
                "parent_name": parent_name,
            })

        return JsonResponse({"students": students, "count": len(students)})
    except Exception as exc:
        logger.error("Error fetching students for WhatsApp: %s", exc)
        return JsonResponse({"error": "Failed to load students"}, status=500)
