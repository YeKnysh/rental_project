from django.core.mail import send_mail
from django.conf import settings

def notify_booking_status(booking):
    """Отправляем письмо арендатору о смене статуса (в консоль)."""
    if not booking.tenant.email:
        return
    subject = f'Booking #{booking.id}: {booking.status}'
    message = (
        f'Listing: {booking.listing.title}\n'
        f'Dates: {booking.start_date} — {booking.end_date}\n'
        f'Status: {booking.status}'
    )
    send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [booking.tenant.email], fail_silently=True)
