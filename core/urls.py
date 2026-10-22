from django.urls import path
from . import views

app_name = "core"

urlpatterns = [
    path("", views.home, name="home"),
    path(
        "traders/<int:trader_id>/directions/",
        views.trader_directions,
        name="trader_directions",
    ),
]
