from django.urls import path
from . import views

urlpatterns = [
    path('', views.signup_view, name='signup'),  # Default route (Signup Page)
    path('login/', views.login_view, name='login'),  # Login Page
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('profile/', views.profile_view, name='profile'),  # Profile Page
    path('attendance/', views.attendence_view, name='attendance'),
]
