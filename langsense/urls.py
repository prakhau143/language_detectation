"""
LangSense AI - Django URL Configuration
Main URL routing for the application
"""

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import TemplateView

from langdetect.views import (
    LanguageDetectionAPI, 
    DetectionHistoryAPI, 
    StatisticsAPI, 
    test_detection
)

urlpatterns = [
    # Admin panel
    path('admin/', admin.site.urls),
    
    # API endpoints
    path('api/detect-language/', LanguageDetectionAPI.as_view(), name='detect-language'),
    path('api/detection-history/', DetectionHistoryAPI.as_view(), name='detection-history'),
    path('api/statistics/', StatisticsAPI.as_view(), name='statistics'),
    path('api/test-detection/', test_detection, name='test-detection'),
    
    # Frontend routes
    path('', TemplateView.as_view(template_name='index.html'), name='home'),
    path('history/', TemplateView.as_view(template_name='history.html'), name='history'),
    path('statistics/', TemplateView.as_view(template_name='statistics.html'), name='statistics'),
    path('about/', TemplateView.as_view(template_name='about.html'), name='about'),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
