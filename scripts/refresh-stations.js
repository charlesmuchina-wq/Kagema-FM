#!/usr/bin/env node
/**
 * refresh-stations.js — Radio Browser mirror resolver / troubleshooter
 * --------------------------------------------------------------------
 * CLAUDE.md references this as the endpoint-troubleshooting step: "If the Radio
 * Browser API returns broken station URLs, execute `node scripts/refresh-stations.js`
 * to query de1.api.radio-browser.info for working mirrors."
 *
 * It probes each known Radio Browser mirror, reports which ones are reachable
 * and their /json/stats, and prints the fastest healthy mirror to use. It has
 * no dependencies and needs no .env.
 *
 * Usage:  node scripts/refresh-stations.js        (or: npm run refresh-stations)
 *
 * Proxy note: start with NODE_USE_ENV_PROXY=1 so Node's fetch honours HTTPS_PROXY
 * (the npm script does this for you).
 *
 * Exit codes:  0 = at least one mirror healthy   2 = no mirror reachable
 */
'use strict';

const MIRRORS = [
  'https://de1.api.radio-browser.info',
  'https://nl1.api.radio-browser.info',
  'https://at1.api.radio-browser.info',
  'https://fi1.api.radio-browser.info',
];

const USER_AGENT = 'KagemaFM-MirrorResolver/1.0 (+https://github.com/charlesmuchina-wq/kagema-fm)';
const TIMEOUT_MS = parseInt(process.env.TIMEOUT_MS || '10000', 10);

function host(u) { try { return new URL(u).host; } catch { return u; } }

async function probe(base) {
  const controller = new AbortController();
  const timer = setTimeout(() => controller.abort(), TIMEOUT_MS);
  const start = Date.now();
  try {
    const res = await fetch(base + '/json/stats', {
      headers: { 'User-Agent': USER_AGENT, Accept: 'application/json' },
      signal: controller.signal,
    });
    const ms = Date.now() - start;
    if (!res.ok) return { base, ok: false, ms, error: `HTTP ${res.status}` };
    const stats = await res.json();
    return { base, ok: true, ms, stations: stats.stations, status: stats.status };
  } catch (err) {
    const cause = err && err.cause ? String(err.cause.message || err.cause) : '';
    const detail = [String((err && err.message) || err), cause].filter(Boolean).join(' — ');
    return { base, ok: false, ms: Date.now() - start, error: err.name === 'AbortError' ? 'timeout' : detail };
  } finally {
    clearTimeout(timer);
  }
}

async function main() {
  if (process.env.HTTPS_PROXY && process.env.NODE_USE_ENV_PROXY !== '1') {
    console.log('⚠ HTTPS_PROXY is set but NODE_USE_ENV_PROXY!=1 — run via `npm run refresh-stations`.\n');
  }
  console.log('Probing Radio Browser mirrors...\n');
  const results = await Promise.all(MIRRORS.map(probe));

  for (const r of results) {
    if (r.ok) {
      console.log(`  ✓ ${host(r.base).padEnd(34)} ${String(r.ms + 'ms').padEnd(8)} stations=${r.stations ?? '?'} status=${r.status ?? '?'}`);
    } else {
      console.log(`  ✗ ${host(r.base).padEnd(34)} ${String(r.ms + 'ms').padEnd(8)} ${r.error}`);
    }
  }

  const healthy = results.filter((r) => r.ok).sort((a, b) => a.ms - b.ms);
  console.log('');
  if (healthy.length) {
    console.log(`Recommended mirror (fastest healthy): ${host(healthy[0].base)}  (${healthy[0].ms}ms)`);
    process.exit(0);
  }
  console.log('✗ No Radio Browser mirror was reachable from this environment.');
  console.log('  If mirrors are blocked by an egress policy, this is a network condition, not a code fault.');
  process.exit(2);
}

main().catch((err) => { console.error('Unexpected error:', err); process.exit(2); });
