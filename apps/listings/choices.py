# apps/listings/choices.py
"""Listing-related enumerations."""
from django.db.models import TextChoices


class ListingType(TextChoices):
    """Type of property."""
    APARTMENT = "apartment", "Apartment"
    HOUSE     = "house",     "House"
    STUDIO    = "studio",    "Studio"
