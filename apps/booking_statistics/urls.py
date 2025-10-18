from rest_framework.routers import DefaultRouter
from .views import StatsViewSet

app_name = "apps.booking_statistics"

router = DefaultRouter()
router.register(r'statistics', StatsViewSet, basename='statistics')

urlpatterns = router.urls
