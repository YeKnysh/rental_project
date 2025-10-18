from rest_framework import viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Count

from django.contrib.auth import get_user_model
from apps.listings.models import Listing
from apps.bookings.models import Booking
from apps.reviews.models import Review


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
        qs = (Booking.objects
              .values('status')
              .annotate(count=Count('id'))
              .order_by('-count'))
        return Response(list(qs))

    @action(detail=False, methods=['get'])
    def top_cities(self, request):
        limit = int(request.query_params.get('limit', 5))
        qs = (Listing.objects
              .values('city')
              .annotate(count=Count('id'))
              .order_by('-count')[:limit])
        return Response(list(qs))

    @action(detail=False, methods=['get'], permission_classes=[permissions.IsAuthenticated])
    def owner_dashboard(self, request):
        my_listings = Listing.objects.filter(owner=request.user)
        bookings = Booking.objects.filter(listing__in=my_listings)
        data = {
            'my_listings': my_listings.count(),
            'bookings_total': bookings.count(),
            'pending': bookings.filter(status='pending').count(),
            'confirmed': bookings.filter(status='confirmed').count(),
            'declined': bookings.filter(status='declined').count(),
            'cancelled': bookings.filter(status='cancelled').count(),
        }
        return Response(data)
