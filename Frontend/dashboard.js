document.addEventListener("DOMContentLoaded", function () {

    const API = 'http://localhost:5000/api';
    window.API_BASE = API;

    /* ===== AUTH CHECK ===== */

    const currentPage = window.location.pathname.split('/').pop();
    if (currentPage !== 'login.html') {
        const user = JSON.parse(localStorage.getItem('crm_user'));
        if (!user) {
            window.location.href = 'login.html';
            return;
        }
        window.CRM_USER = user;

        // Show user name in topbar
        const profileEl = document.querySelector('.topbar .profile span');
        if (profileEl) profileEl.textContent = user.full_name.split(' ')[0];
        const avatarEl = document.querySelector('.topbar .profile .avatar');
        if (avatarEl) avatarEl.textContent = user.full_name[0];

        // Show user in sidebar
        const sidebarName = document.querySelector('.sidebar-profile .profile-info');
        if (sidebarName) sidebarName.innerHTML = user.full_name + '<span>' + user.email + '</span>';
        const sidebarAvatar = document.querySelector('.sidebar-profile .avatar-sm');
        if (sidebarAvatar) sidebarAvatar.textContent = user.full_name[0];
    }

    /* ===== LOGOUT (click profile in topbar) ===== */

    const profileClick = document.querySelector('.topbar .profile');
    if (profileClick) {
        profileClick.style.cursor = 'pointer';
        profileClick.title = 'Click to logout';
        profileClick.addEventListener('click', function() {
            if (confirm('Logout from CRM 360?')) {
                localStorage.removeItem('crm_user');
                window.location.href = 'login.html';
            }
        });
    }

    /* ===== GLOBAL SEARCH ===== */

    const searchInput = document.querySelector('.topbar .search-box input');
    if (searchInput) {
        let searchTimeout;
        let searchDropdown = document.createElement('div');
        searchDropdown.className = 'search-dropdown';
        searchDropdown.style.cssText = 'position:absolute;top:100%;left:0;right:0;background:rgba(15,23,42,0.95);border:1px solid rgba(255,255,255,0.1);border-radius:12px;max-height:300px;overflow-y:auto;display:none;z-index:100;backdrop-filter:blur(20px);margin-top:4px;';
        searchInput.parentElement.style.position = 'relative';
        searchInput.parentElement.appendChild(searchDropdown);

        searchInput.addEventListener('input', function() {
            clearTimeout(searchTimeout);
            const q = this.value.trim();
            if (q.length < 2) { searchDropdown.style.display = 'none'; return; }

            searchTimeout = setTimeout(() => {
                fetch(API + '/search?q=' + encodeURIComponent(q))
                    .then(r => r.json())
                    .then(results => {
                        if (results.length === 0) {
                            searchDropdown.innerHTML = '<div style="padding:16px;color:#64748b;font-size:13px;">No results found</div>';
                        } else {
                            searchDropdown.innerHTML = results.map(r => `
                                <a href="${r.link}" style="display:flex;align-items:center;gap:12px;padding:12px 16px;text-decoration:none;border-bottom:1px solid rgba(255,255,255,0.05);transition:background 0.2s;" onmouseover="this.style.background='rgba(255,255,255,0.05)'" onmouseout="this.style.background='transparent'">
                                    <span style="font-size:18px;">${r.type === 'customer' ? '👤' : '📦'}</span>
                                    <div>
                                        <div style="color:#f1f5f9;font-size:13px;font-weight:500;">${r.title}</div>
                                        <div style="color:#64748b;font-size:11px;">${r.subtitle}</div>
                                    </div>
                                </a>
                            `).join('');
                        }
                        searchDropdown.style.display = 'block';
                    });
            }, 300);
        });

        document.addEventListener('click', e => {
            if (!searchInput.parentElement.contains(e.target)) searchDropdown.style.display = 'none';
        });
    }

    /* ===== ACTIVE SIDEBAR ===== */

    let page = window.location.pathname.split('/').pop().replace('.html', '');
    if (!page || page === '' || page === '/') page = 'dashboard';

    document.querySelectorAll('.nav-link').forEach(link => {
        link.classList.remove('active');
        if (link.dataset.page === page) {
            link.classList.add('active');
        }
    });

    /* ===== COUNTER ANIMATION (reusable) ===== */

    window.animateCounters = function () {
        document.querySelectorAll('.counter').forEach(counter => {
            let target = parseFloat(counter.dataset.target);
            if (!target && target !== 0) return;
            let prefix = counter.dataset.prefix || '';
            let suffix = counter.dataset.suffix || '';
            let decimals = parseInt(counter.dataset.decimals) || 0;
            let useIndian = counter.hasAttribute('data-use-indian');
            let duration = 1200;
            let startTime = null;

            function easeOut(t) { return 1 - Math.pow(1 - t, 3); }

            function formatValue(val) {
                if (useIndian) return prefix + formatNumber(val) + suffix;
                if (decimals > 0) return prefix + val.toFixed(decimals) + suffix;
                return prefix + Math.floor(val).toLocaleString('en-IN') + suffix;
            }

            function animate(timestamp) {
                if (!startTime) startTime = timestamp;
                let progress = Math.min((timestamp - startTime) / duration, 1);
                let current = easeOut(progress) * target;
                counter.innerText = formatValue(current);
                if (progress < 1) {
                    requestAnimationFrame(animate);
                } else {
                    counter.innerText = formatValue(target);
                }
            }
            requestAnimationFrame(animate);
        });
    };

    function formatNumber(num) {
        if (num >= 10000000) return (num / 10000000).toFixed(1) + 'Cr';
        if (num >= 100000) return (num / 100000).toFixed(1) + 'L';
        if (num >= 1000) return (num / 1000).toFixed(1) + 'K';
        return num.toLocaleString('en-IN');
    }

    /* ===== DASHBOARD PAGE ===== */

    if (page === 'dashboard') {

        // Fetch KPI stats
        fetch(API + '/dashboard/stats')
            .then(res => res.json())
            .then(data => {
                const cards = document.querySelectorAll('.kpi-card');
                cards[0].querySelector('.kpi-value').dataset.target = data.total_customers;
                cards[1].querySelector('.kpi-value').dataset.target = data.total_orders;
                cards[2].querySelector('.kpi-value').dataset.target = data.total_revenue;
                cards[3].querySelector('.kpi-value').dataset.target = data.open_tickets;
                window.animateCounters();
            });

        // Fetch Revenue Chart
        fetch(API + '/dashboard/revenue-chart')
            .then(res => res.json())
            .then(chartData => {
                const el = document.getElementById('revenueChart');
                if (!el) return;
                const ctx = el.getContext('2d');
                const grad = ctx.createLinearGradient(0, 0, 0, 300);
                grad.addColorStop(0, 'rgba(59,130,246,0.25)');
                grad.addColorStop(1, 'rgba(59,130,246,0.01)');

                new Chart(el, {
                    type: 'line',
                    data: {
                        labels: chartData.labels,
                        datasets: [{
                            label: 'Revenue (₹)',
                            data: chartData.data,
                            borderColor: '#3b82f6',
                            borderWidth: 2.5,
                            backgroundColor: grad,
                            fill: true,
                            pointBackgroundColor: '#fff',
                            pointBorderColor: '#3b82f6',
                            pointRadius: 4,
                            pointHoverRadius: 7,
                            tension: 0.4
                        }]
                    },
                    options: {
                        responsive: true,
                        plugins: {
                            legend: { labels: { color: '#94a3b8', font: { family: 'Inter' }, usePointStyle: true } },
                            tooltip: {
                                backgroundColor: 'rgba(15,23,42,0.95)',
                                titleColor: '#f1f5f9', bodyColor: '#94a3b8',
                                borderColor: 'rgba(255,255,255,0.08)', borderWidth: 1,
                                cornerRadius: 10, padding: 12,
                                callbacks: {
                                    label: function (ctx) {
                                        return '₹' + ctx.parsed.y.toLocaleString('en-IN');
                                    }
                                }
                            }
                        },
                        scales: {
                            x: { ticks: { color: '#64748b' }, grid: { color: 'rgba(255,255,255,0.04)' } },
                            y: {
                                ticks: {
                                    color: '#64748b',
                                    callback: v => '₹' + (v / 1000) + 'K'
                                },
                                grid: { color: 'rgba(255,255,255,0.04)' }
                            }
                        }
                    }
                });
            });

        // Fetch Segment Chart
        fetch(API + '/dashboard/segments')
            .then(res => res.json())
            .then(segData => {
                const el = document.getElementById('segmentChart');
                if (!el) return;
                const colors = {
                    'Premium': 'rgba(139,92,246,0.85)',
                    'Regular': 'rgba(59,130,246,0.85)',
                    'New': 'rgba(34,197,94,0.85)'
                };
                new Chart(el, {
                    type: 'doughnut',
                    data: {
                        labels: segData.labels,
                        datasets: [{
                            data: segData.data,
                            backgroundColor: segData.labels.map(l => colors[l] || 'rgba(100,116,139,0.7)'),
                            borderColor: 'rgba(10,14,26,0.8)',
                            borderWidth: 3,
                            hoverOffset: 12
                        }]
                    },
                    options: {
                        responsive: true,
                        cutout: '65%',
                        plugins: {
                            legend: {
                                position: 'bottom',
                                labels: { color: '#94a3b8', font: { family: 'Inter' }, usePointStyle: true, padding: 16 }
                            }
                        }
                    }
                });
            });

        // Fetch Recent Activity
        fetch(API + '/dashboard/recent-activity')
            .then(res => res.json())
            .then(activities => {
                const feed = document.getElementById('activity-feed');
                if (!feed) return;
                feed.innerHTML = '';
                const colorMap = { green: 'var(--accent-green)', amber: 'var(--accent-amber)', purple: 'var(--accent-purple)', blue: 'var(--accent-blue)', red: 'var(--accent-red)' };

                activities.forEach(a => {
                    const item = document.createElement('div');
                    item.className = 'activity-item';
                    const dotColor = colorMap[a.color] || 'var(--accent-blue)';
                    const timeStr = new Date(a.time).toLocaleDateString('en-IN', { day: 'numeric', month: 'short' });
                    item.innerHTML = `
                        <div class="activity-dot" style="background: ${dotColor};"></div>
                        <div class="activity-text">${a.text}</div>
                        <div class="activity-time">${timeStr}</div>
                    `;
                    feed.appendChild(item);
                });
            });
    }

    /* ===== RUN COUNTERS (for non-dashboard pages with static targets) ===== */
    else {
        window.animateCounters();
    }
});