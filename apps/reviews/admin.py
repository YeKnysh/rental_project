# apps/reviews/admin.py
from django.contrib import admin
from .models import Review


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    """Admin UI for Review."""
    # список
    list_display = ("id", "listing", "author", "rating", "stars", "created_at")
    list_display_links = ("id", "listing")
    list_filter = ("rating", "created_at", "listing")
    search_fields = (
        "author__username",
        "author__email",
        "listing__title",
        "comment",
    )
    ordering = ("-created_at",)
    list_select_related = ("listing", "author")
    date_hierarchy = "created_at"
    list_per_page = 50
    readonly_fields = ("created_at", "updated_at")
    autocomplete_fields = ("listing", "author")

    fieldsets = (
        ("Main", {"fields": ("listing", "author", "rating", "comment")}),
        ("Timestamps", {"fields": ("created_at", "updated_at")}),
    )

    @admin.display(description="★", ordering="rating")
    def stars(self, obj):
        # визуально показать рейтинг звёздами (1–5)
        return "★" * obj.rating + "☆" * (5 - obj.rating)
