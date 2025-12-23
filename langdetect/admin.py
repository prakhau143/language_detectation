"""
LangSense AI - Django Admin Configuration
Custom admin interface for managing language detection data
"""

from django.contrib import admin
from django.utils.html import format_html
from .models import LanguageDetection, HinglishWord, DetectionStats


@admin.register(LanguageDetection)
class LanguageDetectionAdmin(admin.ModelAdmin):
    """
    Admin interface for language detection history.
    """
    list_display = [
        'input_text_preview', 
        'detected_language', 
        'confidence', 
        'created_at',
        'user_info'
    ]
    list_filter = ['detected_language', 'created_at', 'confidence']
    search_fields = ['input_text', 'detected_language']
    readonly_fields = [
        'hindi_score', 'english_score', 'hinglish_score',
        'hindi_percentage', 'english_percentage', 'hinglish_percentage',
        'created_at'
    ]
    date_hierarchy = 'created_at'
    list_per_page = 50
    
    def input_text_preview(self, obj):
        """Show preview of input text."""
        return obj.input_text[:50] + '...' if len(obj.input_text) > 50 else obj.input_text
    input_text_preview.short_description = 'Input Text'
    
    def user_info(self, obj):
        """Show user information."""
        return obj.user.username if obj.user else 'Anonymous'
    user_info.short_description = 'User'


@admin.register(HinglishWord)
class HinglishWordAdmin(admin.ModelAdmin):
    """
    Admin interface for managing Hinglish words.
    """
    list_display = ['word', 'word_type', 'frequency', 'is_active', 'created_at']
    list_filter = ['word_type', 'is_active', 'created_at']
    search_fields = ['word']
    list_editable = ['is_active', 'frequency']
    actions = ['activate_words', 'deactivate_words']
    
    def activate_words(self, request, queryset):
        """Activate selected Hinglish words."""
        updated = queryset.update(is_active=True)
        self.message_user(request, f'{updated} words activated.')
    activate_words.short_description = 'Activate selected words'
    
    def deactivate_words(self, request, queryset):
        """Deactivate selected Hinglish words."""
        updated = queryset.update(is_active=False)
        self.message_user(request, f'{updated} words deactivated.')
    deactivate_words.short_description = 'Deactivate selected words'


@admin.register(DetectionStats)
class DetectionStatsAdmin(admin.ModelAdmin):
    """
    Admin interface for detection statistics.
    """
    list_display = [
        'date', 'total_detections', 'hindi_count', 'english_count', 
        'hinglish_count', 'avg_confidence'
    ]
    list_filter = ['date']
    date_hierarchy = 'date'
    readonly_fields = [
        'total_detections', 'hindi_count', 'english_count', 
        'hinglish_count', 'unknown_count', 'avg_confidence'
    ]
    
    def has_add_permission(self, request):
        """Disable adding stats manually."""
        return False
