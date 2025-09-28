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
  Modal,
  FlatList,
} from 'react-native';
import { Audio, AVPlaybackStatus } from 'expo-av';
import { Ionicons } from '@expo/vector-icons';
import { useLocation } from '../services/LocationService';
import ContentService from '../services/ContentService';
import LanguageService from '../services/LanguageService';

const { width } = Dimensions.get('window');
const EXPO_PUBLIC_BACKEND_URL = process.env.EXPO_PUBLIC_BACKEND_URL;

interface StationInfo {
  name: string;
  description: string;
  streamUrl: string;
  currentShow?: string;
  detected_language?: string;
  alternative_streams?: Array<{ name: string; stream: string; frequency: string }>;
  localized_content?: any;
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

interface LanguageData {
  detected_language: string;
  alternative_languages: string[];
  county: string;
  confidence: number;
  language_info: any;
  regional_stations: Array<{ name: string; stream: string; frequency: string }>;
  localized_content: any;
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
  const [activeTab, setActiveTab] = useState<'radio' | 'news' | 'music' | 'language'>('radio');
  
  // Language detection state
  const [languageData, setLanguageData] = useState<LanguageData | null>(null);
  const [showLanguageModal, setShowLanguageModal] = useState(false);
  const [supportedLanguages, setSupportedLanguages] = useState<any[]>([]);
  const [selectedStation, setSelectedStation] = useState<any>(null);
  
  const { location, locationInfo, errorMsg: locationError, loading: locationLoading } = useLocation();

  useEffect(() => {
    setupAudio();
    loadSupportedLanguages();
    
    return () => {
      if (sound) {
        sound.unloadAsync();
      }
    };
  }, []);

  useEffect(() => {
    if (location && locationInfo) {
      loadMultilingualContent();
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

  const loadSupportedLanguages = async () => {
    try {
      const languages = await LanguageService.getSupportedLanguages();
      setSupportedLanguages(languages.supported_languages || []);
    } catch (error) {
      console.error('Error loading supported languages:', error);
    }
  };

  const loadMultilingualContent = async () => {
    if (!location) return;

    try {
      setIsLoading(true);

      // Detect language based on location
      const langData = await LanguageService.detectLanguage(
        location.coords.latitude,
        location.coords.longitude
      );
      setLanguageData(langData);

      // Get multilingual station info
      const multilingualStation = await LanguageService.getMultilingualStationInfo(
        location.coords.latitude,
        location.coords.longitude
      );
      if (multilingualStation) {
        setStationInfo(multilingualStation);
      }

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
      console.error('Error loading multilingual content:', error);
    } finally {
      setIsLoading(false);
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

  const playRadio = async (streamUrl?: string) => {
    const url = streamUrl || stationInfo?.streamUrl;
    if (!url) return;

    try {
      setIsLoading(true);
      setError(null);

      // Stop current sound if playing
      if (sound) {
        await sound.unloadAsync();
        setSound(null);
      }

      const { sound: newSound } = await Audio.Sound.createAsync(
        { uri: url },
        { 
          shouldPlay: true,
          isLooping: false,
          volume: 1.0,
        },
        handlePlaybackStatusUpdate
      );
      setSound(newSound);
      setIsPlaying(true);
    } catch (error) {
      console.error('Error playing radio:', error);
      setError('Failed to connect to radio stream');
      Alert.alert('Playback Error', 'Unable to connect to the radio stream. Please check your internet connection and try again.');
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

  const switchToLanguageStation = async (station: any) => {
    setSelectedStation(station);
    await stopRadio();
    await playRadio(station.stream);
    setShowLanguageModal(false);
    
    Alert.alert(
      `${languageData?.localized_content?.content?.greeting || 'Switched to'}`,
      `Now playing: ${station.name} (${station.frequency})`
    );
  };

  const onRefresh = async () => {
    setRefreshing(true);
    await loadMultilingualContent();
    setRefreshing(false);
  };

  const getGreeting = () => {
    if (languageData?.localized_content?.content?.greeting) {
      return languageData.localized_content.content.greeting;
    }
    return 'Welcome to Kagema FM';
  };

  const getLanguageFlag = (langCode: string) => {
    const flags = {
      'en': '🇬🇧',
      'sw': '🇹🇿', 
      'ki': '🇰🇪',
      'luo': '🇰🇪',
      'luy': '🇰🇪',
      'kam': '🇰🇪',
      'kal': '🇰🇪'
    };
    return flags[langCode] || '🇰🇪';
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

        {/* Language Detection Info */}
        {languageData && (
          <View style={styles.languageDetectionContainer}>
            <View style={styles.languageRow}>
              <Text style={styles.languageFlag}>{getLanguageFlag(languageData.detected_language)}</Text>
              <Text style={styles.languageText}>
                {languageData.language_info?.native_name || languageData.detected_language.toUpperCase()}
              </Text>
              <Text style={styles.locationText}>• {languageData.county}</Text>
            </View>
            <Text style={styles.confidenceText}>
              Confidence: {Math.round(languageData.confidence * 100)}%
            </Text>
            <TouchableOpacity 
              style={styles.switchLanguageButton}
              onPress={() => setShowLanguageModal(true)}
            >
              <Ionicons name="language" size={16} color="#ff6b6b" />
              <Text style={styles.switchLanguageText}>Switch Station Language</Text>
            </TouchableOpacity>
          </View>
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
        
        {selectedStation && (
          <Text style={styles.currentStationText}>
            Playing: {selectedStation.name} ({selectedStation.frequency})
          </Text>
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
          <Text style={styles.sectionTitle}>
            {languageData?.localized_content?.content?.music_intro || 'AI Music Recommendations'}
          </Text>
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

  const renderLanguageModal = () => (
    <Modal
      animationType="slide"
      transparent={true}
      visible={showLanguageModal}
      onRequestClose={() => setShowLanguageModal(false)}
    >
      <View style={styles.modalOverlay}>
        <View style={styles.modalContainer}>
          <View style={styles.modalHeader}>
            <Text style={styles.modalTitle}>Choose Radio Station Language</Text>
            <TouchableOpacity 
              style={styles.closeButton}
              onPress={() => setShowLanguageModal(false)}
            >
              <Ionicons name="close" size={24} color="#fff" />
            </TouchableOpacity>
          </View>
          
          {languageData && (
            <ScrollView style={styles.modalContent}>
              <Text style={styles.modalSubtitle}>
                Detected Location: {languageData.county}
              </Text>
              <Text style={styles.modalDescription}>
                Based on your location, here are available radio stations in local languages:
              </Text>
              
              {languageData.regional_stations.map((station, index) => (
                <TouchableOpacity
                  key={index}
                  style={styles.stationOption}
                  onPress={() => switchToLanguageStation(station)}
                >
                  <View style={styles.stationInfo}>
                    <Text style={styles.stationName}>{station.name}</Text>
                    <Text style={styles.stationFreq}>{station.frequency}</Text>
                  </View>
                  <Ionicons name="radio" size={24} color="#ff6b6b" />
                </TouchableOpacity>
              ))}
            </ScrollView>
          )}
        </View>
      </View>
    </Modal>
  );

  const renderNewsTab = () => (
    <ScrollView 
      style={styles.tabContent}
      refreshControl={<RefreshControl refreshing={refreshing} onRefresh={onRefresh} />}
    >
      <Text style={styles.tabTitle}>
        {languageData?.localized_content?.content?.news_intro || 'Local & International News'}
      </Text>
      
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
      <Text style={styles.tabTitle}>
        {languageData?.localized_content?.content?.music_intro || 'Trending Music'}
      </Text>
      
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

  const renderLanguageTab = () => (
    <ScrollView 
      style={styles.tabContent}
      refreshControl={<RefreshControl refreshing={refreshing} onRefresh={onRefresh} />}
    >
      <Text style={styles.tabTitle}>Language Detection</Text>
      
      {languageData && (
        <View style={styles.languageInfoContainer}>
          <View style={styles.detectedLanguageCard}>
            <Text style={styles.detectedLanguageTitle}>Detected Language</Text>
            <View style={styles.languageDisplayRow}>
              <Text style={styles.languageFlagLarge}>
                {getLanguageFlag(languageData.detected_language)}
              </Text>
              <View>
                <Text style={styles.languageNameLarge}>
                  {languageData.language_info?.native_name}
                </Text>
                <Text style={styles.languageNameEn}>
                  {languageData.language_info?.name}
                </Text>
              </View>
            </View>
            <Text style={styles.locationInfo}>
              📍 {languageData.county}, Kenya
            </Text>
            <Text style={styles.confidenceInfo}>
              Confidence: {Math.round(languageData.confidence * 100)}%
            </Text>
          </View>

          <View style={styles.alternativeLanguagesCard}>
            <Text style={styles.cardTitle}>Alternative Languages Available</Text>
            {languageData.alternative_languages.map((langCode, index) => (
              <View key={index} style={styles.altLanguageRow}>
                <Text style={styles.altLanguageFlag}>{getLanguageFlag(langCode)}</Text>
                <Text style={styles.altLanguageName}>
                  {LanguageService.getLanguageDisplayName(langCode)}
                </Text>
              </View>
            ))}
          </View>

          <View style={styles.regionalStationsCard}>
            <Text style={styles.cardTitle}>Regional Radio Stations</Text>
            {languageData.regional_stations.map((station, index) => (
              <TouchableOpacity
                key={index}
                style={styles.regionalStationItem}
                onPress={() => switchToLanguageStation(station)}
              >
                <View style={styles.stationDetails}>
                  <Text style={styles.regionalStationName}>{station.name}</Text>
                  <Text style={styles.regionalStationFreq}>{station.frequency}</Text>
                </View>
                <Ionicons 
                  name={selectedStation?.name === station.name ? 'radio' : 'play-circle-outline'} 
                  size={24} 
                  color="#ff6b6b" 
                />
              </TouchableOpacity>
            ))}
          </View>
        </View>
      )}

      {!languageData && (
        <View style={styles.noLanguageData}>
          <Ionicons name="language-outline" size={64} color="#666" />
          <Text style={styles.noLanguageText}>Enable location services to detect your local language</Text>
        </View>
      )}
    </ScrollView>
  );

  return (
    <SafeAreaView style={styles.container}>
      <StatusBar barStyle="light-content" backgroundColor="#1a1a2e" />
      
      {/* Header */}
      <View style={styles.header}>
        <Text style={styles.headerTitle}>Kagema FM</Text>
        <Text style={styles.headerSubtitle}>Multilingual Radio Experience</Text>
        {languageData && (
          <Text style={styles.languageIndicator}>
            {getLanguageFlag(languageData.detected_language)} {languageData.language_info?.native_name}
          </Text>
        )}
      </View>

      {/* Tab Navigation */}
      <View style={styles.tabNavigation}>
        <TouchableOpacity 
          style={[styles.tabButton, activeTab === 'radio' && styles.activeTabButton]}
          onPress={() => setActiveTab('radio')}
        >
          <Ionicons 
            name="radio" 
            size={20} 
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
            size={20} 
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
            size={20} 
            color={activeTab === 'music' ? '#fff' : '#ff6b6b'} 
          />
          <Text style={[styles.tabText, activeTab === 'music' && styles.activeTabText]}>
            Music
          </Text>
        </TouchableOpacity>

        <TouchableOpacity 
          style={[styles.tabButton, activeTab === 'language' && styles.activeTabButton]}
          onPress={() => setActiveTab('language')}
        >
          <Ionicons 
            name="language" 
            size={20} 
            color={activeTab === 'language' ? '#fff' : '#ff6b6b'} 
          />
          <Text style={[styles.tabText, activeTab === 'language' && styles.activeTabText]}>
            Language
          </Text>
        </TouchableOpacity>
      </View>

      {/* Tab Content */}
      {activeTab === 'radio' && renderRadioTab()}
      {activeTab === 'news' && renderNewsTab()}
      {activeTab === 'music' && renderMusicTab()}
      {activeTab === 'language' && renderLanguageTab()}

      {/* Language Selection Modal */}
      {renderLanguageModal()}
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
    paddingVertical: 15,
    borderBottomWidth: 1,
    borderBottomColor: '#2d2d54',
  },
  headerTitle: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#fff',
    marginBottom: 2,
  },
  headerSubtitle: {
    fontSize: 12,
    color: '#ff6b6b',
    textTransform: 'uppercase',
    letterSpacing: 1,
  },
  languageIndicator: {
    fontSize: 14,
    color: '#ccc',
    marginTop: 5,
  },
  tabNavigation: {
    flexDirection: 'row',
    backgroundColor: '#2d2d54',
    paddingVertical: 8,
  },
  tabButton: {
    flex: 1,
    alignItems: 'center',
    paddingVertical: 8,
  },
  activeTabButton: {
    backgroundColor: '#ff6b6b',
    marginHorizontal: 2,
    borderRadius: 8,
  },
  tabText: {
    color: '#ff6b6b',
    fontSize: 11,
    marginTop: 2,
  },
  activeTabText: {
    color: '#fff',
  },
  tabContent: {
    flex: 1,
  },
  tabTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#fff',
    textAlign: 'center',
    paddingVertical: 15,
  },
  stationContainer: {
    alignItems: 'center',
    paddingHorizontal: 20,
    paddingVertical: 15,
  },
  logoContainer: {
    marginBottom: 15,
  },
  logo: {
    width: 80,
    height: 80,
    borderRadius: 40,
    borderWidth: 2,
    borderColor: '#ff6b6b',
  },
  stationName: {
    fontSize: 20,
    fontWeight: 'bold',
    color: '#fff',
    textAlign: 'center',
    marginBottom: 8,
  },
  stationDescription: {
    fontSize: 14,
    color: '#ccc',
    textAlign: 'center',
    marginBottom: 10,
  },
  currentShow: {
    fontSize: 12,
    color: '#ff6b6b',
    textAlign: 'center',
    fontStyle: 'italic',
  },
  languageDetectionContainer: {
    marginTop: 15,
    alignItems: 'center',
    backgroundColor: '#2d2d54',
    padding: 12,
    borderRadius: 8,
    minWidth: '90%',
  },
  languageRow: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 5,
  },
  languageFlag: {
    fontSize: 20,
    marginRight: 8,
  },
  languageText: {
    color: '#fff',
    fontSize: 14,
    fontWeight: 'bold',
  },
  locationText: {
    color: '#ccc',
    fontSize: 12,
    marginLeft: 5,
  },
  confidenceText: {
    color: '#ccc',
    fontSize: 10,
    marginBottom: 8,
  },
  switchLanguageButton: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: 'rgba(255, 107, 107, 0.2)',
    paddingHorizontal: 12,
    paddingVertical: 6,
    borderRadius: 15,
  },
  switchLanguageText: {
    color: '#ff6b6b',
    fontSize: 12,
    marginLeft: 5,
  },
  locationContainer: {
    marginTop: 15,
    alignItems: 'center',
  },
  locationRow: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 10,
  },
  weatherContainer: {
    alignItems: 'center',
    backgroundColor: '#2d2d54',
    padding: 12,
    borderRadius: 8,
    minWidth: 140,
  },
  weatherTemp: {
    fontSize: 20,
    fontWeight: 'bold',
    color: '#ff6b6b',
  },
  weatherDesc: {
    fontSize: 12,
    color: '#fff',
    marginVertical: 3,
  },
  weatherFeels: {
    fontSize: 10,
    color: '#ccc',
  },
  playerContainer: {
    paddingHorizontal: 20,
    paddingVertical: 20,
  },
  errorText: {
    color: '#f44336',
    textAlign: 'center',
    marginBottom: 15,
    fontSize: 12,
  },
  controlsContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    marginBottom: 15,
  },
  controlButton: {
    width: 50,
    height: 50,
    borderRadius: 25,
    backgroundColor: '#2d2d54',
    alignItems: 'center',
    justifyContent: 'center',
    marginHorizontal: 12,
  },
  playButton: {
    width: 70,
    height: 70,
    borderRadius: 35,
    backgroundColor: '#ff6b6b',
    alignItems: 'center',
    justifyContent: 'center',
    marginHorizontal: 12,
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
    fontSize: 12,
    marginTop: 8,
  },
  currentStationText: {
    color: '#ff6b6b',
    textAlign: 'center',
    fontSize: 12,
    marginTop: 8,
  },
  statusContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    paddingBottom: 15,
  },
  statusDot: {
    width: 8,
    height: 8,
    borderRadius: 4,
    marginRight: 8,
  },
  statusText: {
    color: '#ccc',
    fontSize: 12,
    fontWeight: '500',
  },
  recommendationsContainer: {
    margin: 15,
    padding: 15,
    backgroundColor: '#2d2d54',
    borderRadius: 8,
  },
  sectionTitle: {
    fontSize: 16,
    fontWeight: 'bold',
    color: '#ff6b6b',
    marginBottom: 8,
  },
  recommendationText: {
    color: '#fff',
    fontSize: 12,
    lineHeight: 18,
    marginBottom: 8,
  },
  genreContainer: {
    flexDirection: 'row',
    flexWrap: 'wrap',
  },
  genreTag: {
    backgroundColor: '#ff6b6b',
    paddingHorizontal: 10,
    paddingVertical: 4,
    borderRadius: 12,
    marginRight: 6,
    marginBottom: 6,
  },
  genreText: {
    color: '#fff',
    fontSize: 10,
  },
  summaryContainer: {
    margin: 15,
    padding: 12,
    backgroundColor: '#2d2d54',
    borderRadius: 8,
  },
  summaryTitle: {
    fontSize: 14,
    fontWeight: 'bold',
    color: '#ff6b6b',
    marginBottom: 8,
  },
  summaryText: {
    color: '#fff',
    fontSize: 12,
    lineHeight: 18,
  },
  newsItem: {
    margin: 15,
    padding: 12,
    backgroundColor: '#2d2d54',
    borderRadius: 8,
    borderLeftWidth: 3,
    borderLeftColor: '#ff6b6b',
  },
  newsHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 6,
  },
  newsSource: {
    color: '#ff6b6b',
    fontSize: 10,
    fontWeight: 'bold',
  },
  categoryTag: {
    backgroundColor: '#ff6b6b',
    paddingHorizontal: 6,
    paddingVertical: 2,
    borderRadius: 8,
  },
  categoryText: {
    color: '#fff',
    fontSize: 8,
    textTransform: 'uppercase',
  },
  newsTitle: {
    color: '#fff',
    fontSize: 14,
    fontWeight: 'bold',
    marginBottom: 6,
  },
  newsDescription: {
    color: '#ccc',
    fontSize: 12,
    lineHeight: 16,
    marginBottom: 6,
  },
  newsTime: {
    color: '#999',
    fontSize: 10,
  },
  musicItem: {
    flexDirection: 'row',
    alignItems: 'center',
    margin: 15,
    padding: 12,
    backgroundColor: '#2d2d54',
    borderRadius: 8,
  },
  musicInfo: {
    flex: 1,
  },
  musicTitle: {
    color: '#fff',
    fontSize: 14,
    fontWeight: 'bold',
    marginBottom: 3,
  },
  musicArtist: {
    color: '#ff6b6b',
    fontSize: 12,
    marginBottom: 2,
  },
  musicAlbum: {
    color: '#ccc',
    fontSize: 10,
  },
  musicPopularity: {
    alignItems: 'center',
    minWidth: 50,
  },
  popularityBar: {
    width: 30,
    height: 3,
    backgroundColor: '#444',
    borderRadius: 1.5,
    overflow: 'hidden',
  },
  popularityFill: {
    height: '100%',
    backgroundColor: '#ff6b6b',
  },
  popularityText: {
    color: '#ccc',
    fontSize: 8,
    marginTop: 3,
  },
  languageInfoContainer: {
    padding: 15,
  },
  detectedLanguageCard: {
    backgroundColor: '#2d2d54',
    padding: 15,
    borderRadius: 8,
    marginBottom: 15,
    borderLeftWidth: 4,
    borderLeftColor: '#ff6b6b',
  },
  detectedLanguageTitle: {
    color: '#ff6b6b',
    fontSize: 16,
    fontWeight: 'bold',
    marginBottom: 10,
  },
  languageDisplayRow: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 10,
  },
  languageFlagLarge: {
    fontSize: 32,
    marginRight: 12,
  },
  languageNameLarge: {
    color: '#fff',
    fontSize: 18,
    fontWeight: 'bold',
  },
  languageNameEn: {
    color: '#ccc',
    fontSize: 14,
  },
  locationInfo: {
    color: '#ccc',
    fontSize: 14,
    marginBottom: 5,
  },
  confidenceInfo: {
    color: '#ff6b6b',
    fontSize: 12,
  },
  alternativeLanguagesCard: {
    backgroundColor: '#2d2d54',
    padding: 15,
    borderRadius: 8,
    marginBottom: 15,
  },
  cardTitle: {
    color: '#fff',
    fontSize: 16,
    fontWeight: 'bold',
    marginBottom: 10,
  },
  altLanguageRow: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 8,
  },
  altLanguageFlag: {
    fontSize: 20,
    marginRight: 10,
  },
  altLanguageName: {
    color: '#ccc',
    fontSize: 14,
  },
  regionalStationsCard: {
    backgroundColor: '#2d2d54',
    padding: 15,
    borderRadius: 8,
  },
  regionalStationItem: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    paddingVertical: 10,
    borderBottomWidth: 1,
    borderBottomColor: '#444',
  },
  stationDetails: {
    flex: 1,
  },
  regionalStationName: {
    color: '#fff',
    fontSize: 14,
    fontWeight: 'bold',
  },
  regionalStationFreq: {
    color: '#ccc',
    fontSize: 12,
  },
  noLanguageData: {
    flex: 1,
    alignItems: 'center',
    justifyContent: 'center',
    padding: 50,
  },
  noLanguageText: {
    color: '#666',
    textAlign: 'center',
    marginTop: 20,
    fontSize: 16,
  },
  modalOverlay: {
    flex: 1,
    backgroundColor: 'rgba(0, 0, 0, 0.5)',
    justifyContent: 'center',
    alignItems: 'center',
  },
  modalContainer: {
    backgroundColor: '#2d2d54',
    borderRadius: 15,
    width: '90%',
    maxHeight: '80%',
  },
  modalHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    padding: 20,
    borderBottomWidth: 1,
    borderBottomColor: '#444',
  },
  modalTitle: {
    color: '#fff',
    fontSize: 18,
    fontWeight: 'bold',
  },
  closeButton: {
    padding: 5,
  },
  modalContent: {
    padding: 20,
  },
  modalSubtitle: {
    color: '#ff6b6b',
    fontSize: 16,
    fontWeight: 'bold',
    marginBottom: 10,
  },
  modalDescription: {
    color: '#ccc',
    fontSize: 14,
    marginBottom: 20,
  },
  stationOption: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    backgroundColor: '#1a1a2e',
    padding: 15,
    borderRadius: 8,
    marginBottom: 10,
  },
  stationInfo: {
    flex: 1,
  },
  stationName: {
    color: '#fff',
    fontSize: 16,
    fontWeight: 'bold',
  },
  stationFreq: {
    color: '#ccc',
    fontSize: 14,
  },
});