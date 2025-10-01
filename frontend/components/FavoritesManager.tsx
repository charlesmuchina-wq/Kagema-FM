import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  StyleSheet,
  TouchableOpacity,
  FlatList,
  Alert,
  Modal,
  TextInput,
  Switch,
} from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { useTheme } from '../contexts/ThemeContext';
import AsyncStorage from '@react-native-async-storage/async-storage';
import * as Haptics from 'expo-haptics';

interface FavoriteItem {
  id: string;
  type: 'radio_station' | 'news_article' | 'music_track' | 'playlist';
  title: string;
  description?: string;
  url?: string;
  streamUrl?: string;
  metadata?: any;
  dateAdded: string;
  lastPlayed?: string;
  playCount: number;
  tags: string[];
  isPrivate: boolean;
}

interface FavoritesManagerProps {
  visible: boolean;
  onClose: () => void;
  onPlayItem?: (item: FavoriteItem) => void;
  currentlyPlaying?: string;
}

export const FavoritesManager: React.FC<FavoritesManagerProps> = ({
  visible,
  onClose,
  onPlayItem,
  currentlyPlaying,
}) => {
  const { colors } = useTheme();
  const [favorites, setFavorites] = useState<FavoriteItem[]>([]);
  const [filteredFavorites, setFilteredFavorites] = useState<FavoriteItem[]>([]);
  const [selectedType, setSelectedType] = useState<string>('all');
  const [searchQuery, setSearchQuery] = useState('');
  const [sortBy, setSortBy] = useState<'dateAdded' | 'playCount' | 'lastPlayed' | 'title'>('dateAdded');
  const [showAddModal, setShowAddModal] = useState(false);
  const [newFavorite, setNewFavorite] = useState<Partial<FavoriteItem>>({
    type: 'radio_station',
    title: '',
    description: '',
    streamUrl: '',
    tags: [],
    isPrivate: false,
  });

  useEffect(() => {
    loadFavorites();
  }, []);

  useEffect(() => {
    filterAndSortFavorites();
  }, [favorites, selectedType, searchQuery, sortBy]);

  const loadFavorites = async () => {
    try {
      const stored = await AsyncStorage.getItem('user_favorites');
      if (stored) {
        const parsed = JSON.parse(stored);
        setFavorites(parsed);
      }
    } catch (error) {
      console.log('Error loading favorites:', error);
    }
  };

  const saveFavorites = async (newFavorites: FavoriteItem[]) => {
    try {
      await AsyncStorage.setItem('user_favorites', JSON.stringify(newFavorites));
      setFavorites(newFavorites);
    } catch (error) {
      console.log('Error saving favorites:', error);
    }
  };

  const filterAndSortFavorites = () => {
    let filtered = favorites;

    // Filter by type
    if (selectedType !== 'all') {
      filtered = filtered.filter(item => item.type === selectedType);
    }

    // Filter by search query
    if (searchQuery) {
      filtered = filtered.filter(item =>
        item.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
        item.description?.toLowerCase().includes(searchQuery.toLowerCase()) ||
        item.tags.some(tag => tag.toLowerCase().includes(searchQuery.toLowerCase()))
      );
    }

    // Sort
    filtered.sort((a, b) => {
      switch (sortBy) {
        case 'title':
          return a.title.localeCompare(b.title);
        case 'playCount':
          return b.playCount - a.playCount;
        case 'lastPlayed':
          return new Date(b.lastPlayed || 0).getTime() - new Date(a.lastPlayed || 0).getTime();
        case 'dateAdded':
        default:
          return new Date(b.dateAdded).getTime() - new Date(a.dateAdded).getTime();
      }
    });

    setFilteredFavorites(filtered);
  };

  const addToFavorites = async (item: Partial<FavoriteItem>) => {
    const favorite: FavoriteItem = {
      id: Date.now().toString(),
      type: item.type || 'radio_station',
      title: item.title || '',
      description: item.description,
      url: item.url,
      streamUrl: item.streamUrl,
      metadata: item.metadata,
      dateAdded: new Date().toISOString(),
      playCount: 0,
      tags: item.tags || [],
      isPrivate: item.isPrivate || false,
    };

    const newFavorites = [favorite, ...favorites];
    await saveFavorites(newFavorites);
    await Haptics.notificationAsync(Haptics.NotificationFeedbackType.Success);
  };

  const removeFromFavorites = async (id: string) => {
    Alert.alert(
      'Remove Favorite',
      'Are you sure you want to remove this item from your favorites?',
      [
        { text: 'Cancel', style: 'cancel' },
        {
          text: 'Remove',
          style: 'destructive',
          onPress: async () => {
            const newFavorites = favorites.filter(item => item.id !== id);
            await saveFavorites(newFavorites);
            await Haptics.notificationAsync(Haptics.NotificationFeedbackType.Warning);
          },
        },
      ]
    );
  };

  const playFavorite = async (item: FavoriteItem) => {
    // Update play count and last played
    const updatedFavorites = favorites.map(fav =>
      fav.id === item.id
        ? {
            ...fav,
            playCount: fav.playCount + 1,
            lastPlayed: new Date().toISOString(),
          }
        : fav
    );
    
    await saveFavorites(updatedFavorites);
    onPlayItem?.(item);
    await Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Medium);
  };

  const exportFavorites = async () => {
    try {
      const exportData = {
        favorites: favorites.filter(item => !item.isPrivate),
        exportDate: new Date().toISOString(),
        version: '1.0',
      };
      
      const jsonString = JSON.stringify(exportData, null, 2);
      
      Alert.alert(
        'Export Favorites',
        'Your favorites have been prepared for export. In a full app, this would be saved to a file or shared.',
        [
          { text: 'OK' },
          {
            text: 'Copy to Clipboard',
            onPress: () => {
              // In a real app, copy to clipboard
              console.log('Export data:', jsonString);
            },
          },
        ]
      );
    } catch (error) {
      Alert.alert('Error', 'Failed to export favorites');
    }
  };

  const addNewFavorite = async () => {
    if (!newFavorite.title?.trim()) {
      Alert.alert('Error', 'Please enter a title for your favorite');
      return;
    }

    await addToFavorites(newFavorite);
    setShowAddModal(false);
    setNewFavorite({
      type: 'radio_station',
      title: '',
      description: '',
      streamUrl: '',
      tags: [],
      isPrivate: false,
    });
  };

  const getTypeIcon = (type: string) => {
    switch (type) {
      case 'radio_station':
        return 'radio';
      case 'news_article':
        return 'newspaper';
      case 'music_track':
        return 'musical-notes';
      case 'playlist':
        return 'list';
      default:
        return 'heart';
    }
  };

  const renderFavoriteItem = ({ item }: { item: FavoriteItem }) => {
    const isCurrentlyPlaying = currentlyPlaying === item.id;
    
    return (
      <View style={[styles.favoriteItem, { borderColor: colors.border }]}>
        <TouchableOpacity
          style={styles.favoriteContent}
          onPress={() => playFavorite(item)}
        >
          <View style={styles.favoriteHeader}>
            <View style={styles.favoriteIconContainer}>
              <Ionicons
                name={getTypeIcon(item.type)}
                size={24}
                color={isCurrentlyPlaying ? colors.primary : colors.text}
              />
              {isCurrentlyPlaying && (
                <View style={[styles.playingIndicator, { backgroundColor: colors.primary }]} />
              )}
            </View>
            
            <View style={styles.favoriteInfo}>
              <Text style={[styles.favoriteTitle, { color: colors.text }]} numberOfLines={1}>
                {item.title}
              </Text>
              {item.description && (
                <Text style={[styles.favoriteDescription, { color: colors.textSecondary }]} numberOfLines={2}>
                  {item.description}
                </Text>
              )}
              
              <View style={styles.favoriteStats}>
                <Text style={[styles.statText, { color: colors.textSecondary }]}>
                  Played {item.playCount} times
                </Text>
                {item.lastPlayed && (
                  <Text style={[styles.statText, { color: colors.textSecondary }]}>
                    Last: {new Date(item.lastPlayed).toLocaleDateString()}
                  </Text>
                )}
              </View>
              
              {item.tags.length > 0 && (
                <View style={styles.tagsContainer}>
                  {item.tags.slice(0, 3).map((tag, index) => (
                    <View key={index} style={[styles.tag, { backgroundColor: colors.surface }]}>
                      <Text style={[styles.tagText, { color: colors.textSecondary }]}>{tag}</Text>
                    </View>
                  ))}
                </View>
              )}
            </View>
          </View>
        </TouchableOpacity>
        
        <TouchableOpacity
          style={styles.removeButton}
          onPress={() => removeFromFavorites(item.id)}
        >
          <Ionicons name="trash-outline" size={20} color={colors.error} />
        </TouchableOpacity>
      </View>
    );
  };

  const styles = StyleSheet.create({
    container: {
      flex: 1,
      backgroundColor: colors.background,
    },
    header: {
      padding: 20,
      paddingTop: 60,
      borderBottomWidth: 1,
      borderBottomColor: colors.border,
    },
    headerTitle: {
      fontSize: 24,
      fontWeight: '600',
      color: colors.text,
      textAlign: 'center',
    },
    headerSubtitle: {
      fontSize: 14,
      color: colors.textSecondary,
      textAlign: 'center',
      marginTop: 4,
    },
    closeButton: {
      position: 'absolute',
      top: 60,
      right: 20,
      padding: 8,
    },
    controls: {
      padding: 16,
      backgroundColor: colors.surface,
    },
    searchContainer: {
      flexDirection: 'row',
      alignItems: 'center',
      backgroundColor: colors.background,
      borderRadius: 8,
      paddingHorizontal: 12,
      marginBottom: 12,
    },
    searchInput: {
      flex: 1,
      height: 40,
      color: colors.text,
      marginLeft: 8,
    },
    filterContainer: {
      flexDirection: 'row',
      justifyContent: 'space-between',
      marginBottom: 12,
    },
    filterButton: {
      paddingHorizontal: 12,
      paddingVertical: 6,
      borderRadius: 16,
      backgroundColor: colors.background,
      borderWidth: 1,
      borderColor: colors.border,
    },
    filterButtonActive: {
      backgroundColor: colors.primary,
      borderColor: colors.primary,
    },
    filterText: {
      fontSize: 12,
      color: colors.text,
    },
    filterTextActive: {
      color: colors.background,
    },
    sortContainer: {
      flexDirection: 'row',
      alignItems: 'center',
    },
    sortLabel: {
      fontSize: 14,
      color: colors.textSecondary,
      marginRight: 8,
    },
    actionButtons: {
      flexDirection: 'row',
      justifyContent: 'space-between',
      paddingHorizontal: 16,
      paddingVertical: 8,
      backgroundColor: colors.surface,
    },
    actionButton: {
      flexDirection: 'row',
      alignItems: 'center',
      paddingHorizontal: 16,
      paddingVertical: 8,
      borderRadius: 8,
      backgroundColor: colors.background,
    },
    actionButtonText: {
      fontSize: 14,
      color: colors.text,
      marginLeft: 8,
    },
    favoritesList: {
      flex: 1,
    },
    favoriteItem: {
      backgroundColor: colors.card,
      marginHorizontal: 16,
      marginVertical: 6,
      borderRadius: 12,
      borderWidth: 1,
      overflow: 'hidden',
    },
    favoriteContent: {
      flex: 1,
    },
    favoriteHeader: {
      flexDirection: 'row',
      padding: 16,
    },
    favoriteIconContainer: {
      position: 'relative',
      marginRight: 12,
      alignItems: 'center',
      justifyContent: 'center',
    },
    playingIndicator: {
      position: 'absolute',
      bottom: -2,
      right: -2,
      width: 8,
      height: 8,
      borderRadius: 4,
    },
    favoriteInfo: {
      flex: 1,
    },
    favoriteTitle: {
      fontSize: 16,
      fontWeight: '600',
      marginBottom: 4,
    },
    favoriteDescription: {
      fontSize: 14,
      marginBottom: 8,
    },
    favoriteStats: {
      flexDirection: 'row',
      justifyContent: 'space-between',
      marginBottom: 8,
    },
    statText: {
      fontSize: 12,
    },
    tagsContainer: {
      flexDirection: 'row',
      flexWrap: 'wrap',
    },
    tag: {
      paddingHorizontal: 8,
      paddingVertical: 2,
      borderRadius: 10,
      marginRight: 4,
      marginBottom: 4,
    },
    tagText: {
      fontSize: 10,
    },
    removeButton: {
      position: 'absolute',
      top: 8,
      right: 8,
      padding: 8,
    },
    emptyState: {
      flex: 1,
      alignItems: 'center',
      justifyContent: 'center',
      padding: 40,
    },
    emptyStateText: {
      fontSize: 16,
      color: colors.textSecondary,
      textAlign: 'center',
      marginTop: 16,
    },
    modalOverlay: {
      flex: 1,
      backgroundColor: 'rgba(0,0,0,0.5)',
      justifyContent: 'center',
      padding: 20,
    },
    modalContainer: {
      backgroundColor: colors.card,
      borderRadius: 16,
      padding: 24,
    },
    modalTitle: {
      fontSize: 18,
      fontWeight: '600',
      color: colors.text,
      textAlign: 'center',
      marginBottom: 20,
    },
    input: {
      borderWidth: 1,
      borderColor: colors.border,
      borderRadius: 8,
      padding: 12,
      marginBottom: 16,
      color: colors.text,
      backgroundColor: colors.background,
    },
    switchContainer: {
      flexDirection: 'row',
      justifyContent: 'space-between',
      alignItems: 'center',
      marginBottom: 20,
    },
    switchLabel: {
      fontSize: 16,
      color: colors.text,
    },
    modalButtons: {
      flexDirection: 'row',
      justifyContent: 'space-between',
    },
    modalButton: {
      flex: 1,
      paddingVertical: 12,
      borderRadius: 8,
      alignItems: 'center',
      marginHorizontal: 6,
    },
    cancelButton: {
      backgroundColor: colors.surface,
    },
    saveButton: {
      backgroundColor: colors.primary,
    },
    modalButtonText: {
      fontSize: 16,
      fontWeight: '600',
    },
    cancelButtonText: {
      color: colors.text,
    },
    saveButtonText: {
      color: colors.background,
    },
  });

  const typeFilters = [
    { key: 'all', label: 'All' },
    { key: 'radio_station', label: 'Radio' },
    { key: 'news_article', label: 'News' },
    { key: 'music_track', label: 'Music' },
    { key: 'playlist', label: 'Playlists' },
  ];

  const sortOptions = [
    { key: 'dateAdded', label: 'Recent' },
    { key: 'playCount', label: 'Most Played' },
    { key: 'title', label: 'A-Z' },
  ];

  return (
    <Modal visible={visible} animationType="slide" presentationStyle="formSheet">
      <View style={styles.container}>
        <View style={styles.header}>
          <TouchableOpacity style={styles.closeButton} onPress={onClose}>
            <Ionicons name="close" size={24} color={colors.text} />
          </TouchableOpacity>
          <Text style={styles.headerTitle}>My Favorites</Text>
          <Text style={styles.headerSubtitle}>{favorites.length} saved items</Text>
        </View>

        <View style={styles.controls}>
          <View style={styles.searchContainer}>
            <Ionicons name="search" size={20} color={colors.textSecondary} />
            <TextInput
              style={styles.searchInput}
              placeholder="Search favorites..."
              placeholderTextColor={colors.textSecondary}
              value={searchQuery}
              onChangeText={setSearchQuery}
            />
          </View>

          <View style={styles.filterContainer}>
            {typeFilters.map((filter) => (
              <TouchableOpacity
                key={filter.key}
                style={[
                  styles.filterButton,
                  selectedType === filter.key && styles.filterButtonActive,
                ]}
                onPress={() => setSelectedType(filter.key)}
              >
                <Text
                  style={[
                    styles.filterText,
                    selectedType === filter.key && styles.filterTextActive,
                  ]}
                >
                  {filter.label}
                </Text>
              </TouchableOpacity>
            ))}
          </View>

          <View style={styles.sortContainer}>
            <Text style={styles.sortLabel}>Sort:</Text>
            {sortOptions.map((option) => (
              <TouchableOpacity
                key={option.key}
                style={[
                  styles.filterButton,
                  sortBy === option.key && styles.filterButtonActive,
                ]}
                onPress={() => setSortBy(option.key as any)}
              >
                <Text
                  style={[
                    styles.filterText,
                    sortBy === option.key && styles.filterTextActive,
                  ]}
                >
                  {option.label}
                </Text>
              </TouchableOpacity>
            ))}
          </View>
        </View>

        <View style={styles.actionButtons}>
          <TouchableOpacity
            style={styles.actionButton}
            onPress={() => setShowAddModal(true)}
          >
            <Ionicons name="add" size={20} color={colors.text} />
            <Text style={styles.actionButtonText}>Add</Text>
          </TouchableOpacity>
          
          <TouchableOpacity style={styles.actionButton} onPress={exportFavorites}>
            <Ionicons name="share-outline" size={20} color={colors.text} />
            <Text style={styles.actionButtonText}>Export</Text>
          </TouchableOpacity>
        </View>

        {filteredFavorites.length === 0 ? (
          <View style={styles.emptyState}>
            <Ionicons name="heart-outline" size={64} color={colors.textSecondary} />
            <Text style={styles.emptyStateText}>
              {searchQuery || selectedType !== 'all'
                ? 'No favorites match your search'
                : 'No favorites yet.\nStart adding your favorite radio stations, news, and music!'}
            </Text>
          </View>
        ) : (
          <FlatList
            style={styles.favoritesList}
            data={filteredFavorites}
            renderItem={renderFavoriteItem}
            keyExtractor={(item) => item.id}
            showsVerticalScrollIndicator={false}
          />
        )}
      </View>

      <Modal
        visible={showAddModal}
        transparent
        animationType="fade"
        onRequestClose={() => setShowAddModal(false)}
      >
        <View style={styles.modalOverlay}>
          <View style={styles.modalContainer}>
            <Text style={styles.modalTitle}>Add New Favorite</Text>
            
            <TextInput
              style={styles.input}
              placeholder="Title"
              placeholderTextColor={colors.textSecondary}
              value={newFavorite.title}
              onChangeText={(text) => setNewFavorite({ ...newFavorite, title: text })}
            />
            
            <TextInput
              style={styles.input}
              placeholder="Description (optional)"
              placeholderTextColor={colors.textSecondary}
              value={newFavorite.description}
              onChangeText={(text) => setNewFavorite({ ...newFavorite, description: text })}
              multiline
            />
            
            <TextInput
              style={styles.input}
              placeholder="Stream URL (optional)"
              placeholderTextColor={colors.textSecondary}
              value={newFavorite.streamUrl}
              onChangeText={(text) => setNewFavorite({ ...newFavorite, streamUrl: text })}
            />

            <View style={styles.switchContainer}>
              <Text style={styles.switchLabel}>Private favorite</Text>
              <Switch
                value={newFavorite.isPrivate}
                onValueChange={(value) => setNewFavorite({ ...newFavorite, isPrivate: value })}
                trackColor={{ false: colors.border, true: colors.primary }}
                thumbColor={colors.background}
              />
            </View>

            <View style={styles.modalButtons}>
              <TouchableOpacity
                style={[styles.modalButton, styles.cancelButton]}
                onPress={() => setShowAddModal(false)}
              >
                <Text style={[styles.modalButtonText, styles.cancelButtonText]}>
                  Cancel
                </Text>
              </TouchableOpacity>
              
              <TouchableOpacity
                style={[styles.modalButton, styles.saveButton]}
                onPress={addNewFavorite}
              >
                <Text style={[styles.modalButtonText, styles.saveButtonText]}>
                  Save
                </Text>
              </TouchableOpacity>
            </View>
          </View>
        </View>
      </Modal>
    </Modal>
  );
};

// Export function to add favorites from other components
export const addItemToFavorites = async (item: {
  type: 'radio_station' | 'news_article' | 'music_track' | 'playlist';
  title: string;
  description?: string;
  url?: string;
  streamUrl?: string;
  metadata?: any;
  tags?: string[];
}) => {
  try {
    const stored = await AsyncStorage.getItem('user_favorites');
    const existing = stored ? JSON.parse(stored) : [];
    
    // Check if already exists
    const exists = existing.find((fav: FavoriteItem) => 
      fav.title === item.title && fav.type === item.type
    );
    
    if (exists) {
      return { success: false, message: 'Item already in favorites' };
    }
    
    const favorite: FavoriteItem = {
      id: Date.now().toString(),
      type: item.type,
      title: item.title,
      description: item.description,
      url: item.url,
      streamUrl: item.streamUrl,
      metadata: item.metadata,
      dateAdded: new Date().toISOString(),
      playCount: 0,
      tags: item.tags || [],
      isPrivate: false,
    };
    
    const newFavorites = [favorite, ...existing];
    await AsyncStorage.setItem('user_favorites', JSON.stringify(newFavorites));
    
    await Haptics.notificationAsync(Haptics.NotificationFeedbackType.Success);
    return { success: true, message: 'Added to favorites!' };
    
  } catch (error) {
    console.log('Error adding to favorites:', error);
    return { success: false, message: 'Failed to add to favorites' };
  }
};