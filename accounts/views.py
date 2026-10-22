from django.db import transaction
from django.shortcuts import redirect, render

from traders.models import TraderProfile

from .forms import TraderRegistrationForm


def register(request):
    if request.method == "POST":
        form = TraderRegistrationForm(request.POST)
        if form.is_valid():
            with transaction.atomic():
                user = form.save()
                TraderProfile.objects.create(
                    user=user,
                    business_name=form.cleaned_data["business_name"],
                    phone=form.cleaned_data["phone"],
                    whatsapp_number=form.cleaned_data["whatsapp_number"],
                    plot_number=form.cleaned_data["plot_number"],
                    latitude=form.cleaned_data["latitude"],
                    longitude=form.cleaned_data["longitude"],
                    description=form.cleaned_data["description"],
                    province=form.cleaned_data["province"],
                    district=form.cleaned_data["district"],
                    local_area=form.cleaned_data["local_area"],
                )
            return redirect("accounts:registration_complete")
    else:
        form = TraderRegistrationForm()

    return render(request, "accounts/register.html", {"form": form})


def registration_complete(request):
    return render(request, "accounts/registration_complete.html")
