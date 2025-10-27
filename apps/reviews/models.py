# apps/reviews/models.py
from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone

from apps.common.models import TimeStampedModel
from apps.listings.models import Listing
from apps.bookings.models import Booking
from apps.bookings.choices import BookingStatus


class Review(TimeStampedModel):
    """User review for a listing."""

    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name="reviews")
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="reviews")
    rating = models.PositiveSmallIntegerField()
    comment = models.TextField(blank=True)

    class Meta:
        ordering = ("-created_at",)
        constraints = [
            # rating must be within 1..5 (DB-level)
            models.CheckConstraint(check=models.Q(rating__gte=1, rating__lte=5), name="rating_1_5"),
            # one review per listing from the same user
            models.UniqueConstraint(
                fields=("listing", "author"),
                name="unique_review_per_user_per_listing",
            ),
        ]
        indexes = [
            models.Index(fields=("listing", "author")),
        ]

    def __str__(self) -> str:
        return f"{self.listing_id} ★{self.rating}"

    def clean(self):
        """Basic model-level validation."""
        errors = {}

        # runtime check too (nice error in API in addition to DB check)
        if self.rating is not None and not (1 <= self.rating <= 5):
            errors["rating"] = "Rating must be between 1 and 5."

        # allow review only if user had a confirmed booking for this listing
        if self.listing_id and self.author_id:
            today = timezone.localdate()
            has_confirmed_booking = Booking.objects.filter(
                listing_id=self.listing_id,
                tenant_id=self.author_id,
                status=BookingStatus.CONFIRMED,
                # If you want to allow review only after stay finished, uncomment:
                # end_date__lte=today,
            ).exists()
            if not has_confirmed_booking:
                errors["__all__"] = "You can review a listing only after a confirmed booking."

        if errors:
            raise ValidationError(errors)

    def save(self, *args, **kwargs):
        # ensure clean() runs on every save
        self.full_clean()
        return super().save(*args, **kwargs)
