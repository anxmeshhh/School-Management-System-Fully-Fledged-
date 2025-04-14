from django.urls import path
from . import views

urlpatterns = [
    path('', views.signup_view, name='signup'),  # Default route (Signup Page)
    path('login/', views.login_view, name='login'),  # Login Page
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('profile/', views.profile_view, name='profile'),  # Profile Page
    path('attendance/', views.attendence_view, name='attendance'),
    path('circular/', views.circular_view, name='circular'),
    path('parent_login/', views.parent_login, name='parent_login'),
    path('parent_signup/', views.parent_signup, name='parent_signup'),

]
