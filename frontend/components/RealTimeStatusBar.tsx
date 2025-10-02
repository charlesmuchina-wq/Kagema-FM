import React from 'react';
import {
  View,
  Text,
  StyleSheet,
  TouchableOpacity,
  Alert,
  ActivityIndicator,
  Platform,
} from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { useTheme } from '../contexts/ThemeContext';
import { useRealTime } from '../services/RealTimeService';

interface RealTimeStatusBarProps {
  showFullStatus?: boolean;
  onStatusPress?: () => void;
}

export const RealTimeStatusBar: React.FC<RealTimeStatusBarProps> = ({
  showFullStatus = false,
  onStatusPress
}) => {
  const { colors } = useTheme();
  const {
    currentTime,
    timezone,
    internetStatus,
    connectionType,
    lastSync,
    externalSourcesStatus,
    changedSources,
    forceCheckSources,
    triggerInternetRestorationCheck,
    getFormattedTime,
    getFormattedDate
  } = useRealTime();

  const getConnectionIcon = () => {
    switch (internetStatus) {
      case 'online':
        return connectionType.includes('wifi') || connectionType === 'web' ? 'wifi' : 'cellular';
      case 'offline':
        return 'wifi-off';
      case 'connecting':
        return 'sync';
      default:
        return 'help-circle';
    }
  };

  const getConnectionColor = () => {
    switch (internetStatus) {
      case 'online':
        return '#10b981'; // green
      case 'offline':
        return '#ef4444'; // red
      case 'connecting':
        return '#f59e0b'; // yellow
      default:
        return colors.textSecondary;
    }
  };

  const getSourceStatusIcon = () => {
    switch (externalSourcesStatus) {
      case 'checking':
        return 'sync';
      case 'updated':
        return 'checkmark-circle';
      case 'unchanged':
        return 'checkmark';
      case 'error':
        return 'warning';
      default:
        return 'help-circle';
    }
  };

  const getSourceStatusColor = () => {
    switch (externalSourcesStatus) {
      case 'checking':
        return '#f59e0b'; // yellow
      case 'updated':
        return '#8b5cf6'; // purple
      case 'unchanged':
        return '#10b981'; // green
      case 'error':
        return '#ef4444'; // red
      default:
        return colors.textSecondary;
    }
  };

  const handleStatusPress = () => {
    if (onStatusPress) {
      onStatusPress();
    } else {
      // Show detailed status
      const lastSyncText = lastSync ? lastSync.toLocaleTimeString() : 'Never';
      const changedSourcesText = changedSources.length > 0 
        ? `\n\nUpdated sources:\n${changedSources.join('\n')}`
        : '';
      
      Alert.alert(
        'Real-Time Status',
        `Connection: ${internetStatus.toUpperCase()} (${connectionType})
Time Zone: ${timezone}
Last Sync: ${lastSyncText}
External Sources: ${externalSourcesStatus.toUpperCase()}${changedSourcesText}`,
        [
          { text: 'OK', style: 'default' },
          {
            text: 'Check Sources',
            onPress: async () => {
              const hasChanges = await forceCheckSources();
              Alert.alert(
                'Source Check Complete',
                hasChanges ? 'Sources have been updated!' : 'No changes detected'
              );
            }
          },
          internetStatus === 'offline' && {
            text: 'Test Restoration',
            onPress: triggerInternetRestorationCheck
          }
        ].filter(Boolean) as any
      );
    }
  };

  const styles = StyleSheet.create({
    container: {
      flexDirection: 'row',
      alignItems: 'center',
      justifyContent: 'space-between',
      backgroundColor: colors.surface,
      paddingHorizontal: 16,
      paddingVertical: showFullStatus ? 12 : 8,
      borderBottomWidth: 1,
      borderBottomColor: colors.border,
    },
    leftSection: {
      flexDirection: 'row',
      alignItems: 'center',
      flex: 1,
    },
    rightSection: {
      flexDirection: 'row',
      alignItems: 'center',
    },
    timeContainer: {
      alignItems: showFullStatus ? 'flex-start' : 'center',
    },
    timeText: {
      fontSize: showFullStatus ? 18 : 14,
      fontWeight: '600',
      color: colors.text,
      fontFamily: Platform.OS === 'ios' ? 'Menlo' : 'monospace',
    },
    dateText: {
      fontSize: 12,
      color: colors.textSecondary,
      marginTop: showFullStatus ? 2 : 0,
    },
    timezoneText: {
      fontSize: 10,
      color: colors.textSecondary,
      marginTop: 1,
    },
    statusSection: {
      flexDirection: 'row',
      alignItems: 'center',
      marginLeft: 16,
    },
    statusItem: {
      flexDirection: 'row',
      alignItems: 'center',
      marginLeft: showFullStatus ? 16 : 8,
    },
    statusLabel: {
      fontSize: 11,
      color: colors.textSecondary,
      marginLeft: 4,
    },
    updateIndicator: {
      position: 'absolute',
      top: -2,
      right: -2,
      width: 8,
      height: 8,
      borderRadius: 4,
      backgroundColor: '#8b5cf6',
    },
    pulseDot: {
      width: 6,
      height: 6,
      borderRadius: 3,
      backgroundColor: getConnectionColor(),
      marginLeft: 4,
    },
  });

  return (
    <TouchableOpacity 
      style={styles.container} 
      onPress={handleStatusPress}
      activeOpacity={0.7}
    >
      <View style={styles.leftSection}>
        {/* Real-time clock */}
        <View style={styles.timeContainer}>
          <Text style={styles.timeText}>
            {getFormattedTime(showFullStatus ? '24h' : '12h')}
          </Text>
          {showFullStatus && (
            <>
              <Text style={styles.dateText}>{getFormattedDate()}</Text>
              <Text style={styles.timezoneText}>{timezone}</Text>
            </>
          )}
        </View>
      </View>

      <View style={styles.rightSection}>
        {/* Connection Status */}
        <View style={styles.statusItem}>
          <Ionicons 
            name={getConnectionIcon() as any} 
            size={showFullStatus ? 18 : 14} 
            color={getConnectionColor()} 
          />
          {internetStatus === 'connecting' && (
            <ActivityIndicator 
              size="small" 
              color={getConnectionColor()} 
              style={{ marginLeft: 4 }}
            />
          )}
          {showFullStatus && (
            <Text style={styles.statusLabel}>
              {internetStatus.toUpperCase()}
            </Text>
          )}
        </View>

        {/* External Sources Status */}
        <View style={styles.statusItem}>
          <Ionicons 
            name={getSourceStatusIcon() as any} 
            size={showFullStatus ? 16 : 12} 
            color={getSourceStatusColor()} 
          />
          {externalSourcesStatus === 'checking' && (
            <ActivityIndicator 
              size="small" 
              color={getSourceStatusColor()} 
              style={{ marginLeft: 2 }}
            />
          )}
          {externalSourcesStatus === 'updated' && (
            <View style={styles.updateIndicator} />
          )}
          {showFullStatus && (
            <Text style={styles.statusLabel}>
              SOURCES
            </Text>
          )}
        </View>

        {/* Live indicator */}
        <View style={styles.statusItem}>
          <View style={styles.pulseDot} />
          {showFullStatus && (
            <Text style={[styles.statusLabel, { color: getConnectionColor() }]}>
              LIVE
            </Text>
          )}
        </View>
      </View>
    </TouchableOpacity>
  );
};