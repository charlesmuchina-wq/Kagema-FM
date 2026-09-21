#!/usr/bin/env node
/**
 * test-streams.js — Radio Browser stream-health monitor
 * -----------------------------------------------------
 * Queries the Radio Browser API for a sample of stations and validates that
 * their stream URLs are actually reachable and serving audio. Mirrors the
 * validation logic in backend/stream_validation_service.py, but is fully
 * self-contained (no MongoDB, no .env, no third-party npm dependencies) so it
 * can run as a quick monitoring / CI check.
 *
 * Usage:
 *   node scripts/test-streams.js
 *   SAMPLE_SIZE=20 COUNTRY=KE MIN_PASS_RATE=0.7 node scripts/test-streams.js
 *
 * Config (environment variables, all optional):
 *   SAMPLE_SIZE    number of stations to sample          (default 15)
 *   COUNTRY        ISO 3166-1 alpha-2 filter, e.g. KE     (default: none)
 *   MIN_PASS_RATE  fraction of streams that must pass     (default 0.6)
 *   TIMEOUT_MS     per-request timeout in ms              (default 12000)
 *   RETRIES        retry attempts per stream              (default 2)
 *
 * Proxy note: Node's built-in fetch only honours HTTPS_PROXY when started with
 * NODE_USE_ENV_PROXY=1 (Node >= 22.21). The npm "test:streams" script sets it.
 *
 * Exit codes:
 *   0  API reachable and pass-rate >= MIN_PASS_RATE
 *   1  API reachable but too many streams failed
 *   2  Radio Browser API unreachable (network/egress policy) — no data tested
 */
'use strict';

const CONFIG = {
  sampleSize: intEnv('SAMPLE_SIZE', 15),
  country: (process.env.COUNTRY || '').trim().toUpperCase(),
  minPassRate: floatEnv('MIN_PASS_RATE', 0.6),
  timeoutMs: intEnv('TIMEOUT_MS', 12000),
  retries: intEnv('RETRIES', 2),
};

// Radio Browser mirrors, tried in order until one answers.
const MIRRORS = [
  'https://de1.api.radio-browser.info',
  'https://nl1.api.radio-browser.info',
  'https://at1.api.radio-browser.info',
  'https://fi1.api.radio-browser.info',
];

const USER_AGENT = 'KagemaFM-StreamHealth/1.0 (+https://github.com/charlesmuchina-wq/kagema-fm)';

const VALID_AUDIO_HINTS = [
  'audio/', 'application/ogg', 'application/x-mpegurl',
  'application/vnd.apple.mpegurl', 'video/mp2t', 'application/octet-stream',
];

function intEnv(name, fallback) {
  const v = parseInt(process.env[name] || '', 10);
  return Number.isFinite(v) && v > 0 ? v : fallback;
}
function floatEnv(name, fallback) {
  const v = parseFloat(process.env[name] || '');
  return Number.isFinite(v) && v >= 0 && v <= 1 ? v : fallback;
}

/** Fetch with an AbortController-based timeout. */
async function fetchWithTimeout(url, opts = {}, timeoutMs = CONFIG.timeoutMs) {
  const controller = new AbortController();
  const timer = setTimeout(() => controller.abort(), timeoutMs);
  try {
    return await fetch(url, { ...opts, signal: controller.signal });
  } finally {
    clearTimeout(timer);
  }
}

/** Classify a thrown fetch error into a short, human-readable reason. */
function describeError(err) {
  // fetch() wraps the real reason in err.cause; surface it for clearer messages.
  const cause = err && err.cause ? String(err.cause.message || err.cause) : '';
  const msg = [String((err && err.message) || err), cause].filter(Boolean).join(' — ');
  if (err && err.name === 'AbortError') return 'timeout';
  if (/CONNECT|407|403|tunnel|proxy|denied/i.test(msg)) return 'blocked by egress proxy/policy';
  if (/ENOTFOUND|EAI_AGAIN|getaddrinfo/i.test(msg)) return 'DNS resolution failed';
  if (/ECONNREFUSED|ECONNRESET|socket hang up|network/i.test(msg)) return 'connection failed';
  return msg.slice(0, 160);
}

/** Pull the station sample from the first responsive mirror. */
async function fetchStationSample() {
  const params = new URLSearchParams({
    limit: String(CONFIG.sampleSize),
    hidebroken: 'true',
    order: 'clickcount',
    reverse: 'true',
  });
  if (CONFIG.country) params.set('countrycode', CONFIG.country);
  const path = `/json/stations/search?${params.toString()}`;

  const failures = [];
  for (const base of MIRRORS) {
    try {
      const res = await fetchWithTimeout(base + path, {
        headers: { 'User-Agent': USER_AGENT, Accept: 'application/json' },
      });
      if (!res.ok) {
        failures.push(`${host(base)} → HTTP ${res.status}`);
        continue;
      }
      const stations = await res.json();
      if (Array.isArray(stations) && stations.length) {
        return { mirror: base, stations };
      }
      failures.push(`${host(base)} → empty result set`);
    } catch (err) {
      failures.push(`${host(base)} → ${describeError(err)}`);
    }
  }
  const reason = new Error(`No Radio Browser mirror was reachable:\n  - ${failures.join('\n  - ')}`);
  reason.unreachable = true;
  throw reason;
}

function host(u) {
  try { return new URL(u).host; } catch { return u; }
}

/** Validate a single stream URL. Mirrors the backend service's heuristics. */
async function validateStream(streamUrl) {
  const result = { url: streamUrl, ok: false, status: 'unknown', httpStatus: null, contentType: null, ms: null, error: null };
  if (!streamUrl) {
    result.status = 'error';
    result.error = 'no stream url';
    return result;
  }

  for (let attempt = 0; attempt <= CONFIG.retries; attempt++) {
    const start = Date.now();
    let res;
    try {
      res = await fetchWithTimeout(streamUrl, {
        method: 'GET',
        redirect: 'follow',
        headers: { 'User-Agent': USER_AGENT, Icy: 'MetaData: 0' },
      });
    } catch (err) {
      result.status = describeError(err) === 'timeout' ? 'timeout' : 'error';
      result.error = describeError(err);
      if (attempt < CONFIG.retries) { await sleep(800); continue; }
      return result;
    }

    result.httpStatus = res.status;
    result.contentType = res.headers.get('content-type') || '';
    result.ms = Date.now() - start;

    // Read a single small chunk to confirm the stream is actually flowing.
    let hasData = false;
    try {
      if (res.body) {
        const reader = res.body.getReader();
        const { value } = await reader.read();
        hasData = !!value && value.length > 0;
        await reader.cancel();
      }
    } catch { hasData = false; }

    const ct = result.contentType.toLowerCase();
    const looksAudio = VALID_AUDIO_HINTS.some((h) => ct.includes(h));
    const looksPlaylist = /\.(m3u8?|pls)(\?|$)/i.test(streamUrl) || ct.includes('mpegurl') || ct.includes('scpls');

    if (res.status >= 200 && res.status < 400 && (looksAudio || looksPlaylist || hasData)) {
      result.ok = true;
      result.status = 'online';
      return result;
    }

    result.status = 'error';
    result.error = `HTTP ${res.status}${result.contentType ? ` (${result.contentType})` : ''}`;
    if (attempt < CONFIG.retries) await sleep(800);
  }
  return result;
}

function sleep(ms) { return new Promise((r) => setTimeout(r, ms)); }

function pad(s, n) { s = String(s); return s.length >= n ? s.slice(0, n) : s + ' '.repeat(n - s.length); }

async function main() {
  console.log('Radio Browser stream-health check');
  console.log(`  sample=${CONFIG.sampleSize}  country=${CONFIG.country || 'any'}  minPassRate=${CONFIG.minPassRate}  timeout=${CONFIG.timeoutMs}ms  retries=${CONFIG.retries}`);
  if (process.env.HTTPS_PROXY && process.env.NODE_USE_ENV_PROXY !== '1') {
    console.log('  ⚠ HTTPS_PROXY is set but NODE_USE_ENV_PROXY!=1 — run via `npm run test:streams` so fetch uses the proxy.');
  }
  console.log('');

  let sample;
  try {
    sample = await fetchStationSample();
  } catch (err) {
    console.error('✗ Could not reach the Radio Browser API — no streams were tested.');
    console.error(String(err.message));
    console.error('\nThis is an environment/network condition, not a stream failure.');
    process.exit(2);
  }

  console.log(`Using mirror: ${host(sample.mirror)} — testing ${sample.stations.length} stations\n`);

  const results = [];
  for (const st of sample.stations) {
    const url = st.url_resolved || st.url;
    const r = await validateStream(url);
    results.push({ name: st.name || '(unnamed)', ...r });
    const mark = r.ok ? '✓' : '✗';
    console.log(`  ${mark} ${pad((st.name || '(unnamed)').trim(), 34)} ${pad(r.status, 9)} ${r.ms != null ? r.ms + 'ms' : ''} ${r.ok ? '' : '— ' + (r.error || '')}`);
  }

  const passed = results.filter((r) => r.ok).length;
  const total = results.length;
  const rate = total ? passed / total : 0;

  console.log(`\nResult: ${passed}/${total} streams online (${(rate * 100).toFixed(0)}%), threshold ${(CONFIG.minPassRate * 100).toFixed(0)}%`);

  if (rate >= CONFIG.minPassRate) {
    console.log('✓ PASS');
    process.exit(0);
  }
  console.log('✗ FAIL — too many streams are unreachable.');
  process.exit(1);
}

main().catch((err) => {
  console.error('Unexpected error:', err);
  process.exit(2);
});
