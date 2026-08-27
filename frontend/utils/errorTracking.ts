/**
 * Centralized error tracking.
 *
 * Dependency-free by design: it captures exceptions/messages, keeps a small
 * in-memory ring buffer, installs global handlers for otherwise-unhandled
 * errors, and fans out to registered reporters. A production error backend
 * (e.g. Sentry) can be wired in by calling `addReporter()` from
 * `initErrorTracking()` — see the note below — without touching call sites.
 */

export interface TrackedError {
  message: string;
  stack?: string;
  context?: Record<string, unknown>;
  fatal: boolean;
  timestamp: number;
}

type Reporter = (error: TrackedError) => void;

const MAX_BUFFERED = 50;
const recent: TrackedError[] = [];
const reporters: Reporter[] = [];
let installed = false;

function consoleReporter(error: TrackedError): void {
  const tag = error.fatal ? '💥 fatal' : '⚠️ error';
  // eslint-disable-next-line no-console
  console.error(`[errorTracking] ${tag}: ${error.message}`, error.context ?? '');
}

/** Register an additional reporter (e.g. a Sentry forwarder). */
export function addReporter(reporter: Reporter): void {
  reporters.push(reporter);
}

/** Capture an exception (or any thrown value) with optional context. */
export function captureException(
  error: unknown,
  context?: Record<string, unknown>,
  fatal = false,
): void {
  const err = error instanceof Error ? error : new Error(String(error));
  const tracked: TrackedError = {
    message: err.message,
    stack: err.stack,
    context,
    fatal,
    timestamp: Date.now(),
  };

  recent.push(tracked);
  if (recent.length > MAX_BUFFERED) recent.shift();

  for (const report of reporters) {
    try {
      report(tracked);
    } catch {
      // A failing reporter must never mask the original error.
    }
  }
}

/** Capture a non-exception message (e.g. a soft failure worth recording). */
export function captureMessage(
  message: string,
  context?: Record<string, unknown>,
): void {
  captureException(new Error(message), context, false);
}

/** The most recent captured errors (newest last). */
export function getRecentErrors(): readonly TrackedError[] {
  return recent;
}

/**
 * Install global handlers so unhandled JS errors and promise rejections are
 * captured. Idempotent. Call once at app startup.
 *
 * To forward to Sentry (or any backend), add the SDK and register a reporter:
 *   import * as Sentry from '@sentry/react-native';
 *   Sentry.init({ dsn: process.env.EXPO_PUBLIC_SENTRY_DSN });
 *   addReporter((e) => e.fatal
 *     ? Sentry.captureException(new Error(e.message))
 *     : Sentry.captureMessage(e.message));
 */
export function initErrorTracking(): void {
  if (installed) return;
  installed = true;

  if (reporters.length === 0) {
    reporters.push(consoleReporter);
  }

  // React Native: catch otherwise-unhandled JS errors.
  const globalAny = global as unknown as {
    ErrorUtils?: {
      getGlobalHandler?: () => (error: unknown, isFatal?: boolean) => void;
      setGlobalHandler?: (h: (error: unknown, isFatal?: boolean) => void) => void;
    };
  };
  const errorUtils = globalAny.ErrorUtils;
  if (errorUtils?.setGlobalHandler) {
    const previous = errorUtils.getGlobalHandler?.();
    errorUtils.setGlobalHandler((error: unknown, isFatal?: boolean) => {
      captureException(error, { source: 'global' }, !!isFatal);
      previous?.(error, isFatal);
    });
  }

  // Web: catch window-level errors and unhandled rejections.
  const win = (globalThis as unknown as { addEventListener?: Function }).addEventListener
    ? (globalThis as unknown as {
        addEventListener: (t: string, l: (e: unknown) => void) => void;
      })
    : undefined;
  if (win) {
    win.addEventListener('error', (event: unknown) => {
      const e = event as { error?: unknown; message?: string };
      captureException(e.error ?? e.message ?? 'window error', { source: 'window' }, false);
    });
    win.addEventListener('unhandledrejection', (event: unknown) => {
      const e = event as { reason?: unknown };
      captureException(e.reason ?? 'unhandled rejection', { source: 'promise' }, false);
    });
  }
}
