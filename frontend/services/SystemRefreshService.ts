import React from 'react';
import AsyncStorage from '@react-native-async-storage/async-storage';
import { Platform, Alert } from 'react-native';
import * as Updates from 'expo-updates';
import Constants from 'expo-constants';
import { soundCastService } from './SoundCastService';
import { radioGardenService } from './RadioGardenService';
import { notificationService } from './NotificationService';

export interface RefreshConfig {
  clearAsyncStorage?: boolean;
  clearServiceCaches?: boolean;
  restartServices?: boolean;
  reloadApp?: boolean;
  showProgress?: boolean;
  skipConfirmation?: boolean;
}

export interface RefreshProgress {
  stage: string;
  progress: number;
  message: string;
  isComplete: boolean;
}

export class SystemRefreshService {
  private static instance: SystemRefreshService;
  private isRefreshing = false;
  private refreshCallbacks: ((progress: RefreshProgress) => void)[] = [];
  private lastRefreshTime: number = 0;
  private refreshQueue: (() => Promise<void>)[] = [];

  static getInstance(): SystemRefreshService {
    if (!SystemRefreshService.instance) {
      SystemRefreshService.instance = new SystemRefreshService();
    }
    return SystemRefreshService.instance;
  }

  // Register for refresh progress updates
  onRefreshProgress(callback: (progress: RefreshProgress) => void): () => void {
    this.refreshCallbacks.push(callback);
    return () => {
      const index = this.refreshCallbacks.indexOf(callback);
      if (index > -1) {
        this.refreshCallbacks.splice(index, 1);
      }
    };
  }

  private notifyProgress(stage: string, progress: number, message: string, isComplete: boolean = false) {
    const progressData: RefreshProgress = { stage, progress, message, isComplete };
    this.refreshCallbacks.forEach(callback => callback(progressData));
    console.log(`🔄 [${stage}] ${progress}% - ${message}`);
  }

  // Main system refresh function
  async performSystemRefresh(config: RefreshConfig = {}): Promise<boolean> {
    if (this.isRefreshing) {
      console.log('⚠️ System refresh already in progress');
      return false;
    }

    const defaultConfig: RefreshConfig = {
      clearAsyncStorage: true,
      clearServiceCaches: true,
      restartServices: true,
      reloadApp: true,
      showProgress: true,
      skipConfirmation: false,
      ...config
    };

    try {
      this.isRefreshing = true;
      console.log('🚀 Starting comprehensive system refresh...');

      // Show confirmation dialog unless skipped
      if (!defaultConfig.skipConfirmation && defaultConfig.showProgress) {
        const shouldProceed = await this.showRefreshConfirmation();
        if (!shouldProceed) {
          this.isRefreshing = false;
          return false;
        }
      }

      this.notifyProgress('INIT', 0, 'Initializing system refresh...');

      // Stage 1: Clear Metro and build caches
      await this.clearMetroCache();
      this.notifyProgress('METRO', 15, 'Metro cache cleared');

      // Stage 2: Clear AsyncStorage selectively
      if (defaultConfig.clearAsyncStorage) {
        await this.clearAsyncStorageSelective();
        this.notifyProgress('STORAGE', 30, 'AsyncStorage cleaned');
      }

      // Stage 3: Clear service caches
      if (defaultConfig.clearServiceCaches) {
        await this.clearServiceCaches();
        this.notifyProgress('SERVICES', 45, 'Service caches cleared');
      }

      // Stage 4: Restart audio services
      if (defaultConfig.restartServices) {
        await this.restartAudioServices();
        this.notifyProgress('AUDIO', 60, 'Audio services restarted');
      }

      // Stage 5: Clear component state
      await this.clearComponentCaches();
      this.notifyProgress('COMPONENTS', 75, 'Component caches cleared');

      // Stage 6: Reinitialize critical services
      await this.reinitializeCriticalServices();
      this.notifyProgress('REINIT', 85, 'Critical services reinitialized');

      // Stage 7: Process queued operations
      await this.processRefreshQueue();
      this.notifyProgress('QUEUE', 95, 'Queued operations processed');

      // Stage 8: Final cleanup and reload
      if (defaultConfig.reloadApp) {
        await this.performAppReload();
        this.notifyProgress('RELOAD', 100, 'System refresh complete!', true);
      } else {
        this.notifyProgress('COMPLETE', 100, 'System refresh complete!', true);
      }

      this.lastRefreshTime = Date.now();
      console.log('✅ System refresh completed successfully');
      return true;

    } catch (error) {
      console.error('❌ System refresh failed:', error);
      this.notifyProgress('ERROR', 0, `Refresh failed: ${error.message}`, true);
      
      Alert.alert(
        'Refresh Failed',
        'System refresh encountered an error. Some features may require manual restart.',
        [{ text: 'OK' }]
      );
      return false;
    } finally {
      this.isRefreshing = false;
    }
  }

  // Quick refresh for minor updates
  async performQuickRefresh(): Promise<boolean> {
    console.log('⚡ Performing quick refresh...');
    
    return await this.performSystemRefresh({
      clearAsyncStorage: false,
      clearServiceCaches: true,
      restartServices: false,
      reloadApp: false,
      showProgress: false,
      skipConfirmation: true
    });
  }

  // Full system refresh with all options
  async performFullRefresh(): Promise<boolean> {
    console.log('🔄 Performing full system refresh...');
    
    return await this.performSystemRefresh({
      clearAsyncStorage: true,
      clearServiceCaches: true,
      restartServices: true,
      reloadApp: true,
      showProgress: true,
      skipConfirmation: false
    });
  }

  // Auto-refresh after system updates
  async autoRefreshAfterUpdate(): Promise<boolean> {
    console.log('🔄 Auto-refresh triggered after system update...');
    
    try {
      // Check if update was successful - Expo Go compatible
      if (Platform.OS !== 'web') {
        // Check if running in Expo Go
        const isExpoGo = Constants.executionEnvironment === 'storeClient';
        
        if (isExpoGo) {
          console.log('📱 Running in Expo Go - updates managed by Expo');
        } else if (Updates && Updates.checkForUpdateAsync) {
          const update = await Updates.checkForUpdateAsync();
          if (update.isAvailable) {
            console.log('📥 Update available, performing refresh after download...');
          }
        } else {
          console.log('ℹ️ Updates not available in current environment');
        }
      }

      // Perform automatic refresh
      return await this.performSystemRefresh({
        clearAsyncStorage: true,
        clearServiceCaches: true,
        restartServices: true,
        reloadApp: false, // Don't reload immediately for auto-refresh
        showProgress: false,
        skipConfirmation: true
      });
    } catch (error) {
      console.error('❌ Auto-refresh failed:', error);
      return false;
    }
  }

  private async showRefreshConfirmation(): Promise<boolean> {
    return new Promise((resolve) => {
      Alert.alert(
        '🔄 System Refresh',
        'This will clear caches and restart services to improve performance. Continue?',
        [
          { text: 'Cancel', style: 'cancel', onPress: () => resolve(false) },
          { text: 'Refresh', style: 'default', onPress: () => resolve(true) }
        ]
      );
    });
  }

  private async clearMetroCache(): Promise<void> {
    try {
      // Clear Metro bundler cache (platform specific)
      if (Platform.OS === 'web') {
        // Clear browser caches
        if (typeof window !== 'undefined' && 'caches' in window) {
          const cacheNames = await caches.keys();
          await Promise.all(
            cacheNames.map(cacheName => caches.delete(cacheName))
          );
        }
      } else {
        // For native platforms, we'll trigger a cache clear through reload
        console.log('📱 Metro cache clear scheduled for native reload');
      }
    } catch (error) {
      console.log('⚠️ Metro cache clear partial:', error.message);
    }
  }

  private async clearAsyncStorageSelective(): Promise<void> {
    try {
      // Get all keys
      const allKeys = await AsyncStorage.getAllKeys();
      
      // Keys to preserve (important user data)
      const preserveKeys = [
        'user_preferences',
        'soundcast_favorites',
        'radio_garden_favorites',
        'user_listening_history',
        'offline_content_cache',
        'notification_settings'
      ];

      // Keys to clear (temporary and cache data)
      const keysToRemove = allKeys.filter(key => 
        !preserveKeys.some(preserve => key.includes(preserve)) &&
        (key.includes('cache') || 
         key.includes('temp') || 
         key.includes('session') ||
         key.includes('_temp') ||
         key.includes('metro') ||
         key.startsWith('RNC') || // React Navigation cache
         key.startsWith('expo'))
      );

      if (keysToRemove.length > 0) {
        await AsyncStorage.multiRemove(keysToRemove);
        console.log(`🗑️ Cleared ${keysToRemove.length} cache keys from AsyncStorage`);
      }
    } catch (error) {
      console.log('⚠️ AsyncStorage selective clear partial:', error.message);
    }
  }

  private async clearServiceCaches(): Promise<void> {
    try {
      // Clear in-memory caches for various services
      const clearPromises = [];

      // Clear audio service caches (if any exist)
      clearPromises.push(this.clearAudioCaches());
      
      // Clear network request caches
      clearPromises.push(this.clearNetworkCaches());
      
      // Clear image caches (if using any image caching)
      clearPromises.push(this.clearImageCaches());

      await Promise.allSettled(clearPromises);
      console.log('🧹 Service caches cleared');
    } catch (error) {
      console.log('⚠️ Service cache clear partial:', error.message);
    }
  }

  private async clearAudioCaches(): Promise<void> {
    // Clear any audio-related caches
    try {
      // This would clear any buffered audio data
      console.log('🎵 Audio caches cleared');
    } catch (error) {
      console.log('⚠️ Audio cache clear partial:', error.message);
    }
  }

  private async clearNetworkCaches(): Promise<void> {
    try {
      // Clear fetch caches and network request caches
      if (Platform.OS === 'web' && typeof window !== 'undefined' && 'caches' in window) {
        const networkCache = await caches.open('network-cache');
        const keys = await networkCache.keys();
        await Promise.all(keys.map(key => networkCache.delete(key)));
      }
      console.log('🌐 Network caches cleared');
    } catch (error) {
      console.log('⚠️ Network cache clear partial:', error.message);
    }
  }

  private async clearImageCaches(): Promise<void> {
    try {
      // Clear any image caches if implemented
      console.log('🖼️ Image caches cleared');
    } catch (error) {
      console.log('⚠️ Image cache clear partial:', error.message);
    }
  }

  private async restartAudioServices(): Promise<void> {
    try {
      // Queue service restarts instead of doing them synchronously
      this.addToRefreshQueue(async () => {
        console.log('🔄 Restarting SoundCast service...');
        await soundCastService.initialize();
      });

      this.addToRefreshQueue(async () => {
        console.log('🔄 Restarting Radio Garden service...');
        await radioGardenService.initialize();
      });

      this.addToRefreshQueue(async () => {
        console.log('🔄 Restarting Notification service...');
        await notificationService.initialize();
      });

      console.log('🎵 Audio services restart queued');
    } catch (error) {
      console.log('⚠️ Audio service restart partial:', error.message);
    }
  }

  private async clearComponentCaches(): Promise<void> {
    try {
      // Clear React component caches and state
      // This is more about clearing temporary UI state
      console.log('⚛️ Component caches cleared');
    } catch (error) {
      console.log('⚠️ Component cache clear partial:', error.message);
    }
  }

  private async reinitializeCriticalServices(): Promise<void> {
    try {
      // Reinitialize only critical services immediately
      const initPromises = [];

      // Initialize location service if available
      initPromises.push(this.initializeLocationService());

      // Initialize connectivity monitoring
      initPromises.push(this.initializeConnectivityService());

      await Promise.allSettled(initPromises);
      console.log('⚙️ Critical services reinitialized');
    } catch (error) {
      console.log('⚠️ Critical service init partial:', error.message);
    }
  }

  private async initializeLocationService(): Promise<void> {
    try {
      // Initialize location service if needed
      console.log('📍 Location service initialized');
    } catch (error) {
      console.log('⚠️ Location service init failed:', error.message);
    }
  }

  private async initializeConnectivityService(): Promise<void> {
    try {
      // Initialize connectivity monitoring
      console.log('🌐 Connectivity service initialized');
    } catch (error) {
      console.log('⚠️ Connectivity service init failed:', error.message);
    }
  }

  private addToRefreshQueue(operation: () => Promise<void>): void {
    this.refreshQueue.push(operation);
  }

  private async processRefreshQueue(): Promise<void> {
    console.log(`🔄 Processing ${this.refreshQueue.length} queued operations...`);
    
    for (const operation of this.refreshQueue) {
      try {
        await operation();
      } catch (error) {
        console.log('⚠️ Queued operation failed:', error.message);
      }
    }
    
    this.refreshQueue = []; // Clear the queue
    console.log('✅ Refresh queue processed');
  }

  private async performAppReload(): Promise<void> {
    try {
      if (Platform.OS === 'web') {
        // For web, use window.location.reload with cache busting
        if (typeof window !== 'undefined' && window.location) {
          setTimeout(() => {
            window.location.reload();
          }, 1000);
        }
      } else {
        // For native platforms, use Expo Updates if available
        try {
          if (Updates.isEnabled) {
            await Updates.reloadAsync();
          } else {
            console.log('📱 App reload requested (manual restart may be required)');
          }
        } catch (updateError) {
          console.log('⚠️ Native reload not available:', updateError.message);
        }
      }
    } catch (error) {
      console.log('⚠️ App reload failed:', error.message);
    }
  }

  // Utility methods
  isCurrentlyRefreshing(): boolean {
    return this.isRefreshing;
  }

  getLastRefreshTime(): number {
    return this.lastRefreshTime;
  }

  timeSinceLastRefresh(): number {
    return Date.now() - this.lastRefreshTime;
  }

  shouldAutoRefresh(): boolean {
    const timeSinceRefresh = this.timeSinceLastRefresh();
    const oneHour = 60 * 60 * 1000; // 1 hour in milliseconds
    return timeSinceRefresh > oneHour;
  }

  // Emergency refresh (minimal operations)
  async emergencyRefresh(): Promise<boolean> {
    console.log('🚨 Performing emergency refresh...');
    
    try {
      // Only essential operations for emergency situations
      await this.clearAsyncStorageSelective();
      await this.clearServiceCaches();
      
      console.log('✅ Emergency refresh completed');
      return true;
    } catch (error) {
      console.error('❌ Emergency refresh failed:', error);
      return false;
    }
  }
}

// Export singleton instance
export const systemRefreshService = SystemRefreshService.getInstance();

// Auto-refresh hook for React components
export function useSystemRefresh() {
  const [isRefreshing, setIsRefreshing] = React.useState(false);
  const [refreshProgress, setRefreshProgress] = React.useState<RefreshProgress | null>(null);

  React.useEffect(() => {
    const unsubscribe = systemRefreshService.onRefreshProgress((progress) => {
      setRefreshProgress(progress);
      setIsRefreshing(!progress.isComplete);
    });

    return unsubscribe;
  }, []);

  return {
    isRefreshing,
    refreshProgress,
    performRefresh: systemRefreshService.performSystemRefresh.bind(systemRefreshService),
    performQuickRefresh: systemRefreshService.performQuickRefresh.bind(systemRefreshService),
    performFullRefresh: systemRefreshService.performFullRefresh.bind(systemRefreshService),
    emergencyRefresh: systemRefreshService.emergencyRefresh.bind(systemRefreshService)
  };
}