from django.shortcuts import get_object_or_404, render
from django.urls import reverse

from traders.models import TraderProfile


CATEGORIES = [
    {"name": "Electronics", "icon": "⌘"},
    {"name": "Fashion", "icon": "◇"},
    {"name": "Home & Furniture", "icon": "⌂"},
    {"name": "Food & Agriculture", "icon": "✳"},
    {"name": "Beauty & Personal Care", "icon": "✦"},
    {"name": "Construction", "icon": "▦"},
    {"name": "Transport", "icon": "↗"},
    {"name": "Professional Services", "icon": "◎"},
    {"name": "Education", "icon": "▤"},
    {"name": "Other", "icon": "＋"},
]


def home(request):
    traders = TraderProfile.objects.filter(
        is_verified=True,
        is_suspended=False,
    ).order_by("business_name")
    map_locations = [
        {
            "name": trader.business_name,
            "address": ", ".join(
                part
                for part in (
                    trader.plot_number,
                    trader.local_area,
                    trader.district,
                    trader.province,
                )
                if part
            ),
            "latitude": float(trader.latitude),
            "longitude": float(trader.longitude),
            "url": reverse(
                "core:trader_directions",
                kwargs={"trader_id": trader.pk},
            ),
        }
        for trader in traders
        if trader.latitude is not None and trader.longitude is not None
    ]
    context = {
        "categories": CATEGORIES,
        "query": request.GET.get("q", "").strip(),
        "location": request.GET.get("location", "").strip(),
        "traders": traders,
        "map_locations": map_locations,
    }
    return render(request, "core/home.html", context)


def trader_directions(request, trader_id):
    trader = get_object_or_404(
        TraderProfile.objects.select_related("user"),
        pk=trader_id,
        is_verified=True,
        is_suspended=False,
        latitude__isnull=False,
        longitude__isnull=False,
    )
    destination_parts = [
        trader.business_name,
        trader.plot_number,
        trader.local_area,
        trader.district,
        trader.province,
    ]
    return render(
        request,
        "core/trader_directions.html",
        {
            "trader": trader,
            "destination_label": ", ".join(
                part for part in destination_parts if part
            ),
        },
    )
