"""
Admin configuration for the matches app.

Quick explanation for learning Django:
- The Django Admin is a built-in dashboard that lets you manage your
  database through a web interface — no code needed.
- By registering the Match and SiteSettings models here, you get a full
  CRUD interface at /admin/.
"""

from django.contrib import admin
from .models import Match, SiteSettings


@admin.register(Match)
class MatchAdmin(admin.ModelAdmin):
    list_display = (
        'kickoff', 'home_team', 'away_team', 'tip', 'odds',
        'confidence', 'result', 'is_published',
    )
    list_filter = ('league', 'result', 'is_published')
    search_fields = ('home_team', 'away_team', 'league')
    list_editable = ('result', 'is_published')
    date_hierarchy = 'kickoff'

    fieldsets = (
        ('Match Info', {
            'fields': ('league', 'home_team', 'away_team', 'kickoff')
        }),
        ('Prediction & Odds', {
            'fields': ('tip', 'odds', 'confidence')
        }),
        ('Club Logos (Optional)', {
            'description': 'Leave blank to use the official club logo automatically, or paste direct image URLs.',
            'fields': ('home_team_logo_url', 'away_team_logo_url'),
            'classes': ('collapse',),
        }),
        ('Status & Result', {
            'fields': ('result', 'is_published')
        }),
    )


@admin.register(SiteSettings)
class SiteSettingsAdmin(admin.ModelAdmin):
    """Admin configuration for VIP pricing, perks, and dynamic site metrics."""
    fieldsets = (
        ('Branding', {
            'fields': ('site_title', 'tagline')
        }),
        ('VIP Membership Offer & WhatsApp Concierge', {
            'fields': (
                'vip_headline', 'vip_subline',
                ('vip_currency', 'vip_price', 'vip_period'),
                'whatsapp_number',
                'whatsapp_vip_message',
                'vip_features',
                'vip_payment_or_whatsapp_url',
                'vip_member_count',
            )
        }),
        ('Social Proof & Metrics', {
            'description': 'Set custom numbers or leave empty to calculate automatically from match history.',
            'fields': ('win_rate_override', 'total_predictions_override', 'active_users_label')
        }),
    )

    def has_add_permission(self, request):
        # Only allow 1 settings instance
        return not SiteSettings.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return False
