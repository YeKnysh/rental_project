# rental_project/urls.py
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include
from django.views.generic.base import RedirectView
from rental_project import settings

from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularSwaggerView,
    SpectacularRedocView,
)

from rental_project import settings


api_v1 = [
    path('api/v1/', include('apps.users.urls')),
    path('api/v1/', include('apps.listings.urls')),
    path('api/v1/', include('apps.bookings.urls')),
    path('api/v1/', include('apps.booking_statistics.urls')),
    path('api/v1/', include('apps.reviews.urls')),
]

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api-auth/', include('rest_framework.urls')),

    # OpenAPI schema & docs
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),

    # root redirect
    path('', RedirectView.as_view(url='/admin/', permanent=False)),
] + api_v1

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
