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
from django.db.models import Q
from django.utils import timezone


class MatchQuerySet(models.QuerySet):
    """Helpers for the public visibility rules of a match."""

    def visible(self, now=None):
        """
        Matches a visitor is allowed to see:
        published, and either unscheduled or scheduled to publish by 'now'.
        """
        now = now or timezone.now()
        return self.filter(is_published=True).filter(
            Q(publish_at__isnull=True) | Q(publish_at__lte=now)
        )


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
    sportybet_pick_ids = models.CharField(
        max_length=255,
        blank=True,
        default='',
        help_text='Optional. Comma-separated SportyBet pick IDs for this tip (e.g. 1.27166). '
                  'Lets the Place Slip button auto-fill the betslip on SportyBet. '
                  'Leave blank to just open SportyBet normally.'
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
    publish_at = models.DateTimeField(
        blank=True,
        null=True,
        help_text='Optional: hold this match back until this date/time. '
                  'Leave blank to make it visible immediately.'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    objects = MatchQuerySet.as_manager()

    class Meta:
        ordering = ['kickoff']
        verbose_name_plural = 'matches'

    def __str__(self):
        return f'{self.home_team} vs {self.away_team}'

    @property
    def is_scheduled(self):
        """True when the match is being held back for a future publish time."""
        return bool(self.publish_at and self.publish_at > timezone.now())

    @property
    def sportybet_ids_clean(self):
        """Whitespace-stripped, list or [] — SportyBet pick IDs for deep links."""
        if not self.sportybet_pick_ids:
            return []
        return [p.strip() for p in self.sportybet_pick_ids.split(',') if p.strip()]

    @property
    def sportybet_ids_string(self):
        """Comma-joined pick IDs, ready for a SportyBet deep link ('' if none)."""
        return ','.join(self.sportybet_ids_clean)

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

    # Optional second currency (e.g. Naira) — shows a $/₦ toggle on the card.
    vip_currency_2 = models.CharField(
        max_length=10,
        blank=True,
        default='₦',
        help_text='Second currency symbol, e.g. ₦. Leave blank to hide the currency toggle.'
    )
    vip_price_2 = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True,
        help_text='Price in the second currency. Leave blank to hide the currency toggle.'
    )
    vip_headline = models.CharField(max_length=150, default='VIP MEMBERSHIP')
    vip_subline = models.CharField(max_length=200, default='Unlock premium predictions & exclusive insights')
    vip_features = models.TextField(
        default='Daily 3-5 Safe Odds\n90% Accuracy\nWhatsApp Support\nBanker of the Day\nEarly Tips Access',
        help_text='Enter one feature perk per line'
    )
    whatsapp_number = models.CharField(
        max_length=30,
        blank=True,
        default='',
        help_text="Your WhatsApp phone number with country code (e.g. 2348012345678 or 15551234567, no + or spaces)"
    )
    whatsapp_vip_message = models.CharField(
        max_length=255,
        default="Hello SafeOdds! I want to join the VIP club for $15/month.",
        help_text="Message pre-filled in WhatsApp when visitor clicks Join VIP"
    )

    # Contact page — WhatsApp community
    whatsapp_community_url = models.URLField(
        blank=True,
        default='',
        help_text="Invite link for your WhatsApp community/group. Leave blank until you have it."
    )
    whatsapp_community_note = models.CharField(
        max_length=255,
        default='Join our free WhatsApp community for daily tips, match alerts and updates.',
        help_text='Short description shown on the Contact page'
    )
    vip_payment_or_whatsapp_url = models.URLField(
        blank=True,
        default='',
        help_text='Optional fallback URL if not using standard WhatsApp number'
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

    @property
    def has_secondary_currency(self):
        """True when a second currency/price is configured for the VIP toggle."""
        return bool(self.vip_currency_2 and self.vip_price_2)

    @property
    def vip_price_display(self):
        """Primary price with thousands separators, e.g. 15 or 1,500."""
        return f"{int(self.vip_price):,}"

    @property
    def vip_price_2_display(self):
        """Second price with thousands separators, e.g. 20,000. Empty if unset."""
        return f"{int(self.vip_price_2):,}" if self.vip_price_2 is not None else ''

    @property
    def vip_whatsapp_url(self):
        """Constructs a direct WhatsApp chat link with the pre-filled message."""
        import urllib.parse
        clean_num = ''.join(filter(str.isdigit, self.whatsapp_number or ''))
        # Generate message with current price if default
        msg = self.whatsapp_vip_message or f"Hello {self.site_title}! I want to join the VIP club."
        encoded_msg = urllib.parse.quote(msg)
        if clean_num:
            return f"https://wa.me/{clean_num}?text={encoded_msg}"
        elif self.vip_payment_or_whatsapp_url:
            return self.vip_payment_or_whatsapp_url
        return f"https://wa.me/?text={encoded_msg}"
