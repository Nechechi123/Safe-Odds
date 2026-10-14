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
