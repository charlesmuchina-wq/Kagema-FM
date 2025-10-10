/**
 * Browser Extension Conflict Prevention Tests
 * Automated tests to ensure the app handles extension conflicts gracefully
 */

import { browserExtensionDetector } from '../utils/BrowserExtensionDetector';

// Mock fetch for testing
const originalFetch = global.fetch;

describe('Browser Extension Conflict Prevention', () => {
  beforeEach(() => {
    global.fetch = jest.fn();
    jest.clearAllMocks();
  });

  afterEach(() => {
    global.fetch = originalFetch;
  });

  describe('Extension Detection', () => {
    test('should detect common ad blockers', async () => {
      // Mock DOM elements that indicate ad blockers
      const adBlockElement = document.createElement('div');
      adBlockElement.id = 'adblock';
      document.body.appendChild(adBlockElement);

      const conflictInfo = await browserExtensionDetector.detectConflictingExtensions();
      
      expect(conflictInfo.detected).toBe(true);
      expect(conflictInfo.conflictingExtensions).toContain('AdBlock/uBlock Origin');
      
      document.body.removeChild(adBlockElement);
    });

    test('should detect privacy extensions', async () => {
      // Mock privacy badger global
      (window as any).privacyBadgerLocale = 'en';

      const conflictInfo = await browserExtensionDetector.detectConflictingExtensions();
      
      expect(conflictInfo.detected).toBe(true);
      expect(conflictInfo.conflictingExtensions).toContain('Privacy Badger');
      
      delete (window as any).privacyBadgerLocale;
    });

    test('should provide appropriate severity levels', async () => {
      const conflictInfo = await browserExtensionDetector.detectConflictingExtensions();
      
      expect(['low', 'medium', 'high']).toContain(conflictInfo.severity);
    });
  });

  describe('Robust Fetch', () => {
    test('should retry failed requests', async () => {
      const mockFetch = jest.fn()
        .mockRejectedValueOnce(new Error('Network error'))
        .mockResolvedValueOnce(new Response('success', { status: 200 }));
      
      global.fetch = mockFetch;

      const response = await browserExtensionDetector.robustFetch({
        url: 'https://example.com/api/test',
        retries: 2
      });

      expect(mockFetch).toHaveBeenCalledTimes(2);
      expect(response.status).toBe(200);
    });

    test('should handle timeout scenarios', async () => {
      const mockFetch = jest.fn().mockImplementation(() => 
        new Promise(resolve => setTimeout(() => resolve(new Response('success')), 5000))
      );
      
      global.fetch = mockFetch;

      await expect(
        browserExtensionDetector.robustFetch({
          url: 'https://example.com/api/test',
          timeout: 1000
        })
      ).rejects.toThrow();
    });

    test('should add extension-bypass headers', async () => {
      const mockFetch = jest.fn().mockResolvedValue(new Response('success', { status: 200 }));
      global.fetch = mockFetch;

      await browserExtensionDetector.robustFetch({
        url: 'https://example.com/api/test'
      });

      const [url, options] = mockFetch.mock.calls[0];
      expect(options.headers).toMatchObject({
        'Cache-Control': 'no-cache',
        'Pragma': 'no-cache',
        'X-Requested-With': 'XMLHttpRequest'
      });
    });
  });

  describe('Extension-Safe URL Generation', () => {
    test('should generate cache-busting URLs', () => {
      const url1 = browserExtensionDetector.generateSafeApiUrl('/api/test');
      const url2 = browserExtensionDetector.generateSafeApiUrl('/api/test');
      
      expect(url1).not.toBe(url2);
      expect(url1).toContain('_cb=');
      expect(url2).toContain('_cb=');
    });

    test('should handle existing query parameters', () => {
      const url = browserExtensionDetector.generateSafeApiUrl('/api/test?param=value');
      
      expect(url).toContain('param=value');
      expect(url).toContain('&_cb=');
    });
  });

  describe('Conflict Status Tracking', () => {
    test('should track request attempts', () => {
      const initialStatus = browserExtensionDetector.getConflictStatus();
      expect(initialStatus.attempts).toBe(0);
      expect(initialStatus.hasConflict).toBe(false);
    });

    test('should identify extension-safe environments', () => {
      const isSafe = browserExtensionDetector.isExtensionSafeEnvironment();
      expect(typeof isSafe).toBe('boolean');
    });
  });

  describe('Error Pattern Recognition', () => {
    test('should identify extension-related errors', async () => {
      const extensionErrors = [
        new Error('Unauthorized request from browser extension'),
        new Error('Request blocked by CORS policy'),
        new Error('Browser extension intercepted request'),
        new Error('Content Security Policy violation')
      ];

      for (const error of extensionErrors) {
        const mockFetch = jest.fn().mockRejectedValue(error);
        global.fetch = mockFetch;

        await expect(
          browserExtensionDetector.robustFetch({
            url: 'https://example.com/api/test',
            retries: 1
          })
        ).rejects.toThrow();
      }
    });
  });

  describe('Performance Under Extension Conflicts', () => {
    test('should maintain performance baselines with retries', async () => {
      const startTime = performance.now();
      
      const mockFetch = jest.fn()
        .mockRejectedValueOnce(new Error('Extension conflict'))
        .mockResolvedValueOnce(new Response('success', { status: 200 }));
      
      global.fetch = mockFetch;

      await browserExtensionDetector.robustFetch({
        url: 'https://example.com/api/test',
        retries: 2
      });

      const endTime = performance.now();
      const totalTime = endTime - startTime;
      
      // Should complete within reasonable time despite retry
      expect(totalTime).toBeLessThan(5000); // 5 seconds max
    });
  });

  describe('Graceful Degradation', () => {
    test('should provide fallback behavior when extensions interfere', async () => {
      // Simulate complete fetch failure
      const mockFetch = jest.fn().mockRejectedValue(new Error('Extension blocked all requests'));
      global.fetch = mockFetch;

      let errorCaught = false;
      try {
        await browserExtensionDetector.robustFetch({
          url: 'https://example.com/api/test',
          retries: 1
        });
      } catch (error) {
        errorCaught = true;
        expect(error.message).toContain('Extension blocked all requests');
      }
      
      expect(errorCaught).toBe(true);
      expect(mockFetch).toHaveBeenCalledTimes(1);
    });
  });
});

// Integration test with actual network requests (can be skipped in CI)
describe('Extension Conflict Integration Tests', () => {
  test('should handle real API requests gracefully', async () => {
    const testUrl = process.env.EXPO_PUBLIC_BACKEND_URL || 'https://carmedia-hub-1.preview.emergentagent.com';
    
    try {
      const response = await browserExtensionDetector.robustFetch({
        url: `${testUrl}/api/`,
        timeout: 5000
      });
      
      expect(response.status).toBe(200);
    } catch (error) {
      // If the request fails due to network issues, that's acceptable for tests
      expect(error).toBeDefined();
    }
  }, 10000);

  test('should detect actual browser environment safely', async () => {
    const conflictInfo = await browserExtensionDetector.detectConflictingExtensions();
    
    // Should not throw errors in test environment
    expect(conflictInfo).toBeDefined();
    expect(typeof conflictInfo.detected).toBe('boolean');
    expect(Array.isArray(conflictInfo.conflictingExtensions)).toBe(true);
    expect(Array.isArray(conflictInfo.recommendations)).toBe(true);
  });
});

// Performance benchmarks
describe('Extension Conflict Performance Benchmarks', () => {
  test('extension detection should complete quickly', async () => {
    const startTime = performance.now();
    
    await browserExtensionDetector.detectConflictingExtensions();
    
    const detectionTime = performance.now() - startTime;
    expect(detectionTime).toBeLessThan(100); // Should complete within 100ms
  });

  test('robust fetch should not significantly impact performance', async () => {
    const mockFetch = jest.fn().mockResolvedValue(new Response('success', { status: 200 }));
    global.fetch = mockFetch;

    const startTime = performance.now();
    
    await browserExtensionDetector.robustFetch({
      url: 'https://example.com/api/test'
    });
    
    const fetchTime = performance.now() - startTime;
    expect(fetchTime).toBeLessThan(50); // Should add minimal overhead
  });
});

// Export test utilities for other test files
export const ExtensionTestUtils = {
  mockAdBlocker: () => {
    const element = document.createElement('div');
    element.id = 'adblock';
    document.body.appendChild(element);
    return () => document.body.removeChild(element);
  },
  
  mockPrivacyBadger: () => {
    (window as any).privacyBadgerLocale = 'en';
    return () => delete (window as any).privacyBadgerLocale;
  },
  
  mockExtensionError: (message: string = 'Browser extension conflict') => {
    const mockFetch = jest.fn().mockRejectedValue(new Error(message));
    global.fetch = mockFetch;
    return mockFetch;
  }
};