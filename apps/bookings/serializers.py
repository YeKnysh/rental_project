from rest_framework import serializers

from .models import Booking
from .choices import BookingStatus


class BookingSerializer(serializers.ModelSerializer):
    """
    Booking payload.

    Notes:
    - `tenant` is read-only; it is filled from the request user.
    - `status` is set to PENDING on create; state changes must use /confirm or /decline.
    """

    class Meta:
        model = Booking
        fields = '__all__'
        read_only_fields = ('tenant', 'created_at', 'updated_at')
        extra_kwargs = {
            'listing': {'help_text': 'Listing ID to book'},
            'start_date': {'help_text': 'Check-in date (inclusive)'},
            'end_date': {'help_text': 'Check-out date (inclusive)'},
            'status': {'help_text': 'Booking status (read-only on create/update here)'},
        }

    def validate(self, attrs):
        """
        Cross-field validation:
        - end_date must be >= start_date
        - prevent overlaps with non-cancelled/non-declined bookings of the same listing
        """
        start = attrs.get('start_date', getattr(self.instance, 'start_date', None))
        end = attrs.get('end_date', getattr(self.instance, 'end_date', None))
        listing = attrs.get('listing', getattr(self.instance, 'listing', None))

        if start and end and end < start:
            raise serializers.ValidationError('end_date must be >= start_date')

        if listing and start and end:
            qs = Booking.objects.filter(listing=listing).exclude(
                status__in=[BookingStatus.CANCELLED, BookingStatus.DECLINED]
            )
            if self.instance:
                qs = qs.exclude(pk=self.instance.pk)
            # intervals [a,b] and [c,d] overlap if a <= d and c <= b
            if qs.filter(start_date__lte=end, end_date__gte=start).exists():
                raise serializers.ValidationError(
                    'This listing is already booked for the selected dates.'
                )

        return attrs

    def create(self, validated_data):
        # enforce initial state
        validated_data['status'] = BookingStatus.PENDING
        return super().create(validated_data)

    def update(self, instance, validated_data):
        # status is controlled only via /confirm and /decline actions
        if 'status' in validated_data and validated_data['status'] != instance.status:
            raise serializers.ValidationError({
                'status': 'Use /bookings/{id}/confirm or /bookings/{id}/decline to change status.'
            })
        return super().update(instance, validated_data)
