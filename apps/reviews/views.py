from rest_framework import viewsets, permissions, filters
import django_filters.rest_framework as drf_filters

from .models import Review
from .serializers import ReviewSerializer

class ReviewFilter(drf_filters.FilterSet):
    listing = drf_filters.NumberFilter(field_name='listing_id')
    rating_min = drf_filters.NumberFilter(field_name='rating', lookup_expr='gte')
    rating_max = drf_filters.NumberFilter(field_name='rating', lookup_expr='lte')

    class Meta:
        model = Review
        fields = ['listing', 'rating_min', 'rating_max']


class IsAuthorOrReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user and request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.author_id == getattr(request.user, 'id', None)


class ReviewViewSet(viewsets.ModelViewSet):
    queryset = Review.objects.all().select_related('author', 'listing')
    serializer_class = ReviewSerializer
    permission_classes = [IsAuthorOrReadOnly]
    filter_backends = [drf_filters.DjangoFilterBackend, filters.OrderingFilter]
    filterset_class = ReviewFilter
    ordering_fields = ['created_at', 'rating']

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)
