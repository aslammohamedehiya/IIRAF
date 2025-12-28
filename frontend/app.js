const API_BASE = "";

// Real-time pattern detection using HDBSCAN backend
let cachedPatterns = null;

async function fetchPatterns() {
    try {
        const res = await fetch(`${API_BASE}/api/patterns`);
        const data = await res.json();
        cachedPatterns = data.patterns || [];
        return cachedPatterns;
    } catch (e) {
        console.error("Failed to fetch patterns:", e);
        return [];
    }
}

// Severity prediction with debounce
let severityDebounceTimer = null;

async function predictSeverityOnInput() {
    clearTimeout(severityDebounceTimer);

    severityDebounceTimer = setTimeout(async () => {
        const query = document.getElementById('search-input').value.trim();

        if (query.length < 10) {
            // Hide prediction if query too short
            document.getElementById('severity-prediction').classList.add('hidden');
            document.getElementById('model-info').classList.add('hidden');
            return;
        }

        try {
            const res = await fetch(`${API_BASE}/api/predict/severity`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ query: query })
            });
            const data = await res.json();

            // Display severity prediction
            const predictionDiv = document.getElementById('severity-prediction');
            const badge = document.getElementById('severity-badge');
            const confidence = document.getElementById('severity-confidence');

            badge.innerText = data.severity;
            badge.className = `severity-badge severity-${data.severity.toLowerCase()}`;
            confidence.innerText = `${(data.confidence * 100).toFixed(0)}% confidence`;

            predictionDiv.classList.remove('hidden');

            // Fetch model info
            fetchModelInfo();
        } catch (e) {
            console.error("Severity prediction failed:", e);
        }
    }, 800); // Debounce 800ms
}

// Incident map visualization
let chartInstance = null;

async function loadIncidentMap() {
    const severityFilter = document.getElementById('severity-filter').value;

    try {
        showLoading('Loading incident visualization map...');

        let url = `${API_BASE}/api/visualization/incident-map`;
        if (severityFilter) {
            url += `?severity=${severityFilter}`;
        }

        const res = await fetch(url);
        const data = await res.json();

        hideLoading();

        if (data.error) {
            alert(data.error);
            return;
        }

        // Render scatter plot
        renderIncidentMap(data);

        // Show stats
        const statsDiv = document.getElementById('viz-stats');
        statsDiv.innerHTML = `
            <p><strong>Total Incidents:</strong> ${data.stats.total_incidents}</p>
            <p><strong>Severity Distribution:</strong> ${Object.entries(data.stats.severity_distribution).map(([k, v]) => `${k}: ${v}`).join(', ')}</p>
        `;

        // Refresh icons safely
        if (typeof lucide !== 'undefined' && lucide.createIcons) {
            lucide.createIcons();
        }
    } catch (e) {
        console.error("Visualization failed:", e);
        hideLoading();
        alert('Failed to load visualization. Please try again.');
    }
}

function renderIncidentMap(data) {
    const canvas = document.getElementById('incident-map-canvas');
    const ctx = canvas.getContext('2d');

    // Destroy existing chart
    if (chartInstance) {
        chartInstance.destroy();
    }

    // Prepare data for Chart.js
    const chartData = data.coordinates.map((coord, i) => ({
        x: coord[0],
        y: coord[1],
        incidentId: data.metadata.incident_ids[i],
        description: data.metadata.descriptions[i],
        severity: data.metadata.severities[i],
        backgroundColor: data.metadata.colors[i]
    }));

    // Create scatter plot
    chartInstance = new Chart(ctx, {
        type: 'scatter',
        data: {
            datasets: [{
                label: 'Incidents',
                data: chartData,
                backgroundColor: chartData.map(d => d.backgroundColor),
                pointRadius: 6,
                pointHoverRadius: 8
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: false
                },
                tooltip: {
                    callbacks: {
                        label: function (context) {
                            const point = context.raw;
                            return [
                                `ID: ${point.incidentId}`,
                                `Severity: ${point.severity}`,
                                `Description: ${point.description}`
                            ];
                        }
                    }
                }
            },
            scales: {
                x: {
                    title: {
                        display: true,
                        text: 'UMAP Dimension 1'
                    }
                },
                y: {
                    title: {
                        display: true,
                        text: 'UMAP Dimension 2'
                    }
                }
            }
        }
    });
}

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
        // DISABLED: Pattern detection and cluster details
        // checkPatterns(query);

        // DISABLED: Fetch and display cluster details
        // fetchClusterDetails(query);

        // Initialize lucide icons after all content is rendered
        if (typeof lucide !== 'undefined' && lucide.createIcons) {
            lucide.createIcons();
        }
    } catch (e) {
        console.error("Analysis failed", e);
        hideLoading();
        alert('Analysis failed. Please try again.');
    }
}

// Modal control functions
function openIncidentMapModal() {
    const modal = document.getElementById('incident-map-modal');
    modal.classList.add('active');

    // Load the map when modal opens
    loadIncidentMap();

    // Refresh icons
    if (typeof lucide !== 'undefined' && lucide.createIcons) {
        lucide.createIcons();
    }
}

function closeIncidentMapModal() {
    const modal = document.getElementById('incident-map-modal');
    modal.classList.remove('active');
}

// Incident Detail Modal Functions
function openIncidentDetailModal(incidentData) {
    const modal = document.getElementById('incident-detail-modal');

    // Populate modal with incident data
    document.getElementById('incident-modal-id').innerText = incidentData.id;
    document.getElementById('incident-modal-description').innerText = incidentData.text;
    document.getElementById('incident-modal-resolution').innerText = incidentData.resolution;
    document.getElementById('incident-modal-score').innerText = `${(incidentData.score * 100).toFixed(0)}%`;

    // Show modal
    modal.classList.add('active');
    modal.style.display = 'flex';

    // Refresh Lucide icons
    if (typeof lucide !== 'undefined' && lucide.createIcons) {
        lucide.createIcons();
    }
}

function closeIncidentDetailModal() {
    const modal = document.getElementById('incident-detail-modal');
    modal.classList.remove('active');
    modal.style.display = 'none';
}

// Close modal when clicking outside
document.addEventListener('click', function (event) {
    const modal = document.getElementById('incident-map-modal');
    if (event.target === modal) {
        closeIncidentMapModal();
    }

    const incidentModal = document.getElementById('incident-detail-modal');
    if (event.target === incidentModal) {
        closeIncidentDetailModal();
    }
});

// Close modal with ESC key
document.addEventListener('keydown', function (event) {
    if (event.key === 'Escape') {
        closeIncidentMapModal();
        closeIncidentDetailModal();
    }
});


function renderEvidence(results) {
    // Filter to show only incidents
    const incidents = results.filter(r => r.type === 'incident');
    const container = document.getElementById('evidence-list');

    // Handle empty state
    if (incidents.length === 0) {
        container.innerHTML = '<p style="color: #854d0e; font-size: 0.85rem; text-align: center; padding: 20px;">No similar incidents found. Query may be too different from existing incidents.</p>';
        return;
    }

    container.innerHTML = incidents.slice(0, 3).map((r, index) => `
        <div class="evidence-item" data-incident-index="${index}" style="cursor: pointer;">
            <div class="ev-content">
                <h4>
                    <i data-lucide="file-text" width="16"></i> 
                    ${r.id}: ${r.text.substring(0, 80)}${r.text.length > 80 ? '...' : ''}
                </h4>
                <p><strong>Resolution:</strong> ${r.resolution.substring(0, 100)}${r.resolution.length > 100 ? '...' : ''}</p>
                <div style="margin-top:4px; font-size:0.8em; color:#94a3b8">Matches: ${r.text.substring(0, 60)}...</div>
            </div>
            <div class="relevance-score">${(r.score * 100).toFixed(0)}%</div>
        </div>
    `).join('');

    // Store incident data globally for modal access
    window.incidentData = incidents;

    // Add click event listeners to each evidence item
    const evidenceItems = container.querySelectorAll('.evidence-item');
    evidenceItems.forEach((item, index) => {
        item.addEventListener('click', function () {
            openIncidentDetailModal(window.incidentData[index]);
        });
    });

    // Refresh Lucide icons after rendering
    if (typeof lucide !== 'undefined' && lucide.createIcons) {
        lucide.createIcons();
    }
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

async function checkPatterns(query) {
    // DISABLED: Pattern detection functionality
    return;

    const lowerQ = query.toLowerCase();

    // Fetch real patterns from HDBSCAN backend
    const patterns = await fetchPatterns();

    // Find matching pattern based on description similarity
    let match = null;
    for (const pattern of patterns) {
        if (pattern.pattern_id === 'ANOMALIES') continue; // Skip anomalies

        const desc = pattern.description.toLowerCase();
        // Check if query matches pattern description keywords
        const keywords = lowerQ.split(' ').filter(w => w.length > 3);
        const matchCount = keywords.filter(kw => desc.includes(kw)).length;

        if (matchCount > 0) {
            match = pattern;
            break;
        }
    }

    const patternPanel = document.getElementById('pattern-panel');
    const autohealPanel = document.getElementById('autoheal-panel');

    if (match) {
        // Show panels
        patternPanel.classList.remove('hidden');
        autohealPanel.classList.remove('hidden');

        // Populate with real HDBSCAN data
        document.getElementById('pattern-id').innerText = match.pattern_id;
        document.getElementById('pattern-desc').innerText = match.description;
        document.getElementById('pattern-freq').innerText = `${match.frequency} times`;

        // Generate auto-heal script based on pattern
        const script = generateAutoHealScript(match);
        document.getElementById('heal-script').innerText = script;
    } else {
        // Hide if no pattern
        patternPanel.classList.add('hidden');
        autohealPanel.classList.add('hidden');
    }
}

function generateAutoHealScript(pattern) {
    // Generate appropriate script based on pattern description
    const desc = pattern.description.toLowerCase();

    if (desc.includes('wireless') || desc.includes('network')) {
        return 'kubectl restart deployment wireless-gateway -n network';
    } else if (desc.includes('fios') || desc.includes('fiber')) {
        return 'systemctl restart fios-service && check-fiber-health.sh';
    } else if (desc.includes('payment') || desc.includes('gateway')) {
        return './restart_svc.sh -n payment -r us-east';
    } else {
        return `# Auto-heal for ${pattern.pattern_id}\nkubectl restart deployment app-service`;
    }
}

async function runRemediation() {
    const script = document.getElementById('heal-script').innerText;
    const btn = document.querySelector('.remediation-btn');
    const status = document.getElementById('remediation-status');

    btn.disabled = true;
    btn.innerHTML = '<i data-lucide="loader"></i> Running...';
    if (typeof lucide !== 'undefined' && lucide.createIcons) {
        lucide.createIcons();
    }

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
            if (typeof lucide !== 'undefined' && lucide.createIcons) {
                lucide.createIcons();
            }
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

// Fetch and display cluster details
async function fetchClusterDetails(query) {
    // DISABLED: Cluster details functionality
    return;

    try {
        const res = await fetch(`${API_BASE}/api/patterns/clusters`);
        const data = await res.json();

        if (data.clusters && data.clusters.length > 0) {
            // Find the most relevant cluster based on query
            const cluster = data.clusters[0]; // For now, show the first cluster

            // Show cluster panel
            const clusterPanel = document.getElementById('cluster-panel');
            clusterPanel.classList.remove('hidden');

            // Populate cluster details
            document.getElementById('cluster-id').innerText = cluster.pattern_id;
            document.getElementById('cluster-size').innerText = cluster.frequency;
            document.getElementById('cluster-description').innerText = cluster.description;

            // Populate representative incidents
            const incidentsList = document.getElementById('cluster-incidents-list');
            if (cluster.sample_incidents && cluster.sample_incidents.length > 0) {
                incidentsList.innerHTML = cluster.sample_incidents
                    .slice(0, 5)
                    .map(inc => `<li>${inc}</li>`)
                    .join('');
            } else {
                incidentsList.innerHTML = '<li>No sample incidents available</li>';
            }

            // Refresh icons
            if (typeof lucide !== 'undefined' && lucide.createIcons) {
                lucide.createIcons();
            }
        } else {
            // Hide cluster panel if no clusters
            document.getElementById('cluster-panel').classList.add('hidden');
        }
    } catch (e) {
        console.error("Failed to fetch cluster details:", e);
        document.getElementById('cluster-panel').classList.add('hidden');
    }
}

// Fetch and display model info
async function fetchModelInfo() {
    try {
        const res = await fetch(`${API_BASE}/api/predict/model-info`);
        const data = await res.json();

        if (data.error) {
            console.error("Model info error:", data.error);
            return;
        }

        // Populate model info
        const accuracy = data.accuracy || data.test_accuracy || 0;
        document.getElementById('model-accuracy').innerHTML =
            `<span class="accuracy-badge">${(accuracy * 100).toFixed(1)}%</span>`;
        document.getElementById('model-samples').innerText = data.training_samples || '-';
        document.getElementById('model-trained').innerText = data.last_trained || 'Unknown';
    } catch (e) {
        console.error("Failed to fetch model info:", e);
    }
}

// Toggle model info display
function toggleModelInfo() {
    const modelInfo = document.getElementById('model-info');
    modelInfo.classList.toggle('hidden');
}

