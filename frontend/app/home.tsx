import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  StyleSheet,
  TouchableOpacity,
  TextInput,
  ScrollView,
  Image,
  Dimensions,
  KeyboardAvoidingView,
  Platform,
  Alert,
} from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { router } from 'expo-router';
import { Ionicons } from '@expo/vector-icons';
import { useTheme } from './theme-context';
import { useAudioPlayer } from '../hooks/useAudioPlayer';
import { FeatureTile } from '../components/FeatureTile';
import { BottomFeatureBar } from '../components/BottomFeatureBar';
import AsyncStorage from '@react-native-async-storage/async-storage';

const { width } = Dimensions.get('window');
const API_BASE_URL = process.env.EXPO_PUBLIC_BACKEND_URL || 'https://radio-uifix.preview.emergentagent.com';

interface Station {
  id: string;
  name: string;
  stream_url: string;
  country: string;
  call_sign?: string;
  quality_score?: number;
}

const FEATURES = [
  { id: 'globe', icon: 'globe', label: '3D Globe', color: '#1E88E5' },
  { id: 'map', icon: 'map', label: 'Map & Traffic', color: '#4A5AE8' },
  { id: 'navigate', icon: 'navigate', label: 'Navigate', color: '#00BCD4' },
  { id: 'favorites', icon: 'heart', label: 'Favorites', color: '#FF6B35' },
  { id: 'settings', icon: 'settings', label: 'Settings', color: '#8B92B0' },
] as const;

export default function DragonKarauHome() {
  const { theme, toggleTheme } = useTheme();
  const {
    isPlaying,
    currentStation,
    nowPlayingMetadata,
    playStation: playStationAudio,
    togglePlayPause,
    stop,
  } = useAudioPlayer();

  const [searchQuery, setSearchQuery] = useState('');
  const [activeFeatures, setActiveFeatures] = useState<string[]>([]);
  const [isVoiceSearch, setIsVoiceSearch] = useState(false);
  const [popularStations, setPopularStations] = useState<Station[]>([]);

  useEffect(() => {
    loadPopularStations();
  }, []);

  const loadPopularStations = async () => {
    try {
      console.log('[HOME] Loading stations from:', `${API_BASE_URL}/api/stations?limit=10`);
      console.log('[HOME] API_BASE_URL value:', API_BASE_URL);
      
      const response = await fetch(`${API_BASE_URL}/api/stations?limit=10`);
      console.log('[HOME] Response status:', response.status);
      
      const data = await response.json();
      console.log('[HOME] Response data:', JSON.stringify(data).substring(0, 300));
      console.log('[HOME] Data status:', data.status);
      console.log('[HOME] Stations array:', data.data?.stations);
      console.log('[HOME] Stations count:', data.data?.stations?.length);
      
      if (data.status === 'success' && data.data && data.data.stations) {
        console.log('[HOME] Setting', data.data.stations.length, 'stations');
        setPopularStations(data.data.stations);
        
        // Show alert for debugging
        Alert.alert(
          'Stations Loaded',
          `Successfully loaded ${data.data.stations.length} popular stations!`,
          [{ text: 'OK' }]
        );
      } else {
        console.error('[HOME] Invalid data format:', data);
        Alert.alert('Error', 'Invalid data format from server');
      }
    } catch (error) {
      console.error('[HOME] Error loading stations:', error);
      Alert.alert('Error', `Failed to load stations: ${error}`);
    }
  };

  const handleSearch = async () => {
    if (!searchQuery.trim()) return;
    
    // Navigate to search screen with query
    router.push({
      pathname: '/search',
      params: { query: searchQuery },
    });
  };

  const handleFeatureTilePress = (featureId: string) => {
    switch (featureId) {
      case 'radio':
        router.push('/stations-browser');
        break;
      case 'globe':
        router.push('/globe');
        break;
      case 'map':
        router.push('/map');
        break;
      case 'favorites':
        router.push('/favorites');
        break;
      case 'navigate':
        // Toggle navigation feature in bottom bar
        toggleFeature('navigate');
        break;
      case 'settings':
        router.push('/settings');
        break;
    }
  };

  const toggleFeature = (featureId: string) => {
    setActiveFeatures((prev) =>
      prev.includes(featureId)
        ? prev.filter((f) => f !== featureId)
        : [...prev, featureId]
    );
  };

  const handleLogoPress = () => {
    // Show all features menu
    router.push('/settings');
  };

  const playStation = async (station: Station) => {
    await playStationAudio(station);
  };

  return (
    <SafeAreaView 
      style={[styles.container, { backgroundColor: theme.colors.background }]}
      edges={['top']}
    >
      <KeyboardAvoidingView
        style={styles.keyboardView}
        behavior={Platform.OS === 'ios' ? 'padding' : 'height'}
      >
        <ScrollView
          style={styles.scrollView}
          contentContainerStyle={styles.scrollContent}
          showsVerticalScrollIndicator={false}
        >
          {/* Header with Clickable Logo */}
          <TouchableOpacity
            style={styles.logoContainer}
            onPress={handleLogoPress}
            activeOpacity={0.8}
          >
            <Image
              source={{
                uri: 'https://customer-assets.emergentagent.com/job_7a9dd132-a732-436b-84ea-9628edec4c9e/artifacts/ugutvh86_IMG_7819.jpeg',
              }}
              style={styles.logo}
              resizeMode="contain"
            />
            <Text style={styles.logoText}>Dragon KARAU AI</Text>
            <View style={styles.logoHint}>
              <Ionicons name="chevron-down" size={16} color="#8B92B0" />
              <Text style={styles.logoHintText}>Tap for all features</Text>
            </View>
          </TouchableOpacity>

          {/* AI Search Bar */}
          <View style={styles.searchSection}>
            <View style={styles.searchContainer}>
              <Ionicons name="search" size={20} color="#8B92B0" style={styles.searchIcon} />
              <TextInput
                style={styles.searchInput}
                placeholder="Search radio stations or navigate..."
                placeholderTextColor="#8B92B0"
                value={searchQuery}
                onChangeText={setSearchQuery}
                onSubmitEditing={handleSearch}
                returnKeyType="search"
              />
              <TouchableOpacity
                style={styles.voiceButton}
                onPress={() => setIsVoiceSearch(!isVoiceSearch)}
              >
                <Ionicons 
                  name={isVoiceSearch ? "mic" : "mic-outline"} 
                  size={22} 
                  color={isVoiceSearch ? "#FF6B35" : "#8B92B0"} 
                />
              </TouchableOpacity>
            </View>
            {isVoiceSearch && (
              <View style={styles.voiceHint}>
                <Ionicons name="radio-button-on" size={12} color="#FF6B35" />
                <Text style={styles.voiceHintText}>Voice search active - speak now</Text>
              </View>
            )}
          </View>

          {/* Dragon Logo - Now Playing */}
          {currentStation ? (
            <TouchableOpacity
              style={styles.nowPlayingCard}
              onPress={() => router.push('/index')}
              activeOpacity={0.9}
            >
              <View style={styles.nowPlayingHeader}>
                <Text style={styles.nowPlayingLabel}>🐉 NOW PLAYING</Text>
                {isPlaying && (
                  <View style={styles.playingAnimation}>
                    <View style={[styles.bar, styles.bar1]} />
                    <View style={[styles.bar, styles.bar2]} />
                    <View style={[styles.bar, styles.bar3]} />
                  </View>
                )}
              </View>
              
              <Text style={styles.nowPlayingTitle} numberOfLines={2}>
                {nowPlayingMetadata?.title || currentStation.name}
              </Text>
              <Text style={styles.nowPlayingArtist} numberOfLines={1}>
                {nowPlayingMetadata?.artist || currentStation.country}
              </Text>

              <View style={styles.nowPlayingControls}>
                <TouchableOpacity
                  style={styles.controlButton}
                  onPress={(e) => {
                    e.stopPropagation();
                    togglePlayPause();
                  }}
                >
                  <Ionicons
                    name={isPlaying ? 'pause' : 'play'}
                    size={24}
                    color="#FFFFFF"
                  />
                </TouchableOpacity>
                <TouchableOpacity
                  style={styles.controlButton}
                  onPress={(e) => {
                    e.stopPropagation();
                    stop();
                  }}
                >
                  <Ionicons name="stop" size={24} color="#FFFFFF" />
                </TouchableOpacity>
                <View style={styles.liveIndicator}>
                  <View style={styles.liveDot} />
                  <Text style={styles.liveText}>LIVE</Text>
                </View>
              </View>
            </TouchableOpacity>
          ) : (
            <View style={styles.dragonPlaceholder}>
              <Text style={styles.dragonIcon}>🐉</Text>
              <Text style={styles.dragonText}>Select a station to start listening</Text>
            </View>
          )}

          {/* Feature Tiles */}
          <View style={styles.featuresHeader}>
            <Text style={styles.sectionTitle}>Explore Features</Text>
            <Text style={styles.sectionSubtitle}>Tap a tile to activate</Text>
          </View>

          <View style={styles.tilesGrid}>
            <FeatureTile
              icon="radio"
              title="Radio"
              tagline="16,000+ stations"
              color="#FF6B35"
              onPress={() => handleFeatureTilePress('radio')}
            />
            <FeatureTile
              icon="globe"
              title="3D Globe"
              tagline="Explore worldwide"
              color="#1E88E5"
              onPress={() => handleFeatureTilePress('globe')}
            />
            <FeatureTile
              icon="map"
              title="Map & Traffic"
              tagline="Real-time info"
              color="#4A5AE8"
              onPress={() => handleFeatureTilePress('map')}
            />
            <FeatureTile
              icon="navigate"
              title="Navigate"
              tagline="Turn-by-turn"
              color="#00BCD4"
              onPress={() => handleFeatureTilePress('navigate')}
            />
            <FeatureTile
              icon="heart"
              title="Favorites"
              tagline="Your stations"
              color="#FF6B35"
              onPress={() => handleFeatureTilePress('favorites')}
            />
            <FeatureTile
              icon="stats-chart"
              title="Analytics"
              tagline="System insights"
              color="#9C27B0"
              onPress={() => router.push('/analytics')}
            />
            <FeatureTile
              icon="chatbox-ellipses"
              title="Feedback"
              tagline="Share your thoughts"
              color="#4CAF50"
              onPress={() => router.push('/feedback')}
            />
            <FeatureTile
              icon="sparkles"
              title="AI Search"
              tagline="Smart discovery"
              color="#9C27B0"
              onPress={() => router.push('/search')}
            />
          </View>

          {/* Popular Stations */}
          <View style={styles.popularSection}>
            <Text style={styles.sectionTitle}>Popular Stations</Text>
            <Text style={styles.sectionSubtitle}>
              {popularStations.length > 0 
                ? 'Start listening with one tap' 
                : 'Loading stations...'}
            </Text>
          </View>

          {popularStations.length > 0 ? (
            popularStations.slice(0, 5).map((station) => (
              <TouchableOpacity
                key={station.id}
                style={styles.stationCard}
                onPress={() => playStation(station)}
              >
                <View style={styles.stationIcon}>
                  <Ionicons name="radio" size={24} color="#FF6B35" />
                </View>
                <View style={styles.stationInfo}>
                  <Text style={styles.stationName} numberOfLines={1}>
                    {station.name}
                  </Text>
                  <Text style={styles.stationMeta}>
                    {station.country} • Quality: {station.quality_score || 'N/A'}
                  </Text>
                </View>
                <Ionicons name="play-circle" size={40} color="#FF6B35" />
              </TouchableOpacity>
            ))
          ) : (
            <View style={styles.emptyStationsCard}>
              <Ionicons name="radio-outline" size={48} color="#8B92B0" />
              <Text style={styles.emptyStationsText}>
                Connecting to radio network...
              </Text>
            </View>
          )}

          {/* Spacer for bottom bar */}
          <View style={{ height: 180 }} />
        </ScrollView>

        {/* Bottom Feature Bar */}
        {currentStation && (
          <BottomFeatureBar
            features={FEATURES}
            activeFeatures={activeFeatures}
            onToggleFeature={toggleFeature}
            currentStation={currentStation}
          />
        )}
      </KeyboardAvoidingView>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
  },
  keyboardView: {
    flex: 1,
  },
  scrollView: {
    flex: 1,
  },
  scrollContent: {
    paddingHorizontal: 20,
  },
  logoContainer: {
    alignItems: 'center',
    paddingVertical: 24,
  },
  logo: {
    width: 80,
    height: 80,
    marginBottom: 8,
  },
  logoText: {
    fontSize: 20,
    fontWeight: '700',
    color: '#FFFFFF',
    marginBottom: 4,
  },
  logoHint: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 4,
  },
  logoHintText: {
    fontSize: 12,
    color: '#8B92B0',
  },
  searchSection: {
    marginBottom: 24,
  },
  searchContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: 'rgba(26, 31, 58, 0.95)',
    borderRadius: 16,
    borderWidth: 2,
    borderColor: 'rgba(255, 107, 53, 0.3)',
    paddingHorizontal: 16,
    paddingVertical: 14,
  },
  searchIcon: {
    marginRight: 12,
  },
  searchInput: {
    flex: 1,
    fontSize: 16,
    color: '#FFFFFF',
  },
  voiceButton: {
    padding: 4,
  },
  voiceHint: {
    flexDirection: 'row',
    alignItems: 'center',
    marginTop: 8,
    gap: 8,
  },
  voiceHintText: {
    fontSize: 12,
    color: '#FF6B35',
    fontWeight: '600',
  },
  nowPlayingCard: {
    backgroundColor: 'rgba(26, 31, 58, 0.95)',
    borderRadius: 20,
    padding: 20,
    marginBottom: 32,
    borderWidth: 2,
    borderColor: 'rgba(255, 107, 53, 0.5)',
  },
  nowPlayingHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    marginBottom: 16,
  },
  nowPlayingLabel: {
    fontSize: 14,
    fontWeight: '700',
    color: '#FF6B35',
    letterSpacing: 1,
  },
  playingAnimation: {
    flexDirection: 'row',
    alignItems: 'flex-end',
    gap: 3,
    height: 16,
  },
  bar: {
    width: 3,
    backgroundColor: '#FF6B35',
    borderRadius: 2,
  },
  bar1: { height: '100%', opacity: 0.8 },
  bar2: { height: '60%', opacity: 0.6 },
  bar3: { height: '80%', opacity: 0.7 },
  nowPlayingTitle: {
    fontSize: 20,
    fontWeight: '700',
    color: '#FFFFFF',
    marginBottom: 8,
  },
  nowPlayingArtist: {
    fontSize: 14,
    color: '#8B92B0',
    marginBottom: 16,
  },
  nowPlayingControls: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 12,
  },
  controlButton: {
    width: 48,
    height: 48,
    borderRadius: 24,
    backgroundColor: '#FF6B35',
    justifyContent: 'center',
    alignItems: 'center',
  },
  liveIndicator: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: 'rgba(255, 107, 53, 0.2)',
    paddingHorizontal: 12,
    paddingVertical: 8,
    borderRadius: 16,
    gap: 6,
    marginLeft: 'auto',
  },
  liveDot: {
    width: 8,
    height: 8,
    borderRadius: 4,
    backgroundColor: '#FF6B35',
  },
  liveText: {
    fontSize: 12,
    fontWeight: '700',
    color: '#FF6B35',
    letterSpacing: 1,
  },
  dragonPlaceholder: {
    backgroundColor: 'rgba(26, 31, 58, 0.95)',
    borderRadius: 20,
    padding: 40,
    alignItems: 'center',
    marginBottom: 32,
    borderWidth: 2,
    borderColor: 'rgba(139, 146, 176, 0.3)',
    borderStyle: 'dashed',
  },
  dragonIcon: {
    fontSize: 64,
    marginBottom: 16,
  },
  dragonText: {
    fontSize: 16,
    color: '#8B92B0',
    textAlign: 'center',
  },
  featuresHeader: {
    marginBottom: 16,
  },
  sectionTitle: {
    fontSize: 22,
    fontWeight: '700',
    color: '#FFFFFF',
    marginBottom: 4,
  },
  sectionSubtitle: {
    fontSize: 14,
    color: '#8B92B0',
  },
  tilesGrid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    justifyContent: 'space-between',
    marginTop: 12,
    marginBottom: 16,
  },
  popularSection: {
    marginTop: 32,
    marginBottom: 16,
  },
  stationCard: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: 'rgba(26, 31, 58, 0.95)',
    borderRadius: 16,
    padding: 16,
    marginBottom: 12,
    borderWidth: 1,
    borderColor: 'rgba(139, 146, 176, 0.2)',
  },
  stationIcon: {
    width: 48,
    height: 48,
    borderRadius: 24,
    backgroundColor: 'rgba(255, 107, 53, 0.2)',
    justifyContent: 'center',
    alignItems: 'center',
    marginRight: 16,
  },
  stationInfo: {
    flex: 1,
    marginRight: 12,
  },
  stationName: {
    fontSize: 16,
    fontWeight: '600',
    color: '#FFFFFF',
    marginBottom: 4,
  },
  stationMeta: {
    fontSize: 12,
    color: '#8B92B0',
  },
  emptyStationsCard: {
    backgroundColor: 'rgba(26, 31, 58, 0.95)',
    borderRadius: 16,
    padding: 40,
    marginBottom: 12,
    alignItems: 'center',
    borderWidth: 1,
    borderColor: 'rgba(139, 146, 176, 0.2)',
    borderStyle: 'dashed',
  },
  emptyStationsText: {
    fontSize: 14,
    color: '#8B92B0',
    marginTop: 12,
    textAlign: 'center',
  },
});
