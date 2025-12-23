"""
LangSense AI - Django URL Configuration for langdetect app
"""

from django.urls import path
from .views import LanguageDetectionAPI, DetectionHistoryAPI, StatisticsAPI, test_detection

urlpatterns = [
    path('detect-language/', LanguageDetectionAPI.as_view(), name='detect-language'),
    path('detection-history/', DetectionHistoryAPI.as_view(), name='detection-history'),
    path('statistics/', StatisticsAPI.as_view(), name='statistics'),
    path('test-detection/', test_detection, name='test-detection'),
]
