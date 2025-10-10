/**
 * Browser Extension Conflict Detector and Prevention System
 * Detects and handles browser extension conflicts that cause unauthorized request errors
 */

interface ExtensionConflictInfo {
  detected: boolean;
  conflictingExtensions: string[];
  recommendations: string[];
  severity: 'low' | 'medium' | 'high';
}

interface NetworkRequestOptions {
  url: string;
  options?: RequestInit;
  retries?: number;
  timeout?: number;
}

class BrowserExtensionDetector {
  private static instance: BrowserExtensionDetector;
  private conflictDetected: boolean = false;
  private originalFetch: typeof fetch;
  private requestAttempts: Map<string, number> = new Map();

  static getInstance(): BrowserExtensionDetector {
    if (!BrowserExtensionDetector.instance) {
      BrowserExtensionDetector.instance = new BrowserExtensionDetector();
    }
    return BrowserExtensionDetector.instance;
  }

  constructor() {
    this.originalFetch = window.fetch;
    this.interceptFetch();
  }

  /**
   * Detect common browser extensions that may cause conflicts
   */
  async detectConflictingExtensions(): Promise<ExtensionConflictInfo> {
    const detectedExtensions: string[] = [];
    const recommendations: string[] = [];

    // Check for common ad blockers and privacy extensions
    const extensionTests = [
      // AdBlock/uBlock indicators
      {
        test: () => {
          const adBlockSelectors = [
            '#AdBlock', '#adblock', '.adblock',
            '#uBlock', '#ublock', '.ublock',
            '[id*="adblock"]', '[class*="adblock"]'
          ];
          return adBlockSelectors.some(selector => document.querySelector(selector));
        },
        name: 'AdBlock/uBlock Origin',
        recommendation: 'Whitelist the current domain in your ad blocker settings'
      },
      
      // Privacy Badger indicators
      {
        test: () => {
          return !!(window as any).privacyBadgerLocale || 
                 document.querySelector('[id*="privacy-badger"]') ||
                 document.querySelector('[class*="privacy-badger"]');
        },
        name: 'Privacy Badger',
        recommendation: 'Disable Privacy Badger for this domain'
      },

      // Ghostery indicators
      {
        test: () => {
          return !!(window as any).ghostery || 
                 !!(window as any).GhosteryTracker ||
                 document.querySelector('[id*="ghostery"]');
        },
        name: 'Ghostery',
        recommendation: 'Add this site to Ghostery\'s whitelist'
      },

      // VPN/Proxy extensions
      {
        test: () => {
          const vpnIndicators = [
            '[id*="vpn"]', '[class*="vpn"]',
            '[id*="proxy"]', '[class*="proxy"]',
            '[id*="tunnel"]', '[class*="tunnel"]'
          ];
          return vpnIndicators.some(selector => document.querySelector(selector));
        },
        name: 'VPN/Proxy Extension',
        recommendation: 'Temporarily disable VPN extensions for local development'
      },

      // Request interceptors
      {
        test: () => {
          const originalXHR = (window as any).XMLHttpRequest.toString();
          const originalFetch = window.fetch.toString();
          
          return originalXHR.includes('native code') === false || 
                 originalFetch.includes('native code') === false;
        },
        name: 'Request Interceptor Extension',
        recommendation: 'Disable extensions that modify network requests'
      },

      // CORS-related extensions
      {
        test: () => {
          return document.querySelector('[id*="cors"]') ||
                 document.querySelector('[class*="cors"]') ||
                 !!(window as any).corsExtension;
        },
        name: 'CORS Extension',
        recommendation: 'Configure CORS extension to allow local development domains'
      }
    ];

    // Run extension detection tests
    for (const test of extensionTests) {
      try {
        if (test.test()) {
          detectedExtensions.push(test.name);
          recommendations.push(test.recommendation);
        }
      } catch (error) {
        console.warn(`Extension detection test failed for ${test.name}:`, error);
      }
    }

    // Check for modified navigator properties (common with privacy extensions)
    const navigatorModifications = this.checkNavigatorModifications();
    if (navigatorModifications.length > 0) {
      detectedExtensions.push('Navigator Privacy Extension');
      recommendations.push('Disable extensions that modify browser fingerprinting');
    }

    const severity = detectedExtensions.length >= 3 ? 'high' : 
                    detectedExtensions.length >= 1 ? 'medium' : 'low';

    return {
      detected: detectedExtensions.length > 0,
      conflictingExtensions: detectedExtensions,
      recommendations,
      severity
    };
  }

  /**
   * Check for navigator property modifications
   */
  private checkNavigatorModifications(): string[] {
    const modifications: string[] = [];
    
    try {
      // Check if common navigator properties have been modified
      const expectedUserAgent = navigator.userAgent;
      const expectedPlatform = navigator.platform;
      
      // Some privacy extensions modify these
      if (expectedUserAgent.length < 50) {
        modifications.push('userAgent');
      }
      
      if (!expectedPlatform || expectedPlatform === '') {
        modifications.push('platform');
      }

      // Check for webRTC modifications (privacy extensions often disable this)
      if (!(window as any).RTCPeerConnection && !(window as any).webkitRTCPeerConnection) {
        modifications.push('webRTC');
      }
    } catch (error) {
      console.warn('Navigator modification check failed:', error);
    }

    return modifications;
  }

  /**
   * Intercept fetch requests to detect and handle extension conflicts
   */
  private interceptFetch(): void {
    window.fetch = async (input: RequestInfo | URL, init?: RequestInit): Promise<Response> => {
      const url = input.toString();
      
      try {
        const response = await this.originalFetch(input, init);
        
        // Reset conflict flag on successful request
        if (response.ok) {
          this.conflictDetected = false;
          this.requestAttempts.delete(url);
        }
        
        return response;
      } catch (error) {
        console.warn('Fetch error detected:', error);
        
        // Check if this is an extension-related error
        if (this.isExtensionConflictError(error)) {
          this.handleExtensionConflict(url, error);
        }
        
        throw error;
      }
    };
  }

  /**
   * Identify extension-related errors
   */
  private isExtensionConflictError(error: any): boolean {
    const extensionErrorPatterns = [
      'unauthorized request',
      'browser extension',
      'cors',
      'blocked by client',
      'request intercepted',
      'content security policy',
      'extension conflict'
    ];

    const errorMessage = error.message?.toLowerCase() || '';
    return extensionErrorPatterns.some(pattern => errorMessage.includes(pattern));
  }

  /**
   * Handle detected extension conflicts
   */
  private async handleExtensionConflict(url: string, error: any): Promise<void> {
    this.conflictDetected = true;
    
    // Track failed attempts
    const attempts = this.requestAttempts.get(url) || 0;
    this.requestAttempts.set(url, attempts + 1);
    
    // Show user guidance after multiple failures
    if (attempts >= 2) {
      const conflictInfo = await this.detectConflictingExtensions();
      this.showExtensionConflictGuidance(conflictInfo);
    }
  }

  /**
   * Robust fetch with extension conflict handling
   */
  async robustFetch({ url, options = {}, retries = 3, timeout = 10000 }: NetworkRequestOptions): Promise<Response> {
    for (let attempt = 1; attempt <= retries; attempt++) {
      try {
        // Create timeout controller
        const controller = new AbortController();
        const timeoutId = setTimeout(() => controller.abort(), timeout);
        
        // Add abort signal to options
        const requestOptions: RequestInit = {
          ...options,
          signal: controller.signal,
          // Add headers to bypass common extension blocks
          headers: {
            'Cache-Control': 'no-cache',
            'Pragma': 'no-cache',
            'X-Requested-With': 'XMLHttpRequest',
            ...options.headers
          }
        };

        const response = await this.originalFetch(url, requestOptions);
        clearTimeout(timeoutId);
        
        if (!response.ok && attempt < retries) {
          // Wait before retry (exponential backoff)
          await new Promise(resolve => setTimeout(resolve, attempt * 1000));
          continue;
        }
        
        return response;
      } catch (error) {
        clearTimeout();
        
        if (attempt === retries) {
          // Final attempt failed
          if (this.isExtensionConflictError(error)) {
            const conflictInfo = await this.detectConflictingExtensions();
            this.showExtensionConflictGuidance(conflictInfo);
          }
          throw error;
        }
        
        // Wait before retry
        await new Promise(resolve => setTimeout(resolve, attempt * 1000));
      }
    }
    
    throw new Error('Maximum retry attempts reached');
  }

  /**
   * Show user guidance for resolving extension conflicts
   */
  private showExtensionConflictGuidance(conflictInfo: ExtensionConflictInfo): void {
    if (!conflictInfo.detected) return;

    const message = `
🔧 Browser Extension Conflict Detected

${conflictInfo.conflictingExtensions.length > 0 ? 
  `Potentially conflicting extensions:\n• ${conflictInfo.conflictingExtensions.join('\n• ')}\n\n` : 
  ''
}Recommended solutions:
${conflictInfo.recommendations.map(rec => `• ${rec}`).join('\n')}

Quick fixes:
• Open in incognito/private mode
• Temporarily disable extensions
• Refresh the page
• Try a different browser

Severity: ${conflictInfo.severity.toUpperCase()}
    `.trim();

    // Show notification (you can customize this based on your notification system)
    console.warn('Browser Extension Conflict:', message);
    
    // Show user-friendly alert (can be replaced with custom modal)
    if (conflictInfo.severity === 'high') {
      alert(`Browser Extension Conflict Detected\n\n${message}`);
    }
  }

  /**
   * Generate extension-safe API URL
   */
  generateSafeApiUrl(endpoint: string): string {
    const baseUrl = process.env.EXPO_PUBLIC_BACKEND_URL || 
                   'https://carmedia-hub-1.preview.emergentagent.com';
    
    // Add cache-busting parameter to avoid extension caching
    const cacheBuster = Date.now();
    const separator = endpoint.includes('?') ? '&' : '?';
    
    return `${baseUrl}${endpoint}${separator}_cb=${cacheBuster}`;
  }

  /**
   * Check if running in extension-safe environment
   */
  isExtensionSafeEnvironment(): boolean {
    // Check for incognito mode indicators
    const isIncognito = (
      // Chrome incognito detection
      (window as any).chrome?.runtime?.onConnect === undefined ||
      // Firefox private browsing
      (window as any).InstallTrigger === undefined ||
      // General private browsing indicators
      navigator.webdriver === true
    );

    return isIncognito || !this.conflictDetected;
  }

  /**
   * Get current conflict status
   */
  getConflictStatus(): { hasConflict: boolean; attempts: number } {
    const totalAttempts = Array.from(this.requestAttempts.values())
      .reduce((sum, attempts) => sum + attempts, 0);
    
    return {
      hasConflict: this.conflictDetected,
      attempts: totalAttempts
    };
  }
}

// Export singleton instance
export const browserExtensionDetector = BrowserExtensionDetector.getInstance();

// React hook for extension conflict handling
export function useExtensionConflictDetection() {
  const [conflictInfo, setConflictInfo] = React.useState<ExtensionConflictInfo | null>(null);
  const [isLoading, setIsLoading] = React.useState(false);

  const checkForConflicts = async () => {
    setIsLoading(true);
    try {
      const info = await browserExtensionDetector.detectConflictingExtensions();
      setConflictInfo(info);
    } catch (error) {
      console.error('Extension conflict detection failed:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const robustApiCall = async (url: string, options?: RequestInit) => {
    return browserExtensionDetector.robustFetch({
      url: browserExtensionDetector.generateSafeApiUrl(url),
      options
    });
  };

  React.useEffect(() => {
    checkForConflicts();
  }, []);

  return {
    conflictInfo,
    isLoading,
    checkForConflicts,
    robustApiCall,
    isExtensionSafe: browserExtensionDetector.isExtensionSafeEnvironment(),
    conflictStatus: browserExtensionDetector.getConflictStatus()
  };
}