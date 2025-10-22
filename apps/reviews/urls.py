from rest_framework.routers import DefaultRouter
from .views import ReviewViewSet

app_name = "apps.reviews"

router = DefaultRouter()
router.register(r'reviews', ReviewViewSet, basename='review')

urlpatterns = router.urls
