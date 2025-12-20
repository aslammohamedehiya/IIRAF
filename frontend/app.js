const API_BASE = "";

// Static mappings for demo purposes, since backend data is random synthetic
const MOCK_PATTERNS_MAP = {
    "payment": {
        id: "P002",
        desc: "Payment Gateway Timeout Cluster B",
        freq: 45,
        script: "./restart_svc.sh -n payment -r us-east"
    },
    "vpn": {
        id: "P005",
        desc: "VPN Concentrator Certified Expired",
        freq: 12,
        script: "certbot renew --force-renewal --cert-name vpn"
    },
    "email": {
        id: "P008",
        desc: "Outlook Exchange Sync Timeout",
        freq: 8,
        script: "Restart-Service MSExchangeIS"
    }
};

document.addEventListener("DOMContentLoaded", () => {
    // Initialize with empty state - no auto-analysis
    showEmptyState();
});

async function performAnalysis() {
    const query = document.getElementById('search-input').value;
    if (!query) {
        alert('Please enter an issue description');
        return;
    }

    // Show loading state
    showLoading('Searching knowledge base and analyzing incidents...');

    // 1. Search Knowledge Base
    try {
        const res = await fetch(`${API_BASE}/api/search`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ query: query })
        });
        const data = await res.json();

        // Update loading message for AI generation
        showLoading('Generating AI-powered solution recommendations...');

        // 2. Generate AI Solution
        const solutionRes = await fetch(`${API_BASE}/api/generate-solution`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                query: query,
                results: data.results
            })
        });
        const solutionData = await solutionRes.json();

        // Hide loading and show results
        hideLoading();

        renderEvidence(data.results);
        renderKBArticles(data.results);
        renderAISolution(solutionData, data.results);
        checkPatterns(query);

        // Initialize lucide icons after all content is rendered
        if (typeof lucide !== 'undefined') {
            lucide.createIcons();
        }
    } catch (e) {
        console.error("Analysis failed", e);
        hideLoading();
        alert('Analysis failed. Please try again.');
    }
}

function renderEvidence(results) {
    // Filter to show only incidents
    const incidents = results.filter(r => r.type === 'incident');
    const container = document.getElementById('evidence-list');
    container.innerHTML = incidents.slice(0, 3).map(r => `
        <div class="evidence-item">
            <div class="ev-content">
                <h4>
                    <i data-lucide="file-text" width="16"></i> 
                    ${r.id}: ${r.text.substring(0, 80)}${r.text.length > 80 ? '...' : ''}
                </h4>
                <p><strong>Resolution:</strong> ${r.resolution}</p>
                <div style="margin-top:4px; font-size:0.8em; color:#94a3b8">Matches: ${r.text.substring(0, 60)}...</div>
            </div>
            <div class="relevance-score">${(r.score * 100).toFixed(0)}%</div>
        </div>
    `).join('');
}

function renderKBArticles(results) {
    // Filter to show only KB articles
    const kbArticles = results.filter(r => r.type === 'kb');
    const container = document.getElementById('kb-articles-list');

    if (kbArticles.length === 0) {
        container.innerHTML = '<p style="color: #854d0e; font-size: 0.85rem; text-align: center;">No KB articles found for this query.</p>';
        return;
    }

    container.innerHTML = kbArticles.slice(0, 3).map(r => `
        <div class="kb-article-item">
            <h4>
                <i data-lucide="book-open" width="16"></i> 
                ${r.id}: ${r.title || 'KB Article'}
            </h4>
            <p><strong>Content:</strong> ${r.content}</p>
            <div style="margin-top:4px; font-size:0.8em; color:#94a3b8">Matches: ${r.text.substring(0, 60)}...</div>
            <div class="kb-relevance">Relevance: ${(r.score * 100).toFixed(0)}%</div>
        </div>
    `).join('');
}

function renderAISolution(solutionData, results) {
    // Dynamically update counts
    const incCount = results.filter(r => r.type === 'incident').length;
    const kbCount = results.filter(r => r.type === 'kb').length;

    document.getElementById('inc-count').innerText = `${incCount} similar incidents`;
    document.getElementById('kb-count').innerText = `${kbCount} KB articles`;

    const stepsContainer = document.getElementById('resolution-steps');
    const steps = solutionData.steps || [];

    if (steps.length > 0) {
        stepsContainer.innerHTML = steps.map((step, idx) =>
            `<li><strong>Step ${idx + 1}:</strong> ${step}</li>`
        ).join('');
    } else {
        stepsContainer.innerHTML = '<li>No clear resolution found in similar records. Please investigate manually.</li>';
    }

    // Update tags with source indicator
    const tagsContainer = document.getElementById('solution-tags');
    const sourceTags = results.slice(0, 4).map(r => `<span class="tag">${r.id}</span>`).join('');

    // Add AI badge if generated by AI
    const aiBadge = solutionData.source === 'ai_generated'
        ? '<span class="tag" style="background: #10b981; color: white; border-color: #10b981;">✨ AI Generated</span>'
        : '<span class="tag" style="background: #f59e0b; color: white; border-color: #f59e0b;">📋 Aggregated</span>';

    tagsContainer.innerHTML = aiBadge + sourceTags;
}

function checkPatterns(query) {
    const lowerQ = query.toLowerCase();
    let match = null;

    // Simple keyword match for demo
    for (const [key, pat] of Object.entries(MOCK_PATTERNS_MAP)) {
        if (lowerQ.includes(key)) {
            match = pat;
            break;
        }
    }

    const patternPanel = document.getElementById('pattern-panel');
    const autohealPanel = document.getElementById('autoheal-panel');

    if (match) {
        // Show panels
        patternPanel.classList.remove('hidden');
        autohealPanel.classList.remove('hidden');

        // Populate Data
        document.getElementById('pattern-id').innerText = match.id;
        document.getElementById('pattern-desc').innerText = match.desc;
        document.getElementById('pattern-freq').innerText = `${match.freq} times`;
        document.getElementById('heal-script').innerText = match.script;
    } else {
        // Hide if no pattern
        patternPanel.classList.add('hidden');
        autohealPanel.classList.add('hidden');
    }
}

async function runRemediation() {
    const script = document.getElementById('heal-script').innerText;
    const btn = document.querySelector('.remediation-btn');
    const status = document.getElementById('remediation-status');

    btn.disabled = true;
    btn.innerHTML = '<i data-lucide="loader"></i> Running...';
    lucide.createIcons();

    // Call backend
    try {
        const res = await fetch(`${API_BASE}/api/heal`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ action: script, target: "payment-gateway" })
        });
        const result = await res.json();

        // UI Feedback
        setTimeout(() => {
            btn.innerHTML = '<i data-lucide="check"></i> Remediated';
            btn.style.background = '#059669';
            status.innerText = `Success: Executed at ${new Date().toLocaleTimeString()}`;
            lucide.createIcons();
        }, 1500);

    } catch (e) {
        btn.innerHTML = 'Failed';
        btn.style.background = '#ef4444';
    }
}

function showEmptyState() {
    // Clear all content areas
    document.getElementById('evidence-list').innerHTML = '<p style="color: #94a3b8; text-align: center; padding: 2rem;">Enter a query and click Analyze to see results</p>';
    document.getElementById('kb-articles-list').innerHTML = '<p style="color: #94a3b8; text-align: center; padding: 2rem;">No KB articles loaded yet</p>';
    document.getElementById('resolution-steps').innerHTML = '<li>Enter an issue description above to get AI-generated recommendations</li>';
    document.getElementById('solution-tags').innerHTML = '';
    document.getElementById('inc-count').innerText = '0 similar incidents';
    document.getElementById('kb-count').innerText = '0 KB articles';

    // Hide pattern and autoheal panels
    document.getElementById('pattern-panel').classList.add('hidden');
    document.getElementById('autoheal-panel').classList.add('hidden');
}

function showLoading(message = 'Analyzing incident and searching knowledge base...') {
    // Create and show loading overlay
    const existingLoader = document.getElementById('loading-overlay');
    if (existingLoader) {
        // Update message if loader already exists
        const messageEl = existingLoader.querySelector('p');
        if (messageEl) {
            messageEl.textContent = message;
        }
        existingLoader.style.display = 'flex';
        return;
    }

    const loader = document.createElement('div');
    loader.id = 'loading-overlay';
    loader.innerHTML = `
        <div class="loader-content">
            <div class="spinner"></div>
            <p>${message}</p>
        </div>
    `;
    document.body.appendChild(loader);
}

function hideLoading() {
    const loader = document.getElementById('loading-overlay');
    if (loader) {
        loader.style.display = 'none';
    }
}

