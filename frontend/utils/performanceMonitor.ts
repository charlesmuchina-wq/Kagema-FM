/**
 * Lightweight performance monitor.
 *
 * Records named timing measurements (screen loads, API calls, expensive
 * computations) into a small in-memory ring buffer, warns on slow operations,
 * and exposes simple aggregates. No dependencies; safe on web and native.
 */

export interface PerfMetric {
  name: string;
  duration: number; // milliseconds
  timestamp: number;
}

const MAX_METRICS = 100;
const SLOW_THRESHOLD_MS = 1000;

const timers = new Map<string, number>();
const metrics: PerfMetric[] = [];

function now(): number {
  const perf = (globalThis as unknown as { performance?: { now?: () => number } }).performance;
  return perf?.now ? perf.now() : Date.now();
}

/** Start a named timer. */
export function startTimer(name: string): void {
  timers.set(name, now());
}

/**
 * End a named timer, record the measurement, and return its duration (ms).
 * Returns undefined if the timer was never started.
 */
export function endTimer(name: string): number | undefined {
  const start = timers.get(name);
  if (start === undefined) return undefined;
  timers.delete(name);
  return recordMetric(name, now() - start);
}

/** Record a measurement directly. Returns the duration for convenience. */
export function recordMetric(name: string, duration: number): number {
  metrics.push({ name, duration, timestamp: Date.now() });
  if (metrics.length > MAX_METRICS) metrics.shift();
  if (duration > SLOW_THRESHOLD_MS) {
    // eslint-disable-next-line no-console
    console.warn(`[perf] slow: "${name}" took ${Math.round(duration)}ms`);
  }
  return duration;
}

/** Time an async function under `name` and return its result. */
export async function measure<T>(name: string, fn: () => Promise<T>): Promise<T> {
  startTimer(name);
  try {
    return await fn();
  } finally {
    endTimer(name);
  }
}

/** All recorded metrics (newest last). */
export function getMetrics(): readonly PerfMetric[] {
  return metrics;
}

/** Average duration (ms) for a given metric name, or 0 if none recorded. */
export function getAverage(name: string): number {
  const matching = metrics.filter((m) => m.name === name);
  if (matching.length === 0) return 0;
  return matching.reduce((sum, m) => sum + m.duration, 0) / matching.length;
}

/** Clear all recorded metrics and pending timers. */
export function clearMetrics(): void {
  metrics.length = 0;
  timers.clear();
}
