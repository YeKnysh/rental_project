from rest_framework.routers import DefaultRouter
from .views import ListingViewSet

app_name = "apps.listings"

router = DefaultRouter()
router.register(r'listings', ListingViewSet, basename='listing')

urlpatterns = router.urls
