"""Tests for the privacy-first analytics capture."""

from django.contrib.auth import get_user_model
from django.test import Client, TestCase

from .models import ClickEvent, PageView


class TrackingTests(TestCase):
    def setUp(self):
        # SERVER_NAME='localhost' matches the project's ALLOWED_HOSTS in tests.
        self.client = Client(SERVER_NAME='localhost')

    def test_page_view_recorded(self):
        self.client.get('/')
        self.assertTrue(PageView.objects.filter(path='/').exists())

    def test_admin_is_not_recorded(self):
        before = PageView.objects.count()
        self.client.get('/admin/login/')
        self.assertEqual(PageView.objects.count(), before)

    def test_static_like_paths_are_not_recorded(self):
        before = PageView.objects.count()
        self.client.get('/api/track/')  # not a page view, and skipped prefix
        self.assertEqual(PageView.objects.count(), before)

    def test_go_redirect_logs_click_and_redirects(self):
        response = self.client.get('/go/sportybet/')
        self.assertEqual(response.status_code, 302)
        self.assertTrue(ClickEvent.objects.filter(target='sportybet').exists())

    def test_go_sportybet_forwards_valid_ids(self):
        response = self.client.get('/go/sportybet/', {'ids': '1.27166,1.27167'})
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response['Location'].endswith('ids=1.27166%2C1.27167'))

    def test_go_sportybet_rejects_invalid_ids(self):
        response = self.client.get('/go/sportybet/', {'ids': 'evil<script>'})
        self.assertEqual(response.status_code, 302)
        self.assertNotIn('evil', response['Location'])

    def test_beacon_logs_click(self):
        response = self.client.post('/api/track/', {'target': 'add_to_slip', 'match_id': '5'})
        self.assertEqual(response.status_code, 200)
        self.assertTrue(ClickEvent.objects.filter(target='add_to_slip', match_id=5).exists())

    def test_beacon_without_target_is_rejected(self):
        response = self.client.post('/api/track/', {})
        self.assertEqual(response.status_code, 400)

    def test_bot_is_flagged(self):
        self.client.get('/', HTTP_USER_AGENT='Googlebot/2.1 (+http://www.google.com/bot.html)')
        self.assertTrue(PageView.objects.filter(path='/', is_bot=True).exists())

    def test_visitor_hash_is_anonymous(self):
        self.client.get('/')
        view = PageView.objects.get(path='/')
        self.assertEqual(len(view.visitor), 40)
        self.assertNotIn('127.0.0.1', view.visitor)


class DashboardTests(TestCase):
    def setUp(self):
        self.client = Client(SERVER_NAME='localhost')

    def test_anonymous_is_redirected(self):
        response = self.client.get('/staff/analytics/')
        self.assertEqual(response.status_code, 302)

    def test_non_staff_is_redirected(self):
        get_user_model().objects.create_user(username='joe', password='pw')
        self.client.login(username='joe', password='pw')
        self.assertEqual(self.client.get('/staff/analytics/').status_code, 302)

    def test_staff_can_view_dashboard(self):
        get_user_model().objects.create_user(username='admin', password='pw', is_staff=True)
        self.client.login(username='admin', password='pw')
        response = self.client.get('/staff/analytics/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Site Analytics')
