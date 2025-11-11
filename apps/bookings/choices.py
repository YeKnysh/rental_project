# apps/bookings/choices.py
"""Booking-related enumerations."""
from django.db.models import TextChoices


class BookingStatus(TextChoices):
    """Booking lifecycle states."""
    PENDING   = "pending",   "Pending"
    CONFIRMED = "confirmed", "Confirmed"
    DECLINED  = "declined",  "Declined"
    CANCELLED = "cancelled", "Cancelled"
