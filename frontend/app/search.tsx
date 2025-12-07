import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  StyleSheet,
  TouchableOpacity,
  TextInput,
  FlatList,
  ActivityIndicator,
  ScrollView,
  Dimensions,
} from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { Stack, router } from 'expo-router';
import { Ionicons } from '@expo/vector-icons';

const { width } = Dimensions.get('window');
const API_BASE_URL = process.env.EXPO_PUBLIC_BACKEND_URL || 'https://karau-grid-update.preview.emergentagent.com';

interface Station {
  id: string;
  name: string;
  call_sign?: string;
  standard_display_name?: string;
  stream_url: string;
  country: string;
  language?: string;
  genre?: string;
  quality_score: number;
}

interface ParsedIntent {
  detected_language?: string;
  detected_genre?: string;
  detected_country?: string;
}

export default function IntelligentSearchScreen() {
  const [searchQuery, setSearchQuery] = useState('');
  const [results, setResults] = useState<Station[]>([]);
  const [loading, setLoading] = useState(false);
  const [parsedIntent, setParsedIntent] = useState<ParsedIntent | null>(null);
  const [activeFilter, setActiveFilter] = useState<'all' | 'language' | 'genre' | 'country'>('all');
  const [trending, setTrending] = useState<Station[]>([]);
  const [showFilters, setShowFilters] = useState(false);

  useEffect(() => {
    loadTrending();
  }, []);

  const loadTrending = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/search/trending?limit=10`);
      const data = await response.json();
      
      if (data.status === 'success') {
        setTrending(data.data.trending || []);
      }
    } catch (error) {
      console.error('Error loading trending:', error);
    }
  };

  const handleSearch = async () => {
    if (!searchQuery.trim()) {
      setResults([]);
      return;
    }

    try {
      setLoading(true);
      
      console.log(`[SEARCH] Searching for: "${searchQuery}"`);
      
      const response = await fetch(
        `${API_BASE_URL}/api/search/intelligent?q=${encodeURIComponent(searchQuery)}&limit=50`
      );
      const data = await response.json();
      
      console.log(`[SEARCH] Query: "${searchQuery}" returned ${data.data?.results?.length || 0} results`);
      console.log(`[SEARCH] First 3 results:`, data.data?.results?.slice(0, 3).map((s: Station) => s.name));
      
      if (data.status === 'success') {
        const newResults = data.data.results || [];
        setResults(newResults);
        setParsedIntent(data.data.parsed_intent || null);
        
        console.log(`[SEARCH] Set ${newResults.length} results in state`);
      } else {
        console.error(`[SEARCH] Search failed:`, data);
        setResults([]);
      }
    } catch (error) {
      console.error('[SEARCH] Search error:', error);
      setResults([]);
    } finally {
      setLoading(false);
    }
  };

  const handleQuickSearch = async (query: string) => {
    setSearchQuery(query);
    // Clear previous results immediately
    setResults([]);
    setParsedIntent(null);
    
    // Small delay to allow state update
    setTimeout(async () => {
      if (!query.trim()) return;
      
      try {
        setLoading(true);
        const response = await fetch(
          `${API_BASE_URL}/api/search/intelligent?q=${encodeURIComponent(query)}&limit=50`
        );
        const data = await response.json();
        
        console.log(`[SEARCH] Query: "${query}" returned ${data.data?.results?.length || 0} results`);
        
        if (data.status === 'success') {
          setResults(data.data.results || []);
          setParsedIntent(data.data.parsed_intent || null);
        } else {
          setResults([]);
        }
      } catch (error) {
        console.error('Quick search error:', error);
        setResults([]);
      } finally {
        setLoading(false);
      }
    }, 100);
  };

  const playStation = (station: Station) => {
    console.log('Playing station:', station);
    // Navigate back with station info or handle play
  };

  const renderStation = ({ item }: { item: Station }) => (
    <TouchableOpacity
      style={styles.stationCard}
      onPress={() => playStation(item)}
      activeOpacity={0.8}
    >
      <View style={styles.batikOverlay} />
      
      <View style={styles.cardContent}>
        <View style={styles.stationHeader}>
          <View style={styles.stationInfo}>
            <Text style={styles.stationName} numberOfLines={2}>
              {item.standard_display_name || item.name}
            </Text>
            
            {item.call_sign && (
              <Text style={styles.callSign}>{item.call_sign}</Text>
            )}
            
            <View style={styles.metaRow}>
              <Text style={styles.metaText}>
                {item.country}
                {item.language && ` • ${item.language}`}
                {item.genre && ` • ${item.genre}`}
              </Text>
              {item.quality_score > 0 && (
                <View style={styles.qualityBadge}>
                  <Text style={styles.qualityText}>{item.quality_score}</Text>
                </View>
              )}
            </View>
          </View>

          <TouchableOpacity
            style={styles.playButton}
            onPress={() => playStation(item)}
          >
            <Ionicons name="play-circle" size={48} color="#FFFFFF" />
          </TouchableOpacity>
        </View>
      </View>
    </TouchableOpacity>
  );

  return (
    <SafeAreaView style={styles.container} edges={['top']}>
      <Stack.Screen 
        options={{
          title: 'AI Search',
          headerShown: true,
          headerStyle: {
            backgroundColor: '#000000',
          },
          headerTintColor: '#FFFFFF',
        }}
      />

      <View style={styles.batikBackground} />

      <View style={styles.content}>
        {/* Search Bar */}
        <View style={styles.searchSection}>
          <View style={styles.searchContainer}>
            <Ionicons name="search" size={20} color="#FFFFFF" style={styles.searchIcon} />
            <TextInput
              style={styles.searchInput}
              placeholder="Search stations, countries, languages, genres..."
              placeholderTextColor="#666666"
              value={searchQuery}
              onChangeText={setSearchQuery}
              onSubmitEditing={handleSearch}
              returnKeyType="search"
            />
            {searchQuery ? (
              <TouchableOpacity onPress={() => { setSearchQuery(''); setResults([]); }}>
                <Ionicons name="close-circle" size={20} color="#666666" />
              </TouchableOpacity>
            ) : null}
          </View>

          <TouchableOpacity
            style={styles.searchButton}
            onPress={handleSearch}
            disabled={loading}
          >
            {loading ? (
              <ActivityIndicator color="#000000" />
            ) : (
              <Text style={styles.searchButtonText}>Search</Text>
            )}
          </TouchableOpacity>
        </View>

        {/* Parsed Intent Display */}
        {parsedIntent && (results.length > 0) && (
          <View style={styles.intentCard}>
            <Ionicons name="bulb" size={16} color="#FFFFFF" />
            <Text style={styles.intentText}>
              AI detected: 
              {parsedIntent.detected_country && ` ${parsedIntent.detected_country}`}
              {parsedIntent.detected_language && ` ${parsedIntent.detected_language}`}
              {parsedIntent.detected_genre && ` ${parsedIntent.detected_genre}`}
            </Text>
          </View>
        )}

        {/* Quick Filters */}
        <ScrollView 
          horizontal 
          showsHorizontalScrollIndicator={false}
          style={styles.quickFilters}
          contentContainerStyle={styles.quickFiltersContent}
        >
          <TouchableOpacity
            style={styles.quickFilterChip}
            onPress={() => handleQuickSearch('rock music')}
          >
            <Text style={styles.quickFilterText}>🎸 Rock</Text>
          </TouchableOpacity>
          
          <TouchableOpacity
            style={styles.quickFilterChip}
            onPress={() => handleQuickSearch('news stations')}
          >
            <Text style={styles.quickFilterText}>📰 News</Text>
          </TouchableOpacity>
          
          <TouchableOpacity
            style={styles.quickFilterChip}
            onPress={() => handleQuickSearch('classical music')}
          >
            <Text style={styles.quickFilterText}>🎼 Classical</Text>
          </TouchableOpacity>
          
          <TouchableOpacity
            style={styles.quickFilterChip}
            onPress={() => handleQuickSearch('jazz')}
          >
            <Text style={styles.quickFilterText}>🎷 Jazz</Text>
          </TouchableOpacity>
          
          <TouchableOpacity
            style={styles.quickFilterChip}
            onPress={() => handleQuickSearch('sports')}
          >
            <Text style={styles.quickFilterText}>⚽ Sports</Text>
          </TouchableOpacity>
        </ScrollView>

        {/* Results or Trending */}
        {loading ? (
          <View style={styles.loadingContainer}>
            <ActivityIndicator size="large" color="#FFFFFF" />
            <Text style={styles.loadingText}>Searching with AI...</Text>
          </View>
        ) : results.length > 0 ? (
          <View style={styles.resultsContainer}>
            <Text style={styles.sectionTitle}>
              {results.length} Results Found
            </Text>
            <FlatList
              data={results}
              renderItem={renderStation}
              keyExtractor={(item) => item.id}
              showsVerticalScrollIndicator={false}
              contentContainerStyle={styles.listContent}
            />
          </View>
        ) : trending.length > 0 && !searchQuery ? (
          <View style={styles.resultsContainer}>
            <Text style={styles.sectionTitle}>
              🔥 Trending Now
            </Text>
            <FlatList
              data={trending}
              renderItem={renderStation}
              keyExtractor={(item) => item.id}
              showsVerticalScrollIndicator={false}
              contentContainerStyle={styles.listContent}
            />
          </View>
        ) : searchQuery ? (
          <View style={styles.emptyContainer}>
            <Ionicons name="search-outline" size={64} color="#333333" />
            <Text style={styles.emptyTitle}>No Results Found</Text>
            <Text style={styles.emptyText}>
              Try different keywords or use our quick filters
            </Text>
          </View>
        ) : null}
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
    height: '100%',
    backgroundColor: '#000000',
  },
  content: {
    flex: 1,
    padding: 16,
  },
  searchSection: {
    marginBottom: 16,
  },
  searchContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#1A1A1A',
    borderRadius: 12,
    paddingHorizontal: 16,
    marginBottom: 12,
    borderWidth: 2,
    borderColor: '#FFFFFF',
  },
  searchIcon: {
    marginRight: 8,
  },
  searchInput: {
    flex: 1,
    height: 50,
    fontSize: 16,
    color: '#FFFFFF',
  },
  searchButton: {
    backgroundColor: '#FFFFFF',
    borderRadius: 12,
    height: 50,
    justifyContent: 'center',
    alignItems: 'center',
  },
  searchButtonText: {
    color: '#000000',
    fontSize: 16,
    fontWeight: '700',
  },
  intentCard: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#1A1A1A',
    padding: 12,
    borderRadius: 8,
    marginBottom: 16,
    borderWidth: 1,
    borderColor: '#FFFFFF',
    gap: 8,
  },
  intentText: {
    color: '#FFFFFF',
    fontSize: 14,
    flex: 1,
  },
  quickFilters: {
    marginBottom: 16,
    maxHeight: 50,
  },
  quickFiltersContent: {
    gap: 8,
    paddingRight: 16,
  },
  quickFilterChip: {
    backgroundColor: '#1A1A1A',
    paddingHorizontal: 16,
    paddingVertical: 10,
    borderRadius: 20,
    borderWidth: 1,
    borderColor: '#FFFFFF',
  },
  quickFilterText: {
    color: '#FFFFFF',
    fontSize: 14,
    fontWeight: '600',
  },
  resultsContainer: {
    flex: 1,
  },
  sectionTitle: {
    fontSize: 20,
    fontWeight: '700',
    color: '#FFFFFF',
    marginBottom: 16,
  },
  listContent: {
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
  stationHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
  },
  stationInfo: {
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
  playButton: {
    padding: 4,
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
  },
});
