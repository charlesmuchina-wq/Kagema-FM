import React, { useState, useEffect, useRef } from 'react';
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
  Platform
} from 'react-native';

// Theme Provider - First import
import { ThemeProvider, useTheme } from '../contexts/ThemeContext';

// Audio imports - platform-specific with web fallback
let Audio;
try {
  Audio = require('expo-audio').Audio;
} catch (error) {
  // Web platform fallback - use HTML5 Audio API
  Audio = {
    Sound: class {
      constructor() {
        this.audio = new (window as any).Audio();
        this.isLoaded = false;
        this.status = { isPlaying: false, positionMillis: 0, durationMillis: 0 };
      }
      
      async loadAsync(source: any) {
        if (typeof source === 'string') {
          this.audio.src = source;
        } else if (source.uri) {
          this.audio.src = source.uri;
        }
        return new Promise((resolve) => {
          this.audio.addEventListener('canplay', () => {
            this.isLoaded = true;
            resolve({ status: this.status });
          });
        });
      }
      
      async playAsync() {
        if (this.isLoaded) {
          await this.audio.play();
          this.status.isPlaying = true;
        }
        return { status: this.status };
      }
      
      async pauseAsync() {
        if (this.isLoaded) {
          this.audio.pause();
          this.status.isPlaying = false;
        }
        return { status: this.status };
      }
      
      async stopAsync() {
        if (this.isLoaded) {
          this.audio.pause();
          this.audio.currentTime = 0;
          this.status.isPlaying = false;
        }
        return { status: this.status };
      }
      
      async unloadAsync() {
        if (this.isLoaded) {
          this.audio.pause();
          this.audio.src = '';
          this.isLoaded = false;
          this.status.isPlaying = false;
        }
      }
      
      setOnPlaybackStatusUpdate(callback: (status: any) => void) {
        if (callback) {
          this.audio.addEventListener('play', () => {
            this.status.isPlaying = true;
            callback(this.status);
          });
          this.audio.addEventListener('pause', () => {
            this.status.isPlaying = false;
            callback(this.status);
          });
          this.audio.addEventListener('ended', () => {
            this.status.isPlaying = false;
            callback(this.status);
          });
        }
      }
    },
    setAudioModeAsync: null // Not needed for web
  };
}

import { Ionicons } from '@expo/vector-icons';
import { useLocation } from '../services/LocationService';
import ContentService from '../services/ContentService';
import LanguageService from '../services/LanguageService';
import ContentDisclaimerService from '../services/ContentDisclaimerService';
import IntegrationProvider, { useIntegrations } from '../services/PlatformIntegrationService';
import { notificationService } from '../services/NotificationService';
import ContentDisclaimerModal from '../components/ContentDisclaimerModal';

// Enhanced Components
import { EnhancedAudioPlayer } from '../components/EnhancedAudioPlayer';
import { FavoritesManager, addItemToFavorites } from '../components/FavoritesManager';
import { SocialSharingManager } from '../components/SocialSharingManager';
import { AudioRecorder } from '../components/AudioRecorder';

const { width } = Dimensions.get('window');

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

const EnhancedKagemaFMApp = () => {
  const { colors, isDark, toggleTheme } = useTheme();
  const [sound, setSound] = useState<any>(null);
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
  const [regionalStations, setRegionalStations] = useState<any[]>([]);
  const [activeTab, setActiveTab] = useState<'radio' | 'news' | 'music' | 'language' | 'integrations' | 'settings'>('radio');
  
  // Enhanced UI state
  const [showFavorites, setShowFavorites] = useState(false);
  const [showSharing, setShowSharing] = useState(false);
  const [showRecorder, setShowRecorder] = useState(false);
  const [shareData, setShareData] = useState<any>(null);
  const [currentlyPlaying, setCurrentlyPlaying] = useState<string | null>(null);
  const [useEnhancedPlayer, setUseEnhancedPlayer] = useState(true);
  
  // Language detection state
  const [languageData, setLanguageData] = useState({
    detected_language: 'en',
    county: 'Unknown',
    region: 'Unknown',
    confidence: 1.0,
    alternative_languages: [],
    radio_streams: [],
    language_info: { code: 'en', name: 'English', native_name: 'English' },
    regional_stations: []
  });
  const [showLanguageModal, setShowLanguageModal] = useState(false);
  const [supportedLanguages, setSupportedLanguages] = useState<any[]>([]);
  const [selectedStation, setSelectedStation] = useState<any>(null);
  
  // Regional selection state
  const [selectedKenyaRegion, setSelectedKenyaRegion] = useState('Nairobi');
  const [selectedBrazilRegion, setSelectedBrazilRegion] = useState('Bahia');
  const [showKenyaDropdown, setShowKenyaDropdown] = useState(false);
  const [showBrazilDropdown, setShowBrazilDropdown] = useState(false);
  const [currentAPIVersion, setCurrentAPIVersion] = useState('5.0.0');
  
  // Kenya regions/counties
  const kenyaRegions = [
    'Nairobi', 'Mombasa', 'Kisumu', 'Nakuru', 'Eldoret', 'Nyeri', 'Machakos', 
    'Meru', 'Thika', 'Malindi', 'Kitale', 'Garissa', 'Kakamega', 'Embu',
    'Kericho', 'Bungoma', 'Muranga', 'Kiambu', 'Kajiado', 'Turkana'
  ];
  
  // Brazil states
  const brazilRegions = [
    'São Paulo', 'Rio de Janeiro', 'Minas Gerais', 'Bahia', 'Paraná', 'Rio Grande do Sul',
    'Pernambuco', 'Ceará', 'Pará', 'Santa Catarina', 'Goiás', 'Maranhão',
    'Espírito Santo', 'Paraíba', 'Amazonas', 'Mato Grosso', 'Rio Grande do Norte',
    'Alagoas', 'Piauí', 'Distrito Federal', 'Mato Grosso do Sul', 'Sergipe',
    'Rondônia', 'Acre', 'Amapá', 'Roraima', 'Tocantins'
  ];
  
  // Integration state variables
  const [isVoiceListening, setIsVoiceListening] = useState(false);
  const [nearbyPlaces, setNearbyPlaces] = useState<any[]>([]);
  const [spotifyTracks, setSpotifyTracks] = useState<any[]>([]);
  const [trafficConditions, setTrafficConditions] = useState<any>(null);
  
  // Disclaimer visibility state
  const [showDisclaimers, setShowDisclaimers] = useState(false);
  
  // Connectivity and offline state
  const [connectionType, setConnectionType] = useState<'wifi' | 'cellular' | 'satellite' | 'offline'>('wifi');
  const [dataUsage, setDataUsage] = useState({ used: 0, limit: 1000 }); // MB
  const [satelliteConnected, setSatelliteConnected] = useState(false);
  const [offlineMode, setOfflineMode] = useState(false);
  const [offlineContent, setOfflineContent] = useState<any>(null);
  const [mapDownloaded, setMapDownloaded] = useState(false);
  const [lowDataMode, setLowDataMode] = useState(false);
  
  // User ID for backend integration
  const [userId] = useState(() => `user_${Date.now()}`);

  const { location, locationInfo, errorMsg: locationError, loading: locationLoading } = useLocation();

  const {
    activeIntegrations,
    isInitialized,
    emergencyAlerts,
    startVoiceRecognition,
    stopVoiceRecognition,
    searchSpotify,
    createSpotifyPlaylist,
    getNearbyPlaces,
    getTrafficConditions,
    updateMediaMetadata,
    handlePlay,
    handlePause,
    handleStop
  } = useIntegrations();

  // Initialize enhanced features
  useEffect(() => {
    initializeEnhancedFeatures();
  }, []);

  const initializeEnhancedFeatures = async () => {
    console.log('🚀 Initializing enhanced Kagema FM features...');
    
    try {
      // Initialize notification service
      await notificationService.initialize();
      
      // Setup notification response handler
      notificationService.setupNotificationResponseHandler();
      
      // Load user data and sync with backend
      await loadUserPreferences();
      
      console.log('✅ Enhanced features initialized successfully');
    } catch (error) {
      console.error('❌ Error initializing enhanced features:', error);
    }
  };

  const loadUserPreferences = async () => {
    try {
      const EXPO_PUBLIC_BACKEND_URL = process.env.EXPO_BACKEND_URL || '';
      
      // Get user preferences from backend
      const response = await fetch(`${EXPO_PUBLIC_BACKEND_URL}/api/user/${userId}/preferences`);
      
      if (response.ok) {
        const preferences = await response.json();
        console.log('📋 Loaded user preferences:', preferences);
        
        // Apply theme preference
        if (preferences.theme !== 'auto') {
          // Theme context will handle this
        }
      } else {
        console.log('ℹ️ No existing preferences found, using defaults');
      }
    } catch (error) {
      console.log('ℹ️ Could not load user preferences:', error);
    }
  };

  const saveUserPreferences = async (updates: any) => {
    try {
      const EXPO_PUBLIC_BACKEND_URL = process.env.EXPO_BACKEND_URL || '';
      
      const response = await fetch(`${EXPO_PUBLIC_BACKEND_URL}/api/user/${userId}/preferences`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          ...updates,
          theme: isDark ? 'dark' : 'light',
        }),
      });

      if (response.ok) {
        console.log('💾 Saved user preferences');
      }
    } catch (error) {
      console.log('⚠️ Could not save user preferences:', error);
    }
  };

  // Enhanced audio player handlers
  const handleEnhancedPlayStateChange = (playing: boolean) => {
    setIsPlaying(playing);
    if (stationInfo) {
      setCurrentlyPlaying(playing ? stationInfo.name : null);
      
      // Track listening session
      trackListeningSession(playing);
      
      // Update media metadata
      if (playing) {
        updateMediaMetadata(
          stationInfo.name,
          stationInfo.currentShow || 'Live Radio',
          require('../assets/kagema_fm_international_logo.jpg')
        );
      }
    }
  };

  const trackListeningSession = async (isStarting: boolean) => {
    if (!stationInfo) return;
    
    try {
      const EXPO_PUBLIC_BACKEND_URL = process.env.EXPO_BACKEND_URL || '';
      
      if (isStarting) {
        // Start new session
        const response = await fetch(`${EXPO_PUBLIC_BACKEND_URL}/api/user/${userId}/listening-session`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            station_name: stationInfo.name,
            stream_url: stationInfo.streamUrl,
            started_at: new Date().toISOString(),
          }),
        });
        
        if (response.ok) {
          const session = await response.json();
          console.log('📊 Started listening session:', session.id);
        }
      }
    } catch (error) {
      console.log('ℹ️ Could not track listening session:', error);
    }
  };

  const handleEnhancedPlayerError = (errorMessage: string) => {
    setError(errorMessage);
    Alert.alert('Playback Error', errorMessage);
  };

  // Favorites functionality
  const addCurrentToFavorites = async () => {
    if (!stationInfo) return;
    
    const result = await addItemToFavorites({
      type: 'radio_station',
      title: stationInfo.name,
      description: stationInfo.description,
      streamUrl: stationInfo.streamUrl,
      tags: [languageData.detected_language, 'radio'],
    });
    
    if (result.success) {
      Alert.alert('Added to Favorites!', result.message);
      
      // Also save to backend
      try {
        const EXPO_PUBLIC_BACKEND_URL = process.env.EXPO_BACKEND_URL || '';
        
        await fetch(`${EXPO_PUBLIC_BACKEND_URL}/api/user/${userId}/favorites`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            type: 'radio_station',
            title: stationInfo.name,
            description: stationInfo.description,
            stream_url: stationInfo.streamUrl,
            metadata: {
              language: languageData.detected_language,
              frequency: stationInfo.currentShow,
            },
            tags: [languageData.detected_language, 'radio'],
          }),
        });
        
        console.log('💾 Saved favorite to backend');
      } catch (error) {
        console.log('ℹ️ Could not sync favorite to backend:', error);
      }
    } else {
      Alert.alert('Already in Favorites', result.message);
    }
  };

  const handleFavoritePlay = async (item: any) => {
    if (item.streamUrl) {
      // Update station info
      setStationInfo({
        name: item.title,
        description: item.description || 'Favorite station',
        streamUrl: item.streamUrl,
        currentShow: 'Live Radio',
      });
      
      // Close favorites modal
      setShowFavorites(false);
      
      // Start playing
      if (useEnhancedPlayer) {
        // The enhanced player will handle playback
        handleEnhancedPlayStateChange(true);
      } else {
        // Legacy player
        await playRadio(item.streamUrl);
      }
      
      Alert.alert('Playing Favorite', `Now playing: ${item.title}`);
    }
  };

  // Social sharing functionality
  const shareCurrentStation = () => {
    if (!stationInfo) return;
    
    setShareData({
      type: 'radio_station',
      title: stationInfo.name,
      description: stationInfo.description,
      url: `https://kagema.fm/station/${encodeURIComponent(stationInfo.name)}`,
      metadata: {
        currentShow: stationInfo.currentShow,
        language: languageData.detected_language,
      },
    });
    
    setShowSharing(true);
  };

  const shareNewsArticle = (article: NewsArticle) => {
    setShareData({
      type: 'news_article',
      title: article.title,
      description: article.description,
      metadata: {
        source: article.source,
        publishedAt: article.published_at,
      },
    });
    
    setShowSharing(true);
  };

  const shareMusicTrack = (track: MusicTrack) => {
    setShareData({
      type: 'music_track',
      title: track.name,
      description: `by ${track.artists.join(', ')} from ${track.album}`,
      metadata: {
        artists: track.artists,
        album: track.album,
        popularity: track.popularity,
      },
    });
    
    setShowSharing(true);
  };

  // Audio recording functionality
  const handleRecordingComplete = (recording: any) => {
    console.log('🎙️ Recording completed:', recording);
    
    Alert.alert(
      'Recording Complete',
      `"${recording.title}" has been saved. Would you like to share it?`,
      [
        { text: 'Later', style: 'cancel' },
        {
          text: 'Share',
          onPress: () => {
            setShareData({
              type: 'audio_recording',
              title: recording.title,
              description: `Audio recording from Kagema FM - Duration: ${Math.floor(recording.duration / 60)}:${(recording.duration % 60).toString().padStart(2, '0')}`,
              metadata: {
                duration: recording.duration,
                quality: recording.quality,
                dateCreated: recording.dateCreated,
              },
            });
            setShowSharing(true);
          },
        },
      ]
    );
  };

  // Legacy functions for backward compatibility
  const setupAudio = async () => {
    try {
      if (typeof Audio !== 'undefined' && Audio && Audio.setAudioModeAsync) {
        await Audio.setAudioModeAsync({
          staysActiveInBackground: true,
          shouldDuckAndroid: false,
          playThroughEarpieceAndroid: false,
          allowsRecordingIOS: false,
          playsInSilentModeIOS: true,
        });
        console.log('Audio setup: Configured for native platform');
      } else {
        console.log('Audio setup: Using HTML5 Audio for web platform');
      }
    } catch (error) {
      console.log('Audio setup: Using default audio configuration:', error.message);
    }
  };

  const loadMultilingualContent = async () => {
    console.log('📻 Loading radio content (enhanced version)');
    
    try {
      setIsLoading(true);
      const EXPO_PUBLIC_BACKEND_URL = process.env.EXPO_BACKEND_URL || '';

      const response = await fetch(`${EXPO_PUBLIC_BACKEND_URL}/api/personalized-content/multilingual`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          location: { latitude: -1.286389, longitude: 36.817223 },
          preferences: {
            interests: ['radio', 'music', 'news'],
            favorite_genres: ['general'],
            location: 'Nairobi',
            age_group: 'adult',
            preferred_language: 'auto'
          }
        }),
      });

      if (response.ok) {
        const data = await response.json();
        console.log('✅ Personalized content loaded:', data);

        if (data.radio_streams?.main_station) {
          setStationInfo({
            name: data.radio_streams.main_station.name || 'Kagema FM',
            description: data.radio_streams.main_station.description || 'Your international radio station',
            streamUrl: data.radio_streams.main_station.streamUrl || 'https://ice1.somafm.com/groovesalad-256-mp3',
            currentShow: 'Live Radio',
            frequency: data.radio_streams.main_station.frequency || '101.5 FM'
          });
        }
        if (data.weather) setWeatherData(data.weather);
        if (data.news?.articles) {
          setNewsArticles(data.news.articles);
          setNewsSummary(`${data.news.articles.length} news articles available`);
        }
        if (data.music?.tracks) {
          setMusicTracks(data.music.tracks);
          setMusicRecommendations(`${data.music.tracks.length} trending tracks`);
        }
      } else {
        // Fallback
        setStationInfo({
          name: 'Kagema FM Enhanced',
          description: 'Your Enhanced International Radio Experience',
          streamUrl: 'https://ice1.somafm.com/groovesalad-256-mp3',
          currentShow: 'Live Enhanced Radio',
          frequency: '101.5 FM'
        });
      }

      console.log('✅ Enhanced content loading completed');
      
    } catch (error) {
      console.error('❌ Enhanced content loading error:', error);
      setStationInfo({
        name: 'Kagema FM Enhanced',
        description: 'International Radio Station',
        streamUrl: 'https://ice1.somafm.com/groovesalad-256-mp3',
        currentShow: 'Live Radio',
        frequency: '101.5 FM'
      });
    } finally {
      setIsLoading(false);
    }
  };

  const playRadio = async (streamUrl?: string) => {
    const url = streamUrl || stationInfo?.streamUrl;
    if (!url) return;

    try {
      setIsLoading(true);
      setError(null);

      if (sound) {
        await sound.unloadAsync();
        setSound(null);
      }

      const newSound = new Audio.Sound();
      
      newSound.setOnPlaybackStatusUpdate((status: any) => {
        if (status.isLoaded) {
          setIsBuffering(status.isBuffering || false);
          if (status.isPlaying !== isPlaying) {
            setIsPlaying(status.isPlaying);
            
            if (status.isPlaying && stationInfo) {
              updateMediaMetadata(
                stationInfo.name,
                stationInfo.currentShow || 'Live Radio',
                require('../assets/kagema_fm_international_logo.jpg')
              );
            }
          }
        } else if (status.error) {
          console.error('Playback error:', status.error);
          setError('Failed to play audio stream');
          setIsPlaying(false);
        }
      });
      
      await newSound.loadAsync({ uri: url });
      await newSound.playAsync();
      
      setSound(newSound);
      setIsPlaying(true);
      await handlePlay();
      
      console.log('Radio stream started:', url);
    } catch (error) {
      console.error('Error playing radio:', error);
      setError('Failed to connect to radio stream');
    } finally {
      setIsLoading(false);
    }
  };

  const onRefresh = async () => {
    setRefreshing(true);
    await loadMultilingualContent();
    setRefreshing(false);
  };

  // Initialize on mount
  useEffect(() => {
    setupAudio();
    loadMultilingualContent();
  }, []);

  // Enhanced styles with theme support
  const styles = StyleSheet.create({
    container: {
      flex: 1,
      backgroundColor: colors.background,
    },
    header: {
      backgroundColor: colors.surface,
      paddingTop: 20,
      paddingBottom: 15,
      paddingHorizontal: 20,
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
    themeToggle: {
      position: 'absolute',
      top: 20,
      right: 20,
      padding: 8,
      borderRadius: 8,
      backgroundColor: colors.surface,
    },
    tabBar: {
      flexDirection: 'row',
      backgroundColor: colors.surface,
      paddingVertical: 8,
      paddingHorizontal: 4,
      borderBottomWidth: 1,
      borderBottomColor: colors.border,
    },
    tab: {
      flex: 1,
      alignItems: 'center',
      paddingVertical: 8,
      paddingHorizontal: 4,
      borderRadius: 8,
      marginHorizontal: 2,
    },
    activeTab: {
      backgroundColor: colors.primary,
    },
    tabText: {
      fontSize: 11,
      color: colors.textSecondary,
      marginTop: 2,
    },
    activeTabText: {
      color: colors.background,
      fontWeight: '600',
    },
    content: {
      flex: 1,
    },
    tabContent: {
      flex: 1,
      backgroundColor: colors.background,
    },
    enhancedPlayerContainer: {
      margin: 16,
    },
    legacyPlayerContainer: {
      backgroundColor: colors.card,
      borderRadius: 16,
      padding: 20,
      margin: 16,
    },
    stationName: {
      fontSize: 20,
      fontWeight: '600',
      color: colors.text,
      textAlign: 'center',
      marginBottom: 8,
    },
    stationDescription: {
      fontSize: 14,
      color: colors.textSecondary,
      textAlign: 'center',
      marginBottom: 16,
    },
    playerControls: {
      flexDirection: 'row',
      alignItems: 'center',
      justifyContent: 'space-around',
      marginVertical: 20,
    },
    playButton: {
      width: 70,
      height: 70,
      borderRadius: 35,
      backgroundColor: colors.primary,
      alignItems: 'center',
      justifyContent: 'center',
    },
    controlButton: {
      width: 50,
      height: 50,
      borderRadius: 25,
      backgroundColor: colors.surface,
      alignItems: 'center',
      justifyContent: 'center',
    },
    enhancedControls: {
      flexDirection: 'row',
      justifyContent: 'space-around',
      marginTop: 20,
      paddingTop: 20,
      borderTopWidth: 1,
      borderTopColor: colors.border,
    },
    enhancedButton: {
      alignItems: 'center',
      padding: 12,
      borderRadius: 12,
      backgroundColor: colors.surface,
    },
    enhancedButtonText: {
      fontSize: 12,
      color: colors.text,
      marginTop: 4,
    },
    playerToggle: {
      flexDirection: 'row',
      alignItems: 'center',
      justifyContent: 'center',
      margin: 16,
      padding: 12,
      backgroundColor: colors.surface,
      borderRadius: 12,
    },
    playerToggleText: {
      fontSize: 14,
      color: colors.text,
      marginLeft: 8,
    },
    newsCard: {
      backgroundColor: colors.card,
      borderRadius: 12,
      padding: 16,
      marginHorizontal: 16,
      marginVertical: 6,
      borderWidth: 1,
      borderColor: colors.border,
    },
    newsTitle: {
      fontSize: 16,
      fontWeight: '600',
      color: colors.text,
      marginBottom: 8,
    },
    newsDescription: {
      fontSize: 14,
      color: colors.textSecondary,
      lineHeight: 20,
      marginBottom: 12,
    },
    newsFooter: {
      flexDirection: 'row',
      justifyContent: 'space-between',
      alignItems: 'center',
    },
    newsSource: {
      fontSize: 12,
      color: colors.primary,
    },
    newsTime: {
      fontSize: 12,
      color: colors.textSecondary,
    },
    shareButton: {
      padding: 8,
    },
    musicCard: {
      backgroundColor: colors.card,
      borderRadius: 12,
      padding: 16,
      marginHorizontal: 16,
      marginVertical: 6,
      borderWidth: 1,
      borderColor: colors.border,
    },
    musicHeader: {
      flexDirection: 'row',
      alignItems: 'center',
      justifyContent: 'space-between',
    },
    musicInfo: {
      flex: 1,
    },
    musicTitle: {
      fontSize: 16,
      fontWeight: '600',
      color: colors.text,
      marginBottom: 4,
    },
    musicArtist: {
      fontSize: 14,
      color: colors.textSecondary,
      marginBottom: 2,
    },
    musicAlbum: {
      fontSize: 12,
      color: colors.textSecondary,
    },
    settingsContainer: {
      padding: 20,
    },
    settingsItem: {
      backgroundColor: colors.card,
      borderRadius: 12,
      padding: 16,
      marginBottom: 12,
      borderWidth: 1,
      borderColor: colors.border,
    },
    settingsTitle: {
      fontSize: 16,
      fontWeight: '600',
      color: colors.text,
      marginBottom: 8,
    },
    settingsDescription: {
      fontSize: 14,
      color: colors.textSecondary,
      marginBottom: 12,
    },
    settingsRow: {
      flexDirection: 'row',
      alignItems: 'center',
      justifyContent: 'space-between',
    },
    settingsLabel: {
      fontSize: 14,
      color: colors.text,
    },
  });

  const renderEnhancedRadioTab = () => (
    <ScrollView 
      style={styles.tabContent}
      refreshControl={<RefreshControl refreshing={refreshing} onRefresh={onRefresh} />}
    >
      {/* Player Toggle */}
      <TouchableOpacity 
        style={styles.playerToggle}
        onPress={() => setUseEnhancedPlayer(!useEnhancedPlayer)}
      >
        <Ionicons 
          name={useEnhancedPlayer ? 'options' : 'play-circle'} 
          size={20} 
          color={colors.primary} 
        />
        <Text style={styles.playerToggleText}>
          {useEnhancedPlayer ? 'Enhanced Player' : 'Classic Player'}
        </Text>
      </TouchableOpacity>

      {/* Enhanced or Legacy Player */}
      {useEnhancedPlayer && stationInfo ? (
        <View style={styles.enhancedPlayerContainer}>
          <EnhancedAudioPlayer
            streamUrl={stationInfo.streamUrl}
            title={stationInfo.name}
            subtitle={stationInfo.description || 'Live Radio'}
            onPlayStateChange={handleEnhancedPlayStateChange}
            onError={handleEnhancedPlayerError}
          />
        </View>
      ) : (
        <View style={styles.legacyPlayerContainer}>
          <Text style={styles.stationName}>{stationInfo?.name || 'Kagema FM'}</Text>
          <Text style={styles.stationDescription}>
            {stationInfo?.description || 'Your international radio station'}
          </Text>
          
          <View style={styles.playerControls}>
            <TouchableOpacity style={styles.controlButton} onPress={() => playRadio()}>
              <Ionicons name="stop" size={24} color={colors.text} />
            </TouchableOpacity>
            
            <TouchableOpacity 
              style={styles.playButton} 
              onPress={() => playRadio()}
              disabled={isLoading}
            >
              {isLoading || isBuffering ? (
                <ActivityIndicator size="large" color="#fff" />
              ) : (
                <Ionicons 
                  name={isPlaying ? 'pause' : 'play'} 
                  size={32} 
                  color="#fff" 
                />
              )}
            </TouchableOpacity>
            
            <TouchableOpacity style={styles.controlButton} onPress={onRefresh}>
              <Ionicons name="refresh" size={24} color={colors.text} />
            </TouchableOpacity>
          </View>
        </View>
      )}

      {/* Enhanced Controls */}
      <View style={styles.enhancedControls}>
        <TouchableOpacity 
          style={styles.enhancedButton}
          onPress={addCurrentToFavorites}
        >
          <Ionicons name="heart-outline" size={24} color={colors.primary} />
          <Text style={styles.enhancedButtonText}>Favorite</Text>
        </TouchableOpacity>
        
        <TouchableOpacity 
          style={styles.enhancedButton}
          onPress={() => setShowFavorites(true)}
        >
          <Ionicons name="list" size={24} color={colors.primary} />
          <Text style={styles.enhancedButtonText}>My Favorites</Text>
        </TouchableOpacity>
        
        <TouchableOpacity 
          style={styles.enhancedButton}
          onPress={shareCurrentStation}
        >
          <Ionicons name="share-outline" size={24} color={colors.primary} />
          <Text style={styles.enhancedButtonText}>Share</Text>
        </TouchableOpacity>
        
        <TouchableOpacity 
          style={styles.enhancedButton}
          onPress={() => setShowRecorder(true)}
        >
          <Ionicons name="mic-outline" size={24} color={colors.primary} />
          <Text style={styles.enhancedButtonText}>Record</Text>
        </TouchableOpacity>
      </View>

      {error && (
        <View style={{ margin: 16, padding: 12, backgroundColor: colors.error, borderRadius: 8 }}>
          <Text style={{ color: colors.background }}>{error}</Text>
        </View>
      )}
    </ScrollView>
  );

  const renderEnhancedNewsTab = () => (
    <ScrollView 
      style={styles.tabContent}
      refreshControl={<RefreshControl refreshing={refreshing} onRefresh={onRefresh} />}
    >
      {newsArticles.map((article, index) => (
        <View key={index} style={styles.newsCard}>
          <Text style={styles.newsTitle}>{article.title}</Text>
          <Text style={styles.newsDescription}>{article.description}</Text>
          <View style={styles.newsFooter}>
            <Text style={styles.newsSource}>{article.source}</Text>
            <TouchableOpacity 
              style={styles.shareButton}
              onPress={() => shareNewsArticle(article)}
            >
              <Ionicons name="share-outline" size={18} color={colors.primary} />
            </TouchableOpacity>
          </View>
        </View>
      ))}
    </ScrollView>
  );

  const renderEnhancedMusicTab = () => (
    <ScrollView 
      style={styles.tabContent}
      refreshControl={<RefreshControl refreshing={refreshing} onRefresh={onRefresh} />}
    >
      {musicTracks.map((track, index) => (
        <View key={index} style={styles.musicCard}>
          <View style={styles.musicHeader}>
            <View style={styles.musicInfo}>
              <Text style={styles.musicTitle}>{track.name}</Text>
              <Text style={styles.musicArtist}>{track.artists.join(', ')}</Text>
              <Text style={styles.musicAlbum}>{track.album}</Text>
            </View>
            <TouchableOpacity 
              style={styles.shareButton}
              onPress={() => shareMusicTrack(track)}
            >
              <Ionicons name="share-outline" size={18} color={colors.primary} />
            </TouchableOpacity>
          </View>
        </View>
      ))}
    </ScrollView>
  );

  const renderSettingsTab = () => (
    <ScrollView style={styles.tabContent}>
      <View style={styles.settingsContainer}>
        <View style={styles.settingsItem}>
          <Text style={styles.settingsTitle}>Appearance</Text>
          <Text style={styles.settingsDescription}>
            Customize your app's look and feel
          </Text>
          <View style={styles.settingsRow}>
            <Text style={styles.settingsLabel}>
              Theme: {isDark ? 'Dark' : 'Light'}
            </Text>
            <TouchableOpacity 
              style={[styles.controlButton, { width: 40, height: 40 }]}
              onPress={toggleTheme}
            >
              <Ionicons 
                name={isDark ? 'sunny' : 'moon'} 
                size={20} 
                color={colors.text} 
              />
            </TouchableOpacity>
          </View>
        </View>

        <View style={styles.settingsItem}>
          <Text style={styles.settingsTitle}>Enhanced Player</Text>
          <Text style={styles.settingsDescription}>
            Use the advanced audio player with more controls and features
          </Text>
          <View style={styles.settingsRow}>
            <Text style={styles.settingsLabel}>
              Enhanced Player: {useEnhancedPlayer ? 'On' : 'Off'}
            </Text>
            <TouchableOpacity 
              style={[
                styles.controlButton, 
                { width: 40, height: 40 },
                useEnhancedPlayer && { backgroundColor: colors.primary }
              ]}
              onPress={() => setUseEnhancedPlayer(!useEnhancedPlayer)}
            >
              <Ionicons 
                name={useEnhancedPlayer ? 'checkmark' : 'close'} 
                size={20} 
                color={useEnhancedPlayer ? colors.background : colors.text} 
              />
            </TouchableOpacity>
          </View>
        </View>

        <View style={styles.settingsItem}>
          <Text style={styles.settingsTitle}>Features</Text>
          <Text style={styles.settingsDescription}>
            Access to enhanced Kagema FM features
          </Text>
          <View style={[styles.settingsRow, { marginBottom: 8 }]}>
            <Text style={styles.settingsLabel}>🎵 Enhanced Audio Player</Text>
          </View>
          <View style={[styles.settingsRow, { marginBottom: 8 }]}>
            <Text style={styles.settingsLabel}>❤️ Favorites Manager</Text>
          </View>
          <View style={[styles.settingsRow, { marginBottom: 8 }]}>
            <Text style={styles.settingsLabel}>📤 Social Sharing</Text>
          </View>
          <View style={[styles.settingsRow, { marginBottom: 8 }]}>
            <Text style={styles.settingsLabel}>🎙️ Audio Recording</Text>
          </View>
          <View style={[styles.settingsRow, { marginBottom: 8 }]}>
            <Text style={styles.settingsLabel}>🔔 Smart Notifications</Text>
          </View>
          <View style={styles.settingsRow}>
            <Text style={styles.settingsLabel}>🌙 Dark/Light Theme</Text>
          </View>
        </View>
      </View>
    </ScrollView>
  );

  const tabs = [
    { id: 'radio', label: 'Radio', icon: 'radio', render: renderEnhancedRadioTab },
    { id: 'news', label: 'News', icon: 'newspaper', render: renderEnhancedNewsTab },
    { id: 'music', label: 'Music', icon: 'musical-notes', render: renderEnhancedMusicTab },
    { id: 'language', label: 'Language', icon: 'language', render: () => <View style={styles.tabContent}><Text style={{color: colors.text, textAlign: 'center', marginTop: 40}}>Language settings coming soon!</Text></View> },
    { id: 'integrations', label: 'Apps', icon: 'apps', render: () => <View style={styles.tabContent}><Text style={{color: colors.text, textAlign: 'center', marginTop: 40}}>Platform integrations coming soon!</Text></View> },
    { id: 'settings', label: 'Settings', icon: 'settings', render: renderSettingsTab },
  ];

  return (
    <SafeAreaView style={styles.container}>
      <StatusBar barStyle={isDark ? 'light-content' : 'dark-content'} />
      
      {/* Header */}
      <View style={styles.header}>
        <TouchableOpacity style={styles.themeToggle} onPress={toggleTheme}>
          <Ionicons 
            name={isDark ? 'sunny' : 'moon'} 
            size={20} 
            color={colors.primary} 
          />
        </TouchableOpacity>
        
        <Text style={styles.headerTitle}>Kagema FM Enhanced</Text>
        <Text style={styles.headerSubtitle}>Your Complete Radio Experience</Text>
      </View>

      {/* Tab Bar */}
      <View style={styles.tabBar}>
        {tabs.map((tab) => (
          <TouchableOpacity
            key={tab.id}
            style={[styles.tab, activeTab === tab.id && styles.activeTab]}
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
                activeTab === tab.id && styles.activeTabText,
              ]}
            >
              {tab.label}
            </Text>
          </TouchableOpacity>
        ))}
      </View>

      {/* Content */}
      <View style={styles.content}>
        {tabs.find(tab => tab.id === activeTab)?.render()}
      </View>

      {/* Enhanced Modals */}
      <FavoritesManager
        visible={showFavorites}
        onClose={() => setShowFavorites(false)}
        onPlayItem={handleFavoritePlay}
        currentlyPlaying={currentlyPlaying}
      />

      <SocialSharingManager
        visible={showSharing}
        onClose={() => setShowSharing(false)}
        shareData={shareData || { type: 'radio_station', title: 'Kagema FM' }}
      />

      <AudioRecorder
        visible={showRecorder}
        onClose={() => setShowRecorder(false)}
        onRecordingComplete={handleRecordingComplete}
      />
    </SafeAreaView>
  );
};

// Main App with Theme Provider
const App = () => {
  return (
    <ThemeProvider>
      <IntegrationProvider>
        <EnhancedKagemaFMApp />
      </IntegrationProvider>
    </ThemeProvider>
  );
};

export default App;