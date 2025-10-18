from django.db import models
from django.conf import settings

from apps.common.models import TimeStampedModel
from apps.listings.models import Listing


class Review(TimeStampedModel):
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name='reviews')
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='reviews')
    rating = models.PositiveSmallIntegerField()
    comment = models.TextField(blank=True)

    class Meta:
        ordering = ['-created_at']
        constraints = [
            models.CheckConstraint(check=models.Q(rating__gte=1, rating__lte=5), name='rating_1_5'),
            models.UniqueConstraint(fields=['listing', 'author'], name='unique_review_per_user_per_listing'),
        ]

    def __str__(self):
        return f'{self.listing_id} ★{self.rating}'
