from django.contrib import admin
from .models import Listing

@admin.register(Listing)
class ListingAdmin(admin.ModelAdmin):
    list_display = (
        "title", "listing_type", "category", "trader",
        "province", "status", "created_at",
    )
    list_filter = ("status", "listing_type", "category", "province")
    search_fields = ("title", "description", "trader__business_name")
