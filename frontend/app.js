const socket = io();
let threatChart;

document.addEventListener('DOMContentLoaded', () => {
    refreshData();
    initChart();
    setInterval(refreshData, 5000);
    
    socket.on('threat_detected', (data) => {
        alert(`🚨 THREAT DETECTED!\n\nIP: ${data.source_ip}\nRisk Score: ${data.risk_score}\nSeverity: ${data.severity}\nIndicators: ${data.indicators.join(', ')}`);
        refreshData();
    });
});

async function refreshData() {
    await Promise.all([
        fetchStats(),
        fetchTokens(),
        fetchThreats()
    ]);
    updateChart();
}

async function fetchStats() {
    const res = await fetch('/api/stats');
    const data = await res.json();
    document.getElementById('total-tokens').textContent = data.total_tokens;
    document.getElementById('critical-threats').textContent = data.critical_threats;
    document.getElementById('high-threats').textContent = data.high_threats;
    document.getElementById('contained').textContent = data.contained_threats;
}

async function fetchTokens() {
    const res = await fetch('/api/honeytokens');
    const tokens = await res.json();
    const list = document.getElementById('tokens-list');
    list.innerHTML = tokens.length ? tokens.map(t => `
        <div class="list-item">
            <strong>${t.token_type}</strong> - ${t.location}<br>
            <span class="timestamp">Created: ${new Date(t.created_at).toLocaleString()}</span>
        </div>
    `).join('') : '<p>No tokens deployed</p>';
}

async function fetchThreats() {
    const res = await fetch('/api/threats');
    const threats = await res.json();
    const list = document.getElementById('threats-list');
    list.innerHTML = threats.length ? threats.map(t => `
        <div class="list-item ${t.severity}">
            <strong>${t.event_type}</strong> from ${t.source_ip}<br>
            ${t.description}<br>
            ${t.contained ? '✅ CONTAINED' : '⚠️ ACTIVE'}
            <br><span class="timestamp">${new Date(t.timestamp).toLocaleString()}</span>
        </div>
    `).join('') : '<p>No threats detected</p>';
}

async function generateToken(type) {
    const res = await fetch('/api/honeytokens/generate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ type, location: '/generated/' })
    });
    const data = await res.json();
    alert(`Token generated: ${JSON.stringify(data, null, 2)}`);
    refreshData();
}

async function deployCanary() {
    const res = await fetch('/api/honeytokens/canary', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ target: './deployed/', filename: 'backup.txt' })
    });
    const data = await res.json();
    alert(`Canary deployed: ${data.filepath}`);
    refreshData();
}

async function deployCreds() {
    await fetch('/api/credentials/deploy', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ directory: './deployed_creds/' })
    });
    alert('Credential deception deployed');
    refreshData();
}

async function generateDoc(type) {
    const res = await fetch('/api/documents/generate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ type, target: './deployed_docs/' })
    });
    const data = await res.json();
    alert(`Document created: ${data.filepath}`);
    refreshData();
}

async function deploySourceCode() {
    await fetch('/api/sourcecode/deploy', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ directory: './deployed_code/' })
    });
    alert('Source code deception deployed');
    refreshData();
}

async function deployCloud(provider) {
    const res = await fetch('/api/cloud/deploy', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ type: provider })
    });
    const data = await res.json();
    alert(`Cloud token deployed: ${JSON.stringify(data, null, 2)}`);
    refreshData();
}

async function simulateAttack() {
    const res = await fetch('/api/simulate-attack', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({})
    });
    const data = await res.json();
    refreshData();
}

function initChart() {
    const ctx = document.getElementById('threatChart').getContext('2d');
    threatChart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: ['Critical', 'High', 'Medium', 'Low', 'Contained'],
            datasets: [{
                label: 'Threat Distribution',
                data: [0, 0, 0, 0, 0],
                backgroundColor: ['#ff3366', '#ff9933', '#ffcc00', '#00aaff', '#00ff88']
            }]
        },
        options: {
            responsive: true,
            plugins: {
                legend: { labels: { color: '#00ff88' } }
            },
            scales: {
                y: { ticks: { color: '#00ff88' }, grid: { color: '#2a3f5a' } },
                x: { ticks: { color: '#00ff88' }, grid: { color: '#2a3f5a' } }
            }
        }
    });
}

async function updateChart() {
    const res = await fetch('/api/stats');
    const data = await res.json();
    threatChart.data.datasets[0].data = [
        data.critical_threats || 0,
        data.high_threats || 0,
        data.medium_threats || 0,
        data.low_threats || 0,
        data.contained_threats || 0
    ];
    threatChart.update();
}