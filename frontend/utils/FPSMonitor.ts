/**
 * FPS Monitor - React Native equivalent of Core Animation instrument
 * Monitors frame rates, identifies dropped frames, and UI rendering performance
 */

interface FPSMetrics {
  currentFPS: number;
  averageFPS: number;
  droppedFrames: number;
  totalFrames: number;
  lastUpdate: number;
  renderingIssues: RenderingIssue[];
}

interface RenderingIssue {
  timestamp: number;
  type: 'dropped_frame' | 'slow_render' | 'offscreen_render';
  description: string;
  componentName?: string;
  duration?: number;
}

class FPSMonitor {
  private static instance: FPSMonitor;
  private isMonitoring: boolean = false;
  private frameCount: number = 0;
  private droppedFrameCount: number = 0;
  private lastFrameTime: number = 0;
  private fpsHistory: number[] = [];
  private renderingIssues: RenderingIssue[] = [];
  private animationFrameId: number | null = null;
  private startTime: number = 0;

  // Target 60 FPS for smooth UI
  private readonly TARGET_FPS = 60;
  private readonly FRAME_TIME_THRESHOLD = 1000 / 60; // 16.67ms per frame
  private readonly DROPPED_FRAME_THRESHOLD = 1000 / 30; // 33ms indicates dropped frame

  static getInstance(): FPSMonitor {
    if (!FPSMonitor.instance) {
      FPSMonitor.instance = new FPSMonitor();
    }
    return FPSMonitor.instance;
  }

  /**
   * Start FPS monitoring
   */
  start(): void {
    if (this.isMonitoring) return;

    this.isMonitoring = true;
    this.frameCount = 0;
    this.droppedFrameCount = 0;
    this.startTime = performance.now();
    this.lastFrameTime = this.startTime;
    this.fpsHistory = [];
    this.renderingIssues = [];

    this.monitorFrame();
    console.log('📊 FPS Monitor started');
  }

  /**
   * Stop FPS monitoring
   */
  stop(): void {
    if (!this.isMonitoring) return;

    this.isMonitoring = false;
    if (this.animationFrameId) {
      cancelAnimationFrame(this.animationFrameId);
      this.animationFrameId = null;
    }

    console.log('📊 FPS Monitor stopped');
    this.logSummary();
  }

  /**
   * Monitor individual frame
   */
  private monitorFrame = (): void => {
    if (!this.isMonitoring) return;

    const currentTime = performance.now();
    const deltaTime = currentTime - this.lastFrameTime;

    // Check for dropped frames
    if (deltaTime > this.DROPPED_FRAME_THRESHOLD) {
      this.droppedFrameCount++;
      this.addRenderingIssue({
        timestamp: currentTime,
        type: 'dropped_frame',
        description: `Frame dropped: ${deltaTime.toFixed(2)}ms (target: ${this.FRAME_TIME_THRESHOLD.toFixed(2)}ms)`,
        duration: deltaTime,
      });
    }

    // Check for slow renders
    if (deltaTime > this.FRAME_TIME_THRESHOLD * 2) {
      this.addRenderingIssue({
        timestamp: currentTime,
        type: 'slow_render',
        description: `Slow render detected: ${deltaTime.toFixed(2)}ms`,
        duration: deltaTime,
      });
    }

    this.frameCount++;
    this.lastFrameTime = currentTime;

    // Calculate FPS every second
    if (this.frameCount % 60 === 0) {
      this.calculateFPS();
    }

    this.animationFrameId = requestAnimationFrame(this.monitorFrame);
  };

  /**
   * Calculate current FPS
   */
  private calculateFPS(): void {
    const currentTime = performance.now();
    const elapsed = currentTime - this.startTime;
    const currentFPS = (this.frameCount / elapsed) * 1000;

    this.fpsHistory.push(currentFPS);

    // Keep only last 60 measurements (1 minute at 1Hz)
    if (this.fpsHistory.length > 60) {
      this.fpsHistory = this.fpsHistory.slice(-60);
    }

    // Log significant FPS drops
    if (currentFPS < this.TARGET_FPS * 0.8) {
      console.warn(`🐌 Low FPS detected: ${currentFPS.toFixed(1)} FPS (target: ${this.TARGET_FPS} FPS)`);
    }
  }

  /**
   * Add rendering issue
   */
  private addRenderingIssue(issue: RenderingIssue): void {
    this.renderingIssues.push(issue);

    // Keep only last 100 issues
    if (this.renderingIssues.length > 100) {
      this.renderingIssues = this.renderingIssues.slice(-100);
    }

    // Log critical issues
    if (issue.type === 'dropped_frame' && (issue.duration || 0) > 100) {
      console.warn(`⚠️ Critical frame drop: ${issue.description}`);
    }
  }

  /**
   * Get current FPS metrics
   */
  getMetrics(): FPSMetrics {
    const currentTime = performance.now();
    const elapsed = currentTime - this.startTime;
    const currentFPS = elapsed > 0 ? (this.frameCount / elapsed) * 1000 : 0;
    const averageFPS = this.fpsHistory.length > 0 
      ? this.fpsHistory.reduce((sum, fps) => sum + fps, 0) / this.fpsHistory.length
      : currentFPS;

    return {
      currentFPS,
      averageFPS,
      droppedFrames: this.droppedFrameCount,
      totalFrames: this.frameCount,
      lastUpdate: currentTime,
      renderingIssues: [...this.renderingIssues],
    };
  }

  /**
   * Get performance grade
   */
  getPerformanceGrade(): { grade: string; color: string; description: string } {
    const metrics = this.getMetrics();
    const avgFPS = metrics.averageFPS;
    const dropRate = metrics.totalFrames > 0 ? (metrics.droppedFrames / metrics.totalFrames) * 100 : 0;

    if (avgFPS >= 55 && dropRate < 1) {
      return {
        grade: 'A',
        color: '#4CAF50',
        description: 'Excellent performance - Smooth 60 FPS',
      };
    } else if (avgFPS >= 45 && dropRate < 3) {
      return {
        grade: 'B',
        color: '#8BC34A',
        description: 'Good performance - Minor hitches',
      };
    } else if (avgFPS >= 30 && dropRate < 5) {
      return {
        grade: 'C',
        color: '#FFC107',
        description: 'Fair performance - Noticeable stuttering',
      };
    } else if (avgFPS >= 20 && dropRate < 10) {
      return {
        grade: 'D',
        color: '#FF9800',
        description: 'Poor performance - Significant lag',
      };
    } else {
      return {
        grade: 'F',
        color: '#F44336',
        description: 'Critical performance - Unusable UI',
      };
    }
  }

  /**
   * Monitor specific component rendering
   */
  monitorComponent(componentName: string, renderStart: number): void {
    const renderEnd = performance.now();
    const renderTime = renderEnd - renderStart;

    // Component renders should be fast (< 16ms for 60 FPS)
    if (renderTime > 16) {
      this.addRenderingIssue({
        timestamp: renderEnd,
        type: 'slow_render',
        description: `Slow component render: ${componentName}`,
        componentName,
        duration: renderTime,
      });
    }
  }

  /**
   * Detect offscreen rendering (expensive operations)
   */
  detectOffscreenRendering(description: string): void {
    this.addRenderingIssue({
      timestamp: performance.now(),
      type: 'offscreen_render',
      description: `Offscreen rendering detected: ${description}`,
    });
  }

  /**
   * Log performance summary
   */
  private logSummary(): void {
    const metrics = this.getMetrics();
    const grade = this.getPerformanceGrade();

    console.log('📊 FPS Monitor Summary:', {
      averageFPS: metrics.averageFPS.toFixed(1),
      droppedFrames: metrics.droppedFrames,
      totalFrames: metrics.totalFrames,
      dropRate: ((metrics.droppedFrames / metrics.totalFrames) * 100).toFixed(1) + '%',
      performanceGrade: grade.grade,
      totalRenderingIssues: metrics.renderingIssues.length,
    });
  }

  /**
   * Export detailed report
   */
  exportReport(): string {
    const metrics = this.getMetrics();
    const grade = this.getPerformanceGrade();

    return JSON.stringify({
      timestamp: new Date().toISOString(),
      metrics,
      performanceGrade: grade,
      fpsHistory: this.fpsHistory,
      detailedIssues: this.renderingIssues,
    }, null, 2);
  }

  /**
   * Reset all data
   */
  reset(): void {
    this.frameCount = 0;
    this.droppedFrameCount = 0;
    this.fpsHistory = [];
    this.renderingIssues = [];
    this.startTime = performance.now();
    this.lastFrameTime = this.startTime;
  }
}

// Export singleton instance
export const fpsMonitor = FPSMonitor.getInstance();

import React from 'react';

// React hook for FPS monitoring  
export function useFPSMonitor() {
  const [metrics, setMetrics] = React.useState<FPSMetrics | null>(null);
  const [isMonitoring, setIsMonitoring] = React.useState(false);

  React.useEffect(() => {
    let interval: NodeJS.Timeout;

    if (isMonitoring) {
      fpsMonitor.start();
      interval = setInterval(() => {
        setMetrics(fpsMonitor.getMetrics());
      }, 1000);
    } else {
      fpsMonitor.stop();
    }

    return () => {
      if (interval) clearInterval(interval);
      fpsMonitor.stop();
    };
  }, [isMonitoring]);

  return {
    metrics,
    isMonitoring,
    startMonitoring: () => setIsMonitoring(true),
    stopMonitoring: () => setIsMonitoring(false),
    getPerformanceGrade: () => fpsMonitor.getPerformanceGrade(),
    exportReport: () => fpsMonitor.exportReport(),
  };
}