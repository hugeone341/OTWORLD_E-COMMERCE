from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from traders.models import TraderProfile


class TraderRegistrationTests(TestCase):
    def test_registration_page_loads(self):
        response = self.client.get(reverse("accounts:register"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Trader registration")

    def test_valid_registration_creates_unverified_trader(self):
        response = self.client.post(
            reverse("accounts:register"),
            {
                "username": "newtrader",
                "email": "trader@example.com",
                "password1": "A-safe-test-password-128",
                "password2": "A-safe-test-password-128",
                "business_name": "New Trader Business",
                "phone": "+260 977 123456",
            },
        )

        self.assertRedirects(
            response, reverse("accounts:registration_complete")
        )
        user = get_user_model().objects.get(username="newtrader")
        profile = TraderProfile.objects.get(user=user)
        self.assertEqual(profile.business_name, "New Trader Business")
        self.assertEqual(profile.phone, "+260 977 123456")
        self.assertEqual(profile.whatsapp_number, "")
        self.assertEqual(profile.plot_number, "")
        self.assertFalse(profile.is_verified)

    def test_registration_saves_optional_plot_number_and_whatsapp(self):
        response = self.client.post(
            reverse("accounts:register"),
            {
                "username": "shopowner",
                "email": "shop@example.com",
                "password1": "A-safe-test-password-128",
                "password2": "A-safe-test-password-128",
                "business_name": "Shop Owner",
                "phone": "+260 977 123456",
                "whatsapp_number": "+260 966 123456",
                "plot_number": "Plot 42",
            },
        )

        self.assertRedirects(
            response, reverse("accounts:registration_complete")
        )
        profile = TraderProfile.objects.get(user__username="shopowner")
        self.assertEqual(profile.whatsapp_number, "+260 966 123456")
        self.assertEqual(profile.plot_number, "Plot 42")

    def test_registration_saves_business_pin(self):
        response = self.client.post(
            reverse("accounts:register"),
            {
                "username": "pinnedshop",
                "email": "pinned@example.com",
                "password1": "A-safe-test-password-128",
                "password2": "A-safe-test-password-128",
                "business_name": "Pinned Shop",
                "phone": "+260 977 123456",
                "latitude": "-15.416700",
                "longitude": "28.283300",
            },
        )

        self.assertRedirects(
            response, reverse("accounts:registration_complete")
        )
        profile = TraderProfile.objects.get(user__username="pinnedshop")
        self.assertEqual(str(profile.latitude), "-15.416700")
        self.assertEqual(str(profile.longitude), "28.283300")

    def test_registration_rejects_incomplete_business_pin(self):
        response = self.client.post(
            reverse("accounts:register"),
            {
                "username": "incompletepin",
                "email": "pin@example.com",
                "password1": "A-safe-test-password-128",
                "password2": "A-safe-test-password-128",
                "business_name": "Pinned Shop",
                "phone": "+260 977 123456",
                "latitude": "-15.416700",
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context["form"].non_field_errors())
        self.assertFalse(
            get_user_model().objects.filter(username="incompletepin").exists()
        )

    def test_invalid_registration_does_not_create_user(self):
        response = self.client.post(
            reverse("accounts:register"),
            {
                "username": "newtrader",
                "email": "trader@example.com",
                "password1": "first-password",
                "password2": "different-password",
                "business_name": "New Trader Business",
                "phone": "+260 977 123456",
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context["form"].errors)
        self.assertFalse(
            get_user_model().objects.filter(username="newtrader").exists()
        )
