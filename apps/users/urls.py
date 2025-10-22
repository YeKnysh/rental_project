from rest_framework.routers import DefaultRouter
from .views import UsersViewSet

app_name = 'apps.users'

router = DefaultRouter()
router.register(r'users', UsersViewSet, basename='users')

urlpatterns = router.urls
