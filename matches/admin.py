"""
Admin configuration for the matches app.

Quick explanation for learning Django:
- The Django Admin is a built-in dashboard that lets you manage your
  database through a web interface — no code needed.
- By registering the Match model here, you get a full CRUD (Create, Read,
  Update, Delete) interface at /admin/matches/.
- list_display controls which columns show in the list view.
- list_filter adds sidebar filters.
- list_editable lets you edit fields directly in the list (no need to
  open each match individually).
"""

from django.contrib import admin
from .models import Match


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
