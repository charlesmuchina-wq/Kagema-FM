import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  StyleSheet,
  TouchableOpacity,
  ActivityIndicator,
  TextInput,
  Image,
  Modal,
  ScrollView,
  Dimensions,
} from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { Ionicons } from '@expo/vector-icons';
import { router } from 'expo-router';
import AsyncStorage from '@react-native-async-storage/async-storage';

const { width, height } = Dimensions.get('window');
const API_BASE_URL = process.env.EXPO_PUBLIC_BACKEND_URL || '';

interface Station {
  id: string;
  name: string;
  call_sign?: string;
  standard_display_name?: string;
  stream_url: string;
  country: string;
  quality_score: number;
}

export default function KagemaFMHome() {
  const [loading, setLoading] = useState(false);
  const [nowPlaying, setNowPlaying] = useState<Station | null>(null);
  const [searchQuery, setSearchQuery] = useState('');
  const [searchResults, setSearchResults] = useState<Station[]>([]);
  const [showDisclaimer, setShowDisclaimer] = useState(false);
  const [disclaimerAccepted, setDisclaimerAccepted] = useState(false);
  const [isPlaying, setIsPlaying] = useState(false);
  const [userLocation, setUserLocation] = useState<string>('');
  const [userId, setUserId] = useState<string>('');
  const [isFavorite, setIsFavorite] = useState(false);

  useEffect(() => {
    checkDisclaimerStatus();
    detectUserLocation();
    initializeUser();
  }, []);

  useEffect(() => {
    if (nowPlaying && userId) {
      checkFavoriteStatus();
    }
  }, [nowPlaying, userId]);

  useEffect(() => {
    if (disclaimerAccepted && userLocation) {
      fetchNearestStation();
    }
  }, [disclaimerAccepted, userLocation]);

  const checkDisclaimerStatus = () => {
    // In production, check AsyncStorage
    // For now, show disclaimer on first load
    const accepted = false; // await AsyncStorage.getItem('disclaimer_accepted');
    if (!accepted) {
      setShowDisclaimer(true);
    } else {
      setDisclaimerAccepted(true);
    }
  };

  const acceptDisclaimer = () => {
    setDisclaimerAccepted(true);
    setShowDisclaimer(false);
    // await AsyncStorage.setItem('disclaimer_accepted', 'true');
  };

  const detectUserLocation = async () => {
    try {
      // Try to get user's country from IP
      const response = await fetch('https://ipapi.co/json/');
      const data = await response.json();
      setUserLocation(data.country_code || 'US');
    } catch (error) {
      console.log('Location detection failed, defaulting to US');
      setUserLocation('US');
    }
  };

  const fetchNearestStation = async () => {
    try {
      setLoading(true);
      // Fetch stations from user's country
      const response = await fetch(`${API_BASE_URL}/api/stations?country=${userLocation}&limit=1`);
      const data = await response.json();
      
      if (data.status === 'success' && data.data.stations.length > 0) {
        setNowPlaying(data.data.stations[0]);
      } else {
        // Fallback: get any popular station
        const fallback = await fetch(`${API_BASE_URL}/api/stations?limit=1`);
        const fallbackData = await fallback.json();
        if (fallbackData.status === 'success' && fallbackData.data.stations.length > 0) {
          setNowPlaying(fallbackData.data.stations[0]);
        }
      }
    } catch (error) {
      console.error('Error fetching station:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleSearch = async () => {
    if (!searchQuery.trim()) {
      setSearchResults([]);
      return;
    }

    try {
      setLoading(true);
      const response = await fetch(
        `${API_BASE_URL}/api/stations/search?q=${encodeURIComponent(searchQuery)}&limit=20`
      );
      const data = await response.json();
      
      if (data.status === 'success') {
        setSearchResults(data.data.stations || []);
      }
    } catch (error) {
      console.error('Search error:', error);
      setSearchResults([]);
    } finally {
      setLoading(false);
    }
  };

  const playStation = (station: Station) => {
    setNowPlaying(station);
    setIsPlaying(true);
    setSearchResults([]);
    setSearchQuery('');
    // Audio playback would be implemented here
    console.log('Playing:', station);
  };

  const togglePlayPause = () => {
    setIsPlaying(!isPlaying);
    // Audio control would be implemented here
  };

  const initializeUser = async () => {
    try {
      let storedUserId = await AsyncStorage.getItem('user_id');
      if (!storedUserId) {
        storedUserId = `user_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
        await AsyncStorage.setItem('user_id', storedUserId);
      }
      setUserId(storedUserId);
    } catch (error) {
      console.error('Error initializing user:', error);
      setUserId(`temp_${Date.now()}`);
    }
  };

  const checkFavoriteStatus = async () => {
    if (!nowPlaying || !userId) return;
    
    try {
      const response = await fetch(
        `${API_BASE_URL}/api/favorites/${userId}/check/${nowPlaying.id}`
      );
      const data = await response.json();
      
      if (data.status === 'success') {
        setIsFavorite(data.data.is_favorite);
      }
    } catch (error) {
      console.error('Error checking favorite status:', error);
    }
  };

  const toggleFavorite = async () => {
    if (!nowPlaying || !userId) return;

    try {
      if (isFavorite) {
        // Remove from favorites
        const response = await fetch(
          `${API_BASE_URL}/api/favorites/remove?user_id=${userId}&station_id=${nowPlaying.id}`,
          { method: 'DELETE' }
        );
        const data = await response.json();
        
        if (data.status === 'success') {
          setIsFavorite(false);
        }
      } else {
        // Add to favorites
        const response = await fetch(
          `${API_BASE_URL}/api/favorites/add?user_id=${userId}&station_id=${nowPlaying.id}`,
          { method: 'POST' }
        );
        const data = await response.json();
        
        if (data.status === 'success') {
          setIsFavorite(true);
        }
      }
    } catch (error) {
      console.error('Error toggling favorite:', error);
    }
  };

  return (
    <SafeAreaView style={styles.container} edges={['top']}>
      {/* Holographic Background */}
      <Image
        source={{ uri: 'https://customer-assets.emergentagent.com/job_7a9dd132-a732-436b-84ea-9628edec4c9e/artifacts/f12scp1o_1760465336601.png' }}
        style={styles.backgroundImage}
        blurRadius={3}
      />
      
      <View style={styles.overlay} />

      <View style={styles.content}>
        {/* Header with Logo */}
        <View style={styles.header}>
          <Image
            source={{ uri: 'https://customer-assets.emergentagent.com/job_7a9dd132-a732-436b-84ea-9628edec4c9e/artifacts/ugutvh86_IMG_7819.jpeg' }}
            style={styles.logoImage}
            resizeMode="contain"
          />
          <Text style={styles.subtitle}>A DRAGON KARAU AI Radio</Text>
        </View>

        {/* Now Playing Card */}
        {!showDisclaimer && nowPlaying && (
          <View style={styles.nowPlayingCard}>
            <Text style={styles.nowPlayingLabel}>NOW PLAYING</Text>
            
            <View style={styles.stationInfo}>
              <View style={styles.stationTextContainer}>
                <Text style={styles.stationName} numberOfLines={2}>
                  {nowPlaying.standard_display_name || nowPlaying.name}
                </Text>
                {nowPlaying.call_sign && (
                  <Text style={styles.callSign}>{nowPlaying.call_sign}</Text>
                )}
                <Text style={styles.stationMeta}>
                  {nowPlaying.country} • Quality: {nowPlaying.quality_score}
                </Text>
              </View>

              <TouchableOpacity
                style={styles.playButton}
                onPress={togglePlayPause}
              >
                <Ionicons
                  name={isPlaying ? 'pause' : 'play'}
                  size={48}
                  color="#fff"
                />
              </TouchableOpacity>
            </View>

            {/* Dragon Icon & Favorite Button */}
            <View style={styles.dragonIconContainer}>
              <Text style={styles.dragonIcon}>🐉</Text>
              <TouchableOpacity
                style={styles.favoriteButton}
                onPress={toggleFavorite}
              >
                <Ionicons
                  name={isFavorite ? 'heart' : 'heart-outline'}
                  size={24}
                  color={isFavorite ? '#FF6B35' : '#8B92B0'}
                />
                <Text style={[styles.favoriteText, isFavorite && styles.favoriteTextActive]}>
                  {isFavorite ? 'Favorited' : 'Add to Favorites'}
                </Text>
              </TouchableOpacity>
            </View>
          </View>
        )}

        {/* Global Search */}
        {!showDisclaimer && disclaimerAccepted && (
          <View style={styles.searchSection}>
            <Text style={styles.searchTitle}>Search Global Stations</Text>
            
            <View style={styles.searchContainer}>
              <Ionicons name="search" size={20} color="#8B92B0" style={styles.searchIcon} />
              <TextInput
                style={styles.searchInput}
                placeholder="Station name, country, or call sign..."
                placeholderTextColor="#8B92B0"
                value={searchQuery}
                onChangeText={setSearchQuery}
                onSubmitEditing={handleSearch}
                returnKeyType="search"
              />
              {searchQuery ? (
                <TouchableOpacity onPress={() => { setSearchQuery(''); setSearchResults([]); }}>
                  <Ionicons name="close-circle" size={20} color="#8B92B0" />
                </TouchableOpacity>
              ) : null}
            </View>

            <TouchableOpacity
              style={styles.searchButton}
              onPress={handleSearch}
              disabled={loading}
            >
              {loading ? (
                <ActivityIndicator color="#fff" />
              ) : (
                <Text style={styles.searchButtonText}>Search</Text>
              )}
            </TouchableOpacity>

            {/* Search Results */}
            {searchResults.length > 0 && (
              <ScrollView style={styles.resultsContainer}>
                {searchResults.map((station) => (
                  <TouchableOpacity
                    key={station.id}
                    style={styles.resultCard}
                    onPress={() => playStation(station)}
                  >
                    <View style={styles.resultInfo}>
                      <Text style={styles.resultName} numberOfLines={1}>
                        {station.standard_display_name || station.name}
                      </Text>
                      {station.call_sign && (
                        <Text style={styles.resultCallSign}>{station.call_sign}</Text>
                      )}
                      <Text style={styles.resultMeta}>
                        {station.country} • {station.quality_score}
                      </Text>
                    </View>
                    <Ionicons name="play-circle" size={32} color="#FF6B35" />
                  </TouchableOpacity>
                ))}
              </ScrollView>
            )}
          </View>
        )}

        {/* Action Buttons */}
        {!showDisclaimer && disclaimerAccepted && (
          <View style={styles.actionButtons}>
            <TouchableOpacity
              style={styles.browseAllButton}
              onPress={() => router.push('/stations-browser')}
            >
              <Ionicons name="globe-outline" size={20} color="#fff" />
              <Text style={styles.browseAllText}>Browse Stations</Text>
            </TouchableOpacity>
            
            <TouchableOpacity
              style={styles.favoritesNavButton}
              onPress={() => router.push('/favorites')}
            >
              <Ionicons name="heart" size={20} color="#000" />
              <Text style={styles.favoritesNavText}>My Favorites</Text>
            </TouchableOpacity>
          </View>
        )}
      </View>

      {/* Disclaimer Modal */}
      <Modal
        visible={showDisclaimer}
        animationType="fade"
        transparent={true}
      >
        <View style={styles.modalOverlay}>
          <View style={styles.disclaimerCard}>
            <Ionicons name="alert-circle" size={64} color="#FF6B35" />
            
            <Text style={styles.disclaimerTitle}>Content Disclaimer Required</Text>
            
            <ScrollView style={styles.disclaimerScroll}>
              <Text style={styles.disclaimerText}>
                Welcome to KAGEMA-FM, powered by Dragon KARAU AI.
                {'\n\n'}
                By using this application, you acknowledge that:
                {'\n\n'}
                • Radio content is provided by third-party broadcasters
                {'\n'}
                • We do not control or moderate station content
                {'\n'}
                • Content may vary by region and broadcaster
                {'\n'}
                • Some stations may contain mature content
                {'\n'}
                • Streaming quality depends on source and connection
                {'\n\n'}
                This is a radio aggregation service. All content rights belong to respective broadcasters.
              </Text>
            </ScrollView>

            <TouchableOpacity
              style={styles.acceptButton}
              onPress={acceptDisclaimer}
            >
              <Text style={styles.acceptButtonText}>I Accept & Continue</Text>
            </TouchableOpacity>
          </View>
        </View>
      </Modal>

      {loading && !searchQuery && (
        <View style={styles.loadingOverlay}>
          <ActivityIndicator size="large" color="#FF6B35" />
          <Text style={styles.loadingText}>Loading station...</Text>
        </View>
      )}
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#0A0E27',
  },
  backgroundImage: {
    position: 'absolute',
    width: width,
    height: height,
    opacity: 0.3,
  },
  overlay: {
    position: 'absolute',
    width: width,
    height: height,
    backgroundColor: 'rgba(10, 14, 39, 0.85)',
  },
  content: {
    flex: 1,
    padding: 20,
  },
  header: {
    alignItems: 'center',
    marginTop: 20,
    marginBottom: 40,
  },
  logoImage: {
    width: 280,
    height: 280,
    marginBottom: 16,
  },
  subtitle: {
    fontSize: 16,
    color: '#FF6B35',
    marginTop: 8,
    letterSpacing: 3,
    textTransform: 'uppercase',
    fontWeight: '700',
  },
  nowPlayingCard: {
    backgroundColor: 'rgba(26, 31, 58, 0.95)',
    borderRadius: 20,
    padding: 24,
    marginBottom: 32,
    borderWidth: 1,
    borderColor: 'rgba(255, 107, 53, 0.3)',
    shadowColor: '#FF6B35',
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.3,
    shadowRadius: 12,
  },
  nowPlayingLabel: {
    fontSize: 12,
    color: '#FF6B35',
    fontWeight: '700',
    letterSpacing: 2,
    marginBottom: 16,
  },
  stationInfo: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
  },
  stationTextContainer: {
    flex: 1,
    marginRight: 16,
  },
  stationName: {
    fontSize: 24,
    fontWeight: '700',
    color: '#fff',
    marginBottom: 8,
  },
  callSign: {
    fontSize: 16,
    color: '#FF6B35',
    fontWeight: '700',
    marginBottom: 4,
  },
  stationMeta: {
    fontSize: 12,
    color: '#8B92B0',
  },
  playButton: {
    width: 80,
    height: 80,
    borderRadius: 40,
    backgroundColor: '#FF6B35',
    justifyContent: 'center',
    alignItems: 'center',
    shadowColor: '#FF6B35',
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.5,
    shadowRadius: 12,
  },
  dragonIconContainer: {
    alignItems: 'center',
    marginTop: 16,
  },
  dragonIcon: {
    fontSize: 32,
    marginBottom: 12,
  },
  favoriteButton: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: 'rgba(139, 146, 176, 0.2)',
    paddingVertical: 10,
    paddingHorizontal: 20,
    borderRadius: 20,
    borderWidth: 1,
    borderColor: 'rgba(139, 146, 176, 0.3)',
    gap: 8,
  },
  favoriteText: {
    color: '#8B92B0',
    fontSize: 14,
    fontWeight: '600',
  },
  favoriteTextActive: {
    color: '#FF6B35',
  },
  searchSection: {
    marginBottom: 24,
  },
  searchTitle: {
    fontSize: 18,
    fontWeight: '700',
    color: '#fff',
    marginBottom: 16,
  },
  searchContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: 'rgba(26, 31, 58, 0.95)',
    borderRadius: 12,
    paddingHorizontal: 16,
    marginBottom: 12,
    borderWidth: 1,
    borderColor: 'rgba(139, 146, 176, 0.2)',
  },
  searchIcon: {
    marginRight: 8,
  },
  searchInput: {
    flex: 1,
    height: 50,
    fontSize: 16,
    color: '#fff',
  },
  searchButton: {
    backgroundColor: '#FF6B35',
    borderRadius: 12,
    height: 50,
    justifyContent: 'center',
    alignItems: 'center',
    shadowColor: '#FF6B35',
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.3,
    shadowRadius: 8,
  },
  searchButtonText: {
    color: '#fff',
    fontSize: 16,
    fontWeight: '700',
  },
  resultsContainer: {
    maxHeight: 300,
    marginTop: 16,
  },
  resultCard: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    backgroundColor: 'rgba(26, 31, 58, 0.95)',
    borderRadius: 12,
    padding: 16,
    marginBottom: 8,
    borderWidth: 1,
    borderColor: 'rgba(139, 146, 176, 0.2)',
  },
  resultInfo: {
    flex: 1,
    marginRight: 12,
  },
  resultName: {
    fontSize: 16,
    fontWeight: '600',
    color: '#fff',
    marginBottom: 4,
  },
  resultCallSign: {
    fontSize: 14,
    color: '#FF6B35',
    fontWeight: '700',
    marginBottom: 2,
  },
  resultMeta: {
    fontSize: 12,
    color: '#8B92B0',
  },
  actionButtons: {
    flexDirection: 'row',
    gap: 12,
    marginTop: 8,
  },
  browseAllButton: {
    flex: 1,
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    backgroundColor: 'rgba(26, 31, 58, 0.95)',
    borderRadius: 12,
    padding: 16,
    borderWidth: 1,
    borderColor: '#FF6B35',
    gap: 8,
  },
  browseAllText: {
    color: '#fff',
    fontSize: 16,
    fontWeight: '600',
  },
  favoritesNavButton: {
    flex: 1,
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    backgroundColor: '#FFFFFF',
    borderRadius: 12,
    padding: 16,
    gap: 8,
  },
  favoritesNavText: {
    color: '#000000',
    fontSize: 16,
    fontWeight: '600',
  },
  modalOverlay: {
    flex: 1,
    backgroundColor: 'rgba(0, 0, 0, 0.95)',
    justifyContent: 'center',
    alignItems: 'center',
    padding: 20,
  },
  disclaimerCard: {
    backgroundColor: '#1A1F3A',
    borderRadius: 20,
    padding: 32,
    width: '100%',
    maxWidth: 500,
    alignItems: 'center',
    borderWidth: 2,
    borderColor: '#FF6B35',
  },
  disclaimerTitle: {
    fontSize: 24,
    fontWeight: '700',
    color: '#fff',
    marginTop: 16,
    marginBottom: 16,
    textAlign: 'center',
  },
  disclaimerScroll: {
    maxHeight: 300,
    marginBottom: 24,
  },
  disclaimerText: {
    fontSize: 14,
    color: '#8B92B0',
    lineHeight: 22,
    textAlign: 'center',
  },
  acceptButton: {
    backgroundColor: '#FF6B35',
    borderRadius: 12,
    paddingVertical: 16,
    paddingHorizontal: 32,
    width: '100%',
    shadowColor: '#FF6B35',
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.5,
    shadowRadius: 12,
  },
  acceptButtonText: {
    color: '#fff',
    fontSize: 18,
    fontWeight: '700',
    textAlign: 'center',
  },
  loadingOverlay: {
    position: 'absolute',
    top: 0,
    left: 0,
    right: 0,
    bottom: 0,
    backgroundColor: 'rgba(10, 14, 39, 0.9)',
    justifyContent: 'center',
    alignItems: 'center',
  },
  loadingText: {
    color: '#fff',
    fontSize: 16,
    marginTop: 16,
  },
});
