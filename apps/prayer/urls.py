from django.urls import path
from .views import prayer_times, next_prayer_countdown

urlpatterns = [
    path('times/', prayer_times, name='prayer-times'),
    path('next/', next_prayer_countdown, name='prayer-next'),
]
