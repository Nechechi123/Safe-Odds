"""
Analytics models — lightweight, first-party, privacy-first.

We store anonymous page views and click events. Visitors are identified only
by a daily-salted hash (see analytics.utils.make_visitor_hash); no cookies,
no raw IP addresses, and no personal data are stored.
"""

from django.db import models
from django.utils import timezone


class VisitorEvent(models.Model):
    """Common fields shared by page views and click events."""

    created_at = models.DateTimeField(default=timezone.now, db_index=True)
    visitor = models.CharField(
        max_length=64, db_index=True,
        help_text='Anonymous, daily-salted visitor hash (no personal data).'
    )
    device = models.CharField(max_length=20, blank=True, default='')
    browser = models.CharField(max_length=30, blank=True, default='')
    is_bot = models.BooleanField(default=False)

    class Meta:
        abstract = True
        ordering = ('-created_at',)


class PageView(VisitorEvent):
    """A single page view on a public part of the site."""

    path = models.CharField(max_length=255, db_index=True)
    route_name = models.CharField(max_length=100, blank=True, default='')
    referrer_host = models.CharField(max_length=255, blank=True, default='')

    class Meta(VisitorEvent.Meta):
        verbose_name = 'page view'
        verbose_name_plural = 'page views'

    def __str__(self):
        return f'{self.path} @ {self.created_at:%Y-%m-%d %H:%M}'


class ClickEvent(VisitorEvent):
    """A click on a tracked call-to-action (bet, join VIP, WhatsApp, etc.)."""

    target = models.CharField(max_length=50, db_index=True)
    path = models.CharField(max_length=255, blank=True, default='')
    match_id = models.PositiveIntegerField(null=True, blank=True)

    class Meta(VisitorEvent.Meta):
        verbose_name = 'click event'
        verbose_name_plural = 'click events'

    def __str__(self):
        return f'{self.target} @ {self.created_at:%Y-%m-%d %H:%M}'
