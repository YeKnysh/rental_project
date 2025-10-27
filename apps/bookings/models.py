# apps/bookings/models.py
from datetime import time
from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models

from apps.listings.models import Listing
from .choices import BookingStatus


class Booking(models.Model):
    # что бронируем и кто бронирует
    listing = models.ForeignKey(Listing, related_name="bookings", on_delete=models.CASCADE)
    tenant = models.ForeignKey(settings.AUTH_USER_MODEL, related_name="bookings", on_delete=models.CASCADE)

    # даты и заселение
    start_date = models.DateField()
    end_date = models.DateField()
    check_in_time = models.TimeField(default=time(14, 0))

    # текущее состояние
    status = models.CharField(
        max_length=20,
        choices=BookingStatus.choices,
        default=BookingStatus.PENDING,
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ("-created_at",)
        indexes = [
            models.Index(fields=("listing", "start_date", "end_date", "status")),
        ]

    def __str__(self) -> str:
        return f"Booking #{self.pk} for listing {self.listing_id}"

    def clean(self):
        """Минимальные проверки на уровне модели."""
        errors = {}

        # 1) конец не раньше начала
        if self.start_date and self.end_date and self.end_date < self.start_date:
            errors["end_date"] = "End date must be ≥ start date."

        # 2) пересечения считаем только для подтверждённых броней
        if (
            self.status == BookingStatus.CONFIRMED
            and self.listing_id
            and self.start_date
            and self.end_date
        ):
            qs = Booking.objects.filter(
                listing=self.listing,
                status=BookingStatus.CONFIRMED,
            )
            if self.pk:
                qs = qs.exclude(pk=self.pk)

            # интервалы [a,b] и [c,d] пересекаются, если a ≤ d и c ≤ b
            if qs.filter(start_date__lte=self.end_date, end_date__gte=self.start_date).exists():
                errors["start_date"] = "Overlaps with another confirmed booking for this listing."

        if errors:
            raise ValidationError(errors)

    def save(self, *args, **kwargs):
        # держим валидацию перед сохранением
        self.full_clean()
        return super().save(*args, **kwargs)
