import React, { Suspense, ComponentType, useState, useEffect, useRef } from 'react';
import { InteractionManager, Platform, AppState, AppStateStatus } from 'react-native';
import { PerformanceMonitor, MemoryOptimizer } from './performance';

// Advanced lazy loading with preloading capabilities
export class LazyComponentLoader {
  private static preloadPromises = new Map<string, Promise<any>>();
  private static loadedComponents = new Map<string, ComponentType<any>>();

  static lazy<T extends ComponentType<any>>(
    importFunc: () => Promise<{ default: T }>,
    componentName: string,
    preload: boolean = false
  ): React.LazyExoticComponent<T> {
    const lazyComponent = React.lazy(importFunc);
    
    if (preload) {
      this.preload(componentName, importFunc);
    }
    
    return lazyComponent;
  }

  static preload<T extends ComponentType<any>>(
    componentName: string,
    importFunc: () => Promise<{ default: T }>
  ): Promise<{ default: T }> {
    if (!this.preloadPromises.has(componentName)) {
      const promise = importFunc();
      this.preloadPromises.set(componentName, promise);
      
      promise.then(({ default: Component }) => {
        this.loadedComponents.set(componentName, Component);
        console.log(`🚀 Preloaded component: ${componentName}`);
      }).catch(error => {
        console.error(`❌ Failed to preload component ${componentName}:`, error);
        this.preloadPromises.delete(componentName);
      });
    }
    
    return this.preloadPromises.get(componentName)!;
  }

  static isPreloaded(componentName: string): boolean {
    return this.loadedComponents.has(componentName);
  }
}

// Intelligent bundle splitting
export const createAsyncComponent = <P extends object>(
  importFunc: () => Promise<{ default: ComponentType<P> }>,
  fallback?: ComponentType<any>,
  options: {
    preload?: boolean;
    priority?: 'high' | 'low';
    timeout?: number;
  } = {}
) => {
  const { preload = false, priority = 'low', timeout = 10000 } = options;
  const componentName = importFunc.toString().match(/\/([^\/]+)\.tsx?/)?.[1] || 'UnknownComponent';

  const LazyComponent = LazyComponentLoader.lazy(importFunc, componentName, preload);

  return (props: P) => (
    <Suspense fallback={fallback ? React.createElement(fallback) : null}>
      <LazyComponent {...props} />
    </Suspense>
  );
};

// Advanced caching with TTL and size limits
export class AdvancedCache<T = any> {
  private cache = new Map<string, { value: T; timestamp: number; accessCount: number }>();
  private readonly maxSize: number;
  private readonly ttl: number; // Time to live in milliseconds

  constructor(maxSize: number = 100, ttlMinutes: number = 30) {
    this.maxSize = maxSize;
    this.ttl = ttlMinutes * 60 * 1000;
  }

  set(key: string, value: T): void {
    // Remove expired entries
    this.cleanup();

    // Remove oldest entry if at capacity
    if (this.cache.size >= this.maxSize) {
      const oldestKey = this.getOldestKey();
      if (oldestKey) {
        this.cache.delete(oldestKey);
      }
    }

    this.cache.set(key, {
      value,
      timestamp: Date.now(),
      accessCount: 0,
    });
  }

  get(key: string): T | undefined {
    const entry = this.cache.get(key);
    
    if (!entry) {
      return undefined;
    }

    // Check if expired
    if (Date.now() - entry.timestamp > this.ttl) {
      this.cache.delete(key);
      return undefined;
    }

    // Update access count
    entry.accessCount++;
    
    return entry.value;
  }

  has(key: string): boolean {
    return this.get(key) !== undefined;
  }

  delete(key: string): boolean {
    return this.cache.delete(key);
  }

  clear(): void {
    this.cache.clear();
  }

  size(): number {
    this.cleanup();
    return this.cache.size;
  }

  getStats(): { size: number; hitRate: number; totalAccesses: number } {
    let totalAccesses = 0;
    this.cache.forEach(entry => {
      totalAccesses += entry.accessCount;
    });

    return {
      size: this.cache.size,
      hitRate: totalAccesses > 0 ? (this.cache.size / totalAccesses) * 100 : 0,
      totalAccesses,
    };
  }

  private cleanup(): void {
    const now = Date.now();
    for (const [key, entry] of this.cache.entries()) {
      if (now - entry.timestamp > this.ttl) {
        this.cache.delete(key);
      }
    }
  }

  private getOldestKey(): string | undefined {
    let oldestKey: string | undefined;
    let oldestTimestamp = Date.now();

    for (const [key, entry] of this.cache.entries()) {
      if (entry.timestamp < oldestTimestamp) {
        oldestTimestamp = entry.timestamp;
        oldestKey = key;
      }
    }

    return oldestKey;
  }
}

// Image optimization and lazy loading
export class ImageOptimizer {
  private static cache = new AdvancedCache<string>(50, 60); // 60-minute cache
  private static loadingImages = new Set<string>();

  static optimizeImageUrl(
    url: string,
    options: {
      width?: number;
      height?: number;
      quality?: number;
      format?: 'webp' | 'jpeg' | 'png';
    } = {}
  ): string {
    if (!url || url.startsWith('data:')) return url;

    const { width, height, quality = 80, format = 'webp' } = options;
    
    try {
      const urlObj = new URL(url);
      
      if (width) urlObj.searchParams.set('w', width.toString());
      if (height) urlObj.searchParams.set('h', height.toString());
      urlObj.searchParams.set('q', quality.toString());
      if (Platform.OS === 'web' && format === 'webp') {
        urlObj.searchParams.set('f', 'webp');
      }

      return urlObj.toString();
    } catch {
      return url;
    }
  }

  static async preloadImage(url: string): Promise<void> {
    if (this.cache.has(url) || this.loadingImages.has(url)) {
      return;
    }

    this.loadingImages.add(url);

    try {
      if (Platform.OS === 'web') {
        const img = new Image();
        await new Promise<void>((resolve, reject) => {
          img.onload = () => resolve();
          img.onerror = reject;
          img.src = url;
        });
      } else {
        // For React Native, we would use Image.prefetch
        // await Image.prefetch(url);
      }
      
      this.cache.set(url, 'loaded');
      console.log(`📷 Preloaded image: ${url.substring(0, 50)}...`);
    } catch (error) {
      console.error('Failed to preload image:', error);
    } finally {
      this.loadingImages.delete(url);
    }
  }
}

// Render optimization hooks
export function useOptimizedRender<T>(
  value: T,
  isEqual?: (a: T, b: T) => boolean
): T {
  const ref = useRef<T>(value);
  
  const areEqual = isEqual || ((a, b) => JSON.stringify(a) === JSON.stringify(b));
  
  if (!areEqual(ref.current, value)) {
    ref.current = value;
  }
  
  return ref.current;
}

export function useDebounce<T>(value: T, delay: number): T {
  const [debouncedValue, setDebouncedValue] = useState<T>(value);

  useEffect(() => {
    const handler = setTimeout(() => {
      setDebouncedValue(value);
    }, delay);

    return () => {
      clearTimeout(handler);
    };
  }, [value, delay]);

  return debouncedValue;
}

// Memory pressure monitoring
export class MemoryPressureMonitor {
  private static listeners: Array<() => void> = [];
  private static isMonitoring = false;

  static startMonitoring(): void {
    if (this.isMonitoring) return;
    this.isMonitoring = true;

    // Monitor app state changes
    AppState.addEventListener('change', this.handleAppStateChange);

    // Periodic memory check
    const memoryInterval = setInterval(() => {
      this.checkMemoryPressure();
    }, 30000); // Check every 30 seconds

    // Cleanup on app termination
    const cleanup = () => {
      clearInterval(memoryInterval);
      AppState.removeEventListener('change', this.handleAppStateChange);
      this.isMonitoring = false;
    };

    // Store cleanup function
    (global as any).__memoryCleanup = cleanup;
  }

  static addListener(callback: () => void): void {
    this.listeners.push(callback);
  }

  static removeListener(callback: () => void): void {
    this.listeners = this.listeners.filter(listener => listener !== callback);
  }

  private static handleAppStateChange = (nextAppState: AppStateStatus) => {
    if (nextAppState === 'background') {
      console.log('📱 App backgrounded - triggering memory cleanup');
      this.triggerMemoryCleanup();
    }
  };

  private static checkMemoryPressure(): void {
    // In a real implementation, you would check actual memory usage
    // For now, we'll simulate based on cache sizes
    const cacheSize = MemoryOptimizer.size();
    const criticalThreshold = 80; // MB

    if (cacheSize > criticalThreshold) {
      console.warn(`⚠️ Memory pressure detected: ${cacheSize}MB cache size`);
      this.triggerMemoryCleanup();
    }
  }

  private static triggerMemoryCleanup(): void {
    this.listeners.forEach(listener => {
      try {
        listener();
      } catch (error) {
        console.error('Memory cleanup listener error:', error);
      }
    });

    // Clear caches
    MemoryOptimizer.clear();
    
    // Force garbage collection if available
    if (global.gc) {
      global.gc();
    }
  }
}

// Network-aware loading
export class NetworkAwareLoader {
  private static connectionType: 'wifi' | '4g' | '3g' | 'slow' = 'wifi';

  static setConnectionType(type: 'wifi' | '4g' | '3g' | 'slow'): void {
    this.connectionType = type;
  }

  static getOptimalLoadingStrategy(): {
    concurrentRequests: number;
    imageQuality: number;
    enablePreloading: boolean;
  } {
    switch (this.connectionType) {
      case 'wifi':
        return {
          concurrentRequests: 6,
          imageQuality: 90,
          enablePreloading: true,
        };
      case '4g':
        return {
          concurrentRequests: 4,
          imageQuality: 80,
          enablePreloading: true,
        };
      case '3g':
        return {
          concurrentRequests: 2,
          imageQuality: 60,
          enablePreloading: false,
        };
      case 'slow':
        return {
          concurrentRequests: 1,
          imageQuality: 40,
          enablePreloading: false,
        };
      default:
        return {
          concurrentRequests: 3,
          imageQuality: 70,
          enablePreloading: false,
        };
    }
  }
}

// Performance monitoring and analytics
export class PerformanceAnalytics {
  private static metrics: Array<{
    name: string;
    duration: number;
    timestamp: number;
    metadata?: any;
  }> = [];

  static recordMetric(
    name: string,
    duration: number,
    metadata?: any
  ): void {
    this.metrics.push({
      name,
      duration,
      timestamp: Date.now(),
      metadata,
    });

    // Keep only last 100 metrics
    if (this.metrics.length > 100) {
      this.metrics = this.metrics.slice(-100);
    }

    // Log slow operations
    if (duration > 1000) {
      console.warn(`🐌 Slow operation detected: ${name} took ${duration}ms`);
    }
  }

  static getMetrics(name?: string): Array<{
    name: string;
    duration: number;
    timestamp: number;
    metadata?: any;
  }> {
    if (name) {
      return this.metrics.filter(metric => metric.name === name);
    }
    return [...this.metrics];
  }

  static getAverageTime(name: string): number {
    const relevantMetrics = this.getMetrics(name);
    if (relevantMetrics.length === 0) return 0;

    const totalTime = relevantMetrics.reduce((sum, metric) => sum + metric.duration, 0);
    return totalTime / relevantMetrics.length;
  }

  static getSlowOperations(threshold: number = 1000): Array<{
    name: string;
    duration: number;
    timestamp: number;
  }> {
    return this.metrics.filter(metric => metric.duration > threshold);
  }

  static generateReport(): {
    totalMetrics: number;
    averageResponseTime: number;
    slowOperations: number;
    topSlowOperations: Array<{ name: string; averageTime: number }>;
  } {
    const uniqueOperations = [...new Set(this.metrics.map(m => m.name))];
    const totalTime = this.metrics.reduce((sum, metric) => sum + metric.duration, 0);
    const slowOps = this.getSlowOperations();

    const topSlow = uniqueOperations
      .map(name => ({
        name,
        averageTime: this.getAverageTime(name),
      }))
      .sort((a, b) => b.averageTime - a.averageTime)
      .slice(0, 5);

    return {
      totalMetrics: this.metrics.length,
      averageResponseTime: this.metrics.length > 0 ? totalTime / this.metrics.length : 0,
      slowOperations: slowOps.length,
      topSlowOperations: topSlow,
    };
  }
}

// Initialize performance monitoring
export const initializePerformanceOptimizations = () => {
  console.log('🚀 Initializing advanced performance optimizations...');
  
  // Start memory pressure monitoring
  MemoryPressureMonitor.startMonitoring();
  
  // Set up performance analytics
  PerformanceMonitor.start('app-initialization');
  PerformanceAnalytics.recordMetric('app-initialization', 0, {
    platform: Platform.OS,
    timestamp: Date.now(),
  });
  
  console.log('✅ Performance optimizations initialized');
};

export {
  LazyComponentLoader,
  AdvancedCache,
  ImageOptimizer,
  MemoryPressureMonitor,
  NetworkAwareLoader,
  PerformanceAnalytics,
};