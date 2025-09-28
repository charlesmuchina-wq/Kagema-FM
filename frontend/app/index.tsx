import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  StyleSheet,
  TouchableOpacity,
  ActivityIndicator,
  Alert,
  SafeAreaView,
  StatusBar,
  Dimensions,
  Image,
  ScrollView,
  RefreshControl,
} from 'react-native';
import { Audio, AVPlaybackStatus } from 'expo-av';
import { Ionicons } from '@expo/vector-icons';
import { useLocation } from '../services/LocationService';
import ContentService from '../services/ContentService';

const { width } = Dimensions.get('window');
const EXPO_PUBLIC_BACKEND_URL = process.env.EXPO_PUBLIC_BACKEND_URL;

interface StationInfo {
  name: string;
  description: string;
  streamUrl: string;
  currentShow?: string;
}

interface WeatherData {
  location: string;
  temperature: number;
  feels_like: number;
  humidity: number;
  description: string;
  icon: string;
  timestamp: string;
}

interface NewsArticle {
  title: string;
  description: string;
  source: string;
  published_at: string;
  category?: string;
}

interface MusicTrack {
  id: string;
  name: string;
  artists: string[];
  album: string;
  popularity: number;
}

export default function KagemaFMApp() {
  const [sound, setSound] = useState<Audio.Sound | null>(null);
  const [isPlaying, setIsPlaying] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [isBuffering, setIsBuffering] = useState(false);
  const [stationInfo, setStationInfo] = useState<StationInfo | null>(null);
  const [error, setError] = useState<string | null>(null);
  
  // Enhanced state
  const [weatherData, setWeatherData] = useState<WeatherData | null>(null);
  const [newsArticles, setNewsArticles] = useState<NewsArticle[]>([]);
  const [newsSummary, setNewsSummary] = useState<string | null>(null);
  const [musicTracks, setMusicTracks] = useState<MusicTrack[]>([]);
  const [musicRecommendations, setMusicRecommendations] = useState<any>(null);
  const [refreshing, setRefreshing] = useState(false);
  const [activeTab, setActiveTab] = useState<'radio' | 'news' | 'music'>('radio');
  
  const { location, locationInfo, errorMsg: locationError, loading: locationLoading } = useLocation();

  useEffect(() => {
    setupAudio();
    fetchStationInfo();
    
    return () => {
      if (sound) {
        sound.unloadAsync();
      }
    };
  }, []);

  useEffect(() => {
    if (location && locationInfo) {
      loadEnhancedContent();
    }
  }, [location, locationInfo]);

  const setupAudio = async () => {
    try {
      await Audio.setAudioModeAsync({
        staysActiveInBackground: true,
        playsInSilentModeIOS: true,
        shouldDuckAndroid: false,
        playThroughEarpieceAndroid: false,
      });
    } catch (error) {
      console.error('Error setting up audio:', error);
    }
  };

  const fetchStationInfo = async () => {
    try {
      const response = await fetch(`${EXPO_PUBLIC_BACKEND_URL}/api/station-info`);
      const data = await response.json();
      setStationInfo(data);
    } catch (error) {
      console.error('Error fetching station info:', error);
      setStationInfo({
        name: 'Kagema FM',
        description: 'Your enhanced radio experience',
        streamUrl: 'http://ice1.somafm.com/groovesalad-256-mp3',
      });
    }
  };

  const loadEnhancedContent = async () => {
    if (!location) return;

    try {
      // Load weather data
      const weather = await ContentService.getWeatherData(
        location.coords.latitude,
        location.coords.longitude
      );
      setWeatherData(weather);

      // Load news
      const localNews = await ContentService.getLocalNews(10);
      const internationalNews = await ContentService.getInternationalNews(5);
      
      setNewsArticles([...localNews.articles, ...internationalNews.articles]);
      setNewsSummary(localNews.summary || 'Stay updated with the latest news.');

      // Load music
      const trendingMusic = await ContentService.getTrendingMusic('KE', 20);
      const kenyanMusic = await ContentService.getKenyanMusic(10);
      
      setMusicTracks([...trendingMusic.tracks, ...kenyanMusic.tracks]);
      setMusicRecommendations(trendingMusic.recommendations);

    } catch (error) {
      console.error('Error loading enhanced content:', error);
    }
  };

  const handlePlaybackStatusUpdate = (status: AVPlaybackStatus) => {
    if (status.isLoaded) {
      setIsBuffering(status.isBuffering || false);
      if (status.isPlaying !== isPlaying) {
        setIsPlaying(status.isPlaying);
      }
    } else if (status.error) {
      console.error('Playback error:', status.error);
      setError('Failed to play audio stream');
      setIsPlaying(false);
    }
  };

  const playRadio = async () => {
    if (!stationInfo) return;

    try {
      setIsLoading(true);
      setError(null);

      if (sound) {
        await sound.playAsync();
        setIsPlaying(true);
      } else {
        const { sound: newSound } = await Audio.Sound.createAsync(
          { uri: stationInfo.streamUrl },
          { 
            shouldPlay: true,
            isLooping: false,
            volume: 1.0,
          },
          handlePlaybackStatusUpdate
        );
        setSound(newSound);
        setIsPlaying(true);
      }
    } catch (error) {
      console.error('Error playing radio:', error);
      setError('Failed to connect to radio stream');
      Alert.alert('Playbook Error', 'Unable to connect to the radio stream. Please check your internet connection and try again.');
    } finally {
      setIsLoading(false);
    }
  };

  const pauseRadio = async () => {
    if (sound) {
      try {
        await sound.pauseAsync();
        setIsPlaying(false);
      } catch (error) {
        console.error('Error pausing radio:', error);
      }
    }
  };

  const stopRadio = async () => {
    if (sound) {
      try {
        await sound.stopAsync();
        await sound.unloadAsync();
        setSound(null);
        setIsPlaying(false);
        setIsBuffering(false);
      } catch (error) {
        console.error('Error stopping radio:', error);
      }
    }
  };

  const handlePlayPause = () => {
    if (isPlaying) {
      pauseRadio();
    } else {
      playRadio();
    }
  };

  const onRefresh = async () => {
    setRefreshing(true);
    await loadEnhancedContent();
    setRefreshing(false);
  };

  const renderRadioTab = () => (
    <ScrollView 
      style={styles.tabContent}
      refreshControl={<RefreshControl refreshing={refreshing} onRefresh={onRefresh} />}
    >
      {/* Station Info */}
      <View style={styles.stationContainer}>
        <View style={styles.logoContainer}>
          <Image
            source={require('../assets/kagema-fm-logo.jpg')}
            style={styles.logo}
          />
        </View>
        
        {stationInfo && (
          <>
            <Text style={styles.stationName}>{stationInfo.name}</Text>
            <Text style={styles.stationDescription}>{stationInfo.description}</Text>
            {stationInfo.currentShow && (
              <Text style={styles.currentShow}>Now Playing: {stationInfo.currentShow}</Text>
            )}
          </>
        )}

        {/* Location and Weather Info */}
        {locationInfo && (
          <View style={styles.locationContainer}>
            <View style={styles.locationRow}>
              <Ionicons name="location-outline" size={16} color="#ff6b6b" />
              <Text style={styles.locationText}>
                {locationInfo.city}, {locationInfo.country}
              </Text>
            </View>
            {weatherData && (
              <View style={styles.weatherContainer}>
                <Text style={styles.weatherTemp}>{Math.round(weatherData.temperature)}°C</Text>
                <Text style={styles.weatherDesc}>{weatherData.description}</Text>
                <Text style={styles.weatherFeels}>Feels like {Math.round(weatherData.feels_like)}°C</Text>
              </View>
            )}
          </View>
        )}
      </View>

      {/* Player Controls */}
      <View style={styles.playerContainer}>
        {error && (
          <Text style={styles.errorText}>{error}</Text>
        )}
        
        <View style={styles.controlsContainer}>
          <TouchableOpacity 
            style={styles.controlButton}
            onPress={stopRadio}
            disabled={!sound}
          >
            <Ionicons 
              name="stop" 
              size={30} 
              color={sound ? '#ff6b6b' : '#666'} 
            />
          </TouchableOpacity>

          <TouchableOpacity 
            style={[styles.playButton, isPlaying && styles.playButtonActive]}
            onPress={handlePlayPause}
            disabled={isLoading}
          >
            {isLoading || isBuffering ? (
              <ActivityIndicator size="large" color="#fff" />
            ) : (
              <Ionicons 
                name={isPlaying ? 'pause' : 'play'} 
                size={40} 
                color="#fff" 
              />
            )}
          </TouchableOpacity>

          <TouchableOpacity 
            style={styles.controlButton}
            onPress={onRefresh}
          >
            <Ionicons name="refresh" size={30} color="#ff6b6b" />
          </TouchableOpacity>
        </View>

        {isBuffering && !isLoading && (
          <Text style={styles.bufferingText}>Buffering...</Text>
        )}
      </View>

      {/* Status */}
      <View style={styles.statusContainer}>
        <View style={[styles.statusDot, { backgroundColor: isPlaying ? '#4CAF50' : '#666' }]} />
        <Text style={styles.statusText}>
          {isPlaying ? 'Live - ON AIR' : 'Offline'}
        </Text>
      </View>

      {/* Music Recommendations */}
      {musicRecommendations && (
        <View style={styles.recommendationsContainer}>
          <Text style={styles.sectionTitle}>AI Music Recommendations</Text>
          <Text style={styles.recommendationText}>{musicRecommendations.explanation}</Text>
          {musicRecommendations.genres && (
            <View style={styles.genreContainer}>
              {musicRecommendations.genres.map((genre, index) => (
                <View key={index} style={styles.genreTag}>
                  <Text style={styles.genreText}>{genre}</Text>
                </View>
              ))}
            </View>
          )}
        </View>
      )}
    </ScrollView>
  );

  const renderNewsTab = () => (
    <ScrollView 
      style={styles.tabContent}
      refreshControl={<RefreshControl refreshing={refreshing} onRefresh={onRefresh} />}
    >
      <Text style={styles.tabTitle}>Local & International News</Text>
      
      {newsSummary && (
        <View style={styles.summaryContainer}>
          <Text style={styles.summaryTitle}>Today's Summary</Text>
          <Text style={styles.summaryText}>{newsSummary}</Text>
        </View>
      )}

      {newsArticles.map((article, index) => (
        <View key={index} style={styles.newsItem}>
          <View style={styles.newsHeader}>
            <Text style={styles.newsSource}>{article.source}</Text>
            {article.category && (
              <View style={styles.categoryTag}>
                <Text style={styles.categoryText}>{article.category}</Text>
              </View>
            )}
          </View>
          <Text style={styles.newsTitle}>{article.title}</Text>
          <Text style={styles.newsDescription}>{article.description}</Text>
          <Text style={styles.newsTime}>
            {new Date(article.published_at).toLocaleDateString()}
          </Text>
        </View>
      ))}
    </ScrollView>
  );

  const renderMusicTab = () => (
    <ScrollView 
      style={styles.tabContent}
      refreshControl={<RefreshControl refreshing={refreshing} onRefresh={onRefresh} />}
    >
      <Text style={styles.tabTitle}>Trending Music</Text>
      
      {musicTracks.map((track, index) => (
        <View key={index} style={styles.musicItem}>
          <View style={styles.musicInfo}>
            <Text style={styles.musicTitle}>{track.name}</Text>
            <Text style={styles.musicArtist}>{track.artists.join(', ')}</Text>
            <Text style={styles.musicAlbum}>{track.album}</Text>
          </View>
          <View style={styles.musicPopularity}>
            <View style={styles.popularityBar}>
              <View 
                style={[
                  styles.popularityFill,
                  { width: `${track.popularity}%` }
                ]}
              />
            </View>
            <Text style={styles.popularityText}>{track.popularity}%</Text>
          </View>
        </View>
      ))}
    </ScrollView>
  );

  return (
    <SafeAreaView style={styles.container}>
      <StatusBar barStyle="light-content" backgroundColor="#1a1a2e" />
      
      {/* Header */}
      <View style={styles.header}>
        <Text style={styles.headerTitle}>Kagema FM</Text>
        <Text style={styles.headerSubtitle}>Enhanced Radio Experience</Text>
      </View>

      {/* Tab Navigation */}
      <View style={styles.tabNavigation}>
        <TouchableOpacity 
          style={[styles.tabButton, activeTab === 'radio' && styles.activeTabButton]}
          onPress={() => setActiveTab('radio')}
        >
          <Ionicons 
            name="radio" 
            size={24} 
            color={activeTab === 'radio' ? '#fff' : '#ff6b6b'} 
          />
          <Text style={[styles.tabText, activeTab === 'radio' && styles.activeTabText]}>
            Radio
          </Text>
        </TouchableOpacity>
        
        <TouchableOpacity 
          style={[styles.tabButton, activeTab === 'news' && styles.activeTabButton]}
          onPress={() => setActiveTab('news')}
        >
          <Ionicons 
            name="newspaper" 
            size={24} 
            color={activeTab === 'news' ? '#fff' : '#ff6b6b'} 
          />
          <Text style={[styles.tabText, activeTab === 'news' && styles.activeTabText]}>
            News
          </Text>
        </TouchableOpacity>
        
        <TouchableOpacity 
          style={[styles.tabButton, activeTab === 'music' && styles.activeTabButton]}
          onPress={() => setActiveTab('music')}
        >
          <Ionicons 
            name="musical-notes" 
            size={24} 
            color={activeTab === 'music' ? '#fff' : '#ff6b6b'} 
          />
          <Text style={[styles.tabText, activeTab === 'music' && styles.activeTabText]}>
            Music
          </Text>
        </TouchableOpacity>
      </View>

      {/* Tab Content */}
      {activeTab === 'radio' && renderRadioTab()}
      {activeTab === 'news' && renderNewsTab()}
      {activeTab === 'music' && renderMusicTab()}
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#1a1a2e',
  },
  header: {
    alignItems: 'center',
    paddingVertical: 20,
    borderBottomWidth: 1,
    borderBottomColor: '#2d2d54',
  },
  headerTitle: {
    fontSize: 28,
    fontWeight: 'bold',
    color: '#fff',
    marginBottom: 5,
  },
  headerSubtitle: {
    fontSize: 14,
    color: '#ff6b6b',
    textTransform: 'uppercase',
    letterSpacing: 1,
  },
  tabNavigation: {
    flexDirection: 'row',
    backgroundColor: '#2d2d54',
    paddingVertical: 10,
  },
  tabButton: {
    flex: 1,
    alignItems: 'center',
    paddingVertical: 10,
  },
  activeTabButton: {
    backgroundColor: '#ff6b6b',
    marginHorizontal: 5,
    borderRadius: 10,
  },
  tabText: {
    color: '#ff6b6b',
    fontSize: 12,
    marginTop: 4,
  },
  activeTabText: {
    color: '#fff',
  },
  tabContent: {
    flex: 1,
  },
  tabTitle: {
    fontSize: 20,
    fontWeight: 'bold',
    color: '#fff',
    textAlign: 'center',
    paddingVertical: 20,
  },
  stationContainer: {
    alignItems: 'center',
    paddingHorizontal: 30,
    paddingVertical: 20,
  },
  logoContainer: {
    marginBottom: 20,
  },
  logo: {
    width: 100,
    height: 100,
    borderRadius: 50,
    borderWidth: 3,
    borderColor: '#ff6b6b',
  },
  stationName: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#fff',
    textAlign: 'center',
    marginBottom: 10,
  },
  stationDescription: {
    fontSize: 16,
    color: '#ccc',
    textAlign: 'center',
    marginBottom: 15,
  },
  currentShow: {
    fontSize: 14,
    color: '#ff6b6b',
    textAlign: 'center',
    fontStyle: 'italic',
  },
  locationContainer: {
    marginTop: 20,
    alignItems: 'center',
  },
  locationRow: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 10,
  },
  locationText: {
    color: '#ccc',
    fontSize: 14,
    marginLeft: 5,
  },
  weatherContainer: {
    alignItems: 'center',
    backgroundColor: '#2d2d54',
    padding: 15,
    borderRadius: 10,
    minWidth: 150,
  },
  weatherTemp: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#ff6b6b',
  },
  weatherDesc: {
    fontSize: 14,
    color: '#fff',
    marginVertical: 5,
  },
  weatherFeels: {
    fontSize: 12,
    color: '#ccc',
  },
  playerContainer: {
    paddingHorizontal: 30,
    paddingVertical: 30,
  },
  errorText: {
    color: '#f44336',
    textAlign: 'center',
    marginBottom: 20,
    fontSize: 14,
  },
  controlsContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    marginBottom: 20,
  },
  controlButton: {
    width: 60,
    height: 60,
    borderRadius: 30,
    backgroundColor: '#2d2d54',
    alignItems: 'center',
    justifyContent: 'center',
    marginHorizontal: 15,
  },
  playButton: {
    width: 80,
    height: 80,
    borderRadius: 40,
    backgroundColor: '#ff6b6b',
    alignItems: 'center',
    justifyContent: 'center',
    marginHorizontal: 15,
    elevation: 5,
    shadowColor: '#ff6b6b',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.3,
    shadowRadius: 4,
  },
  playButtonActive: {
    backgroundColor: '#ff5252',
  },
  bufferingText: {
    color: '#ccc',
    textAlign: 'center',
    fontSize: 14,
    marginTop: 10,
  },
  statusContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    paddingBottom: 20,
  },
  statusDot: {
    width: 10,
    height: 10,
    borderRadius: 5,
    marginRight: 10,
  },
  statusText: {
    color: '#ccc',
    fontSize: 14,
    fontWeight: '500',
  },
  recommendationsContainer: {
    margin: 20,
    padding: 20,
    backgroundColor: '#2d2d54',
    borderRadius: 10,
  },
  sectionTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#ff6b6b',
    marginBottom: 10,
  },
  recommendationText: {
    color: '#fff',
    fontSize: 14,
    lineHeight: 20,
    marginBottom: 10,
  },
  genreContainer: {
    flexDirection: 'row',
    flexWrap: 'wrap',
  },
  genreTag: {
    backgroundColor: '#ff6b6b',
    paddingHorizontal: 12,
    paddingVertical: 6,
    borderRadius: 15,
    marginRight: 8,
    marginBottom: 8,
  },
  genreText: {
    color: '#fff',
    fontSize: 12,
  },
  summaryContainer: {
    margin: 20,
    padding: 15,
    backgroundColor: '#2d2d54',
    borderRadius: 10,
  },
  summaryTitle: {
    fontSize: 16,
    fontWeight: 'bold',
    color: '#ff6b6b',
    marginBottom: 10,
  },
  summaryText: {
    color: '#fff',
    fontSize: 14,
    lineHeight: 20,
  },
  newsItem: {
    margin: 20,
    padding: 15,
    backgroundColor: '#2d2d54',
    borderRadius: 10,
    borderLeftWidth: 4,
    borderLeftColor: '#ff6b6b',
  },
  newsHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 8,
  },
  newsSource: {
    color: '#ff6b6b',
    fontSize: 12,
    fontWeight: 'bold',
  },
  categoryTag: {
    backgroundColor: '#ff6b6b',
    paddingHorizontal: 8,
    paddingVertical: 4,
    borderRadius: 10,
  },
  categoryText: {
    color: '#fff',
    fontSize: 10,
    textTransform: 'uppercase',
  },
  newsTitle: {
    color: '#fff',
    fontSize: 16,
    fontWeight: 'bold',
    marginBottom: 8,
  },
  newsDescription: {
    color: '#ccc',
    fontSize: 14,
    lineHeight: 18,
    marginBottom: 8,
  },
  newsTime: {
    color: '#999',
    fontSize: 12,
  },
  musicItem: {
    flexDirection: 'row',
    alignItems: 'center',
    margin: 20,
    padding: 15,
    backgroundColor: '#2d2d54',
    borderRadius: 10,
  },
  musicInfo: {
    flex: 1,
  },
  musicTitle: {
    color: '#fff',
    fontSize: 16,
    fontWeight: 'bold',
    marginBottom: 4,
  },
  musicArtist: {
    color: '#ff6b6b',
    fontSize: 14,
    marginBottom: 2,
  },
  musicAlbum: {
    color: '#ccc',
    fontSize: 12,
  },
  musicPopularity: {
    alignItems: 'center',
    minWidth: 60,
  },
  popularityBar: {
    width: 40,
    height: 4,
    backgroundColor: '#444',
    borderRadius: 2,
    overflow: 'hidden',
  },
  popularityFill: {
    height: '100%',
    backgroundColor: '#ff6b6b',
  },
  popularityText: {
    color: '#ccc',
    fontSize: 10,
    marginTop: 4,
  },
});