from django.contrib import admin
from .models import Surah, Verse, Translation, Tafsir, PageMapping


@admin.register(Surah)
class SurahAdmin(admin.ModelAdmin):
    list_display = ['number', 'name_arabic', 'name_transliteration', 'revelation_type', 'total_verses', 'page_start']
    list_filter = ['revelation_type']
    search_fields = ['name_transliteration', 'name_en', 'name_arabic']
    ordering = ['number']


class TranslationInline(admin.TabularInline):
    model = Translation
    extra = 0
    fields = ['language', 'text', 'source']


@admin.register(Verse)
class VerseAdmin(admin.ModelAdmin):
    list_display = ['surah', 'number', 'page_number', 'juz_number', 'is_sajda']
    list_filter = ['juz_number', 'is_sajda']
    search_fields = ['surah__name_transliteration', 'text_arabic']
    inlines = [TranslationInline]
    raw_id_fields = ['surah']


@admin.register(Translation)
class TranslationAdmin(admin.ModelAdmin):
    list_display = ['verse', 'language', 'source']
    list_filter = ['language', 'source']
    raw_id_fields = ['verse']


@admin.register(Tafsir)
class TafsirAdmin(admin.ModelAdmin):
    list_display = ['verse', 'language', 'source']
    list_filter = ['language']
    raw_id_fields = ['verse']


@admin.register(PageMapping)
class PageMappingAdmin(admin.ModelAdmin):
    list_display = ['page_number', 'surah_start', 'verse_start', 'juz_number']
    ordering = ['page_number']
