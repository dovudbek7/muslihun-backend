from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ['email', 'username', 'preferred_language', 'reading_mode', 'is_active', 'created_at']
    list_filter = ['preferred_language', 'reading_mode', 'is_active', 'tajweed_mode']
    search_fields = ['email', 'username']
    ordering = ['-created_at']
    fieldsets = BaseUserAdmin.fieldsets + (
        ('Preferences', {
            'fields': (
                'avatar', 'preferred_language', 'reading_mode', 'font_size',
                'tajweed_mode', 'arabic_only', 'zen_mode', 'show_transliteration',
            )
        }),
        ('Reading Progress', {
            'fields': ('last_read_surah', 'last_read_verse', 'last_read_page')
        }),
    )
