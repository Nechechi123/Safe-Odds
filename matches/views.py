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
    Separates the top match as the featured match for the hero spotlight.
    """
    now = timezone.now()
    matches = list(Match.objects.filter(
        is_published=True,
        kickoff__gte=now.replace(hour=0, minute=0, second=0, microsecond=0),
    ).order_by('kickoff'))

    featured_match = matches[0] if matches else None
    other_matches = matches[1:] if len(matches) > 1 else []

    context = {
        'matches': matches,
        'featured_match': featured_match,
        'other_matches': other_matches,
        'today_date': now.strftime('%B %d, %Y • %A'),
        'total_matches_count': len(matches),
        'sportybet_url': getattr(settings, 'SPORTYBET_URL', 'https://www.sportybet.com'),
    }
    return render(request, 'matches/home.html', context)
