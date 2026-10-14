"""
Custom template filters for the matches app.

Quick explanation for learning Django:
- Template filters let you transform data right inside your HTML templates.
- We use these to convert UTC times to WAT (West Africa Time),
  EST (Eastern Standard Time), and GMT for display.
- Also provides helper functions for countdowns and team badges.
"""

from datetime import datetime, timezone as dt_timezone
from zoneinfo import ZoneInfo

from django import template
from django.utils import timezone
from django.utils.safestring import mark_safe

register = template.Library()


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


@register.filter
def team_badge(team_name):
    """
    Renders a stylized SVG crest with realistic colors and branding
    for popular football clubs, or a sleek fallback shield.
    """
    name = (team_name or '').strip().lower()

    # Pre-defined club crest colors & glyphs
    clubs = {
        'arsenal': {'bg': '#DB0007', 'border': '#9C824A', 'initials': 'AFC', 'icon': 'cannon'},
        'chelsea': {'bg': '#034694', 'border': '#DBA111', 'initials': 'CFC', 'icon': 'lion'},
        'barcelona': {'bg': '#A50044', 'border': '#004D98', 'initials': 'FCB', 'icon': 'stripes'},
        'real madrid': {'bg': '#FFFFFF', 'border': '#FEBE10', 'initials': 'RMCF', 'icon': 'crown', 'text': '#00529F'},
        'bayern munich': {'bg': '#DC052D', 'border': '#0066B2', 'initials': 'FCB', 'icon': 'diamonds'},
        'bayern': {'bg': '#DC052D', 'border': '#0066B2', 'initials': 'FCB', 'icon': 'diamonds'},
        'dortmund': {'bg': '#FDE100', 'border': '#000000', 'initials': 'BVB', 'icon': 'bvb', 'text': '#000'},
        'liverpool': {'bg': '#C8102E', 'border': '#00B2A9', 'initials': 'LFC', 'icon': 'bird'},
        'manchester city': {'bg': '#6CABDD', 'border': '#1C2C5B', 'initials': 'MCFC', 'icon': 'ship'},
        'man city': {'bg': '#6CABDD', 'border': '#1C2C5B', 'initials': 'MCFC', 'icon': 'ship'},
        'manchester united': {'bg': '#DA291C', 'border': '#FBE122', 'initials': 'MUFC', 'icon': 'devil'},
        'man utd': {'bg': '#DA291C', 'border': '#FBE122', 'initials': 'MUFC', 'icon': 'devil'},
    }

    info = clubs.get(name, {
        'bg': '#1e293b',
        'border': '#22c55e',
        'initials': ''.join([w[0] for w in team_name.split()[:2]]).upper() or 'FC',
        'text': '#ffffff'
    })

    text_color = info.get('text', '#ffffff')
    initials = info.get('initials', 'FC')

    svg = f'''
    <svg class="team-crest-svg" viewBox="0 0 48 48" width="46" height="46" fill="none" xmlns="http://www.w3.org/2000/svg">
        <defs>
            <filter id="glow-{abs(hash(team_name)) % 1000}" x="-20%" y="-20%" width="140%" height="140%">
                <feDropShadow dx="0" dy="2" stdDeviation="3" flood-color="{info['border']}" flood-opacity="0.35"/>
            </filter>
        </defs>
        <path d="M24 3L40 7V22C40 33 24 43 24 43C24 43 8 33 8 22V7L24 3Z"
              fill="{info['bg']}" stroke="{info['border']}" stroke-width="2"
              filter="url(#glow-{abs(hash(team_name)) % 1000})"/>
        <path d="M24 6L37 9.5V21C37 30 24 38 24 38C24 38 11 30 11 21V9.5L24 6Z"
              fill="rgba(255,255,255,0.06)"/>
        <text x="24" y="27" font-family="-apple-system, system-ui, sans-serif" font-size="11" font-weight="900"
              fill="{text_color}" text-anchor="middle" letter-spacing="-0.5">{initials}</text>
    </svg>
    '''
    return mark_safe(svg)
