"""
Views for the matches app.

Quick explanation for learning Django:
- A "view" is a Python function that receives a web request and returns
  a web response (usually an HTML page).
- The view fetches data from the database and passes it to a template
  for rendering.
"""

from django.conf import settings
from django.shortcuts import render
from django.utils import timezone
from .models import Match


def home(request):
    """
    The main public page.
    Shows all published matches with kickoff today or in the future,
    ordered by kickoff time.
    """
    now = timezone.now()
    matches = Match.objects.filter(
        is_published=True,
        kickoff__gte=now.replace(hour=0, minute=0, second=0, microsecond=0),
    ).order_by('kickoff')

    context = {
        'matches': matches,
        'sportybet_url': settings.SPORTYBET_URL,
    }
    return render(request, 'matches/home.html', context)
