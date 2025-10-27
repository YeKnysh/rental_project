from django.core.mail import send_mail
from django.conf import settings


def notify_booking_status(booking):
    """
    Send status email to the tenant.
    Called from apps.bookings.signals on create and on status change.
    """
    email = getattr(booking.tenant, 'email', None)
    if not email:
        return

    # human-readable choice label
    status_label = booking.get_status_display()

    subject = f'Booking #{booking.pk}: {status_label}'
    message = (
        f'Listing: {booking.listing.title}\n'
        f'Dates: {booking.start_date} — {booking.end_date}\n'
        f'Status: {status_label}'
    )
    sender = getattr(settings, 'DEFAULT_FROM_EMAIL', 'noreply@example.com')

    send_mail(subject, message, sender, [email], fail_silently=True)
