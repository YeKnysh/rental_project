from django.db.models import TextChoices

class BookingStatus(TextChoices):
    PENDING    = 'pending', 'Pending'
    CONFIRMED  = 'confirmed', 'Confirmed'
    DECLINED   = 'declined', 'Declined'
    CANCELLED  = 'cancelled', 'Cancelled'
