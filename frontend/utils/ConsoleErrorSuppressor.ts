/**
 * Console Error Suppression Utility
 * Prevents known non-critical warnings from cluttering the console
 */

export class ConsoleErrorSuppressor {
  private static instance: ConsoleErrorSuppressor;
  private originalConsoleError: typeof console.error;
  private originalConsoleWarn: typeof console.warn;
  private originalConsoleLog: typeof console.log;
  private suppressedPatterns: RegExp[] = [];
  private isActive: boolean = false;

  private constructor() {
    this.originalConsoleError = console.error.bind(console);
    this.originalConsoleWarn = console.warn.bind(console);
    this.originalConsoleLog = console.log.bind(console);
    
    // Define known non-critical warning patterns
    this.suppressedPatterns = [
      /expo-notifications.*not yet fully supported on web/i,
      /tunnel.*already connected/i,
      /listening to push token changes.*no effect/i,
      /componentWillMount.*deprecated/i,
      /componentWillReceiveProps.*deprecated/i,
      /non-serializable values were found/i,
      /failed to fetch.*localhost/i,
      /cors.*origin/i,
      /unauthorized request from.*emergent\.sh/i,
      /this may happen because of.*browser extension/i,
      /disable browser extensions.*incognito/i,
      /unexpected end of json input/i,
      /syntax.*error.*json/i,
      /skipping dependency validation.*offline mode/i,
      /iheart.*cors.*blocked/i,
      /streema.*api.*rate.*limit/i,
      /radio.*garden.*403.*forbidden/i,
      /stream.*validation.*failed/i,
      /network.*error.*external.*source/i,
      /fetch.*error.*external.*api/i,
      /aborterror.*signal.*aborted/i,
      /timeout.*external.*service/i,
      /stream.*url.*accessibility.*failed/i,
      /api.*request.*failed.*cors/i
    ];
  }

  public static getInstance(): ConsoleErrorSuppressor {
    if (!ConsoleErrorSuppressor.instance) {
      ConsoleErrorSuppressor.instance = new ConsoleErrorSuppressor();
    }
    return ConsoleErrorSuppressor.instance;
  }

  public activate(): void {
    if (this.isActive) return;

    console.error = this.createFilteredLogger('error', this.originalConsoleError);
    console.warn = this.createFilteredLogger('warn', this.originalConsoleWarn);
    console.log = this.createFilteredLogger('log', this.originalConsoleLog);
    
    this.isActive = true;
    console.log('🔇 Console error suppressor activated');
  }

  public deactivate(): void {
    if (!this.isActive) return;

    console.error = this.originalConsoleError;
    console.warn = this.originalConsoleWarn;
    console.log = this.originalConsoleLog;
    
    this.isActive = false;
    console.log('🔊 Console error suppressor deactivated');
  }

  public addPattern(pattern: RegExp): void {
    this.suppressedPatterns.push(pattern);
  }

  public removePattern(pattern: RegExp): void {
    const index = this.suppressedPatterns.indexOf(pattern);
    if (index > -1) {
      this.suppressedPatterns.splice(index, 1);
    }
  }

  private createFilteredLogger(level: string, originalLogger: Function) {
    return (...args: any[]) => {
      const message = args.join(' ');
      
      // Check if message matches any suppressed patterns
      const shouldSuppress = this.suppressedPatterns.some(pattern => 
        pattern.test(message)
      );
      
      if (!shouldSuppress) {
        originalLogger(...args);
      } else {
        // Optionally log suppressed messages to a separate debug channel
        if (process.env.NODE_ENV === 'development' && globalThis.__DEV__) {
          console.debug(`[SUPPRESSED ${level.toUpperCase()}]:`, ...args);
        }
      }
    };
  }

  public getSuppressedPatterns(): RegExp[] {
    return [...this.suppressedPatterns];
  }

  public isPatternSuppressed(message: string): boolean {
    return this.suppressedPatterns.some(pattern => pattern.test(message));
  }
}

// Global instance for easy access
export const consoleErrorSuppressor = ConsoleErrorSuppressor.getInstance();

// Auto-activate in development mode to prevent console spam
if (typeof window !== 'undefined' && process.env.NODE_ENV === 'development') {
  consoleErrorSuppressor.activate();
}