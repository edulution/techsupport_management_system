from django.test import TestCase
from django.urls import reverse
from techsupport.models import SupportTicket, User, Category, SubCategory, Centre
from uuid import uuid4
import json
from django.utils import timezone
from techsupport.views import (
    user_login,
    user_logout,
    dashboard,
    ticket_details,
    create_ticket,
    get_subcategories,
)


class ViewsTestCase(TestCase):
    
    @classmethod
    def setUpTestData(cls):
        # Create a test user
        cls.user = User.objects.create_user(username="admin", password="admin123")

    def setUp(self):
        # Log in the test user for each test
        self.client.login(username="admin", password="admin123")

    def test_user_login_view(self):
        response = self.client.post(reverse("login"), {"username": "admin", "password": "admin123"})
        self.assertRedirects(response, reverse("dashboard"))

    def test_user_logout_view(self):
        response = self.client.get(reverse("logout"))
        self.assertEqual(response.status_code, 200)

    def test_dashboard_view(self):
        response = self.client.get(reverse("dashboard"))
        self.assertEqual(response.status_code, 200)

    def test_create_ticket_view(self):
        response = self.client.get(reverse("create_ticket"))
        self.assertEqual(response.status_code, 200)

        

