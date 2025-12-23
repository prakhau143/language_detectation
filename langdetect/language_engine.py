"""
LangSense AI - Advanced Language Detection Engine
Implements 4-technique scoring system for English/Hindi/Hinglish detection
"""

import re
import unicodedata
from collections import Counter
from typing import Dict, Tuple, List


class LanguageDetector:
    """
    Advanced language detection using weighted scoring system.
    Combines Unicode analysis, token analysis, and pattern matching.
    """
    
    def __init__(self):
        # Devanagari Unicode range for Hindi detection
        self.devanagari_range = ('\u0900', '\u097F')
        
        # English stopwords for token analysis
        self.english_stopwords = {
            'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 
            'by', 'is', 'are', 'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had',
            'do', 'does', 'did', 'will', 'would', 'could', 'should', 'may', 'might', 'must',
            'i', 'you', 'he', 'she', 'it', 'we', 'they', 'me', 'him', 'her', 'us', 'them',
            'my', 'your', 'his', 'her', 'its', 'our', 'their', 'this', 'that', 'these', 'those',
            'here', 'there', 'where', 'when', 'why', 'how', 'what', 'which', 'who', 'whom',
            'am', 'going', 'office', 'home', 'work', 'time', 'day', 'good', 'bad', 'big', 'small'
        }
        
        # Roman Hindi dictionary and common patterns
        self.roman_hindi_words = {
            'hai', 'hoon', 'raha', 'rahi', 'rahen', 'tha', 'thi', 'the', 'kar', 'kya', 'kyun', 
            'nahi', 'mat', 'bhi', 'to', 'hi', 'aur', 'ya', 'lekin', 'par', 'ke', 'ka', 'ki',
            'ko', 'se', 'mein', 'par', 'tak', 'se', 'ke', 'liye', 'sakta', 'sakti', 'sakte',
            'ja', 'aao', 'chalo', 'dekho', 'suno', 'bolo', 'karo', 'kijiye', 'dijiye',
            'kal', 'aaj', 'kal', 'subah', 'shaam', 'raat', 'din', 'week', 'month', 'year'
        }
        
        # Hinglish bigram patterns
        self.hinglish_patterns = [
            'ja raha', 'ja rahi', 'ja rahe', 'kar raha', 'kar rahi', 'kar rahe',
            'ho gaya', 'ho gaye', 'ho gayi', 'aa raha', 'aa rahi', 'aa rahe',
            'dekh raha', 'dekh rahi', 'dekh rahe', 'suna hai', 'pata hai', 'lagta hai'
        ]
        
        # Common English words for validation
        self.english_words = {
            'hello', 'hi', 'good', 'morning', 'evening', 'night', 'how', 'are', 'you',
            'fine', 'thank', 'thanks', 'please', 'sorry', 'excuse', 'meeting', 'office',
            'home', 'work', 'time', 'today', 'tomorrow', 'yesterday', 'yes', 'no'
        }
    
    def detect_unicode_hindi(self, text: str) -> float:
        """
        Technique 1: Unicode-based Hindi detection using Devanagari range.
        Returns score between 0-100.
        """
        if not text.strip():
            return 0.0
        
        devanagari_count = 0
        total_chars = 0
        
        for char in text:
            if char.strip():  # Skip whitespace
                total_chars += 1
                if self.devanagari_range[0] <= char <= self.devanagari_range[1]:
                    devanagari_count += 1
        
        if total_chars == 0:
            return 0.0
        
        # Calculate percentage of Devanagari characters
        hindi_ratio = (devanagari_count / total_chars) * 100
        
        # Apply strong signal weighting for high Devanagari content
        if hindi_ratio > 70:
            return min(100, hindi_ratio * 1.2)  # Boost high-confidence cases
        elif hindi_ratio > 30:
            return hindi_ratio * 0.8  # Moderate boost for mixed content
        else:
            return hindi_ratio * 0.3  # Low weight for minimal Devanagari
    
    def detect_english_tokens(self, text: str) -> float:
        """
        Technique 2: Token-based English detection using dictionary and stopwords.
        Returns score between 0-100.
        """
        if not text.strip():
            return 0.0
        
        # Clean and tokenize text
        words = re.findall(r'\b[a-zA-Z]+\b', text.lower())
        
        if not words:
            return 0.0
        
        english_score = 0
        total_words = len(words)
        
        for word in words:
            if word in self.english_stopwords:
                english_score += 2  # Higher weight for stopwords
            elif word in self.english_words:
                english_score += 1.5  # Medium weight for common words
            elif len(word) > 3 and word.endswith(('ing', 'ed', 'ly', 'tion')):
                english_score += 1  # Morphological patterns
        
        # Calculate percentage
        max_possible_score = total_words * 2
        english_ratio = (english_score / max_possible_score) * 100 if max_possible_score > 0 else 0
        
        return min(100, english_ratio)
    
    def detect_hinglish_patterns(self, text: str) -> float:
        """
        Technique 3: Hinglish detection using Roman Hindi dictionary and grammar heuristics.
        Returns score between 0-100.
        """
        if not text.strip():
            return 0.0
        
        text_lower = text.lower()
        hinglish_score = 0
        
        # Check for Roman Hindi words
        words = re.findall(r'\b[a-zA-Z]+\b', text_lower)
        total_words = len(words)
        
        if total_words == 0:
            return 0.0
        
        for word in words:
            if word in self.roman_hindi_words:
                hinglish_score += 2
        
        # Check for Hinglish bigram patterns
        for pattern in self.hinglish_patterns:
            if pattern in text_lower:
                hinglish_score += 3  # High weight for patterns
        
        # Check for mixed script patterns (Roman + Devanagari)
        has_roman = bool(re.search(r'[a-zA-Z]', text))
        has_devanagari = bool(re.search(r'[\u0900-\u097F]', text))
        
        if has_roman and has_devanagari:
            hinglish_score += 5  # Strong indicator of Hinglish
        
        # Calculate percentage
        max_possible_score = total_words * 2 + len(self.hinglish_patterns) * 3 + 5
        hinglish_ratio = (hinglish_score / max_possible_score) * 100 if max_possible_score > 0 else 0
        
        return min(100, hinglish_ratio)
    
    def calculate_confidence(self, scores: Dict[str, float]) -> float:
        """
        Calculate confidence based on score differences.
        Higher confidence when one language clearly dominates.
        """
        hindi_score = scores.get('hindi', 0)
        english_score = scores.get('english', 0)
        hinglish_score = scores.get('hinglish', 0)
        
        total_score = hindi_score + english_score + hinglish_score
        
        if total_score == 0:
            return 0.0
        
        # Find the highest score
        max_score = max(hindi_score, english_score, hinglish_score)
        
        # Calculate confidence as percentage of top score relative to total
        confidence = (max_score / total_score) * 100
        
        # Boost confidence if there's a clear winner
        if max_score > 50:
            confidence = min(100, confidence * 1.1)
        
        return round(confidence, 2)
    
    def detect_language(self, text: str) -> Dict:
        """
        Main detection method using weighted scoring system.
        Returns detected language with confidence and breakdown.
        """
        if not text or not text.strip():
            return {
                'language': 'Unknown',
                'confidence': 0.0,
                'hindi_score': 0.0,
                'english_score': 0.0,
                'hinglish_score': 0.0,
                'breakdown': {
                    'hindi_percentage': 0.0,
                    'english_percentage': 0.0,
                    'hinglish_percentage': 0.0
                }
            }
        
        # Calculate scores for each technique
        hindi_score = self.detect_unicode_hindi(text)
        english_score = self.detect_english_tokens(text)
        hinglish_score = self.detect_hinglish_patterns(text)
        
        scores = {
            'hindi': hindi_score,
            'english': english_score,
            'hinglish': hinglish_score
        }
        
        # Determine dominant language
        detected_language = max(scores, key=scores.get)
        confidence = self.calculate_confidence(scores)
        
        # Calculate breakdown percentages
        total_score = sum(scores.values())
        if total_score > 0:
            breakdown = {
                'hindi_percentage': round((hindi_score / total_score) * 100, 2),
                'english_percentage': round((english_score / total_score) * 100, 2),
                'hinglish_percentage': round((hinglish_score / total_score) * 100, 2)
            }
        else:
            breakdown = {
                'hindi_percentage': 0.0,
                'english_percentage': 0.0,
                'hinglish_percentage': 0.0
            }
        
        return {
            'language': detected_language.title(),
            'confidence': confidence,
            'hindi_score': round(hindi_score, 2),
            'english_score': round(english_score, 2),
            'hinglish_score': round(hinglish_score, 2),
            'breakdown': breakdown
        }


# Global detector instance
detector = LanguageDetector()
