from rest_framework import viewsets, permissions, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status as http_status
import django_filters.rest_framework as drf_filters

from .models import Booking
from .serializers import BookingSerializer
from .choices import BookingStatus
from apps.common.permissions import IsListingOwner
from .services import notify_booking_status
from drf_spectacular.utils import (
    extend_schema, extend_schema_view,
    OpenApiParameter, OpenApiResponse
)


class BookingFilter(drf_filters.FilterSet):
    """Filters for the bookings list."""
    listing = drf_filters.NumberFilter(field_name='listing_id')
    status = drf_filters.CharFilter(field_name='status', lookup_expr='exact')
    start_min = drf_filters.DateFilter(field_name='start_date', lookup_expr='gte')
    start_max = drf_filters.DateFilter(field_name='start_date', lookup_expr='lte')

    class Meta:
        model = Booking
        fields = ['listing', 'status', 'start_min', 'start_max']


class IsTenantOrReadOnly(permissions.BasePermission):
    """
    Read for everyone.
    Write only for authenticated users.
    Object-level: only the tenant can modify their own booking.
    """
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user and request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.tenant_id == getattr(request.user, 'id', None)


@extend_schema_view(
    list=extend_schema(
        tags=["bookings"],
        summary="List bookings",
        parameters=[
            OpenApiParameter(name="listing", type=int, location=OpenApiParameter.QUERY, description="Listing ID"),
            OpenApiParameter(name="status", type=str, location=OpenApiParameter.QUERY, description="Booking status"),
            OpenApiParameter(name="start_min", type=str, location=OpenApiParameter.QUERY, description="Start date ≥ (YYYY-MM-DD)"),
            OpenApiParameter(name="start_max", type=str, location=OpenApiParameter.QUERY, description="Start date ≤ (YYYY-MM-DD)"),
            OpenApiParameter(name="ordering", type=str, location=OpenApiParameter.QUERY, description="start_date, -start_date, created_at, -created_at"),
        ],
    ),
    retrieve=extend_schema(tags=["bookings"], summary="Retrieve a booking"),
    create=extend_schema(tags=["bookings"], summary="Create a booking"),
    update=extend_schema(tags=["bookings"], summary="Update a booking"),
    partial_update=extend_schema(tags=["bookings"], summary="Partially update a booking"),
    destroy=extend_schema(tags=["bookings"], summary="Delete a booking"),
)
class BookingViewSet(viewsets.ModelViewSet):
    """
    Bookings API.

    List/retrieve: public.
    Create/update/delete: only by the authenticated tenant for their own booking.

    Extra actions:
      • POST /bookings/{id}/confirm/ — confirm by listing owner.
      • POST /bookings/{id}/decline/ — decline by listing owner.
    """
    queryset = Booking.objects.all().select_related('tenant', 'listing', 'listing__owner')
    serializer_class = BookingSerializer
    permission_classes = [IsTenantOrReadOnly]
    filter_backends = [drf_filters.DjangoFilterBackend, filters.OrderingFilter]
    filterset_class = BookingFilter
    ordering_fields = ['start_date', 'created_at']

    def perform_create(self, serializer):
        """Assign current user as tenant on create."""
        serializer.save(tenant=self.request.user)

    @extend_schema(
        operation_id="booking_confirm",
        tags=["bookings"],
        summary="Confirm a booking",
        description=(
            "Confirm the booking by listing owner. "
            "Returns 409 if the period overlaps with another confirmed booking for the same listing."
        ),
        request=None,
        responses={
            200: OpenApiResponse(response=BookingSerializer, description="Confirmed"),
            400: OpenApiResponse(description="Invalid state (e.g., cancelled/declined)"),
            403: OpenApiResponse(description="Forbidden"),
            404: OpenApiResponse(description="Not found"),
            409: OpenApiResponse(description="Date overlap conflict"),
        },
    )
    @action(detail=True, methods=['post'], permission_classes=[IsListingOwner])
    def confirm(self, request, pk=None):
        booking = self.get_object()

        if booking.status in {BookingStatus.CANCELLED, BookingStatus.DECLINED}:
            return Response({'detail': 'Cannot confirm a cancelled/declined booking.'},
                            status=http_status.HTTP_400_BAD_REQUEST)

        conflict = Booking.objects.filter(
            listing=booking.listing,
            status=BookingStatus.CONFIRMED,
            start_date__lte=booking.end_date,
            end_date__gte=booking.start_date
        ).exclude(pk=booking.pk).exists()
        if conflict:
            return Response({'detail': 'Overlaps with an existing confirmed booking.'},
                            status=http_status.HTTP_409_CONFLICT)

        booking.status = BookingStatus.CONFIRMED
        booking.save(update_fields=['status'])
        notify_booking_status(booking)
        return Response({'status': booking.status}, status=http_status.HTTP_200_OK)

    @extend_schema(
        operation_id="booking_decline",
        tags=["bookings"],
        summary="Decline a booking",
        request=None,
        responses={
            200: OpenApiResponse(response=BookingSerializer, description="Declined"),
            400: OpenApiResponse(description="Already declined"),
            403: OpenApiResponse(description="Forbidden"),
            404: OpenApiResponse(description="Not found"),
        },
    )
    @action(detail=True, methods=['post'], permission_classes=[IsListingOwner])
    def decline(self, request, pk=None):
        booking = self.get_object()
        if booking.status == BookingStatus.DECLINED:
            return Response({'detail': 'Already declined.'},
                            status=http_status.HTTP_400_BAD_REQUEST)

        booking.status = BookingStatus.DECLINED
        booking.save(update_fields=['status'])
        notify_booking_status(booking)
        return Response({'status': booking.status}, status=http_status.HTTP_200_OK)
