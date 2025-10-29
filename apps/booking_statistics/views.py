# apps/booking_statistics/views.py
from django.db.models import Count
from django.contrib.auth import get_user_model

from rest_framework import permissions, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import serializers

from drf_spectacular.utils import (
    extend_schema,
    extend_schema_view,
    OpenApiParameter,
)

from apps.listings.models import Listing
from apps.bookings.models import Booking
from apps.reviews.models import Review
from apps.bookings.choices import BookingStatus


# ---- inline serializers for documentation ----

class SummarySerializer(serializers.Serializer):
    """Totals across the whole project."""
    users = serializers.IntegerField()
    listings = serializers.IntegerField()
    bookings = serializers.IntegerField()
    reviews = serializers.IntegerField()


class StatusCountSerializer(serializers.Serializer):
    """Count of bookings by status."""
    status = serializers.CharField()
    count = serializers.IntegerField()


class CityCountSerializer(serializers.Serializer):
    """Top cities by number of listings."""
    city = serializers.CharField(allow_blank=True, allow_null=True)
    count = serializers.IntegerField()


class OwnerDashboardSerializer(serializers.Serializer):
    """Owner-only aggregated stats."""
    my_listings = serializers.IntegerField()
    bookings_total = serializers.IntegerField()
    pending = serializers.IntegerField()
    confirmed = serializers.IntegerField()
    declined = serializers.IntegerField()
    cancelled = serializers.IntegerField()


@extend_schema_view(
    summary=extend_schema(
        tags=["statistics"],
        summary="Project summary",
        description="Total counts for users, listings, bookings and reviews.",
        responses={200: SummarySerializer},
    ),
    bookings_by_status=extend_schema(
        tags=["statistics"],
        summary="Bookings by status",
        description="Aggregated bookings grouped by status.",
        responses={200: StatusCountSerializer(many=True)},
    ),
    top_cities=extend_schema(
        tags=["statistics"],
        summary="Top cities by listings",
        description="Most popular cities by number of listings.",
        parameters=[
            OpenApiParameter(
                name="limit",
                description="How many cities to return (1–50). Default: 5",
                required=False,
                type=int,
                location=OpenApiParameter.QUERY,
            ),
        ],
        responses={200: CityCountSerializer(many=True)},
    ),
    owner_dashboard=extend_schema(
        tags=["statistics"],
        summary="Owner dashboard",
        description="Private aggregate stats for the current owner (session auth required).",
        responses={200: OwnerDashboardSerializer},
    ),
)
class StatsViewSet(viewsets.ViewSet):
    """
    Statistics API.

    Public:
      • GET /statistics/summary/
      • GET /statistics/bookings_by_status/
      • GET /statistics/top_cities/?limit=5

    Private (owner only by session auth):
      • GET /statistics/owner_dashboard/
    """
    permission_classes = [permissions.AllowAny]

    @action(detail=False, methods=["get"])
    def summary(self, request):
        U = get_user_model()
        data = {
            "users": U.objects.count(),
            "listings": Listing.objects.count(),
            "bookings": Booking.objects.count(),
            "reviews": Review.objects.count(),
        }
        return Response(SummarySerializer(instance=data).data)

    @action(detail=False, methods=["get"])
    def bookings_by_status(self, request):
        qs = (
            Booking.objects
            .values("status")
            .annotate(count=Count("id"))
            .order_by("-count")
        )
        # normalize to readable labels (keep original if not matched)
        status_map = {
            BookingStatus.PENDING: "pending",
            BookingStatus.CONFIRMED: "confirmed",
            BookingStatus.DECLINED: "declined",
            BookingStatus.CANCELLED: "cancelled",
        }
        data = [
            {"status": status_map.get(row["status"], row["status"]), "count": row["count"]}
            for row in qs
        ]
        return Response(StatusCountSerializer(instance=data, many=True).data)

    @action(detail=False, methods=["get"])
    def top_cities(self, request):
        # simple, safe limit parsing
        try:
            limit = int(request.query_params.get("limit", 5))
        except (TypeError, ValueError):
            limit = 5
        limit = max(1, min(limit, 50))  # clamp to [1..50]

        qs = (
            Listing.objects
            .values("city")
            .annotate(count=Count("id"))
            .order_by("-count")[:limit]
        )
        data = list(qs)
        return Response(CityCountSerializer(instance=data, many=True).data)

    @action(
        detail=False,
        methods=["get"],
        permission_classes=[permissions.IsAuthenticated],
    )
    def owner_dashboard(self, request):
        my_listings = Listing.objects.filter(owner=request.user)
        bookings = Booking.objects.filter(listing__in=my_listings)
        data = {
            "my_listings": my_listings.count(),
            "bookings_total": bookings.count(),
            "pending": bookings.filter(status=BookingStatus.PENDING).count(),
            "confirmed": bookings.filter(status=BookingStatus.CONFIRMED).count(),
            "declined": bookings.filter(status=BookingStatus.DECLINED).count(),
            "cancelled": bookings.filter(status=BookingStatus.CANCELLED).count(),
        }
        return Response(OwnerDashboardSerializer(instance=data).data)
