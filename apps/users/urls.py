# apps/users/urls.py
"""
Users endpoints, mounted under /api/v1/.

Generated routes (via DefaultRouter + ViewSet actions):
  - POST /api/v1/users/register/
  - GET  /api/v1/users/me/
"""
from rest_framework.routers import DefaultRouter
from .views import UsersViewSet

app_name = "apps.users"

router = DefaultRouter()
router.register(r"users", UsersViewSet, basename="users")

urlpatterns = router.urls
