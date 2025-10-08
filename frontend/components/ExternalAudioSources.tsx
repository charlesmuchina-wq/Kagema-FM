// External Audio Sources Component
// Browse and play content from external audio platforms

import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  StyleSheet,
  TouchableOpacity,
  FlatList,
  TextInput,
  ActivityIndicator,
  Alert,
  Modal,
  ScrollView,
  SafeAreaView
} from 'react-native';
import ExternalAudioService, { AudioTrack, AudioSource } from '../services/ExternalAudioService';
import { shadowStyles } from '../utils/shadowStyles';

interface ExternalAudioSourcesProps {
  visible: boolean;
  onClose: () => void;
  onPlayTrack: (track: AudioTrack) => void;
}

const ExternalAudioSources: React.FC<ExternalAudioSourcesProps> = ({
  visible,
  onClose,
  onPlayTrack
}) => {
  const [sources, setSources] = useState<AudioSource[]>([]);
  const [selectedSource, setSelectedSource] = useState<AudioSource | null>(null);
  const [tracks, setTracks] = useState<AudioTrack[]>([]);
  const [loading, setLoading] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedGenre, setSelectedGenre] = useState('');
  const [selectedCountry, setSelectedCountry] = useState('');
  const [viewMode, setViewMode] = useState<'sources' | 'browse' | 'search'>('sources');

  const genres = [
    'Rock', 'Pop', 'Jazz', 'Classical', 'Electronic', 'Folk', 'Country', 
    'Hip Hop', 'Blues', 'Reggae', 'Ambient', 'Acoustic', 'Corporate'
  ];

  const countries = [
    'USA', 'Canada', 'UK', 'Germany', 'France', 'Italy', 'Spain', 'Netherlands',
    'Brazil', 'Kenya', 'South Africa', 'Nigeria', 'Morocco', 'Egypt',
    'Australia', 'New Zealand', 'Japan', 'China', 'India', 'Jamaica', 'Haiti'
  ];

  useEffect(() => {
    if (visible) {
      loadSources();
      detectUserLocation();
    }
  }, [visible]);

  const detectUserLocation = async () => {
    try {
      // Try to get user's location and detect country
      if (navigator.geolocation) {
        navigator.geolocation.getCurrentPosition(
          async (position) => {
            const { latitude, longitude } = position.coords;
            
            // Call the backend to get location info
            const response = await fetch(`${process.env.EXPO_PUBLIC_BACKEND_URL}/api/googlemaps/reverse-geocode`, {
              method: 'POST',
              headers: { 'Content-Type': 'application/json' },
              body: JSON.stringify({ latitude, longitude })
            });
            
            if (response.ok) {
              const data = await response.json();
              if (data.address && data.address.address_components) {
                const countryComponent = data.address.address_components.find(
                  (component: any) => component.types.includes('country')
                );
                
                if (countryComponent) {
                  const detectedCountry = getCountryMapping(countryComponent.long_name);
                  if (detectedCountry && countries.includes(detectedCountry)) {
                    setSelectedCountry(detectedCountry);
                    console.log('🌍 Auto-detected country:', detectedCountry);
                  }
                }
              }
            }
          },
          (error) => {
            console.log('🗺️ Location detection failed, using default:', error.message);
          },
          { timeout: 5000, enableHighAccuracy: false }
        );
      }
    } catch (error) {
      console.log('🗺️ Location detection not available:', error);
    }
  };

  const getCountryMapping = (countryName: string): string => {
    const countryMap: { [key: string]: string } = {
      'United States': 'USA',
      'United Kingdom': 'UK',
      'Deutschland': 'Germany',
      'Brasil': 'Brazil',
      'Kenia': 'Kenya'
    };
    
    return countryMap[countryName] || countryName;
  };

  const loadSources = () => {
    const audioSources = ExternalAudioService.getAudioSources();
    setSources(audioSources);
  };

  const handleSourceSelect = async (source: AudioSource) => {
    setSelectedSource(source);
    setViewMode('browse');
    setLoading(true);
    
    try {
      // Load popular tracks from the selected source
      const popularTracks = await ExternalAudioService.getPopularTracks(source.id, 20);
      setTracks(popularTracks);
    } catch (error) {
      console.error('Error loading tracks:', error);
      Alert.alert('Error', 'Failed to load tracks from this source');
    } finally {
      setLoading(false);
    }
  };

  const handleSearch = async () => {
    if (!searchQuery.trim()) {
      Alert.alert('Search', 'Please enter a search term');
      return;
    }

    setLoading(true);
    setViewMode('search');

    try {
      let sourceId = selectedSource?.id;
      
      // If a country is selected, use appropriate regional source
      if (selectedCountry && !sourceId) {
        sourceId = getSourceForCountry(selectedCountry);
      }

      const searchResults = await ExternalAudioService.searchTracks(searchQuery, sourceId);
      setTracks(searchResults);
    } catch (error) {
      console.error('Search error:', error);
      Alert.alert('Error', 'Failed to search tracks');
    } finally {
      setLoading(false);
    }
  };

  const getSourceForCountry = (country: string): string => {
    const countrySourceMap: { [key: string]: string } = {
      'USA': 'iheart',
      'Canada': 'north_america_radio',
      'UK': 'bbc_sounds',
      'Germany': 'europe_radio',
      'France': 'radiofrance',
      'Italy': 'europe_radio',
      'Spain': 'europe_radio',
      'Netherlands': 'europe_radio',
      'Brazil': 'latin_america',
      'Kenya': 'kenya_radio',
      'South Africa': 'central_south_africa_radio',
      'Nigeria': 'central_south_africa_radio',
      'Morocco': 'north_africa_radio',
      'Egypt': 'north_africa_radio',
      'Australia': 'australia_radio',
      'New Zealand': 'new_zealand_radio',
      'Jamaica': 'caribbean_radio',
      'Haiti': 'caribbean_radio'
    };
    
    return countrySourceMap[country] || 'radio.net';
  };

  const handleGenreSelect = async (genre: string) => {
    setSelectedGenre(genre);
    setLoading(true);

    try {
      const sourceId = selectedSource?.id;
      const genreTracks = await ExternalAudioService.getTracksByGenre(genre, sourceId, 20);
      setTracks(genreTracks);
    } catch (error) {
      console.error('Genre error:', error);
      Alert.alert('Error', 'Failed to load tracks for this genre');
    } finally {
      setLoading(false);
    }
  };

  const handlePlayTrack = async (track: AudioTrack) => {
    try {
      // Validate stream URL before playing
      const isValid = await ExternalAudioService.validateStreamUrl(track.streamUrl);
      
      if (isValid) {
        onPlayTrack(track);
        Alert.alert(
          'Now Playing',
          `${track.title} by ${track.artist}\n${track.attribution || `From ${track.source}`}`,
          [{ text: 'OK' }]
        );
      } else {
        Alert.alert('Playback Error', 'This track is currently unavailable');
      }
    } catch (error) {
      console.error('Playback error:', error);
      Alert.alert('Error', 'Failed to play this track');
    }
  };

  const handleBackToSources = () => {
    setViewMode('sources');
    setSelectedSource(null);
    setTracks([]);
    setSearchQuery('');
    setSelectedGenre('');
  };

  const renderSourceItem = ({ item }: { item: AudioSource }) => (
    <TouchableOpacity
      style={styles.sourceCard}
      onPress={() => handleSourceSelect(item)}
    >
      <View style={styles.sourceHeader}>
        <Text style={styles.sourceName}>{item.name}</Text>
        {item.requiresAttribution && (
          <Text style={styles.attributionBadge}>Attribution Required</Text>
        )}
      </View>
      <Text style={styles.sourceDescription}>{item.description}</Text>
      <View style={styles.sourceFooter}>
        <Text style={styles.exploreText}>Tap to explore →</Text>
      </View>
    </TouchableOpacity>
  );

  const renderTrackItem = ({ item }: { item: AudioTrack }) => (
    <TouchableOpacity
      style={styles.trackCard}
      onPress={() => handlePlayTrack(item)}
    >
      <View style={styles.trackHeader}>
        <Text style={styles.trackTitle} numberOfLines={2}>{item.title}</Text>
        <Text style={styles.trackSource}>{item.source}</Text>
      </View>
      <Text style={styles.trackArtist}>{item.artist}</Text>
      {item.album && <Text style={styles.trackAlbum}>{item.album}</Text>}
      {item.genre && <Text style={styles.trackGenre}>Genre: {item.genre}</Text>}
      <View style={styles.trackFooter}>
        <Text style={styles.trackDuration}>
          {Math.floor(item.duration / 60)}:{(item.duration % 60).toString().padStart(2, '0')}
        </Text>
        {item.license && <Text style={styles.trackLicense}>{item.license}</Text>}
      </View>
      {item.attribution && (
        <Text style={styles.trackAttribution} numberOfLines={1}>
          {item.attribution}
        </Text>
      )}
    </TouchableOpacity>
  );

  const renderGenreItem = ({ item }: { item: string }) => (
    <TouchableOpacity
      style={[
        styles.genreChip,
        selectedGenre === item && styles.selectedGenreChip
      ]}
      onPress={() => handleGenreSelect(item)}
    >
      <Text style={[
        styles.genreText,
        selectedGenre === item && styles.selectedGenreText
      ]}>
        {item}
      </Text>
    </TouchableOpacity>
  );

  return (
    <Modal
      visible={visible}
      animationType="slide"
      presentationStyle="pageSheet"
    >
      <SafeAreaView style={styles.container}>
        <View style={styles.header}>
          <TouchableOpacity onPress={onClose} style={styles.closeButton}>
            <Text style={styles.closeButtonText}>✕</Text>
          </TouchableOpacity>
          <Text style={styles.headerTitle}>
            {viewMode === 'sources' ? 'External Audio Sources' : 
             viewMode === 'browse' ? selectedSource?.name || 'Browse' :
             'Search Results'}
          </Text>
          {viewMode !== 'sources' && (
            <TouchableOpacity onPress={handleBackToSources} style={styles.backButton}>
              <Text style={styles.backButtonText}>← Back</Text>
            </TouchableOpacity>
          )}
        </View>

        {viewMode === 'sources' && (
          <View style={styles.content}>
            <Text style={styles.sectionTitle}>Choose an Audio Source</Text>
            <Text style={styles.sectionSubtitle}>
              Discover music from various external platforms
            </Text>
            
            <FlatList
              data={sources}
              renderItem={renderSourceItem}
              keyExtractor={(item) => item.id}
              showsVerticalScrollIndicator={false}
              contentContainerStyle={styles.sourcesList}
            />
          </View>
        )}

        {(viewMode === 'browse' || viewMode === 'search') && (
          <View style={styles.content}>
            {/* Search Bar */}
            <View style={styles.searchContainer}>
              <TextInput
                style={styles.searchInput}
                placeholder="Search for music..."
                value={searchQuery}
                onChangeText={setSearchQuery}
                onSubmitEditing={handleSearch}
                returnKeyType="search"
              />
              <TouchableOpacity
                style={styles.searchButton}
                onPress={handleSearch}
                disabled={loading}
              >
                <Text style={styles.searchButtonText}>Search</Text>
              </TouchableOpacity>
            </View>

            {/* Country Filter */}
            <View style={styles.genresContainer}>
              <Text style={styles.genresTitle}>Filter by Country:</Text>
              <FlatList
                data={['All Countries', ...countries]}
                renderItem={({ item }) => (
                  <TouchableOpacity
                    style={[
                      styles.genreButton,
                      (item === 'All Countries' ? !selectedCountry : selectedCountry === item) && styles.genreButtonActive
                    ]}
                    onPress={() => setSelectedCountry(item === 'All Countries' ? '' : item)}
                  >
                    <Text style={[
                      styles.genreButtonText,
                      (item === 'All Countries' ? !selectedCountry : selectedCountry === item) && styles.genreButtonTextActive
                    ]}>
                      {item}
                    </Text>
                  </TouchableOpacity>
                )}
                keyExtractor={(item) => item}
                horizontal
                showsHorizontalScrollIndicator={false}
                contentContainerStyle={styles.genresList}
              />
            </View>

            {/* Genre Filters */}
            <View style={styles.genresContainer}>
              <Text style={styles.genresTitle}>Browse by Genre:</Text>
              <FlatList
                data={genres}
                renderItem={renderGenreItem}
                keyExtractor={(item) => item}
                horizontal
                showsHorizontalScrollIndicator={false}
                contentContainerStyle={styles.genresList}
              />
            </View>

            {/* Loading Indicator */}
            {loading && (
              <View style={styles.loadingContainer}>
                <ActivityIndicator size="large" color="#007AFF" />
                <Text style={styles.loadingText}>Loading tracks...</Text>
              </View>
            )}

            {/* Tracks List */}
            {!loading && tracks.length > 0 && (
              <FlatList
                data={tracks}
                renderItem={renderTrackItem}
                keyExtractor={(item) => item.id}
                showsVerticalScrollIndicator={false}
                contentContainerStyle={styles.tracksList}
              />
            )}

            {/* Empty State */}
            {!loading && tracks.length === 0 && viewMode === 'search' && (
              <View style={styles.emptyContainer}>
                <Text style={styles.emptyTitle}>No tracks found</Text>
                <Text style={styles.emptyText}>
                  Try searching with different keywords or browse by genre
                </Text>
              </View>
            )}
          </View>
        )}
      </SafeAreaView>
    </Modal>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f5f5f5',
  },
  header: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingHorizontal: 16,
    paddingVertical: 12,
    backgroundColor: '#fff',
    borderBottomWidth: 1,
    borderBottomColor: '#e0e0e0',
    minHeight: 60,
  },
  closeButton: {
    width: 32,
    height: 32,
    borderRadius: 16,
    backgroundColor: '#f0f0f0',
    justifyContent: 'center',
    alignItems: 'center',
  },
  closeButtonText: {
    fontSize: 16,
    fontWeight: 'bold',
    color: '#666',
  },
  headerTitle: {
    flex: 1,
    fontSize: 18,
    fontWeight: 'bold',
    textAlign: 'center',
    color: '#333',
  },
  backButton: {
    paddingHorizontal: 12,
    paddingVertical: 6,
    borderRadius: 12,
    backgroundColor: '#007AFF',
  },
  backButtonText: {
    color: 'white',
    fontSize: 14,
    fontWeight: '600',
  },
  content: {
    flex: 1,
    paddingHorizontal: 16,
  },
  sectionTitle: {
    fontSize: 20,
    fontWeight: 'bold',
    color: '#333',
    marginTop: 20,
    marginBottom: 8,
  },
  sectionSubtitle: {
    fontSize: 14,
    color: '#666',
    marginBottom: 20,
  },
  sourcesList: {
    paddingBottom: 20,
  },
  sourceCard: {
    backgroundColor: '#fff',
    borderRadius: 12,
    padding: 16,
    marginBottom: 12,
    ...shadowStyles.medium,
  },
  sourceHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 8,
  },
  sourceName: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#333',
  },
  attributionBadge: {
    fontSize: 10,
    color: '#FF6B35',
    backgroundColor: '#FFF2EC',
    paddingHorizontal: 8,
    paddingVertical: 4,
    borderRadius: 8,
    fontWeight: '600',
  },
  sourceDescription: {
    fontSize: 14,
    color: '#666',
    marginBottom: 12,
    lineHeight: 20,
  },
  sourceFooter: {
    alignItems: 'flex-end',
  },
  exploreText: {
    fontSize: 14,
    color: '#007AFF',
    fontWeight: '600',
  },
  searchContainer: {
    flexDirection: 'row',
    marginTop: 16,
    marginBottom: 16,
    gap: 12,
  },
  searchInput: {
    flex: 1,
    height: 40,
    borderWidth: 1,
    borderColor: '#ddd',
    borderRadius: 8,
    paddingHorizontal: 12,
    backgroundColor: '#fff',
    fontSize: 16,
  },
  searchButton: {
    backgroundColor: '#007AFF',
    paddingHorizontal: 16,
    paddingVertical: 10,
    borderRadius: 8,
    justifyContent: 'center',
  },
  searchButtonText: {
    color: 'white',
    fontWeight: '600',
    fontSize: 14,
  },
  genresContainer: {
    marginBottom: 16,
  },
  genresTitle: {
    fontSize: 16,
    fontWeight: '600',
    color: '#333',
    marginBottom: 12,
  },
  genresList: {
    paddingRight: 16,
  },
  genreChip: {
    backgroundColor: '#fff',
    paddingHorizontal: 16,
    paddingVertical: 8,
    borderRadius: 20,
    marginRight: 8,
    borderWidth: 1,
    borderColor: '#ddd',
  },
  selectedGenreChip: {
    backgroundColor: '#007AFF',
    borderColor: '#007AFF',
  },
  genreText: {
    fontSize: 14,
    color: '#333',
    fontWeight: '500',
  },
  selectedGenreText: {
    color: 'white',
  },
  loadingContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
  },
  loadingText: {
    marginTop: 12,
    fontSize: 16,
    color: '#666',
  },
  tracksList: {
    paddingBottom: 20,
  },
  trackCard: {
    backgroundColor: '#fff',
    borderRadius: 12,
    padding: 16,
    marginBottom: 12,
    ...shadowStyles.small,
  },
  trackHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'flex-start',
    marginBottom: 4,
  },
  trackTitle: {
    flex: 1,
    fontSize: 16,
    fontWeight: 'bold',
    color: '#333',
    marginRight: 8,
  },
  trackSource: {
    fontSize: 12,
    color: '#007AFF',
    fontWeight: '600',
    backgroundColor: '#F0F8FF',
    paddingHorizontal: 8,
    paddingVertical: 2,
    borderRadius: 8,
  },
  trackArtist: {
    fontSize: 14,
    color: '#666',
    marginBottom: 2,
  },
  trackAlbum: {
    fontSize: 12,
    color: '#999',
    marginBottom: 4,
  },
  trackGenre: {
    fontSize: 12,
    color: '#999',
    marginBottom: 8,
  },
  trackFooter: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 4,
  },
  trackDuration: {
    fontSize: 12,
    color: '#666',
    fontWeight: '500',
  },
  trackLicense: {
    fontSize: 10,
    color: '#FF6B35',
    backgroundColor: '#FFF2EC',
    paddingHorizontal: 6,
    paddingVertical: 2,
    borderRadius: 6,
  },
  trackAttribution: {
    fontSize: 10,
    color: '#999',
    fontStyle: 'italic',
  },
  emptyContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    paddingHorizontal: 32,
  },
  emptyTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#333',
    marginBottom: 8,
  },
  emptyText: {
    fontSize: 14,
    color: '#666',
    textAlign: 'center',
    lineHeight: 20,
  },
});

export default ExternalAudioSources;