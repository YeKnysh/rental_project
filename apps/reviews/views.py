from rest_framework import viewsets, permissions, filters
import django_filters.rest_framework as drf_filters

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


class IsAuthorOrReadOnly(permissions.BasePermission):
    """
    Read for everyone.
    Write only for authenticated users.
    Object-level: only the author can modify their own review.
    """
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user and request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.author_id == getattr(request.user, 'id', None)


@extend_schema_view(
    list=extend_schema(
        tags=["reviews"],
        summary="List reviews",
        parameters=[
            OpenApiParameter(name="listing", type=int, location=OpenApiParameter.QUERY, description="Listing ID"),
            OpenApiParameter(name="rating_min", type=int, location=OpenApiParameter.QUERY, description="Rating ≥"),
            OpenApiParameter(name="rating_max", type=int, location=OpenApiParameter.QUERY, description="Rating ≤"),
            OpenApiParameter(name="ordering", type=str, location=OpenApiParameter.QUERY, description="created_at, -created_at, rating, -rating"),
        ],
    ),
    retrieve=extend_schema(tags=["reviews"], summary="Retrieve a review"),
    create=extend_schema(tags=["reviews"], summary="Create a review"),
    update=extend_schema(tags=["reviews"], summary="Update a review"),
    partial_update=extend_schema(tags=["reviews"], summary="Partially update a review"),
    destroy=extend_schema(tags=["reviews"], summary="Delete a review"),
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

    def perform_create(self, serializer):
        # set author to current user
        serializer.save(author=self.request.user)
