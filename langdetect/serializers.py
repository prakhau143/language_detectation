"""
LangSense AI - Django Serializers
Serializers for API data validation and transformation
"""

from rest_framework import serializers
from .models import LanguageDetection, HinglishWord


class LanguageDetectionSerializer(serializers.ModelSerializer):
    """
    Serializer for language detection results.
    """
    class Meta:
        model = LanguageDetection
        fields = [
            'id', 'input_text', 'detected_language', 'confidence',
            'hindi_score', 'english_score', 'hinglish_score',
            'hindi_percentage', 'english_percentage', 'hinglish_percentage',
            'created_at'
        ]
        read_only_fields = [
            'id', 'hindi_score', 'english_score', 'hinglish_score',
            'hindi_percentage', 'english_percentage', 'hinglish_percentage',
            'created_at'
        ]


class LanguageDetectionRequestSerializer(serializers.Serializer):
    """
    Serializer for language detection request validation.
    """
    text = serializers.CharField(
        max_length=10000,
        help_text="Text to analyze for language detection"
    )
    
    def validate_text(self, value):
        """Validate input text."""
        if not value or not value.strip():
            raise serializers.ValidationError("Text cannot be empty.")
        return value.strip()


class HinglishWordSerializer(serializers.ModelSerializer):
    """
    Serializer for Hinglish word management.
    """
    class Meta:
        model = HinglishWord
        fields = ['id', 'word', 'word_type', 'frequency', 'is_active', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']
