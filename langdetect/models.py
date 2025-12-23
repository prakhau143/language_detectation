"""
LangSense AI - Django Models
Handles detection history and admin panel management
"""

from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class LanguageDetection(models.Model):
    """
    Model to store language detection history and results.
    """
    LANGUAGE_CHOICES = [
        ('Hindi', 'Hindi'),
        ('English', 'English'),
        ('Hinglish', 'Hinglish'),
        ('Unknown', 'Unknown'),
    ]
    
    # Input text
    input_text = models.TextField()
    
    # Detection results
    detected_language = models.CharField(max_length=20, choices=LANGUAGE_CHOICES)
    confidence = models.FloatField()
    
    # Individual scores
    hindi_score = models.FloatField(default=0.0)
    english_score = models.FloatField(default=0.0)
    hinglish_score = models.FloatField(default=0.0)
    
    # Breakdown percentages
    hindi_percentage = models.FloatField(default=0.0)
    english_percentage = models.FloatField(default=0.0)
    hinglish_percentage = models.FloatField(default=0.0)
    
    # Metadata
    created_at = models.DateTimeField(default=timezone.now)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Language Detection'
        verbose_name_plural = 'Language Detections'
    
    def __str__(self):
        return f"{self.detected_language} ({self.confidence}%) - {self.created_at.strftime('%Y-%m-%d %H:%M')}"


class HinglishWord(models.Model):
    """
    Model to manage Hinglish words dynamically through admin panel.
    """
    WORD_TYPES = [
        ('verb', 'Verb'),
        ('noun', 'Noun'),
        ('adjective', 'Adjective'),
        ('particle', 'Particle'),
        ('expression', 'Expression'),
    ]
    
    word = models.CharField(max_length=100, unique=True)
    word_type = models.CharField(max_length=20, choices=WORD_TYPES)
    frequency = models.IntegerField(default=1)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-frequency', 'word']
        verbose_name = 'Hinglish Word'
        verbose_name_plural = 'Hinglish Words'
    
    def __str__(self):
        return f"{self.word} ({self.word_type})"


class DetectionStats(models.Model):
    """
    Model to store aggregated detection statistics.
    """
    date = models.DateField(unique=True)
    total_detections = models.IntegerField(default=0, null=False, blank=False)
    hindi_count = models.IntegerField(default=0, null=False, blank=False)
    english_count = models.IntegerField(default=0, null=False, blank=False)
    hinglish_count = models.IntegerField(default=0, null=False, blank=False)
    unknown_count = models.IntegerField(default=0, null=False, blank=False)
    avg_confidence = models.FloatField(default=0.0, null=False, blank=False)
    
    class Meta:
        ordering = ['-date']
        verbose_name = 'Detection Statistics'
        verbose_name_plural = 'Detection Statistics'
    
    def __str__(self):
        return f"Stats for {self.date}: {self.total_detections} detections"
