import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  StyleSheet,
  TouchableOpacity,
  Modal,
  ActivityIndicator,
  Alert,
  ScrollView,
  Switch,
} from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { useTheme } from '../contexts/ThemeContext';
import { systemRefreshService, useSystemRefresh } from '../services/SystemRefreshService';
import { autoUpdateManager } from '../services/AutoUpdateManager';

interface SystemRefreshManagerProps {
  visible: boolean;
  onClose: () => void;
}

export const SystemRefreshManager: React.FC<SystemRefreshManagerProps> = ({
  visible,
  onClose
}) => {
  const { colors } = useTheme();
  const {
    isRefreshing,
    refreshProgress,
    performRefresh,
    performQuickRefresh,
    performFullRefresh,
    emergencyRefresh
  } = useSystemRefresh();

  const [updateStatus, setUpdateStatus] = useState(autoUpdateManager.getStatus());
  const [autoRefreshEnabled, setAutoRefreshEnabled] = useState(true);
  const [showAdvancedOptions, setShowAdvancedOptions] = useState(false);

  useEffect(() => {
    if (!visible) return;

    // Subscribe to update status changes
    const unsubscribe = autoUpdateManager.onStatusChange((status) => {
      setUpdateStatus(status);
    });

    return unsubscribe;
  }, [visible]);

  const handleQuickRefresh = async () => {
    try {
      const success = await performQuickRefresh();
      if (success) {
        Alert.alert('Success', 'Quick refresh completed successfully!');
      } else {
        Alert.alert('Error', 'Quick refresh failed. Please try full refresh.');
      }
    } catch (error) {
      Alert.alert('Error', `Refresh failed: ${error.message}`);
    }
  };

  const handleFullRefresh = async () => {
    Alert.alert(
      'Full System Refresh',
      'This will clear all caches and restart services. Continue?',
      [
        { text: 'Cancel', style: 'cancel' },
        {
          text: 'Continue',
          style: 'destructive',
          onPress: async () => {
            try {
              const success = await performFullRefresh();
              if (success) {
                Alert.alert('Success', 'Full system refresh completed!');
              }
            } catch (error) {
              Alert.alert('Error', `Full refresh failed: ${error.message}`);
            }
          }
        }
      ]
    );
  };

  const handleEmergencyRefresh = async () => {
    Alert.alert(
      'Emergency Refresh',
      'This will perform minimal essential operations only. Use if app is not working properly.',
      [
        { text: 'Cancel', style: 'cancel' },
        {
          text: 'Emergency Refresh',
          style: 'destructive',
          onPress: async () => {
            try {
              const success = await emergencyRefresh();
              if (success) {
                Alert.alert('Success', 'Emergency refresh completed!');
              }
            } catch (error) {
              Alert.alert('Error', `Emergency refresh failed: ${error.message}`);
            }
          }
        }
      ]
    );
  };

  const handleCheckForUpdates = async () => {
    try {
      const hasUpdates = await autoUpdateManager.forceCheck();
      if (hasUpdates) {
        Alert.alert(
          'Update Available',
          'A new version is available. Would you like to update now?',
          [
            { text: 'Later', style: 'cancel' },
            {
              text: 'Update Now',
              onPress: async () => {
                await autoUpdateManager.forceUpdate();
              }
            }
          ]
        );
      } else {
        Alert.alert('No Updates', 'You are running the latest version.');
      }
    } catch (error) {
      Alert.alert('Error', `Update check failed: ${error.message}`);
    }
  };

  const toggleAutoRefresh = async (enabled: boolean) => {
    setAutoRefreshEnabled(enabled);
    
    if (enabled) {
      // Initialize auto-update manager if enabling
      await autoUpdateManager.initialize({
        autoRefreshAfterUpdate: true,
        autoCheckInterval: 30 // 30 minutes
      });
      
      Alert.alert(
        'Auto-Refresh Enabled',
        'The system will automatically refresh after updates and check for new versions every 30 minutes.'
      );
    } else {
      // Update config to disable auto-refresh
      autoUpdateManager.updateConfig({
        autoRefreshAfterUpdate: false
      });
      
      Alert.alert(
        'Auto-Refresh Disabled',
        'You will need to manually refresh the system after updates.'
      );
    }
  };

  const formatTime = (timestamp: number): string => {
    if (!timestamp) return 'Never';
    return new Date(timestamp).toLocaleString();
  };

  const formatProgress = (progress: number): string => {
    return `${Math.round(progress)}%`;
  };

  const styles = StyleSheet.create({
    container: {
      flex: 1,
      backgroundColor: colors.background,
    },
    header: {
      flexDirection: 'row',
      alignItems: 'center',
      justifyContent: 'space-between',
      padding: 20,
      paddingTop: 40,
      borderBottomWidth: 1,
      borderBottomColor: colors.border,
      backgroundColor: colors.surface,
    },
    headerTitle: {
      fontSize: 20,
      fontWeight: '600',
      color: colors.text,
    },
    closeButton: {
      padding: 8,
      borderRadius: 8,
      backgroundColor: colors.background,
    },
    content: {
      flex: 1,
      padding: 20,
    },
    section: {
      backgroundColor: colors.card,
      borderRadius: 16,
      padding: 16,
      marginBottom: 16,
      borderWidth: 1,
      borderColor: colors.border,
    },
    sectionTitle: {
      fontSize: 18,
      fontWeight: '600',
      color: colors.text,
      marginBottom: 12,
    },
    statusRow: {
      flexDirection: 'row',
      alignItems: 'center',
      justifyContent: 'space-between',
      marginBottom: 8,
    },
    statusLabel: {
      fontSize: 14,
      color: colors.textSecondary,
    },
    statusValue: {
      fontSize: 14,
      fontWeight: '500',
      color: colors.text,
    },
    progressSection: {
      marginTop: 16,
      padding: 16,
      backgroundColor: colors.surface,
      borderRadius: 12,
    },
    progressTitle: {
      fontSize: 16,
      fontWeight: '600',
      color: colors.text,
      marginBottom: 8,
    },
    progressBar: {
      height: 8,
      backgroundColor: colors.border,
      borderRadius: 4,
      overflow: 'hidden',
      marginBottom: 8,
    },
    progressFill: {
      height: '100%',
      backgroundColor: colors.primary,
      borderRadius: 4,
    },
    progressText: {
      fontSize: 12,
      color: colors.textSecondary,
      textAlign: 'center',
    },
    buttonRow: {
      flexDirection: 'row',
      gap: 12,
      marginTop: 16,
    },
    button: {
      flex: 1,
      backgroundColor: colors.primary,
      borderRadius: 12,
      padding: 16,
      alignItems: 'center',
      justifyContent: 'center',
    },
    buttonSecondary: {
      backgroundColor: colors.surface,
      borderWidth: 1,
      borderColor: colors.border,
    },
    buttonDanger: {
      backgroundColor: '#ff4757',
    },
    buttonText: {
      fontSize: 14,
      fontWeight: '600',
      color: colors.background,
      marginTop: 4,
    },
    buttonTextSecondary: {
      color: colors.text,
    },
    switchRow: {
      flexDirection: 'row',
      alignItems: 'center',
      justifyContent: 'space-between',
      marginBottom: 12,
    },
    switchLabel: {
      fontSize: 16,
      color: colors.text,
      flex: 1,
    },
    switchDescription: {
      fontSize: 12,
      color: colors.textSecondary,
      marginTop: 4,
      marginBottom: 8,
    },
    advancedToggle: {
      flexDirection: 'row',
      alignItems: 'center',
      justifyContent: 'center',
      padding: 12,
      marginTop: 16,
    },
    advancedToggleText: {
      fontSize: 14,
      color: colors.primary,
      marginLeft: 8,
    },
    versionInfo: {
      fontSize: 12,
      color: colors.textSecondary,
      textAlign: 'center',
      marginTop: 16,
    },
    loadingOverlay: {
      position: 'absolute',
      top: 0,
      left: 0,
      right: 0,
      bottom: 0,
      backgroundColor: colors.background + 'E6',
      alignItems: 'center',
      justifyContent: 'center',
      zIndex: 1000,
    },
  });

  return (
    <Modal visible={visible} animationType="slide" presentationStyle="pageSheet">
      <View style={styles.container}>
        {/* Header */}
        <View style={styles.header}>
          <Text style={styles.headerTitle}>🔄 System Refresh</Text>
          <TouchableOpacity style={styles.closeButton} onPress={onClose}>
            <Ionicons name="close" size={24} color={colors.text} />
          </TouchableOpacity>
        </View>

        <ScrollView style={styles.content} showsVerticalScrollIndicator={false}>
          {/* Auto-Refresh Settings */}
          <View style={styles.section}>
            <Text style={styles.sectionTitle}>Auto-Refresh Settings</Text>
            
            <View style={styles.switchRow}>
              <View style={{ flex: 1 }}>
                <Text style={styles.switchLabel}>Auto-Refresh After Updates</Text>
                <Text style={styles.switchDescription}>
                  Automatically refresh system after app updates
                </Text>
              </View>
              <Switch
                value={autoRefreshEnabled}
                onValueChange={toggleAutoRefresh}
                thumbColor={colors.primary}
                trackColor={{ false: colors.border, true: colors.primary + '40' }}
              />
            </View>
          </View>

          {/* Current Status */}
          <View style={styles.section}>
            <Text style={styles.sectionTitle}>System Status</Text>
            
            <View style={styles.statusRow}>
              <Text style={styles.statusLabel}>Current Version:</Text>
              <Text style={styles.statusValue}>{updateStatus.currentVersion}</Text>
            </View>
            
            <View style={styles.statusRow}>
              <Text style={styles.statusLabel}>Last Update Check:</Text>
              <Text style={styles.statusValue}>
                {formatTime(updateStatus.lastCheckTime)}
              </Text>
            </View>
            
            <View style={styles.statusRow}>
              <Text style={styles.statusLabel}>Last Refresh:</Text>
              <Text style={styles.statusValue}>
                {formatTime(systemRefreshService.getLastRefreshTime())}
              </Text>
            </View>

            {updateStatus.updateAvailable && (
              <View style={styles.statusRow}>
                <Text style={[styles.statusLabel, { color: colors.primary }]}>
                  Update Available:
                </Text>
                <Text style={[styles.statusValue, { color: colors.primary }]}>
                  {updateStatus.availableVersion || 'Yes'}
                </Text>
              </View>
            )}
          </View>

          {/* Progress Display */}
          {(isRefreshing || updateStatus.isUpdating) && refreshProgress && (
            <View style={styles.progressSection}>
              <Text style={styles.progressTitle}>
                {refreshProgress.stage}: {refreshProgress.message}
              </Text>
              <View style={styles.progressBar}>
                <View 
                  style={[
                    styles.progressFill, 
                    { width: `${refreshProgress.progress}%` }
                  ]} 
                />
              </View>
              <Text style={styles.progressText}>
                {formatProgress(refreshProgress.progress)}
              </Text>
            </View>
          )}

          {/* Quick Actions */}
          <View style={styles.section}>
            <Text style={styles.sectionTitle}>Quick Actions</Text>
            
            <View style={styles.buttonRow}>
              <TouchableOpacity
                style={[styles.button, styles.buttonSecondary]}
                onPress={handleQuickRefresh}
                disabled={isRefreshing || updateStatus.isUpdating}
              >
                <Ionicons name="refresh" size={20} color={colors.text} />
                <Text style={[styles.buttonText, styles.buttonTextSecondary]}>
                  Quick Refresh
                </Text>
              </TouchableOpacity>
              
              <TouchableOpacity
                style={styles.button}
                onPress={handleCheckForUpdates}
                disabled={updateStatus.isChecking || updateStatus.isUpdating}
              >
                <Ionicons name="cloud-download" size={20} color={colors.background} />
                <Text style={styles.buttonText}>Check Updates</Text>
              </TouchableOpacity>
            </View>
          </View>

          {/* Advanced Options */}
          <TouchableOpacity 
            style={styles.advancedToggle}
            onPress={() => setShowAdvancedOptions(!showAdvancedOptions)}
          >
            <Ionicons 
              name={showAdvancedOptions ? 'chevron-up' : 'chevron-down'} 
              size={16} 
              color={colors.primary} 
            />
            <Text style={styles.advancedToggleText}>Advanced Options</Text>
          </TouchableOpacity>

          {showAdvancedOptions && (
            <View style={styles.section}>
              <Text style={styles.sectionTitle}>Advanced Refresh Options</Text>
              
              <View style={styles.buttonRow}>
                <TouchableOpacity
                  style={styles.button}
                  onPress={handleFullRefresh}
                  disabled={isRefreshing || updateStatus.isUpdating}
                >
                  <Ionicons name="sync" size={20} color={colors.background} />
                  <Text style={styles.buttonText}>Full Refresh</Text>
                </TouchableOpacity>
              </View>

              <View style={[styles.buttonRow, { marginTop: 12 }]}>
                <TouchableOpacity
                  style={[styles.button, styles.buttonDanger]}
                  onPress={handleEmergencyRefresh}
                  disabled={isRefreshing || updateStatus.isUpdating}
                >
                  <Ionicons name="warning" size={20} color={colors.background} />
                  <Text style={styles.buttonText}>Emergency Refresh</Text>
                </TouchableOpacity>
              </View>

              <Text style={styles.switchDescription}>
                ⚠️ Emergency refresh should only be used when the app is not functioning properly.
              </Text>
            </View>
          )}

          <Text style={styles.versionInfo}>
            Kagema FM Enhanced • System Refresh Manager v1.0
          </Text>
        </ScrollView>

        {/* Loading Overlay */}
        {(isRefreshing || updateStatus.isUpdating) && (
          <View style={styles.loadingOverlay}>
            <ActivityIndicator size="large" color={colors.primary} />
            <Text style={[styles.progressTitle, { marginTop: 16, textAlign: 'center' }]}>
              {refreshProgress?.message || 'Processing...'}
            </Text>
          </View>
        )}
      </View>
    </Modal>
  );
};