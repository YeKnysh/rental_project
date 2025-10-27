# apps/bookings/signals.py
from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import Booking
from .services import notify_booking_status


@receiver(post_save, sender=Booking)
def booking_saved(sender, instance: Booking, created, **kwargs):
    """
    Notify on create or when status changes.
    Works with .save(update_fields=['status']) used in confirm/decline actions.
    """
    update_fields = kwargs.get('update_fields')
    if created or (update_fields and 'status' in update_fields):
        notify_booking_status(instance)
