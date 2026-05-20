from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView, SpectacularRedocView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),

    path('api/v1/auth/', include('apps.accounts.urls')),
    path('api/v1/quran/', include('apps.quran.urls')),
    path('api/v1/search/', include('apps.search.urls')),
    path('api/v1/audio/', include('apps.audio.urls')),
    path('api/v1/hifz/', include('apps.hifz.urls')),
    path('api/v1/prayer/', include('apps.prayer.urls')),
    path('api/v1/gamification/', include('apps.gamification.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
