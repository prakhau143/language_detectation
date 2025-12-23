/**
 * LangSense AI - Frontend JavaScript
 * Handles language detection UI interactions and API communication
 */

class LanguageDetectionApp {
    constructor() {
        this.apiBaseUrl = '/api';
        this.init();
    }

    init() {
        this.bindEvents();
        this.loadTheme();
        this.updateCharCount();
    }

    bindEvents() {
        // Input text events
        const inputText = document.getElementById('input-text');
        const detectBtn = document.getElementById('detect-btn');
        const clearBtn = document.getElementById('clear-btn');
        const newDetectionBtn = document.getElementById('new-detection-btn');

        inputText.addEventListener('input', () => {
            this.updateCharCount();
            this.toggleDetectButton();
        });

        detectBtn.addEventListener('click', () => {
            this.detectLanguage();
        });

        clearBtn.addEventListener('click', () => {
            this.clearInput();
        });

        newDetectionBtn.addEventListener('click', () => {
            this.resetDetection();
        });

        // Sample text buttons
        document.querySelectorAll('.sample-text').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const text = e.currentTarget.dataset.text;
                inputText.value = text;
                this.updateCharCount();
                this.toggleDetectButton();
                inputText.focus();
            });
        });

        // Theme toggle
        const themeToggle = document.getElementById('theme-toggle');
        themeToggle.addEventListener('click', () => {
            this.toggleTheme();
        });

        // Keyboard shortcuts
        document.addEventListener('keydown', (e) => {
            if (e.ctrlKey && e.key === 'Enter') {
                this.detectLanguage();
            }
            if (e.key === 'Escape') {
                this.clearInput();
            }
        });
    }

    updateCharCount() {
        const inputText = document.getElementById('input-text');
        const charCount = document.getElementById('char-count');
        const count = inputText.value.length;
        
        charCount.textContent = count;
        
        // Color coding based on length
        if (count > 9000) {
            charCount.className = 'text-red-400 text-sm';
        } else if (count > 7000) {
            charCount.className = 'text-yellow-400 text-sm';
        } else {
            charCount.className = 'text-white/60 text-sm';
        }
    }

    toggleDetectButton() {
        const inputText = document.getElementById('input-text');
        const detectBtn = document.getElementById('detect-btn');
        
        const hasText = inputText.value.trim().length > 0;
        detectBtn.disabled = !hasText;
        
        if (hasText) {
            detectBtn.classList.remove('opacity-50', 'cursor-not-allowed');
        } else {
            detectBtn.classList.add('opacity-50', 'cursor-not-allowed');
        }
    }

    async detectLanguage() {
        const inputText = document.getElementById('input-text').value.trim();
        
        if (!inputText) {
            this.showError('Please enter some text to analyze.');
            return;
        }

        this.setLoadingState(true);
        this.hideResults();
        this.hideError();

        try {
            const response = await fetch(`${this.apiBaseUrl}/detect-language/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ text: inputText })
            });

            const data = await response.json();

            if (data.success) {
                this.displayResults(data.data);
            } else {
                this.showError(data.error || 'Detection failed. Please try again.');
            }
        } catch (error) {
            console.error('Detection error:', error);
            this.showError('Network error. Please check your connection and try again.');
        } finally {
            this.setLoadingState(false);
        }
    }

    displayResults(result) {
        const resultsSection = document.getElementById('results-section');
        
        // Update language badge
        this.updateLanguageBadge(result.detected_language, result.confidence);
        
        // Update confidence bar
        this.updateConfidenceBar(result.confidence);
        
        // Update breakdown
        this.updateBreakdown(result);
        
        // Show results with animation
        resultsSection.classList.remove('hidden');
        resultsSection.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
    }

    updateLanguageBadge(language, confidence) {
        const badge = document.getElementById('language-badge');
        const icon = document.getElementById('language-icon');
        const languageText = document.getElementById('detected-language');
        const confidenceText = document.getElementById('confidence-text');

        // Reset classes
        badge.className = 'inline-flex items-center px-6 py-3 rounded-full text-white font-bold text-xl shadow-lg';
        
        // Set language-specific styling
        switch (language.toLowerCase()) {
            case 'hindi':
                badge.classList.add('bg-gradient-to-r', 'from-orange-500', 'to-red-500');
                icon.className = 'fas fa-om mr-3 text-2xl';
                break;
            case 'english':
                badge.classList.add('bg-gradient-to-r', 'from-blue-500', 'to-blue-600');
                icon.className = 'fab fa-english mr-3 text-2xl';
                break;
            case 'hinglish':
                badge.classList.add('bg-gradient-to-r', 'from-green-500', 'to-emerald-500');
                icon.className = 'fas fa-globe mr-3 text-2xl';
                break;
            default:
                badge.classList.add('bg-gradient-to-r', 'from-gray-500', 'to-gray-600');
                icon.className = 'fas fa-question mr-3 text-2xl';
        }

        languageText.textContent = language;
        confidenceText.textContent = `(${confidence}%)`;
    }

    updateConfidenceBar(confidence) {
        const bar = document.getElementById('confidence-bar');
        const percentage = document.getElementById('confidence-percentage');
        
        // Animate the bar
        setTimeout(() => {
            bar.style.width = `${confidence}%`;
        }, 100);
        
        percentage.textContent = `${confidence}%`;
        
        // Color coding based on confidence level
        if (confidence >= 90) {
            bar.className = 'bg-gradient-to-r from-green-400 to-green-600 h-3 rounded-full transition-all duration-1000 ease-out';
        } else if (confidence >= 70) {
            bar.className = 'bg-gradient-to-r from-yellow-400 to-orange-500 h-3 rounded-full transition-all duration-1000 ease-out';
        } else {
            bar.className = 'bg-gradient-to-r from-red-400 to-red-600 h-3 rounded-full transition-all duration-1000 ease-out';
        }
    }

    updateBreakdown(result) {
        // Update Hindi
        document.getElementById('hindi-percentage').textContent = `${result.breakdown.hindi_percentage}%`;
        document.getElementById('hindi-score').textContent = `Score: ${result.hindi_score}`;
        
        // Update English
        document.getElementById('english-percentage').textContent = `${result.breakdown.english_percentage}%`;
        document.getElementById('english-score').textContent = `Score: ${result.english_score}`;
        
        // Update Hinglish
        document.getElementById('hinglish-percentage').textContent = `${result.breakdown.hinglish_percentage}%`;
        document.getElementById('hinglish-score').textContent = `Score: ${result.hinglish_score}`;
    }

    setLoadingState(isLoading) {
        const btn = document.getElementById('detect-btn');
        const btnText = document.getElementById('btn-text');
        const spinner = document.getElementById('loading-spinner');
        
        if (isLoading) {
            btn.disabled = true;
            btnText.textContent = 'Detecting...';
            spinner.classList.remove('hidden');
            btn.classList.add('opacity-75');
        } else {
            btn.disabled = false;
            btnText.textContent = 'Detect Language';
            spinner.classList.add('hidden');
            btn.classList.remove('opacity-75');
        }
    }

    hideResults() {
        const resultsSection = document.getElementById('results-section');
        resultsSection.classList.add('hidden');
    }

    showError(message) {
        const errorSection = document.getElementById('error-section');
        const errorMessage = document.getElementById('error-message');
        
        errorMessage.textContent = message;
        errorSection.classList.remove('hidden');
        
        // Auto-hide after 5 seconds
        setTimeout(() => {
            this.hideError();
        }, 5000);
    }

    hideError() {
        const errorSection = document.getElementById('error-section');
        errorSection.classList.add('hidden');
    }

    clearInput() {
        const inputText = document.getElementById('input-text');
        inputText.value = '';
        this.updateCharCount();
        this.toggleDetectButton();
        this.hideResults();
        this.hideError();
        inputText.focus();
    }

    resetDetection() {
        this.clearInput();
        document.getElementById('input-text').focus();
    }

    toggleTheme() {
        const body = document.body;
        const themeToggle = document.getElementById('theme-toggle');
        const icon = themeToggle.querySelector('i');
        
        if (body.classList.contains('dark')) {
            body.classList.remove('dark');
            icon.className = 'fas fa-moon text-white';
            localStorage.setItem('theme', 'light');
        } else {
            body.classList.add('dark');
            icon.className = 'fas fa-sun text-white';
            localStorage.setItem('theme', 'dark');
        }
    }

    loadTheme() {
        const savedTheme = localStorage.getItem('theme');
        const themeToggle = document.getElementById('theme-toggle');
        const icon = themeToggle.querySelector('i');
        
        if (savedTheme === 'dark') {
            document.body.classList.add('dark');
            icon.className = 'fas fa-sun text-white';
        } else {
            document.body.classList.remove('dark');
            icon.className = 'fas fa-moon text-white';
        }
    }
}

// Initialize the app when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    new LanguageDetectionApp();
});

// Add some utility functions for enhanced UX
function copyToClipboard(text) {
    navigator.clipboard.writeText(text).then(() => {
        // Show a temporary success message
        const toast = document.createElement('div');
        toast.className = 'fixed top-4 right-4 px-4 py-2 rounded-lg shadow-lg z-50';
        toast.style.background = 'var(--accent-secondary)';
        toast.style.color = 'white';
        toast.textContent = 'Copied to clipboard!';
        document.body.appendChild(toast);
        
        setTimeout(() => {
            toast.remove();
        }, 2000);
    });
}

// Add smooth scrolling for navigation links
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function (e) {
        e.preventDefault();
        const target = document.querySelector(this.getAttribute('href'));
        if (target) {
            target.scrollIntoView({
                behavior: 'smooth'
            });
        }
    });
});
