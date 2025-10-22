from rest_framework import viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Count

from django.contrib.auth import get_user_model
from apps.listings.models import Listing
from apps.bookings.models import Booking
from apps.reviews.models import Review
from apps.bookings.choices import BookingStatus

from drf_spectacular.utils import (
    extend_schema, extend_schema_view, OpenApiParameter, OpenApiResponse
)


@extend_schema_view(
    summary=extend_schema(
        tags=["statistics"],
        summary="Project summary",
        description="Total counts for users, listings, bookings and reviews.",
        responses={200: OpenApiResponse(description="Aggregated totals")},
    ),
    bookings_by_status=extend_schema(
        tags=["statistics"],
        summary="Bookings by status",
        description="Aggregated bookings grouped by status.",
        responses={200: OpenApiResponse(description="List of {'status': str, 'count': int}")},
    ),
    top_cities=extend_schema(
        tags=["statistics"],
        summary="Top cities by listings",
        description="Most popular cities by number of listings.",
        parameters=[
            OpenApiParameter(
                name="limit",
                description="How many cities to return",
                required=False,
                type=int,
                location=OpenApiParameter.QUERY,
            ),
        ],
        responses={200: OpenApiResponse(description="List of {'city': str, 'count': int}")},
    ),
    owner_dashboard=extend_schema(
        tags=["statistics"],
        summary="Owner dashboard",
        description="Private aggregate stats for the current owner.",
        responses={200: OpenApiResponse(description="Owner-specific totals")},
    ),
)
class StatsViewSet(viewsets.ViewSet):
    permission_classes = [permissions.AllowAny]

    @action(detail=False, methods=['get'])
    def summary(self, request):
        U = get_user_model()
        data = {
            'users': U.objects.count(),
            'listings': Listing.objects.count(),
            'bookings': Booking.objects.count(),
            'reviews': Review.objects.count(),
        }
        return Response(data)

    @action(detail=False, methods=['get'])
    def bookings_by_status(self, request):
        qs = (
            Booking.objects
            .values('status')
            .annotate(count=Count('id'))
            .order_by('-count')
        )
        # optional: normalize keys to known statuses
        status_map = {
            BookingStatus.PENDING: 'pending',
            BookingStatus.CONFIRMED: 'confirmed',
            BookingStatus.DECLINED: 'declined',
            BookingStatus.CANCELLED: 'cancelled',
        }
        result = [{'status': status_map.get(row['status'], row['status']), 'count': row['count']} for row in qs]
        return Response(result)

    @action(detail=False, methods=['get'])
    def top_cities(self, request):
        try:
            limit = int(request.query_params.get('limit', 5))
        except ValueError:
            limit = 5

        qs = (
            Listing.objects
            .values('city')
            .annotate(count=Count('id'))
            .order_by('-count')[:limit]
        )
        return Response(list(qs))

    @action(detail=False, methods=['get'], permission_classes=[permissions.IsAuthenticated])
    def owner_dashboard(self, request):
        my_listings = Listing.objects.filter(owner=request.user)
        bookings = Booking.objects.filter(listing__in=my_listings)
        data = {
            'my_listings': my_listings.count(),
            'bookings_total': bookings.count(),
            'pending': bookings.filter(status=BookingStatus.PENDING).count(),
            'confirmed': bookings.filter(status=BookingStatus.CONFIRMED).count(),
            'declined': bookings.filter(status=BookingStatus.DECLINED).count(),
            'cancelled': bookings.filter(status=BookingStatus.CANCELLED).count(),
        }
        return Response(data)
