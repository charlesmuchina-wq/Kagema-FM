import React, { useState, useEffect, useRef } from 'react';
import {
  View,
  Text,
  StyleSheet,
  TouchableOpacity,
  Modal,
  ScrollView,
  ActivityIndicator,
  Alert,
  Dimensions,
  Animated,
  Platform,
} from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { useTheme } from '../contexts/ThemeContext';
import AsyncStorage from '@react-native-async-storage/async-storage';

const { width, height } = Dimensions.get('window');

interface SatelliteChannel {
  id: string;
  number: number;
  name: string;
  category: string;
  description: string;
  genre: string;
  streamUrl: string;
  isOffline?: boolean;
  cached?: boolean;
}

interface SatelliteRadioProps {
  visible: boolean;
  onClose: () => void;
  onChannelSelect?: (channel: SatelliteChannel) => void;
  offlineMode?: boolean;
}

export const SatelliteRadio: React.FC<SatelliteRadioProps> = ({
  visible,
  onClose,
  onChannelSelect,
  offlineMode = false,
}) => {
  const { colors, isDark } = useTheme();
  
  // State
  const [channels, setChannels] = useState<SatelliteChannel[]>([]);
  const [currentChannel, setCurrentChannel] = useState<SatelliteChannel | null>(null);
  const [selectedCategory, setSelectedCategory] = useState<string>('All');
  const [isLoading, setIsLoading] = useState(false);
  const [satelliteConnected, setSatelliteConnected] = useState(false);
  const [connectionStrength, setConnectionStrength] = useState(0);
  const [channelNumber, setChannelNumber] = useState('');
  const [isScanning, setIsScanning] = useState(false);
  
  // Animations
  const pulseAnim = useRef(new Animated.Value(1)).current;
  const signalAnim = useRef(new Animated.Value(0)).current;
  
  // Categories
  const categories = [
    'All', 'Music', 'News', 'Sports', 'Talk', 'International', 'Comedy', 'Classical'
  ];

  useEffect(() => {
    if (visible) {
      initializeSatelliteRadio();
      startConnectionAnimation();
    }
    return () => {
      stopAnimations();
    };
  }, [visible]);

  const initializeSatelliteRadio = async () => {
    setIsLoading(true);
    try {
      console.log('📡 Initializing Satellite Radio...');
      
      // Simulate satellite connection
      await simulateConnection();
      
      // Load channels
      const satelliteChannels = await loadSatelliteChannels();
      setChannels(satelliteChannels);
      
      // Set default channel
      if (satelliteChannels.length > 0) {
        setCurrentChannel(satelliteChannels[0]);
      }
      
      console.log('✅ Satellite Radio initialized with', satelliteChannels.length, 'channels');
    } catch (error) {
      console.error('❌ Error initializing Satellite Radio:', error);
      Alert.alert('Connection Error', 'Failed to connect to satellite. Using cached channels.');
      
      // Load cached channels
      const cachedChannels = await getCachedChannels();
      setChannels(cachedChannels);
    } finally {
      setIsLoading(false);
    }
  };

  const simulateConnection = async (): Promise<void> => {
    return new Promise((resolve) => {
      let strength = 0;
      const connectionInterval = setInterval(() => {
        strength += Math.random() * 20;
        setConnectionStrength(Math.min(strength, 100));
        
        if (strength >= 80) {
          setSatelliteConnected(true);
          clearInterval(connectionInterval);
          resolve();
        }
      }, 200);
    });
  };

  const loadSatelliteChannels = async (): Promise<SatelliteChannel[]> => {
    // Simulate satellite channel data
    const satelliteChannels: SatelliteChannel[] = [
      // Music Channels
      {
        id: 'sat_001',
        number: 1,
        name: 'Kagema Hits',
        category: 'Music',
        description: 'Contemporary hits and popular music',
        genre: 'Pop/Rock',
        streamUrl: 'https://ice1.somafm.com/groovesalad-256-mp3',
        cached: !offlineMode
      },
      {
        id: 'sat_002',
        number: 2,
        name: 'Electronic Waves',
        category: 'Music',
        description: 'Electronic and ambient music',
        genre: 'Electronic',
        streamUrl: 'http://ice1.somafm.com/dronezone-256-mp3',
        cached: true
      },
      {
        id: 'sat_003',
        number: 3,
        name: 'Jazz Lounge',
        category: 'Music',
        description: 'Smooth jazz and lounge music',
        genre: 'Jazz',
        streamUrl: 'http://ice1.somafm.com/secretagent-256-mp3',
        cached: true
      },
      
      // News Channels
      {
        id: 'sat_101',
        number: 101,
        name: 'Global News',
        category: 'News',
        description: 'International news and current affairs',
        genre: 'News/Talk',
        streamUrl: 'https://stream.radioparadise.com/aac-320',
        cached: !offlineMode
      },
      {
        id: 'sat_102',
        number: 102,
        name: 'Business Update',
        category: 'News',
        description: 'Financial markets and business news',
        genre: 'Business',
        streamUrl: 'https://icecast.radiofrance.fr/fip-hifi.aac',
        cached: false,
        isOffline: offlineMode
      },
      
      // International
      {
        id: 'sat_201',
        number: 201,
        name: 'African Rhythms',
        category: 'International',
        description: 'Music from across Africa',
        genre: 'World Music',
        streamUrl: 'https://ice1.somafm.com/groovesalad-256-mp3',
        cached: true
      },
      {
        id: 'sat_202',
        number: 202,
        name: 'European Mix',
        category: 'International',
        description: 'Contemporary European music',
        genre: 'European',
        streamUrl: 'https://icecast.radiofrance.fr/fip-midfi.mp3',
        cached: !offlineMode
      },
      
      // Talk & Comedy
      {
        id: 'sat_301',
        number: 301,
        name: 'Comedy Central',
        category: 'Comedy',
        description: 'Stand-up comedy and humor',
        genre: 'Comedy',
        streamUrl: 'http://ice1.somafm.com/defcon-256-mp3',
        cached: true
      },
      
      // Classical
      {
        id: 'sat_401',
        number: 401,
        name: 'Classical Masters',
        category: 'Classical',
        description: 'Classical music masterpieces',
        genre: 'Classical',
        streamUrl: 'https://stream.radioparadise.com/mp3-192',
        cached: true
      },
      
      // Sports
      {
        id: 'sat_501',
        number: 501,
        name: 'Sports Talk',
        category: 'Sports',
        description: 'Sports news and commentary',
        genre: 'Sports',
        streamUrl: 'http://ice1.somafm.com/groovesalad-256-mp3',
        cached: false,
        isOffline: offlineMode
      }
    ];

    // Mark offline channels if in offline mode
    if (offlineMode) {
      satelliteChannels.forEach(channel => {
        if (!channel.cached) {
          channel.isOffline = true;
        }
      });
    }

    // Cache channels
    await setCachedChannels(satelliteChannels);
    
    return satelliteChannels;
  };

  const getCachedChannels = async (): Promise<SatelliteChannel[]> => {
    try {
      const cached = await AsyncStorage.getItem('satellite_channels');
      if (cached) {
        return JSON.parse(cached);
      }
    } catch (error) {
      console.error('Error loading cached channels:', error);
    }
    
    // Return minimal fallback channels
    return [
      {
        id: 'fallback_001',
        number: 1,
        name: 'Emergency Broadcast',
        category: 'News',
        description: 'Emergency information channel',
        genre: 'Emergency',
        streamUrl: 'https://ice1.somafm.com/groovesalad-256-mp3',
        cached: true
      }
    ];
  };

  const setCachedChannels = async (channels: SatelliteChannel[]): Promise<void> => {
    try {
      await AsyncStorage.setItem('satellite_channels', JSON.stringify(channels));
    } catch (error) {
      console.error('Error caching channels:', error);
    }
  };

  const startConnectionAnimation = () => {
    Animated.loop(
      Animated.sequence([
        Animated.timing(pulseAnim, {
          toValue: 1.1,
          duration: 1500,
          useNativeDriver: true,
        }),
        Animated.timing(pulseAnim, {
          toValue: 1,
          duration: 1500,
          useNativeDriver: true,
        }),
      ])
    ).start();

    // Signal strength animation
    Animated.loop(
      Animated.sequence([
        Animated.timing(signalAnim, {
          toValue: 1,
          duration: 2000,
          useNativeDriver: false,
        }),
        Animated.timing(signalAnim, {
          toValue: 0.3,
          duration: 2000,
          useNativeDriver: false,
        }),
      ])
    ).start();
  };

  const stopAnimations = () => {
    pulseAnim.stopAnimation();
    signalAnim.stopAnimation();
  };

  const handleChannelSelect = (channel: SatelliteChannel) => {
    if (channel.isOffline && offlineMode) {
      Alert.alert(
        'Channel Unavailable',
        `${channel.name} is not available in offline mode. This channel requires satellite connection.`,
        [{ text: 'OK' }]
      );
      return;
    }

    setCurrentChannel(channel);
    
    Alert.alert(
      'Switch Channel?',
      `Change to Channel ${channel.number}: ${channel.name}?`,
      [
        { text: 'Cancel', style: 'cancel' },
        {
          text: 'Switch',
          onPress: () => {
            onChannelSelect?.(channel);
            onClose();
          }
        }
      ]
    );
  };

  const handleDirectChannelInput = (number: string) => {
    const channelNum = parseInt(number);
    const channel = channels.find(ch => ch.number === channelNum);
    
    if (channel) {
      handleChannelSelect(channel);
    } else {
      Alert.alert('Channel Not Found', `No channel found at number ${number}`);
    }
    setChannelNumber('');
  };

  const scanChannels = async () => {
    setIsScanning(true);
    
    // Simulate channel scanning
    for (let i = 0; i < channels.length; i++) {
      await new Promise(resolve => setTimeout(resolve, 300));
      setCurrentChannel(channels[i]);
    }
    
    setIsScanning(false);
    Alert.alert('Scan Complete', `Found ${channels.length} available channels`);
  };

  const getFilteredChannels = () => {
    if (selectedCategory === 'All') {
      return channels;
    }
    return channels.filter(channel => channel.category === selectedCategory);
  };

  const getConnectionIcon = () => {
    if (!satelliteConnected) return 'cloud-offline-outline';
    if (connectionStrength > 80) return 'wifi';
    if (connectionStrength > 50) return 'wifi-outline';
    return 'cellular-outline';
  };

  const getConnectionColor = () => {
    if (!satelliteConnected) return colors.error;
    if (connectionStrength > 80) return '#4CAF50';
    if (connectionStrength > 50) return '#FF9800';
    return colors.error;
  };

  const styles = StyleSheet.create({
    modalOverlay: {
      flex: 1,
      backgroundColor: 'rgba(0,0,0,0.8)',
      justifyContent: 'center',
    },
    container: {
      backgroundColor: colors.background,
      margin: 10,
      borderRadius: 16,
      maxHeight: height * 0.9,
      flex: 1,
    },
    header: {
      flexDirection: 'row',
      justifyContent: 'space-between',
      alignItems: 'center',
      padding: 16,
      borderBottomWidth: 1,
      borderBottomColor: colors.border,
      backgroundColor: colors.card,
    },
    title: {
      fontSize: 20,
      fontWeight: '600',
      color: colors.text,
    },
    satelliteStatus: {
      flexDirection: 'row',
      alignItems: 'center',
      gap: 8,
    },
    connectionStrength: {
      fontSize: 12,
      color: colors.textSecondary,
    },
    closeButton: {
      padding: 8,
    },
    channelDisplay: {
      backgroundColor: colors.card,
      padding: 20,
      alignItems: 'center',
      borderBottomWidth: 1,
      borderBottomColor: colors.border,
    },
    currentChannelNumber: {
      fontSize: 48,
      fontWeight: '700',
      color: colors.primary,
    },
    currentChannelName: {
      fontSize: 20,
      fontWeight: '600',
      color: colors.text,
      marginTop: 8,
    },
    currentChannelDescription: {
      fontSize: 14,
      color: colors.textSecondary,
      textAlign: 'center',
      marginTop: 4,
    },
    currentChannelGenre: {
      fontSize: 12,
      color: colors.primary,
      marginTop: 4,
      paddingHorizontal: 12,
      paddingVertical: 4,
      backgroundColor: colors.surface,
      borderRadius: 12,
    },
    controls: {
      flexDirection: 'row',
      justifyContent: 'space-around',
      padding: 16,
      borderBottomWidth: 1,
      borderBottomColor: colors.border,
    },
    controlButton: {
      alignItems: 'center',
      padding: 12,
    },
    controlButtonText: {
      fontSize: 12,
      color: colors.textSecondary,
      marginTop: 4,
    },
    categoryTabs: {
      paddingVertical: 8,
      borderBottomWidth: 1,
      borderBottomColor: colors.border,
    },
    categoryScrollView: {
      paddingHorizontal: 16,
    },
    categoryTab: {
      paddingHorizontal: 16,
      paddingVertical: 8,
      borderRadius: 16,
      marginRight: 8,
      backgroundColor: colors.surface,
    },
    activeCategoryTab: {
      backgroundColor: colors.primary,
    },
    categoryTabText: {
      fontSize: 14,
      color: colors.textSecondary,
    },
    activeCategoryTabText: {
      color: '#fff',
    },
    channelsList: {
      flex: 1,
      padding: 16,
    },
    channelItem: {
      flexDirection: 'row',
      alignItems: 'center',
      backgroundColor: colors.card,
      borderRadius: 8,
      padding: 16,
      marginBottom: 8,
    },
    channelItemOffline: {
      opacity: 0.5,
      backgroundColor: colors.surface,
    },
    channelNumber: {
      width: 50,
      fontSize: 18,
      fontWeight: '600',
      color: colors.primary,
      textAlign: 'center',
    },
    channelInfo: {
      flex: 1,
      marginLeft: 16,
    },
    channelName: {
      fontSize: 16,
      fontWeight: '600',
      color: colors.text,
      marginBottom: 2,
    },
    channelDescription: {
      fontSize: 12,
      color: colors.textSecondary,
      marginBottom: 2,
    },
    channelGenre: {
      fontSize: 10,
      color: colors.primary,
      backgroundColor: colors.surface,
      paddingHorizontal: 8,
      paddingVertical: 2,
      borderRadius: 8,
      alignSelf: 'flex-start',
    },
    channelStatus: {
      alignItems: 'center',
    },
    statusIcon: {
      marginBottom: 4,
    },
    statusText: {
      fontSize: 10,
      color: colors.textSecondary,
    },
    loadingContainer: {
      flex: 1,
      alignItems: 'center',
      justifyContent: 'center',
      padding: 40,
    },
    loadingText: {
      fontSize: 16,
      color: colors.textSecondary,
      marginTop: 16,
      textAlign: 'center',
    },
    emptyState: {
      alignItems: 'center',
      padding: 40,
    },
    emptyText: {
      fontSize: 16,
      color: colors.textSecondary,
      textAlign: 'center',
      marginTop: 16,
    },
  });

  return (
    <Modal visible={visible} transparent animationType="slide">
      <View style={styles.modalOverlay}>
        <View style={styles.container}>
          {/* Header */}
          <View style={styles.header}>
            <View>
              <Text style={styles.title}>📡 Satellite Radio</Text>
              <View style={styles.satelliteStatus}>
                <Animated.View style={{ transform: [{ scale: pulseAnim }] }}>
                  <Ionicons
                    name={getConnectionIcon()}
                    size={16}
                    color={getConnectionColor()}
                  />
                </Animated.View>
                <Text style={styles.connectionStrength}>
                  {satelliteConnected ? `${Math.round(connectionStrength)}%` : 'Connecting...'}
                </Text>
              </View>
            </View>
            <TouchableOpacity style={styles.closeButton} onPress={onClose}>
              <Ionicons name="close" size={24} color={colors.text} />
            </TouchableOpacity>
          </View>

          {isLoading ? (
            <View style={styles.loadingContainer}>
              <ActivityIndicator size="large" color={colors.primary} />
              <Text style={styles.loadingText}>
                Establishing satellite connection...{'\n'}
                Scanning for available channels...
              </Text>
            </View>
          ) : (
            <>
              {/* Current Channel Display */}
              {currentChannel && (
                <Animated.View style={[styles.channelDisplay, { transform: [{ scale: pulseAnim }] }]}>
                  <Text style={styles.currentChannelNumber}>{currentChannel.number}</Text>
                  <Text style={styles.currentChannelName}>{currentChannel.name}</Text>
                  <Text style={styles.currentChannelDescription}>{currentChannel.description}</Text>
                  <Text style={styles.currentChannelGenre}>{currentChannel.genre}</Text>
                </Animated.View>
              )}

              {/* Controls */}
              <View style={styles.controls}>
                <TouchableOpacity style={styles.controlButton} onPress={scanChannels}>
                  <Ionicons 
                    name={isScanning ? 'scan' : 'search'} 
                    size={24} 
                    color={colors.primary} 
                  />
                  <Text style={styles.controlButtonText}>
                    {isScanning ? 'Scanning...' : 'Scan'}
                  </Text>
                </TouchableOpacity>
                
                <TouchableOpacity style={styles.controlButton}>
                  <Ionicons name="heart-outline" size={24} color={colors.primary} />
                  <Text style={styles.controlButtonText}>Favorite</Text>
                </TouchableOpacity>
                
                <TouchableOpacity style={styles.controlButton}>
                  <Ionicons name="bookmark-outline" size={24} color={colors.primary} />
                  <Text style={styles.controlButtonText}>Preset</Text>
                </TouchableOpacity>
                
                <TouchableOpacity style={styles.controlButton}>
                  <Ionicons 
                    name={offlineMode ? 'cloud-offline' : 'cloud-done'} 
                    size={24} 
                    color={offlineMode ? colors.error : colors.primary} 
                  />
                  <Text style={styles.controlButtonText}>
                    {offlineMode ? 'Offline' : 'Online'}
                  </Text>
                </TouchableOpacity>
              </View>

              {/* Category Tabs */}
              <View style={styles.categoryTabs}>
                <ScrollView horizontal showsHorizontalScrollIndicator={false} style={styles.categoryScrollView}>
                  {categories.map((category) => (
                    <TouchableOpacity
                      key={category}
                      style={[
                        styles.categoryTab,
                        selectedCategory === category && styles.activeCategoryTab,
                      ]}
                      onPress={() => setSelectedCategory(category)}
                    >
                      <Text
                        style={[
                          styles.categoryTabText,
                          selectedCategory === category && styles.activeCategoryTabText,
                        ]}
                      >
                        {category}
                      </Text>
                    </TouchableOpacity>
                  ))}
                </ScrollView>
              </View>

              {/* Channels List */}
              <ScrollView style={styles.channelsList}>
                {getFilteredChannels().map((channel) => (
                  <TouchableOpacity
                    key={channel.id}
                    style={[
                      styles.channelItem,
                      channel.isOffline && styles.channelItemOffline,
                    ]}
                    onPress={() => handleChannelSelect(channel)}
                    disabled={channel.isOffline && offlineMode}
                  >
                    <Text style={styles.channelNumber}>{channel.number}</Text>
                    <View style={styles.channelInfo}>
                      <Text style={styles.channelName}>{channel.name}</Text>
                      <Text style={styles.channelDescription}>{channel.description}</Text>
                      <Text style={styles.channelGenre}>{channel.genre}</Text>
                    </View>
                    <View style={styles.channelStatus}>
                      <Ionicons
                        name={
                          channel.isOffline
                            ? 'cloud-offline'
                            : channel.cached
                            ? 'cloud-done'
                            : 'cloud-download'
                        }
                        size={20}
                        color={
                          channel.isOffline
                            ? colors.error
                            : channel.cached
                            ? colors.primary
                            : colors.textSecondary
                        }
                        style={styles.statusIcon}
                      />
                      <Text style={styles.statusText}>
                        {channel.isOffline
                          ? 'Offline'
                          : channel.cached
                          ? 'Cached'
                          : 'Stream'}
                      </Text>
                    </View>
                  </TouchableOpacity>
                ))}
              </ScrollView>
            </>
          )}
        </View>
      </View>
    </Modal>
  );
};