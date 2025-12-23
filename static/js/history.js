/**
 * LangSense AI - History Page JavaScript
 * Handles detection history display, filtering, and pagination
 */

class HistoryManager {
    constructor() {
        this.apiBaseUrl = '/api';
        this.currentPage = 1;
        this.perPage = 20;
        this.totalPages = 1;
        this.currentFilters = {};
        this.init();
    }

    init() {
        this.bindEvents();
        this.loadHistory();
    }

    bindEvents() {
        // Filter events
        const languageFilter = document.getElementById('language-filter');
        const searchFilter = document.getElementById('search-filter');
        const applyFiltersBtn = document.getElementById('apply-filters');

        applyFiltersBtn.addEventListener('click', () => {
            this.applyFilters();
        });

        // Enter key for search
        searchFilter.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                this.applyFilters();
            }
        });

        // Pagination events
        const prevPageBtn = document.getElementById('prev-page');
        const nextPageBtn = document.getElementById('next-page');

        prevPageBtn.addEventListener('click', () => {
            if (this.currentPage > 1) {
                this.currentPage--;
                this.loadHistory();
            }
        });

        nextPageBtn.addEventListener('click', () => {
            if (this.currentPage < this.totalPages) {
                this.currentPage++;
                this.loadHistory();
            }
        });
    }

    applyFilters() {
        const languageFilter = document.getElementById('language-filter').value;
        const searchFilter = document.getElementById('search-filter').value.trim();

        this.currentFilters = {};
        if (languageFilter) {
            this.currentFilters.language = languageFilter;
        }
        if (searchFilter) {
            this.currentFilters.search = searchFilter;
        }

        this.currentPage = 1; // Reset to first page
        this.loadHistory();
    }

    async loadHistory() {
        this.showLoading(true);

        try {
            const params = new URLSearchParams({
                page: this.currentPage,
                per_page: this.perPage,
                ...this.currentFilters
            });

            const response = await fetch(`${this.apiBaseUrl}/detection-history/?${params}`);
            const data = await response.json();

            if (data.success) {
                // cache detections for modal look-ups
                this.detections = data.data.detections;
                this.displayHistory(this.detections);
                this.updatePagination(data.data.pagination);
                this.createHistoryActivityChart(data.data.detections);
            } else {
                this.showError('Failed to load detection history.');
            }
        } catch (error) {
            console.error('History loading error:', error);
            this.showError('Network error. Please check your connection.');
        } finally {
            this.showLoading(false);
        }
    }

    displayHistory(detections) {
        const tableBody = document.getElementById('history-table-body');
        const emptyState = document.getElementById('empty-state');

        if (detections.length === 0) {
            tableBody.innerHTML = '';
            emptyState.classList.remove('hidden');
            return;
        }

        emptyState.classList.add('hidden');

        tableBody.innerHTML = detections.map(detection => {
            const date = new Date(detection.created_at).toLocaleDateString();
            const time = new Date(detection.created_at).toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'});
            const textPreview = detection.input_text.length > 100 
                ? detection.input_text.substring(0, 100) + '...' 
                : detection.input_text;

            return `
                <tr class="border-b transition-colors" style="border-color: var(--border-soft);" onmouseover="this.style.background='var(--bg-card)'" onmouseout="this.style.background='transparent'">
                    <td class="px-6 py-4">
                        <div style="color: var(--text-main);">${this.escapeHtml(textPreview)}</div>
                        ${detection.input_text.length > 100 ? `
                            <button class="text-sm mt-1 hover:opacity-80 transition-opacity" style="color: var(--accent-primary);" onclick="historyManager.showFullText('${this.escapeHtml(detection.input_text)}')">
                                Show full text
                            </button>
                        ` : ''}
                    </td>
                    <td class="px-6 py-4">
                        <span class="inline-flex items-center px-3 py-1 rounded-full text-sm font-medium text-white ${this.getLanguageBadgeClass(detection.detected_language)}">
                            ${this.getLanguageIcon(detection.detected_language)}
                            ${detection.detected_language}
                        </span>
                    </td>
                    <td class="px-6 py-4">
                        <div class="flex items-center">
                            <div class="w-16 rounded-full h-2 mr-3" style="background: var(--border-soft);">
                                <div class="h-2 rounded-full transition-all duration-1000" style="width: ${detection.confidence}%; background: var(--primary-gradient);"></div>
                            </div>
                            <span class="font-medium" style="color: var(--text-main);">${detection.confidence}%</span>
                        </div>
                    </td>
                    <td class="px-6 py-4">
                        <div style="color: var(--text-muted);">
                            <div>${date}</div>
                            <div class="text-sm">${time}</div>
                        </div>
                    </td>
                    <td class="px-6 py-4">
                        <div class="flex space-x-2">
                            <button onclick="historyManager.viewDetails(${detection.id})" 
                                    class="p-2 rounded-lg transition-opacity" 
                                    style="background: var(--bg-card); border: 1px solid var(--border-soft); color: var(--text-main);"
                                    title="View Details">
                                <i class="fas fa-eye"></i>
                            </button>
                            <button onclick="historyManager.copyText('${this.escapeHtml(detection.input_text)}')" 
                                    class="p-2 rounded-lg transition-opacity" 
                                    style="background: var(--bg-card); border: 1px solid var(--border-soft); color: var(--text-main);"
                                    title="Copy Text">
                                <i class="fas fa-copy"></i>
                            </button>
                        </div>
                    </td>
                </tr>
            `;
        }).join('');
    }

    showFullText(fullText) {
        // Create modal or expand functionality
        const modal = document.createElement('div');
        modal.className = 'fixed inset-0 z-50 flex items-center justify-center p-4';
        modal.style.background = 'rgba(0, 0, 0, 0.5)';
        modal.style.backdropFilter = 'blur(4px)';
        modal.innerHTML = `
            <div class="glass-card p-6 max-w-2xl w-full max-h-96 overflow-y-auto">
                <div class="flex justify-between items-center mb-4">
                    <h3 class="text-xl font-bold" style="color: var(--text-main);">Full Text</h3>
                    <button onclick="this.closest('.fixed').remove()" class="p-2 rounded-lg transition-opacity" style="background: var(--bg-card);">
                        <i class="fas fa-times" style="color: var(--text-main);"></i>
                    </button>
                </div>
                <div class="whitespace-pre-wrap" style="color: var(--text-muted);">${this.escapeHtml(fullText)}</div>
                <div class="mt-4 text-right">
                    <button onclick="this.closest('.fixed').remove()" class="px-4 py-2 rounded-lg font-medium transition-colors" style="background: var(--primary-gradient); color: white;">
                        Close
                    </button>
                </div>
            </div>
        `;
        document.body.appendChild(modal);
    }

    viewDetails(detectionId) {
        // Show modal with detection details
        const detection = this.detections.find(d => d.id === detectionId);
        if (detection) {
            this.showDetectionModal(detection);
        }
    }

    showDetectionModal(detection) {
        const modal = document.getElementById('viewModal');
        const modalText = document.getElementById('modalText');
        
        modalText.textContent = detection.input_text;
        modal.classList.remove('hidden');
    }

    copyText(text) {
        navigator.clipboard.writeText(text).then(() => {
            this.showToast('Text copied to clipboard!', 'success');
        }).catch(() => {
            this.showToast('Failed to copy text', 'error');
        });
    }

    getLanguageBadgeClass(language) {
        switch (language.toLowerCase()) {
            case 'hindi':
                return 'bg-gradient-to-r from-orange-500 to-red-500';
            case 'english':
                return 'bg-gradient-to-r from-blue-500 to-blue-600';
            case 'hinglish':
                return 'bg-gradient-to-r from-green-500 to-emerald-500';
            default:
                return 'bg-gradient-to-r from-gray-500 to-gray-600';
        }
    }

    getLanguageIcon(language) {
        switch (language.toLowerCase()) {
            case 'hindi':
                return '<i class="fas fa-om mr-1"></i>';
            case 'english':
                return '<i class="fab fa-english mr-1"></i>';
            case 'hinglish':
                return '<i class="fas fa-globe mr-1"></i>';
            default:
                return '<i class="fas fa-question mr-1"></i>';
        }
    }

    getLanguageColor(language) {
        switch (language.toLowerCase()) {
            case 'hindi':
                return '#FF6B35';
            case 'english':
                return '#3B82F6';
            case 'hinglish':
                return '#10B981';
            default:
                return '#9CA3AF';
        }
    }

    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }

    updatePagination(pagination) {
        const prevBtn = document.getElementById('prev-page');
        const nextBtn = document.getElementById('next-page');
        const info = document.getElementById('pagination-info');

        // Update button states
        prevBtn.disabled = !pagination.has_previous;
        nextBtn.disabled = !pagination.has_next;

        // Update info text
        const start = (pagination.current_page - 1) * pagination.per_page + 1;
        const end = Math.min(pagination.current_page * pagination.per_page, pagination.total_count);
        info.textContent = `Showing ${start}-${end} of ${pagination.total_count} results`;

        this.totalPages = pagination.total_pages;
    }

    showLoading(show) {
        const loadingState = document.getElementById('loading-state');
        const table = document.querySelector('.overflow-x-auto table');
        
        if (show) {
            loadingState.classList.remove('hidden');
            if (table) table.style.display = 'none';
        } else {
            loadingState.classList.add('hidden');
            if (table) table.style.display = 'table';
        }
    }

    showError(message) {
        const tableBody = document.getElementById('history-table-body');
        tableBody.innerHTML = `
            <tr>
                <td colspan="5" class="px-6 py-12 text-center">
                    <div class="text-red-400">
                        <i class="fas fa-exclamation-triangle text-2xl mb-2"></i>
                        <p>${message}</p>
                    </div>
                </td>
            </tr>
        `;
    }

    createHistoryActivityChart(detections) {
        const ctx = document.getElementById('historyActivityChart');
        if (!ctx) return;

        // Process data for last 7 days
        const last7Days = [];
        const today = new Date();
        for (let i = 6; i >= 0; i--) {
            const date = new Date(today);
            date.setDate(date.getDate() - i);
            last7Days.push(date.toISOString().split('T')[0]);
        }

        // Count detections per day
        const dailyCounts = {};
        last7Days.forEach(date => {
            dailyCounts[date] = 0;
        });

        detections.forEach(detection => {
            const detectionDate = new Date(detection.created_at).toISOString().split('T')[0];
            if (dailyCounts.hasOwnProperty(detectionDate)) {
                dailyCounts[detectionDate]++;
            }
        });

        // Create chart
        if (window.Chart) {
            new Chart(ctx, {
                type: 'bar',
                data: {
                    labels: last7Days.map(date => new Date(date).toLocaleDateString()),
                    datasets: [{
                        label: 'Detections',
                        data: last7Days.map(date => dailyCounts[date]),
                        backgroundColor: '#3B82F6',
                        borderColor: '#2563EB',
                        borderWidth: 1
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    scales: {
                        y: {
                            beginAtZero: true,
                            ticks: { color: '#E5E7EB' },
                            grid: { color: 'rgba(255, 255, 255, 0.1)' }
                        },
                        x: {
                            ticks: { color: '#E5E7EB' },
                            grid: { color: 'rgba(255, 255, 255, 0.1)' }
                        }
                    },
                    plugins: {
                        legend: {
                            labels: { color: '#E5E7EB' }
                        }
                    }
                }
            });
        }
    }
}

// Global function so inline onclick can hide modal
window.closeModal = function () {
    const modal = document.getElementById('viewModal');
    if (modal) modal.classList.add('hidden');
};

// Initialize history manager when DOM is loaded
let historyManager;
document.addEventListener('DOMContentLoaded', () => {
    historyManager = new HistoryManager();
});
