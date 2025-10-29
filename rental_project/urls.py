# rental_project/urls.py
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include

from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularSwaggerView,
    SpectacularRedocView,
)

from rental_project import settings
from rental_project.redirects import (
    HomeRedirectView,
    SwaggerShortcutRedirect,
    SchemaRedirect,
    RedocRedirect,
    AdminShortcutRedirect,
    AdminMeRedirectView,     # ← добавили
)

api_v1 = [
    path("api/v1/", include("apps.users.urls")),
    path("api/v1/", include("apps.listings.urls")),
    path("api/v1/", include("apps.bookings.urls")),
    path("api/v1/", include("apps.booking_statistics.urls")),
    path("api/v1/", include("apps.reviews.urls")),
]

urlpatterns = [
    # Админка
    path("admin/", admin.site.urls),
    path("admin", AdminShortcutRedirect.as_view(), name="admin-short"),
    path("admin/me/", AdminMeRedirectView.as_view(), name="admin-me"),  # ← новый удобный редирект

    # DRF login/logout (сессии)
    path("api-auth/", include("rest_framework.urls")),

    # OpenAPI schema & docs
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path("api/docs/", SpectacularSwaggerView.as_view(url_name="schema"), name="swagger-ui"),
    path("api/redoc/", SpectacularRedocView.as_view(url_name="schema"), name="redoc"),

    # Быстрые сокращения и корневой редирект
    path("", HomeRedirectView.as_view(), name="home"),
    path("docs", SwaggerShortcutRedirect.as_view(), name="docs-short"),
    path("swagger", SwaggerShortcutRedirect.as_view(), name="swagger-short"),
    path("openapi", SchemaRedirect.as_view(), name="openapi-short"),
    path("schema", SchemaRedirect.as_view(), name="schema-short"),
    path("redoc", RedocRedirect.as_view(), name="redoc-short"),
] + api_v1

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
