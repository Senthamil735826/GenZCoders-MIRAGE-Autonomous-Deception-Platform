<<<<<<< HEAD
let currentRole = 'host';

function selectRole(role){
  currentRole = role;
  document.getElementById('tab-host').classList.toggle('active', role==='host');
  document.getElementById('tab-analyst').classList.toggle('active', role==='analyst');
}

function enterDashboard(){
  document.getElementById('login-screen').classList.add('hidden');
  document.getElementById('dashboard').classList.remove('hidden');
  document.getElementById('role-badge').textContent = currentRole === 'host' ? 'Host' : 'Analyst · view only';
  document.getElementById('modules-sub').textContent = currentRole === 'host' ? 'host controls' : 'monitoring only';
  renderModules();
  startLiveFeed();
  startWorldMap(); // defined in worldmap.js
}

function logout(){
  document.getElementById('dashboard').classList.add('hidden');
  document.getElementById('login-screen').classList.remove('hidden');
  document.getElementById('login-user').value = '';
  document.getElementById('login-pass').value = '';
  stopWorldMap(); // defined in worldmap.js
}

// clock
function tickClock(){
  document.getElementById('clock').textContent = new Date().toLocaleTimeString('en-GB');
}
setInterval(tickClock, 1000); tickClock();

// ---- module definitions ----
const modules = [
  {id:'honeytoken', name:'Honeytoken generation', action:'Generate honeytoken', color:'cyan', icon:'target', count:142, status:'active'},
  {id:'canary', name:'Canary deployment', action:'Deploy canary', color:'amber', icon:'flag', count:28, status:'active'},
  {id:'credential', name:'Credential deception', action:'Plant fake credentials', color:'purple', icon:'key', count:63, status:'active'},
  {id:'document', name:'Fake document creation', action:'Create decoy document', color:'green', icon:'doc', count:19, status:'idle'},
  {id:'cloud', name:'Cloud deception', action:'Deploy cloud decoy', color:'cyan', icon:'cloud', count:8, status:'active'},
  {id:'sourcecode', name:'Source-code deception', action:'Inject code trap', color:'red', icon:'code', count:11, status:'idle'},
];

const icons = {
  target: '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><circle cx="12" cy="12" r="8"/><circle cx="12" cy="12" r="4"/><circle cx="12" cy="12" r="0.6" fill="currentColor"/></svg>',
  flag: '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><path d="M5 21V4"/><path d="M5 4h13l-3 4 3 4H5"/></svg>',
  key: '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><circle cx="8" cy="15" r="4"/><path d="M11 12l8-8"/><path d="M16 5l3 3"/><path d="M13 8l2.5 2.5"/></svg>',
  doc: '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><path d="M7 3h7l4 4v14H7z"/><path d="M14 3v4h4"/><path d="M9 13h7M9 17h7"/></svg>',
  cloud: '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><path d="M7 18a4 4 0 0 1-.5-7.97A5.5 5.5 0 0 1 17 9.5 4 4 0 0 1 17 18H7z"/></svg>',
  code: '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><path d="M9 8l-4 4 4 4"/><path d="M15 8l4 4-4 4"/></svg>',
};

function renderModules(){
  const grid = document.getElementById('modules-grid');
  grid.innerHTML = modules.map(m => `
    <div class="module-card" id="mod-${m.id}">
      <div class="module-head">
        <div class="module-icon" style="background:var(--${m.color}-dim); color:var(--${m.color}-text);">${icons[m.icon]}</div>
        <span class="status-pill ${m.status==='active'?'status-active':'status-idle'}" id="status-${m.id}"><span class="d"></span>${m.status==='active'?'Active':'Idle'}</span>
      </div>
      <div class="module-name">${m.name}</div>
      <div class="module-count" id="count-${m.id}">${m.count}</div>
      <div class="module-meta">deployed</div>
      ${currentRole==='host'
        ? `<button class="module-btn" onclick="triggerModule('${m.id}')">${m.action}</button>`
        : `<div class="view-only-tag">View only</div>`}
    </div>
  `).join('');
}

function triggerModule(id){
  const m = modules.find(x => x.id === id);
  m.count += 1;
  m.status = 'active';
  document.getElementById(`count-${id}`).textContent = m.count;
  const pill = document.getElementById(`status-${id}`);
  pill.className = 'status-pill status-active';
  pill.innerHTML = '<span class="d"></span>Active';
  pushFeedItem(`<b>${m.name}</b> triggered manually — new decoy deployed`, 'info');
}

// ---- threat chart ----
const chartData = Array.from({length:20}, () => Math.floor(Math.random()*30)+15);
const chartLabels = Array.from({length:20}, (_,i) => `${20-i}m`);
const ctx = document.getElementById('threatChart');
const threatChart = new Chart(ctx, {
  type:'line',
  data:{ labels: chartLabels, datasets:[{ data: chartData, borderColor:'#2dd4c4', backgroundColor:'rgba(45,212,196,0.08)', fill:true, tension:.35, pointRadius:0, borderWidth:2 }]},
  options:{ responsive:true, maintainAspectRatio:false,
    plugins:{ legend:{display:false} },
    scales:{
      x:{ ticks:{ color:'#576070', font:{size:10} }, grid:{ display:false } },
      y:{ ticks:{ color:'#576070', font:{size:10} }, grid:{ color:'#1a212a' }, min:0, max:100 }
    }
  }
});

function pushChartPoint(){
  const last = chartData[chartData.length-1];
  let next = last + (Math.random()*20-10);
  next = Math.max(5, Math.min(95, Math.round(next)));
  chartData.push(next); chartData.shift();
  threatChart.data.datasets[0].data = chartData;
  threatChart.update('none');
}

// ---- telemetry feed ----
const feedTemplates = [
  {text:'Honeytoken <b>HT-3391</b> accessed from unrecognised host', sev:'critical'},
  {text:'Canary <b>CN-002</b> triggered — possible lateral movement', sev:'critical'},
  {text:'Credential decoy used in failed login attempt', sev:'warn'},
  {text:'Decoy document <b>finance_Q3_report.xlsx</b> opened', sev:'warn'},
  {text:'Cloud bucket <b>decoy-storage-07</b> listed by unfamiliar IAM role', sev:'warn'},
  {text:'Source trap <b>getAdminToken()</b> invoked in staging repo', sev:'critical'},
  {text:'New honeytoken beacon registered', sev:'info'},
  {text:'Telemetry sync completed — 0 anomalies', sev:'info'},
  {text:'Canary heartbeat received from edge node 4', sev:'info'},
];

const containmentTemplates = [
  'Auto-blocked source IP',
  'Isolated workstation from network',
  'Revoked session token',
  'Quarantined outbound transfer',
  'Disabled compromised IAM role',
  'Rotated exposed credential',
];

function nowTime(){ return new Date().toLocaleTimeString('en-GB'); }

function pushFeedItem(text, sev){
  const list = document.getElementById('feed-list');
  const el = document.createElement('div');
  el.className = `feed-item sev-${sev}`;
  el.innerHTML = `<span class="feed-time">${nowTime()}</span><span class="feed-text">${text}</span>`;
  list.prepend(el);
  while (list.children.length > 30) list.removeChild(list.lastChild);
}

function pushContainmentItem(){
  const list = document.getElementById('containment-list');
  const action = containmentTemplates[Math.floor(Math.random()*containmentTemplates.length)];
  const el = document.createElement('div');
  el.className = 'containment-item';
  el.innerHTML = `<span class="tick">✓</span><span>${action}</span><span class="containment-time">${nowTime()}</span>`;
  list.prepend(el);
  while (list.children.length > 12) list.removeChild(list.lastChild);
  const kc = document.getElementById('kpi-contained');
  kc.textContent = parseInt(kc.textContent) + 1;
}

let feedInterval, chartInterval;
function startLiveFeed(){
  clearInterval(feedInterval); clearInterval(chartInterval);
  document.getElementById('feed-list').innerHTML = '';
  document.getElementById('containment-list').innerHTML = '';
  for (let i=0;i<5;i++){
    const t = feedTemplates[Math.floor(Math.random()*feedTemplates.length)];
    pushFeedItem(t.text, t.sev);
  }
  pushContainmentItem(); pushContainmentItem();

  feedInterval = setInterval(() => {
    const t = feedTemplates[Math.floor(Math.random()*feedTemplates.length)];
    pushFeedItem(t.text, t.sev);
    if (t.sev !== 'info'){
      const kt = document.getElementById('kpi-threats');
      kt.textContent = parseInt(kt.textContent) + 1;
      if (Math.random() > 0.35) setTimeout(pushContainmentItem, 900 + Math.random()*1200);
    }
    if (Math.random() > 0.6){
      const kk = document.getElementById('kpi-tokens');
      kk.textContent = parseInt(kk.textContent) + (Math.random() > 0.5 ? 1 : 0);
    }
  }, 3200);

  chartInterval = setInterval(pushChartPoint, 2200);
}
=======
* { margin: 0; padding: 0; box-sizing: border-box; }

body {
    font-family: 'Courier New', monospace;
    background: #0a0e1a;
    color: #00ff88;
    min-height: 100vh;
    padding: 20px;
}

.container {
    max-width: 1400px;
    margin: 0 auto;
}

header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 20px;
    background: linear-gradient(135deg, #1a1f3a, #0f1424);
    border: 1px solid #00ff88;
    border-radius: 8px;
    margin-bottom: 20px;
}

header h1 {
    font-size: 1.5em;
    color: #00ff88;
    text-shadow: 0 0 10px #00ff88;
}

.status-indicator {
    display: flex;
    align-items: center;
    gap: 10px;
    color: #00ff88;
}

.dot {
    width: 12px;
    height: 12px;
    background: #00ff88;
    border-radius: 50%;
    box-shadow: 0 0 10px #00ff88;
    animation: pulse 2s infinite;
}

@keyframes pulse {
    0%, 100% { opacity: 1; }
    50% { opacity: 0.5; }
}

.stats-grid {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 15px;
    margin-bottom: 20px;
}

.stat-card {
    background: #1a1f3a;
    border: 1px solid #2a3f5a;
    border-radius: 8px;
    padding: 20px;
    text-align: center;
}

.stat-card.critical { border-color: #ff3366; }
.stat-card.high { border-color: #ff9933; }
.stat-card.contained { border-color: #00ff88; }

.stat-card h3 {
    color: #8a9ab0;
    font-size: 0.85em;
    margin-bottom: 10px;
}

.stat-card p {
    color: #00ff88;
    font-size: 2em;
    font-weight: bold;
}

.actions-panel {
    background: #1a1f3a;
    border: 1px solid #2a3f5a;
    border-radius: 8px;
    padding: 20px;
    margin-bottom: 20px;
}

.actions-panel h2 {
    color: #00ff88;
    margin-bottom: 15px;
}

.action-buttons {
    display: flex;
    flex-wrap: wrap;
    gap: 10px;
}

button {
    background: #2a3f5a;
    color: #00ff88;
    border: 1px solid #00ff88;
    padding: 10px 20px;
    border-radius: 4px;
    cursor: pointer;
    font-family: inherit;
    transition: all 0.3s;
}

button:hover {
    background: #00ff88;
    color: #0a0e1a;
    box-shadow: 0 0 10px #00ff88;
}

button.danger {
    border-color: #ff3366;
    color: #ff3366;
}

button.danger:hover {
    background: #ff3366;
    color: #0a0e1a;
    box-shadow: 0 0 10px #ff3366;
}

.panels-grid {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 15px;
    margin-bottom: 20px;
}

.panel {
    background: #1a1f3a;
    border: 1px solid #2a3f5a;
    border-radius: 8px;
    padding: 20px;
}

.panel h2 {
    color: #00ff88;
    margin-bottom: 15px;
}

.list {
    max-height: 400px;
    overflow-y: auto;
}

.list-item {
    background: #0f1424;
    border-left: 3px solid #00ff88;
    padding: 10px;
    margin-bottom: 8px;
    border-radius: 4px;
    font-size: 0.9em;
}

.list-item.critical { border-left-color: #ff3366; }
.list-item.high { border-left-color: #ff9933; }
.list-item.medium { border-left-color: #ffcc00; }

.list-item .timestamp {
    color: #8a9ab0;
    font-size: 0.8em;
}

.list-item .risk {
    color: #ff3366;
    font-weight: bold;
}
>>>>>>> 64298fec6fb91e777e509072a0ac21eac30fa1f4
