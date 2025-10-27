from django.contrib import admin
from .models import Booking


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'listing', 'tenant', 'start_date', 'end_date',
        'check_in_time', 'status', 'created_at',
    )
    list_filter = ('status', 'start_date', 'end_date', 'listing')
    search_fields = ('listing__title', 'tenant__username', 'tenant__email')
    ordering = ('-created_at',)

    readonly_fields = ('created_at', 'updated_at')
    list_select_related = ('listing', 'tenant')
    date_hierarchy = 'start_date'
    list_per_page = 50
