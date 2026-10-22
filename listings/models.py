from django.db import models

class Listing(models.Model):
    class ListingType(models.TextChoices):
        PRODUCT = "product", "Product"
        SERVICE = "service", "Service"

    class Status(models.TextChoices):
        PENDING = "pending", "Pending review"
        APPROVED = "approved", "Approved"
        REJECTED = "rejected", "Rejected"
        HIDDEN = "hidden", "Hidden"

    CATEGORY_CHOICES = [
        ("electronics", "Electronics"),
        ("fashion", "Fashion"),
        ("home_furniture", "Home & Furniture"),
        ("food_agriculture", "Food & Agriculture"),
        ("beauty_personal_care", "Beauty & Personal Care"),
        ("construction_hardware", "Construction & Hardware"),
        ("vehicles_transport", "Vehicles & Transport"),
        ("professional_services", "Professional Services"),
        ("education", "Education"),
        ("other", "Other"),
    ]

    trader = models.ForeignKey(
        "traders.TraderProfile",
        on_delete=models.CASCADE,
        related_name="listings",
    )
    title = models.CharField(max_length=180)
    description = models.TextField()
    listing_type = models.CharField(
        max_length=10,
        choices=ListingType.choices,
        default=ListingType.PRODUCT,
    )
    category = models.CharField(
        max_length=40,
        choices=CATEGORY_CHOICES,
        default="other",
    )
    price = models.DecimalField(
        max_digits=12, decimal_places=2, null=True, blank=True
    )
    is_negotiable = models.BooleanField(default=False)
    province = models.CharField(max_length=80, blank=True)
    district = models.CharField(max_length=100, blank=True)
    town_or_area = models.CharField(max_length=120, blank=True)
    status = models.CharField(
        max_length=12,
        choices=Status.choices,
        default=Status.PENDING,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.title
