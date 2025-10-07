import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  StyleSheet,
  TouchableOpacity,
  ScrollView,
  FlatList,
  Modal,
  TextInput,
  ActivityIndicator,
  Alert,
  Dimensions,
} from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { useTheme } from '../contexts/ThemeContext';
import { 
  streemaService, 
  StreemaStation, 
  StreemaCountry,
  StreemaSearchResult 
} from '../services/StreemaService';
import { shadowStyles } from '../utils/shadowStyles';

const { width } = Dimensions.get('window');

interface StreemaInterfaceProps {
  visible: boolean;
  onClose: () => void;
  onStationSelect: (station: StreemaStation) => void;
  currentStation?: StreemaStation | null;
  userLocation?: [number, number];
}

export const StreemaInterface: React.FC<StreemaInterfaceProps> = ({
  visible,
  onClose,
  onStationSelect,
  currentStation,
  userLocation
}) => {
  const { colors } = useTheme();
  const [countries, setCountries] = useState<StreemaCountry[]>([]);
  const [selectedCountry, setSelectedCountry] = useState<string>('all');
  const [searchQuery, setSearchQuery] = useState('');
  const [searchResults, setSearchResults] = useState<StreemaStation[]>([]);
  const [favoriteStations, setFavoriteStations] = useState<StreemaStation[]>([]);
  const [loading, setLoading] = useState(true);
  const [searching, setSearching] = useState(false);
  const [activeTab, setActiveTab] = useState<'browse' | 'favorites' | 'search' | 'popular' | 'nearby'>('browse');

  useEffect(() => {
    if (visible) {
      initializeStreema();
    }
  }, [visible]);

  useEffect(() => {
    if (searchQuery.length > 2) {
      handleSearch();
    } else {
      setSearchResults([]);
    }
  }, [searchQuery]);

  const initializeStreema = async () => {
    try {
      setLoading(true);
      await streemaService.initialize();
      
      const countriesList = streemaService.getCountries();
      setCountries(countriesList);
      
      const favorites = streemaService.getFavoriteStations();
      setFavoriteStations(favorites);
      
      const stats = streemaService.getServiceStats();
      console.log('🌍 Streema initialized:', stats);
    } catch (error) {
      console.error('Error initializing Streema:', error);
      Alert.alert('Error', 'Failed to load Streema stations');
    } finally {
      setLoading(false);
    }
  };

  const handleSearch = async () => {
    if (searching) return;
    
    try {
      setSearching(true);
      const result: StreemaSearchResult = await streemaService.searchStations(
        searchQuery,
        selectedCountry === 'all' ? undefined : selectedCountry
      );
      setSearchResults(result.stations);
      console.log(`🔍 Found ${result.totalResults} Streema stations for "${searchQuery}"`);
    } catch (error) {
      console.error('Search error:', error);
    } finally {
      setSearching(false);
    }
  };

  const handleStationPlay = (station: StreemaStation) => {
    console.log('🌍 Playing Streema station:', station.name);
    onStationSelect(station);
    
    Alert.alert(
      'Now Playing',
      `${station.name}${station.frequency ? ` (${station.frequency} ${station.band})` : ''}\n${station.description}\n\nLocation: ${station.city}, ${station.country}\nGenre: ${station.genre}\nLanguage: ${station.language}`,
      [{ text: 'OK' }]
    );
  };

  const toggleFavorite = async (station: StreemaStation) => {
    const isFavorite = streemaService.isFavorite(station.id);
    
    if (isFavorite) {
      await streemaService.removeFromFavorites(station.id);
      Alert.alert('Removed', `${station.name} removed from favorites`);
    } else {
      await streemaService.addToFavorites(station.id);
      Alert.alert('Added', `${station.name} added to favorites`);
    }
    
    // Update favorites list
    const favorites = streemaService.getFavoriteStations();
    setFavoriteStations(favorites);
  };

  const getNearbyStations = (): StreemaStation[] => {
    if (!userLocation) return [];
    return streemaService.getStationsByLocation(userLocation[0], userLocation[1], 200);
  };

  const getDisplayStations = (): StreemaStation[] => {
    switch (activeTab) {
      case 'favorites':
        return favoriteStations;
      case 'search':
        return searchResults;
      case 'popular':
        return streemaService.getPopularStations(20);
      case 'nearby':
        return getNearbyStations();
      case 'browse':
      default:
        if (selectedCountry === 'all') {
          return streemaService.getAllStations();
        }
        return streemaService.getStationsByCountry(selectedCountry);
    }
  };

  const renderStationCard = ({ item: station }: { item: StreemaStation }) => {
    const isCurrentStation = currentStation?.id === station.id;
    const isFavorite = streemaService.isFavorite(station.id);
    
    return (
      <View style={[
        styles.stationCard,
        { backgroundColor: colors.card, borderColor: colors.border },
        isCurrentStation && { borderColor: colors.primary, borderWidth: 2 }
      ]}>
        <View style={styles.stationHeader}>
          <View style={styles.stationInfo}>
            <View style={styles.stationTitleRow}>
              <Text style={[styles.stationName, { color: colors.text }]}>{station.name}</Text>
              <View style={[styles.countryFlag, { backgroundColor: colors.primary + '20' }]}>
                <Text style={styles.flagEmoji}>{countries.find(c => c.code === station.countryCode)?.flag || '🌍'}</Text>
              </View>
            </View>
            
            {station.frequency && (
              <View style={styles.frequencyRow}>
                <Text style={[styles.frequencyText, { color: colors.primary }]}>
                  {station.frequency} {station.band}
                </Text>
              </View>
            )}
            
            <Text style={[styles.stationDescription, { color: colors.textSecondary }]}>
              {station.description}
            </Text>
            
            <View style={styles.stationMeta}>
              <View style={[styles.genreTag, { backgroundColor: colors.success + '20' }]}>
                <Text style={[styles.genreText, { color: colors.success }]}>{station.genre}</Text>
              </View>
              
              <Text style={[styles.locationText, { color: colors.textSecondary }]}>
                {station.city}, {station.country}
              </Text>
            </View>
            
            <View style={styles.stationStats}>
              <Ionicons name="people" size={12} color={colors.textSecondary} />
              <Text style={[styles.listenersText, { color: colors.textSecondary }]}>
                {station.listeners.toLocaleString()} listeners
              </Text>
              <Text style={[styles.bitrateText, { color: colors.textSecondary }]}>
                • {station.bitrate}
              </Text>
              <Text style={[styles.languageText, { color: colors.textSecondary }]}>
                • {station.language}
              </Text>
            </View>
          </View>
          
          <View style={styles.stationActions}>
            <TouchableOpacity
              style={[styles.favoriteButton, { backgroundColor: colors.surface }]}
              onPress={() => toggleFavorite(station)}
            >
              <Ionicons
                name={isFavorite ? 'heart' : 'heart-outline'}
                size={20}
                color={isFavorite ? '#ff4757' : colors.textSecondary}
              />
            </TouchableOpacity>
            
            {station.websiteUrl && (
              <TouchableOpacity
                style={[styles.webButton, { backgroundColor: colors.surface }]}
                onPress={() => Alert.alert('Website', `Visit ${station.name} at ${station.websiteUrl}`)}
              >
                <Ionicons name="globe-outline" size={16} color={colors.textSecondary} />
              </TouchableOpacity>
            )}
            
            <TouchableOpacity
              style={[
                styles.playButton,
                { backgroundColor: colors.primary },
                isCurrentStation && { backgroundColor: colors.success }
              ]}
              onPress={() => handleStationPlay(station)}
            >
              <Ionicons
                name={isCurrentStation ? 'pause' : 'play'}
                size={20}
                color={colors.background}
              />
            </TouchableOpacity>
          </View>
        </View>
      </View>
    );
  };

  const renderCountryTab = (country: StreemaCountry) => (
    <TouchableOpacity
      key={country.code}
      style={[
        styles.countryTab,
        { backgroundColor: selectedCountry === country.code ? colors.primary : colors.surface },
        { borderColor: colors.border }
      ]}
      onPress={() => setSelectedCountry(country.code)}
    >
      <Text style={styles.countryFlag}>{country.flag}</Text>
      <Text
        style={[
          styles.countryTabText,
          { color: selectedCountry === country.code ? colors.background : colors.text }
        ]}
      >
        {country.name}
      </Text>
    </TouchableOpacity>
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
    closeButton: {
      padding: 8,
      borderRadius: 8,
      backgroundColor: colors.surface,
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
      marginHorizontal: 2,
    },
    activeTab: {
      backgroundColor: colors.primary,
    },
    tabText: {
      fontSize: 11,
      fontWeight: '600',
      marginTop: 4,
    },
    activeTabText: {
      color: colors.background,
    },
    searchContainer: {
      padding: 16,
      backgroundColor: colors.surface,
    },
    searchInput: {
      backgroundColor: colors.background,
      borderRadius: 12,
      paddingHorizontal: 16,
      paddingVertical: 12,
      fontSize: 16,
      color: colors.text,
      borderWidth: 1,
      borderColor: colors.border,
    },
    countriesContainer: {
      padding: 16,
      backgroundColor: colors.surface,
    },
    countriesRow: {
      flexDirection: 'row',
      flexWrap: 'wrap',
      gap: 8,
    },
    countryTab: {
      flexDirection: 'row',
      alignItems: 'center',
      paddingHorizontal: 10,
      paddingVertical: 8,
      borderRadius: 8,
      borderWidth: 1,
      gap: 6,
    },
    countryFlag: {
      fontSize: 16,
    },
    countryTabText: {
      fontSize: 12,
      fontWeight: '500',
    },
    content: {
      flex: 1,
    },
    stationCard: {
      margin: 12,
      borderRadius: 16,
      padding: 16,
      borderWidth: 1,
      ...shadowStyles.medium,
    },
    stationHeader: {
      flexDirection: 'row',
      alignItems: 'flex-start',
      justifyContent: 'space-between',
    },
    stationInfo: {
      flex: 1,
      marginRight: 12,
    },
    stationTitleRow: {
      flexDirection: 'row',
      alignItems: 'center',
      marginBottom: 4,
      gap: 8,
    },
    stationName: {
      fontSize: 16,
      fontWeight: '600',
      flex: 1,
    },
    countryFlag: {
      paddingHorizontal: 8,
      paddingVertical: 4,
      borderRadius: 6,
    },
    flagEmoji: {
      fontSize: 16,
    },
    frequencyRow: {
      marginBottom: 4,
    },
    frequencyText: {
      fontSize: 12,
      fontWeight: '600',
    },
    stationDescription: {
      fontSize: 14,
      lineHeight: 20,
      marginBottom: 8,
    },
    stationMeta: {
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
    locationText: {
      fontSize: 12,
    },
    stationStats: {
      flexDirection: 'row',
      alignItems: 'center',
      gap: 4,
      flexWrap: 'wrap',
    },
    listenersText: {
      fontSize: 11,
      marginLeft: 4,
    },
    bitrateText: {
      fontSize: 11,
    },
    languageText: {
      fontSize: 11,
    },
    stationActions: {
      alignItems: 'center',
      gap: 8,
    },
    favoriteButton: {
      width: 32,
      height: 32,
      borderRadius: 16,
      alignItems: 'center',
      justifyContent: 'center',
    },
    webButton: {
      width: 32,
      height: 32,
      borderRadius: 16,
      alignItems: 'center',
      justifyContent: 'center',
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
            <Text style={styles.headerTitle}>🌍 Streema</Text>
            <TouchableOpacity style={styles.closeButton} onPress={onClose}>
              <Ionicons name="close" size={24} color={colors.text} />
            </TouchableOpacity>
          </View>
          <View style={styles.loadingContainer}>
            <ActivityIndicator size="large" color={colors.primary} />
            <Text style={styles.loadingText}>Loading international radio stations...</Text>
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
          <Text style={styles.headerTitle}>🌍 Streema</Text>
          <TouchableOpacity style={styles.closeButton} onPress={onClose}>
            <Ionicons name="close" size={24} color={colors.text} />
          </TouchableOpacity>
        </View>

        {/* Tab Bar */}
        <View style={styles.tabBar}>
          {[
            { id: 'browse', label: 'Browse', icon: 'library' },
            { id: 'popular', label: 'Popular', icon: 'trending-up' },
            { id: 'nearby', label: 'Nearby', icon: 'location' },
            { id: 'favorites', label: 'Favorites', icon: 'heart' },
            { id: 'search', label: 'Search', icon: 'search' },
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
                size={18}
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

        {/* Search Input */}
        {activeTab === 'search' && (
          <View style={styles.searchContainer}>
            <TextInput
              style={styles.searchInput}
              placeholder="Search stations, genres, countries..."
              placeholderTextColor={colors.textSecondary}
              value={searchQuery}
              onChangeText={setSearchQuery}
            />
            {searching && (
              <ActivityIndicator 
                size="small" 
                color={colors.primary} 
                style={{ position: 'absolute', right: 28, top: 28 }} 
              />
            )}
          </View>
        )}

        {/* Country Filter for Browse tab */}
        {activeTab === 'browse' && (
          <View style={styles.countriesContainer}>
            <ScrollView horizontal showsHorizontalScrollIndicator={false}>
              <View style={styles.countriesRow}>
                <TouchableOpacity
                  style={[
                    styles.countryTab,
                    { backgroundColor: selectedCountry === 'all' ? colors.primary : colors.surface },
                    { borderColor: colors.border }
                  ]}
                  onPress={() => setSelectedCountry('all')}
                >
                  <Text style={styles.countryFlag}>🌍</Text>
                  <Text
                    style={[
                      styles.countryTabText,
                      { color: selectedCountry === 'all' ? colors.background : colors.text }
                    ]}
                  >
                    All Countries
                  </Text>
                </TouchableOpacity>
                {countries.map(renderCountryTab)}
              </View>
            </ScrollView>
          </View>
        )}

        {/* Station List */}
        <View style={styles.content}>
          <FlatList
            data={getDisplayStations()}
            renderItem={renderStationCard}
            keyExtractor={(item) => item.id}
            showsVerticalScrollIndicator={false}
            ListEmptyComponent={
              <View style={styles.emptyContainer}>
                <Ionicons name="globe" size={64} color={colors.textSecondary} />
                <Text style={styles.emptyText}>
                  {activeTab === 'search' && searchQuery.length <= 2
                    ? 'Type at least 3 characters to search'
                    : activeTab === 'favorites' && favoriteStations.length === 0
                    ? 'No favorite stations yet\nTap the heart icon to add favorites'
                    : activeTab === 'nearby' && !userLocation
                    ? 'Location access required for nearby stations'
                    : 'No stations found'
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