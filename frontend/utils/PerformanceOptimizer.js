/**
 * Performance Optimization Utilities
 * Preemptive measures to improve app performance
 */
import { Platform } from 'react-native';

export class PerformanceOptimizer {
  
  /**
   * Lazy loading utility for heavy components
   */
  static createLazyComponent(componentLoader) {
    return React.lazy(() => {
      return new Promise(resolve => {
        // Add small delay to prevent UI blocking
        setTimeout(() => {
          resolve(componentLoader());
        }, 50);
      });
    });
  }

  /**
   * Debounce function for search inputs and API calls
   */
  static debounce(func, delay = 300) {
    let timeoutId;
    return (...args) => {
      clearTimeout(timeoutId);
      timeoutId = setTimeout(() => func.apply(null, args), delay);
    };
  }

  /**
   * Throttle function for scroll events and continuous actions
   */
  static throttle(func, limit = 100) {
    let inThrottle;
    return (...args) => {
      if (!inThrottle) {
        func.apply(null, args);
        inThrottle = true;
        setTimeout(() => inThrottle = false, limit);
      }
    };
  }

  /**
   * Memory cleanup for large objects
   */
  static cleanupLargeObjects(objects) {
    objects.forEach(obj => {
      if (obj && typeof obj === 'object') {
        Object.keys(obj).forEach(key => {
          if (obj[key] && typeof obj[key] === 'object') {
            obj[key] = null;
          }
        });
      }
    });
  }

  /**
   * Optimize image loading with progressive enhancement
   */
  static getOptimizedImageProps(source, size = 'medium') {
    const sizes = {
      small: { width: 100, height: 100 },
      medium: { width: 200, height: 200 },
      large: { width: 400, height: 400 }
    };

    return {
      source,
      style: sizes[size],
      resizeMode: 'cover',
      // Add progressive loading for better UX
      loadingIndicatorSource: { uri: 'data:image/gif;base64,R0lGODlhAQABAIAAAAAAAP///yH5BAEAAAAALAAAAAABAAEAAAIBRAA7' }
    };
  }

  /**
   * Batch API requests to reduce network overhead
   */
  static createBatchRequestManager(maxBatchSize = 5, batchDelay = 100) {
    const batchQueue = [];
    let batchTimeout = null;

    const processBatch = async () => {
      if (batchQueue.length === 0) return;
      
      const currentBatch = batchQueue.splice(0, maxBatchSize);
      const promises = currentBatch.map(request => request.execute());
      
      try {
        const results = await Promise.allSettled(promises);
        results.forEach((result, index) => {
          if (result.status === 'fulfilled') {
            currentBatch[index].resolve(result.value);
          } else {
            currentBatch[index].reject(result.reason);
          }
        });
      } catch (error) {
        currentBatch.forEach(request => request.reject(error));
      }

      // Process remaining requests if any
      if (batchQueue.length > 0) {
        setTimeout(processBatch, batchDelay);
      }
    };

    return {
      addRequest: (request) => {
        return new Promise((resolve, reject) => {
          batchQueue.push({ ...request, resolve, reject });
          
          // Clear existing timeout
          if (batchTimeout) {
            clearTimeout(batchTimeout);
          }
          
          // Set new timeout
          batchTimeout = setTimeout(processBatch, batchDelay);
        });
      }
    };
  }

  /**
   * Optimize component re-renders with memoization helper
   */
  static createMemoizedSelector(selector) {
    let lastArgs = null;
    let lastResult = null;

    return (...args) => {
      // Shallow comparison of arguments
      if (lastArgs && args.length === lastArgs.length && 
          args.every((arg, index) => arg === lastArgs[index])) {
        return lastResult;
      }

      lastArgs = args;
      lastResult = selector(...args);
      return lastResult;
    };
  }

  /**
   * Preload critical resources
   */
  static async preloadCriticalResources(resources) {
    console.log('🚀 Preloading critical resources...');
    
    const preloadPromises = resources.map(async (resource) => {
      try {
        switch (resource.type) {
          case 'api':
            const response = await fetch(resource.url, { method: 'HEAD' });
            console.log(`✅ API ${resource.name} preloaded`);
            break;
          case 'image':
            await new Promise((resolve) => {
              const img = new Image();
              img.onload = resolve;
              img.onerror = resolve;
              img.src = resource.url;
            });
            console.log(`✅ Image ${resource.name} preloaded`);
            break;
          default:
            console.log(`⚠️ Unknown resource type: ${resource.type}`);
        }
      } catch (error) {
        console.warn(`❌ Failed to preload ${resource.name}:`, error);
      }
    });

    await Promise.allSettled(preloadPromises);
    console.log('✅ Critical resources preloaded');
  }

  /**
   * Monitor performance metrics
   */
  static startPerformanceMonitoring() {
    if (Platform.OS === 'web' && typeof window !== 'undefined' && window.performance) {
      console.log('📊 Starting performance monitoring...');
      
      // Monitor navigation timing
      setTimeout(() => {
        const navigation = window.performance.getEntriesByType('navigation')[0];
        if (navigation) {
          console.log('📈 Page Load Performance:');
          console.log(`  - DNS Lookup: ${navigation.domainLookupEnd - navigation.domainLookupStart}ms`);
          console.log(`  - Connection: ${navigation.connectEnd - navigation.connectStart}ms`);
          console.log(`  - Response: ${navigation.responseEnd - navigation.responseStart}ms`);
          console.log(`  - DOM Load: ${navigation.domContentLoadedEventEnd - navigation.domContentLoadedEventStart}ms`);
          console.log(`  - Total Load: ${navigation.loadEventEnd - navigation.loadEventStart}ms`);
        }
      }, 1000);

      // Monitor resource timing
      setTimeout(() => {
        const resources = window.performance.getEntriesByType('resource');
        const slowResources = resources.filter(resource => resource.duration > 1000);
        
        if (slowResources.length > 0) {
          console.warn('⚠️ Slow loading resources detected:');
          slowResources.forEach(resource => {
            console.warn(`  - ${resource.name}: ${Math.round(resource.duration)}ms`);
          });
        }
      }, 2000);
    }
  }
}

export default PerformanceOptimizer;