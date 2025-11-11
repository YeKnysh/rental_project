# rental_project/redirects.py
from django.views.generic import RedirectView
from django.urls import reverse_lazy, reverse
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin

class HomeRedirectView(RedirectView):
    """Корень сайта → Swagger UI (/api/docs/)."""
    permanent = False
    def get_redirect_url(self, *args, **kwargs):
        return reverse_lazy("swagger-ui")

class SwaggerShortcutRedirect(RedirectView):
    """/docs и /swagger → /api/docs/"""
    permanent = False
    url = "/api/docs/"

class SchemaRedirect(RedirectView):
    """/openapi и /schema → /api/schema/"""
    permanent = False
    url = "/api/schema/"

class RedocRedirect(RedirectView):
    """/redoc → /api/redoc/"""
    permanent = False
    url = "/api/redoc/"

class AdminShortcutRedirect(RedirectView):
    """/admin (без слэша) → /admin/"""
    permanent = False
    url = "/admin/"

class AdminMeRedirectView(LoginRequiredMixin, UserPassesTestMixin, RedirectView):
    """
    /admin/me/ → страница изменения текущего пользователя в админке.
    Требуются права staff/superuser. Иначе — редирект на /admin/login/.
    """
    permanent = False
    login_url = "/admin/login/"

    def test_func(self):
        return bool(self.request.user and self.request.user.is_staff)

    def get_redirect_url(self, *args, **kwargs):
        u = self.request.user
        # admin namespace строится из метаданных модели пользователя
        return reverse(f"admin:{u._meta.app_label}_{u._meta.model_name}_change", args=[u.pk])
