"""
Helpers for privacy-first analytics: client IP, anonymous visitor hashing,
and a lightweight (dependency-free) user-agent parser.
"""

import hashlib
import re

from django.conf import settings
from django.utils import timezone


def get_client_ip(request):
    """Return the visitor's IP, honouring a proxy's X-Forwarded-For header."""
    forwarded = request.META.get('HTTP_X_FORWARDED_FOR', '')
    if forwarded:
        return forwarded.split(',')[0].strip()
    return request.META.get('REMOTE_ADDR', '')


def _truncate_ip(ip):
    """Drop the last IPv4 octet (or the last IPv6 groups) to reduce precision."""
    if not ip:
        return ''
    if ':' in ip:  # IPv6
        return ':'.join(ip.split(':')[:4])
    parts = ip.split('.')
    if len(parts) == 4:
        return '.'.join(parts[:3])
    return ip


def make_visitor_hash(ip, user_agent, day=None):
    """
    Build an anonymous visitor identifier.

    The salt rotates daily (derived from SECRET_KEY + the date) so the same
    visitor cannot be linked across different days. Only the resulting hash is
    ever stored — never the IP or the raw user-agent.
    """
    day = day or timezone.localdate().isoformat()
    salt = hashlib.sha256(f'{settings.SECRET_KEY}:{day}'.encode()).hexdigest()
    raw = f'{_truncate_ip(ip)}|{user_agent or ""}|{salt}'
    return hashlib.sha256(raw.encode()).hexdigest()[:40]


_BOT_RE = re.compile(
    r'bot|crawl|spider|slurp|bingpreview|facebookexternalhit|whatsapp|'
    r'telegrambot|preview|monitoring|uptime|curl|wget|python-requests|httpclient',
    re.IGNORECASE,
)


def parse_user_agent(user_agent):
    """Return (device, browser, is_bot) from a User-Agent string, without deps."""
    ua = user_agent or ''
    low = ua.lower()

    is_bot = bool(_BOT_RE.search(low))

    if 'ipad' in low or ('android' in low and 'mobile' not in low):
        device = 'tablet'
    elif 'mobi' in low or 'iphone' in low or 'ipod' in low or 'windows phone' in low:
        device = 'mobile'
    else:
        device = 'desktop'

    if 'edg' in low or 'edge' in low:
        browser = 'Edge'
    elif 'opr' in low or 'opera' in low:
        browser = 'Opera'
    elif 'chrome' in low and 'chromium' not in low:
        browser = 'Chrome'
    elif 'firefox' in low:
        browser = 'Firefox'
    elif 'safari' in low:
        browser = 'Safari'
    elif is_bot:
        browser = 'Bot'
    else:
        browser = 'Other'

    return device, browser, is_bot


def referrer_host(request):
    """Return just the hostname of the referring page (or '' if same/absent)."""
    from urllib.parse import urlparse

    ref = request.META.get('HTTP_REFERER', '')
    if not ref:
        return ''
    host = urlparse(ref).hostname or ''
    return host if host != request.get_host() else ''
