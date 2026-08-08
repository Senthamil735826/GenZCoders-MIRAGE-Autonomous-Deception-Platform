from fastapi import APIRouter
from fastapi.responses import HTMLResponse

router = APIRouter()

DASHBOARD_HTML = r"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>MIRAGE Threat Dashboard</title>

    <style>
        :root {
            --bg: #07111f;
            --panel: #0d1b2e;
            --panel2: #10243b;
            --border: #1e3a56;
            --text: #e6f1ff;
            --muted: #91a7bf;
            --cyan: #38d9ff;
            --green: #35d07f;
            --yellow: #ffc857;
            --red: #ff5c77;
            --purple: #a78bfa;
        }

        * {
            box-sizing: border-box;
        }

        body {
            margin: 0;
            padding: 24px;
            background: var(--bg);
            color: var(--text);
            font-family: Arial, Helvetica, sans-serif;
        }

        .container {
            max-width: 1400px;
            margin: auto;
        }

        header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            gap: 20px;
            margin-bottom: 24px;
            flex-wrap: wrap;
        }

        h1 {
            margin: 0 0 6px;
            color: var(--cyan);
            letter-spacing: 1px;
        }

        h2 {
            margin-top: 0;
            font-size: 18px;
        }

        .subtitle {
            color: var(--muted);
        }

        .auth-box {
            display: flex;
            gap: 8px;
            flex-wrap: wrap;
        }

        input {
            min-width: 310px;
            padding: 11px 13px;
            border: 1px solid var(--border);
            border-radius: 7px;
            background: #081525;
            color: white;
        }

        button {
            padding: 11px 16px;
            border: 0;
            border-radius: 7px;
            cursor: pointer;
            color: #00131e;
            background: var(--cyan);
            font-weight: bold;
        }

        button:hover {
            filter: brightness(1.12);
        }

        .status {
            margin: 12px 0 20px;
            color: var(--muted);
        }

        .status.ok {
            color: var(--green);
        }

        .status.error {
            color: var(--red);
        }

        .cards {
            display: grid;
            grid-template-columns: repeat(4, 1fr);
            gap: 16px;
            margin-bottom: 20px;
        }

        .card,
        .panel {
            background: var(--panel);
            border: 1px solid var(--border);
            border-radius: 12px;
            box-shadow: 0 8px 25px rgba(0, 0, 0, 0.18);
        }

        .card {
            padding: 20px;
        }

        .card-label {
            color: var(--muted);
            font-size: 13px;
            margin-bottom: 10px;
        }

        .card-value {
            font-size: 32px;
            font-weight: bold;
        }

        .cyan {
            color: var(--cyan);
        }

        .green {
            color: var(--green);
        }

        .yellow {
            color: var(--yellow);
        }

        .red {
            color: var(--red);
        }

        .grid {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 20px;
            margin-bottom: 20px;
        }

        .panel {
            padding: 20px;
            overflow: hidden;
        }

        .bar-row {
            display: grid;
            grid-template-columns: 130px 1fr 40px;
            align-items: center;
            gap: 10px;
            margin: 13px 0;
            font-size: 13px;
        }

        .bar-track {
            height: 12px;
            border-radius: 10px;
            background: #172d45;
            overflow: hidden;
        }

        .bar-fill {
            height: 100%;
            background: linear-gradient(90deg, var(--cyan), var(--purple));
            border-radius: 10px;
        }

        .table-wrap {
            overflow-x: auto;
        }

        table {
            width: 100%;
            border-collapse: collapse;
            font-size: 13px;
        }

        th,
        td {
            text-align: left;
            padding: 11px 8px;
            border-bottom: 1px solid var(--border);
            white-space: nowrap;
        }

        th {
            color: var(--muted);
            font-weight: normal;
        }

        .badge {
            display: inline-block;
            padding: 4px 8px;
            border-radius: 20px;
            font-size: 11px;
            font-weight: bold;
        }

        .critical {
            color: #ffdce2;
            background: #7d2035;
        }

        .high {
            color: #ffe9bd;
            background: #704b14;
        }

        .medium {
            color: #dbe8ff;
            background: #24456d;
        }

        .dry-run {
            color: #ffe9bd;
            background: #704b14;
        }

        .executed {
            color: #caffdf;
            background: #155b3a;
        }

        .empty {
            padding: 25px 0;
            color: var(--muted);
            text-align: center;
        }

        .footer-note {
            color: var(--muted);
            font-size: 12px;
            margin-top: 22px;
        }

        @media (max-width: 950px) {
            .cards {
                grid-template-columns: repeat(2, 1fr);
            }

            .grid {
                grid-template-columns: 1fr;
            }
        }

        @media (max-width: 560px) {
            body {
                padding: 12px;
            }

            .cards {
                grid-template-columns: 1fr;
            }

            input {
                min-width: 100%;
            }
        }
    </style>
</head>

<body>
<div class="container">
    <header>
        <div>
            <h1>MIRAGE</h1>
            <div class="subtitle">
                Autonomous Deception Intelligence Platform
            </div>
        </div>

        <div class="auth-box">
            <input
                id="apiKey"
                type="password"
                placeholder="Enter MIRAGE API key"
                autocomplete="off"
            >
            <button id="connectButton">Load Dashboard</button>
            <button id="refreshButton">Refresh</button>
        </div>
    </header>

    <div id="status" class="status">
        Enter your API key to load protected telemetry.
    </div>

    <section class="cards">
        <div class="card">
            <div class="card-label">Total Honeytokens</div>
            <div id="tokensTotal" class="card-value cyan">—</div>
        </div>

        <div class="card">
            <div class="card-label">Triggered Tokens</div>
            <div id="tokensTriggered" class="card-value red">—</div>
        </div>

        <div class="card">
            <div class="card-label">Trigger Events</div>
            <div id="triggerEvents" class="card-value yellow">—</div>
        </div>

        <div class="card">
            <div class="card-label">Unique Attacker IPs</div>
            <div id="attackerIps" class="card-value green">—</div>
        </div>
    </section>

    <section class="grid">
        <div class="panel">
            <h2>Honeytokens by Type</h2>
            <div id="tokenTypes">
                <div class="empty">No data</div>
            </div>
        </div>

        <div class="panel">
            <h2>Recent Telemetry</h2>
            <div class="table-wrap">
                <table>
                    <thead>
                    <tr>
                        <th>Time</th>
                        <th>Source IP</th>
                        <th>Token</th>
                        <th>Severity</th>
                        <th>Score</th>
                    </tr>
                    </thead>
                    <tbody id="eventsBody">
                    <tr>
                        <td colspan="5" class="empty">No events</td>
                    </tr>
                    </tbody>
                </table>
            </div>
        </div>
    </section>

    <section class="grid">
        <div class="panel">
            <h2>Automated Containment</h2>
            <div class="table-wrap">
                <table>
                    <thead>
                    <tr>
                        <th>Time</th>
                        <th>IP</th>
                        <th>Action</th>
                        <th>Status</th>
                    </tr>
                    </thead>
                    <tbody id="actionsBody">
                    <tr>
                        <td colspan="4" class="empty">No containment actions</td>
                    </tr>
                    </tbody>
                </table>
            </div>
        </div>

        <div class="panel">
            <h2>Honeytoken Inventory</h2>
            <div class="table-wrap">
                <table>
                    <thead>
                    <tr>
                        <th>Name</th>
                        <th>Type</th>
                        <th>Sensitivity</th>
                        <th>Triggers</th>
                        <th>Status</th>
                    </tr>
                    </thead>
                    <tbody id="tokensBody">
                    <tr>
                        <td colspan="5" class="empty">No tokens</td>
                    </tr>
                    </tbody>
                </table>
            </div>
        </div>
    </section>

    <div class="footer-note">
        Dashboard refreshes automatically every 5 seconds. DRY_RUN containment actions are recorded but do not modify the host firewall.
    </div>
</div>

<script>
    const apiKeyInput = document.getElementById("apiKey");
    const statusElement = document.getElementById("status");

    const savedKey = localStorage.getItem("mirage_api_key");
    if (savedKey) {
        apiKeyInput.value = savedKey;
    }

    function escapeHtml(value) {
        return String(value ?? "")
            .replaceAll("&", "&amp;")
            .replaceAll("<", "&lt;")
            .replaceAll(">", "&gt;")
            .replaceAll('"', "&quot;")
            .replaceAll("'", "&#039;");
    }

    function currentKey() {
        return apiKeyInput.value.trim();
    }

    function formatDate(value) {
        if (!value) {
            return "—";
        }

        return new Date(value).toLocaleString();
    }

    function severityBadge(severity) {
        const value = String(severity || "unknown").toLowerCase();
        return `<span class="badge ${escapeHtml(value)}">${escapeHtml(value)}</span>`;
    }

    function statusBadge(status) {
        const value = String(status || "unknown").toLowerCase();
        const css = value.replace("_", "-");
        return `<span class="badge ${escapeHtml(css)}">${escapeHtml(value)}</span>`;
    }

    async function getJson(path) {
        const key = currentKey();

        if (!key) {
            throw new Error("Enter your MIRAGE API key first.");
        }

        const response = await fetch(path, {
            method: "GET",
            headers: {
                "X-API-Key": key
            }
        });

        const text = await response.text();

        let data;
        try {
            data = text ? JSON.parse(text) : {};
        } catch {
            data = { detail: text };
        }

        if (!response.ok) {
            throw new Error(`${response.status}: ${data.detail || "Request failed"}`);
        }

        return data;
    }

    function renderTypes(types) {
        const container = document.getElementById("tokenTypes");
        const entries = Object.entries(types || {});

        if (!entries.length) {
            container.innerHTML = '<div class="empty">No token data</div>';
            return;
        }

        const maximum = Math.max(...entries.map(item => Number(item[1])), 1);

        container.innerHTML = entries.map(([type, count]) => {
            const width = Math.max(5, (Number(count) / maximum) * 100);

            return `
                <div class="bar-row">
                    <span>${escapeHtml(type)}</span>
                    <div class="bar-track">
                        <div class="bar-fill" style="width: ${width}%"></div>
                    </div>
                    <strong>${escapeHtml(count)}</strong>
                </div>
            `;
        }).join("");
    }

    function renderEvents(events) {
        const body = document.getElementById("eventsBody");

        if (!events || !events.length) {
            body.innerHTML = '<tr><td colspan="5" class="empty">No events</td></tr>';
            return;
        }

        body.innerHTML = events.slice(0, 15).map(event => `
            <tr>
                <td>${escapeHtml(formatDate(event.occurred_at))}</td>
                <td>${escapeHtml(event.source_ip)}</td>
                <td>#${escapeHtml(event.token_id)}</td>
                <td>${severityBadge(event.severity)}</td>
                <td>${escapeHtml(event.threat_score)}</td>
            </tr>
        `).join("");
    }

    function renderActions(actions) {
        const body = document.getElementById("actionsBody");

        if (!actions || !actions.length) {
            body.innerHTML = '<tr><td colspan="4" class="empty">No containment actions</td></tr>';
            return;
        }

        body.innerHTML = actions.slice(0, 15).map(action => `
            <tr>
                <td>${escapeHtml(formatDate(action.created_at))}</td>
                <td>${escapeHtml(action.attacker_ip)}</td>
                <td>${escapeHtml(action.action_type)}</td>
                <td>${statusBadge(action.status)}</td>
            </tr>
        `).join("");
    }

    function renderTokens(tokens) {
        const body = document.getElementById("tokensBody");

        if (!tokens || !tokens.length) {
            body.innerHTML = '<tr><td colspan="5" class="empty">No tokens</td></tr>';
            return;
        }

        body.innerHTML = tokens.slice(0, 15).map(token => `
            <tr>
                <td>${escapeHtml(token.name)}</td>
                <td>${escapeHtml(token.token_type)}</td>
                <td>${escapeHtml(token.sensitivity)}/10</td>
                <td>${escapeHtml(token.trigger_count)}</td>
                <td>${token.is_active ? "Active" : "Inactive"}</td>
            </tr>
        `).join("");
    }

    async function refreshDashboard() {
        try {
            const [stats, events, actions, tokens] = await Promise.all([
                getJson("/api/v1/stats"),
                getJson("/api/v1/events?limit=50"),
                getJson("/api/v1/containment/actions"),
                getJson("/api/v1/tokens?limit=50")
            ]);

            document.getElementById("tokensTotal").textContent =
                stats.tokens_total ?? 0;

            document.getElementById("tokensTriggered").textContent =
                stats.tokens_triggered ?? 0;

            document.getElementById("triggerEvents").textContent =
                stats.trigger_events ?? 0;

            document.getElementById("attackerIps").textContent =
                stats.unique_attacker_ips ?? 0;

            renderTypes(stats.tokens_by_type);
            renderEvents(events);
            renderActions(actions);
            renderTokens(tokens);

            statusElement.textContent =
                `Connected. Last updated: ${new Date().toLocaleTimeString()}`;

            statusElement.className = "status ok";
        } catch (error) {
            statusElement.textContent = error.message;
            statusElement.className = "status error";
        }
    }

    document.getElementById("connectButton").addEventListener("click", () => {
        const key = currentKey();

        if (key) {
            localStorage.setItem("mirage_api_key", key);
        }

        refreshDashboard();
    });

    document.getElementById("refreshButton").addEventListener(
        "click",
        refreshDashboard
    );

    setInterval(() => {
        if (currentKey()) {
            refreshDashboard();
        }
    }, 5000);

    if (savedKey) {
        refreshDashboard();
    }
</script>
</body>
</html>
"""


@router.get(
    "/dashboard",
    response_class=HTMLResponse,
    include_in_schema=False,
)
async def dashboard() -> HTMLResponse:
    return HTMLResponse(content=DASHBOARD_HTML)