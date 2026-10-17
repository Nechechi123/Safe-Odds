from datetime import datetime, timedelta
from decimal import Decimal
from zoneinfo import ZoneInfo

from django.test import TestCase, Client
from django.utils import timezone

from .models import Match
from .templatetags.match_extras import to_wat, to_est


class MatchModelTest(TestCase):
    def setUp(self):
        self.now = timezone.now()

    def test_match_str(self):
        match = Match.objects.create(
            league="Premier League",
            home_team="Arsenal",
            away_team="Chelsea",
            kickoff=self.now + timedelta(days=1),
            tip="Over 1.5 Goals",
            odds=Decimal("1.35"),
            confidence=85,
        )
        self.assertEqual(str(match), "Arsenal vs Chelsea")

    def test_confidence_labels(self):
        # >= 75 -> SAFE
        safe_match = Match(confidence=80)
        self.assertEqual(safe_match.label, "SAFE")

        # 50 to 74 -> MODERATE
        moderate_match = Match(confidence=60)
        self.assertEqual(moderate_match.label, "MODERATE")

        # < 50 -> RISKY
        risky_match = Match(confidence=40)
        self.assertEqual(risky_match.label, "RISKY")


class MatchViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.now = timezone.now()

        # Published future match
        self.published_future = Match.objects.create(
            league="Premier League",
            home_team="Liverpool",
            away_team="Man City",
            kickoff=self.now + timedelta(days=1),
            tip="Home Win",
            odds=Decimal("1.80"),
            confidence=75,
            is_published=True,
        )

        # Unpublished match (should NOT appear on public page)
        self.unpublished = Match.objects.create(
            league="La Liga",
            home_team="Barcelona",
            away_team="Sevilla",
            kickoff=self.now + timedelta(days=1),
            tip="Over 2.5",
            odds=Decimal("1.50"),
            confidence=70,
            is_published=False,
        )

    def test_homepage_shows_published_matches_only(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Liverpool vs Man City")
        self.assertNotContains(response, "Barcelona vs Sevilla")


class ScheduledPublishTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.now = timezone.now()

    def _make(self, home, **kwargs):
        defaults = dict(
            league="Test League",
            away_team="Away FC",
            kickoff=self.now + timedelta(days=1),
            tip="Home Win",
            odds=Decimal("1.50"),
            confidence=80,
        )
        defaults.update(kwargs)
        return Match.objects.create(home_team=home, **defaults)

    def test_future_scheduled_match_hidden(self):
        self._make("FutureHold", publish_at=self.now + timedelta(hours=2))
        response = self.client.get("/")
        self.assertNotContains(response, "FutureHold vs Away FC")

    def test_past_scheduled_match_visible(self):
        self._make("PastRelease", publish_at=self.now - timedelta(hours=2))
        response = self.client.get("/")
        self.assertContains(response, "PastRelease vs Away FC")

    def test_visible_queryset_excludes_scheduled(self):
        scheduled = self._make("SchedOne", publish_at=self.now + timedelta(hours=2))
        live = self._make("LiveOne")
        visible = Match.objects.visible()
        self.assertIn(live, visible)
        self.assertNotIn(scheduled, visible)


class TimezoneFiltersTest(TestCase):
    def test_to_wat_and_to_est(self):
        # 2026-10-15 12:00:00 UTC
        utc_time = datetime(2026, 10, 15, 12, 0, 0, tzinfo=ZoneInfo("UTC"))

        # In WAT (UTC+1), this is 1:00 PM
        wat_str = to_wat(utc_time)
        self.assertIn("01:00 PM", wat_str)

        # In EST/EDT (America/New_York is EDT in October, UTC-4), this is 08:00 AM
        est_str = to_est(utc_time)
        self.assertIn("08:00 AM", est_str)
