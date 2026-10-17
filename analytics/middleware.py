"""
Middleware that records anonymous page views.

It runs after AuthenticationMiddleware so it can skip logged-in staff, and it
never lets a tracking error break a real request.
"""

from django.urls import Resolver404, resolve

from . import utils
from .models import PageView

SKIP_PREFIXES = ('/admin/', '/static/', '/media/', '/go/', '/api/')


class AnalyticsMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        try:
            self._record(request, response)
        except Exception:
            # Analytics must never interfere with serving the site.
            pass
        return response

    def _record(self, request, response):
        if request.method != 'GET' or response.status_code != 200:
            return
        if request.path.startswith(SKIP_PREFIXES):
            return
        if 'text/html' not in response.get('Content-Type', ''):
            return

        user = getattr(request, 'user', None)
        if user is not None and user.is_authenticated:
            return

        ua = request.META.get('HTTP_USER_AGENT', '')
        device, browser, is_bot = utils.parse_user_agent(ua)

        try:
            route_name = resolve(request.path).url_name or ''
        except Resolver404:
            route_name = ''

        PageView.objects.create(
            path=request.path[:255],
            route_name=route_name[:100],
            referrer_host=utils.referrer_host(request)[:255],
            visitor=utils.make_visitor_hash(utils.get_client_ip(request), ua),
            device=device,
            browser=browser,
            is_bot=is_bot,
        )
