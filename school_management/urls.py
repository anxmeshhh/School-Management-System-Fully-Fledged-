from django.contrib import admin
from django.urls import path, include

from django.views.generic import TemplateView

urlpatterns = [
    path('sw.js', TemplateView.as_view(template_name='users/sw.js', content_type='application/javascript'), name='sw.js'),
    path('', include('users.urls')), 
]
