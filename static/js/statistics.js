/**
 * LangSense AI - Statistics Page JavaScript
 * Handles statistics display, charts, and analytics
 */

class StatisticsManager {
    constructor() {
        this.apiBaseUrl = '/api';
        this.charts = {};
        this.init();
    }

    init() {
        this.loadStatistics();
    }

    async loadStatistics() {
        try {
            const response = await fetch(`${this.apiBaseUrl}/statistics/`);
            const data = await response.json();

            if (data.success) {
                this.displayStatistics(data.data);
                this.createCharts(data.data);
            } else {
                this.showError('Failed to load statistics.');
            }
        } catch (error) {
            console.error('Statistics loading error:', error);
            this.showError('Network error. Please check your connection.');
        }
    }

    displayStatistics(stats) {
        // Update overview cards
        document.getElementById('total-detections').textContent = stats.total_detections.toLocaleString();
        document.getElementById('avg-confidence').textContent = `${Math.round(stats.avg_confidence)}%`;
        
        // Find most detected language
        const languageCounts = stats.language_distribution;
        let mostDetected = '-';
        let maxCount = 0;
        
        for (const [lang, data] of Object.entries(languageCounts)) {
            if (data.count > maxCount) {
                maxCount = data.count;
                mostDetected = lang;
            }
        }
        
        document.getElementById('most-detected').textContent = mostDetected;
        
        // Calculate success rate (detections with >70% confidence)
        const highConfidenceCount = Object.values(stats.confidence_distribution)
            .slice(0, 4) // First 4 ranges (90-100%, 80-89%, 70-79%, 60-69%)
            .reduce((sum, count) => sum + count, 0);
        
        const successRate = stats.total_detections > 0 
            ? Math.round((highConfidenceCount / stats.total_detections) * 100) 
            : 0;
        document.getElementById('success-rate').textContent = `${successRate}%`;
    }

    createCharts(stats) {
        this.createLanguageChart(stats.language_distribution);
        this.createConfidenceChart(stats.confidence_distribution);
        this.createActivityChart(stats.recent_activity);
    }

    createLanguageChart(languageData) {
        const ctx = document.getElementById('languageChart').getContext('2d');
        
        const languageColors = {
            English: '#3B82F6',
            Hindi: '#FF6B35',
            Hinglish: '#10B981'
        };
        
        const labels = Object.keys(languageData);
        const data = Object.values(languageData).map(item => item.count);
        const colors = Object.keys(languageData).map(
            lang => languageColors[lang] || '#9CA3AF'
        );
        
        this.charts.language = new Chart(ctx, {
            type: 'doughnut',
            data: {
                labels: labels,
                datasets: [{
                    data: data,
                    backgroundColor: colors,
                    borderColor: '#0F172A',
                    borderWidth: 2
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'bottom',
                        labels: {
                            color: '#E5E7EB',
                            padding: 20
                        }
                    }
                }
            }
        });
    }

    createConfidenceChart(confidenceData) {
        const ctx = document.getElementById('confidenceChart').getContext('2d');
        
        const labels = Object.keys(confidenceData);
        const data = Object.values(confidenceData);
        
        this.charts.confidence = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: labels,
                datasets: [{
                    label: 'Number of Detections',
                    data: data,
                    backgroundColor: [
                        '#22C55E', // 90-100%
                        '#3B82F6', // 80-89%
                        '#FACC15', // 70-79%
                        '#FB923C', // 60-69%
                        '#EF4444'  // Below 60%
                    ],
                    borderColor: [
                        '#22C55E',
                        '#3B82F6',
                        '#FACC15',
                        '#FB923C',
                        '#EF4444'
                    ],
                    borderWidth: 1
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    y: {
                        beginAtZero: true,
                        ticks: {
                            color: '#CBD5F5'
                        },
                        grid: {
                            color: 'rgba(255, 255, 255, 0.1)'
                        }
                    },
                    x: {
                        ticks: {
                            color: '#CBD5F5'
                        },
                        grid: {
                            color: 'rgba(255, 255, 255, 0.1)'
                        }
                    }
                },
                plugins: {
                    legend: {
                        labels: {
                            color: '#E5E7EB'
                        }
                    }
                }
            }
        });
    }

    createActivityChart(recentActivity) {
        const ctx = document.getElementById('activityChart').getContext('2d');
        
        // Process recent activity data with proper mapping
        const days = {};
        recentActivity.forEach(item => {
            const date = item.created_at__date;
            if (!days[date]) {
                days[date] = { Hindi: 0, English: 0, Hinglish: 0 };
            }
            days[date][item.detected_language] = item.count;
        });

        const labels = Object.keys(days);

        this.charts.activity = new Chart(ctx, {
            type: 'line',
            data: {
                labels,
                datasets: [
                    {
                        label: 'English',
                        data: labels.map(d => days[d].English),
                        borderColor: '#3B82F6',
                        tension: 0.4,
                        fill: false
                    },
                    {
                        label: 'Hindi',
                        data: labels.map(d => days[d].Hindi),
                        borderColor: '#FF6B35',
                        tension: 0.4,
                        fill: false
                    },
                    {
                        label: 'Hinglish',
                        data: labels.map(d => days[d].Hinglish),
                        borderColor: '#10B981',
                        tension: 0.4,
                        fill: false
                    }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    y: {
                        beginAtZero: true,
                        ticks: {
                            color: '#E5E7EB'
                        },
                        grid: {
                            color: 'rgba(255, 255, 255, 0.1)'
                        }
                    },
                    x: {
                        ticks: {
                            color: '#E5E7EB'
                        },
                        grid: {
                            color: 'rgba(255, 255, 255, 0.1)'
                        }
                    }
                },
                plugins: {
                    legend: {
                        labels: {
                            color: '#E5E7EB'
                        }
                    }
                }
            }
        });
    }

    showError(message) {
        console.error(message);
        // Show error in stats cards
        document.getElementById('total-detections').textContent = 'Error';
        document.getElementById('avg-confidence').textContent = 'Error';
        document.getElementById('most-detected').textContent = 'Error';
        document.getElementById('success-rate').textContent = 'Error';
    }
}

// Initialize statistics manager when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    new StatisticsManager();
});
