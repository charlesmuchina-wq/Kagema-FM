/**
 * Performance Profiler - React Native equivalent of iOS Time Profiler
 * Measures CPU usage, method execution times, and identifies bottlenecks
 */

import React from 'react';

interface ProfilerResult {
  methodName: string;
  executionTime: number;
  timestamp: number;
  memoryUsage?: number;
  cpuUsage?: number;
}

interface PerformanceMetrics {
  averageExecutionTime: number;
  totalExecutions: number;
  slowestExecution: ProfilerResult;
  fastestExecution: ProfilerResult;
  memoryTrend: number[];
}

class PerformanceProfiler {
  private static instance: PerformanceProfiler;
  private results: ProfilerResult[] = [];
  private isEnabled: boolean = __DEV__;
  private memoryBaseline: number = 0;

  static getInstance(): PerformanceProfiler {
    if (!PerformanceProfiler.instance) {
      PerformanceProfiler.instance = new PerformanceProfiler();
    }
    return PerformanceProfiler.instance;
  }

  /**
   * Time Profiler equivalent - Profile method execution
   */
  profile<T>(methodName: string, fn: () => T): T {
    if (!this.isEnabled) return fn();

    const startTime = performance.now();
    const startMemory = this.getMemoryUsage();
    
    try {
      const result = fn();
      
      // Handle both sync and async results
      if (result instanceof Promise) {
        return result.then((asyncResult) => {
          this.recordResult(methodName, startTime, startMemory);
          return asyncResult;
        }).catch((error) => {
          this.recordResult(methodName, startTime, startMemory, true);
          throw error;
        }) as T;
      }
      
      this.recordResult(methodName, startTime, startMemory);
      return result;
    } catch (error) {
      this.recordResult(methodName, startTime, startMemory, true);
      throw error;
    }
  }

  /**
   * Async profiler for Promise-based operations
   */
  async profileAsync<T>(methodName: string, fn: () => Promise<T>): Promise<T> {
    if (!this.isEnabled) return fn();

    const startTime = performance.now();
    const startMemory = this.getMemoryUsage();
    
    try {
      const result = await fn();
      this.recordResult(methodName, startTime, startMemory);
      return result;
    } catch (error) {
      this.recordResult(methodName, startTime, startMemory, true);
      throw error;
    }
  }

  /**
   * Record profiling result
   */
  private recordResult(methodName: string, startTime: number, startMemory: number, hasError: boolean = false): void {
    const executionTime = performance.now() - startTime;
    const currentMemory = this.getMemoryUsage();
    
    const result: ProfilerResult = {
      methodName: hasError ? `${methodName} (ERROR)` : methodName,
      executionTime,
      timestamp: Date.now(),
      memoryUsage: currentMemory - startMemory,
    };

    this.results.push(result);
    
    // Log slow operations (>100ms)
    if (executionTime > 100) {
      console.warn(`🐌 Slow operation detected: ${methodName} took ${executionTime.toFixed(2)}ms`);
    }

    // Keep only last 1000 results to prevent memory leaks
    if (this.results.length > 1000) {
      this.results = this.results.slice(-1000);
    }
  }

  /**
   * Get memory usage (approximate for React Native)
   */
  private getMemoryUsage(): number {
    // React Native doesn't expose direct memory API like iOS
    // We'll use performance.memory if available (Chrome DevTools)
    if (typeof performance !== 'undefined' && (performance as any).memory) {
      return (performance as any).memory.usedJSHeapSize / 1024 / 1024; // Convert to MB
    }
    return 0;
  }

  /**
   * Get performance metrics for a specific method
   */
  getMetrics(methodName: string): PerformanceMetrics | null {
    const methodResults = this.results.filter(r => r.methodName.includes(methodName));
    
    if (methodResults.length === 0) return null;

    const executionTimes = methodResults.map(r => r.executionTime);
    const averageExecutionTime = executionTimes.reduce((sum, time) => sum + time, 0) / executionTimes.length;
    
    const slowestExecution = methodResults.reduce((prev, current) => 
      prev.executionTime > current.executionTime ? prev : current
    );
    
    const fastestExecution = methodResults.reduce((prev, current) => 
      prev.executionTime < current.executionTime ? prev : current
    );

    return {
      averageExecutionTime,
      totalExecutions: methodResults.length,
      slowestExecution,
      fastestExecution,
      memoryTrend: methodResults.map(r => r.memoryUsage || 0),
    };
  }

  /**
   * Get all results sorted by execution time (slowest first)
   */
  getBottlenecks(limit: number = 10): ProfilerResult[] {
    return [...this.results]
      .sort((a, b) => b.executionTime - a.executionTime)
      .slice(0, limit);
  }

  /**
   * Clear all results
   */
  clear(): void {
    this.results = [];
  }

  /**
   * Export results for analysis
   */
  exportResults(): string {
    return JSON.stringify({
      timestamp: new Date().toISOString(),
      totalResults: this.results.length,
      results: this.results,
      topBottlenecks: this.getBottlenecks(20),
    }, null, 2);
  }

  /**
   * Enable/disable profiling
   */
  setEnabled(enabled: boolean): void {
    this.isEnabled = enabled;
  }

  /**
   * Get current status
   */
  getStatus(): { enabled: boolean; resultCount: number; memoryUsage: number } {
    return {
      enabled: this.isEnabled,
      resultCount: this.results.length,
      memoryUsage: this.getMemoryUsage(),
    };
  }
}

// Export singleton instance
export const performanceProfiler = PerformanceProfiler.getInstance();

// Decorator for automatic profiling
export function Profile(target: any, propertyName: string, descriptor: PropertyDescriptor) {
  const method = descriptor.value;
  
  descriptor.value = function (...args: any[]) {
    return performanceProfiler.profile(
      `${target.constructor.name}.${propertyName}`,
      () => method.apply(this, args)
    );
  };
  
  return descriptor;
}

// Higher-order component for profiling React components
export function withProfiler<P extends object>(
  WrappedComponent: React.ComponentType<P>,
  componentName?: string
): React.ComponentType<P> {
  const ProfiledComponent = (props: P) => {
    const renderStart = performance.now();
    const element = React.createElement(WrappedComponent, props);
    const renderTime = performance.now() - renderStart;
    
    if (renderTime > 16) { // Report slow renders (>16ms for 60fps)
      console.warn(`Slow render: ${componentName || WrappedComponent.displayName || WrappedComponent.name} took ${renderTime.toFixed(2)}ms`);
    }
    
    return element;
  };
  
  ProfiledComponent.displayName = `Profiled(${componentName || WrappedComponent.displayName || WrappedComponent.name})`;
  return ProfiledComponent;
}