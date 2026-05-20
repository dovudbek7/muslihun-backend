from django.urls import path
from .views import (
    SurahListView,
    SurahDetailView,
    VerseDetailView,
    PageView,
    JuzView,
    TafsirView,
    surah_meta,
    navigation_data,
)

urlpatterns = [
    path('surahs/', SurahListView.as_view(), name='surah-list'),
    path('surahs/<int:surah_number>/', SurahDetailView.as_view(), name='surah-detail'),
    path('surahs/<int:surah_number>/verses/<int:verse_number>/', VerseDetailView.as_view(), name='verse-detail'),
    path('surahs/<int:surah_number>/verses/<int:verse_number>/tafsir/', TafsirView.as_view(), name='verse-tafsir'),
    path('pages/<int:page_number>/', PageView.as_view(), name='page-detail'),
    path('juz/<int:juz_number>/', JuzView.as_view(), name='juz-detail'),
    path('meta/surahs/', surah_meta, name='surah-meta'),
    path('navigation/', navigation_data, name='navigation-data'),
]
