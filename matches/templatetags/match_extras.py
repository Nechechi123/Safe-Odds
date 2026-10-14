"""
Custom template filters for the matches app.

Quick explanation for learning Django:
- Template filters let you transform data right inside your HTML templates.
- We use these to convert UTC times to WAT (West Africa Time) and
  EST (Eastern Standard Time) for display.
- In a template you use them like: {{ match.kickoff|to_wat }}
"""

from datetime import timezone as dt_timezone
from zoneinfo import ZoneInfo

from django import template

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
