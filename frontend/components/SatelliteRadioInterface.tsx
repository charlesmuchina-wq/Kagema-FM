import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  StyleSheet,
  TouchableOpacity,
  ScrollView,
  FlatList,
  Modal,
  ActivityIndicator,
  Alert,
  Dimensions,
} from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { useTheme } from '../contexts/ThemeContext';
import { 
  satelliteRadioService, 
  SatelliteChannel, 
  SatelliteProvider, 
  SatelliteConnection 
} from '../services/SatelliteRadioService';
import { shadowStyles } from '../utils/shadowStyles';

const { width } = Dimensions.get('window');

interface SatelliteRadioInterfaceProps {
  visible: boolean;
  onClose: () => void;
  onChannelSelect: (channel: SatelliteChannel) => void;
  currentChannel?: SatelliteChannel | null;
  userLocation?: [number, number];
}

export const SatelliteRadioInterface: React.FC<SatelliteRadioInterfaceProps> = ({
  visible,
  onClose,
  onChannelSelect,
  currentChannel,
  userLocation
}) => {
  const { colors } = useTheme();
  const [providers, setProviders] = useState<SatelliteProvider[]>([]);
  const [selectedProvider, setSelectedProvider] = useState<string>('all');
  const [connection, setConnection] = useState<SatelliteConnection | null>(null);
  const [loading, setLoading] = useState(true);
  const [connecting, setConnecting] = useState(false);
  const [activeTab, setActiveTab] = useState<'browse' | 'emergency' | 'coverage'>('browse');
  const [emergencyMode, setEmergencyMode] = useState(false);

  useEffect(() => {
    if (visible) {
      initializeSatelliteRadio();
    }
  }, [visible]);

  useEffect(() => {
    checkEmergencyMode();
  }, []);

  const initializeSatelliteRadio = async () => {
    try {
      setLoading(true);
      await satelliteRadioService.initialize();
      
      const providersList = satelliteRadioService.getProviders();
      setProviders(providersList);
      
      const satelliteConnection = satelliteRadioService.getSatelliteConnection();
      setConnection(satelliteConnection);
      
      console.log('🛰️ Satellite Radio initialized with', providersList.length, 'providers');
    } catch (error) {
      console.error('Error initializing Satellite Radio:', error);
      Alert.alert('Error', 'Failed to initialize satellite radio');
    } finally {
      setLoading(false);
    }
  };

  const checkEmergencyMode = async () => {
    const isEmergencyMode = await satelliteRadioService.isEmergencyModeEnabled();
    setEmergencyMode(isEmergencyMode);
  };

  const handleConnectSatellite = async () => {
    setConnecting(true);
    try {
      const connected = await satelliteRadioService.connectToSatellite(userLocation);
      
      if (connected) {
        const newConnection = satelliteRadioService.getSatelliteConnection();
        setConnection(newConnection);
        Alert.alert(
          'Satellite Connected',
          `Successfully connected to ${newConnection?.provider}\nSignal strength: ${newConnection?.signalStrength}%`,
          [{ text: 'OK' }]
        );
      } else {
        Alert.alert('Connection Failed', 'Unable to connect to satellite network');
      }
    } catch (error) {
      console.error('Satellite connection error:', error);
      Alert.alert('Connection Error', 'Failed to connect to satellite');
    } finally {
      setConnecting(false);
    }
  };

  const handleChannelPlay = (channel: SatelliteChannel) => {
    console.log('🛰️ Tuning to satellite channel:', channel.name);
    onChannelSelect(channel);
    
    Alert.alert(
      'Now Playing',
      `${channel.name} (Channel ${channel.number})\n${channel.description}\n\nProvider: ${channel.provider}\nQuality: ${channel.quality}`,
      [{ text: 'OK' }]
    );
  };

  const toggleEmergencyMode = async () => {
    try {
      if (emergencyMode) {
        await satelliteRadioService.disableEmergencyMode();
        setEmergencyMode(false);
        Alert.alert('Emergency Mode Disabled', 'Regular satellite channels restored');
      } else {
        await satelliteRadioService.enableEmergencyMode();
        setEmergencyMode(true);
        Alert.alert('Emergency Mode Enabled', 'Prioritizing emergency broadcasts');
      }
    } catch (error) {
      console.error('Error toggling emergency mode:', error);
    }
  };

  const getDisplayChannels = (): SatelliteChannel[] => {
    switch (activeTab) {
      case 'emergency':
        return satelliteRadioService.getEmergencyChannels();
      case 'coverage':
        return userLocation 
          ? satelliteRadioService.getCoverageForLocation(userLocation[0], userLocation[1])
          : [];
      case 'browse':
      default:
        if (selectedProvider === 'all') {
          return satelliteRadioService.getAvailableChannels(false); // Free channels only for demo
        }
        return satelliteRadioService.getChannelsByProvider(selectedProvider);
    }
  };

  const renderChannelCard = ({ item: channel }: { item: SatelliteChannel }) => {
    const isCurrentChannel = currentChannel?.id === channel.id;
    const isSubscriptionRequired = channel.subscriptionRequired;
    
    return (
      <View style={[
        styles.channelCard,
        { backgroundColor: colors.card, borderColor: colors.border },
        isCurrentChannel && { borderColor: colors.primary, borderWidth: 2 }
      ]}>
        <View style={styles.channelHeader}>
          <View style={styles.channelNumber}>
            <Text style={[styles.channelNumberText, { color: colors.background }]}>
              {channel.number}
            </Text>
          </View>
          
          <View style={styles.channelInfo}>
            <Text style={[styles.channelName, { color: colors.text }]}>{channel.name}</Text>
            <Text style={[styles.channelDescription, { color: colors.textSecondary }]}>
              {channel.description}
            </Text>
            
            <View style={styles.channelMeta}>
              <View style={[styles.genreTag, { backgroundColor: colors.primary + '20' }]}>
                <Text style={[styles.genreText, { color: colors.primary }]}>{channel.genre}</Text>
              </View>
              
              <View style={[styles.qualityTag, { backgroundColor: colors.success + '20' }]}>
                <Text style={[styles.qualityText, { color: colors.success }]}>{channel.quality}</Text>
              </View>
              
              {channel.emergencyBroadcast && (
                <View style={[styles.emergencyTag, { backgroundColor: '#ff4757' + '20' }]}>
                  <Ionicons name="alert-circle" size={12} color="#ff4757" />
                  <Text style={[styles.emergencyText, { color: '#ff4757' }]}>EMERGENCY</Text>
                </View>
              )}
            </View>
            
            <View style={styles.channelStats}>
              <Text style={[styles.providerText, { color: colors.textSecondary }]}>
                {channel.provider.toUpperCase()} • {channel.bitrate}
              </Text>
              {isSubscriptionRequired && (
                <Text style={[styles.subscriptionText, { color: colors.warning }]}>
                  • Subscription Required
                </Text>
              )}
            </View>
          </View>
          
          <TouchableOpacity
            style={[
              styles.playButton,
              { backgroundColor: isCurrentChannel ? colors.success : colors.primary },
              isSubscriptionRequired && !connection && { backgroundColor: colors.textSecondary }
            ]}
            onPress={() => handleChannelPlay(channel)}
            disabled={isSubscriptionRequired && !connection}
          >
            <Ionicons
              name={isCurrentChannel ? 'pause' : 'play'}
              size={20}
              color={colors.background}
            />
          </TouchableOpacity>
        </View>
      </View>
    );
  };

  const renderProviderTab = (provider: SatelliteProvider) => (
    <TouchableOpacity
      key={provider.id}
      style={[
        styles.providerTab,
        { backgroundColor: selectedProvider === provider.id ? colors.primary : colors.surface },
        { borderColor: colors.border }
      ]}
      onPress={() => setSelectedProvider(provider.id)}
    >
      <Text
        style={[
          styles.providerTabText,
          { color: selectedProvider === provider.id ? colors.background : colors.text }
        ]}
      >
        {provider.name}
      </Text>
    </TouchableOpacity>
  );

  const ConnectionStatus = () => (
    <View style={[styles.connectionStatus, { backgroundColor: colors.surface }]}>
      <View style={styles.connectionInfo}>
        <Ionicons 
          name={connection?.isConnected ? 'radio' : 'radio-outline'} 
          size={20} 
          color={connection?.isConnected ? colors.success : colors.textSecondary} 
        />
        <Text style={[styles.connectionText, { color: colors.text }]}>
          {connection ? `${connection.provider} • ${connection.signalStrength}%` : 'Not Connected'}
        </Text>
      </View>
      
      <TouchableOpacity
        style={[
          styles.connectButton,
          { backgroundColor: connection?.isConnected ? colors.success : colors.primary }
        ]}
        onPress={handleConnectSatellite}
        disabled={connecting}
      >
        {connecting ? (
          <ActivityIndicator size="small" color={colors.background} />
        ) : (
          <Text style={[styles.connectButtonText, { color: colors.background }]}>
            {connection?.isConnected ? 'Connected' : 'Connect'}
          </Text>
        )}
      </TouchableOpacity>
    </View>
  );

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
    headerActions: {
      flexDirection: 'row',
      gap: 12,
    },
    emergencyButton: {
      padding: 8,
      borderRadius: 8,
      backgroundColor: emergencyMode ? '#ff4757' : colors.surface,
    },
    closeButton: {
      padding: 8,
      borderRadius: 8,
      backgroundColor: colors.surface,
    },
    connectionStatus: {
      flexDirection: 'row',
      alignItems: 'center',
      justifyContent: 'space-between',
      padding: 16,
      borderBottomWidth: 1,
      borderBottomColor: colors.border,
    },
    connectionInfo: {
      flexDirection: 'row',
      alignItems: 'center',
      gap: 8,
    },
    connectionText: {
      fontSize: 14,
      fontWeight: '500',
    },
    connectButton: {
      paddingHorizontal: 16,
      paddingVertical: 8,
      borderRadius: 8,
      minWidth: 80,
      alignItems: 'center',
    },
    connectButtonText: {
      fontSize: 12,
      fontWeight: '600',
    },
    tabBar: {
      flexDirection: 'row',
      backgroundColor: colors.surface,
      paddingHorizontal: 16,
      paddingVertical: 8,
      borderBottomWidth: 1,
      borderBottomColor: colors.border,
    },
    tab: {
      flex: 1,
      alignItems: 'center',
      paddingVertical: 12,
      borderRadius: 8,
      marginHorizontal: 4,
    },
    activeTab: {
      backgroundColor: colors.primary,
    },
    tabText: {
      fontSize: 12,
      fontWeight: '600',
      marginTop: 4,
    },
    activeTabText: {
      color: colors.background,
    },
    providersContainer: {
      padding: 16,
      backgroundColor: colors.surface,
    },
    providersRow: {
      flexDirection: 'row',
      flexWrap: 'wrap',
      gap: 8,
    },
    providerTab: {
      paddingHorizontal: 12,
      paddingVertical: 8,
      borderRadius: 8,
      borderWidth: 1,
    },
    providerTabText: {
      fontSize: 12,
      fontWeight: '500',
    },
    content: {
      flex: 1,
    },
    channelCard: {
      margin: 12,
      borderRadius: 16,
      padding: 16,
      borderWidth: 1,
      ...shadowStyles.medium,
    },
    channelHeader: {
      flexDirection: 'row',
      alignItems: 'flex-start',
      gap: 12,
    },
    channelNumber: {
      width: 40,
      height: 40,
      borderRadius: 20,
      backgroundColor: colors.primary,
      alignItems: 'center',
      justifyContent: 'center',
    },
    channelNumberText: {
      fontSize: 16,
      fontWeight: '700',
    },
    channelInfo: {
      flex: 1,
    },
    channelName: {
      fontSize: 16,
      fontWeight: '600',
      marginBottom: 4,
    },
    channelDescription: {
      fontSize: 14,
      lineHeight: 20,
      marginBottom: 8,
    },
    channelMeta: {
      flexDirection: 'row',
      alignItems: 'center',
      marginBottom: 8,
      gap: 8,
      flexWrap: 'wrap',
    },
    genreTag: {
      paddingHorizontal: 8,
      paddingVertical: 4,
      borderRadius: 6,
    },
    genreText: {
      fontSize: 10,
      fontWeight: '600',
      textTransform: 'uppercase',
    },
    qualityTag: {
      paddingHorizontal: 8,
      paddingVertical: 4,
      borderRadius: 6,
    },
    qualityText: {
      fontSize: 10,
      fontWeight: '600',
      textTransform: 'uppercase',
    },
    emergencyTag: {
      flexDirection: 'row',
      alignItems: 'center',
      paddingHorizontal: 6,
      paddingVertical: 4,
      borderRadius: 6,
      gap: 4,
    },
    emergencyText: {
      fontSize: 9,
      fontWeight: '700',
    },
    channelStats: {
      flexDirection: 'row',
      alignItems: 'center',
      gap: 4,
    },
    providerText: {
      fontSize: 11,
    },
    subscriptionText: {
      fontSize: 11,
      fontWeight: '500',
    },
    playButton: {
      width: 48,
      height: 48,
      borderRadius: 24,
      alignItems: 'center',
      justifyContent: 'center',
    },
    loadingContainer: {
      flex: 1,
      alignItems: 'center',
      justifyContent: 'center',
    },
    loadingText: {
      marginTop: 16,
      fontSize: 16,
      color: colors.textSecondary,
    },
    emptyContainer: {
      flex: 1,
      alignItems: 'center',
      justifyContent: 'center',
      padding: 32,
    },
    emptyText: {
      fontSize: 16,
      color: colors.textSecondary,
      textAlign: 'center',
      marginTop: 16,
    },
  });

  if (loading) {
    return (
      <Modal visible={visible} animationType="slide" presentationStyle="pageSheet">
        <View style={styles.container}>
          <View style={styles.header}>
            <Text style={styles.headerTitle}>🛰️ Satellite Radio</Text>
            <TouchableOpacity style={styles.closeButton} onPress={onClose}>
              <Ionicons name="close" size={24} color={colors.text} />
            </TouchableOpacity>
          </View>
          <View style={styles.loadingContainer}>
            <ActivityIndicator size="large" color={colors.primary} />
            <Text style={styles.loadingText}>Connecting to satellites...</Text>
          </View>
        </View>
      </Modal>
    );
  }

  return (
    <Modal visible={visible} animationType="slide" presentationStyle="pageSheet">
      <View style={styles.container}>
        {/* Header */}
        <View style={styles.header}>
          <Text style={styles.headerTitle}>🛰️ Satellite Radio</Text>
          <View style={styles.headerActions}>
            <TouchableOpacity 
              style={styles.emergencyButton} 
              onPress={toggleEmergencyMode}
            >
              <Ionicons 
                name="alert-circle" 
                size={20} 
                color={emergencyMode ? colors.background : colors.text} 
              />
            </TouchableOpacity>
            <TouchableOpacity style={styles.closeButton} onPress={onClose}>
              <Ionicons name="close" size={24} color={colors.text} />
            </TouchableOpacity>
          </View>
        </View>

        {/* Connection Status */}
        <ConnectionStatus />

        {/* Tab Bar */}
        <View style={styles.tabBar}>
          {[
            { id: 'browse', label: 'Browse', icon: 'library' },
            { id: 'emergency', label: 'Emergency', icon: 'alert-circle' },
            { id: 'coverage', label: 'Local Coverage', icon: 'location' },
          ].map((tab) => (
            <TouchableOpacity
              key={tab.id}
              style={[
                styles.tab,
                activeTab === tab.id && styles.activeTab,
              ]}
              onPress={() => setActiveTab(tab.id as any)}
            >
              <Ionicons
                name={tab.icon as any}
                size={20}
                color={activeTab === tab.id ? colors.background : colors.textSecondary}
              />
              <Text
                style={[
                  styles.tabText,
                  { color: activeTab === tab.id ? colors.background : colors.textSecondary },
                  activeTab === tab.id && styles.activeTabText,
                ]}
              >
                {tab.label}
              </Text>
            </TouchableOpacity>
          ))}
        </View>

        {/* Provider Filter for Browse tab */}
        {activeTab === 'browse' && (
          <View style={styles.providersContainer}>
            <ScrollView horizontal showsHorizontalScrollIndicator={false}>
              <View style={styles.providersRow}>
                <TouchableOpacity
                  style={[
                    styles.providerTab,
                    { backgroundColor: selectedProvider === 'all' ? colors.primary : colors.surface },
                    { borderColor: colors.border }
                  ]}
                  onPress={() => setSelectedProvider('all')}
                >
                  <Text
                    style={[
                      styles.providerTabText,
                      { color: selectedProvider === 'all' ? colors.background : colors.text }
                    ]}
                  >
                    All Providers
                  </Text>
                </TouchableOpacity>
                {providers.map(renderProviderTab)}
              </View>
            </ScrollView>
          </View>
        )}

        {/* Channel List */}
        <View style={styles.content}>
          <FlatList
            data={getDisplayChannels()}
            renderItem={renderChannelCard}
            keyExtractor={(item) => item.id}
            showsVerticalScrollIndicator={false}
            ListEmptyComponent={
              <View style={styles.emptyContainer}>
                <Ionicons name="satellite" size={64} color={colors.textSecondary} />
                <Text style={styles.emptyText}>
                  {activeTab === 'emergency'
                    ? 'No emergency broadcasts active'
                    : activeTab === 'coverage' && !userLocation
                    ? 'Location access required for coverage info'
                    : 'No satellite channels available'
                  }
                </Text>
              </View>
            }
          />
        </View>
      </View>
    </Modal>
  );
};