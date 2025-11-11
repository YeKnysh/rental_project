# apps/reviews/views.py
from rest_framework import viewsets, filters
import django_filters.rest_framework as drf_filters

from apps.common.permissions import IsAuthorOrReadOnly
from .models import Review
from .serializers import ReviewSerializer
from drf_spectacular.utils import (
    extend_schema, extend_schema_view, OpenApiParameter
)


class ReviewFilter(drf_filters.FilterSet):
    """Filters for the reviews list."""
    listing = drf_filters.NumberFilter(field_name='listing_id')
    rating_min = drf_filters.NumberFilter(field_name='rating', lookup_expr='gte')
    rating_max = drf_filters.NumberFilter(field_name='rating', lookup_expr='lte')

    class Meta:
        model = Review
        fields = ['listing', 'rating_min', 'rating_max']


@extend_schema_view(
    list=extend_schema(
        tags=["reviews"],
        summary="List reviews",
        parameters=[
            OpenApiParameter(name="listing", type=int, location=OpenApiParameter.QUERY, description="Listing ID"),
            OpenApiParameter(name="rating_min", type=int, location=OpenApiParameter.QUERY, description="Rating ≥"),
            OpenApiParameter(name="rating_max", type=int, location=OpenApiParameter.QUERY, description="Rating ≤"),
            OpenApiParameter(
                name="ordering", type=str, location=OpenApiParameter.QUERY,
                description="created_at, -created_at, rating, -rating"
            ),
        ],
        responses={200: ReviewSerializer(many=True)},
    ),
    retrieve=extend_schema(tags=["reviews"], summary="Retrieve a review", responses={200: ReviewSerializer}),
    create=extend_schema(tags=["reviews"], summary="Create a review", responses={201: ReviewSerializer}),
    update=extend_schema(tags=["reviews"], summary="Update a review", responses={200: ReviewSerializer}),
    partial_update=extend_schema(tags=["reviews"], summary="Partially update a review", responses={200: ReviewSerializer}),
    destroy=extend_schema(tags=["reviews"], summary="Delete a review", responses={204: None}),
)
class ReviewViewSet(viewsets.ModelViewSet):
    """
    Reviews API.

    List/retrieve: public.
    Create/update/delete: only by the authenticated author.
    """
    queryset = Review.objects.all().select_related('author', 'listing')
    serializer_class = ReviewSerializer
    permission_classes = [IsAuthorOrReadOnly]

    filter_backends = [drf_filters.DjangoFilterBackend, filters.OrderingFilter]
    filterset_class = ReviewFilter
    ordering_fields = ['created_at', 'rating']
    ordering = ['-created_at']  # по умолчанию — свежие сначала

    def perform_create(self, serializer):
        """Attach current user as review author on create."""
        serializer.save(author=self.request.user)
