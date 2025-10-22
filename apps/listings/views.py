from rest_framework import viewsets, filters
import django_filters.rest_framework as drf_filters

from .models import Listing
from .serializers import ListingSerializer
from apps.common.permissions import IsOwnerOrReadOnly
from drf_spectacular.utils import (
    extend_schema, extend_schema_view, OpenApiParameter
)


class ListingFilter(drf_filters.FilterSet):
    price_min = drf_filters.NumberFilter(field_name='price', lookup_expr='gte')
    price_max = drf_filters.NumberFilter(field_name='price', lookup_expr='lte')
    city = drf_filters.CharFilter(field_name='city', lookup_expr='iexact')
    district = drf_filters.CharFilter(field_name='district', lookup_expr='iexact')
    rooms = drf_filters.NumberFilter(field_name='rooms', lookup_expr='exact')
    type = drf_filters.CharFilter(field_name='type', lookup_expr='exact')

    class Meta:
        model = Listing
        fields = ['city', 'district', 'rooms', 'type', 'price_min', 'price_max']


@extend_schema_view(
    list=extend_schema(
        tags=["listings"],
        summary="List listings",
        parameters=[
            OpenApiParameter(name="city", description="City (case-insensitive)", required=False, type=str, location=OpenApiParameter.QUERY),
            OpenApiParameter(name="district", description="District (case-insensitive)", required=False, type=str, location=OpenApiParameter.QUERY),
            OpenApiParameter(name="rooms", description="Exact rooms", required=False, type=int, location=OpenApiParameter.QUERY),
            OpenApiParameter(name="type", description="Listing type", required=False, type=str, location=OpenApiParameter.QUERY),
            OpenApiParameter(name="price_min", description="Price ≥", required=False, type=float, location=OpenApiParameter.QUERY),
            OpenApiParameter(name="price_max", description="Price ≤", required=False, type=float, location=OpenApiParameter.QUERY),
            OpenApiParameter(name="search", description="Search in title/description/city/district", required=False, type=str, location=OpenApiParameter.QUERY),
            OpenApiParameter(name="ordering", description="price, -price, created_at, -created_at", required=False, type=str, location=OpenApiParameter.QUERY),
        ],
    ),
    retrieve=extend_schema(tags=["listings"], summary="Retrieve a listing"),
    create=extend_schema(tags=["listings"], summary="Create a listing"),
    update=extend_schema(tags=["listings"], summary="Update a listing"),
    partial_update=extend_schema(tags=["listings"], summary="Partially update a listing"),
    destroy=extend_schema(tags=["listings"], summary="Delete a listing"),
)
class ListingViewSet(viewsets.ModelViewSet):
    """
    Listings API.

    List/retrieve: public.
    Create/update/delete: only by the owner.
    """
    queryset = Listing.objects.all().select_related('owner')
    serializer_class = ListingSerializer
    permission_classes = [IsOwnerOrReadOnly]
    filter_backends = [drf_filters.DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = ListingFilter
    search_fields = ['title', 'description', 'city', 'district']
    ordering_fields = ['price', 'created_at']

    def perform_create(self, serializer):
        # set owner to current user
        serializer.save(owner=self.request.user)
