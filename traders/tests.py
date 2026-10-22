from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from .models import TraderProfile


class TraderAccountTests(TestCase):
    def setUp(self):
        self.password = "Safe-Test-Password-218!"
        self.user = get_user_model().objects.create_user(
            username="verifiedtrader",
            password=self.password,
        )
        self.profile = TraderProfile.objects.create(
            user=self.user,
            business_name="Verified Shop",
            phone="+260 977 123456",
            whatsapp_number="+260 966 123456",
            plot_number="Plot 42",
            province="Lusaka",
            latitude="-15.416700",
            longitude="28.283300",
            is_verified=True,
        )

    def test_login_page_loads(self):
        response = self.client.get(reverse("trader_login"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Trader sign in")
        self.assertContains(response, reverse("accounts:register"))

    def test_verified_trader_can_sign_in_and_view_dashboard(self):
        response = self.client.post(
            reverse("trader_login"),
            {"username": self.user.username, "password": self.password},
        )

        self.assertRedirects(response, reverse("trader_dashboard"))
        response = self.client.get(reverse("trader_dashboard"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Verified Shop")
        self.assertContains(response, "Plot 42")

    def test_unverified_trader_cannot_sign_in(self):
        self.profile.is_verified = False
        self.profile.save()

        response = self.client.post(
            reverse("trader_login"),
            {"username": self.user.username, "password": self.password},
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "awaiting verification")
        self.assertNotIn("_auth_user_id", self.client.session)

    def test_dashboard_redirects_anonymous_visitors_to_trader_login(self):
        response = self.client.get(reverse("trader_dashboard"))

        self.assertRedirects(
            response,
            f"{reverse('trader_login')}?next={reverse('trader_dashboard')}",
        )

    def test_trader_can_sign_out_with_post(self):
        self.client.force_login(self.user)

        response = self.client.post(reverse("trader_logout"))

        self.assertRedirects(response, reverse("trader_login"))
        self.assertNotIn("_auth_user_id", self.client.session)

    def test_sign_out_rejects_get_requests(self):
        self.client.force_login(self.user)

        response = self.client.get(reverse("trader_logout"))

        self.assertEqual(response.status_code, 405)
