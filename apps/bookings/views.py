# apps/bookings/views.py
from django.utils import timezone
from django_filters import rest_framework as drf_filters
from rest_framework import status as http_status, filters, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import (
    OpenApiExample,
    OpenApiParameter,
    OpenApiResponse,
    extend_schema,
    extend_schema_view,
)

from .choices import BookingStatus
from .models import Booking
from .serializers import BookingSerializer
from apps.common.permissions import IsListingOwner, IsTenantOrReadOnly


class BookingFilter(drf_filters.FilterSet):
    """Filters for bookings list."""
    # основной параметр
    listing_id = drf_filters.NumberFilter(field_name="listing_id")
    # алиас для обратной совместимости
    listing = drf_filters.NumberFilter(field_name="listing_id")

    status = drf_filters.CharFilter(field_name="status", lookup_expr="exact")
    start_min = drf_filters.DateFilter(field_name="start_date", lookup_expr="gte")
    start_max = drf_filters.DateFilter(field_name="start_date", lookup_expr="lte")

    class Meta:
        model = Booking
        fields = ["listing_id", "listing", "status", "start_min", "start_max"]


create_example = OpenApiExample(
    name="Create booking (example)",
    value={
        "listing": 1,
        "start_date": "2025-11-10",
        "end_date": "2025-11-13",
        "check_in_time": "14:00:00",
    },
    request_only=True,
)

error_400_example = OpenApiExample(
    name="Validation error",
    value={"non_field_errors": ["End date must be after start date."]},
    response_only=True,
)


@extend_schema_view(
    list=extend_schema(
        tags=["bookings"],
        summary="List bookings",
        description="Filtered and paginated list of bookings.",
        parameters=[
            OpenApiParameter("listing_id", type=int, location=OpenApiParameter.QUERY, description="Filter by listing id"),
            OpenApiParameter("listing", type=int, location=OpenApiParameter.QUERY, description="Same as listing_id (alias)"),
            OpenApiParameter("status", type=str, location=OpenApiParameter.QUERY, description="Booking status"),
            OpenApiParameter("start_min", type=str, location=OpenApiParameter.QUERY, description="Start date ≥ (YYYY-MM-DD)"),
            OpenApiParameter("start_max", type=str, location=OpenApiParameter.QUERY, description="Start date ≤ (YYYY-MM-DD)"),
            OpenApiParameter("ordering", type=str, location=OpenApiParameter.QUERY,
                             description="start_date, -start_date, created_at, -created_at"),
        ],
        responses={200: BookingSerializer(many=True)},
    ),
    retrieve=extend_schema(tags=["bookings"], summary="Retrieve a booking", responses={200: BookingSerializer}),
    create=extend_schema(
        tags=["bookings"],
        summary="Create a booking",
        description="Tenant creates a booking request.",
        request=BookingSerializer,
        responses={201: BookingSerializer, 400: OpenApiTypes.OBJECT, 403: OpenApiTypes.OBJECT},
        examples=[create_example, error_400_example],
    ),
    update=extend_schema(
        tags=["bookings"], summary="Update a booking",
        request=BookingSerializer,
        responses={200: BookingSerializer, 400: OpenApiTypes.OBJECT, 403: OpenApiTypes.OBJECT},
    ),
    partial_update=extend_schema(
        tags=["bookings"], summary="Partially update a booking",
        request=BookingSerializer,
        responses={200: BookingSerializer, 400: OpenApiTypes.OBJECT, 403: OpenApiTypes.OBJECT},
    ),
    destroy=extend_schema(tags=["bookings"], summary="Delete a booking", responses={204: None, 403: OpenApiTypes.OBJECT}),
)
class BookingViewSet(viewsets.ModelViewSet):
    """
    Bookings API.
    List/retrieve: public.
    Create/update/delete: only by the authenticated tenant for their own booking.
    Extra actions:
      • POST /bookings/{id}/confirm/ — confirm by listing owner.
      • POST /bookings/{id}/decline/ — decline by listing owner.
      • POST /bookings/{id}/cancel/ — cancel by tenant (only before start date).
    """
    queryset = Booking.objects.all().select_related("tenant", "listing", "listing__owner")
    serializer_class = BookingSerializer
    permission_classes = [IsTenantOrReadOnly]
    filter_backends = [drf_filters.DjangoFilterBackend, filters.OrderingFilter]
    filterset_class = BookingFilter
    ordering_fields = ["start_date", "created_at"]
    ordering = ["-created_at"]

    def perform_create(self, serializer):
        """Assign current user as tenant on create."""
        serializer.save(tenant=self.request.user)

    # ---- confirm (owner) ----
    @extend_schema(
        operation_id="booking_confirm",
        tags=["bookings"],
        summary="Confirm a booking",
        description=(
            "Confirm the booking by the listing owner. "
            "Returns **409** if the period overlaps with another *confirmed* booking for the same listing."
        ),
        request=None,
        responses={
            200: OpenApiResponse(response=BookingSerializer, description="Confirmed"),
            400: OpenApiResponse(description="Invalid state (e.g. already declined/cancelled)"),
            403: OpenApiResponse(description="Forbidden"),
            404: OpenApiResponse(description="Not found"),
            409: OpenApiResponse(description="Date overlap conflict"),
        },
    )
    @action(detail=True, methods=["post"], permission_classes=[IsListingOwner])
    def confirm(self, request, pk=None):
        booking = self.get_object()
        # важно: на кастомных action проверяем объектные права явно
        self.check_object_permissions(request, booking)

        if booking.status in {BookingStatus.CANCELLED, BookingStatus.DECLINED}:
            return Response({"detail": "Cannot confirm a cancelled or declined booking."},
                            status=http_status.HTTP_400_BAD_REQUEST)

        conflict = Booking.objects.filter(
            listing=booking.listing,
            status=BookingStatus.CONFIRMED,
            start_date__lte=booking.end_date,
            end_date__gte=booking.start_date,
        ).exclude(pk=booking.pk).exists()
        if conflict:
            return Response({"detail": "Overlaps with an existing confirmed booking."},
                            status=http_status.HTTP_409_CONFLICT)

        booking.status = BookingStatus.CONFIRMED
        booking.save(update_fields=["status"])
        return Response(BookingSerializer(booking).data, status=http_status.HTTP_200_OK)

    # ---- decline (owner) ----
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
    @action(detail=True, methods=["post"], permission_classes=[IsListingOwner])
    def decline(self, request, pk=None):
        booking = self.get_object()
        self.check_object_permissions(request, booking)

        if booking.status == BookingStatus.DECLINED:
            return Response({"detail": "Already declined."}, status=http_status.HTTP_400_BAD_REQUEST)

        booking.status = BookingStatus.DECLINED
        booking.save(update_fields=["status"])
        return Response(BookingSerializer(booking).data, status=http_status.HTTP_200_OK)

    # ---- cancel (tenant) ----
    @extend_schema(
        operation_id="booking_cancel",
        tags=["bookings"],
        summary="Cancel a booking",
        description="Cancel by tenant **only before** the start date.",
        request=None,
        responses={
            200: OpenApiResponse(response=BookingSerializer, description="Cancelled"),
            400: OpenApiResponse(description="Too late to cancel / already cancelled/declined"),
            403: OpenApiResponse(description="Forbidden"),
            404: OpenApiResponse(description="Not found"),
        },
    )
    @action(detail=True, methods=["post"], permission_classes=[IsTenantOrReadOnly])
    def cancel(self, request, pk=None):
        booking = self.get_object()
        self.check_object_permissions(request, booking)

        if booking.status in {BookingStatus.CANCELLED, BookingStatus.DECLINED}:
            return Response({"detail": "Already cancelled or declined."}, status=http_status.HTTP_400_BAD_REQUEST)

        if timezone.localdate() >= booking.start_date:
            return Response({"detail": "Too late to cancel."}, status=http_status.HTTP_400_BAD_REQUEST)

        booking.status = BookingStatus.CANCELLED
        booking.save(update_fields=["status"])
        return Response(BookingSerializer(booking).data, status=http_status.HTTP_200_OK)
