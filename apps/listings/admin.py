from django.contrib import admin
from .models import Listing


@admin.register(Listing)
class ListingAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'title', 'city', 'district', 'price',
        'rooms', 'listing_type_label', 'is_active', 'owner', 'created_at',
    )
    list_filter = (
        'city', 'district', 'rooms', 'listing_type', 'is_active', 'owner', 'created_at',
    )
    search_fields = ('title', 'description', 'city', 'district', 'owner__username', 'owner__email')
    ordering = ('-created_at',)

    # качество жизни в админке
    readonly_fields = ('created_at', 'updated_at')
    list_select_related = ('owner',)
    date_hierarchy = 'created_at'
    list_per_page = 50

    # показываем «человеческую» метку типа
    def listing_type_label(self, obj):
        return obj.get_listing_type_display()
    listing_type_label.short_description = 'Type'
    listing_type_label.admin_order_field = 'listing_type'
