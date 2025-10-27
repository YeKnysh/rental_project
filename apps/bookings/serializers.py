# apps/bookings/serializers.py
from django.utils import timezone
from rest_framework import serializers

from .models import Booking
from .choices import BookingStatus
from apps.listings.models import Listing


class ListingBriefSerializer(serializers.ModelSerializer):
    """Compact listing card shown inside booking responses."""
    class Meta:
        model = Listing
        fields = ("id", "title", "city", "district", "price", "rooms", "listing_type")


class BookingSerializer(serializers.ModelSerializer):
    """
    Booking payload (stable).

    Response:
      - booking_id: booking PK
      - listing_id: listing PK
      - listing_info: compact listing card (city/district/etc.)
      - tenant_id / tenant_email
      - listing_owner_email
    Rules:
      - On create -> PENDING.
      - Status changes only via actions (/confirm, /decline, /cancel).
      - Listing cannot be changed by update.
      - Overlaps are allowed on create; conflicts are checked on /confirm.
    """

    # explicit ids (no source=... to avoid DRF assertion)
    booking_id = serializers.IntegerField(source="id", read_only=True)
    listing_id = serializers.IntegerField(read_only=True)
    tenant_id = serializers.IntegerField(read_only=True)

    # write listing as PK in requests; hide it in responses
    listing = serializers.PrimaryKeyRelatedField(
        queryset=Listing.objects.filter(is_active=True),
        write_only=True,
        help_text="Listing ID to book",
    )

    # richer context in responses
    listing_info = ListingBriefSerializer(source="listing", read_only=True)
    tenant_email = serializers.EmailField(source="tenant.email", read_only=True)
    listing_owner_email = serializers.EmailField(
        source="listing.owner.email",
        read_only=True,
        help_text="Owner email of the booked listing",
    )

    class Meta:
        model = Booking
        fields = [
            "booking_id",
            "listing_id",
            "listing",              # write_only
            "listing_info",         # read_only
            "tenant_id",
            "tenant_email",
            "listing_owner_email",
            "start_date",
            "end_date",
            "check_in_time",
            "status",
            "created_at",
            "updated_at",
        ]
        read_only_fields = (
            "booking_id",
            "listing_id",
            "listing_info",
            "tenant_id",
            "tenant_email",
            "listing_owner_email",
            "status",
            "created_at",
            "updated_at",
        )
        extra_kwargs = {
            "start_date": {"help_text": "Check-in date (YYYY-MM-DD)"},
            "end_date": {"help_text": "Check-out date (YYYY-MM-DD)"},
            "check_in_time": {"help_text": "HH:MM:SS"},
        }

    # ---- validation (dates only) ----
    def validate(self, attrs):
        instance = getattr(self, "instance", None)
        start = attrs.get("start_date", getattr(instance, "start_date", None))
        end = attrs.get("end_date", getattr(instance, "end_date", None))

        if start and start < timezone.localdate():
            raise serializers.ValidationError({"start_date": "start_date must be today or later"})
        if start and end and end < start:
            raise serializers.ValidationError({"end_date": "end_date must be >= start_date"})
        # overlaps intentionally not checked here (handled on /confirm)
        return attrs

    # ---- create/update rules ----
    def create(self, validated_data):
        validated_data["status"] = BookingStatus.PENDING
        return super().create(validated_data)

    def update(self, instance, validated_data):
        if "status" in validated_data and validated_data["status"] != instance.status:
            raise serializers.ValidationError({
                "status": "Use /bookings/{id}/confirm, /decline or /cancel to change status."
            })
        if "listing" in validated_data:
            raise serializers.ValidationError({"listing": "Listing cannot be changed"})
        return super().update(instance, validated_data)
