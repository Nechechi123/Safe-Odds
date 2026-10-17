"""
URL patterns for the matches app.

Quick explanation for learning Django:
- This file maps URL paths to views, but only for this app.
- It's included by the main config/urls.py file.
- The empty string '' means the root URL (homepage).
"""

from django.urls import path
from . import views

app_name = 'matches'

urlpatterns = [
    path('', views.home, name='home'),
    path('results/', views.results, name='results'),
    path('contact/', views.contact, name='contact'),
]
