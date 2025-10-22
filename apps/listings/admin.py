from django.contrib import admin
from .models import Listing

@admin.register(Listing)
class ListingAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'city', 'district', 'price', 'rooms', 'type', 'owner', 'is_active', 'created_at')
    list_filter = ('city', 'type', 'is_active')
    search_fields = ('title', 'city', 'district')
