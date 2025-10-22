from django.db import models
from django.conf import settings
from django.db.models import Q, F

from apps.common.models import TimeStampedModel
from apps.listings.models import Listing
from .choices import BookingStatus


class Booking(TimeStampedModel):
    listing = models.ForeignKey(Listing, on_delete=models.PROTECT, related_name='bookings')
    tenant = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name='bookings')

    start_date = models.DateField()
    end_date = models.DateField()
    check_in_time = models.TimeField(null=True, blank=True)  # время заезда (необязательное)

    status = models.CharField(max_length=20, choices=BookingStatus.choices, default=BookingStatus.PENDING)

    class Meta:
        constraints = [
            models.CheckConstraint(check=Q(end_date__gte=F('start_date')), name='booking_end_after_start'),
        ]
        indexes = [
            models.Index(fields=['listing', 'start_date']),
            models.Index(fields=['listing', 'end_date']),
        ]

    def __str__(self):
        return f'Booking #{self.pk} ({self.listing_id})'
