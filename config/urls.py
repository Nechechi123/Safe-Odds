"""
URL configuration for the Safe Odds project.

Quick explanation for learning Django:
- This file is the "master router". It maps URL paths to views.
- When someone visits your site, Django checks these patterns top-to-bottom
  to find which view should handle the request.
- 'include()' lets each app (like 'matches') define its own URL patterns.
- The admin site gets its own URL at /admin/.
"""

from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('analytics.urls')),
    path('', include('matches.urls')),
]
