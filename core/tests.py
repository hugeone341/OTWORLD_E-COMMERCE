from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from traders.models import TraderProfile


class TraderDirectionsTests(TestCase):
    def setUp(self):
        self.trader = TraderProfile.objects.create(
            user=get_user_model().objects.create_user(
                username="verifiedtrader",
                password="safe-test-password",
            ),
            business_name="Verified Shop",
            phone="+260 977 123456",
            province="Lusaka",
            plot_number="Plot 42",
            latitude="-15.416700",
            longitude="28.283300",
            is_verified=True,
        )

    def test_verified_trader_directions_page_loads(self):
        response = self.client.get(
            reverse(
                "core:trader_directions",
                kwargs={"trader_id": self.trader.pk},
            )
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Verified Shop")
        self.assertContains(response, "Plot 42")
        self.assertContains(response, "Your current location")

    def test_directions_page_is_unavailable_without_verification(self):
        self.trader.is_verified = False
        self.trader.save()

        response = self.client.get(
            reverse(
                "core:trader_directions",
                kwargs={"trader_id": self.trader.pk},
            )
        )

        self.assertEqual(response.status_code, 404)

    def test_directions_page_is_unavailable_without_map_pin(self):
        self.trader.latitude = None
        self.trader.longitude = None
        self.trader.save()

        response = self.client.get(
            reverse(
                "core:trader_directions",
                kwargs={"trader_id": self.trader.pk},
            )
        )

        self.assertEqual(response.status_code, 404)

    def test_home_page_shows_directions_for_verified_traders(self):
        response = self.client.get(reverse("core:home"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Verified Shop")
        self.assertContains(
            response,
            reverse(
                "core:trader_directions",
                kwargs={"trader_id": self.trader.pk},
            ),
        )
        self.assertContains(response, "Map &amp; directions")
        self.assertEqual(
            response.context["map_locations"],
            [
                {
                    "name": "Verified Shop",
                    "address": "Plot 42, Lusaka",
                    "latitude": -15.4167,
                    "longitude": 28.2833,
                    "url": reverse(
                        "core:trader_directions",
                        kwargs={"trader_id": self.trader.pk},
                    ),
                }
            ],
        )

    def test_home_map_only_includes_verified_traders_with_coordinates(self):
        TraderProfile.objects.create(
            user=get_user_model().objects.create_user(
                username="unverifiedtrader",
                password="safe-test-password",
            ),
            business_name="Unverified Shop",
            phone="+260 977 654321",
            latitude="-15.400000",
            longitude="28.200000",
        )
        TraderProfile.objects.create(
            user=get_user_model().objects.create_user(
                username="unpinnedtrader",
                password="safe-test-password",
            ),
            business_name="Unpinned Shop",
            phone="+260 977 654322",
            is_verified=True,
        )

        response = self.client.get(reverse("core:home"))

        self.assertEqual(
            [location["name"] for location in response.context["map_locations"]],
            ["Verified Shop"],
        )
