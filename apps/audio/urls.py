from django.urls import path
from .views import ReciterListView, verse_audio, surah_audio

urlpatterns = [
    path('reciters/', ReciterListView.as_view(), name='reciter-list'),
    path('surah/<int:surah_number>/', surah_audio, name='surah-audio'),
    path('verse/<int:surah_number>/<int:verse_number>/', verse_audio, name='verse-audio'),
]
