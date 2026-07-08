from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, UserSettings

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'full_name', 'role', 'mobile', 'is_active')
    list_filter = ('role', 'is_active')
    search_fields = ('username', 'email', 'full_name', 'mobile')
    fieldsets = UserAdmin.fieldsets + (
        ('Additional Info', {
            'fields': ('full_name', 'role', 'mobile', 'profile_picture')
        }),
    )

@admin.register(UserSettings)
class UserSettingsAdmin(admin.ModelAdmin):
    list_display = ('user', 'theme', 'default_language', 'email_notifications', 'public_profile')
    list_filter = ('theme', 'default_language', 'public_profile')
    search_fields = ('user__username', 'user__email')
