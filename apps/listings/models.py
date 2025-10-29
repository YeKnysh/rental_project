# apps/listings/models.py
"""
Listing models.
"""

from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db.models import Q

from apps.common.models import TimeStampedModel
from .choices import ListingType


class Listing(TimeStampedModel):
    """
    Property listing.

    Validation:
      - price >= 0.00
      - rooms in [1..20]
    """

    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="listings",
    )

    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    city = models.CharField(max_length=120)
    district = models.CharField(max_length=120, blank=True, null=True)

    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)]
    )

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
        indexes = [
            models.Index(fields=['city']),
            models.Index(fields=['-created_at']),
        ]

    def __str__(self) -> str:
        return f"{self.title} — {self.city}"
# apps/listings/models.py
"""
Listing models.
"""
from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db.models import Q

from apps.common.models import TimeStampedModel
from .choices import ListingType


class Listing(TimeStampedModel):
    """
    Property listing.

    Validation:
      - price >= 0.00
      - rooms in [1..20]
    """

    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="listings",
    )

    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    city = models.CharField(max_length=120)
    district = models.CharField(max_length=120, blank=True, null=True)

    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)],
    )

    rooms = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(20)],
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
        indexes = [
            models.Index(fields=['city']),
            models.Index(fields=['-created_at']),
        ]

    def __str__(self) -> str:
        return f"{self.title} — {self.city}"
