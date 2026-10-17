"""
Analytics views: click tracking via a redirect endpoint and a JS beacon.
"""

from datetime import timedelta
from urllib.parse import urlparse

from django.conf import settings
from django.contrib.admin.views.decorators import staff_member_required
from django.db.models import Count
from django.db.models.functions import TruncDate
from django.http import HttpResponseBadRequest, HttpResponseRedirect, JsonResponse
from django.shortcuts import redirect, render
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from . import utils
from .models import ClickEvent, PageView


def _log_click(request, target, match_id=None):
    ua = request.META.get('HTTP_USER_AGENT', '')
    device, browser, is_bot = utils.parse_user_agent(ua)
    ref_path = urlparse(request.META.get('HTTP_REFERER', '')).path
    ClickEvent.objects.create(
        target=target[:50],
        path=ref_path[:255],
        match_id=match_id,
        visitor=utils.make_visitor_hash(utils.get_client_ip(request), ua),
        device=device,
        browser=browser,
        is_bot=is_bot,
    )


def _destination(slug):
    """Resolve a tracked link slug to its real destination URL (or None)."""
    from matches.models import SiteSettings

    if slug == 'sportybet':
        return getattr(settings, 'SPORTYBET_URL', 'https://www.sportybet.com')
    if slug == 'join_vip':
        return SiteSettings.load().vip_whatsapp_url
    if slug == 'whatsapp_community':
        return SiteSettings.load().whatsapp_community_url or None
    return None


def go(request, slug):
    """Log a click, then redirect the visitor to the destination."""
    destination = _destination(slug)
    _log_click(request, slug)
    if not destination:
        return redirect('matches:contact')
    return HttpResponseRedirect(destination)


@csrf_exempt
@require_POST
def track(request):
    """Receive in-page click events from navigator.sendBeacon()."""
    target = (request.POST.get('target') or '').strip()
    if not target:
        return HttpResponseBadRequest('missing target')

    match_id = request.POST.get('match_id') or None
    try:
        match_id = int(match_id) if match_id else None
    except (TypeError, ValueError):
        match_id = None

    _log_click(request, target, match_id)
    return JsonResponse({'ok': True})


@staff_member_required(login_url='/admin/login/')
def dashboard(request):
    """Staff-only dashboard with charts of views, visitors and clicks."""
    days = 30
    today = timezone.localdate()
    start = today - timedelta(days=days - 1)

    views_qs = PageView.objects.filter(is_bot=False, created_at__date__gte=start)
    clicks_qs = ClickEvent.objects.filter(is_bot=False, created_at__date__gte=start)

    # Daily views + unique visitors, filled in for days with no traffic.
    daily_rows = (
        views_qs.annotate(day=TruncDate('created_at'))
        .values('day')
        .annotate(views=Count('id'), visitors=Count('visitor', distinct=True))
    )
    daily_map = {row['day']: row for row in daily_rows}
    labels, views_series, visitors_series = [], [], []
    for offset in range(days):
        day = start + timedelta(days=offset)
        row = daily_map.get(day)
        labels.append(day.strftime('%b %d'))
        views_series.append(row['views'] if row else 0)
        visitors_series.append(row['visitors'] if row else 0)

    top_pages = list(views_qs.values('path').annotate(count=Count('id')).order_by('-count')[:8])
    click_targets = list(clicks_qs.values('target').annotate(count=Count('id')).order_by('-count'))
    devices = list(views_qs.values('device').annotate(count=Count('id')).order_by('-count'))
    referrers = list(
        views_qs.exclude(referrer_host='')
        .values('referrer_host')
        .annotate(count=Count('id'))
        .order_by('-count')[:8]
    )

    chart_data = {
        'labels': labels,
        'views': views_series,
        'visitors': visitors_series,
        'pages': {
            'labels': [p['path'] for p in top_pages],
            'values': [p['count'] for p in top_pages],
        },
        'clicks': {
            'labels': [c['target'] for c in click_targets],
            'values': [c['count'] for c in click_targets],
        },
        'devices': {
            'labels': [d['device'] or 'unknown' for d in devices],
            'values': [d['count'] for d in devices],
        },
    }

    context = {
        'days': days,
        'total_views': views_qs.count(),
        'total_visitors': views_qs.values('visitor').distinct().count(),
        'total_clicks': clicks_qs.count(),
        'top_pages': top_pages,
        'referrers': referrers,
        'chart_data': chart_data,
    }
    return render(request, 'analytics/dashboard.html', context)
