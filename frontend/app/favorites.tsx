import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  StyleSheet,
  TouchableOpacity,
  ActivityIndicator,
  FlatList,
  Image,
  Dimensions,
  Alert,
} from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { Stack, router } from 'expo-router';
import { Ionicons } from '@expo/vector-icons';
import AsyncStorage from '@react-native-async-storage/async-storage';

const { width, height } = Dimensions.get('window');
const API_BASE_URL = process.env.EXPO_PUBLIC_BACKEND_URL || 'https://dragon-radio.preview.emergentagent.com';

interface Station {
  id: string;
  name: string;
  call_sign?: string;
  standard_display_name?: string;
  stream_url: string;
  country: string;
  quality_score: number;
  division_level1?: string;
  division_level2?: string;
  added_at?: string;
  play_count?: number;
  last_played?: string;
}

export default function FavoritesScreen() {
  const [loading, setLoading] = useState(true);
  const [favorites, setFavorites] = useState<Station[]>([]);
  const [userId, setUserId] = useState<string>('');
  const [refreshing, setRefreshing] = useState(false);
  const [stats, setStats] = useState<any>(null);

  useEffect(() => {
    initializeUser();
  }, []);

  useEffect(() => {
    if (userId) {
      loadFavorites();
      loadStats();
    }
  }, [userId]);

  const initializeUser = async () => {
    try {
      let storedUserId = await AsyncStorage.getItem('user_id');
      if (!storedUserId) {
        // Generate a unique user ID
        storedUserId = `user_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
        await AsyncStorage.setItem('user_id', storedUserId);
      }
      setUserId(storedUserId);
    } catch (error) {
      console.error('Error initializing user:', error);
      setUserId(`temp_${Date.now()}`);
    }
  };

  const loadFavorites = async () => {
    try {
      setLoading(true);
      const response = await fetch(`${API_BASE_URL}/api/favorites/${userId}`);
      const data = await response.json();
      
      if (data.status === 'success' && data.data.success) {
        setFavorites(data.data.favorites || []);
      } else {
        setFavorites([]);
      }
    } catch (error) {
      console.error('Error loading favorites:', error);
      setFavorites([]);
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  };

  const loadStats = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/favorites/${userId}/stats`);
      const data = await response.json();
      
      if (data.status === 'success') {
        setStats(data.data);
      }
    } catch (error) {
      console.error('Error loading stats:', error);
    }
  };

  const removeFavorite = async (stationId: string) => {
    try {
      const response = await fetch(
        `${API_BASE_URL}/api/favorites/remove?user_id=${userId}&station_id=${stationId}`,
        { method: 'DELETE' }
      );
      const data = await response.json();
      
      if (data.status === 'success') {
        // Remove from local state
        setFavorites(prev => prev.filter(s => s.id !== stationId));
        loadStats(); // Refresh stats
      } else {
        Alert.alert('Error', 'Failed to remove favorite');
      }
    } catch (error) {
      console.error('Error removing favorite:', error);
      Alert.alert('Error', 'Failed to remove favorite');
    }
  };

  const confirmRemoveFavorite = (station: Station) => {
    Alert.alert(
      'Remove Favorite',
      `Remove ${station.standard_display_name || station.name} from favorites?`,
      [
        { text: 'Cancel', style: 'cancel' },
        {
          text: 'Remove',
          style: 'destructive',
          onPress: () => removeFavorite(station.id),
        },
      ]
    );
  };

  const playStation = (station: Station) => {
    // Update play stats
    fetch(
      `${API_BASE_URL}/api/favorites/play-stats?user_id=${userId}&station_id=${station.id}`,
      { method: 'POST' }
    ).catch(err => console.error('Play stats error:', err));

    // Navigate back and play
    console.log('Playing favorite:', station);
    Alert.alert('Playing', station.standard_display_name || station.name);
  };

  const onRefresh = () => {
    setRefreshing(true);
    loadFavorites();
    loadStats();
  };

  const renderStation = ({ item }: { item: Station }) => (
    <TouchableOpacity
      style={styles.stationCard}
      onPress={() => playStation(item)}
      activeOpacity={0.8}
    >
      {/* Batik Pattern Overlay */}
      <View style={styles.batikOverlay} />
      
      <View style={styles.cardContent}>
        <View style={styles.stationInfo}>
          <View style={styles.stationTextContainer}>
            <Text style={styles.stationName} numberOfLines={2}>
              {item.standard_display_name || item.name}
            </Text>
            
            {item.call_sign && (
              <Text style={styles.callSign}>{item.call_sign}</Text>
            )}
            
            <View style={styles.metaRow}>
              <Text style={styles.metaText}>
                {item.country}
                {item.division_level1 && ` • ${item.division_level1}`}
              </Text>
              {item.quality_score > 0 && (
                <View style={styles.qualityBadge}>
                  <Text style={styles.qualityText}>{item.quality_score}</Text>
                </View>
              )}
            </View>

            {item.play_count !== undefined && item.play_count > 0 && (
              <Text style={styles.playCount}>
                🎵 Played {item.play_count} {item.play_count === 1 ? 'time' : 'times'}
              </Text>
            )}
          </View>

          <View style={styles.actionsContainer}>
            <TouchableOpacity
              style={styles.playButton}
              onPress={() => playStation(item)}
            >
              <Ionicons name="play-circle" size={48} color="#FFFFFF" />
            </TouchableOpacity>

            <TouchableOpacity
              style={styles.removeButton}
              onPress={() => confirmRemoveFavorite(item)}
            >
              <Ionicons name="heart-dislike" size={24} color="#FFFFFF" />
            </TouchableOpacity>
          </View>
        </View>
      </View>
    </TouchableOpacity>
  );

  return (
    <SafeAreaView style={styles.container} edges={['top']}>
      <Stack.Screen 
        options={{
          title: 'My Favorites',
          headerShown: true,
          headerStyle: {
            backgroundColor: '#000000',
          },
          headerTintColor: '#FFFFFF',
        }}
      />

      {/* Batik Background Pattern */}
      <View style={styles.batikBackground} />

      <View style={styles.content}>
        {/* Stats Header */}
        {!loading && favorites.length > 0 && stats && (
          <View style={styles.statsCard}>
            <View style={styles.statsBatikOverlay} />
            <View style={styles.statsContent}>
              <View style={styles.statItem}>
                <Text style={styles.statNumber}>{stats.total_favorites || 0}</Text>
                <Text style={styles.statLabel}>Favorites</Text>
              </View>
              <View style={styles.statDivider} />
              <View style={styles.statItem}>
                <Text style={styles.statNumber}>{stats.countries_represented || 0}</Text>
                <Text style={styles.statLabel}>Countries</Text>
              </View>
            </View>
          </View>
        )}

        {/* Loading State */}
        {loading && (
          <View style={styles.loadingContainer}>
            <ActivityIndicator size="large" color="#FFFFFF" />
            <Text style={styles.loadingText}>Loading your favorites...</Text>
          </View>
        )}

        {/* Empty State */}
        {!loading && favorites.length === 0 && (
          <View style={styles.emptyContainer}>
            <Ionicons name="heart-outline" size={80} color="#4A4A4A" />
            <Text style={styles.emptyTitle}>No Favorites Yet</Text>
            <Text style={styles.emptyText}>
              Start adding stations to your favorites to see them here
            </Text>
            <TouchableOpacity
              style={styles.browseButton}
              onPress={() => router.push('/stations-browser')}
            >
              <Text style={styles.browseButtonText}>Browse Stations</Text>
            </TouchableOpacity>
          </View>
        )}

        {/* Favorites List */}
        {!loading && favorites.length > 0 && (
          <FlatList
            data={favorites}
            renderItem={renderStation}
            keyExtractor={(item) => item.id}
            refreshing={refreshing}
            onRefresh={onRefresh}
            contentContainerStyle={styles.listContainer}
            showsVerticalScrollIndicator={false}
          />
        )}
      </View>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#000000',
  },
  batikBackground: {
    position: 'absolute',
    width: width,
    height: height,
    backgroundColor: '#000000',
    opacity: 1,
  },
  content: {
    flex: 1,
    padding: 16,
  },
  statsCard: {
    backgroundColor: '#1A1A1A',
    borderRadius: 16,
    padding: 20,
    marginBottom: 20,
    borderWidth: 2,
    borderColor: '#FFFFFF',
    overflow: 'hidden',
  },
  statsBatikOverlay: {
    position: 'absolute',
    top: 0,
    left: 0,
    right: 0,
    bottom: 0,
    backgroundColor: '#FFFFFF',
    opacity: 0.05,
  },
  statsContent: {
    flexDirection: 'row',
    justifyContent: 'space-around',
    alignItems: 'center',
  },
  statItem: {
    alignItems: 'center',
  },
  statNumber: {
    fontSize: 32,
    fontWeight: '700',
    color: '#FFFFFF',
    marginBottom: 4,
  },
  statLabel: {
    fontSize: 14,
    color: '#888888',
    textTransform: 'uppercase',
    letterSpacing: 1,
  },
  statDivider: {
    width: 1,
    height: 40,
    backgroundColor: '#333333',
  },
  listContainer: {
    paddingBottom: 20,
  },
  stationCard: {
    backgroundColor: '#1A1A1A',
    borderRadius: 16,
    marginBottom: 16,
    borderWidth: 2,
    borderColor: '#FFFFFF',
    overflow: 'hidden',
  },
  batikOverlay: {
    position: 'absolute',
    top: 0,
    left: 0,
    right: 0,
    bottom: 0,
    backgroundColor: '#FFFFFF',
    opacity: 0.03,
  },
  cardContent: {
    padding: 16,
  },
  stationInfo: {
    flexDirection: 'row',
    justifyContent: 'space-between',
  },
  stationTextContainer: {
    flex: 1,
    marginRight: 16,
  },
  stationName: {
    fontSize: 18,
    fontWeight: '700',
    color: '#FFFFFF',
    marginBottom: 8,
  },
  callSign: {
    fontSize: 14,
    color: '#888888',
    fontWeight: '700',
    marginBottom: 8,
    letterSpacing: 1,
  },
  metaRow: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 4,
  },
  metaText: {
    fontSize: 12,
    color: '#666666',
    flex: 1,
  },
  qualityBadge: {
    backgroundColor: '#FFFFFF',
    paddingHorizontal: 8,
    paddingVertical: 4,
    borderRadius: 4,
    marginLeft: 8,
  },
  qualityText: {
    color: '#000000',
    fontSize: 12,
    fontWeight: '700',
  },
  playCount: {
    fontSize: 12,
    color: '#888888',
    marginTop: 4,
  },
  actionsContainer: {
    alignItems: 'center',
    justifyContent: 'space-between',
  },
  playButton: {
    marginBottom: 12,
  },
  removeButton: {
    width: 40,
    height: 40,
    borderRadius: 20,
    backgroundColor: '#333333',
    justifyContent: 'center',
    alignItems: 'center',
  },
  loadingContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
  },
  loadingText: {
    color: '#888888',
    fontSize: 16,
    marginTop: 16,
  },
  emptyContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    paddingHorizontal: 32,
  },
  emptyTitle: {
    fontSize: 24,
    fontWeight: '700',
    color: '#FFFFFF',
    marginTop: 24,
    marginBottom: 12,
  },
  emptyText: {
    fontSize: 16,
    color: '#888888',
    textAlign: 'center',
    lineHeight: 24,
    marginBottom: 32,
  },
  browseButton: {
    backgroundColor: '#FFFFFF',
    paddingVertical: 16,
    paddingHorizontal: 32,
    borderRadius: 12,
  },
  browseButtonText: {
    color: '#000000',
    fontSize: 16,
    fontWeight: '700',
  },
});
