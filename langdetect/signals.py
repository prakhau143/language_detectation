"""
LangSense AI - Django Signals
Handles automatic statistics updates and data processing
"""

from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import LanguageDetection, DetectionStats
from django.utils import timezone
from datetime import date


@receiver(post_save, sender=LanguageDetection)
def update_detection_stats(sender, instance, created, **kwargs):
    """
    Update daily detection statistics when a new detection is saved.
    """
    if created:
        today = date.today()
        
        # Get or create today's stats
        stats, created = DetectionStats.objects.get_or_create(date=today)
        
        # Update total count
        stats.total_detections += 1
        
        # Update language-specific counts
        language = instance.detected_language
        if language == 'Hindi':
            stats.hindi_count += 1
        elif language == 'English':
            stats.english_count += 1
        elif language == 'Hinglish':
            stats.hinglish_count += 1
        else:
            stats.unknown_count += 1
        
        # Update average confidence
        total_confidence = stats.avg_confidence * (stats.total_detections - 1) + instance.confidence
        stats.avg_confidence = total_confidence / stats.total_detections
        
        stats.save()
