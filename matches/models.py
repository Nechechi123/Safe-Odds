"""
Models for the matches app.

Quick explanation for learning Django:
- A "model" is a Python class that represents a database table.
- Each field (like CharField, DecimalField) becomes a column in the table.
- Django automatically creates the table and handles all the SQL for you.
- When you change a model, you run 'makemigrations' and 'migrate' to
  update the database.
"""

from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models


class Match(models.Model):
    """A single football match tip with odds and confidence level."""

    # --- Result choices ---
    PENDING = 'PENDING'
    WON = 'WON'
    LOST = 'LOST'
    VOID = 'VOID'
    RESULT_CHOICES = [
        (PENDING, 'Pending'),
        (WON, 'Won'),
        (LOST, 'Lost'),
        (VOID, 'Void'),
    ]

    league = models.CharField(max_length=100, help_text='e.g. Premier League')
    home_team = models.CharField(max_length=100)
    away_team = models.CharField(max_length=100)

    # Optional custom club logo image URLs (overrides default official crests)
    home_team_logo_url = models.URLField(
        blank=True,
        null=True,
        help_text='Optional: Direct image URL for the home club logo'
    )
    away_team_logo_url = models.URLField(
        blank=True,
        null=True,
        help_text='Optional: Direct image URL for the away club logo'
    )

    kickoff = models.DateTimeField(
        help_text='Match kickoff time (stored in UTC)'
    )
    tip = models.CharField(
        max_length=150,
        help_text='e.g. Over 1.5 Goals'
    )
    odds = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        validators=[MinValueValidator(1.01)],
        help_text='Decimal odds, e.g. 1.35'
    )
    confidence = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        help_text='0 to 100 — the site owner\'s confidence in this tip'
    )
    result = models.CharField(
        max_length=10,
        choices=RESULT_CHOICES,
        default=PENDING,
    )
    is_published = models.BooleanField(
        default=True,
        help_text='Uncheck to hide this match from the public page'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['kickoff']
        verbose_name_plural = 'matches'

    def __str__(self):
        return f'{self.home_team} vs {self.away_team}'

    @property
    def label(self):
        """
        Returns a confidence label based on the confidence percentage.
        - 75+ → SAFE (high confidence)
        - 50-74 → MODERATE
        - Below 50 → RISKY
        """
        if self.confidence >= 75:
            return 'SAFE'
        elif self.confidence >= 50:
            return 'MODERATE'
        return 'RISKY'


class SiteSettings(models.Model):
    """
    Global site & VIP settings editable by the administrator in Django Admin.
    Allows changing VIP pricing, perks, links, and social proof metrics without code changes.
    """
    site_title = models.CharField(max_length=100, default='SafeOdds')
    tagline = models.CharField(max_length=200, default="Money can finish, but odds can't finish")

    # VIP Membership Configuration
    vip_price = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        default=15.00,
        help_text='Monthly VIP subscription price'
    )
    vip_currency = models.CharField(max_length=10, default='$', help_text='e.g. $, ₦, £, €')
    vip_period = models.CharField(max_length=20, default='/month')
    vip_headline = models.CharField(max_length=150, default='VIP MEMBERSHIP')
    vip_subline = models.CharField(max_length=200, default='Unlock premium predictions & exclusive insights')
    vip_features = models.TextField(
        default='Daily 3-5 Safe Odds\n90% Accuracy\nWhatsApp Support\nBanker of the Day\nEarly Tips Access\nExclusive Analysis',
        help_text='Enter one feature perk per line'
    )
    vip_payment_or_whatsapp_url = models.URLField(
        blank=True,
        default='',
        help_text='Direct link for VIP purchase (WhatsApp link, Paystack, Flutterwave, or Stripe URL)'
    )
    vip_member_count = models.PositiveIntegerField(
        default=1500,
        help_text='Displayed VIP members count (e.g. 1500)'
    )

    # Stats / Social Proof overrides
    win_rate_override = models.PositiveSmallIntegerField(
        blank=True,
        null=True,
        help_text='Optional: Override win rate percentage (e.g. 85). If empty, calculates automatically from finished matches.'
    )
    active_users_label = models.CharField(
        max_length=50,
        default='1.2K',
        help_text='Social proof active users label (e.g. 1.2K, 5K+)'
    )
    total_predictions_override = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        help_text='Optional: Override total predictions label (e.g. 210+). If empty, calculates from database.'
    )

    class Meta:
        verbose_name = 'Site & VIP Settings'
        verbose_name_plural = 'Site & VIP Settings'

    def __str__(self):
        return f'{self.site_title} Settings'

    @classmethod
    def load(cls):
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj

    @property
    def vip_features_list(self):
        return [line.strip() for line in self.vip_features.splitlines() if line.strip()]
