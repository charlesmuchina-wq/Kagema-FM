import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  StyleSheet,
  TouchableOpacity,
  ScrollView,
  Alert,
  Platform,
} from 'react-native';
import { Ionicons } from '@expo/vector-icons';

// Import all the new services
import { sleepTimerService, SleepTimerState } from '../services/SleepTimerService';
import { enhancedBackgroundAudioService, BackgroundAudioState } from '../services/EnhancedBackgroundAudioService';
import { monetizationService, MonetizationState } from '../services/MonetizationService';
import { mapKitService, RadioStationPlace } from '../services/MapKitService';
import { iOSAudioInputPickerService, AudioInputState } from '../services/iOSAudioInputPickerService';

// Import components
import SleepTimerComponent from './SleepTimerComponent';
import { iOSAudioInputPicker } from './iOSAudioInputPicker';

interface EnhancedRadioDashboardProps {
  onClose?: () => void;
  style?: any;
}

export const EnhancedRadioDashboard: React.FC<EnhancedRadioDashboardProps> = ({
  onClose,
  style
}) => {
  // State management for all services
  const [sleepTimerState, setSleepTimerState] = useState<SleepTimerState>(sleepTimerService.getState());
  const [audioState, setAudioState] = useState<BackgroundAudioState>(enhancedBackgroundAudioService.getState());
  const [monetizationState, setMonetizationState] = useState<MonetizationState>(monetizationService.getState());
  const [audioInputState, setAudioInputState] = useState<AudioInputState>(iOSAudioInputPickerService.getState());
  const [nearbyStations, setNearbyStations] = useState<RadioStationPlace[]>([]);
  
  // UI state
  const [showSleepTimer, setShowSleepTimer] = useState(false);
  const [currentLocation, setCurrentLocation] = useState<{ latitude: number; longitude: number } | null>(null);

  useEffect(() => {
    // Subscribe to all service state changes
    const unsubscribes = [
      sleepTimerService.addListener(setSleepTimerState),
      enhancedBackgroundAudioService.addListener(setAudioState),
      monetizationService.addListener(setMonetizationState),
      iOSAudioInputPickerService.addListener(setAudioInputState)
    ];

    // Initialize location and nearby stations
    initializeLocation();

    return () => {
      unsubscribes.forEach(unsub => unsub());
    };
  }, []);

  const initializeLocation = async () => {
    try {
      // Get user location
      if (navigator.geolocation) {
        navigator.geolocation.getCurrentPosition(
          async (position) => {
            const { latitude, longitude } = position.coords;
            setCurrentLocation({ latitude, longitude });
            
            // Find nearby radio stations using MapKit
            const stations = await mapKitService.findNearbyRadioStations(latitude, longitude, 100);
            setNearbyStations(stations);
          },
          (error) => {
            console.log('Location access denied, using default location');
            // Use default location (Nairobi)
            setCurrentLocation({ latitude: -1.2921, longitude: 36.8219 });
            mapKitService.findNearbyRadioStations(-1.2921, 36.8219, 100).then(setNearbyStations);
          }
        );
      }
    } catch (error) {
      console.error('Failed to initialize location:', error);
    }
  };

  const handleSleepTimerToggle = () => {
    if (sleepTimerState.isActive) {
      Alert.alert(
        'Sleep Timer Active',
        `Timer is running with ${sleepTimerService.getRemainingMinutes()} minutes remaining.`,
        [
          { text: 'Cancel Timer', style: 'destructive', onPress: () => sleepTimerService.cancelTimer() },
          { text: 'Close', style: 'cancel' }
        ]
      );
    } else {
      setShowSleepTimer(true);
    }
  };

  const handleBackgroundAudioDemo = async () => {
    if (!audioState.isPlaying) {
      // Load demo audio
      const success = await enhancedBackgroundAudioService.loadAudio(
        'https://stream.live.vc.bbcmedia.co.uk/bbc_radio_one',
        {
          title: 'BBC Radio 1',
          artist: 'BBC',
          album: 'Live Radio'
        }
      );
      
      if (success) {
        await enhancedBackgroundAudioService.play();
        Alert.alert('Background Audio', 'Audio will continue playing when you background the app!');
      }
    } else {
      await enhancedBackgroundAudioService.pause();
    }
  };

  const handleAirPlayDemo = async () => {
    if (Platform.OS === 'ios') {
      const success = await iOSAudioInputPickerService.presentInputPicker();
      if (success) {
        Alert.alert('AirPlay', 'Select your AirPlay device from the picker!');
      }
    } else {
      Alert.alert('AirPlay', 'AirPlay is only available on iOS devices.');
    }
  };

  const handleMonetizationDemo = async () => {
    if (monetizationState.isPremium) {
      Alert.alert(
        'Premium Active',
        `You have ${monetizationService.getDaysRemaining()} days remaining in your subscription.`,
        [{ text: 'OK' }]
      );
    } else {
      Alert.alert(
        'Monetization Demo',
        'Choose an action:',
        [
          { text: 'Start Free Trial', onPress: () => monetizationService.startFreeTrial() },
          { text: 'Show Banner Ad', onPress: () => monetizationService.showBannerAd() },
          { text: 'Show Interstitial Ad', onPress: () => monetizationService.showInterstitialAd() },
          { text: 'Purchase Premium', onPress: () => monetizationService.purchaseProduct('kagema_premium_monthly') },
          { text: 'Cancel', style: 'cancel' }
        ]
      );
    }
  };

  const handleMapKitDemo = async () => {
    if (nearbyStations.length === 0) {
      Alert.alert('No Stations', 'No nearby radio stations found.');
      return;
    }

    const stationNames = nearbyStations.map(s => s.name).join(', ');
    Alert.alert(
      'MapKit Integration',
      `Found ${nearbyStations.length} nearby stations:\n${stationNames}`,
      [
        { text: 'Get Directions', onPress: () => getDirectionsToStation(nearbyStations[0]) },
        { text: 'View Details', onPress: () => viewStationDetails(nearbyStations[0]) },
        { text: 'Close', style: 'cancel' }
      ]
    );
  };

  const getDirectionsToStation = async (station: RadioStationPlace) => {
    if (!currentLocation) return;

    const directions = await mapKitService.getDirections({
      origin: currentLocation,
      destination: station,
      transportType: 'automobile'
    });

    if (directions) {
      const distance = (directions.distance / 1000).toFixed(1);
      const time = Math.round(directions.expectedTravelTime / 60);
      
      Alert.alert(
        'Directions',
        `${station.name}\n\nDistance: ${distance} km\nEstimated time: ${time} minutes`,
        [{ text: 'OK' }]
      );
    }
  };

  const viewStationDetails = async (station: RadioStationPlace) => {
    const details = `
📡 ${station.name}
📍 ${station.address}
📞 ${station.phoneNumber}
🌐 ${station.website}
📻 ${station.frequency}
🎵 ${station.genre}
📡 Broadcast radius: ${station.broadcastRadius} km
    `.trim();

    Alert.alert('Station Details', details, [{ text: 'OK' }]);
  };

  return (
    <View style={[styles.container, style]}>
      {/* Header */}
      <View style={styles.header}>
        <Text style={styles.headerTitle}>Enhanced Radio Features</Text>
        {onClose && (
          <TouchableOpacity style={styles.closeButton} onPress={onClose}>
            <Ionicons name="close" size={24} color="#666" />
          </TouchableOpacity>
        )}
      </View>

      <ScrollView style={styles.scrollContainer} showsVerticalScrollIndicator={false}>
        
        {/* Sleep Timer Card */}
        <View style={styles.featureCard}>
          <View style={styles.cardHeader}>
            <Ionicons name="moon-outline" size={24} color="#007AFF" />
            <Text style={styles.cardTitle}>Sleep Timer</Text>
            <View style={styles.statusBadge}>
              <Text style={[styles.statusText, sleepTimerState.isActive && styles.statusActive]}>
                {sleepTimerState.isActive ? sleepTimerService.getFormattedTime() : 'OFF'}
              </Text>
            </View>
          </View>
          <Text style={styles.cardDescription}>
            Automatically stop playback after a set duration with fade-out
          </Text>
          <TouchableOpacity style={styles.actionButton} onPress={handleSleepTimerToggle}>
            <Text style={styles.actionButtonText}>
              {sleepTimerState.isActive ? 'Manage Timer' : 'Set Sleep Timer'}
            </Text>
          </TouchableOpacity>
        </View>

        {/* Background Audio Card */}
        <View style={styles.featureCard}>
          <View style={styles.cardHeader}>
            <Ionicons name="musical-notes-outline" size={24} color="#007AFF" />
            <Text style={styles.cardTitle}>Background Audio</Text>
            <View style={styles.statusBadge}>
              <Text style={[styles.statusText, audioState.isPlaying && styles.statusActive]}>
                {audioState.isPlaying ? 'PLAYING' : 'PAUSED'}
              </Text>
            </View>
          </View>
          <Text style={styles.cardDescription}>
            Continuous playback with lock screen controls when app is backgrounded
          </Text>
          {audioState.metadata && (
            <View style={styles.nowPlaying}>
              <Text style={styles.nowPlayingText}>
                🎵 {audioState.metadata.title} - {audioState.metadata.artist}
              </Text>
            </View>
          )}
          <TouchableOpacity style={styles.actionButton} onPress={handleBackgroundAudioDemo}>
            <Text style={styles.actionButtonText}>
              {audioState.isPlaying ? 'Pause Demo' : 'Play Demo'}
            </Text>
          </TouchableOpacity>
        </View>

        {/* AirPlay Integration Card */}
        <View style={styles.featureCard}>
          <View style={styles.cardHeader}>
            <Ionicons name="wifi-outline" size={24} color="#007AFF" />
            <Text style={styles.cardTitle}>AirPlay Integration</Text>
            <View style={styles.statusBadge}>
              <Text style={styles.statusText}>
                {audioInputState.selectedInput?.type === 'airplay' ? 'CONNECTED' : 'DEVICE'}
              </Text>
            </View>
          </View>
          <Text style={styles.cardDescription}>
            Stream to AirPlay devices, HomePod, Apple TV, and Bluetooth speakers
          </Text>
          {audioInputState.selectedInput && (
            <View style={styles.deviceInfo}>
              <Text style={styles.deviceText}>
                🎧 {audioInputState.selectedInput.name}
              </Text>
            </View>
          )}
          <TouchableOpacity style={styles.actionButton} onPress={handleAirPlayDemo}>
            <Text style={styles.actionButtonText}>Select Audio Device</Text>
          </TouchableOpacity>
        </View>

        {/* Monetization Card */}
        <View style={styles.featureCard}>
          <View style={styles.cardHeader}>
            <Ionicons name="diamond-outline" size={24} color="#007AFF" />
            <Text style={styles.cardTitle}>Premium Features</Text>
            <View style={[styles.statusBadge, monetizationState.isPremium && styles.premiumBadge]}>
              <Text style={[
                styles.statusText, 
                monetizationState.isPremium && styles.premiumText
              ]}>
                {monetizationState.isPremium ? 'PREMIUM' : 'FREE'}
              </Text>
            </View>
          </View>
          <Text style={styles.cardDescription}>
            {monetizationState.isPremium 
              ? `Premium features active • ${monetizationService.getDaysRemaining()} days remaining`
              : 'Remove ads, unlock sleep timer, and access premium stations'
            }
          </Text>
          <TouchableOpacity style={styles.actionButton} onPress={handleMonetizationDemo}>
            <Text style={styles.actionButtonText}>
              {monetizationState.isPremium ? 'Manage Premium' : 'Upgrade to Premium'}
            </Text>
          </TouchableOpacity>
        </View>

        {/* MapKit Integration Card */}
        <View style={styles.featureCard}>
          <View style={styles.cardHeader}>
            <Ionicons name="map-outline" size={24} color="#007AFF" />
            <Text style={styles.cardTitle}>MapKit Integration</Text>
            <View style={styles.statusBadge}>
              <Text style={styles.statusText}>
                {nearbyStations.length} NEARBY
              </Text>
            </View>
          </View>
          <Text style={styles.cardDescription}>
            Find radio stations, get directions, and explore with Look Around
          </Text>
          {currentLocation && (
            <View style={styles.locationInfo}>
              <Text style={styles.locationText}>
                📍 {currentLocation.latitude.toFixed(4)}, {currentLocation.longitude.toFixed(4)}
              </Text>
            </View>
          )}
          <TouchableOpacity style={styles.actionButton} onPress={handleMapKitDemo}>
            <Text style={styles.actionButtonText}>Explore Nearby Stations</Text>
          </TouchableOpacity>
        </View>

        {/* iOS Audio Picker (iOS only) */}
        {Platform.OS === 'ios' && (
          <View style={styles.featureCard}>
            <iOSAudioInputPicker 
              showManualPicker={false}
              style={styles.audioPickerContainer}
            />
          </View>
        )}

      </ScrollView>

      {/* Sleep Timer Modal */}
      <SleepTimerComponent
        visible={showSleepTimer}
        onClose={() => setShowSleepTimer(false)}
      />
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f8f9fa',
  },
  header: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    padding: 16,
    backgroundColor: '#fff',
    borderBottomWidth: 1,
    borderBottomColor: '#e0e0e0',
  },
  headerTitle: {
    fontSize: 18,
    fontWeight: '600',
    color: '#333',
  },
  closeButton: {
    padding: 8,
  },
  scrollContainer: {
    flex: 1,
    padding: 16,
  },
  featureCard: {
    backgroundColor: '#fff',
    borderRadius: 12,
    padding: 16,
    marginBottom: 16,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 1 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 2,
  },
  cardHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 8,
  },
  cardTitle: {
    fontSize: 16,
    fontWeight: '600',
    color: '#333',
    marginLeft: 8,
    flex: 1,
  },
  statusBadge: {
    backgroundColor: '#f0f0f0',
    paddingHorizontal: 8,
    paddingVertical: 4,
    borderRadius: 6,
  },
  premiumBadge: {
    backgroundColor: '#FFD700',
  },
  statusText: {
    fontSize: 12,
    fontWeight: '600',
    color: '#666',
  },
  statusActive: {
    color: '#007AFF',
  },
  premiumText: {
    color: '#B8860B',
  },
  cardDescription: {
    fontSize: 14,
    color: '#666',
    marginBottom: 12,
    lineHeight: 20,
  },
  nowPlaying: {
    backgroundColor: '#f8f9fa',
    padding: 8,
    borderRadius: 6,
    marginBottom: 8,
  },
  nowPlayingText: {
    fontSize: 12,
    color: '#007AFF',
  },
  deviceInfo: {
    backgroundColor: '#f8f9fa',
    padding: 8,
    borderRadius: 6,
    marginBottom: 8,
  },
  deviceText: {
    fontSize: 12,
    color: '#007AFF',
  },
  locationInfo: {
    backgroundColor: '#f8f9fa',
    padding: 8,
    borderRadius: 6,
    marginBottom: 8,
  },
  locationText: {
    fontSize: 12,
    color: '#007AFF',
    fontFamily: Platform.OS === 'ios' ? 'Menlo' : 'monospace',
  },
  actionButton: {
    backgroundColor: '#007AFF',
    borderRadius: 8,
    paddingVertical: 10,
    paddingHorizontal: 16,
    alignItems: 'center',
  },
  actionButtonText: {
    color: '#fff',
    fontSize: 14,
    fontWeight: '500',
  },
  audioPickerContainer: {
    marginVertical: 0,
  },
});

export default EnhancedRadioDashboard;