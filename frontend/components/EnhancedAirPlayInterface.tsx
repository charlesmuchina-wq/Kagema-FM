import React, { useState, useEffect } from 'react';
import { 
  View, 
  Text, 
  StyleSheet, 
  TouchableOpacity, 
  ScrollView, 
  Alert,
  Modal,
  Platform
} from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import enhancedAirPlay2Service, { 
  AirPlay2Device, 
  AirPlay2Group, 
  AirPlay2State,
  StreamingOptions 
} from '../services/EnhancedAirPlay2Service';

interface EnhancedAirPlayInterfaceProps {
  currentlyPlaying?: {
    title: string;
    artist: string;
    stream: string;
  };
  onDeviceChange?: (deviceId: string) => void;
  onGroupChange?: (groupId: string) => void;
}

/**
 * Enhanced AirPlay Interface Component
 * 
 * Features:
 * - Multi-room audio device management
 * - Seamless device switching during playback
 * - Group creation and management for synchronized playback
 * - Location-aware device suggestions
 * - High-quality streaming options (lossless support)
 * - Visual device status and connection indicators
 */
export const EnhancedAirPlayInterface: React.FC<EnhancedAirPlayInterfaceProps> = ({
  currentlyPlaying,
  onDeviceChange,
  onGroupChange
}) => {
  const [airPlayState, setAirPlayState] = useState<AirPlay2State>(enhancedAirPlay2Service.getState());
  const [showDevicePicker, setShowDevicePicker] = useState(false);
  const [showGroupCreator, setShowGroupCreator] = useState(false);
  const [selectedDevicesForGroup, setSelectedDevicesForGroup] = useState<string[]>([]);
  const [newGroupName, setNewGroupName] = useState('');
  const [streamingQuality, setStreamingQuality] = useState<'standard' | 'high' | 'lossless'>('high');

  useEffect(() => {
    // Listen for AirPlay state changes
    const unsubscribe = enhancedAirPlay2Service.addListener(setAirPlayState);

    // Initial device discovery
    enhancedAirPlay2Service.discoverDevices();

    return () => {
      unsubscribe();
    };
  }, []);

  /**
   * Connect to a specific AirPlay device
   */
  const handleConnectDevice = async (deviceId: string) => {
    try {
      const options: Partial<StreamingOptions> = {
        quality: streamingQuality,
        enableMultiRoom: true,
        volume: 0.8
      };

      const success = await enhancedAirPlay2Service.connectToDevice(deviceId, options);
      
      if (success) {
        Alert.alert('✅ Connected', 'Successfully connected to AirPlay device');
        onDeviceChange?.(deviceId);
      } else {
        Alert.alert('❌ Connection Failed', 'Could not connect to the selected device');
      }
    } catch (error) {
      Alert.alert('❌ Error', `Connection error: ${error instanceof Error ? error.message : 'Unknown error'}`);
    }
  };

  /**
   * Switch streaming between devices seamlessly
   */
  const handleSwitchDevice = async (fromDeviceId: string, toDeviceId: string) => {
    try {
      const success = await enhancedAirPlay2Service.switchDevice(fromDeviceId, toDeviceId);
      
      if (success) {
        Alert.alert('🔄 Switched', 'Audio output switched successfully');
        onDeviceChange?.(toDeviceId);
      } else {
        Alert.alert('❌ Switch Failed', 'Could not switch to the selected device');
      }
    } catch (error) {
      Alert.alert('❌ Error', `Switch error: ${error instanceof Error ? error.message : 'Unknown error'}`);
    }
  };

  /**
   * Create multi-room audio group
   */
  const handleCreateGroup = async () => {
    if (selectedDevicesForGroup.length < 2) {
      Alert.alert('⚠️ Selection Required', 'Please select at least 2 devices for multi-room audio');
      return;
    }

    if (!newGroupName.trim()) {
      Alert.alert('⚠️ Name Required', 'Please enter a name for the group');
      return;
    }

    try {
      const groupId = await enhancedAirPlay2Service.createMultiRoomGroup(
        selectedDevicesForGroup, 
        newGroupName.trim()
      );
      
      if (groupId) {
        Alert.alert('✅ Group Created', `Multi-room group "${newGroupName}" created successfully`);
        setShowGroupCreator(false);
        setSelectedDevicesForGroup([]);
        setNewGroupName('');
        onGroupChange?.(groupId);
      } else {
        Alert.alert('❌ Creation Failed', 'Could not create multi-room group');
      }
    } catch (error) {
      Alert.alert('❌ Error', `Group creation error: ${error instanceof Error ? error.message : 'Unknown error'}`);
    }
  };

  /**
   * Adjust volume for device or group
   */
  const handleVolumeChange = async (targetId: string, newVolume: number) => {
    try {
      await enhancedAirPlay2Service.setVolume(targetId, newVolume);
    } catch (error) {
      console.error('Volume change error:', error);
    }
  };

  /**
   * Present enhanced AirPlay picker
   */
  const handlePresentAirPlayPicker = async () => {
    try {
      await enhancedAirPlay2Service.presentEnhancedAirPlayPicker();
    } catch (error) {
      console.error('AirPlay picker error:', error);
    }
  };

  /**
   * Get device type icon
   */
  const getDeviceIcon = (device: AirPlay2Device): string => {
    switch (device.type) {
      case 'apple_tv': return 'tv';
      case 'homepod': return 'musical-notes-circle';
      case 'smart_speaker': return 'radio';
      case 'audio_system': return 'car-sport';
      default: return 'bluetooth';
    }
  };

  /**
   * Get audio quality indicator
   */
  const getQualityIndicator = (quality: string): string => {
    switch (quality) {
      case 'lossless': return '🔊';
      case 'high': return '🎵';
      default: return '🎼';
    }
  };

  if (!airPlayState.isAvailable) {
    return (
      <View style={styles.unavailableContainer}>
        <Ionicons name="phone-portrait-outline" size={48} color="#666" />
        <Text style={styles.unavailableText}>
          Enhanced AirPlay is only available on iOS devices
        </Text>
      </View>
    );
  }

  return (
    <ScrollView style={styles.container}>
      {/* Header */}
      <View style={styles.header}>
        <Ionicons name="wifi" size={32} color="#007AFF" />
        <Text style={styles.title}>Enhanced AirPlay 2</Text>
        <Text style={styles.subtitle}>Multi-room audio streaming</Text>
      </View>

      {/* Currently Playing Section */}
      {currentlyPlaying && (
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>🎵 Now Playing</Text>
          <View style={styles.nowPlayingCard}>
            <Text style={styles.trackTitle}>{currentlyPlaying.title}</Text>
            <Text style={styles.trackArtist}>{currentlyPlaying.artist}</Text>
            <View style={styles.connectedDevicesCount}>
              <Ionicons name="wifi" size={16} color="#007AFF" />
              <Text style={styles.connectedCount}>
                {airPlayState.connectedDevices.length} device(s) connected
              </Text>
            </View>
          </View>
        </View>
      )}

      {/* Quick Actions */}
      <View style={styles.section}>
        <Text style={styles.sectionTitle}>🎛️ Quick Actions</Text>
        
        <View style={styles.quickActionsRow}>
          <TouchableOpacity 
            style={styles.quickActionButton}
            onPress={() => setShowDevicePicker(true)}
          >
            <Ionicons name="list" size={24} color="#007AFF" />
            <Text style={styles.quickActionText}>Device Picker</Text>
          </TouchableOpacity>

          <TouchableOpacity 
            style={styles.quickActionButton}
            onPress={() => setShowGroupCreator(true)}
          >
            <Ionicons name="people" size={24} color="#007AFF" />
            <Text style={styles.quickActionText}>Create Group</Text>
          </TouchableOpacity>

          <TouchableOpacity 
            style={styles.quickActionButton}
            onPress={handlePresentAirPlayPicker}
          >
            <Ionicons name="options" size={24} color="#007AFF" />
            <Text style={styles.quickActionText}>Native Picker</Text>
          </TouchableOpacity>
        </View>
      </View>

      {/* Available Devices */}
      <View style={styles.section}>
        <Text style={styles.sectionTitle}>📱 Available Devices</Text>
        
        {airPlayState.availableDevices.length === 0 ? (
          <View style={styles.emptyState}>
            <Ionicons name="search" size={32} color="#666" />
            <Text style={styles.emptyText}>No AirPlay devices found</Text>
            <Text style={styles.emptySubtext}>Make sure devices are powered on and connected to the same network</Text>
          </View>
        ) : (
          airPlayState.availableDevices.map((device) => (
            <View key={device.id} style={styles.deviceCard}>
              <View style={styles.deviceInfo}>
                <View style={styles.deviceHeader}>
                  <Ionicons 
                    name={getDeviceIcon(device)} 
                    size={24} 
                    color={device.isConnected ? '#007AFF' : '#666'} 
                  />
                  <View style={styles.deviceDetails}>
                    <Text style={styles.deviceName}>{device.name}</Text>
                    <View style={styles.deviceMeta}>
                      <Text style={styles.deviceLocation}>{device.location}</Text>
                      <Text style={styles.deviceQuality}>
                        {getQualityIndicator(device.audioQuality)} {device.audioQuality}
                      </Text>
                    </View>
                  </View>
                </View>
                
                <View style={styles.deviceControls}>
                  {device.isConnected ? (
                    <View style={styles.connectedIndicator}>
                      <Ionicons name="checkmark-circle" size={20} color="#28a745" />
                      <Text style={styles.connectedText}>Connected</Text>
                    </View>
                  ) : (
                    <TouchableOpacity
                      style={styles.connectButton}
                      onPress={() => handleConnectDevice(device.id)}
                    >
                      <Text style={styles.connectButtonText}>Connect</Text>
                    </TouchableOpacity>
                  )}
                </View>
              </View>
              
              {device.isConnected && (
                <View style={styles.deviceExtended}>
                  <View style={styles.volumeControl}>
                    <Ionicons name="volume-medium" size={16} color="#666" />
                    <Text style={styles.volumeText}>{device.volume}%</Text>
                  </View>
                  
                  {device.supportsMultiRoom && (
                    <View style={styles.multiRoomBadge}>
                      <Text style={styles.multiRoomText}>Multi-room</Text>
                    </View>
                  )}
                  
                  {device.batteryLevel && (
                    <View style={styles.batteryIndicator}>
                      <Ionicons name="battery-half" size={16} color="#666" />
                      <Text style={styles.batteryText}>{device.batteryLevel}%</Text>
                    </View>
                  )}
                </View>
              )}
            </View>
          ))
        )}
      </View>

      {/* Active Groups */}
      {airPlayState.activeGroups.length > 0 && (
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>👥 Multi-room Groups</Text>
          
          {airPlayState.activeGroups.map((group) => (
            <View key={group.id} style={styles.groupCard}>
              <View style={styles.groupHeader}>
                <Ionicons name="people" size={24} color="#007AFF" />
                <View style={styles.groupInfo}>
                  <Text style={styles.groupName}>{group.name}</Text>
                  <Text style={styles.groupDeviceCount}>
                    {group.devices.length} devices • Volume {group.volume}%
                  </Text>
                </View>
                {group.isPlaying && (
                  <View style={styles.playingIndicator}>
                    <Ionicons name="musical-notes" size={16} color="#28a745" />
                  </View>
                )}
              </View>
              
              <View style={styles.groupDevices}>
                {group.devices.map((device, index) => (
                  <View key={device.id} style={styles.groupDeviceItem}>
                    <Ionicons name={getDeviceIcon(device)} size={16} color="#666" />
                    <Text style={styles.groupDeviceName}>{device.name}</Text>
                  </View>
                ))}
              </View>
            </View>
          ))}
        </View>
      )}

      {/* Streaming Quality Settings */}
      <View style={styles.section}>
        <Text style={styles.sectionTitle}>🔊 Streaming Quality</Text>
        
        <View style={styles.qualityOptions}>
          {(['standard', 'high', 'lossless'] as const).map((quality) => (
            <TouchableOpacity
              key={quality}
              style={[
                styles.qualityOption,
                streamingQuality === quality && styles.qualityOptionActive
              ]}
              onPress={() => setStreamingQuality(quality)}
            >
              <Text style={[
                styles.qualityText,
                streamingQuality === quality && styles.qualityTextActive
              ]}>
                {getQualityIndicator(quality)} {quality.charAt(0).toUpperCase() + quality.slice(1)}
              </Text>
            </TouchableOpacity>
          ))}
        </View>
      </View>

      {/* Device Picker Modal */}
      <Modal
        visible={showDevicePicker}
        animationType="slide"
        presentationStyle="pageSheet"
      >
        <View style={styles.modalContainer}>
          <View style={styles.modalHeader}>
            <Text style={styles.modalTitle}>Select AirPlay Device</Text>
            <TouchableOpacity onPress={() => setShowDevicePicker(false)}>
              <Ionicons name="close" size={24} color="#666" />
            </TouchableOpacity>
          </View>
          
          <ScrollView style={styles.modalContent}>
            {airPlayState.availableDevices.map((device) => (
              <TouchableOpacity
                key={device.id}
                style={styles.modalDeviceItem}
                onPress={() => {
                  handleConnectDevice(device.id);
                  setShowDevicePicker(false);
                }}
              >
                <Ionicons name={getDeviceIcon(device)} size={24} color="#007AFF" />
                <View style={styles.modalDeviceInfo}>
                  <Text style={styles.modalDeviceName}>{device.name}</Text>
                  <Text style={styles.modalDeviceDetails}>
                    {device.location} • {device.audioQuality}
                  </Text>
                </View>
                {device.isConnected && (
                  <Ionicons name="checkmark" size={24} color="#28a745" />
                )}
              </TouchableOpacity>
            ))}
          </ScrollView>
        </View>
      </Modal>

      {/* Group Creator Modal */}
      <Modal
        visible={showGroupCreator}
        animationType="slide"
        presentationStyle="pageSheet"
      >
        <View style={styles.modalContainer}>
          <View style={styles.modalHeader}>
            <Text style={styles.modalTitle}>Create Multi-room Group</Text>
            <TouchableOpacity onPress={() => setShowGroupCreator(false)}>
              <Ionicons name="close" size={24} color="#666" />
            </TouchableOpacity>
          </View>
          
          <ScrollView style={styles.modalContent}>
            <Text style={styles.modalSectionTitle}>Group Name</Text>
            {/* Note: In a real implementation, you would use TextInput here */}
            <Text style={styles.modalNote}>
              Group name input would be implemented with TextInput component
            </Text>
            
            <Text style={styles.modalSectionTitle}>Select Devices (2+ required)</Text>
            {airPlayState.availableDevices
              .filter(device => device.supportsMultiRoom)
              .map((device) => (
                <TouchableOpacity
                  key={device.id}
                  style={[
                    styles.modalDeviceItem,
                    selectedDevicesForGroup.includes(device.id) && styles.modalDeviceItemSelected
                  ]}
                  onPress={() => {
                    if (selectedDevicesForGroup.includes(device.id)) {
                      setSelectedDevicesForGroup(prev => prev.filter(id => id !== device.id));
                    } else {
                      setSelectedDevicesForGroup(prev => [...prev, device.id]);
                    }
                  }}
                >
                  <Ionicons name={getDeviceIcon(device)} size={24} color="#007AFF" />
                  <View style={styles.modalDeviceInfo}>
                    <Text style={styles.modalDeviceName}>{device.name}</Text>
                    <Text style={styles.modalDeviceDetails}>{device.location}</Text>
                  </View>
                  {selectedDevicesForGroup.includes(device.id) && (
                    <Ionicons name="checkmark-circle" size={24} color="#007AFF" />
                  )}
                </TouchableOpacity>
              ))
            }
            
            <TouchableOpacity 
              style={[
                styles.createGroupButton,
                selectedDevicesForGroup.length < 2 && styles.createGroupButtonDisabled
              ]}
              onPress={handleCreateGroup}
              disabled={selectedDevicesForGroup.length < 2}
            >
              <Text style={styles.createGroupButtonText}>Create Group</Text>
            </TouchableOpacity>
          </ScrollView>
        </View>
      </Modal>
    </ScrollView>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f8f9fa',
  },
  unavailableContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    padding: 32,
    backgroundColor: '#f8f9fa',
  },
  unavailableText: {
    marginTop: 16,
    fontSize: 16,
    color: '#666',
    textAlign: 'center',
    lineHeight: 24,
  },
  header: {
    alignItems: 'center',
    padding: 24,
    backgroundColor: 'white',
    borderBottomWidth: 1,
    borderBottomColor: '#e1e8ed',
  },
  title: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#1d1d1d',
    marginTop: 8,
  },
  subtitle: {
    fontSize: 14,
    color: '#666',
    marginTop: 4,
  },
  section: {
    backgroundColor: 'white',
    marginTop: 12,
    paddingHorizontal: 16,
    paddingVertical: 20,
  },
  sectionTitle: {
    fontSize: 18,
    fontWeight: '600',
    color: '#1d1d1d',
    marginBottom: 16,
  },
  nowPlayingCard: {
    backgroundColor: '#f8f9fa',
    padding: 16,
    borderRadius: 12,
    borderWidth: 1,
    borderColor: '#e1e8ed',
  },
  trackTitle: {
    fontSize: 16,
    fontWeight: '600',
    color: '#1d1d1d',
    marginBottom: 4,
  },
  trackArtist: {
    fontSize: 14,
    color: '#666',
    marginBottom: 8,
  },
  connectedDevicesCount: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  connectedCount: {
    fontSize: 12,
    color: '#007AFF',
    marginLeft: 4,
  },
  quickActionsRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
  },
  quickActionButton: {
    flex: 1,
    alignItems: 'center',
    padding: 12,
    marginHorizontal: 4,
    backgroundColor: '#f8f9fa',
    borderRadius: 8,
    borderWidth: 1,
    borderColor: '#e1e8ed',
  },
  quickActionText: {
    fontSize: 12,
    color: '#007AFF',
    marginTop: 4,
    fontWeight: '500',
  },
  emptyState: {
    alignItems: 'center',
    padding: 32,
  },
  emptyText: {
    fontSize: 16,
    color: '#666',
    marginTop: 8,
    fontWeight: '500',
  },
  emptySubtext: {
    fontSize: 14,
    color: '#999',
    marginTop: 4,
    textAlign: 'center',
    lineHeight: 20,
  },
  deviceCard: {
    backgroundColor: '#f8f9fa',
    borderRadius: 12,
    padding: 16,
    marginBottom: 12,
    borderWidth: 1,
    borderColor: '#e1e8ed',
  },
  deviceInfo: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'flex-start',
  },
  deviceHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    flex: 1,
  },
  deviceDetails: {
    marginLeft: 12,
    flex: 1,
  },
  deviceName: {
    fontSize: 16,
    fontWeight: '600',
    color: '#1d1d1d',
  },
  deviceMeta: {
    flexDirection: 'row',
    alignItems: 'center',
    marginTop: 2,
  },
  deviceLocation: {
    fontSize: 12,
    color: '#666',
    marginRight: 12,
  },
  deviceQuality: {
    fontSize: 12,
    color: '#007AFF',
  },
  deviceControls: {
    marginLeft: 12,
  },
  connectedIndicator: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  connectedText: {
    fontSize: 12,
    color: '#28a745',
    marginLeft: 4,
    fontWeight: '500',
  },
  connectButton: {
    backgroundColor: '#007AFF',
    paddingHorizontal: 16,
    paddingVertical: 8,
    borderRadius: 6,
  },
  connectButtonText: {
    color: 'white',
    fontSize: 12,
    fontWeight: '600',
  },
  deviceExtended: {
    flexDirection: 'row',
    alignItems: 'center',
    marginTop: 12,
    paddingTop: 12,
    borderTopWidth: 1,
    borderTopColor: '#e1e8ed',
  },
  volumeControl: {
    flexDirection: 'row',
    alignItems: 'center',
    marginRight: 16,
  },
  volumeText: {
    fontSize: 12,
    color: '#666',
    marginLeft: 4,
  },
  multiRoomBadge: {
    backgroundColor: '#e3f2fd',
    paddingHorizontal: 6,
    paddingVertical: 2,
    borderRadius: 4,
    marginRight: 8,
  },
  multiRoomText: {
    fontSize: 10,
    color: '#007AFF',
    fontWeight: '500',
  },
  batteryIndicator: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  batteryText: {
    fontSize: 12,
    color: '#666',
    marginLeft: 4,
  },
  groupCard: {
    backgroundColor: '#f8f9fa',
    borderRadius: 12,
    padding: 16,
    marginBottom: 12,
    borderWidth: 1,
    borderColor: '#e1e8ed',
  },
  groupHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 12,
  },
  groupInfo: {
    marginLeft: 12,
    flex: 1,
  },
  groupName: {
    fontSize: 16,
    fontWeight: '600',
    color: '#1d1d1d',
  },
  groupDeviceCount: {
    fontSize: 12,
    color: '#666',
    marginTop: 2,
  },
  playingIndicator: {
    marginLeft: 8,
  },
  groupDevices: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: 8,
  },
  groupDeviceItem: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: 'white',
    paddingHorizontal: 8,
    paddingVertical: 4,
    borderRadius: 6,
  },
  groupDeviceName: {
    fontSize: 12,
    color: '#666',
    marginLeft: 4,
  },
  qualityOptions: {
    flexDirection: 'row',
    gap: 8,
  },
  qualityOption: {
    flex: 1,
    padding: 12,
    backgroundColor: '#f8f9fa',
    borderRadius: 8,
    borderWidth: 1,
    borderColor: '#e1e8ed',
    alignItems: 'center',
  },
  qualityOptionActive: {
    backgroundColor: '#007AFF',
    borderColor: '#007AFF',
  },
  qualityText: {
    fontSize: 14,
    color: '#666',
    fontWeight: '500',
  },
  qualityTextActive: {
    color: 'white',
  },
  modalContainer: {
    flex: 1,
    backgroundColor: 'white',
  },
  modalHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    padding: 16,
    borderBottomWidth: 1,
    borderBottomColor: '#e1e8ed',
  },
  modalTitle: {
    fontSize: 18,
    fontWeight: '600',
    color: '#1d1d1d',
  },
  modalContent: {
    flex: 1,
    padding: 16,
  },
  modalSectionTitle: {
    fontSize: 16,
    fontWeight: '600',
    color: '#1d1d1d',
    marginBottom: 12,
    marginTop: 16,
  },
  modalNote: {
    fontSize: 14,
    color: '#666',
    fontStyle: 'italic',
    marginBottom: 16,
  },
  modalDeviceItem: {
    flexDirection: 'row',
    alignItems: 'center',
    padding: 12,
    borderRadius: 8,
    marginBottom: 8,
    backgroundColor: '#f8f9fa',
  },
  modalDeviceItemSelected: {
    backgroundColor: '#e3f2fd',
    borderWidth: 2,
    borderColor: '#007AFF',
  },
  modalDeviceInfo: {
    marginLeft: 12,
    flex: 1,
  },
  modalDeviceName: {
    fontSize: 16,
    fontWeight: '500',
    color: '#1d1d1d',
  },
  modalDeviceDetails: {
    fontSize: 14,
    color: '#666',
    marginTop: 2,
  },
  createGroupButton: {
    backgroundColor: '#007AFF',
    padding: 16,
    borderRadius: 8,
    alignItems: 'center',
    marginTop: 24,
  },
  createGroupButtonDisabled: {
    backgroundColor: '#ccc',
  },
  createGroupButtonText: {
    color: 'white',
    fontSize: 16,
    fontWeight: '600',
  },
});

export default EnhancedAirPlayInterface;