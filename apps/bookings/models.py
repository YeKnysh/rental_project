from django.db import models
from django.conf import settings

from apps.common.models import TimeStampedModel
from apps.listings.models import Listing
from .choices import BookingStatus


class Booking(TimeStampedModel):
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name='bookings')
    tenant = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='bookings')
    start_date = models.DateField()
    end_date = models.DateField()
    status = models.CharField(max_length=20, choices=BookingStatus.choices, default=BookingStatus.PENDING)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.listing_id} {self.start_date}–{self.end_date} {self.status}'
