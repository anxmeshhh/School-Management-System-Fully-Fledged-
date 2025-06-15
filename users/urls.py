from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static
from django.urls import path
from users.views import profile_view, login_view  # Import views directly
urlpatterns = [
    path('', views.signup_view, name='signup'),  
    path('login/', views.login_view, name='login'),  
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('profile/', views.profile_view, name='profile_view'), 
    
    
    
    
    path('parent_login/', views.parent_login, name='parent_login'),
    path('parent_signup/', views.parent_signup, name='parent_signup'),
    path('parent_dashboard/', views.parent_dashboard, name='parent_dashboard'),
    path('mark_entry/', views.mark_entry, name='mark_entry'),
    path('save_marks/', views.save_marks, name='save_marks'),
    path('add_subject/', views.add_subject, name='add_subject'),
    path('delete_subject/', views.delete_subject, name='delete_subject'),
    path('progress_card/', views.progress_card, name='progress_card'),
    path('get_students/', views.get_students, name='get_students'),
    path('get_subjects/', views.get_subjects, name='get_subjects'),

    path('teacher_mark_entry/', views.teacher_mark_entry, name='teacher_mark_entry'),
    path('teacher_save_marks/', views.teacher_save_marks, name='teacher_save_marks'),
    path('teacher_add_subject/', views.teacher_add_subject, name='teacher_add_subject'),
    path('teacher_delete_subject/', views.teacher_delete_subject, name='teacher_delete_subject'),
    path('teacher_progress_card/', views.teacher_progress_card, name='teacher_progress_card'),
    path('teacher_get_students/', views.teacher_get_students, name='teacher_get_students'),
    path('teacher_get_subjects/', views.teacher_get_subjects, name='teacher_get_subjects'),

    path('homework/', views.homework_view, name='homework'),
    path('study_materials/', views.study_materials, name='study_materials'),
    
    path('teacher/', views.teacher_view, name='teacher'),
    path('teacher_profile/', views.teacher_profile, name='teacher_profile'),
    path('fees/', views.fees, name='fees'),
    
    path('generate-id-card/', views.generate_id_card, name='generate_id_card'),
    path('qr_page/', views.qr_page, name='qr_page'),

    path('bulk-id-card/', views.bulk_id_card, name='bulk_id_card'), 
    path('admin/', views.admin_page, name='admin_dashboard'),
    path('admin_login/', views.admin_login, name='admin_login'),
    path('admin_signup/', views.admin_signup, name='admin_signup'),
    path('admin_page/', views.admin_page, name='admin_page'),
    path('admin_portal/', views.admin_accept_portal, name='admin_accept_portal'),
    path('admin_study_materials_upload/', views.admin_study_materials_upload, name='admin_study_materials_upload'),  # Updated path
    path('teacher_study_materials_upload/', views.teacher_study_materials_upload, name='teacher_study_materials_upload'),  # Updated path
    path('media/<path:file_path>', views.serve_pdf, name='serve_pdf'),
    path('admin_homework_panel/', views.admin_homework_panel, name='admin_homework_panel'),
    path('teacher_homework_panel/', views.teacher_homework_panel, name='teacher_homework_panel'),
    path('teacher_accept_portal/', views.teacher_accept_portal, name='teacher_accept_portal'),

    path('admin_circular_upload/', views.admin_circular_upload, name='admin_circular_upload'),
    path('student_circular/', views.student_circular, name='student_circular'),
    path('teacher_circular_upload/', views.teacher_circular_upload, name='teacher_circular_upload'),
    
    path('student-portal/leave/', views.student_leave, name='student_leave'),
    path('download-leave-pdf/', views.download_leave_pdf, name='download_leave_pdf'),
     
    path('accept-portal/', views.admin_accept_portal, name='admin_accept_portal'),


    # URLs for View and Edit Class functionality
    path('view_edit_class/', views.view_edit_class, name='view_edit_class'),
    path('add_class/', views.add_class, name='add_class'),
    path('update_class/<int:class_id>/', views.update_class, name='update_class'),
    path('delete_class/<int:class_id>/', views.delete_class, name='delete_class'),

    # Student Information URLs
    path('student_info/', views.student_info, name='student_info'),
    path('add_student/', views.add_student, name='add_student'),
    path('update/<str:admission_number>/', views.update_student, name='update_student'),
    path('delete/<str:admission_number>/', views.delete_student, name='delete_student'),
    # Batch Management URLs
    path('view_batches/', views.view_batches, name='view_batches'),
    path('add_batch/', views.add_batch, name='add_batch'),
    path('update_batch/<int:batch_id>/', views.update_batch, name='update_batch'),
    path('delete_batch/<int:batch_id>/', views.delete_batch, name='delete_batch'),




    path('manage_users/', views.manage_users, name='manage_users'),
    path('add_user/', views.add_user, name='add_user'),
    path('update_user/<int:user_id>/', views.update_user, name='update_user'),
    path('delete_user/<int:user_id>/', views.delete_user, name='delete_user'),


    path('bulk-upload/', views.bulk_upload, name='bulk_upload'),


    path('teachers/', views.manage_teachers, name='manage_teachers'),
    path('teachers/add/', views.add_teacher, name='add_teacher'),
    path('teachers/update/', views.update_teacher, name='update_teacher'),
    path('teachers/delete/<int:teacher_id>/', views.delete_teacher, name='delete_teacher'),



    
    path('teacher_signup/', views.teacher_signup, name='teacher_signup'),
    path('teacher_login/', views.teacher_login, name='teacher_login'),
    path('teacher-dashboard/', views.teacher_dashboard, name='teacher_dashboard'),

   
    path('teacher_portal/', views.teacher_portal, name='teacher_portal'),
    path('mark_attendance/', views.mark_attendance, name='mark_attendance'),
    
    path('student_portal/', views.student_portal, name='student_portal'),
    path('admin_attendance/', views.admin_attendance_portal, name='admin_attendance_portal'),
    path('admin_mark_attendance/', views.admin_mark_attendance, name='admin_mark_attendance'),
    path('admin_generate_attendance_pdf/', views.admin_generate_attendance_pdf, name='admin_generate_attendance_pdf'),


    path('admin_timetable/', views.admin_timetable_view, name='admin_timetable'),
    path('admin_timetable/add/', views.admin_timetable_add, name='admin_timetable_add'),
    path('admin_timetable/edit/<int:id>/', views.admin_timetable_edit, name='admin_timetable_edit'),
    path('admin_timetable/delete/<int:id>/', views.admin_timetable_delete, name='admin_timetable_delete'),
    path('admin_timetable/weekly/', views.admin_timetable_weekly, name='admin_timetable_weekly'),
    path('admin_timetable/filter/', views.admin_timetable_filter, name='admin_timetable_filter'),
    
    # Teacher route
    path('teacher_timetable/', views.teacher_timetable_view, name='teacher_timetable'),
    
    # Student route
    path('student_timetable/', views.student_timetable_view, name='student_timetable'),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)


if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)