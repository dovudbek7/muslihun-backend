from django.contrib import admin
from .models import HifzSession, HifzProgress, ErrorLog


@admin.register(HifzSession)
class HifzSessionAdmin(admin.ModelAdmin):
    list_display = ['user', 'surah', 'mode', 'started_at', 'ended_at', 'verses_attempted', 'verses_correct']
    list_filter = ['mode']
    raw_id_fields = ['user', 'surah']


@admin.register(HifzProgress)
class HifzProgressAdmin(admin.ModelAdmin):
    list_display = ['user', 'verse', 'status', 'next_review', 'total_reviews', 'total_errors']
    list_filter = ['status']
    raw_id_fields = ['user', 'verse']


@admin.register(ErrorLog)
class ErrorLogAdmin(admin.ModelAdmin):
    list_display = ['user', 'verse', 'error_type', 'created_at']
    list_filter = ['error_type']
    raw_id_fields = ['user', 'verse']
