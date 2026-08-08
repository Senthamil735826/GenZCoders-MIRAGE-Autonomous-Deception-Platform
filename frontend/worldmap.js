/*
 * worldmap.js — live threat-origin geolocation
 * ------------------------------------------------
 * Plots markers on the world-map panel at the real lat/lon of each
 * detection event's source IP. Data comes from the backend endpoint
 * GET /api/threat-locations (see backend integration guide).
 *
 * Falls back to simulated points if the backend isn't reachable yet,
 * so the panel still looks alive during frontend-only development —
 * remove FALLBACK_MODE once your API is wired up.
 */

const GEO_API_URL = '/api/threat-locations';   // adjust if your backend runs on a different origin, e.g. 'http://localhost:5000/api/threat-locations'
const GEO_POLL_MS = 4000;
const FALLBACK_MODE = true; // set to false once the backend endpoint is live

let geoPollInterval = null;
const activeMarkers = new Map(); // key: unique id -> marker element

// Equirectangular projection: convert lat/lon to % position on the map div
function latLonToPercent(lat, lon){
  const left = ((lon + 180) / 360) * 100;
  const top  = ((90 - lat) / 180) * 100;
  return { left: `${left}%`, top: `${top}%` };
}

function severityClass(sev){
  if (sev === 'critical') return 'sev-critical';
  if (sev === 'warn') return 'sev-warn';
  return 'sev-info';
}

function upsertMarker(loc){
  // loc: { id, lat, lon, ip, city, country, severity, ts }
  const overlay = document.getElementById('world-map-overlay');
  const pos = latLonToPercent(loc.lat, loc.lon);

  let el = activeMarkers.get(loc.id);
  if (!el){
    el = document.createElement('div');
    el.className = `geo-marker ${severityClass(loc.severity)}`;
    el.innerHTML = `<span class="tip"></span>`;
    overlay.appendChild(el);
    activeMarkers.set(loc.id, el);
  }
  el.style.left = pos.left;
  el.style.top = pos.top;
  el.querySelector('.tip').textContent = `${loc.ip || 'unknown ip'} · ${loc.city || ''}${loc.city && loc.country ? ', ' : ''}${loc.country || ''}`.trim();
}

function pruneOldMarkers(freshIds){
  for (const [id, el] of activeMarkers.entries()){
    if (!freshIds.has(id)){
      el.remove();
      activeMarkers.delete(id);
    }
  }
}

async function fetchLiveLocations(){
  try {
    const res = await fetch(GEO_API_URL, { headers: { 'Accept': 'application/json' } });
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    const data = await res.json(); // expected: [{id, lat, lon, ip, city, country, severity, ts}, ...]

    const freshIds = new Set(data.map(d => d.id));
    data.forEach(upsertMarker);
    pruneOldMarkers(freshIds);

    document.getElementById('geo-sub').textContent = `world map · live · ${data.length} active`;
  } catch (err){
    document.getElementById('geo-sub').textContent = 'world map · backend unreachable';
    if (FALLBACK_MODE) simulateOneLocation();
    console.warn('threat-locations fetch failed:', err);
  }
}

// ---- fallback simulator (dev-only, remove once backend is wired) ----
const demoCities = [
  {city:'Moscow', country:'RU', lat:55.75, lon:37.61},
  {city:'Lagos', country:'NG', lat:6.52, lon:3.38},
  {city:'Sao Paulo', country:'BR', lat:-23.55, lon:-46.63},
  {city:'Beijing', country:'CN', lat:39.90, lon:116.40},
  {city:'Bucharest', country:'RO', lat:44.43, lon:26.10},
  {city:'Jakarta', country:'ID', lat:-6.20, lon:106.85},
  {city:'Lahore', country:'PK', lat:31.55, lon:74.34},
  {city:'Kyiv', country:'UA', lat:50.45, lon:30.52},
];
let simCounter = 0;
function simulateOneLocation(){
  const c = demoCities[Math.floor(Math.random()*demoCities.length)];
  const sevRoll = Math.random();
  const severity = sevRoll > 0.8 ? 'critical' : sevRoll > 0.5 ? 'warn' : 'info';
  const id = `sim-${simCounter++ % 12}`; // reuse ids so old markers get replaced/pruned, keeps map from growing forever
  upsertMarker({
    id, lat: c.lat + (Math.random()-0.5)*1.5, lon: c.lon + (Math.random()-0.5)*1.5,
    ip: `${Math.floor(Math.random()*223)+1}.${Math.floor(Math.random()*255)}.${Math.floor(Math.random()*255)}.${Math.floor(Math.random()*255)}`,
    city: c.city, country: c.country, severity
  });
}

function startWorldMap(){
  stopWorldMap();
  document.getElementById('world-map-overlay').innerHTML = '';
  activeMarkers.clear();
  fetchLiveLocations();
  geoPollInterval = setInterval(fetchLiveLocations, GEO_POLL_MS);
}

function stopWorldMap(){
  clearInterval(geoPollInterval);
  geoPollInterval = null;
}