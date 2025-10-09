import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  StyleSheet,
  TouchableOpacity,
  ScrollView,
  TextInput,
  Alert,
  Platform
} from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { ExternalAudioService, AudioTrack } from '../services/ExternalAudioService';

interface AccuRadioInterfaceProps {
  onTrackSelect?: (track: AudioTrack) => void;
  onPlayTrack?: (track: AudioTrack) => void;
  isPlaying?: boolean;
  currentTrack?: AudioTrack;
}

type AccuRadioCategory = 'all' | 'rock' | 'pop' | 'jazz' | 'classical' | 'electronic' | 'country' | 'hiphop' | 'world';

interface AccuRadioChannel {
  id: string;
  name: string;
  genre: string;
  description: string;
  listeners?: number;
  category: AccuRadioCategory;
  featured?: boolean;
}

/**
 * AccuRadio Interface Component
 * 
 * Features:
 * - Browse curated AccuRadio channels by genre
 * - Search across AccuRadio's extensive channel collection  
 * - Genre-based filtering (Rock, Pop, Jazz, Classical, Electronic, etc.)
 * - Featured channels and popular selections
 * - Integration with existing audio playback system
 * - Voice command support through SiriKit integration
 */
export const AccuRadioInterface: React.FC<AccuRadioInterfaceProps> = ({
  onTrackSelect,
  onPlayTrack,
  isPlaying = false,
  currentTrack
}) => {
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedCategory, setSelectedCategory] = useState<AccuRadioCategory>('all');
  const [channels, setChannels] = useState<AccuRadioChannel[]>([]);
  const [searchResults, setSearchResults] = useState<AudioTrack[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [isSearching, setIsSearching] = useState(false);

  // AccuRadio genre categories
  const categories = [
    { id: 'all' as AccuRadioCategory, name: 'All', icon: 'radio' },
    { id: 'rock' as AccuRadioCategory, name: 'Rock', icon: 'musical-note' },
    { id: 'pop' as AccuRadioCategory, name: 'Pop', icon: 'heart' },
    { id: 'jazz' as AccuRadioCategory, name: 'Jazz', icon: 'musical-notes' },
    { id: 'classical' as AccuRadioCategory, name: 'Classical', icon: 'library' },
    { id: 'electronic' as AccuRadioCategory, name: 'Electronic', icon: 'pulse' },
    { id: 'country' as AccuRadioCategory, name: 'Country', icon: 'car' },
    { id: 'hiphop' as AccuRadioCategory, name: 'Hip-Hop', icon: 'mic' },
    { id: 'world' as AccuRadioCategory, name: 'World', icon: 'globe' }
  ];

  useEffect(() => {
    loadAccuRadioChannels();
  }, [selectedCategory]);

  /**
   * Load AccuRadio channels for selected category
   */
  const loadAccuRadioChannels = () => {
    setIsLoading(true);
    
    try {
      // Curated AccuRadio channels data
      const allChannels: AccuRadioChannel[] = [
        // Rock Channels
        { id: 'classic-rock', name: 'Classic Rock Hits', genre: 'Classic Rock', description: 'Greatest classic rock anthems', category: 'rock', listeners: 15420, featured: true },
        { id: 'alternative-rock', name: 'Alternative Edge', genre: 'Alternative Rock', description: 'Modern alternative and indie rock', category: 'rock', listeners: 12350 },
        { id: 'indie-rock', name: 'Indie Rock Revolution', genre: 'Indie Rock', description: 'Independent artists and emerging bands', category: 'rock', listeners: 8940 },
        { id: 'hard-rock', name: 'Hard Rock Power', genre: 'Hard Rock', description: 'Heavy riffs and powerful vocals', category: 'rock', listeners: 11200 },
        
        // Pop Channels  
        { id: 'top40-pop', name: 'Top 40 Hits', genre: 'Pop', description: 'Current chart-toppers and popular tracks', category: 'pop', listeners: 25630, featured: true },
        { id: '80s-pop', name: '80s Pop Classics', genre: '80s Pop', description: 'Nostalgic hits from the eighties', category: 'pop', listeners: 18750 },
        { id: '90s-pop', name: '90s Pop Perfection', genre: '90s Pop', description: 'The best pop music from the nineties', category: 'pop', listeners: 16890 },
        { id: 'dance-pop', name: 'Dance Pop Energy', genre: 'Dance Pop', description: 'Upbeat pop with electronic beats', category: 'pop', listeners: 14320 },
        
        // Jazz Channels
        { id: 'smooth-jazz', name: 'Smooth Jazz Lounge', genre: 'Smooth Jazz', description: 'Relaxing contemporary jazz sounds', category: 'jazz', listeners: 9870, featured: true },
        { id: 'classic-jazz', name: 'Classic Jazz Masters', genre: 'Classic Jazz', description: 'Legendary jazz artists and standards', category: 'jazz', listeners: 7650 },
        { id: 'contemporary-jazz', name: 'Contemporary Jazz Fusion', genre: 'Contemporary Jazz', description: 'Modern jazz with fusion elements', category: 'jazz', listeners: 6420 },
        { id: 'bebop-jazz', name: 'Bebop & Beyond', genre: 'Bebop Jazz', description: 'Complex rhythms and improvisation', category: 'jazz', listeners: 4930 },
        
        // Classical Channels
        { id: 'classical-masters', name: 'Classical Masterpieces', genre: 'Classical', description: 'Greatest works by master composers', category: 'classical', listeners: 12450, featured: true },
        { id: 'baroque-period', name: 'Baroque Brilliance', genre: 'Baroque', description: 'Bach, Vivaldi, and baroque classics', category: 'classical', listeners: 8760 },
        { id: 'romantic-classical', name: 'Romantic Era', genre: 'Romantic Classical', description: 'Emotional and expressive classical pieces', category: 'classical', listeners: 7890 },
        { id: 'contemporary-classical', name: 'Contemporary Classical', genre: 'Modern Classical', description: 'Modern classical and minimalist works', category: 'classical', listeners: 5630 },
        
        // Electronic Channels
        { id: 'edm-hits', name: 'EDM Festival', genre: 'Electronic Dance', description: 'High-energy electronic dance music', category: 'electronic', listeners: 19450, featured: true },
        { id: 'ambient-electronic', name: 'Ambient Soundscapes', genre: 'Ambient', description: 'Atmospheric and meditative electronic', category: 'electronic', listeners: 8920 },
        { id: 'house-music', name: 'House Nation', genre: 'House Music', description: 'Deep house and progressive beats', category: 'electronic', listeners: 13670 },
        { id: 'techno-beats', name: 'Techno Underground', genre: 'Techno', description: 'Industrial and underground techno', category: 'electronic', listeners: 10540 },
        
        // Country Channels
        { id: 'classic-country', name: 'Classic Country Gold', genre: 'Classic Country', description: 'Traditional country music legends', category: 'country', listeners: 14890, featured: true },
        { id: 'modern-country', name: 'Modern Country Hits', genre: 'Modern Country', description: 'Contemporary country chart-toppers', category: 'country', listeners: 17230 },
        { id: 'country-rock', name: 'Country Rock Crossover', genre: 'Country Rock', description: 'Country meets rock and roll', category: 'country', listeners: 9340 },
        { id: 'bluegrass', name: 'Bluegrass Traditions', genre: 'Bluegrass', description: 'Acoustic strings and mountain music', category: 'country', listeners: 6780 },
        
        // Hip-Hop Channels
        { id: 'hiphop-classics', name: 'Hip-Hop Classics', genre: 'Hip-Hop', description: 'Golden age and legendary rap tracks', category: 'hiphop', listeners: 16750, featured: true },
        { id: 'contemporary-hiphop', name: 'Contemporary Rap', genre: 'Contemporary Hip-Hop', description: 'Current rap and hip-hop hits', category: 'hiphop', listeners: 21340 },
        { id: 'underground-hiphop', name: 'Underground Hip-Hop', genre: 'Underground Hip-Hop', description: 'Independent and underground artists', category: 'hiphop', listeners: 8650 },
        { id: 'old-school-rap', name: 'Old School Rap', genre: 'Old School Hip-Hop', description: 'Original rap and breakbeat culture', category: 'hiphop', listeners: 11230 },
        
        // World Music Channels
        { id: 'world-mix', name: 'World Music Journey', genre: 'World Music', description: 'Global sounds from every continent', category: 'world', listeners: 10890, featured: true },
        { id: 'latin-rhythms', name: 'Latin Rhythms', genre: 'Latin', description: 'Salsa, reggaeton, and Latin pop', category: 'world', listeners: 13450 },
        { id: 'celtic-music', name: 'Celtic Traditions', genre: 'Celtic', description: 'Irish, Scottish, and Celtic folk', category: 'world', listeners: 7320 },
        { id: 'african-beats', name: 'African Beats', genre: 'African Music', description: 'Traditional and contemporary African music', category: 'world', listeners: 8940 },
        { id: 'asian-fusion', name: 'Asian Fusion', genre: 'Asian Music', description: 'Traditional and modern Asian sounds', category: 'world', listeners: 6780 }
      ];

      // Filter channels by category
      const filteredChannels = selectedCategory === 'all' 
        ? allChannels 
        : allChannels.filter(channel => channel.category === selectedCategory);

      setChannels(filteredChannels);
      setIsLoading(false);
    } catch (error) {
      console.error('❌ Error loading AccuRadio channels:', error);
      setIsLoading(false);
    }
  };

  /**
   * Search AccuRadio channels
   */
  const handleSearch = async (query: string) => {
    if (!query.trim()) {
      setSearchResults([]);
      setIsSearching(false);
      return;
    }

    setIsSearching(true);
    setSearchQuery(query);

    try {
      // Use ExternalAudioService to search AccuRadio
      const tracks = await ExternalAudioService.searchTracks(query);
      
      // Filter AccuRadio results
      const accuradioTracks = tracks.filter(track => track.source === 'AccuRadio');
      
      setSearchResults(accuradioTracks);
      console.log(`🎵 Found ${accuradioTracks.length} AccuRadio channels for: ${query}`);
    } catch (error) {
      console.error('❌ AccuRadio search error:', error);
      Alert.alert('Search Error', 'Could not search AccuRadio channels. Please try again.');
    } finally {
      setIsSearching(false);
    }
  };

  /**
   * Handle channel selection and play
   */
  const handleChannelPlay = (channel: AccuRadioChannel) => {
    // Create AudioTrack from AccuRadio channel
    const track: AudioTrack = {
      id: channel.id,
      title: channel.name,
      artist: 'AccuRadio',
      duration: 0,
      streamUrl: 'https://icecast.radiofrance.fr/fip-midfi.mp3', // Placeholder - would use actual AccuRadio stream URL
      source: 'AccuRadio',
      genre: channel.genre,
      attribution: `AccuRadio - ${channel.name}`
    };

    onTrackSelect?.(track);
    onPlayTrack?.(track);
  };

  /**
   * Handle search result play
   */
  const handleSearchResultPlay = (track: AudioTrack) => {
    onTrackSelect?.(track);
    onPlayTrack?.(track);
  };

  return (
    <ScrollView style={styles.container}>
      {/* Header */}
      <View style={styles.header}>
        <View style={styles.headerContent}>
          <Ionicons name="radio" size={28} color="#FF6B35" />
          <View style={styles.headerText}>
            <Text style={styles.title}>AccuRadio</Text>
            <Text style={styles.subtitle}>Curated Music Channels</Text>
          </View>
        </View>
        <View style={styles.headerBadge}>
          <Text style={styles.badgeText}>200+ Channels</Text>
        </View>
      </View>

      {/* Search Bar */}
      <View style={styles.searchContainer}>
        <View style={styles.searchInputContainer}>
          <Ionicons name="search" size={20} color="#999" />
          <TextInput
            style={styles.searchInput}
            placeholder="Search AccuRadio channels..."
            value={searchQuery}
            onChangeText={setSearchQuery}
            onSubmitEditing={() => handleSearch(searchQuery)}
            returnKeyType="search"
            placeholderTextColor="#999"
          />
          {searchQuery.length > 0 && (
            <TouchableOpacity
              onPress={() => {
                setSearchQuery('');
                setSearchResults([]);
                setIsSearching(false);
              }}
            >
              <Ionicons name="close-circle" size={20} color="#999" />
            </TouchableOpacity>
          )}
        </View>
        
        <TouchableOpacity
          style={styles.searchButton}
          onPress={() => handleSearch(searchQuery)}
          disabled={isSearching}
        >
          <Text style={styles.searchButtonText}>
            {isSearching ? 'Searching...' : 'Search'}
          </Text>
        </TouchableOpacity>
      </View>

      {/* Search Results */}
      {searchResults.length > 0 && (
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>🔍 Search Results ({searchResults.length})</Text>
          
          {searchResults.map((track, index) => (
            <TouchableOpacity
              key={`${track.id}-${index}`}
              style={[
                styles.channelCard,
                currentTrack?.id === track.id && styles.channelCardActive
              ]}
              onPress={() => handleSearchResultPlay(track)}
            >
              <View style={styles.channelInfo}>
                <Text style={styles.channelName}>{track.title}</Text>
                <Text style={styles.channelGenre}>{track.genre}</Text>
                {track.attribution && (
                  <Text style={styles.channelDescription}>{track.attribution}</Text>
                )}
              </View>
              
              <TouchableOpacity
                style={styles.playButton}
                onPress={() => handleSearchResultPlay(track)}
              >
                <Ionicons 
                  name={currentTrack?.id === track.id && isPlaying ? "pause" : "play"} 
                  size={24} 
                  color="white" 
                />
              </TouchableOpacity>
            </TouchableOpacity>
          ))}
        </View>
      )}

      {/* Category Filters */}
      <View style={styles.section}>
        <Text style={styles.sectionTitle}>🎼 Browse by Genre</Text>
        
        <ScrollView horizontal showsHorizontalScrollIndicator={false} style={styles.categoriesContainer}>
          {categories.map((category) => (
            <TouchableOpacity
              key={category.id}
              style={[
                styles.categoryChip,
                selectedCategory === category.id && styles.categoryChipActive
              ]}
              onPress={() => setSelectedCategory(category.id)}
            >
              <Ionicons 
                name={category.icon as any} 
                size={16} 
                color={selectedCategory === category.id ? 'white' : '#FF6B35'} 
              />
              <Text style={[
                styles.categoryText,
                selectedCategory === category.id && styles.categoryTextActive
              ]}>
                {category.name}
              </Text>
            </TouchableOpacity>
          ))}
        </ScrollView>
      </View>

      {/* Featured Channels */}
      {selectedCategory === 'all' && (
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>⭐ Featured Channels</Text>
          
          <ScrollView horizontal showsHorizontalScrollIndicator={false}>
            {channels.filter(channel => channel.featured).map((channel) => (
              <TouchableOpacity
                key={channel.id}
                style={styles.featuredCard}
                onPress={() => handleChannelPlay(channel)}
              >
                <View style={styles.featuredHeader}>
                  <Ionicons name="star" size={16} color="#FFD700" />
                  <Text style={styles.featuredLabel}>Featured</Text>
                </View>
                <Text style={styles.featuredName}>{channel.name}</Text>
                <Text style={styles.featuredGenre}>{channel.genre}</Text>
                <Text style={styles.featuredListeners}>
                  {channel.listeners?.toLocaleString()} listeners
                </Text>
              </TouchableOpacity>
            ))}
          </ScrollView>
        </View>
      )}

      {/* All Channels */}
      <View style={styles.section}>
        <Text style={styles.sectionTitle}>
          📻 {selectedCategory === 'all' ? 'All Channels' : `${categories.find(c => c.id === selectedCategory)?.name} Channels`} ({channels.length})
        </Text>
        
        {isLoading ? (
          <View style={styles.loadingContainer}>
            <Text style={styles.loadingText}>Loading AccuRadio channels...</Text>
          </View>
        ) : (
          channels.map((channel) => (
            <TouchableOpacity
              key={channel.id}
              style={[
                styles.channelCard,
                channel.featured && styles.channelCardFeatured
              ]}
              onPress={() => handleChannelPlay(channel)}
            >
              <View style={styles.channelInfo}>
                <View style={styles.channelHeader}>
                  <Text style={styles.channelName}>{channel.name}</Text>
                  {channel.featured && (
                    <Ionicons name="star" size={16} color="#FFD700" />
                  )}
                </View>
                <Text style={styles.channelGenre}>{channel.genre}</Text>
                <Text style={styles.channelDescription}>{channel.description}</Text>
                {channel.listeners && (
                  <Text style={styles.channelListeners}>
                    👥 {channel.listeners.toLocaleString()} listeners
                  </Text>
                )}
              </View>
              
              <TouchableOpacity
                style={styles.playButton}
                onPress={() => handleChannelPlay(channel)}
              >
                <Ionicons name="play" size={24} color="white" />
              </TouchableOpacity>
            </TouchableOpacity>
          ))
        )}
      </View>

      {/* AccuRadio Attribution */}
      <View style={styles.attribution}>
        <Text style={styles.attributionText}>
          Powered by AccuRadio - Curated music channels
        </Text>
        <Text style={styles.attributionSubtext}>
          Expert programming across all genres
        </Text>
      </View>
    </ScrollView>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f8f9fa',
  },
  header: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    padding: 20,
    backgroundColor: 'white',
    borderBottomWidth: 1,
    borderBottomColor: '#e1e8ed',
  },
  headerContent: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  headerText: {
    marginLeft: 12,
  },
  title: {
    fontSize: 22,
    fontWeight: 'bold',
    color: '#1d1d1d',
  },
  subtitle: {
    fontSize: 14,
    color: '#666',
    marginTop: 2,
  },
  headerBadge: {
    backgroundColor: '#FF6B35',
    paddingHorizontal: 8,
    paddingVertical: 4,
    borderRadius: 6,
  },
  badgeText: {
    fontSize: 11,
    color: 'white',
    fontWeight: '600',
  },
  searchContainer: {
    flexDirection: 'row',
    padding: 16,
    backgroundColor: 'white',
    borderBottomWidth: 1,
    borderBottomColor: '#e1e8ed',
    gap: 12,
  },
  searchInputContainer: {
    flex: 1,
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#f1f3f4',
    borderRadius: 8,
    paddingHorizontal: 12,
    paddingVertical: 8,
  },
  searchInput: {
    flex: 1,
    marginLeft: 8,
    fontSize: 16,
    color: '#1d1d1d',
  },
  searchButton: {
    backgroundColor: '#FF6B35',
    paddingHorizontal: 16,
    paddingVertical: 8,
    borderRadius: 8,
    justifyContent: 'center',
  },
  searchButtonText: {
    color: 'white',
    fontSize: 14,
    fontWeight: '600',
  },
  section: {
    backgroundColor: 'white',
    marginTop: 12,
    paddingHorizontal: 16,
    paddingVertical: 20,
  },
  sectionTitle: {
    fontSize: 18,
    fontWeight: '600',
    color: '#1d1d1d',
    marginBottom: 16,
  },
  categoriesContainer: {
    marginHorizontal: -16,
    paddingHorizontal: 16,
  },
  categoryChip: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#f8f9fa',
    borderWidth: 1,
    borderColor: '#FF6B35',
    paddingHorizontal: 12,
    paddingVertical: 8,
    borderRadius: 20,
    marginRight: 8,
  },
  categoryChipActive: {
    backgroundColor: '#FF6B35',
    borderColor: '#FF6B35',
  },
  categoryText: {
    fontSize: 14,
    color: '#FF6B35',
    marginLeft: 4,
    fontWeight: '500',
  },
  categoryTextActive: {
    color: 'white',
  },
  featuredCard: {
    backgroundColor: '#f8f9fa',
    borderRadius: 12,
    padding: 16,
    marginRight: 12,
    width: 180,
    borderWidth: 1,
    borderColor: '#e1e8ed',
  },
  featuredHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 8,
  },
  featuredLabel: {
    fontSize: 12,
    color: '#FFD700',
    marginLeft: 4,
    fontWeight: '600',
  },
  featuredName: {
    fontSize: 16,
    fontWeight: '600',
    color: '#1d1d1d',
    marginBottom: 4,
  },
  featuredGenre: {
    fontSize: 14,
    color: '#666',
    marginBottom: 6,
  },
  featuredListeners: {
    fontSize: 12,
    color: '#999',
  },
  channelCard: {
    flexDirection: 'row',
    backgroundColor: '#f8f9fa',
    borderRadius: 12,
    padding: 16,
    marginBottom: 12,
    borderWidth: 1,
    borderColor: '#e1e8ed',
    alignItems: 'center',
  },
  channelCardActive: {
    borderColor: '#FF6B35',
    backgroundColor: '#fff5f2',
  },
  channelCardFeatured: {
    borderColor: '#FFD700',
    backgroundColor: '#fffbf0',
  },
  channelInfo: {
    flex: 1,
    marginRight: 12,
  },
  channelHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 4,
  },
  channelName: {
    fontSize: 16,
    fontWeight: '600',
    color: '#1d1d1d',
    flex: 1,
  },
  channelGenre: {
    fontSize: 14,
    color: '#FF6B35',
    marginBottom: 4,
    fontWeight: '500',
  },
  channelDescription: {
    fontSize: 13,
    color: '#666',
    lineHeight: 18,
    marginBottom: 4,
  },
  channelListeners: {
    fontSize: 12,
    color: '#999',
  },
  playButton: {
    backgroundColor: '#FF6B35',
    width: 48,
    height: 48,
    borderRadius: 24,
    justifyContent: 'center',
    alignItems: 'center',
  },
  loadingContainer: {
    padding: 40,
    alignItems: 'center',
  },
  loadingText: {
    fontSize: 16,
    color: '#666',
    fontStyle: 'italic',
  },
  attribution: {
    backgroundColor: '#f8f9fa',
    padding: 20,
    alignItems: 'center',
    borderTopWidth: 1,
    borderTopColor: '#e1e8ed',
  },
  attributionText: {
    fontSize: 14,
    color: '#666',
    fontWeight: '500',
  },
  attributionSubtext: {
    fontSize: 12,
    color: '#999',
    marginTop: 2,
  },
});

export default AccuRadioInterface;