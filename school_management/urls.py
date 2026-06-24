from django.contrib import admin
from django.urls import path, include
from django.views.generic import TemplateView
from django.views.generic.base import RedirectView

urlpatterns = [
    path('sw.js', TemplateView.as_view(template_name='users/sw.js', content_type='application/javascript'), name='sw.js'),
    path('favicon.ico', RedirectView.as_view(url='/static/users/images/adminlogo.jpg', permanent=True)),
    path('', include('users.urls')), 
]
