"""
Custom template filters for the matches app.

Quick explanation for learning Django:
- Template filters let you transform data right inside your HTML templates.
- We use these to convert UTC times to WAT, EST, and GMT for display.
- Also provides helper functions for official club logos and countdowns.
"""

from datetime import datetime, timezone as dt_timezone
from zoneinfo import ZoneInfo

from django import template
from django.utils import timezone
from django.utils.safestring import mark_safe

register = template.Library()

# CDN URLs for official club crests (transparent PNGs from verified football data CDNs)
OFFICIAL_CLUB_LOGOS = {
    'arsenal': 'https://media.api-sports.io/football/teams/42.png',
    'chelsea': 'https://media.api-sports.io/football/teams/49.png',
    'liverpool': 'https://media.api-sports.io/football/teams/40.png',
    'manchester city': 'https://media.api-sports.io/football/teams/50.png',
    'man city': 'https://media.api-sports.io/football/teams/50.png',
    'manchester united': 'https://media.api-sports.io/football/teams/33.png',
    'man utd': 'https://media.api-sports.io/football/teams/33.png',
    'tottenham': 'https://media.api-sports.io/football/teams/47.png',
    'spurs': 'https://media.api-sports.io/football/teams/47.png',
    'aston villa': 'https://media.api-sports.io/football/teams/66.png',
    'newcastle': 'https://media.api-sports.io/football/teams/34.png',
    'barcelona': 'https://media.api-sports.io/football/teams/529.png',
    'real madrid': 'https://media.api-sports.io/football/teams/541.png',
    'atletico madrid': 'https://media.api-sports.io/football/teams/530.png',
    'bayern munich': 'https://media.api-sports.io/football/teams/157.png',
    'bayern': 'https://media.api-sports.io/football/teams/157.png',
    'dortmund': 'https://media.api-sports.io/football/teams/165.png',
    'borussia dortmund': 'https://media.api-sports.io/football/teams/165.png',
    'bayer leverkusen': 'https://media.api-sports.io/football/teams/168.png',
    'leverkusen': 'https://media.api-sports.io/football/teams/168.png',
    'paris saint-germain': 'https://media.api-sports.io/football/teams/85.png',
    'psg': 'https://media.api-sports.io/football/teams/85.png',
    'juventus': 'https://media.api-sports.io/football/teams/496.png',
    'inter milan': 'https://media.api-sports.io/football/teams/505.png',
    'inter': 'https://media.api-sports.io/football/teams/505.png',
    'ac milan': 'https://media.api-sports.io/football/teams/489.png',
    'milan': 'https://media.api-sports.io/football/teams/489.png',
    'napoli': 'https://media.api-sports.io/football/teams/492.png',
}


@register.filter
def to_wat(value):
    """Convert a datetime to West Africa Time (Africa/Lagos, UTC+1)."""
    if value is None:
        return ''
    wat = value.astimezone(ZoneInfo('Africa/Lagos'))
    return wat.strftime('%b %d, %I:%M %p')


@register.filter
def to_est(value):
    """Convert a datetime to Eastern Time (America/New_York)."""
    if value is None:
        return ''
    est = value.astimezone(ZoneInfo('America/New_York'))
    return est.strftime('%b %d, %I:%M %p')


@register.filter
def to_gmt(value):
    """Format datetime as 'HH:MM GMT'."""
    if value is None:
        return ''
    return value.strftime('%H:%M GMT')


@register.filter
def countdown(value):
    """Returns 'Live in Xh Ym' or 'Live now' relative to current time."""
    if value is None:
        return 'Upcoming'
    now = timezone.now()
    diff = value - now
    if diff.total_seconds() <= 0:
        return 'Live now'
    hours = int(diff.total_seconds() // 3600)
    minutes = int((diff.total_seconds() % 3600) // 60)
    if hours > 24:
        days = hours // 24
        return f'In {days}d {hours % 24}h'
    if hours > 0:
        return f'Live in {hours}h {minutes}m'
    return f'Live in {minutes}m'


@register.simple_tag
def club_crest(team_name, custom_url=None):
    """
    Renders the official club logo:
    1. If custom_url was entered by the admin, use it.
    2. Else if team is in OFFICIAL_CLUB_LOGOS, use verified transparent PNG.
    3. Else fallback to clean SVG shield.
    """
    name_clean = (team_name or '').strip().lower()
    img_url = custom_url or OFFICIAL_CLUB_LOGOS.get(name_clean)

    if img_url:
        return mark_safe(f'''
            <div class="crest-img-wrapper">
                <img src="{img_url}" alt="{team_name}" class="team-crest-img" loading="lazy"
                     onerror="this.style.display='none'; this.nextElementSibling.style.display='block';">
                <div class="crest-fallback" style="display:none;">
                    {_render_svg_shield(team_name)}
                </div>
            </div>
        ''')

    return mark_safe(_render_svg_shield(team_name))


@register.filter
def team_badge(team_name):
    """Convenience filter for templates without a custom url."""
    return club_crest(team_name)


def _render_svg_shield(team_name):
    """Fallback stylized SVG shield with initials."""
    initials = ''.join([w[0] for w in (team_name or 'FC').split()[:2]]).upper() or 'FC'
    return f'''
    <svg class="team-crest-svg" viewBox="0 0 48 48" width="46" height="46" fill="none" xmlns="http://www.w3.org/2000/svg">
        <path d="M24 3L40 7V22C40 33 24 43 24 43C24 43 8 33 8 22V7L24 3Z"
              fill="#101c2b" stroke="#22c55e" stroke-width="2"/>
        <text x="24" y="27" font-family="-apple-system, system-ui, sans-serif" font-size="11" font-weight="900"
              fill="#ffffff" text-anchor="middle" letter-spacing="-0.5">{initials}</text>
    </svg>
    '''
