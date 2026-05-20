from django.urls import path
from .views import (
    SessionListCreateView,
    ProgressListView,
    ErrorLogListCreateView,
    end_session,
    due_verses,
    weak_verses,
    submit_review,
    my_errors_stats,
    surah_progress,
    hifz_dashboard,
    transcribe_verse,
)

urlpatterns = [
    path('sessions/', SessionListCreateView.as_view(), name='hifz-sessions'),
    path('sessions/<int:session_id>/end/', end_session, name='hifz-session-end'),
    path('progress/', ProgressListView.as_view(), name='hifz-progress'),
    path('progress/due/', due_verses, name='hifz-due-verses'),
    path('progress/weak/', weak_verses, name='hifz-weak-verses'),
    path('progress/review/', submit_review, name='hifz-review'),
    path('progress/surah/<int:surah_number>/', surah_progress, name='hifz-surah-progress'),
    path('errors/', ErrorLogListCreateView.as_view(), name='hifz-errors'),
    path('errors/stats/', my_errors_stats, name='hifz-error-stats'),
    path('dashboard/', hifz_dashboard, name='hifz-dashboard'),
    path('transcribe/', transcribe_verse, name='hifz-transcribe'),
]
