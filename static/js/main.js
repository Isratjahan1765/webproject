/**
 * SPHWMS — Main JavaScript
 * Sidebar toggle, chart init, auto-refresh, and utility functions.
 */

document.addEventListener('DOMContentLoaded', () => {
    initSidebar();
    initAutoRefresh();
    initFadeIn();
});

/* ── Sidebar Toggle ── */
function initSidebar() {
    const sidebar = document.getElementById('sidebar');
    const openBtn = document.getElementById('sidebarOpen');
    const closeBtn = document.getElementById('sidebarClose');

    if (openBtn) {
        openBtn.addEventListener('click', () => sidebar.classList.add('show'));
    }
    if (closeBtn) {
        closeBtn.addEventListener('click', () => sidebar.classList.remove('show'));
    }
    // Close sidebar on outside click (mobile)
    document.addEventListener('click', (e) => {
        if (sidebar && sidebar.classList.contains('show') && !sidebar.contains(e.target) && e.target !== openBtn) {
            sidebar.classList.remove('show');
        }
    });
}

/* ── Dashboard Charts ── */
function initRevenueChart(data) {
    const ctx = document.getElementById('revenueChart');
    if (!ctx) return;

    const parsed = typeof data === 'string' ? JSON.parse(data) : data;
    new Chart(ctx, {
        type: 'line',
        data: {
            labels: parsed.map(d => d.month),
            datasets: [{
                label: 'Revenue (৳)',
                data: parsed.map(d => parseFloat(d.revenue)),
                borderColor: '#6366f1',
                backgroundColor: 'rgba(99,102,241,0.1)',
                borderWidth: 2,
                fill: true,
                tension: 0.4,
                pointBackgroundColor: '#6366f1',
                pointRadius: 4,
                pointHoverRadius: 6,
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { labels: { color: '#94a3b8', font: { family: 'Inter' } } },
            },
            scales: {
                x: { ticks: { color: '#64748b' }, grid: { color: 'rgba(99,102,241,0.06)' } },
                y: { ticks: { color: '#64748b' }, grid: { color: 'rgba(99,102,241,0.06)' } },
            }
        }
    });
}

function initInventoryChart(data) {
    const ctx = document.getElementById('inventoryChart');
    if (!ctx) return;

    const parsed = typeof data === 'string' ? JSON.parse(data) : data;
    const colors = ['#6366f1', '#8b5cf6', '#06b6d4', '#10b981', '#f59e0b', '#ef4444', '#3b82f6'];

    new Chart(ctx, {
        type: 'pie',
        data: {
            labels: parsed.map(d => d.product__category),
            datasets: [{
                data: parsed.map(d => parseFloat(d.total)),
                backgroundColor: colors.slice(0, parsed.length),
                borderColor: '#1a1a3e',
                borderWidth: 2,
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { position: 'bottom', labels: { color: '#94a3b8', font: { family: 'Inter' }, padding: 16 } },
            },
        }
    });
}

function initCategoryBarChart(data) {
    const ctx = document.getElementById('categoryBarChart');
    if (!ctx) return;

    const parsed = typeof data === 'string' ? JSON.parse(data) : data;
    const colors = ['#6366f1', '#8b5cf6', '#06b6d4', '#10b981', '#f59e0b', '#ef4444', '#3b82f6'];

    new Chart(ctx, {
        type: 'bar',
        data: {
            labels: parsed.map(d => d.product__category),
            datasets: [{
                label: 'Total Quantity',
                data: parsed.map(d => parseFloat(d.total)),
                backgroundColor: colors.slice(0, parsed.length),
                borderRadius: 4,
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { display: false },
            },
            scales: {
                x: { ticks: { color: '#64748b' }, grid: { display: false } },
                y: { ticks: { color: '#64748b' }, grid: { color: 'rgba(99,102,241,0.06)' } },
            }
        }
    });
}

/* ── Auto Refresh Dashboard ── */
function initAutoRefresh() {
    const dashboard = document.getElementById('dashboard-container');
    if (!dashboard) return;

    setInterval(async () => {
        try {
            const response = await fetch('/api/dashboard/');
            if (response.ok) {
                // Could update DOM elements here for live data
                console.log('Dashboard data refreshed');
            }
        } catch (e) {
            console.warn('Auto-refresh failed:', e);
        }
    }, 60000); // Refresh every 60 seconds
}

/* ── Fade-in Animation ── */
function initFadeIn() {
    document.querySelectorAll('.fade-in-card').forEach((el, i) => {
        el.style.animationDelay = `${i * 0.08}s`;
        el.classList.add('fade-in');
    });
}

/* ── Utility: Format currency ── */
function formatBDT(amount) {
    return '৳' + parseFloat(amount).toLocaleString('en-BD', { minimumFractionDigits: 2 });
}

/* ── Confirm actions ── */
function confirmAction(message) {
    return confirm(message || 'Are you sure?');
}
