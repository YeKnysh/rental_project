from django.contrib import admin
from .models import Review


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('id', 'listing', 'author', 'rating', 'created_at')
    list_filter = ('rating', 'created_at', 'listing')
    search_fields = ('author__username', 'author__email', 'listing__title', 'comment')
    ordering = ('-created_at',)

    readonly_fields = ('created_at', 'updated_at')
    list_select_related = ('listing', 'author')
    date_hierarchy = 'created_at'
    list_per_page = 50
