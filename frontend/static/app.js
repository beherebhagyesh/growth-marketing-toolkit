const API_BASE = '';

// Tab switching
document.querySelectorAll('.tab').forEach(tab => {
    tab.addEventListener('click', () => {
        document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
        document.querySelectorAll('.tab-content').forEach(c => c.classList.remove('active'));
        tab.classList.add('active');
        document.getElementById(tab.dataset.tab).classList.add('active');
    });
});

function showLoading(elementId) {
    document.getElementById(elementId).innerHTML = `
        <div class="loading">
            <div class="spinner"></div>
            <span>Loading...</span>
        </div>
    `;
    document.getElementById(elementId).classList.add('show');
}

function showResult(elementId, data) {
    const el = document.getElementById(elementId);
    el.classList.add('show');
    
    if (elementId === 'pagespeed-results' && data.scores) {
        const scores = data.scores;
        const opportunities = data.opportunities || [];
        
        let html = `
            <div class="score-card">
                <div class="score ${scores.performance >= 90 ? 'good' : scores.performance >= 50 ? 'warning' : 'bad'}">
                    <div class="value">${scores.performance.toFixed(0)}</div>
                    <div class="label">Performance</div>
                </div>
                <div class="score ${scores.accessibility >= 90 ? 'good' : scores.accessibility >= 50 ? 'warning' : 'bad'}">
                    <div class="value">${scores.accessibility.toFixed(0)}</div>
                    <div class="label">Accessibility</div>
                </div>
                <div class="score ${scores['best_practices'] >= 90 ? 'good' : scores['best_practices'] >= 50 ? 'warning' : 'bad'}">
                    <div class="value">${scores['best_practices'].toFixed(0)}</div>
                    <div class="label">Best Practices</div>
                </div>
                <div class="score ${scores.seo >= 90 ? 'good' : scores.seo >= 50 ? 'warning' : 'bad'}">
                    <div class="value">${scores.seo.toFixed(0)}</div>
                    <div class="label">SEO</div>
                </div>
            </div>
        `;
        
        if (opportunities.length > 0) {
            html += '<h3>Opportunities</h3>';
            opportunities.slice(0, 5).forEach(opp => {
                html += `
                    <div class="opportunity ${opp.impact === 'high' ? 'high' : ''}">
                        <div class="opportunity-title">${opp.title}</div>
                        <div class="opportunity-impact">${opp.impact} impact - Score: ${opp.score.toFixed(0)}</div>
                    </div>
                `;
            });
        }
        
        el.innerHTML = html;
    } else {
        el.innerHTML = `<pre>${JSON.stringify(data, null, 2)}</pre>`;
    }
}

function showError(elementId, error) {
    document.getElementById(elementId).innerHTML = `
        <div style="color: #ef4444; padding: 1rem;">
            Error: ${error}
        </div>
    `;
    document.getElementById(elementId).classList.add('show');
}

// Analytics functions
async function trackEvent() {
    const eventName = document.getElementById('event-name').value;
    const propsStr = document.getElementById('event-props').value;
    
    if (!eventName) {
        alert('Please enter an event name');
        return;
    }
    
    let properties = {};
    if (propsStr) {
        try {
            properties = JSON.parse(propsStr);
        } catch (e) {
            alert('Invalid JSON in properties');
            return;
        }
    }
    
    showLoading('analytics-results');
    
    try {
        const res = await fetch('/api/analytics/track', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ event_name: eventName, properties })
        });
        const data = await res.json();
        showResult('analytics-results', data);
    } catch (e) {
        showError('analytics-results', e.message);
    }
}

async function checkEvents() {
    const eventsStr = document.getElementById('check-events').value;
    
    if (!eventsStr) {
        alert('Please enter event names');
        return;
    }
    
    const events = eventsStr.split(',').map(e => e.trim()).filter(e => e);
    
    showLoading('analytics-results');
    
    try {
        const res = await fetch('/api/analytics/check', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(events)
        });
        const data = await res.json();
        showResult('analytics-results', data);
    } catch (e) {
        showError('analytics-results', e.message);
    }
}

async function getReport() {
    const query = document.getElementById('analytics-query').value;
    
    if (!query) {
        alert('Please enter a query');
        return;
    }
    
    showLoading('analytics-results');
    
    try {
        const res = await fetch('/api/analytics/report', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(query)
        });
        const data = await res.json();
        showResult('analytics-results', data);
    } catch (e) {
        showError('analytics-results', e.message);
    }
}

// SEO functions
async function createUniverse() {
    const keywordsStr = document.getElementById('seed-keywords').value;
    
    if (!keywordsStr) {
        alert('Please enter seed keywords');
        return;
    }
    
    const keywords = keywordsStr.split(',').map(k => k.trim()).filter(k => k);
    
    showLoading('seo-results');
    
    try {
        const res = await fetch('/api/seo/universe', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ keywords })
        });
        const data = await res.json();
        showResult('seo-results', data);
    } catch (e) {
        showError('seo-results', e.message);
    }
}

async function optimizePage() {
    const url = document.getElementById('optimize-url').value;
    const keywordsStr = document.getElementById('target-keywords').value;
    
    if (!url || !keywordsStr) {
        alert('Please enter URL and keywords');
        return;
    }
    
    const keywords = keywordsStr.split(',').map(k => k.trim()).filter(k => k);
    
    showLoading('seo-results');
    
    try {
        const res = await fetch('/api/seo/optimize', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ url, keywords })
        });
        const data = await res.json();
        showResult('seo-results', data);
    } catch (e) {
        showError('seo-results', e.message);
    }
}

async function createPage() {
    const keyword = document.getElementById('new-keyword').value;
    const competitorsStr = document.getElementById('competitors').value;
    
    if (!keyword || !competitorsStr) {
        alert('Please enter keyword and competitors');
        return;
    }
    
    const competitors = competitorsStr.split(',').map(c => c.trim()).filter(c => c);
    
    showLoading('seo-results');
    
    try {
        const res = await fetch('/api/seo/create-page', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ keyword, competitors })
        });
        const data = await res.json();
        showResult('seo-results', data);
    } catch (e) {
        showError('seo-results', e.message);
    }
}

// Indexing functions
async function analyzeIndexing() {
    const sitemapPath = document.getElementById('sitemap-path').value;
    const gscPath = document.getElementById('gsc-path').value;
    
    if (!sitemapPath) {
        alert('Please enter a sitemap URL or path');
        return;
    }
    
    showLoading('indexing-results');
    
    try {
        const res = await fetch('/api/indexing/analyze', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ 
                sitemap_path: sitemapPath,
                gsc_path: gscPath || null
            })
        });
        const data = await res.json();
        showResult('indexing-results', data);
    } catch (e) {
        showError('indexing-results', e.message);
    }
}

// Pagespeed functions
async function runPagespeed() {
    const url = document.getElementById('pagespeed-url').value;
    const optimize = document.getElementById('optimize-mode').checked;
    
    if (!url) {
        alert('Please enter a URL');
        return;
    }
    
    showLoading('pagespeed-results');
    
    try {
        const res = await fetch('/api/pagespeed/analyze', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ url, optimize })
        });
        const data = await res.json();
        showResult('pagespeed-results', data.data || data);
    } catch (e) {
        showError('pagespeed-results', e.message);
    }
}
