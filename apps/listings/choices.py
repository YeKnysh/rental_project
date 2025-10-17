from django.db.models import TextChoices

class ListingType(TextChoices):
    APARTMENT = "apartment", "Apartment"
    HOUSE     = "house",     "House"
    STUDIO    = "studio",    "Studio"
