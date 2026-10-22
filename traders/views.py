from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from .models import TraderProfile


def trader_login(request):
    if request.user.is_authenticated:
        if TraderProfile.objects.filter(user=request.user).exists():
            return redirect("trader_dashboard")

    if request.method == "POST":
        username = request.POST.get("username", "").strip()
        password = request.POST.get("password", "")
        user = authenticate(request, username=username, password=password)

        if user is not None and user.is_active:
            try:
                profile = TraderProfile.objects.get(user=user)
            except TraderProfile.DoesNotExist:
                messages.error(request, "This account is not registered as a trader.")
                return render(request, "traders/login.html")

            if profile.is_suspended or not profile.is_verified:
                messages.error(
                    request,
                    "Your trader account is suspended or awaiting verification."
                )
                return render(request, "traders/login.html")

            login(request, user)
            return redirect("trader_dashboard")

        messages.error(request, "Invalid username or password.")

    return render(request, "traders/login.html")


@login_required(login_url="trader_login")
def trader_dashboard(request):
    try:
        profile = TraderProfile.objects.get(user=request.user)
    except TraderProfile.DoesNotExist:
        logout(request)
        messages.error(request, "Trader profile not found.")
        return redirect("trader_login")

    if profile.is_suspended or not profile.is_verified:
        logout(request)
        messages.error(request, "Your trader account is not active.")
        return redirect("trader_login")

    return render(
        request,
        "traders/dashboard.html",
        {"profile": profile}
    )


@require_POST
def trader_logout(request):
    logout(request)
    return redirect("trader_login")