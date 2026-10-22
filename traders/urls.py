from django.urls import path
from . import views

urlpatterns = [
    path("login/", views.trader_login, name="trader_login"),
    path("dashboard/", views.trader_dashboard, name="trader_dashboard"),
    path("logout/", views.trader_logout, name="trader_logout"),
]