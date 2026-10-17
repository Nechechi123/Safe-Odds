"""
Read-only admin views for analytics — browse raw page views and clicks.
"""

from django.contrib import admin

from .models import ClickEvent, PageView


@admin.register(PageView)
class PageViewAdmin(admin.ModelAdmin):
    list_display = ('created_at', 'path', 'route_name', 'device', 'browser', 'referrer_host', 'is_bot')
    list_filter = ('device', 'browser', 'is_bot', 'route_name')
    search_fields = ('path', 'referrer_host', 'visitor')
    date_hierarchy = 'created_at'

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False


@admin.register(ClickEvent)
class ClickEventAdmin(admin.ModelAdmin):
    list_display = ('created_at', 'target', 'path', 'match_id', 'device', 'is_bot')
    list_filter = ('target', 'device', 'is_bot')
    search_fields = ('target', 'path', 'visitor')
    date_hierarchy = 'created_at'

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False
