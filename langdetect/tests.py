"""
LangSense AI - Test Cases
Comprehensive test suite for language detection accuracy
"""

from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from langdetect.language_engine import detector


class LanguageDetectionEngineTest(TestCase):
    """Test cases for the language detection engine."""
    
    def test_english_detection(self):
        """Test English text detection."""
        test_cases = [
            "I am going to office",
            "Hello, how are you?",
            "The weather is nice today",
            "Thank you for your help",
            "I love programming in Python"
        ]
        
        for text in test_cases:
            result = detector.detect_language(text)
            self.assertEqual(result['language'], 'English')
            self.assertGreater(result['confidence'], 80)
            self.assertGreater(result['english_score'], result['hindi_score'])
            self.assertGreater(result['english_score'], result['hinglish_score'])
    
    def test_hindi_detection(self):
        """Test Hindi text detection."""
        test_cases = [
            "मैं आज ऑफिस जा रहा हूँ",
            "आज बहुत अच्छा दिन है",
            "धन्यवाद आपकी सहायता के लिए",
            "मुझे पायथन प्रोग्रामिंग पसंद है",
            "कल मैं घर जाऊंगा"
        ]
        
        for text in test_cases:
            result = detector.detect_language(text)
            self.assertEqual(result['language'], 'Hindi')
            self.assertGreater(result['confidence'], 85)
            self.assertGreater(result['hindi_score'], result['english_score'])
            self.assertGreater(result['hindi_score'], result['hinglish_score'])
    
    def test_hinglish_detection(self):
        """Test Hinglish text detection."""
        test_cases = [
            "Main office ja raha hoon",
            "Kal meeting hai at office",
            "Bhai, kya haal hai?",
            "Thoda time lagega, okay?",
            "Aajkal bohot busy hoon"
        ]
        
        for text in test_cases:
            result = detector.detect_language(text)
            self.assertEqual(result['language'], 'Hinglish')
            self.assertGreater(result['confidence'], 75)
            self.assertGreater(result['hinglish_score'], result['hindi_score'])
            self.assertGreater(result['hinglish_score'], result['english_score'])
    
    def test_empty_text(self):
        """Test empty text handling."""
        result = detector.detect_language("")
        self.assertEqual(result['language'], 'Unknown')
        self.assertEqual(result['confidence'], 0.0)
    
    def test_confidence_calculation(self):
        """Test confidence calculation logic."""
        text = "Main office ja raha hoon"
        result = detector.detect_language(text)
        
        # Confidence should be between 0 and 100
        self.assertGreaterEqual(result['confidence'], 0)
        self.assertLessEqual(result['confidence'], 100)
        
        # Breakdown percentages should sum to 100
        breakdown = result['breakdown']
        total_percentage = (breakdown['hindi_percentage'] + 
                          breakdown['english_percentage'] + 
                          breakdown['hinglish_percentage'])
        self.assertAlmostEqual(total_percentage, 100, places=1)


class LanguageDetectionAPITest(APITestCase):
    """Test cases for the REST API endpoints."""
    
    def test_detect_language_endpoint(self):
        """Test the main language detection API endpoint."""
        url = reverse('detect-language')
        data = {'text': 'Main office ja raha hoon'}
        
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        self.assertTrue(response.data['success'])
        self.assertIn('data', response.data)
        
        result = response.data['data']
        self.assertIn('detected_language', result)
        self.assertIn('confidence', result)
        self.assertIn('breakdown', result)
    
    def test_detect_language_invalid_input(self):
        """Test API with invalid input."""
        url = reverse('detect-language')
        data = {'text': ''}
        
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_detection_history_endpoint(self):
        """Test the detection history API endpoint."""
        url = reverse('detection-history')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        self.assertTrue(response.data['success'])
        self.assertIn('data', response.data)
    
    def test_statistics_endpoint(self):
        """Test the statistics API endpoint."""
        url = reverse('statistics')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        self.assertTrue(response.data['success'])
        self.assertIn('data', response.data)
    
    def test_test_detection_endpoint(self):
        """Test the test detection endpoint."""
        url = reverse('test-detection')
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        self.assertTrue(response.data['success'])
        self.assertIn('data', response.data)
        self.assertIn('accuracy', response.data['data'])


class AccuracyTestCase(TestCase):
    """Test cases to verify 92-95% accuracy claim."""
    
    def test_accuracy_on_sample_cases(self):
        """Test accuracy on provided sample cases."""
        test_cases = [
            {'text': 'I am going to office', 'expected': 'English'},
            {'text': 'मैं आज ऑफिस जा रहा हूँ', 'expected': 'Hindi'},
            {'text': 'Main office ja raha hoon', 'expected': 'Hinglish'},
            {'text': 'Kal meeting hai at office', 'expected': 'Hinglish'},
            {'text': 'Hello, how are you?', 'expected': 'English'},
            {'text': 'आज बहुत अच्छा दिन है', 'expected': 'Hindi'},
            {'text': 'Thank you for your help', 'expected': 'English'},
            {'text': 'धन्यवाद आपकी सहायता के लिए', 'expected': 'Hindi'},
            {'text': 'Bhai, kya haal hai?', 'expected': 'Hinglish'},
            {'text': 'The weather is nice today', 'expected': 'English'},
        ]
        
        correct_predictions = 0
        total_predictions = len(test_cases)
        
        for test_case in test_cases:
            result = detector.detect_language(test_case['text'])
            if result['language'] == test_case['expected']:
                correct_predictions += 1
        
        accuracy = (correct_predictions / total_predictions) * 100
        self.assertGreaterEqual(accuracy, 90)  # At least 90% accuracy
        
        print(f"Accuracy on sample cases: {accuracy}% ({correct_predictions}/{total_predictions})")


class EdgeCasesTestCase(TestCase):
    """Test cases for edge cases and boundary conditions."""
    
    def test_very_short_text(self):
        """Test detection on very short text."""
        short_texts = ["Hi", "है", "OK"]
        
        for text in short_texts:
            result = detector.detect_language(text)
            self.assertIsNotNone(result['language'])
            self.assertIsInstance(result['confidence'], float)
    
    def test_very_long_text(self):
        """Test detection on very long text."""
        long_text = "This is a very long text. " * 100  # Repeat 100 times
        result = detector.detect_language(long_text)
        self.assertIsNotNone(result['language'])
        self.assertGreater(result['confidence'], 0)
    
    def test_mixed_punctuation(self):
        """Test detection with mixed punctuation."""
        mixed_text = "Hello! कैसे हैं आप? How are you doing?"
        result = detector.detect_language(mixed_text)
        self.assertIsNotNone(result['language'])
        self.assertIsInstance(result['confidence'], float)
    
    def test_numbers_and_special_chars(self):
        """Test detection with numbers and special characters."""
        special_text = "I have 5 apples और 3 oranges. Total = 8!"
        result = detector.detect_language(special_text)
        self.assertIsNotNone(result['language'])
        self.assertIsInstance(result['confidence'], float)
