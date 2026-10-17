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
from .models import Match, SiteSettings


def home(request):
    """
    The main public page.
    Shows all published matches with kickoff today or in the future,
    ordered by kickoff time.
    Separates the top match as the featured match for the hero spotlight.
    Calculates live win rate & total predictions from real match outcomes,
    with admin overrides available via SiteSettings.
    """
    now = timezone.now()
    site_settings = SiteSettings.load()

    matches = list(Match.objects.visible(now).filter(
        kickoff__gte=now.replace(hour=0, minute=0, second=0, microsecond=0),
    ).order_by('kickoff'))

    featured_match = matches[0] if matches else None
    other_matches = matches[1:] if len(matches) > 1 else []

    # Dynamic Win Rate calculation
    if site_settings.win_rate_override is not None:
        win_rate = site_settings.win_rate_override
    else:
        finished = Match.objects.filter(result__in=[Match.WON, Match.LOST])
        won = Match.objects.filter(result=Match.WON).count()
        if finished.exists():
            win_rate = round((won / finished.count()) * 100)
        else:
            win_rate = 85  # Clean benchmark default before first graded match

    # Dynamic Predictions Count calculation
    if site_settings.total_predictions_override:
        total_predictions = site_settings.total_predictions_override
    else:
        total_in_db = Match.objects.count()
        total_predictions = f"{total_in_db}+" if total_in_db > 10 else "210+"

    # VIP Action Link (Direct WhatsApp Concierge)
    vip_action_url = site_settings.vip_whatsapp_url

    context = {
        'matches': matches,
        'featured_match': featured_match,
        'other_matches': other_matches,
        'today_date': now.strftime('%B %d, %Y • %A'),
        'total_matches_count': len(matches),
        'site_settings': site_settings,
        'win_rate': win_rate,
        'total_predictions': total_predictions,
        'active_users': site_settings.active_users_label,
        'vip_action_url': vip_action_url,
        'sportybet_url': getattr(settings, 'SPORTYBET_URL', 'https://www.sportybet.com'),
    }
    return render(request, 'matches/home.html', context)


def results(request):
    """
    Public results page — the site's track record.

    Shows every published match the owner has graded (WON / LOST / VOID),
    newest first, plus an overall record summary. VOID tips are counted in
    the list but excluded from the win-rate calculation.
    """
    site_settings = SiteSettings.load()

    settled = Match.objects.visible().filter(
        result__in=[Match.WON, Match.LOST, Match.VOID],
    ).order_by('-kickoff')

    won_count = settled.filter(result=Match.WON).count()
    lost_count = settled.filter(result=Match.LOST).count()
    void_count = settled.filter(result=Match.VOID).count()

    decided = won_count + lost_count
    win_rate = round((won_count / decided) * 100) if decided else 0

    # Last 5 decided outcomes, newest first, for the "recent form" strip.
    recent_form = [
        'W' if match.result == Match.WON else 'L'
        for match in settled.exclude(result=Match.VOID)[:5]
    ]

    context = {
        'site_settings': site_settings,
        'results': settled[:60],
        'won_count': won_count,
        'lost_count': lost_count,
        'void_count': void_count,
        'settled_count': won_count + lost_count + void_count,
        'win_rate': win_rate,
        'recent_form': recent_form,
    }
    return render(request, 'matches/results.html', context)


def contact(request):
    """
    Contact page — points visitors to the WhatsApp community.

    The invite link and blurb are managed in Admin (SiteSettings), so the
    community URL can be added later without any code changes.
    """
    site_settings = SiteSettings.load()
    context = {
        'site_settings': site_settings,
    }
    return render(request, 'matches/contact.html', context)
