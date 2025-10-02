import { Platform } from 'react-native';
import NetInfo from '@react-native-community/netinfo';
import AsyncStorage from '@react-native-async-storage/async-storage';
import { systemRefreshService } from './SystemRefreshService';
import { autoUpdateManager } from './AutoUpdateManager';

export interface RealTimeData {
  currentTime: Date;
  timezone: string;
  internetStatus: 'online' | 'offline' | 'connecting';
  connectionType: string;
  lastSync: Date | null;
  externalSourcesStatus: 'checking' | 'updated' | 'unchanged' | 'error';
  changedSources: string[];
}

export interface ExternalSource {
  id: string;
  name: string;
  url: string;
  type: 'radio_stream' | 'api_endpoint' | 'cdn_resource' | 'news_feed';
  lastChecked: Date;
  lastModified: Date | null;
  checksum: string | null;
  isActive: boolean;
  retryCount: number;
}

export class RealTimeService {
  private static instance: RealTimeService;
  private timeUpdateInterval: NodeJS.Timeout | null = null;
  private sourceCheckInterval: NodeJS.Timeout | null = null;
  private networkListener: (() => void) | null = null;
  private callbacks: ((data: RealTimeData) => void)[] = [];
  
  private currentData: RealTimeData = {
    currentTime: new Date(),
    timezone: Intl.DateTimeFormat().resolvedOptions().timeZone,
    internetStatus: 'connecting',
    connectionType: 'unknown',
    lastSync: null,
    externalSourcesStatus: 'checking',
    changedSources: []
  };

  private externalSources: ExternalSource[] = [];
  private wasOffline = false;

  static getInstance(): RealTimeService {
    if (!RealTimeService.instance) {
      RealTimeService.instance = new RealTimeService();
    }
    return RealTimeService.instance;
  }

  async initialize(): Promise<void> {
    console.log('⏰ Initializing Real-Time Service...');
    
    try {
      // Load saved external sources
      await this.loadExternalSources();
      
      // Start real-time clock
      this.startTimeUpdates();
      
      // Start network monitoring
      await this.startNetworkMonitoring();
      
      // Start external source monitoring
      this.startExternalSourceMonitoring();
      
      console.log('✅ Real-Time Service initialized');
      this.notifyCallbacks();
      
    } catch (error) {
      console.error('❌ Real-Time Service initialization failed:', error);
    }
  }

  // Subscribe to real-time updates
  subscribe(callback: (data: RealTimeData) => void): () => void {
    this.callbacks.push(callback);
    // Immediately call with current data
    callback({ ...this.currentData });
    
    return () => {
      const index = this.callbacks.indexOf(callback);
      if (index > -1) {
        this.callbacks.splice(index, 1);
      }
    };
  }

  private notifyCallbacks() {
    this.callbacks.forEach(callback => callback({ ...this.currentData }));
  }

  private startTimeUpdates() {
    // Update time every second
    this.timeUpdateInterval = setInterval(() => {
      this.currentData.currentTime = new Date();
      this.currentData.timezone = Intl.DateTimeFormat().resolvedOptions().timeZone;
      this.notifyCallbacks();
    }, 1000);
    
    console.log('⏰ Real-time clock started');
  }

  private async startNetworkMonitoring() {
    try {
      if (Platform.OS !== 'web') {
        // Use NetInfo for native platforms
        const unsubscribe = NetInfo.addEventListener(state => {
          this.handleConnectivityChange(
            state.isConnected || false,
            state.type || 'unknown'
          );
        });
        this.networkListener = unsubscribe;
        
        // Get initial state
        const state = await NetInfo.fetch();
        this.handleConnectivityChange(
          state.isConnected || false,
          state.type || 'unknown'
        );
      } else {
        // Web platform monitoring
        this.startWebNetworkMonitoring();
      }
      
      console.log('🌐 Network monitoring started');
    } catch (error) {
      console.log('⚠️ Network monitoring setup partial:', error.message);
      // Fallback to basic connectivity
      this.currentData.internetStatus = 'online';
      this.currentData.connectionType = 'unknown';
    }
  }

  private startWebNetworkMonitoring() {
    if (typeof window === 'undefined') return;
    
    // Initial status
    this.currentData.internetStatus = navigator.onLine ? 'online' : 'offline';
    this.currentData.connectionType = 'web';
    
    // Listen for online/offline events
    const handleOnline = () => {
      console.log('🌐 Web: Connection restored');
      this.handleConnectivityChange(true, 'web');
    };
    
    const handleOffline = () => {
      console.log('🌐 Web: Connection lost');
      this.handleConnectivityChange(false, 'web');
    };
    
    window.addEventListener('online', handleOnline);
    window.addEventListener('offline', handleOffline);
    
    // Cleanup function
    this.networkListener = () => {
      window.removeEventListener('online', handleOnline);
      window.removeEventListener('offline', handleOffline);
    };
  }

  private async handleConnectivityChange(isConnected: boolean, connectionType: string) {
    const wasOnline = this.currentData.internetStatus === 'online';
    
    this.currentData.internetStatus = isConnected ? 'online' : 'offline';
    this.currentData.connectionType = connectionType;
    
    console.log(`🌐 Connectivity changed: ${this.currentData.internetStatus} (${connectionType})`);
    
    // If we just came back online
    if (isConnected && !wasOnline) {
      console.log('🔄 Internet restored - triggering auto-updates...');
      await this.handleInternetRestored();
    }
    
    // If we just went offline
    if (!isConnected && wasOnline) {
      console.log('📱 Gone offline - enabling offline mode...');
      this.wasOffline = true;
    }
    
    this.notifyCallbacks();
  }

  private async handleInternetRestored() {
    try {
      console.log('🔄 Handling internet restoration...');
      
      // Update last sync time
      this.currentData.lastSync = new Date();
      
      // Check for app updates
      const hasUpdates = await autoUpdateManager.forceCheck();
      if (hasUpdates) {
        console.log('📥 App updates available - applying...');
        await autoUpdateManager.forceUpdate();
      }
      
      // Check external sources for changes
      await this.checkExternalSources();
      
      // Perform system refresh if we were offline for a while
      if (this.wasOffline) {
        console.log('🔄 Performing post-offline system refresh...');
        await systemRefreshService.performQuickRefresh();
        this.wasOffline = false;
      }
      
      console.log('✅ Internet restoration handling complete');
      
    } catch (error) {
      console.error('❌ Error handling internet restoration:', error);
    }
  }

  private async loadExternalSources() {
    try {
      // Load default external sources for Kagema FM
      this.externalSources = [
        {
          id: 'soma_fm_streams',
          name: 'SomaFM Stream List',
          url: 'https://somafm.com/channels.json',
          type: 'api_endpoint',
          lastChecked: new Date(),
          lastModified: null,
          checksum: null,
          isActive: true,
          retryCount: 0
        },
        {
          id: 'bbc_world_service',
          name: 'BBC World Service Stream',
          url: 'https://stream.live.vc.bbcmedia.co.uk/bbc_world_service',
          type: 'radio_stream',
          lastChecked: new Date(),
          lastModified: null,
          checksum: null,
          isActive: true,
          retryCount: 0
        },
        {
          id: 'radio_garden_api',
          name: 'Radio Garden API',
          url: 'https://radio.garden/api',
          type: 'api_endpoint',
          lastChecked: new Date(),
          lastModified: null,
          checksum: null,
          isActive: true,
          retryCount: 0
        },
        {
          id: 'kenya_news_feed',
          name: 'Kenya News Feed',
          url: 'https://feeds.standardmedia.co.ke/rss',
          type: 'news_feed',
          lastChecked: new Date(),
          lastModified: null,
          checksum: null,
          isActive: true,
          retryCount: 0
        }
      ];

      // Try to load saved sources
      const saved = await AsyncStorage.getItem('external_sources');
      if (saved) {
        const savedSources = JSON.parse(saved);
        // Merge with defaults, keeping saved data for known sources
        this.externalSources = this.externalSources.map(defaultSource => {
          const savedSource = savedSources.find((s: ExternalSource) => s.id === defaultSource.id);
          return savedSource || defaultSource;
        });
      }
      
      console.log(`📡 Loaded ${this.externalSources.length} external sources`);
      
    } catch (error) {
      console.log('⚠️ Error loading external sources:', error.message);
    }
  }

  private async saveExternalSources() {
    try {
      await AsyncStorage.setItem('external_sources', JSON.stringify(this.externalSources));
    } catch (error) {
      console.log('⚠️ Error saving external sources:', error.message);
    }
  }

  private startExternalSourceMonitoring() {
    // Check external sources every 5 minutes
    this.sourceCheckInterval = setInterval(async () => {
      if (this.currentData.internetStatus === 'online') {
        await this.checkExternalSources();
      }
    }, 5 * 60 * 1000);
    
    console.log('📡 External source monitoring started (5-minute intervals)');
  }

  private async checkExternalSources(): Promise<boolean> {
    if (this.currentData.internetStatus !== 'online') {
      return false;
    }
    
    console.log('🔍 Checking external sources for changes...');
    this.currentData.externalSourcesStatus = 'checking';
    this.currentData.changedSources = [];
    this.notifyCallbacks();
    
    let hasChanges = false;
    
    for (const source of this.externalSources.filter(s => s.isActive)) {
      try {
        const changed = await this.checkSingleSource(source);
        if (changed) {
          hasChanges = true;
          this.currentData.changedSources.push(source.name);
        }
        source.retryCount = 0; // Reset on success
      } catch (error) {
        console.log(`⚠️ Error checking ${source.name}:`, error.message);
        source.retryCount++;
        
        // Disable source after 3 consecutive failures
        if (source.retryCount >= 3) {
          source.isActive = false;
          console.log(`❌ Disabled ${source.name} after 3 failures`);
        }
      }
    }
    
    this.currentData.externalSourcesStatus = hasChanges ? 'updated' : 'unchanged';
    await this.saveExternalSources();
    this.notifyCallbacks();
    
    if (hasChanges) {
      console.log(`📡 External sources changed: ${this.currentData.changedSources.join(', ')}`);
      // Trigger system refresh to reload with new sources
      await systemRefreshService.performQuickRefresh();
    }
    
    return hasChanges;
  }

  private async checkSingleSource(source: ExternalSource): Promise<boolean> {
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), 10000); // 10 second timeout
    
    try {
      const response = await fetch(source.url, {
        method: 'HEAD', // Use HEAD request to check headers without downloading content
        signal: controller.signal,
        cache: 'no-cache'
      });
      
      clearTimeout(timeoutId);
      
      const lastModified = response.headers.get('last-modified');
      const etag = response.headers.get('etag');
      const newChecksum = lastModified || etag || response.headers.get('content-length') || null;
      
      source.lastChecked = new Date();
      
      const hasChanged = source.checksum !== null && source.checksum !== newChecksum;
      
      if (hasChanged) {
        console.log(`🔄 ${source.name} has changed`);
        source.lastModified = new Date();
      }
      
      source.checksum = newChecksum;
      
      return hasChanged;
      
    } catch (error) {
      clearTimeout(timeoutId);
      if (error.name === 'AbortError') {
        throw new Error('Request timeout');
      }
      throw error;
    }
  }

  // Public methods
  getCurrentData(): RealTimeData {
    return { ...this.currentData };
  }

  async forceCheckSources(): Promise<boolean> {
    return await this.checkExternalSources();
  }

  addExternalSource(source: Omit<ExternalSource, 'id' | 'lastChecked' | 'retryCount'>): void {
    const newSource: ExternalSource = {
      ...source,
      id: `custom_${Date.now()}`,
      lastChecked: new Date(),
      retryCount: 0
    };
    
    this.externalSources.push(newSource);
    this.saveExternalSources();
    
    console.log(`📡 Added external source: ${newSource.name}`);
  }

  removeExternalSource(sourceId: string): void {
    const index = this.externalSources.findIndex(s => s.id === sourceId);
    if (index > -1) {
      const removed = this.externalSources.splice(index, 1)[0];
      this.saveExternalSources();
      console.log(`📡 Removed external source: ${removed.name}`);
    }
  }

  getExternalSources(): ExternalSource[] {
    return [...this.externalSources];
  }

  // Force an internet restoration check (for testing)
  async triggerInternetRestorationCheck(): Promise<void> {
    console.log('🔄 Manually triggering internet restoration check...');
    await this.handleInternetRestored();
  }

  // Get formatted time string
  getFormattedTime(format: '12h' | '24h' = '12h'): string {
    const time = this.currentData.currentTime;
    
    if (format === '24h') {
      return time.toLocaleTimeString('en-US', { 
        hour12: false, 
        hour: '2-digit', 
        minute: '2-digit',
        second: '2-digit'
      });
    } else {
      return time.toLocaleTimeString('en-US', { 
        hour12: true, 
        hour: 'numeric', 
        minute: '2-digit',
        second: '2-digit'
      });
    }
  }

  // Get formatted date string
  getFormattedDate(): string {
    return this.currentData.currentTime.toLocaleDateString('en-US', {
      weekday: 'long',
      year: 'numeric',
      month: 'long',
      day: 'numeric'
    });
  }

  dispose(): void {
    if (this.timeUpdateInterval) {
      clearInterval(this.timeUpdateInterval);
    }
    
    if (this.sourceCheckInterval) {
      clearInterval(this.sourceCheckInterval);
    }
    
    if (this.networkListener) {
      this.networkListener();
    }
    
    this.callbacks = [];
    console.log('🔄 Real-Time Service disposed');
  }
}

// Export singleton instance and React hook
export const realTimeService = RealTimeService.getInstance();

// React hook for easy integration
export function useRealTime() {
  const [data, setData] = React.useState<RealTimeData>(realTimeService.getCurrentData());
  
  React.useEffect(() => {
    const unsubscribe = realTimeService.subscribe(setData);
    return unsubscribe;
  }, []);
  
  return {
    ...data,
    forceCheckSources: realTimeService.forceCheckSources.bind(realTimeService),
    triggerInternetRestorationCheck: realTimeService.triggerInternetRestorationCheck.bind(realTimeService),
    getFormattedTime: realTimeService.getFormattedTime.bind(realTimeService),
    getFormattedDate: realTimeService.getFormattedDate.bind(realTimeService)
  };
}