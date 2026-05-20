from django.contrib import admin
from .models import Reciter, AudioEdition, UserPlaybackHistory


@admin.register(Reciter)
class ReciterAdmin(admin.ModelAdmin):
    list_display = ['name_en', 'identifier', 'style', 'bitrate', 'is_active', 'display_order']
    list_filter = ['style', 'is_active']
    search_fields = ['name_en', 'identifier']


@admin.register(AudioEdition)
class AudioEditionAdmin(admin.ModelAdmin):
    list_display = ['reciter', 'surah', 'duration_seconds']
    raw_id_fields = ['reciter', 'surah']
