from django.contrib import admin
from .models import TraderProfile

@admin.register(TraderProfile)
class TraderProfileAdmin(admin.ModelAdmin):
    list_display = (
        "business_name", "user", "phone", "province",
        "is_verified", "is_suspended",
    )
    list_filter = ("is_verified", "is_suspended", "province")
    search_fields = (
        "business_name", "phone", "user__username", "user__email",
    )
