# apps/listings/admin.py
from django.contrib import admin
from .models import Listing


@admin.register(Listing)
class ListingAdmin(admin.ModelAdmin):
    """Admin UI for Listing."""

    # список объектов
    list_display = (
        "id", "title", "city", "district", "price",
        "rooms", "listing_type_label", "is_active", "owner", "created_at",
    )
    list_display_links = ("id", "title")
    list_editable = ("is_active",)
    list_filter = ("city", "district", "rooms", "listing_type", "is_active", "owner", "created_at")
    search_fields = ("title", "description", "city", "district", "owner__username", "owner__email")
    search_help_text = "Search by title/description/city/district/owner"
    ordering = ("-created_at",)
    list_select_related = ("owner",)
    date_hierarchy = "created_at"
    list_per_page = 50
    save_on_top = True
    autocomplete_fields = ("owner",)

    # форма редактирования
    readonly_fields = ("created_at", "updated_at")
    fieldsets = (
        ("Owner & status", {"fields": ("owner", "is_active")}),
        ("Main", {"fields": ("title", "description")}),
        ("Location", {"fields": ("city", "district")}),
        ("Details", {"fields": ("price", "rooms", "listing_type")}),
        ("Timestamps", {"fields": ("created_at", "updated_at")}),
    )

    # «человеческая» метка типа в списке
    @admin.display(description="Type", ordering="listing_type")
    def listing_type_label(self, obj):
        return obj.get_listing_type_display()
