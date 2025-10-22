from django.db import models
from apps.common.models import TimeStampedModel
from django.conf import settings
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
    price = models.DecimalField(max_digits=10, decimal_places=2)
    rooms = models.PositiveSmallIntegerField()
    type = models.CharField(max_length=20, choices=ListingType.choices)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.title} — {self.city}"

