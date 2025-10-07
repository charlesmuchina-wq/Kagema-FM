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
  iHeartRadioService, 
  iHeartRadioStation, 
  iHeartRadioMarket,
  iHeartRadioSearchResult 
} from '../services/iHeartRadioService';
import { shadowStyles } from '../utils/shadowStyles';

const { width } = Dimensions.get('window');

interface iHeartRadioInterfaceProps {
  visible: boolean;
  onClose: () => void;
  onStationSelect: (station: iHeartRadioStation) => void;
  currentStation?: iHeartRadioStation | null;
  userLocation?: [number, number];
}

export const iHeartRadioInterface: React.FC<iHeartRadioInterfaceProps> = ({
  visible,
  onClose,
  onStationSelect,
  currentStation,
  userLocation
}) => {
  const { colors } = useTheme();
  const [markets, setMarkets] = useState<iHeartRadioMarket[]>([]);
  const [selectedMarket, setSelectedMarket] = useState<string>('all');
  const [searchQuery, setSearchQuery] = useState('');
  const [searchResults, setSearchResults] = useState<iHeartRadioStation[]>([]);
  const [favoriteStations, setFavoriteStations] = useState<iHeartRadioStation[]>([]);
  const [loading, setLoading] = useState(true);
  const [searching, setSearching] = useState(false);
  const [activeTab, setActiveTab] = useState<'browse' | 'favorites' | 'search' | 'nearby'>('browse');

  useEffect(() => {
    if (visible) {
      initializeiHeartRadio();
    }
  }, [visible]);

  useEffect(() => {
    if (searchQuery.length > 2) {
      handleSearch();
    } else {
      setSearchResults([]);
    }
  }, [searchQuery]);

  const initializeiHeartRadio = async () => {
    try {
      setLoading(true);
      await iHeartRadioService.initialize();
      
      const marketsList = iHeartRadioService.getMarkets();
      setMarkets(marketsList);
      
      const favorites = iHeartRadioService.getFavoriteStations();
      setFavoriteStations(favorites);
      
      console.log('📻 iHeartRadio initialized with', marketsList.length, 'markets');
    } catch (error) {
      console.error('Error initializing iHeartRadio:', error);
      Alert.alert('Error', 'Failed to load iHeartRadio stations');
    } finally {
      setLoading(false);
    }
  };

  const handleSearch = async () => {
    if (searching) return;
    
    try {
      setSearching(true);
      const result: iHeartRadioSearchResult = await iHeartRadioService.searchStations(
        searchQuery,
        selectedMarket === 'all' ? undefined : selectedMarket
      );
      setSearchResults(result.stations);
      console.log(`🔍 Found ${result.totalResults} iHeartRadio stations for "${searchQuery}"`);
    } catch (error) {
      console.error('Search error:', error);
    } finally {
      setSearching(false);
    }
  };

  const handleStationPlay = (station: iHeartRadioStation) => {
    console.log('📻 Playing iHeartRadio station:', station.name);
    onStationSelect(station);
    
    Alert.alert(
      'Now Playing',
      `${station.name} ${station.frequency ? `(${station.frequency} ${station.band})` : ''}\n${station.description}\n\nCity: ${station.city}, ${station.state}\nGenre: ${station.genre}`,
      [{ text: 'OK' }]
    );
  };

  const toggleFavorite = async (station: iHeartRadioStation) => {
    const isFavorite = iHeartRadioService.isFavorite(station.id);
    
    if (isFavorite) {
      await iHeartRadioService.removeFromFavorites(station.id);
      Alert.alert('Removed', `${station.name} removed from favorites`);
    } else {
      await iHeartRadioService.addToFavorites(station.id);
      Alert.alert('Added', `${station.name} added to favorites`);
    }
    
    // Update favorites list
    const favorites = iHeartRadioService.getFavoriteStations();
    setFavoriteStations(favorites);
  };

  const getNearbyStations = (): iHeartRadioStation[] => {
    if (!userLocation) return [];
    return iHeartRadioService.getStationsByLocation(userLocation[0], userLocation[1], 150);
  };

  const getDisplayStations = (): iHeartRadioStation[] => {
    switch (activeTab) {
      case 'favorites':
        return favoriteStations;
      case 'search':
        return searchResults;
      case 'nearby':
        return getNearbyStations();
      case 'browse':
      default:
        if (selectedMarket === 'all') {
          return iHeartRadioService.getAllStations();
        }
        return iHeartRadioService.getStationsByMarket(selectedMarket);
    }
  };

  const renderStationCard = ({ item: station }: { item: iHeartRadioStation }) => {
    const isCurrentStation = currentStation?.id === station.id;
    const isFavorite = iHeartRadioService.isFavorite(station.id);
    
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
              {station.frequency && (
                <View style={[styles.frequencyTag, { backgroundColor: colors.primary + '20' }]}>
                  <Text style={[styles.frequencyText, { color: colors.primary }]}>
                    {station.frequency} {station.band}
                  </Text>
                </View>
              )}
            </View>
            
            <Text style={[styles.stationCallSign, { color: colors.textSecondary }]}>
              {station.callSign}
            </Text>
            
            <Text style={[styles.stationDescription, { color: colors.textSecondary }]}>
              {station.description}
            </Text>
            
            <View style={styles.stationMeta}>
              <View style={[styles.genreTag, { backgroundColor: colors.success + '20' }]}>
                <Text style={[styles.genreText, { color: colors.success }]}>{station.genre}</Text>
              </View>
              
              <Text style={[styles.locationText, { color: colors.textSecondary }]}>
                {station.city}, {station.state}
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
              {station.isLive && (
                <View style={[styles.liveTag, { backgroundColor: '#ff4757' }]}>
                  <Text style={[styles.liveText, { color: 'white' }]}>LIVE</Text>
                </View>
              )}
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

  const renderMarketTab = (market: iHeartRadioMarket) => (
    <TouchableOpacity
      key={market.id}
      style={[
        styles.marketTab,
        { backgroundColor: selectedMarket === market.id ? colors.primary : colors.surface },
        { borderColor: colors.border }
      ]}
      onPress={() => setSelectedMarket(market.id)}
    >
      <Text
        style={[
          styles.marketTabText,
          { color: selectedMarket === market.id ? colors.background : colors.text }
        ]}
      >
        {market.name}
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
    marketsContainer: {
      padding: 16,
      backgroundColor: colors.surface,
    },
    marketsRow: {
      flexDirection: 'row',
      flexWrap: 'wrap',
      gap: 8,
    },
    marketTab: {
      paddingHorizontal: 12,
      paddingVertical: 8,
      borderRadius: 8,
      borderWidth: 1,
    },
    marketTabText: {
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
    frequencyTag: {
      paddingHorizontal: 8,
      paddingVertical: 4,
      borderRadius: 6,
    },
    frequencyText: {
      fontSize: 10,
      fontWeight: '700',
    },
    stationCallSign: {
      fontSize: 12,
      fontWeight: '500',
      marginBottom: 4,
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
    },
    listenersText: {
      fontSize: 11,
      marginLeft: 4,
    },
    bitrateText: {
      fontSize: 11,
    },
    liveTag: {
      paddingHorizontal: 6,
      paddingVertical: 2,
      borderRadius: 4,
      marginLeft: 8,
    },
    liveText: {
      fontSize: 9,
      fontWeight: '700',
    },
    stationActions: {
      alignItems: 'center',
      gap: 8,
    },
    favoriteButton: {
      width: 36,
      height: 36,
      borderRadius: 18,
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
            <Text style={styles.headerTitle}>📻 iHeartRadio</Text>
            <TouchableOpacity style={styles.closeButton} onPress={onClose}>
              <Ionicons name="close" size={24} color={colors.text} />
            </TouchableOpacity>
          </View>
          <View style={styles.loadingContainer}>
            <ActivityIndicator size="large" color={colors.primary} />
            <Text style={styles.loadingText}>Loading iHeartRadio stations...</Text>
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
          <Text style={styles.headerTitle}>📻 iHeartRadio</Text>
          <TouchableOpacity style={styles.closeButton} onPress={onClose}>
            <Ionicons name="close" size={24} color={colors.text} />
          </TouchableOpacity>
        </View>

        {/* Tab Bar */}
        <View style={styles.tabBar}>
          {[
            { id: 'browse', label: 'Browse', icon: 'library' },
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

        {/* Search Input */}
        {activeTab === 'search' && (
          <View style={styles.searchContainer}>
            <TextInput
              style={styles.searchInput}
              placeholder="Search stations, genres, cities..."
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

        {/* Market Filter for Browse tab */}
        {activeTab === 'browse' && (
          <View style={styles.marketsContainer}>
            <ScrollView horizontal showsHorizontalScrollIndicator={false}>
              <View style={styles.marketsRow}>
                <TouchableOpacity
                  style={[
                    styles.marketTab,
                    { backgroundColor: selectedMarket === 'all' ? colors.primary : colors.surface },
                    { borderColor: colors.border }
                  ]}
                  onPress={() => setSelectedMarket('all')}
                >
                  <Text
                    style={[
                      styles.marketTabText,
                      { color: selectedMarket === 'all' ? colors.background : colors.text }
                    ]}
                  >
                    All Markets
                  </Text>
                </TouchableOpacity>
                {markets.map(renderMarketTab)}
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
                <Ionicons name="radio" size={64} color={colors.textSecondary} />
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