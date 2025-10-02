import AsyncStorage from '@react-native-async-storage/async-storage';
import { Platform } from 'react-native';
import * as FileSystem from 'expo-file-system';
import NetInfo from '@react-native-community/netinfo';

export interface OfflineContent {
  id: string;
  type: 'audio' | 'station' | 'playlist' | 'episode';
  title: string;
  description: string;
  url: string;
  localPath?: string;
  metadata: {
    duration?: number;
    size?: number;
    format?: string;
    downloadedAt: string;
    lastAccessed: string;
  };
  isDownloaded: boolean;
}

export interface OfflineSettings {
  maxCacheSize: number; // in MB
  autoDownloadFavorites: boolean;
  downloadOnWifiOnly: boolean;
  keepDownloadsForDays: number;
}

export interface NetworkStatus {
  isConnected: boolean;
  connectionType: string;
  isWiFi: boolean;
  isMetered?: boolean;
}

class OfflineModeService {
  private static instance: OfflineModeService;
  private offlineContent: OfflineContent[] = [];
  private settings: OfflineSettings;
  private networkStatus: NetworkStatus = { isConnected: false, connectionType: 'none', isWiFi: false };
  private listeners: Set<(status: { isOffline: boolean; content: OfflineContent[] }) => void> = new Set();
  private downloadQueue: string[] = [];
  private downloadInProgress: Set<string> = new Set();

  private constructor() {
    this.settings = {
      maxCacheSize: 500, // 500MB default
      autoDownloadFavorites: false,
      downloadOnWifiOnly: true,
      keepDownloadsForDays: 30,
    };
    this.initialize();
  }

  public static getInstance(): OfflineModeService {
    if (!OfflineModeService.instance) {
      OfflineModeService.instance = new OfflineModeService();
    }
    return OfflineModeService.instance;
  }

  private async initialize(): Promise<void> {
    try {
      // Load offline content from storage
      await this.loadOfflineContent();
      
      // Load settings
      await this.loadSettings();
      
      // Setup network monitoring
      this.setupNetworkMonitoring();
      
      // Clean up old downloads
      await this.cleanupOldDownloads();
      
      console.log('✅ Offline mode service initialized');
    } catch (error) {
      console.error('❌ Failed to initialize offline mode service:', error);
    }
  }

  private setupNetworkMonitoring(): void {
    NetInfo.addEventListener(state => {
      this.networkStatus = {
        isConnected: !!state.isConnected,
        connectionType: state.type,
        isWiFi: state.type === 'wifi',
        isMetered: state.details && 'isConnectionExpensive' in state.details 
          ? (state.details as any).isConnectionExpensive 
          : undefined,
      };

      this.notifyListeners();

      // Process download queue if connection is available
      if (this.networkStatus.isConnected && (!this.settings.downloadOnWifiOnly || this.networkStatus.isWiFi)) {
        this.processDownloadQueue();
      }
    });
  }

  // Download content for offline use
  async downloadContent(content: Omit<OfflineContent, 'isDownloaded' | 'localPath'>): Promise<boolean> {
    const contentId = content.id;
    
    try {
      // Check if already downloaded
      const existing = this.offlineContent.find(item => item.id === contentId);
      if (existing?.isDownloaded) {
        console.log(`Content ${contentId} already downloaded`);
        return true;
      }

      // Check network conditions
      if (!this.canDownload()) {
        console.log(`Adding ${contentId} to download queue - network conditions not met`);
        this.addToDownloadQueue(contentId);
        return false;
      }

      // Check available space
      if (!(await this.hasAvailableSpace(content.metadata.size || 0))) {
        console.log(`Not enough space for ${contentId}`);
        return false;
      }

      console.log(`📥 Starting download: ${content.title}`);
      this.downloadInProgress.add(contentId);

      // Generate local file path
      const fileExtension = this.getFileExtension(content.url);
      const fileName = `${contentId}.${fileExtension}`;
      const localPath = `${FileSystem.documentDirectory}offline_content/${fileName}`;

      // Ensure directory exists
      const dirPath = `${FileSystem.documentDirectory}offline_content/`;
      const dirInfo = await FileSystem.getInfoAsync(dirPath);
      if (!dirInfo.exists) {
        await FileSystem.makeDirectoryAsync(dirPath, { intermediates: true });
      }

      // Download the file
      const downloadResult = await FileSystem.downloadAsync(content.url, localPath);
      
      if (downloadResult.status === 200) {
        // Get file size
        const fileInfo = await FileSystem.getInfoAsync(localPath);
        const downloadedContent: OfflineContent = {
          ...content,
          localPath: localPath,
          isDownloaded: true,
          metadata: {
            ...content.metadata,
            size: fileInfo.size,
            downloadedAt: new Date().toISOString(),
            lastAccessed: new Date().toISOString(),
          }
        };

        // Add to offline content
        this.offlineContent.push(downloadedContent);
        await this.saveOfflineContent();

        console.log(`✅ Download completed: ${content.title} (${this.formatFileSize(fileInfo.size || 0)})`);
        this.downloadInProgress.delete(contentId);
        this.notifyListeners();
        
        return true;
      } else {
        throw new Error(`Download failed with status ${downloadResult.status}`);
      }

    } catch (error) {
      console.error(`❌ Download failed for ${content.title}:`, error);
      this.downloadInProgress.delete(contentId);
      
      // Add to queue for retry
      this.addToDownloadQueue(contentId);
      return false;
    }
  }

  // Remove downloaded content
  async removeDownload(contentId: string): Promise<boolean> {
    try {
      const contentIndex = this.offlineContent.findIndex(item => item.id === contentId);
      if (contentIndex === -1) return false;

      const content = this.offlineContent[contentIndex];
      
      // Delete local file
      if (content.localPath) {
        const fileInfo = await FileSystem.getInfoAsync(content.localPath);
        if (fileInfo.exists) {
          await FileSystem.deleteAsync(content.localPath);
        }
      }

      // Remove from offline content
      this.offlineContent.splice(contentIndex, 1);
      await this.saveOfflineContent();

      console.log(`🗑️ Removed download: ${content.title}`);
      this.notifyListeners();
      
      return true;
    } catch (error) {
      console.error(`❌ Failed to remove download for ${contentId}:`, error);
      return false;
    }
  }

  // Get offline content
  getOfflineContent(): OfflineContent[] {
    return [...this.offlineContent];
  }

  // Check if content is available offline
  isContentAvailableOffline(contentId: string): boolean {
    const content = this.offlineContent.find(item => item.id === contentId);
    return content?.isDownloaded || false;
  }

  // Get local path for content
  getLocalPath(contentId: string): string | null {
    const content = this.offlineContent.find(item => item.id === contentId && item.isDownloaded);
    return content?.localPath || null;
  }

  // Get offline storage usage
  async getStorageUsage(): Promise<{ used: number; total: number; available: number }> {
    try {
      const totalSize = this.offlineContent.reduce((sum, item) => sum + (item.metadata.size || 0), 0);
      const maxSize = this.settings.maxCacheSize * 1024 * 1024; // Convert MB to bytes
      
      return {
        used: totalSize,
        total: maxSize,
        available: maxSize - totalSize,
      };
    } catch (error) {
      console.error('❌ Failed to get storage usage:', error);
      return { used: 0, total: 0, available: 0 };
    }
  }

  // Clean up old downloads
  private async cleanupOldDownloads(): Promise<void> {
    try {
      const now = new Date();
      const keepDays = this.settings.keepDownloadsForDays;
      
      const itemsToRemove = this.offlineContent.filter(item => {
        const downloadedAt = new Date(item.metadata.downloadedAt);
        const daysDiff = (now.getTime() - downloadedAt.getTime()) / (1000 * 60 * 60 * 24);
        return daysDiff > keepDays;
      });

      for (const item of itemsToRemove) {
        await this.removeDownload(item.id);
      }

      if (itemsToRemove.length > 0) {
        console.log(`🧹 Cleaned up ${itemsToRemove.length} old downloads`);
      }
    } catch (error) {
      console.error('❌ Failed to cleanup old downloads:', error);
    }
  }

  // Check if download is allowed based on network conditions
  private canDownload(): boolean {
    if (!this.networkStatus.isConnected) return false;
    if (this.settings.downloadOnWifiOnly && !this.networkStatus.isWiFi) return false;
    return true;
  }

  // Check available space
  private async hasAvailableSpace(requiredSize: number): Promise<boolean> {
    const usage = await this.getStorageUsage();
    return usage.available >= requiredSize;
  }

  // Add to download queue
  private addToDownloadQueue(contentId: string): void {
    if (!this.downloadQueue.includes(contentId)) {
      this.downloadQueue.push(contentId);
    }
  }

  // Process download queue
  private async processDownloadQueue(): Promise<void> {
    if (this.downloadQueue.length === 0) return;
    
    console.log(`📋 Processing download queue: ${this.downloadQueue.length} items`);
    
    // Process one item at a time to avoid overwhelming the system
    const contentId = this.downloadQueue.shift();
    if (contentId) {
      // This would need the original content object - in a real implementation,
      // you'd store the full content data in the queue
      console.log(`⏳ Processing queued download: ${contentId}`);
    }
  }

  // Utility functions
  private getFileExtension(url: string): string {
    const path = url.split('?')[0]; // Remove query parameters
    const segments = path.split('/');
    const fileName = segments[segments.length - 1];
    const parts = fileName.split('.');
    return parts.length > 1 ? parts[parts.length - 1] : 'mp3'; // Default to mp3 for audio
  }

  private formatFileSize(bytes: number): string {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  }

  // Settings management
  async updateSettings(newSettings: Partial<OfflineSettings>): Promise<void> {
    this.settings = { ...this.settings, ...newSettings };
    await this.saveSettings();
    console.log('💾 Offline mode settings updated');
  }

  getSettings(): OfflineSettings {
    return { ...this.settings };
  }

  private async loadSettings(): Promise<void> {
    try {
      const storedSettings = await AsyncStorage.getItem('offline_mode_settings');
      if (storedSettings) {
        this.settings = { ...this.settings, ...JSON.parse(storedSettings) };
      }
    } catch (error) {
      console.error('❌ Failed to load offline mode settings:', error);
    }
  }

  private async saveSettings(): Promise<void> {
    try {
      await AsyncStorage.setItem('offline_mode_settings', JSON.stringify(this.settings));
    } catch (error) {
      console.error('❌ Failed to save offline mode settings:', error);
    }
  }

  // Storage management
  private async loadOfflineContent(): Promise<void> {
    try {
      const storedContent = await AsyncStorage.getItem('offline_content');
      if (storedContent) {
        this.offlineContent = JSON.parse(storedContent);
        
        // Verify local files still exist
        for (const content of this.offlineContent) {
          if (content.localPath) {
            const fileInfo = await FileSystem.getInfoAsync(content.localPath);
            if (!fileInfo.exists) {
              content.isDownloaded = false;
              content.localPath = undefined;
            }
          }
        }
        
        await this.saveOfflineContent();
      }
    } catch (error) {
      console.error('❌ Failed to load offline content:', error);
      this.offlineContent = [];
    }
  }

  private async saveOfflineContent(): Promise<void> {
    try {
      await AsyncStorage.setItem('offline_content', JSON.stringify(this.offlineContent));
    } catch (error) {
      console.error('❌ Failed to save offline content:', error);
    }
  }

  // Listener management
  addListener(callback: (status: { isOffline: boolean; content: OfflineContent[] }) => void): () => void {
    this.listeners.add(callback);
    
    // Immediately call with current state
    callback({
      isOffline: !this.networkStatus.isConnected,
      content: [...this.offlineContent],
    });
    
    return () => {
      this.listeners.delete(callback);
    };
  }

  private notifyListeners(): void {
    const status = {
      isOffline: !this.networkStatus.isConnected,
      content: [...this.offlineContent],
    };

    this.listeners.forEach(callback => {
      try {
        callback(status);
      } catch (error) {
        console.error('❌ Offline mode listener error:', error);
      }
    });
  }

  // Get current network status
  getNetworkStatus(): NetworkStatus {
    return { ...this.networkStatus };
  }

  // Export/Import offline content (for backup/restore)
  async exportOfflineContent(): Promise<string> {
    return JSON.stringify({
      content: this.offlineContent,
      settings: this.settings,
      exportedAt: new Date().toISOString(),
    });
  }

  async importOfflineContent(exportData: string): Promise<boolean> {
    try {
      const data = JSON.parse(exportData);
      
      if (data.content && Array.isArray(data.content)) {
        this.offlineContent = data.content;
        await this.saveOfflineContent();
      }
      
      if (data.settings) {
        await this.updateSettings(data.settings);
      }
      
      console.log('✅ Offline content imported successfully');
      this.notifyListeners();
      return true;
    } catch (error) {
      console.error('❌ Failed to import offline content:', error);
      return false;
    }
  }
}

// Export singleton instance
export const offlineModeService = OfflineModeService.getInstance();