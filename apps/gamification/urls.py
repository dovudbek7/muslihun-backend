from django.urls import path
from .views import (
    streak_view,
    TasbihDhikrListView,
    TasbihSessionListCreateView,
    tasbih_increment,
    AchievementListView,
    UserAchievementListView,
    gamification_dashboard,
)

urlpatterns = [
    path('streak/', streak_view, name='streak'),
    path('tasbih/dhikr/', TasbihDhikrListView.as_view(), name='tasbih-dhikr-list'),
    path('tasbih/sessions/', TasbihSessionListCreateView.as_view(), name='tasbih-sessions'),
    path('tasbih/sessions/<int:session_id>/increment/', tasbih_increment, name='tasbih-increment'),
    path('achievements/', AchievementListView.as_view(), name='achievements'),
    path('achievements/mine/', UserAchievementListView.as_view(), name='my-achievements'),
    path('dashboard/', gamification_dashboard, name='gamification-dashboard'),
]
