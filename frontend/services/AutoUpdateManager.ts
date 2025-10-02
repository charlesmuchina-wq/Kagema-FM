import { systemRefreshService } from './SystemRefreshService';
import AsyncStorage from '@react-native-async-storage/async-storage';
import { Platform } from 'react-native';
import * as Updates from 'expo-updates';

export interface UpdateConfig {
  autoCheckInterval: number; // in minutes
  autoRefreshAfterUpdate: boolean;
  showUpdateProgress: boolean;
  backupDataBeforeUpdate: boolean;
  fallbackOnFailure: boolean;
}

export interface UpdateStatus {
  isChecking: boolean;
  isUpdating: boolean;
  isRefreshing: boolean;
  lastCheckTime: number;
  lastUpdateTime: number;
  updateAvailable: boolean;
  currentVersion: string;
  availableVersion?: string;
  error?: string;
}

export class AutoUpdateManager {
  private static instance: AutoUpdateManager;
  private config: UpdateConfig;
  private status: UpdateStatus;
  private checkInterval: NodeJS.Timeout | null = null;
  private updateCallbacks: ((status: UpdateStatus) => void)[] = [];

  static getInstance(): AutoUpdateManager {
    if (!AutoUpdateManager.instance) {
      AutoUpdateManager.instance = new AutoUpdateManager();
    }
    return AutoUpdateManager.instance;
  }

  constructor() {
    this.config = {
      autoCheckInterval: 30, // Check every 30 minutes
      autoRefreshAfterUpdate: true,
      showUpdateProgress: true,
      backupDataBeforeUpdate: true,
      fallbackOnFailure: true
    };

    this.status = {
      isChecking: false,
      isUpdating: false,
      isRefreshing: false,
      lastCheckTime: 0,
      lastUpdateTime: 0,
      updateAvailable: false,
      currentVersion: this.getCurrentVersion()
    };
  }

  async initialize(config?: Partial<UpdateConfig>): Promise<void> {
    console.log('🔄 Initializing Auto-Update Manager...');

    if (config) {
      this.config = { ...this.config, ...config };
    }

    // Load previous status
    await this.loadStatus();

    // Start auto-check interval
    this.startAutoCheck();

    // Check for updates on startup
    await this.checkForUpdates();

    console.log('✅ Auto-Update Manager initialized');
  }

  // Subscribe to update status changes
  onStatusChange(callback: (status: UpdateStatus) => void): () => void {
    this.updateCallbacks.push(callback);
    // Immediately call with current status
    callback(this.status);
    
    return () => {
      const index = this.updateCallbacks.indexOf(callback);
      if (index > -1) {
        this.updateCallbacks.splice(index, 1);
      }
    };
  }

  private notifyStatusChange() {
    this.updateCallbacks.forEach(callback => callback({ ...this.status }));
    this.saveStatus();
  }

  // Check for available updates
  async checkForUpdates(): Promise<boolean> {
    if (this.status.isChecking || this.status.isUpdating) {
      console.log('⚠️ Update check already in progress');
      return false;
    }

    try {
      this.status.isChecking = true;
      this.status.lastCheckTime = Date.now();
      this.status.error = undefined;
      this.notifyStatusChange();

      console.log('🔍 Checking for updates...');

      if (Platform.OS === 'web') {
        // For web, check app version or manifest changes
        const hasUpdates = await this.checkWebUpdates();
        this.status.updateAvailable = hasUpdates;
        
        if (hasUpdates) {
          console.log('📥 Web app updates available');
          return await this.handleWebUpdate();
        }
      } else {
        // For native, use Expo Updates
        if (Updates.isEnabled) {
          const update = await Updates.checkForUpdateAsync();
          this.status.updateAvailable = update.isAvailable;
          
          if (update.isAvailable) {
            console.log('📥 Native app update available');
            this.status.availableVersion = update.manifest?.version || 'Unknown';
            return await this.handleNativeUpdate();
          }
        }
      }

      console.log('✅ No updates available');
      return false;

    } catch (error) {
      console.error('❌ Update check failed:', error);
      this.status.error = error.message;
      return false;
    } finally {
      this.status.isChecking = false;
      this.notifyStatusChange();
    }
  }

  private async checkWebUpdates(): Promise<boolean> {
    try {
      // Check for service worker updates or manifest changes
      if ('serviceWorker' in navigator) {
        const registration = await navigator.serviceWorker.getRegistration();
        if (registration) {
          await registration.update();
          return registration.waiting !== null;
        }
      }
      
      // Alternative: Check app version via API or cache
      return await this.checkAppVersionAPI();
    } catch (error) {
      console.log('⚠️ Web update check partial:', error.message);
      return false;
    }
  }

  private async checkAppVersionAPI(): Promise<boolean> {
    try {
      // Check if there's a newer version available via backend
      const EXPO_PUBLIC_BACKEND_URL = process.env.EXPO_BACKEND_URL || '';
      const response = await fetch(`${EXPO_PUBLIC_BACKEND_URL}/api/app/version`);
      
      if (response.ok) {
        const data = await response.json();
        const serverVersion = data.version;
        const currentVersion = this.getCurrentVersion();
        
        return this.isVersionNewer(serverVersion, currentVersion);
      }
    } catch (error) {
      console.log('⚠️ Version API check failed:', error.message);
    }
    
    return false;
  }

  private async handleWebUpdate(): Promise<boolean> {
    try {
      this.status.isUpdating = true;
      this.notifyStatusChange();

      console.log('🔄 Applying web updates...');

      // Backup data if configured
      if (this.config.backupDataBeforeUpdate) {
        await this.backupUserData();
      }

      // Perform system refresh for web updates
      await systemRefreshService.performSystemRefresh({
        clearAsyncStorage: false, // Don't clear user data
        clearServiceCaches: true,
        restartServices: true,
        reloadApp: true,
        showProgress: this.config.showUpdateProgress,
        skipConfirmation: true
      });

      this.status.lastUpdateTime = Date.now();
      this.status.currentVersion = this.getCurrentVersion();
      
      console.log('✅ Web update completed');
      return true;

    } catch (error) {
      console.error('❌ Web update failed:', error);
      
      if (this.config.fallbackOnFailure) {
        await this.performFallbackRecovery();
      }
      
      return false;
    } finally {
      this.status.isUpdating = false;
      this.notifyStatusChange();
    }
  }

  private async handleNativeUpdate(): Promise<boolean> {
    try {
      this.status.isUpdating = true;
      this.notifyStatusChange();

      console.log('📥 Downloading native update...');

      // Backup data if configured
      if (this.config.backupDataBeforeUpdate) {
        await this.backupUserData();
      }

      if (Updates.isEnabled) {
        // Download and apply update
        const result = await Updates.fetchUpdateAsync();
        
        if (result.isNew) {
          console.log('✅ Update downloaded successfully');
          
          // Perform system refresh before applying update
          if (this.config.autoRefreshAfterUpdate) {
            await systemRefreshService.autoRefreshAfterUpdate();
          }
          
          this.status.lastUpdateTime = Date.now();
          
          // Apply update (this will restart the app)
          await Updates.reloadAsync();
          
          return true;
        }
      }

      return false;

    } catch (error) {
      console.error('❌ Native update failed:', error);
      
      if (this.config.fallbackOnFailure) {
        await this.performFallbackRecovery();
      }
      
      return false;
    } finally {
      this.status.isUpdating = false;
      this.notifyStatusChange();
    }
  }

  private async backupUserData(): Promise<void> {
    try {
      console.log('💾 Backing up user data...');
      
      const backupData = {
        preferences: await AsyncStorage.getItem('user_preferences'),
        favorites: await AsyncStorage.getItem('soundcast_favorites'),
        radioGardenFavorites: await AsyncStorage.getItem('radio_garden_favorites'),
        notificationSettings: await AsyncStorage.getItem('notification_settings'),
        timestamp: Date.now()
      };

      await AsyncStorage.setItem('user_data_backup', JSON.stringify(backupData));
      console.log('✅ User data backed up successfully');
      
    } catch (error) {
      console.log('⚠️ User data backup partial:', error.message);
    }
  }

  private async performFallbackRecovery(): Promise<void> {
    try {
      console.log('🔧 Performing fallback recovery...');
      
      // Restore backed up data
      const backupData = await AsyncStorage.getItem('user_data_backup');
      if (backupData) {
        const backup = JSON.parse(backupData);
        
        // Restore critical data
        if (backup.preferences) {
          await AsyncStorage.setItem('user_preferences', backup.preferences);
        }
        if (backup.favorites) {
          await AsyncStorage.setItem('soundcast_favorites', backup.favorites);
        }
        if (backup.radioGardenFavorites) {
          await AsyncStorage.setItem('radio_garden_favorites', backup.radioGardenFavorites);
        }
        
        console.log('✅ User data restored from backup');
      }

      // Perform emergency refresh
      await systemRefreshService.emergencyRefresh();
      
    } catch (error) {
      console.error('❌ Fallback recovery failed:', error);
    }
  }

  private startAutoCheck(): void {
    if (this.checkInterval) {
      clearInterval(this.checkInterval);
    }

    const intervalMs = this.config.autoCheckInterval * 60 * 1000; // Convert to milliseconds
    
    this.checkInterval = setInterval(async () => {
      console.log('⏰ Performing scheduled update check...');
      await this.checkForUpdates();
    }, intervalMs);

    console.log(`⏰ Auto-check scheduled every ${this.config.autoCheckInterval} minutes`);
  }

  private stopAutoCheck(): void {
    if (this.checkInterval) {
      clearInterval(this.checkInterval);
      this.checkInterval = null;
      console.log('⏹️ Auto-check stopped');
    }
  }

  private getCurrentVersion(): string {
    try {
      if (Platform.OS !== 'web' && Updates.manifest?.version) {
        return Updates.manifest.version;
      }
      
      // Fallback to a default version
      return '1.0.0';
    } catch {
      return '1.0.0';
    }
  }

  private isVersionNewer(newVersion: string, currentVersion: string): boolean {
    const parseVersion = (version: string) => {
      return version.split('.').map(num => parseInt(num, 10));
    };

    const newParts = parseVersion(newVersion);
    const currentParts = parseVersion(currentVersion);

    for (let i = 0; i < Math.max(newParts.length, currentParts.length); i++) {
      const newPart = newParts[i] || 0;
      const currentPart = currentParts[i] || 0;

      if (newPart > currentPart) return true;
      if (newPart < currentPart) return false;
    }

    return false;
  }

  private async loadStatus(): Promise<void> {
    try {
      const storedStatus = await AsyncStorage.getItem('auto_update_status');
      if (storedStatus) {
        const parsed = JSON.parse(storedStatus);
        this.status = { ...this.status, ...parsed };
      }
    } catch (error) {
      console.log('⚠️ Failed to load update status:', error.message);
    }
  }

  private async saveStatus(): Promise<void> {
    try {
      await AsyncStorage.setItem('auto_update_status', JSON.stringify(this.status));
    } catch (error) {
      console.log('⚠️ Failed to save update status:', error.message);
    }
  }

  // Public methods
  getStatus(): UpdateStatus {
    return { ...this.status };
  }

  updateConfig(newConfig: Partial<UpdateConfig>): void {
    this.config = { ...this.config, ...newConfig };
    
    // Restart auto-check with new interval if changed
    if (newConfig.autoCheckInterval) {
      this.startAutoCheck();
    }
  }

  async forceCheck(): Promise<boolean> {
    console.log('🔍 Force checking for updates...');
    return await this.checkForUpdates();
  }

  async forceUpdate(): Promise<boolean> {
    if (this.status.updateAvailable) {
      if (Platform.OS === 'web') {
        return await this.handleWebUpdate();
      } else {
        return await this.handleNativeUpdate();
      }
    }
    return false;
  }

  // Auto-refresh after all system updates
  async autoRefreshAfterAllUpdates(): Promise<boolean> {
    console.log('🔄 Auto-refreshing after all system updates...');
    
    try {
      // Wait a moment for any ongoing operations to complete
      await new Promise(resolve => setTimeout(resolve, 2000));
      
      // Perform comprehensive system refresh
      const success = await systemRefreshService.performSystemRefresh({
        clearAsyncStorage: false, // Preserve user data
        clearServiceCaches: true,
        restartServices: true,
        reloadApp: false, // Don't reload immediately
        showProgress: false,
        skipConfirmation: true
      });

      if (success) {
        console.log('✅ Auto-refresh after updates completed successfully');
        
        // Schedule a delayed reload if needed
        if (Platform.OS === 'web') {
          setTimeout(() => {
            if (typeof window !== 'undefined' && window.location) {
              window.location.reload();
            }
          }, 3000);
        }
      }

      return success;
      
    } catch (error) {
      console.error('❌ Auto-refresh after updates failed:', error);
      return false;
    }
  }

  dispose(): void {
    this.stopAutoCheck();
    this.updateCallbacks = [];
  }
}

// Export singleton instance
export const autoUpdateManager = AutoUpdateManager.getInstance();