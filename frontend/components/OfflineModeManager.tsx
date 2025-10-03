import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  TouchableOpacity,
  StyleSheet,
  ScrollView,
  Alert,
  ProgressBarAndroid,
  ProgressViewIOS,
  Platform,
  Switch,
  Modal,
} from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { offlineModeService, OfflineContent, OfflineSettings, NetworkStatus } from '../services/OfflineModeService';
import { accessibilityService } from '../services/AccessibilityService';

interface OfflineModeManagerProps {
  visible: boolean;
  onClose: () => void;
  onPlayOfflineContent: (content: OfflineContent) => void;
}

export const OfflineModeManager: React.FC<OfflineModeManagerProps> = ({
  visible,
  onClose,
  onPlayOfflineContent,
}) => {
  const [offlineContent, setOfflineContent] = useState<OfflineContent[]>([]);
  const [settings, setSettings] = useState<OfflineSettings | null>(null);
  const [networkStatus, setNetworkStatus] = useState<NetworkStatus>({ isConnected: false, connectionType: 'none', isWiFi: false });
  const [storageUsage, setStorageUsage] = useState({ used: 0, total: 0, available: 0 });
  const [currentTab, setCurrentTab] = useState<'downloads' | 'settings' | 'storage'>('downloads');
  const [downloadProgress, setDownloadProgress] = useState<{ [key: string]: number }>({});
  const [accessibility] = useState(() => accessibilityService.getSettings());

  useEffect(() => {
    if (visible) {
      loadData();
      setupListeners();
    }
  }, [visible]);

  const loadData = async () => {
    try {
      setOfflineContent(offlineModeService.getOfflineContent());
      setSettings(offlineModeService.getSettings());
      setNetworkStatus(offlineModeService.getNetworkStatus());
      
      const usage = await offlineModeService.getStorageUsage();
      setStorageUsage(usage);
    } catch (error) {
      console.error('Failed to load offline mode data:', error);
    }
  };

  const setupListeners = () => {
    const unsubscribe = offlineModeService.addListener((status) => {
      setOfflineContent(status.content);
      setNetworkStatus(offlineModeService.getNetworkStatus());
    });

    return () => {
      unsubscribe();
    };
  };

  const handleDownloadContent = async (content: Omit<OfflineContent, 'isDownloaded' | 'localPath'>) => {
    try {
      accessibilityService.hapticFeedback('light');
      accessibilityService.announceIf(`Starting download: ${content.title}`);
      
      const success = await offlineModeService.downloadContent(content);
      if (success) {
        Alert.alert('Download Started', `"${content.title}" is downloading in the background.`);
        accessibilityService.hapticFeedback('success');
      } else {
        Alert.alert('Download Queued', `"${content.title}" has been added to the download queue and will start when conditions are met.`);
        accessibilityService.hapticFeedback('warning');
      }
    } catch (error) {
      Alert.alert('Download Failed', `Failed to download "${content.title}". Please try again.`);
      accessibilityService.hapticFeedback('error');
    }
  };

  const handleRemoveDownload = async (contentId: string) => {
    const content = offlineContent.find(item => item.id === contentId);
    if (!content) return;

    Alert.alert(
      'Remove Download',
      `Are you sure you want to remove "${content.title}" from your device?`,
      [
        { text: 'Cancel', style: 'cancel' },
        {
          text: 'Remove',
          style: 'destructive',
          onPress: async () => {
            const success = await offlineModeService.removeDownload(contentId);
            if (success) {
              accessibilityService.announceIf(`${content.title} removed from downloads`);
              accessibilityService.hapticFeedback('light');
              loadData();
            }
          },
        },
      ]
    );
  };

  const handleUpdateSettings = async (newSettings: Partial<OfflineSettings>) => {
    try {
      await offlineModeService.updateSettings(newSettings);
      setSettings({ ...settings!, ...newSettings });
      accessibilityService.hapticFeedback('light');
    } catch (error) {
      console.error('Failed to update offline mode settings:', error);
    }
  };

  const formatFileSize = (bytes: number): string => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  const getConnectionIcon = (type: string) => {
    switch (type) {
      case 'wifi': return 'wifi';
      case 'cellular': return 'cellular';
      default: return 'wifi-off';
    }
  };

  const renderNetworkStatus = () => (
    <View style={styles.networkStatus}>
      <Ionicons 
        name={getConnectionIcon(networkStatus.connectionType)} 
        size={20} 
        color={networkStatus.isConnected ? '#4CAF50' : '#F44336'} 
      />
      <Text style={styles.networkText}>
        {networkStatus.isConnected 
          ? `Connected via ${networkStatus.connectionType}${networkStatus.isWiFi ? ' (WiFi)' : ''}` 
          : 'Offline'}
      </Text>
    </View>
  );

  const renderDownloadsTab = () => (
    <ScrollView style={styles.tabContent}>
      {renderNetworkStatus()}
      
      <Text style={styles.sectionTitle}>Downloaded Content</Text>
      
      {offlineContent.length === 0 ? (
        <View style={styles.emptyState}>
          <Ionicons name="download-outline" size={48} color="#999" />
          <Text style={styles.emptyText}>No offline content yet</Text>
          <Text style={styles.emptySubtext}>
            Download your favorite stations and content to enjoy them offline
          </Text>
        </View>
      ) : (
        offlineContent.map((content) => (
          <View key={content.id} style={styles.contentItem}>
            <View style={styles.contentIcon}>
              <Ionicons 
                name={content.type === 'audio' ? 'musical-notes' : 'radio'} 
                size={24} 
                color="#4ECDC4" 
              />
            </View>
            
            <View style={styles.contentDetails}>
              <Text style={styles.contentTitle} numberOfLines={1}>
                {content.title}
              </Text>
              <Text style={styles.contentMeta}>
                {content.metadata.size ? formatFileSize(content.metadata.size) : 'Unknown size'} • 
                {content.type}
              </Text>
              <Text style={styles.contentDate}>
                Downloaded: {new Date(content.metadata.downloadedAt).toLocaleDateString()}
              </Text>
            </View>
            
            <View style={styles.contentActions}>
              <TouchableOpacity
                style={styles.actionButton}
                onPress={() => {
                  onPlayOfflineContent(content);
                  accessibilityService.hapticFeedback('light');
                }}
                accessible={true}
                accessibilityLabel={`Play ${content.title}`}
                accessibilityHint="Double tap to play this offline content"
              >
                <Ionicons name="play" size={20} color="#4ECDC4" />
              </TouchableOpacity>
              
              <TouchableOpacity
                style={styles.actionButton}
                onPress={() => handleRemoveDownload(content.id)}
                accessible={true}
                accessibilityLabel={`Remove ${content.title}`}
                accessibilityHint="Double tap to remove from device"
              >
                <Ionicons name="trash-outline" size={20} color="#F44336" />
              </TouchableOpacity>
            </View>
          </View>
        ))
      )}

      {/* Quick download suggestions */}
      <Text style={styles.sectionTitle}>Suggested Downloads</Text>
      <View style={styles.suggestionCard}>
        <Text style={styles.suggestionTitle}>Favorite Stations</Text>
        <Text style={styles.suggestionText}>
          Enable auto-download for your favorite stations to always have them available offline
        </Text>
        <TouchableOpacity
          style={styles.suggestionButton}
          onPress={() => setCurrentTab('settings')}
        >
          <Text style={styles.suggestionButtonText}>Configure Auto-Download</Text>
        </TouchableOpacity>
      </View>
    </ScrollView>
  );

  const renderSettingsTab = () => (
    <ScrollView style={styles.tabContent}>
      <Text style={styles.sectionTitle}>Download Settings</Text>
      
      <View style={styles.settingItem}>
        <View style={styles.settingLabel}>
          <Text style={styles.settingTitle}>Auto-Download Favorites</Text>
          <Text style={styles.settingDescription}>
            Automatically download new favorite stations
          </Text>
        </View>
        <Switch
          value={settings?.autoDownloadFavorites || false}
          onValueChange={(value) => handleUpdateSettings({ autoDownloadFavorites: value })}
          accessible={true}
          accessibilityLabel="Auto-download favorites"
        />
      </View>
      
      <View style={styles.settingItem}>
        <View style={styles.settingLabel}>
          <Text style={styles.settingTitle}>WiFi Only Downloads</Text>
          <Text style={styles.settingDescription}>
            Only download content when connected to WiFi
          </Text>
        </View>
        <Switch
          value={settings?.downloadOnWifiOnly || false}
          onValueChange={(value) => handleUpdateSettings({ downloadOnWifiOnly: value })}
          accessible={true}
          accessibilityLabel="WiFi only downloads"
        />
      </View>

      <Text style={styles.sectionTitle}>Storage Management</Text>
      
      <View style={styles.settingItem}>
        <View style={styles.settingLabel}>
          <Text style={styles.settingTitle}>Maximum Cache Size</Text>
          <Text style={styles.settingDescription}>
            {settings?.maxCacheSize || 0} MB
          </Text>
        </View>
      </View>
      
      <View style={styles.settingItem}>
        <View style={styles.settingLabel}>
          <Text style={styles.settingTitle}>Keep Downloads</Text>
          <Text style={styles.settingDescription}>
            {settings?.keepDownloadsForDays || 0} days
          </Text>
        </View>
      </View>
    </ScrollView>
  );

  const renderStorageTab = () => {
    const usagePercentage = storageUsage.total > 0 ? (storageUsage.used / storageUsage.total) * 100 : 0;
    
    return (
      <ScrollView style={styles.tabContent}>
        <Text style={styles.sectionTitle}>Storage Usage</Text>
        
        <View style={styles.storageCard}>
          <View style={styles.storageHeader}>
            <Text style={styles.storageTitle}>Offline Content</Text>
            <Text style={styles.storageUsed}>
              {formatFileSize(storageUsage.used)} of {formatFileSize(storageUsage.total)} used
            </Text>
          </View>
          
          <View style={styles.progressContainer}>
            {Platform.OS === 'ios' ? (
              <ProgressViewIOS 
                progress={usagePercentage / 100} 
                progressTintColor={usagePercentage > 80 ? '#F44336' : '#4ECDC4'}
                trackTintColor="#E0E0E0"
              />
            ) : (
              <ProgressBarAndroid
                styleAttr="Horizontal"
                indeterminate={false}
                progress={usagePercentage / 100}
                color={usagePercentage > 80 ? '#F44336' : '#4ECDC4'}
              />
            )}
          </View>
          
          <Text style={styles.storageAvailable}>
            {formatFileSize(storageUsage.available)} available
          </Text>
        </View>
        
        <Text style={styles.sectionTitle}>Content Breakdown</Text>
        
        {offlineContent.reduce((acc, content) => {
          const type = content.type;
          if (!acc[type]) {
            acc[type] = { count: 0, size: 0 };
          }
          acc[type].count += 1;
          acc[type].size += content.metadata.size || 0;
          return acc;
        }, {} as { [key: string]: { count: number; size: number } }) && 
          Object.entries(
            offlineContent.reduce((acc, content) => {
              const type = content.type;
              if (!acc[type]) {
                acc[type] = { count: 0, size: 0 };
              }
              acc[type].count += 1;
              acc[type].size += content.metadata.size || 0;
              return acc;
            }, {} as { [key: string]: { count: number; size: number } })
          ).map(([type, data]) => (
            <View key={type} style={styles.breakdownItem}>
              <View style={styles.breakdownIcon}>
                <Ionicons 
                  name={type === 'audio' ? 'musical-notes' : 'radio'} 
                  size={20} 
                  color="#4ECDC4" 
                />
              </View>
              <View style={styles.breakdownDetails}>
                <Text style={styles.breakdownType}>
                  {type.charAt(0).toUpperCase() + type.slice(1)}
                </Text>
                <Text style={styles.breakdownMeta}>
                  {data.count} items • {formatFileSize(data.size)}
                </Text>
              </View>
            </View>
          ))
        }
      </ScrollView>
    );
  };

  const renderTabBar = () => (
    <View style={styles.tabBar}>
      {[
        { key: 'downloads', label: 'Downloads', icon: 'download-outline' },
        { key: 'settings', label: 'Settings', icon: 'settings-outline' },
        { key: 'storage', label: 'Storage', icon: 'server-outline' },
      ].map((tab) => (
        <TouchableOpacity
          key={tab.key}
          style={[styles.tab, currentTab === tab.key && styles.activeTab]}
          onPress={() => {
            setCurrentTab(tab.key as any);
            accessibilityService.hapticFeedback('light');
          }}
          accessible={true}
          accessibilityLabel={tab.label}
          accessibilityRole="tab"
        >
          <Ionicons 
            name={tab.icon as any} 
            size={20} 
            color={currentTab === tab.key ? '#4ECDC4' : '#999'} 
          />
          <Text style={[
            styles.tabLabel,
            currentTab === tab.key && styles.activeTabLabel
          ]}>
            {tab.label}
          </Text>
        </TouchableOpacity>
      ))}
    </View>
  );

  return (
    <Modal visible={visible} animationType="slide" presentationStyle="pageSheet">
      <View style={styles.container}>
        <View style={styles.header}>
          <Text style={styles.title}>Offline Mode</Text>
          <TouchableOpacity
            style={styles.closeButton}
            onPress={onClose}
            accessible={true}
            accessibilityLabel="Close offline mode"
            accessibilityHint="Double tap to close this screen"
          >
            <Ionicons name="close" size={24} color="#333" />
          </TouchableOpacity>
        </View>
        
        {renderTabBar()}
        
        <View style={styles.content}>
          {currentTab === 'downloads' && renderDownloadsTab()}
          {currentTab === 'settings' && renderSettingsTab()}
          {currentTab === 'storage' && renderStorageTab()}
        </View>
      </View>
    </Modal>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#FFFFFF',
  },
  header: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingHorizontal: 20,
    paddingTop: Platform.OS === 'ios' ? 50 : 20,
    paddingBottom: 15,
    borderBottomWidth: 1,
    borderBottomColor: '#E0E0E0',
  },
  title: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#333',
  },
  closeButton: {
    padding: 5,
  },
  tabBar: {
    flexDirection: 'row',
    backgroundColor: '#F8F9FA',
    borderBottomWidth: 1,
    borderBottomColor: '#E0E0E0',
  },
  tab: {
    flex: 1,
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    paddingVertical: 12,
    paddingHorizontal: 8,
  },
  activeTab: {
    backgroundColor: '#FFFFFF',
    borderBottomWidth: 2,
    borderBottomColor: '#4ECDC4',
  },
  tabLabel: {
    marginLeft: 6,
    fontSize: 14,
    color: '#999',
    fontWeight: '500',
  },
  activeTabLabel: {
    color: '#4ECDC4',
  },
  content: {
    flex: 1,
  },
  tabContent: {
    flex: 1,
    padding: 20,
  },
  networkStatus: {
    flexDirection: 'row',
    alignItems: 'center',
    padding: 12,
    backgroundColor: '#F0F8FF',
    borderRadius: 8,
    marginBottom: 20,
  },
  networkText: {
    marginLeft: 8,
    fontSize: 14,
    color: '#333',
    fontWeight: '500',
  },
  sectionTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#333',
    marginBottom: 15,
    marginTop: 10,
  },
  emptyState: {
    alignItems: 'center',
    paddingVertical: 40,
  },
  emptyText: {
    fontSize: 16,
    fontWeight: '600',
    color: '#999',
    marginTop: 15,
    textAlign: 'center',
  },
  emptySubtext: {
    fontSize: 14,
    color: '#666',
    marginTop: 8,
    textAlign: 'center',
    paddingHorizontal: 20,
    lineHeight: 20,
  },
  contentItem: {
    flexDirection: 'row',
    alignItems: 'center',
    padding: 15,
    backgroundColor: '#F8F9FA',
    borderRadius: 10,
    marginBottom: 10,
  },
  contentIcon: {
    width: 40,
    height: 40,
    borderRadius: 20,
    backgroundColor: '#4ECDC4',
    justifyContent: 'center',
    alignItems: 'center',
    marginRight: 15,
  },
  contentDetails: {
    flex: 1,
  },
  contentTitle: {
    fontSize: 16,
    fontWeight: '600',
    color: '#333',
    marginBottom: 4,
  },
  contentMeta: {
    fontSize: 12,
    color: '#666',
    marginBottom: 2,
  },
  contentDate: {
    fontSize: 11,
    color: '#999',
  },
  contentActions: {
    flexDirection: 'row',
  },
  actionButton: {
    padding: 10,
    marginLeft: 5,
  },
  suggestionCard: {
    padding: 15,
    backgroundColor: '#E8F5E8',
    borderRadius: 10,
    marginTop: 10,
  },
  suggestionTitle: {
    fontSize: 16,
    fontWeight: '600',
    color: '#2E7D32',
    marginBottom: 8,
  },
  suggestionText: {
    fontSize: 14,
    color: '#388E3C',
    marginBottom: 15,
    lineHeight: 20,
  },
  suggestionButton: {
    backgroundColor: '#4CAF50',
    paddingHorizontal: 20,
    paddingVertical: 10,
    borderRadius: 20,
    alignSelf: 'flex-start',
  },
  suggestionButtonText: {
    color: '#FFFFFF',
    fontSize: 14,
    fontWeight: '600',
  },
  settingItem: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingVertical: 15,
    paddingHorizontal: 5,
    borderBottomWidth: 1,
    borderBottomColor: '#F0F0F0',
  },
  settingLabel: {
    flex: 1,
    marginRight: 15,
  },
  settingTitle: {
    fontSize: 16,
    fontWeight: '500',
    color: '#333',
    marginBottom: 4,
  },
  settingDescription: {
    fontSize: 14,
    color: '#666',
    lineHeight: 18,
  },
  storageCard: {
    padding: 20,
    backgroundColor: '#F8F9FA',
    borderRadius: 12,
    marginBottom: 20,
  },
  storageHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'flex-end',
    marginBottom: 15,
  },
  storageTitle: {
    fontSize: 16,
    fontWeight: '600',
    color: '#333',
  },
  storageUsed: {
    fontSize: 12,
    color: '#666',
  },
  progressContainer: {
    marginBottom: 10,
  },
  storageAvailable: {
    fontSize: 12,
    color: '#4CAF50',
    textAlign: 'center',
    marginTop: 5,
  },
  breakdownItem: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingVertical: 12,
    paddingHorizontal: 5,
    borderBottomWidth: 1,
    borderBottomColor: '#F0F0F0',
  },
  breakdownIcon: {
    width: 32,
    height: 32,
    borderRadius: 16,
    backgroundColor: '#E8F4FD',
    justifyContent: 'center',
    alignItems: 'center',
    marginRight: 12,
  },
  breakdownDetails: {
    flex: 1,
  },
  breakdownType: {
    fontSize: 14,
    fontWeight: '500',
    color: '#333',
    marginBottom: 2,
  },
  breakdownMeta: {
    fontSize: 12,
    color: '#666',
  },
});

export default OfflineModeManager;