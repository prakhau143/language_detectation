"""
LangSense AI - Django API Views
REST API endpoints for language detection
"""

from rest_framework import status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.parsers import JSONParser
from django.utils import timezone
from django.contrib.auth.models import User
from django.db.models import Count, Avg
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
import json
from rest_framework.authentication import BaseAuthentication

from .models import LanguageDetection, HinglishWord, DetectionStats
from .serializers import (
    LanguageDetectionSerializer, 
    LanguageDetectionRequestSerializer,
    HinglishWordSerializer
)
from .language_engine import detector

class CsrfExemptSessionAuthentication(BaseAuthentication):
    def authenticate(self, request):
        return None

@method_decorator(csrf_exempt, name='dispatch')
class LanguageDetectionAPI(APIView):
    authentication_classes = [CsrfExemptSessionAuthentication]
    permission_classes = [permissions.AllowAny]
    parser_classes = [JSONParser]
    
    def post(self, request):
        print("DEBUG: POST request received")
        print("DEBUG: request.data =", request.data)

        serializer = LanguageDetectionRequestSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=400)

        text = serializer.validated_data["text"]

        detection_result = detector.detect_language(text)

        record = LanguageDetection.objects.create(
            input_text=text[:10000],
            detected_language=detection_result["language"],
            confidence=detection_result["confidence"],
            hindi_score=detection_result["hindi_score"],
            english_score=detection_result["english_score"],
            hinglish_score=detection_result["hinglish_score"],
            hindi_percentage=detection_result["breakdown"]["hindi_percentage"],
            english_percentage=detection_result["breakdown"]["english_percentage"],
            hinglish_percentage=detection_result["breakdown"]["hinglish_percentage"],
            ip_address=request.META.get("REMOTE_ADDR"),
            user_agent=request.META.get("HTTP_USER_AGENT", "")[:500],
        )

        self.update_daily_stats(
            detection_result["language"],
            detection_result["confidence"]
        )

        return Response({
            "success": True,
            "data": {
                "detected_language": detection_result["language"],
                "confidence": detection_result["confidence"],
                "breakdown": detection_result["breakdown"]
            }
        })
    
    def get_client_ip(self, request):
        """Extract client IP address."""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip
    
    def update_daily_stats(self, language, confidence):
        """Update daily detection statistics."""
        today = timezone.now().date()
        
        stats, created = DetectionStats.objects.get_or_create(date=today)
        
        # Initialize counters if they are None
        if stats.total_detections is None:
            stats.total_detections = 0
        if stats.avg_confidence is None:
            stats.avg_confidence = 0.0
        if stats.hindi_count is None:
            stats.hindi_count = 0
        if stats.english_count is None:
            stats.english_count = 0
        if stats.hinglish_count is None:
            stats.hinglish_count = 0
        if stats.unknown_count is None:
            stats.unknown_count = 0
        
        stats.total_detections += 1
        
        if language == 'Hindi':
            stats.hindi_count += 1
        elif language == 'English':
            stats.english_count += 1
        elif language == 'Hinglish':
            stats.hinglish_count += 1
        else:
            stats.unknown_count += 1
        
        # Update average confidence safely
        if stats.total_detections > 0:
            total_confidence = (stats.avg_confidence * (stats.total_detections - 1)) + confidence
            stats.avg_confidence = total_confidence / stats.total_detections
        
        stats.save()


class DetectionHistoryAPI(APIView):
    """
    API endpoint for retrieving detection history.
    GET /api/detection-history
    """
    permission_classes = [permissions.AllowAny]
    
    def get(self, request):
        """
        Retrieve detection history with pagination.
        """
        try:
            # Get query parameters
            page = int(request.GET.get('page', 1))
            per_page = min(int(request.GET.get('per_page', 20)), 100)
            language_filter = request.GET.get('language')
            
            # Build queryset
            queryset = LanguageDetection.objects.all()
            
            if language_filter:
                queryset = queryset.filter(detected_language=language_filter)
            
            # Paginate results
            start = (page - 1) * per_page
            end = start + per_page
            
            detections = queryset[start:end]
            serializer = LanguageDetectionSerializer(detections, many=True)
            
            # Get total count
            total_count = queryset.count()
            total_pages = (total_count + per_page - 1) // per_page
            
            return Response({
                'success': True,
                'data': {
                    'detections': serializer.data,
                    'pagination': {
                        'current_page': page,
                        'per_page': per_page,
                        'total_count': total_count,
                        'total_pages': total_pages,
                        'has_next': page < total_pages,
                        'has_previous': page > 1
                    }
                }
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response({
                'error': 'Internal server error',
                'message': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class StatisticsAPI(APIView):
    """
    API endpoint for detection statistics.
    GET /api/statistics
    """
    permission_classes = [permissions.AllowAny]
    
    def get(self, request):
        """
        Get detection statistics and analytics.
        """
        try:
            # Get overall statistics
            total_detections = LanguageDetection.objects.count()
            
            language_counts = LanguageDetection.objects.values('detected_language').annotate(
                count=Count('detected_language')
            )
            
            # Calculate percentages
            language_stats = {}
            for item in language_counts:
                lang = item['detected_language']
                count = item['count']
                percentage = (count / total_detections * 100) if total_detections > 0 else 0
                language_stats[lang] = {
                    'count': count,
                    'percentage': round(percentage, 2)
                }
            
            # Get recent activity (last 7 days)
            from django.utils import timezone
            from datetime import timedelta
            
            recent_date = timezone.now().date() - timedelta(days=7)
            recent_detections = LanguageDetection.objects.filter(
                created_at__date__gte=recent_date
            ).values('detected_language', 'created_at__date').annotate(
                count=Count('id')
            )
            
            # Get confidence distribution
            confidence_ranges = {
                '90-100%': LanguageDetection.objects.filter(confidence__gte=90).count(),
                '80-89%': LanguageDetection.objects.filter(confidence__gte=80, confidence__lt=90).count(),
                '70-79%': LanguageDetection.objects.filter(confidence__gte=70, confidence__lt=80).count(),
                '60-69%': LanguageDetection.objects.filter(confidence__gte=60, confidence__lt=70).count(),
                'Below 60%': LanguageDetection.objects.filter(confidence__lt=60).count(),
            }
            
            return Response({
                'success': True,
                'data': {
                    'total_detections': total_detections,
                    'language_distribution': language_stats,
                    'recent_activity': list(recent_detections),
                    'confidence_distribution': confidence_ranges,
                    'avg_confidence': LanguageDetection.objects.aggregate(
                        avg_confidence=Avg('confidence')
                    )['avg_confidence'] or 0
                }
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response({
                'error': 'Internal server error',
                'message': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([permissions.AllowAny])
@csrf_exempt
def test_detection(request):
    """
    Test endpoint with predefined test cases.
    """
    test_cases = [
        {'text': 'I am going to office', 'expected': 'English'},
        {'text': 'मैं आज ऑफिस जा रहा हूँ', 'expected': 'Hindi'},
        {'text': 'Main office ja raha hoon', 'expected': 'Hinglish'},
        {'text': 'Kal meeting hai at office', 'expected': 'Hinglish'},
        {'text': 'Hello, how are you?', 'expected': 'English'},
        {'text': 'आज बहुत अच्छा दिन है', 'expected': 'Hindi'},
    ]
    
    results = []
    for test_case in test_cases:
        result = detector.detect_language(test_case['text'])
        results.append({
            'input': test_case['text'],
            'expected': test_case['expected'],
            'detected': result['language'],
            'confidence': result['confidence'],
            'correct': result['language'] == test_case['expected']
        })
    
    accuracy = sum(1 for r in results if r['correct']) / len(results) * 100
    
    return Response({
        'success': True,
        'data': {
            'test_results': results,
            'accuracy': round(accuracy, 2),
            'total_tests': len(results)
        }
    })
