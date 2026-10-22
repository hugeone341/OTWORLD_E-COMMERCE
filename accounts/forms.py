from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm
from django.core.exceptions import ValidationError


class TraderRegistrationForm(UserCreationForm):
    email = forms.EmailField()
    business_name = forms.CharField(max_length=180)
    phone = forms.CharField(max_length=30)
    whatsapp_number = forms.CharField(
        max_length=30, required=False, label="WhatsApp number (optional)"
    )
    plot_number = forms.CharField(
        max_length=50,
        required=False,
        help_text="For physical shops, if applicable.",
    )
    latitude = forms.DecimalField(
        required=False,
        max_digits=9,
        decimal_places=6,
        min_value=-90,
        max_value=90,
        widget=forms.HiddenInput,
    )
    longitude = forms.DecimalField(
        required=False,
        max_digits=9,
        decimal_places=6,
        min_value=-180,
        max_value=180,
        widget=forms.HiddenInput,
    )
    description = forms.CharField(required=False, widget=forms.Textarea)
    province = forms.CharField(max_length=80, required=False)
    district = forms.CharField(max_length=100, required=False)
    local_area = forms.CharField(max_length=120, required=False)

    class Meta:
        model = get_user_model()
        fields = ("username", "email")

    field_order = (
        "username",
        "email",
        "password1",
        "password2",
        "business_name",
        "phone",
        "whatsapp_number",
        "plot_number",
        "latitude",
        "longitude",
        "province",
        "district",
        "local_area",
        "description",
    )

    def clean(self):
        cleaned_data = super().clean()
        latitude = cleaned_data.get("latitude")
        longitude = cleaned_data.get("longitude")
        if (latitude is None) != (longitude is None):
            raise ValidationError(
                "Select a complete map location, or leave the map pin unset."
            )
        return cleaned_data
