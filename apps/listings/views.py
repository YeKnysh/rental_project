from rest_framework import viewsets, filters
from django_filters.rest_framework import (
    DjangoFilterBackend, FilterSet, NumberFilter, CharFilter
)
from drf_spectacular.utils import (
    extend_schema, extend_schema_view, OpenApiParameter, OpenApiExample
)
from drf_spectacular.types import OpenApiTypes

from .models import Listing
from .serializers import ListingSerializer
from apps.common.permissions import IsOwnerOrReadOnly


class ListingFilter(FilterSet):
    price_min = NumberFilter(field_name="price", lookup_expr="gte")
    price_max = NumberFilter(field_name="price", lookup_expr="lte")
    rooms_min = NumberFilter(field_name="rooms", lookup_expr="gte")
    rooms_max = NumberFilter(field_name="rooms", lookup_expr="lte")
    city = CharFilter(field_name="city", lookup_expr="icontains")
    district = CharFilter(field_name="district", lookup_expr="icontains")
    listing_type = CharFilter(field_name="listing_type", lookup_expr="exact")

    class Meta:
        model = Listing
        fields = [
            "city", "district", "listing_type",
            "price_min", "price_max", "rooms_min", "rooms_max",
        ]


create_example = OpenApiExample(
    name="Create listing (example)",
    value={
        "title": "Sunny Studio in Cologne",
        "description": "Cozy studio near the center.",
        "city": "Cologne",
        "district": "Innenstadt",
        "price": "550.00",
        "rooms": 1,
        "listing_type": "apartment",
    },
    request_only=True,
)

update_example = OpenApiExample(
    name="Update listing (example)",
    value={"price": "575.00", "rooms": 2, "is_active": True},
    request_only=True,
)

error_400_example = OpenApiExample(
    name="Validation error",
    value={"price": ["Ensure this value is greater than or equal to 0."]},
    response_only=True,
)


@extend_schema_view(
    list=extend_schema(
        tags=["listings"],
        summary="List listings",
        description="Filtered and paginated list of listings.",
        parameters=[
            OpenApiParameter(name="city", description="City contains", required=False, type=str,
                             location=OpenApiParameter.QUERY),
            OpenApiParameter(name="district", description="District contains", required=False, type=str,
                             location=OpenApiParameter.QUERY),
            OpenApiParameter(name="listing_type", description="Listing type (choice)", required=False, type=str,
                             location=OpenApiParameter.QUERY),
            OpenApiParameter(name="rooms_min", description="Rooms ≥", required=False, type=int,
                             location=OpenApiParameter.QUERY),
            OpenApiParameter(name="rooms_max", description="Rooms ≤", required=False, type=int,
                             location=OpenApiParameter.QUERY),
            OpenApiParameter(name="price_min", description="Price ≥", required=False, type=float,
                             location=OpenApiParameter.QUERY),
            OpenApiParameter(name="price_max", description="Price ≤", required=False, type=float,
                             location=OpenApiParameter.QUERY),
            OpenApiParameter(name="search", description="Search in title/description/city/district",
                             required=False, type=str, location=OpenApiParameter.QUERY),
            OpenApiParameter(name="ordering",
                             description="price | -price | created_at | -created_at",
                             required=False, type=str, location=OpenApiParameter.QUERY),
        ],
        responses={200: ListingSerializer(many=True)},
    ),
    retrieve=extend_schema(
        tags=["listings"],
        summary="Retrieve a listing",
        responses={200: ListingSerializer},
    ),
    create=extend_schema(
        tags=["listings"],
        summary="Create a listing",
        description="Owner creates a new listing.",
        request=ListingSerializer,
        responses={
            201: ListingSerializer,
            400: OpenApiTypes.OBJECT,  # validation error schema
            403: OpenApiTypes.OBJECT,  # forbidden / auth required
        },
        examples=[create_example, error_400_example],
    ),
    update=extend_schema(
        tags=["listings"],
        summary="Update a listing",
        request=ListingSerializer,
        responses={200: ListingSerializer, 400: OpenApiTypes.OBJECT, 403: OpenApiTypes.OBJECT},
        examples=[update_example, error_400_example],
    ),
    partial_update=extend_schema(
        tags=["listings"],
        summary="Partially update a listing",
        request=ListingSerializer,
        responses={200: ListingSerializer, 400: OpenApiTypes.OBJECT, 403: OpenApiTypes.OBJECT},
        examples=[update_example, error_400_example],
    ),
    destroy=extend_schema(
        tags=["listings"],
        summary="Delete a listing",
        responses={204: None, 403: OpenApiTypes.OBJECT},
    ),
)
class ListingViewSet(viewsets.ModelViewSet):
    """Manage property listings.
    List/retrieve: public. Create/update/delete: owner only."""
    queryset = Listing.objects.all().select_related("owner")
    serializer_class = ListingSerializer
    permission_classes = [IsOwnerOrReadOnly]

    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = ListingFilter
    search_fields = ["title", "description", "city", "district"]
    ordering_fields = ["price", "created_at"]
    ordering = ["-created_at"]

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)
