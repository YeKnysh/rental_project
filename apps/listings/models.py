from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db.models import Q

from apps.common.models import TimeStampedModel
from .choices import ListingType


class Listing(TimeStampedModel):
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="listings",
    )

    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    city = models.CharField(max_length=120)
    district = models.CharField(max_length=120, blank=True, null=True)

    # price must be >= 0.00
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)]
    )

    # rooms between 1 and (e.g.) 20
    rooms = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(20)]
    )

    # avoid using the built-in name "type"
    listing_type = models.CharField(
        max_length=20,
        choices=ListingType.choices,
    )

    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['-created_at']
        constraints = [
            models.CheckConstraint(check=Q(price__gte=0), name='listing_price_non_negative'),
            models.CheckConstraint(check=Q(rooms__gte=1), name='listing_rooms_min_1'),
        ]

    def __str__(self):
        return f"{self.title} — {self.city}"
