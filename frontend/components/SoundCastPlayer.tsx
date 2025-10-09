import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  StyleSheet,
  TouchableOpacity,
  ScrollView,
  FlatList,
  Alert,
  Modal,
  TextInput,
  ActivityIndicator,
  Dimensions,
} from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { useTheme } from '../contexts/ThemeContext';
import { soundCastService, SoundCastStation, SoundCastCategory } from '../services/SoundCastService';
import { shadowStyles } from '../utils/shadowStyles';
import hybridLocationService, { LocationInfo } from '../services/HybridLocationService';

const { width } = Dimensions.get('window');

interface SoundCastPlayerProps {
  visible: boolean;
  onClose: () => void;
  onStationSelect: (station: SoundCastStation) => void;
  currentStation?: SoundCastStation | null;
}

export const SoundCastPlayer: React.FC<SoundCastPlayerProps> = ({
  visible,
  onClose,
  onStationSelect,
  currentStation
}) => {
  const { colors } = useTheme();
  const [categories, setCategories] = useState<SoundCastCategory[]>([]);
  const [selectedCategory, setSelectedCategory] = useState<string>('all');
  const [searchQuery, setSearchQuery] = useState('');
  const [searchResults, setSearchResults] = useState<SoundCastStation[]>([]);
  const [favoriteStations, setFavoriteStations] = useState<SoundCastStation[]>([]);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState<'browse' | 'favorites' | 'search' | 'popular'>('browse');

  useEffect(() => {
    if (visible) {
      initializeSoundCast();
    }
  }, [visible]);

  useEffect(() => {
    if (searchQuery.length > 2) {
      const results = soundCastService.searchStations(searchQuery);
      setSearchResults(results);
    } else {
      setSearchResults([]);
    }
  }, [searchQuery]);

  const initializeSoundCast = async () => {
    try {
      setLoading(true);
      await soundCastService.initialize();
      
      const cats = soundCastService.getCategories();
      setCategories(cats);
      
      const favorites = soundCastService.getFavoriteStations();
      setFavoriteStations(favorites);
      
      console.log('🎵 SoundCast initialized with', soundCastService.getTotalStationsCount(), 'stations');
    } catch (error) {
      console.error('Error initializing SoundCast:', error);
      Alert.alert('Error', 'Failed to load SoundCast stations');
    } finally {
      setLoading(false);
    }
  };

  const handleStationPlay = (station: SoundCastStation) => {
    console.log('🎵 Playing SoundCast station:', station.name);
    onStationSelect(station);
    Alert.alert(
      'Now Playing',
      `${station.name}\n${station.description}`,
      [{ text: 'OK' }]
    );
  };

  const toggleFavorite = async (station: SoundCastStation) => {
    const isFavorite = soundCastService.isFavorite(station.id);
    
    if (isFavorite) {
      await soundCastService.removeFromFavorites(station.id);
      Alert.alert('Removed', `${station.name} removed from favorites`);
    } else {
      await soundCastService.addToFavorites(station.id);
      Alert.alert('Added', `${station.name} added to favorites`);
    }
    
    // Update favorites list
    const favorites = soundCastService.getFavoriteStations();
    setFavoriteStations(favorites);
  };

  const renderStationCard = ({ item: station }: { item: SoundCastStation }) => {
    const isCurrentStation = currentStation?.id === station.id;
    const isFavorite = soundCastService.isFavorite(station.id);
    
    return (
      <View style={[
        styles.stationCard,
        { backgroundColor: colors.card, borderColor: colors.border },
        isCurrentStation && { borderColor: colors.primary, borderWidth: 2 }
      ]}>
        <View style={styles.stationHeader}>
          <View style={styles.stationInfo}>
            <Text style={[styles.stationName, { color: colors.text }]}>{station.name}</Text>
            <Text style={[styles.stationDescription, { color: colors.textSecondary }]}>
              {station.description}
            </Text>
            <View style={styles.stationMeta}>
              <View style={[styles.genreTag, { backgroundColor: colors.primary + '20' }]}>
                <Text style={[styles.genreText, { color: colors.primary }]}>{station.genre}</Text>
              </View>
              <Text style={[styles.countryText, { color: colors.textSecondary }]}>
                {station.country}
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

  const renderCategoryTab = (category: SoundCastCategory) => (
    <TouchableOpacity
      key={category.id}
      style={[
        styles.categoryTab,
        { backgroundColor: selectedCategory === category.id ? colors.primary : colors.surface },
        { borderColor: colors.border }
      ]}
      onPress={() => setSelectedCategory(category.id)}
    >
      <Ionicons
        name={category.icon as any}
        size={16}
        color={selectedCategory === category.id ? colors.background : colors.text}
      />
      <Text
        style={[
          styles.categoryTabText,
          { color: selectedCategory === category.id ? colors.background : colors.text }
        ]}
      >
        {category.name}
      </Text>
    </TouchableOpacity>
  );

  const getDisplayStations = (): SoundCastStation[] => {
    switch (activeTab) {
      case 'favorites':
        return favoriteStations;
      case 'search':
        return searchResults;
      case 'popular':
        return soundCastService.getPopularStations(20);
      case 'browse':
      default:
        if (selectedCategory === 'all') {
          return soundCastService.getAllStations();
        }
        const category = soundCastService.getCategoryById(selectedCategory);
        return category ? category.stations : [];
    }
  };

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
    categoriesContainer: {
      padding: 16,
      backgroundColor: colors.surface,
    },
    categoriesRow: {
      flexDirection: 'row',
      flexWrap: 'wrap',
      gap: 8,
    },
    categoryTab: {
      flexDirection: 'row',
      alignItems: 'center',
      paddingHorizontal: 12,
      paddingVertical: 8,
      borderRadius: 8,
      borderWidth: 1,
      gap: 6,
    },
    categoryTabText: {
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
    stationName: {
      fontSize: 16,
      fontWeight: '600',
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
    countryText: {
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
            <Text style={styles.headerTitle}>SoundCast</Text>
            <TouchableOpacity style={styles.closeButton} onPress={onClose}>
              <Ionicons name="close" size={24} color={colors.text} />
            </TouchableOpacity>
          </View>
          <View style={styles.loadingContainer}>
            <ActivityIndicator size="large" color={colors.primary} />
            <Text style={styles.loadingText}>Loading radio stations...</Text>
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
          <Text style={styles.headerTitle}>🎵 SoundCast</Text>
          <TouchableOpacity style={styles.closeButton} onPress={onClose}>
            <Ionicons name="close" size={24} color={colors.text} />
          </TouchableOpacity>
        </View>

        {/* Tab Bar */}
        <View style={styles.tabBar}>
          {[
            { id: 'browse', label: 'Browse', icon: 'library' },
            { id: 'popular', label: 'Popular', icon: 'trending-up' },
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
              placeholder="Search stations, genres, countries..."
              placeholderTextColor={colors.textSecondary}
              value={searchQuery}
              onChangeText={setSearchQuery}
            />
          </View>
        )}

        {/* Category Filter for Browse tab */}
        {activeTab === 'browse' && (
          <View style={styles.categoriesContainer}>
            <ScrollView horizontal showsHorizontalScrollIndicator={false}>
              <View style={styles.categoriesRow}>
                <TouchableOpacity
                  style={[
                    styles.categoryTab,
                    { backgroundColor: selectedCategory === 'all' ? colors.primary : colors.surface },
                    { borderColor: colors.border }
                  ]}
                  onPress={() => setSelectedCategory('all')}
                >
                  <Ionicons
                    name="globe"
                    size={16}
                    color={selectedCategory === 'all' ? colors.background : colors.text}
                  />
                  <Text
                    style={[
                      styles.categoryTabText,
                      { color: selectedCategory === 'all' ? colors.background : colors.text }
                    ]}
                  >
                    All Stations
                  </Text>
                </TouchableOpacity>
                {categories.map(renderCategoryTab)}
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