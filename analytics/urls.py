"""URL patterns for the analytics app (tracked redirects + JS beacon)."""

from django.urls import path

from . import views

app_name = 'analytics'

urlpatterns = [
    path('go/<slug:slug>/', views.go, name='go'),
    path('api/track/', views.track, name='track'),
    path('staff/analytics/', views.dashboard, name='dashboard'),
]
