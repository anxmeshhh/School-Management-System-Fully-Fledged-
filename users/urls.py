from django.urls import path
from . import views

urlpatterns = [
    path('', views.signup_view, name='signup'),  # Default route (Signup Page)
    path('signup/', views.signup_view, name='signup'),  # Explicit signup route
    path('login/', views.login_view, name='login'),  # Login Page
    path('profile/', views.profile_view, name='profile'),  # Profile Page
]
