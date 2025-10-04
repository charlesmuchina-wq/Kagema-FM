import { InteractionManager, Platform } from 'react-native';

/**
 * Performance optimization utilities for Kagema FM mobile app
 */

// Debounce function for performance optimization
export const debounce = <T extends (...args: any[]) => any>(
  func: T,
  delay: number
): ((...args: Parameters<T>) => void) => {
  let timeoutId: NodeJS.Timeout;
  return (...args: Parameters<T>) => {
    clearTimeout(timeoutId);
    timeoutId = setTimeout(() => func(...args), delay);
  };
};

// Throttle function for high-frequency events
export const throttle = <T extends (...args: any[]) => any>(
  func: T,
  limit: number
): ((...args: Parameters<T>) => void) => {
  let inThrottle: boolean;
  return (...args: Parameters<T>) => {
    if (!inThrottle) {
      func(...args);
      inThrottle = true;
      setTimeout(() => (inThrottle = false), limit);
    }
  };
};

// Run heavy tasks after interactions are complete
export const runAfterInteractions = (callback: () => void): Promise<void> => {
  return new Promise((resolve) => {
    InteractionManager.runAfterInteractions(() => {
      callback();
      resolve();
    });
  });
};

// Memory optimization for large data sets
export class MemoryOptimizer {
  private static cache = new Map<string, any>();
  private static readonly MAX_CACHE_SIZE = 50;

  static set(key: string, value: any): void {
    if (this.cache.size >= this.MAX_CACHE_SIZE) {
      const firstKey = this.cache.keys().next().value;
      this.cache.delete(firstKey);
    }
    this.cache.set(key, value);
  }

  static get(key: string): any {
    return this.cache.get(key);
  }

  static clear(): void {
    this.cache.clear();
  }

  static delete(key: string): boolean {
    return this.cache.delete(key);
  }

  static size(): number {
    return this.cache.size;
  }
}

// Performance monitoring
export class PerformanceMonitor {
  private static startTimes = new Map<string, number>();

  static start(label: string): void {
    this.startTimes.set(label, Date.now());
  }

  static end(label: string): number {
    const startTime = this.startTimes.get(label);
    if (!startTime) {
      console.warn(`Performance monitor: No start time found for ${label}`);
      return 0;
    }

    const duration = Date.now() - startTime;
    this.startTimes.delete(label);
    
    console.log(`⚡ Performance [${label}]: ${duration}ms`);
    return duration;
  }

  static measure<T>(label: string, fn: () => T): T {
    this.start(label);
    const result = fn();
    this.end(label);
    return result;
  }

  static async measureAsync<T>(label: string, fn: () => Promise<T>): Promise<T> {
    this.start(label);
    const result = await fn();
    this.end(label);
    return result;
  }
}

// Image optimization utilities
export const optimizeImageSource = (uri: string, width?: number, height?: number) => {
  if (!uri) return { uri };

  // For web platform, we can add resize parameters
  if (Platform.OS === 'web') {
    const url = new URL(uri);
    if (width) url.searchParams.set('w', width.toString());
    if (height) url.searchParams.set('h', height.toString());
    return { uri: url.toString() };
  }

  // For mobile, return as is (React Native handles optimization)
  return { uri };
};

// Bundle size optimization
export const lazyImport = <T extends React.ComponentType<any>>(
  importFunc: () => Promise<{ default: T }>
): React.LazyExoticComponent<T> => {
  return React.lazy(importFunc);
};

// Network optimization
export class NetworkOptimizer {
  private static requestQueue: Array<() => Promise<any>> = [];
  private static isProcessing = false;
  private static readonly MAX_CONCURRENT_REQUESTS = 3;

  static async queueRequest<T>(request: () => Promise<T>): Promise<T> {
    return new Promise((resolve, reject) => {
      this.requestQueue.push(async () => {
        try {
          const result = await request();
          resolve(result);
        } catch (error) {
          reject(error);
        }
      });
      this.processQueue();
    });
  }

  private static async processQueue(): Promise<void> {
    if (this.isProcessing || this.requestQueue.length === 0) {
      return;
    }

    this.isProcessing = true;

    while (this.requestQueue.length > 0) {
      const batch = this.requestQueue.splice(0, this.MAX_CONCURRENT_REQUESTS);
      await Promise.all(batch.map(request => request()));
    }

    this.isProcessing = false;
  }
}

// Audio streaming optimization
export const optimizeAudioStream = (url: string, quality: 'low' | 'medium' | 'high' = 'medium') => {
  // Return optimized stream URL based on connection quality
  const qualityParams = {
    low: '128',
    medium: '256',
    high: '320'
  };

  // If the URL already has bitrate parameter, replace it
  if (url.includes('-256-')) {
    return url.replace('-256-', `-${qualityParams[quality]}-`);
  }

  return url;
};

// Component optimization hooks
import React, { useCallback, useMemo } from 'react';

export const useOptimizedCallback = <T extends (...args: any[]) => any>(
  callback: T,
  deps: React.DependencyList
): T => {
  return useCallback(callback, deps);
};

export const useOptimizedMemo = <T>(
  factory: () => T,
  deps: React.DependencyList | undefined
): T => {
  return useMemo(factory, deps);
};

// Render optimization
export const shouldComponentUpdate = <T extends Record<string, any>>(
  prevProps: T,
  nextProps: T,
  keys?: (keyof T)[]
): boolean => {
  const keysToCheck = keys || Object.keys(nextProps) as (keyof T)[];
  
  return keysToCheck.some(key => prevProps[key] !== nextProps[key]);
};