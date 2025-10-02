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
  TextInput,
  Platform,
} from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { useTheme } from '../contexts/ThemeContext';
import { RadioGardenService, RadioGardenPlace, RadioGardenStation } from '../services/RadioGardenService';

const { width, height } = Dimensions.get('window');

interface RadioGardenMapProps {
  visible: boolean;
  onClose: () => void;
  onStationSelect?: (station: RadioGardenStation) => void;
}

export const RadioGardenMap: React.FC<RadioGardenMapProps> = ({
  visible,
  onClose,
  onStationSelect,
}) => {
  const { colors, isDark } = useTheme();
  const radioGarden = RadioGardenService.getInstance();
  
  // State
  const [places, setPlaces] = useState<RadioGardenPlace[]>([]);
  const [selectedPlace, setSelectedPlace] = useState<RadioGardenPlace | null>(null);
  const [stations, setStations] = useState<RadioGardenStation[]>([]);
  const [searchQuery, setSearchQuery] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [loadingStations, setLoadingStations] = useState(false);
  const [currentView, setCurrentView] = useState<'map' | 'search' | 'stations'>('map');
  const [nearbyPlaces, setNearbyPlaces] = useState<RadioGardenPlace[]>([]);
  
  // Map simulation data (for visual representation)
  const [mapRegion, setMapRegion] = useState({
    latitude: 0,
    longitude: 0,
    zoom: 1
  });

  useEffect(() => {
    if (visible) {
      initializeRadioGarden();
    }
  }, [visible]);

  const initializeRadioGarden = async () => {
    setIsLoading(true);
    try {
      console.log('🗺️ Initializing Radio Garden Map...');
      
      await radioGarden.initialize();
      
      // Get popular places
      const popularPlaces = await radioGarden.getPopularPlaces();
      setPlaces(popularPlaces);
      
      // Get nearby places (simulated current location: Nairobi)
      const nearby = await radioGarden.getNearbyPlaces(-1.286389, 36.817223);
      setNearbyPlaces(nearby.slice(0, 10));
      
      console.log('✅ Radio Garden Map initialized with', popularPlaces.length, 'places');
    } catch (error) {
      console.error('❌ Error initializing Radio Garden:', error);
      Alert.alert('Error', 'Failed to load Radio Garden data. Using cached stations.');
      
      // Use fallback data
      setPlaces([
        {
          id: 'nairobi',
          title: 'Nairobi',
          country: 'Kenya',
          size: 15,
          geo: [-1.286389, 36.817223],
          stations: []
        },
        {
          id: 'london',
          title: 'London',
          country: 'United Kingdom', 
          size: 45,
          geo: [51.5074, -0.1278],
          stations: []
        },
        {
          id: 'new-york',
          title: 'New York',
          country: 'United States',
          size: 38,
          geo: [40.7128, -74.0060],
          stations: []
        }
      ]);
    } finally {
      setIsLoading(false);
    }
  };

  const handlePlaceSelect = async (place: RadioGardenPlace) => {
    setSelectedPlace(place);
    setLoadingStations(true);
    setCurrentView('stations');
    
    try {
      console.log('📻 Loading stations for', place.title, place.country);
      
      const placeStations = await radioGarden.getStationsForPlace(place.id);
      setStations(placeStations);
      
      console.log('✅ Loaded', placeStations.length, 'stations for', place.title);
    } catch (error) {
      console.error('❌ Error loading stations:', error);
      Alert.alert('Error', `Failed to load stations for ${place.title}`);
      setStations([]);
    } finally {
      setLoadingStations(false);
    }
  };

  const handleStationPlay = (station: RadioGardenStation) => {
    console.log('🎵 Playing station:', station.title, 'from', station.place);
    
    Alert.alert(
      'Play Station?',
      `Start playing ${station.title} from ${station.place}, ${station.country}?`,
      [
        { text: 'Cancel', style: 'cancel' },
        {
          text: 'Play',
          onPress: () => {
            onStationSelect?.(station);
            onClose();
          }
        }
      ]
    );
  };

  const handleSearch = async () => {
    if (!searchQuery.trim()) return;
    
    setIsLoading(true);
    try {
      const results = await radioGarden.searchPlaces(searchQuery);
      setPlaces(results);
      setCurrentView('search');
      console.log('🔍 Search results for', searchQuery, ':', results.length, 'places');
    } catch (error) {
      console.error('❌ Search error:', error);
      Alert.alert('Search Error', 'Failed to search places. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  const renderMapView = () => (
    <View style={styles.mapContainer}>
      {/* Simulated World Map */}
      <View style={styles.worldMap}>
        <Text style={[styles.mapTitle, { color: colors.text }]}>
          🌍 Radio Garden World Map
        </Text>
        <Text style={[styles.mapSubtitle, { color: colors.textSecondary }]}>
          Tap on places to explore radio stations
        </Text>
        
        {/* Interactive Points */}
        <View style={styles.mapPoints}>
          {places.slice(0, 12).map((place, index) => (
            <TouchableOpacity
              key={place.id}
              style={[
                styles.mapPoint,
                { 
                  backgroundColor: colors.primary,
                  left: `${(place.geo[1] + 180) / 3.6}%`,
                  top: `${(90 - place.geo[0]) / 1.8}%`
                }
              ]}
              onPress={() => handlePlaceSelect(place)}
            >
              <Text style={styles.mapPointText}>{place.size}</Text>
            </TouchableOpacity>
          ))}
        </View>
        
        {/* Map Controls */}
        <View style={styles.mapControls}>
          <TouchableOpacity style={[styles.mapControlButton, { backgroundColor: colors.surface }]}>
            <Ionicons name="add" size={20} color={colors.text} />
          </TouchableOpacity>
          <TouchableOpacity style={[styles.mapControlButton, { backgroundColor: colors.surface }]}>
            <Ionicons name="remove" size={20} color={colors.text} />
          </TouchableOpacity>
          <TouchableOpacity style={[styles.mapControlButton, { backgroundColor: colors.surface }]}>
            <Ionicons name="locate" size={20} color={colors.text} />
          </TouchableOpacity>
        </View>
      </View>

      {/* Popular Places */}
      <View style={styles.popularPlacesContainer}>
        <Text style={[styles.sectionTitle, { color: colors.text }]}>Popular Places</Text>
        <ScrollView horizontal showsHorizontalScrollIndicator={false}>
          {places.slice(0, 8).map((place) => (
            <TouchableOpacity
              key={place.id}
              style={[styles.placeCard, { backgroundColor: colors.card }]}
              onPress={() => handlePlaceSelect(place)}
            >
              <Text style={[styles.placeTitle, { color: colors.text }]}>{place.title}</Text>
              <Text style={[styles.placeCountry, { color: colors.textSecondary }]}>
                {place.country}
              </Text>
              <Text style={[styles.placeStations, { color: colors.primary }]}>
                {place.size} stations
              </Text>
            </TouchableOpacity>
          ))}
        </ScrollView>
      </View>

      {/* Nearby Places */}
      {nearbyPlaces.length > 0 && (
        <View style={styles.nearbyContainer}>
          <Text style={[styles.sectionTitle, { color: colors.text }]}>Near You</Text>
          <ScrollView horizontal showsHorizontalScrollIndicator={false}>
            {nearbyPlaces.map((place) => (
              <TouchableOpacity
                key={place.id}
                style={[styles.nearbyCard, { backgroundColor: colors.surface }]}
                onPress={() => handlePlaceSelect(place)}
              >
                <Text style={[styles.nearbyTitle, { color: colors.text }]}>{place.title}</Text>
                <Text style={[styles.nearbyCountry, { color: colors.textSecondary }]}>
                  {place.country}
                </Text>
              </TouchableOpacity>
            ))}
          </ScrollView>
        </View>
      )}
    </View>
  );

  const renderStationsView = () => (
    <View style={styles.stationsContainer}>
      {/* Header */}
      <View style={styles.stationsHeader}>
        <TouchableOpacity
          style={styles.backButton}
          onPress={() => setCurrentView('map')}
        >
          <Ionicons name="arrow-back" size={24} color={colors.text} />
        </TouchableOpacity>
        <View style={styles.stationsHeaderText}>
          <Text style={[styles.stationsTitle, { color: colors.text }]}>
            {selectedPlace?.title}
          </Text>
          <Text style={[styles.stationsSubtitle, { color: colors.textSecondary }]}>
            {selectedPlace?.country} • {stations.length} stations
          </Text>
        </View>
      </View>

      {/* Stations List */}
      {loadingStations ? (
        <View style={styles.loadingContainer}>
          <ActivityIndicator size="large" color={colors.primary} />
          <Text style={[styles.loadingText, { color: colors.textSecondary }]}>
            Loading stations...
          </Text>
        </View>
      ) : (
        <ScrollView style={styles.stationsList}>
          {stations.map((station, index) => (
            <TouchableOpacity
              key={station.id}
              style={[styles.stationCard, { backgroundColor: colors.card }]}
              onPress={() => handleStationPlay(station)}
            >
              <View style={styles.stationInfo}>
                <Text style={[styles.stationTitle, { color: colors.text }]}>
                  {station.title}
                </Text>
                {station.subtitle && (
                  <Text style={[styles.stationSubtitle, { color: colors.textSecondary }]}>
                    {station.subtitle}
                  </Text>
                )}
                <Text style={[styles.stationPlace, { color: colors.textSecondary }]}>
                  {station.place}, {station.country}
                </Text>
              </View>
              <TouchableOpacity style={[styles.playButton, { backgroundColor: colors.primary }]}>
                <Ionicons name="play" size={20} color="#fff" />
              </TouchableOpacity>
            </TouchableOpacity>
          ))}
          
          {stations.length === 0 && !loadingStations && (
            <View style={styles.emptyState}>
              <Ionicons name="radio-outline" size={48} color={colors.textSecondary} />
              <Text style={[styles.emptyText, { color: colors.textSecondary }]}>
                No stations available for this location
              </Text>
            </View>
          )}
        </ScrollView>
      )}
    </View>
  );

  const renderSearchView = () => (
    <View style={styles.searchContainer}>
      <Text style={[styles.searchTitle, { color: colors.text }]}>Search Results</Text>
      <Text style={[styles.searchSubtitle, { color: colors.textSecondary }]}>
        Found {places.length} places for "{searchQuery}"
      </Text>
      
      <ScrollView style={styles.searchResults}>
        {places.map((place) => (
          <TouchableOpacity
            key={place.id}
            style={[styles.searchResultCard, { backgroundColor: colors.card }]}
            onPress={() => handlePlaceSelect(place)}
          >
            <View style={styles.searchResultInfo}>
              <Text style={[styles.searchResultTitle, { color: colors.text }]}>
                {place.title}
              </Text>
              <Text style={[styles.searchResultCountry, { color: colors.textSecondary }]}>
                {place.country} • {place.size} stations
              </Text>
            </View>
            <Ionicons name="chevron-forward" size={20} color={colors.textSecondary} />
          </TouchableOpacity>
        ))}
      </ScrollView>
    </View>
  );

  const styles = StyleSheet.create({
    modalOverlay: {
      flex: 1,
      backgroundColor: 'rgba(0,0,0,0.5)',
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
    },
    title: {
      fontSize: 20,
      fontWeight: '600',
      color: colors.text,
    },
    closeButton: {
      padding: 8,
    },
    searchContainer: {
      padding: 16,
      flex: 1,
    },
    searchInputContainer: {
      flexDirection: 'row',
      marginBottom: 16,
    },
    searchInput: {
      flex: 1,
      height: 44,
      borderWidth: 1,
      borderColor: colors.border,
      borderRadius: 8,
      paddingHorizontal: 16,
      backgroundColor: colors.surface,
      color: colors.text,
      marginRight: 8,
    },
    searchButton: {
      width: 44,
      height: 44,
      borderRadius: 8,
      backgroundColor: colors.primary,
      alignItems: 'center',
      justifyContent: 'center',
    },
    tabContainer: {
      flexDirection: 'row',
      borderBottomWidth: 1,
      borderBottomColor: colors.border,
    },
    tab: {
      flex: 1,
      paddingVertical: 12,
      alignItems: 'center',
    },
    activeTab: {
      borderBottomWidth: 2,
      borderBottomColor: colors.primary,
    },
    tabText: {
      fontSize: 14,
      color: colors.textSecondary,
    },
    activeTabText: {
      color: colors.primary,
      fontWeight: '600',
    },
    mapContainer: {
      flex: 1,
      padding: 16,
    },
    worldMap: {
      height: 200,
      backgroundColor: colors.surface,
      borderRadius: 12,
      padding: 16,
      marginBottom: 20,
      position: 'relative',
      overflow: 'hidden',
    },
    mapTitle: {
      fontSize: 18,
      fontWeight: '600',
      textAlign: 'center',
      marginBottom: 4,
    },
    mapSubtitle: {
      fontSize: 12,
      textAlign: 'center',
      marginBottom: 16,
    },
    mapPoints: {
      position: 'absolute',
      top: 60,
      left: 16,
      right: 16,
      bottom: 16,
    },
    mapPoint: {
      position: 'absolute',
      width: 24,
      height: 24,
      borderRadius: 12,
      alignItems: 'center',
      justifyContent: 'center',
    },
    mapPointText: {
      fontSize: 10,
      color: '#fff',
      fontWeight: '600',
    },
    mapControls: {
      position: 'absolute',
      right: 16,
      bottom: 16,
      gap: 8,
    },
    mapControlButton: {
      width: 32,
      height: 32,
      borderRadius: 16,
      alignItems: 'center',
      justifyContent: 'center',
    },
    popularPlacesContainer: {
      marginBottom: 20,
    },
    nearbyContainer: {
      marginBottom: 20,
    },
    sectionTitle: {
      fontSize: 16,
      fontWeight: '600',
      marginBottom: 12,
    },
    placeCard: {
      width: 120,
      padding: 12,
      borderRadius: 8,
      marginRight: 12,
    },
    placeTitle: {
      fontSize: 14,
      fontWeight: '600',
      marginBottom: 4,
    },
    placeCountry: {
      fontSize: 12,
      marginBottom: 4,
    },
    placeStations: {
      fontSize: 12,
      fontWeight: '500',
    },
    nearbyCard: {
      width: 100,
      padding: 10,
      borderRadius: 8,
      marginRight: 10,
    },
    nearbyTitle: {
      fontSize: 12,
      fontWeight: '600',
    },
    nearbyCountry: {
      fontSize: 10,
    },
    stationsContainer: {
      flex: 1,
    },
    stationsHeader: {
      flexDirection: 'row',
      alignItems: 'center',
      padding: 16,
      borderBottomWidth: 1,
      borderBottomColor: colors.border,
    },
    backButton: {
      marginRight: 16,
    },
    stationsHeaderText: {
      flex: 1,
    },
    stationsTitle: {
      fontSize: 18,
      fontWeight: '600',
    },
    stationsSubtitle: {
      fontSize: 14,
      marginTop: 2,
    },
    stationsList: {
      flex: 1,
      padding: 16,
    },
    stationCard: {
      flexDirection: 'row',
      alignItems: 'center',
      padding: 16,
      borderRadius: 8,
      marginBottom: 8,
    },
    stationInfo: {
      flex: 1,
    },
    stationTitle: {
      fontSize: 16,
      fontWeight: '600',
      marginBottom: 4,
    },
    stationSubtitle: {
      fontSize: 14,
      marginBottom: 2,
    },
    stationPlace: {
      fontSize: 12,
    },
    playButton: {
      width: 40,
      height: 40,
      borderRadius: 20,
      alignItems: 'center',
      justifyContent: 'center',
    },
    loadingContainer: {
      flex: 1,
      alignItems: 'center',
      justifyContent: 'center',
      padding: 40,
    },
    loadingText: {
      fontSize: 14,
      marginTop: 12,
    },
    emptyState: {
      alignItems: 'center',
      padding: 40,
    },
    emptyText: {
      fontSize: 16,
      textAlign: 'center',
      marginTop: 16,
    },
    searchTitle: {
      fontSize: 18,
      fontWeight: '600',
      marginBottom: 4,
    },
    searchSubtitle: {
      fontSize: 14,
      marginBottom: 16,
    },
    searchResults: {
      flex: 1,
    },
    searchResultCard: {
      flexDirection: 'row',
      alignItems: 'center',
      padding: 16,
      borderRadius: 8,
      marginBottom: 8,
    },
    searchResultInfo: {
      flex: 1,
    },
    searchResultTitle: {
      fontSize: 16,
      fontWeight: '600',
      marginBottom: 4,
    },
    searchResultCountry: {
      fontSize: 14,
    },
  });

  return (
    <Modal visible={visible} transparent animationType="slide">
      <View style={styles.modalOverlay}>
        <View style={styles.container}>
          {/* Header */}
          <View style={styles.header}>
            <Text style={styles.title}>Radio Garden</Text>
            <TouchableOpacity style={styles.closeButton} onPress={onClose}>
              <Ionicons name="close" size={24} color={colors.text} />
            </TouchableOpacity>
          </View>

          {/* Search */}
          <View style={styles.searchInputContainer}>
            <TextInput
              style={styles.searchInput}
              placeholder="Search places or countries..."
              placeholderTextColor={colors.textSecondary}
              value={searchQuery}
              onChangeText={setSearchQuery}
              onSubmitEditing={handleSearch}
            />
            <TouchableOpacity style={styles.searchButton} onPress={handleSearch}>
              <Ionicons name="search" size={20} color="#fff" />
            </TouchableOpacity>
          </View>

          {/* Tabs */}
          <View style={styles.tabContainer}>
            <TouchableOpacity
              style={[styles.tab, currentView === 'map' && styles.activeTab]}
              onPress={() => setCurrentView('map')}
            >
              <Text style={[styles.tabText, currentView === 'map' && styles.activeTabText]}>
                Map
              </Text>
            </TouchableOpacity>
            <TouchableOpacity
              style={[styles.tab, currentView === 'search' && styles.activeTab]}
              onPress={() => setCurrentView('search')}
            >
              <Text style={[styles.tabText, currentView === 'search' && styles.activeTabText]}>
                Search
              </Text>
            </TouchableOpacity>
            <TouchableOpacity
              style={[styles.tab, currentView === 'stations' && styles.activeTab]}
              onPress={() => setCurrentView('stations')}
            >
              <Text style={[styles.tabText, currentView === 'stations' && styles.activeTabText]}>
                Stations
              </Text>
            </TouchableOpacity>
          </View>

          {/* Loading */}
          {isLoading && (
            <View style={styles.loadingContainer}>
              <ActivityIndicator size="large" color={colors.primary} />
              <Text style={[styles.loadingText, { color: colors.textSecondary }]}>
                Loading Radio Garden...
              </Text>
            </View>
          )}

          {/* Content */}
          {!isLoading && (
            <>
              {currentView === 'map' && renderMapView()}
              {currentView === 'search' && renderSearchView()}
              {currentView === 'stations' && renderStationsView()}
            </>
          )}
        </View>
      </View>
    </Modal>
  );
};