from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth import get_user_model

User = get_user_model()

@admin.register(User)
class UserAdmin(BaseUserAdmin):
    # показывать в списке
    list_display = ('id', 'username', 'email', 'is_staff', 'is_active', 'is_superuser')
    search_fields = ('username', 'email')

    fieldsets = BaseUserAdmin.fieldsets + (
        ('Extra', {'fields': ('nickname', 'role')}),
    )
