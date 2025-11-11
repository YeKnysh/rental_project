# apps/bookings/admin.py
from django.contrib import admin
from .models import Booking
from .choices import BookingStatus


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    """Admin UI for Booking."""

    # список
    list_display = (
        "id", "listing", "tenant",
        "start_date", "end_date", "check_in_time",
        "status_label", "created_at",
    )
    list_display_links = ("id", "listing")
    list_filter = ("status", "start_date", "end_date", "listing")
    search_fields = (
        "listing__title",
        "listing__city",
        "tenant__username",
        "tenant__email",
    )
    search_help_text = "Search by listing title/city or tenant username/email"
    ordering = ("-created_at",)
    list_select_related = ("listing", "tenant")
    date_hierarchy = "start_date"
    list_per_page = 50
    autocomplete_fields = ("listing", "tenant")
    readonly_fields = ("created_at", "updated_at")

    fieldsets = (
        ("Relations & status", {"fields": ("listing", "tenant", "status")}),
        ("Dates", {"fields": ("start_date", "end_date", "check_in_time")}),
        ("Timestamps", {"fields": ("created_at", "updated_at")}),
    )

    # человекочитаемый статус
    @admin.display(description="Status", ordering="status")
    def status_label(self, obj):
        return obj.get_status_display()

    # удобные экшены смены статуса
    @admin.action(description="Mark selected as CONFIRMED")
    def action_confirm(self, request, queryset):
        updated = queryset.update(status=BookingStatus.CONFIRMED)
        self.message_user(request, f"Updated {updated} bookings to CONFIRMED.")

    @admin.action(description="Mark selected as DECLINED")
    def action_decline(self, request, queryset):
        updated = queryset.update(status=BookingStatus.DECLINED)
        self.message_user(request, f"Updated {updated} bookings to DECLINED.")

    @admin.action(description="Mark selected as CANCELLED")
    def action_cancel(self, request, queryset):
        updated = queryset.update(status=BookingStatus.CANCELLED)
        self.message_user(request, f"Updated {updated} bookings to CANCELLED.")

    actions = ("action_confirm", "action_decline", "action_cancel")
