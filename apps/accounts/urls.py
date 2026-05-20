from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from .views import (
    CustomTokenObtainPairView,
    RegisterView,
    ProfileView,
    PreferencesView,
    update_last_read,
    logout_view,
)

urlpatterns = [
    path('register/', RegisterView.as_view(), name='auth-register'),
    path('login/', CustomTokenObtainPairView.as_view(), name='auth-login'),
    path('refresh/', TokenRefreshView.as_view(), name='auth-token-refresh'),
    path('logout/', logout_view, name='auth-logout'),
    path('profile/', ProfileView.as_view(), name='auth-profile'),
    path('preferences/', PreferencesView.as_view(), name='auth-preferences'),
    path('last-read/', update_last_read, name='auth-last-read'),
]
