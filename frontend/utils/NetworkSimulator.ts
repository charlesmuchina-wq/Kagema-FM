/**
 * Network Simulator - React Native equivalent of Network Link Conditioner
 * Simulates various network conditions to test app behavior under poor connectivity
 */

interface NetworkProfile {
  name: string;
  downloadSpeed: number; // Kbps
  uploadSpeed: number; // Kbps
  latency: number; // ms
  packetLoss: number; // percentage
  description: string;
}

interface NetworkRequest {
  url: string;
  method: string;
  timestamp: number;
  actualTime?: number;
  simulatedTime?: number;
  status: 'pending' | 'success' | 'timeout' | 'failed';
  profile: string;
}

class NetworkSimulator {
  private static instance: NetworkSimulator;
  private isEnabled: boolean = false;
  private currentProfile: NetworkProfile;
  private requests: NetworkRequest[] = [];

  // Network profiles based on real-world conditions
  private profiles: NetworkProfile[] = [
    {
      name: 'WiFi',
      downloadSpeed: 50000, // 50 Mbps
      uploadSpeed: 10000, // 10 Mbps  
      latency: 20,
      packetLoss: 0.1,
      description: 'High-speed WiFi connection',
    },
    {
      name: '5G',
      downloadSpeed: 100000, // 100 Mbps
      uploadSpeed: 50000, // 50 Mbps
      latency: 10,
      packetLoss: 0.05,
      description: '5G cellular network',
    },
    {
      name: '4G LTE',
      downloadSpeed: 20000, // 20 Mbps
      uploadSpeed: 5000, // 5 Mbps
      latency: 50,
      packetLoss: 0.5,
      description: 'Standard 4G LTE connection',
    },
    {
      name: '3G',
      downloadSpeed: 3000, // 3 Mbps
      uploadSpeed: 1000, // 1 Mbps
      latency: 200,
      packetLoss: 2,
      description: 'Slower 3G connection',
    },
    {
      name: '2G Edge',
      downloadSpeed: 236, // 236 Kbps
      uploadSpeed: 118, // 118 Kbps
      latency: 840,
      packetLoss: 5,
      description: 'Very slow 2G connection',
    },
    {
      name: 'Slow WiFi',
      downloadSpeed: 1000, // 1 Mbps
      uploadSpeed: 500, // 500 Kbps
      latency: 300,
      packetLoss: 3,
      description: 'Congested or distant WiFi',
    },
    {
      name: 'Intermittent',
      downloadSpeed: 5000, // 5 Mbps
      uploadSpeed: 2000, // 2 Mbps
      latency: 500,
      packetLoss: 15,
      description: 'Unstable connection with frequent drops',
    },
    {
      name: 'Offline',
      downloadSpeed: 0,
      uploadSpeed: 0,
      latency: 0,
      packetLoss: 100,
      description: 'No network connection',
    },
  ];

  static getInstance(): NetworkSimulator {
    if (!NetworkSimulator.instance) {
      NetworkSimulator.instance = new NetworkSimulator();
    }
    return NetworkSimulator.instance;
  }

  constructor() {
    this.currentProfile = this.profiles[0]; // Default to WiFi
  }

  /**
   * Enable network simulation with a specific profile
   */
  enable(profileName: string): boolean {
    const profile = this.profiles.find(p => p.name === profileName);
    if (!profile) {
      console.error(`Network profile '${profileName}' not found`);
      return false;
    }

    this.currentProfile = profile;
    this.isEnabled = true;
    console.log(`🌐 Network simulation enabled: ${profile.name} - ${profile.description}`);
    return true;
  }

  /**
   * Disable network simulation
   */
  disable(): void {
    this.isEnabled = false;
    console.log('🌐 Network simulation disabled');
  }

  /**
   * Simulate network request with current profile
   */
  async simulateRequest(
    originalFetch: typeof fetch,
    url: string,
    options?: RequestInit
  ): Promise<Response> {
    const request: NetworkRequest = {
      url,
      method: options?.method || 'GET',
      timestamp: Date.now(),
      status: 'pending',
      profile: this.currentProfile.name,
    };

    this.requests.push(request);

    // If simulation is disabled, use normal fetch
    if (!this.isEnabled) {
      const startTime = performance.now();
      try {
        const response = await originalFetch(url, options);
        request.actualTime = performance.now() - startTime;
        request.status = response.ok ? 'success' : 'failed';
        return response;
      } catch (error) {
        request.actualTime = performance.now() - startTime;
        request.status = 'failed';
        throw error;
      }
    }

    const startTime = performance.now();

    // Simulate packet loss
    if (Math.random() * 100 < this.currentProfile.packetLoss) {
      request.status = 'failed';
      request.simulatedTime = this.currentProfile.latency;
      
      await this.delay(this.currentProfile.latency);
      throw new Error(`Network Error: Simulated packet loss (${this.currentProfile.name})`);
    }

    // Calculate simulated delay based on data size and bandwidth
    const estimatedSize = this.estimateRequestSize(url, options);
    const transferTime = this.calculateTransferTime(estimatedSize);
    const totalDelay = this.currentProfile.latency + transferTime;

    // Apply simulated delay
    await this.delay(totalDelay);

    try {
      // Add timeout simulation for very slow connections
      const timeoutDuration = this.getTimeoutDuration();
      const fetchPromise = originalFetch(url, options);
      const timeoutPromise = this.delay(timeoutDuration).then(() => {
        throw new Error(`Network Error: Timeout after ${timeoutDuration}ms (${this.currentProfile.name})`);
      });

      const response = await Promise.race([fetchPromise, timeoutPromise]);
      
      request.actualTime = performance.now() - startTime;
      request.simulatedTime = totalDelay;
      request.status = 'success';

      // Log slow requests
      if (totalDelay > 3000) {
        console.warn(`🐌 Slow network request: ${url} took ${totalDelay}ms on ${this.currentProfile.name}`);
      }

      return response as Response;
    } catch (error) {
      request.actualTime = performance.now() - startTime;
      request.simulatedTime = totalDelay;
      request.status = error.message.includes('Timeout') ? 'timeout' : 'failed';
      throw error;
    }
  }

  /**
   * Get timeout duration based on current profile
   */
  private getTimeoutDuration(): number {
    switch (this.currentProfile.name) {
      case 'WiFi':
      case '5G':
        return 10000; // 10 seconds
      case '4G LTE':
        return 15000; // 15 seconds
      case '3G':
        return 30000; // 30 seconds
      case '2G Edge':
      case 'Slow WiFi':
        return 60000; // 60 seconds
      case 'Intermittent':
        return 20000; // 20 seconds
      default:
        return 30000; // Default 30 seconds
    }
  }

  /**
   * Estimate request size in bytes
   */
  private estimateRequestSize(url: string, options?: RequestInit): number {
    let size = 500; // Base request overhead
    
    // Add body size if present
    if (options?.body) {
      if (typeof options.body === 'string') {
        size += new Blob([options.body]).size;
      } else if (options.body instanceof FormData) {
        size += 2000; // Estimate for FormData
      }
    }

    // Estimate response size based on endpoint
    if (url.includes('/api/radio/streams')) {
      size += 5000; // Stream list response
    } else if (url.includes('/api/station-info')) {
      size += 2000; // Station info response
    } else if (url.includes('/api/voice/')) {
      size += 1000; // Voice command response
    } else {
      size += 1500; // Default API response
    }

    return size;
  }

  /**
   * Calculate transfer time based on size and current profile
   */
  private calculateTransferTime(sizeBytes: number): number {
    if (this.currentProfile.downloadSpeed === 0) {
      return 0; // Offline
    }

    const sizeBits = sizeBytes * 8;
    const speedBitsPerSecond = this.currentProfile.downloadSpeed * 1000;
    return (sizeBits / speedBitsPerSecond) * 1000; // Convert to milliseconds
  }

  /**
   * Simple delay function
   */
  private delay(ms: number): Promise<void> {
    return new Promise(resolve => setTimeout(resolve, ms));
  }

  /**
   * Get available network profiles
   */
  getProfiles(): NetworkProfile[] {
    return [...this.profiles];
  }

  /**
   * Get current profile
   */
  getCurrentProfile(): NetworkProfile {
    return this.currentProfile;
  }

  /**
   * Get network statistics
   */
  getStatistics(): {
    totalRequests: number;
    successRate: number;
    averageLatency: number;
    timeoutRate: number;
    profileBreakdown: Record<string, number>;
  } {
    const total = this.requests.length;
    const successful = this.requests.filter(r => r.status === 'success').length;
    const timeouts = this.requests.filter(r => r.status === 'timeout').length;
    
    const latencies = this.requests
      .filter(r => r.simulatedTime !== undefined)
      .map(r => r.simulatedTime!);
    
    const averageLatency = latencies.length > 0
      ? latencies.reduce((sum, lat) => sum + lat, 0) / latencies.length
      : 0;

    const profileBreakdown = this.requests.reduce((acc, req) => {
      acc[req.profile] = (acc[req.profile] || 0) + 1;
      return acc;
    }, {} as Record<string, number>);

    return {
      totalRequests: total,
      successRate: total > 0 ? (successful / total) * 100 : 0,
      averageLatency,
      timeoutRate: total > 0 ? (timeouts / total) * 100 : 0,
      profileBreakdown,
    };
  }

  /**
   * Test app behavior under specific network conditions
   */
  async testNetworkConditions(
    testFunction: () => Promise<any>,
    profileNames: string[] = ['WiFi', '4G LTE', '3G', 'Slow WiFi']
  ): Promise<Record<string, any>> {
    const results: Record<string, any> = {};

    for (const profileName of profileNames) {
      console.log(`🧪 Testing with ${profileName} network conditions...`);
      
      this.enable(profileName);
      
      try {
        const startTime = performance.now();
        const result = await testFunction();
        const duration = performance.now() - startTime;
        
        results[profileName] = {
          success: true,
          duration,
          result,
        };
        
        console.log(`✅ ${profileName}: Completed in ${duration.toFixed(0)}ms`);
      } catch (error) {
        results[profileName] = {
          success: false,
          error: error.message,
        };
        
        console.log(`❌ ${profileName}: Failed - ${error.message}`);
      }
    }

    this.disable();
    return results;
  }

  /**
   * Clear request history
   */
  clearHistory(): void {
    this.requests = [];
  }

  /**
   * Export network performance report
   */
  exportReport(): string {
    const stats = this.getStatistics();
    
    return JSON.stringify({
      timestamp: new Date().toISOString(),
      currentProfile: this.currentProfile,
      isEnabled: this.isEnabled,
      statistics: stats,
      recentRequests: this.requests.slice(-50), // Last 50 requests
      recommendations: this.generateRecommendations(stats),
    }, null, 2);
  }

  /**
   * Generate performance recommendations based on statistics
   */
  private generateRecommendations(stats: any): string[] {
    const recommendations: string[] = [];

    if (stats.successRate < 90) {
      recommendations.push('Consider implementing retry logic for failed requests');
    }

    if (stats.averageLatency > 5000) {
      recommendations.push('Implement request caching to reduce network dependency');
    }

    if (stats.timeoutRate > 5) {
      recommendations.push('Consider increasing timeout values or implementing progressive loading');
    }

    if (stats.totalRequests > 100) {
      recommendations.push('Consider implementing request debouncing to reduce network load');
    }

    return recommendations;
  }
}

// Export singleton instance
export const networkSimulator = NetworkSimulator.getInstance();

// Fetch interceptor for automatic network simulation
export const createNetworkInterceptor = (originalFetch: typeof fetch) => {
  return async (url: string | Request, options?: RequestInit): Promise<Response> => {
    const urlString = typeof url === 'string' ? url : url.url;
    
    return networkSimulator.simulateRequest(originalFetch, urlString, options);
  };
};

import React from 'react';

// React hook for network simulation  
export function useNetworkSimulation() {
  const [currentProfile, setCurrentProfile] = React.useState(networkSimulator.getCurrentProfile());
  const [isEnabled, setIsEnabled] = React.useState(false);
  const [statistics, setStatistics] = React.useState(networkSimulator.getStatistics());

  const enableProfile = (profileName: string) => {
    const success = networkSimulator.enable(profileName);
    if (success) {
      setCurrentProfile(networkSimulator.getCurrentProfile());
      setIsEnabled(true);
    }
    return success;
  };

  const disable = () => {
    networkSimulator.disable();
    setIsEnabled(false);
  };

  const refreshStats = () => {
    setStatistics(networkSimulator.getStatistics());
  };

  return {
    currentProfile,
    isEnabled,
    statistics,
    profiles: networkSimulator.getProfiles(),
    enableProfile,
    disable,
    refreshStats,
    exportReport: () => networkSimulator.exportReport(),
    clearHistory: () => networkSimulator.clearHistory(),
  };
}