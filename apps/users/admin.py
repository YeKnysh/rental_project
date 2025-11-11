# apps/users/admin.py
from typing import List, Tuple

from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

User = get_user_model()


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """
    Admin UI for custom User model.
    — Динамически добавляет поля nickname/role, если они реально есть в модели.
    — Удобные фильтры, поиск по email/username.
    """

    # --- dynamic list_display ---
    def get_list_display(self, request) -> Tuple[str, ...]:
        base: List[str] = ["id", "username", "email"]
        # include optional fields if present
        if hasattr(User, "nickname"):
            base.append("nickname")
        if hasattr(User, "role"):
            base.append("role")
        base += ["is_staff", "is_active", "is_superuser"]
        if hasattr(User, "date_joined"):
            base.append("date_joined")
        return tuple(base)

    list_display_links = ("id", "username")
    search_fields = ("username", "email")

    # filters
    def get_list_filter(self, request):
        base = ["is_staff", "is_active", "is_superuser", "groups"]
        if hasattr(User, "role"):
            base.append("role")
        return base

    list_per_page = 50

    # ordering
    def get_ordering(self, request):
        return ("-date_joined",) if hasattr(User, "date_joined") else ("-id",)

    # readonly
    def get_readonly_fields(self, request, obj=None):
        ro = list(super().get_readonly_fields(request, obj))
        for f in ("last_login", "date_joined"):
            if hasattr(User, f) and f not in ro:
                ro.append(f)
        return tuple(ro)

    # edit form fieldsets
    def get_fieldsets(self, request, obj=None):
        fieldsets = list(super().get_fieldsets(request, obj))

        # Append "Extra" only if at least one of optional fields exists
        extra_fields = []
        if hasattr(User, "nickname"):
            extra_fields.append("nickname")
        if hasattr(User, "role"):
            extra_fields.append("role")

        if extra_fields:
            fieldsets.append(("Extra", {"fields": tuple(extra_fields)}))

        return tuple(fieldsets)

    # create form fieldsets (make sure email is visible at creation)
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": ("username", "email", "password1", "password2"),
            },
        ),
    )

    # relations
    filter_horizontal = ("groups", "user_permissions")
