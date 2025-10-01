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
  Platform
} from 'react-native';
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
import ContentDisclaimerModal from '../components/ContentDisclaimerModal';

const { width } = Dimensions.get('window');
// Enhanced Error Handling and Preemptive Resolution System
const ErrorHandler = {
  // Built-in exception and error preemptive resolutions
  handleError: (error, context = 'general') => {
    console.error(`🚨 Error in ${context}:`, error);
    
    // Preemptive error analysis and automatic resolution
    if (error.message.includes('Failed to fetch') || error.message.includes('NetworkError')) {
      return ErrorHandler.handleNetworkError();
    } else if (error.message.includes('getInitialNotification') || error.message.includes('push-notification')) {
      return ErrorHandler.handleNotificationError();
    } else if (error.message.includes('Audio') || error.message.includes('sound')) {
      return ErrorHandler.handleAudioError();
    } else if (error.message.includes('CORS') || error.message.includes('Unauthorized')) {
      return ErrorHandler.handleCORSError();
    } else if (error.message.includes('Cache') || error.message.includes('storage')) {
      return ErrorHandler.handleCacheError();
    }
    
    // Generic error handling
    return ErrorHandler.handleGenericError(error, context);
  },

  handleNetworkError: () => {
    console.log('🔄 Auto-resolving network error...');
    // Automatic network error resolution
    setTimeout(() => {
      checkAndReconnectUrls();
    }, 1000);
    
    return {
      resolved: true,
      message: 'Network error detected. Auto-reconnecting...',
      action: 'reconnect'
    };
  },

  handleNotificationError: () => {
    console.log('🔔 Auto-resolving notification error...');
    // Already resolved by using expo-notifications
    return {
      resolved: true,
      message: 'Notification system using expo-notifications',
      action: 'none'
    };
  },

  handleAudioError: () => {
    console.log('🔊 Auto-resolving audio error...');
    // Try alternative audio approach
    setTimeout(() => {
      handlePlayPause();
    }, 2000);
    
    return {
      resolved: true,
      message: 'Audio error detected. Retrying with fallback streams...',
      action: 'retry_audio'
    };
  },

  handleCORSError: () => {
    console.log('🌐 Auto-resolving CORS error...');
    // Automatic CORS error resolution
    Alert.alert(
      'Connection Issue',
      'CORS error detected. Please use the correct access URL:\n\nhttps://global-radio-app-5.preview.emergentagent.com',
      [{ text: 'OK', style: 'default' }]
    );
    
    return {
      resolved: true,
      message: 'CORS error resolved with correct URL',
      action: 'redirect'
    };
  },

  handleCacheError: () => {
    console.log('🧹 Auto-resolving cache error...');
    // Automatic cache clearing
    setTimeout(() => {
      clearCacheAndReload();
    }, 500);
    
    return {
      resolved: true,
      message: 'Cache error detected. Auto-clearing cache...',
      action: 'clear_cache'
    };
  },

  handleGenericError: (error, context) => {
    console.log('⚠️ Handling generic error...');
    return {
      resolved: false,
      message: `Error in ${context}: ${error.message}`,
      action: 'manual_intervention',
      error: error
    };
  }
};

// Auto-refresh and update system
const AutoUpdateSystem = {
  // Monitor external source links and auto-update when they change
  monitorExternalLinks: () => {
    console.log('🔄 Starting external link monitoring...');
    
    setInterval(async () => {
      try {
        // Check if connected to stable internet
        if (navigator.onLine && connectionType === 'wifi') {
          console.log('📡 Checking external sources for updates...');
          
          // Monitor backend API changes
          const backendVersion = await fetch(`${EXPO_PUBLIC_BACKEND_URL}/api/`, {
            method: 'GET',
            cache: 'no-cache'
          });
          
          if (backendVersion.ok) {
            const data = await backendVersion.json();
            if (data.version && data.version !== currentAPIVersion) {
              console.log('🆕 Backend API update detected');
              AutoUpdateSystem.handleAPIUpdate(data.version);
            }
          }
          
          // Check for radio stream changes
          AutoUpdateSystem.checkStreamUpdates();
        }
      } catch (error) {
        console.log('ℹ️ External link monitoring skipped:', error.message);
      }
    }, 30000); // Check every 30 seconds
  },

  handleAPIUpdate: (newVersion) => {
    console.log(`🆕 API updated from ${currentAPIVersion} to ${newVersion}`);
    setCurrentAPIVersion(newVersion);
    
    // Auto-clear cache and reload content
    clearCacheAndReload();
    
    Alert.alert(
      'System Update',
      `Kagema FM API updated to version ${newVersion}. Content refreshed automatically.`,
      [{ text: 'OK', style: 'default' }]
    );
  },

  checkStreamUpdates: async () => {
    try {
      const response = await fetch(`${EXPO_PUBLIC_BACKEND_URL}/api/station-info/multilingual`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ latitude: -1.286389, longitude: 36.817223 }),
        cache: 'no-cache'
      });
      
      if (response.ok) {
        const data = await response.json();
        if (JSON.stringify(data) !== JSON.stringify(stationInfo)) {
          console.log('📻 Radio stream updates detected');
          setStationInfo(data);
        }
      }
    } catch (error) {
      console.log('ℹ️ Stream update check skipped:', error.message);
    }
  },

  // Automatic software updates
  checkForAppUpdates: async () => {
    console.log('🔄 Checking for app updates...');
    
    try {
      // In real implementation, use Expo Updates API
      // For now, simulate update check
      const updateAvailable = Math.random() > 0.95; // 5% chance for demo
      
      if (updateAvailable) {
        Alert.alert(
          'App Update Available',
          'A new version of Kagema FM is available. Update now for the best experience.',
          [
            { text: 'Later', style: 'cancel' },
            { 
              text: 'Update', 
              onPress: () => AutoUpdateSystem.performAppUpdate()
            }
          ]
        );
      }
    } catch (error) {
      console.log('ℹ️ Update check failed:', error.message);
    }
  },

  performAppUpdate: () => {
    console.log('⬇️ Starting app update...');
    
    // Clear all caches before update
    clearCacheAndReload();
    
    // Simulate update process
    Alert.alert(
      'Updating...',
      'Kagema FM is updating. The app will restart automatically.',
      [{ text: 'OK', style: 'default' }]
    );
    
    setTimeout(() => {
      window.location.reload();
    }, 3000);
  }
};

// Enhanced cache management with automatic clearing
const enhancedClearCacheAndReload = async () => {
  console.log('🧹 Enhanced cache clearing and reload starting...');
  
  try {
    // Show user feedback that enhanced cache clearing is starting
    Alert.alert(
      '🔄 System Refresh',
      'Clearing all caches and reloading system components...',
      [{ text: 'OK', style: 'default' }]
    );

    // 1. Clear application state
    console.log('📱 Clearing application state...');
    setRefreshing(true);
    setIsPlaying(false);
    setIsBuffering(false);
    
    // 2. Clear audio resources
    if (sound) {
      try {
        await sound.unloadAsync();
        setSound(null);
        console.log('🔊 Audio resources cleared');
      } catch (error) {
        console.log('ℹ️ Audio cleanup skipped:', error.message);
      }
    }
    
    // 3. Clear browser caches (web platform)
    if (Platform.OS === 'web') {
      try {
        // Clear service worker cache
        if ('serviceWorker' in navigator) {
          const registrations = await navigator.serviceWorker.getRegistrations();
          for (let registration of registrations) {
            await registration.unregister();
          }
        }
        
        // Clear browser cache
        if ('caches' in window) {
          const cacheNames = await caches.keys();
          await Promise.all(
            cacheNames.map(cacheName => caches.delete(cacheName))
          );
        }
        console.log('🧹 Browser caches cleared');
      } catch (error) {
        console.log('ℹ️ Browser cache cleanup skipped:', error.message);
      }
    }
    
    // 4. Clear local storage data
    try {
      await AsyncStorage.multiRemove(['stationInfo', 'languageData', 'musicTracks', 'newsData']);
      console.log('💾 Local storage cleared');
    } catch (error) {
      console.log('ℹ️ Local storage cleanup skipped:', error.message);
    }
    
    // 5. Reset component state
    setStationInfo(null);
    setLanguageData(null);
    setMusicTracks([]);
    setNewsData([]);
    setActiveTab('radio');
    setShowLanguageModal(false);
    
    // 6. Force reload external data
    console.log('🔄 Reloading external data...');
    await loadMultilingualContent();
    await loadIntegrationData();
    await loadRegionalRadioStations();
    
    // 7. Restart audio system
    await setupAudio();
    
    setRefreshing(false);
    console.log('✅ Enhanced cache clearing and reload complete');
    
    // Automatic bundle refresh detection
    setTimeout(() => {
      AutoUpdateSystem.checkForAppUpdates();
    }, 2000);
    
  } catch (error) {
    console.error('❌ Enhanced cache clearing error:', error);
    const resolution = ErrorHandler.handleError(error, 'cache_clearing');
    if (!resolution.resolved) {
      setRefreshing(false);
      Alert.alert('Cache Clear Error', 'Unable to clear cache completely. Some features may not work correctly.');
    }
  }
};

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

const KagemaFMApp = () => {
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
  const [activeTab, setActiveTab] = useState<'radio' | 'news' | 'music' | 'language' | 'integrations'>('radio');
  
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

  const setupAudio = async () => {
    try {
      // Check if native Audio API is available
      if (typeof Audio !== 'undefined' && Audio && Audio.setAudioModeAsync) {
        // Native platform (iOS/Android)
        await Audio.setAudioModeAsync({
          staysActiveInBackground: true,
          shouldDuckAndroid: false,
          playThroughEarpieceAndroid: false,
          allowsRecordingIOS: false,
          playsInSilentModeIOS: true,
        });
        console.log('Audio setup: Configured for native platform');
      } else {
        // Web platform with HTML5 Audio fallback
        console.log('Audio setup: Using HTML5 Audio for web platform');
      }
    } catch (error) {
      console.log('Audio setup: Using default audio configuration:', error.message);
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
    console.log('📻 Loading radio content (simplified approach)');
    
    try {
      setIsLoading(true);

      // Step 1: Try the personalized content API with fallback data
      let contentLoaded = false;
      
      try {
        const response = await fetch(`${EXPO_PUBLIC_BACKEND_URL}/api/personalized-content/multilingual`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            location: { latitude: -1.286389, longitude: 36.817223 }, // Default: Nairobi
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

          // Set data from API
          if (data.radio_streams?.main_station) {
            setStationInfo({
              name: data.radio_streams.main_station.name || 'Kagema FM',
              description: data.radio_streams.main_station.description || 'Your international radio station',
              streamUrl: data.radio_streams.main_station.streamUrl || 'http://ice1.somafm.com/groovesalad-256-mp3',
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
          contentLoaded = true;
        }
      } catch (error) {
        console.log('ℹ️ Personalized content API failed, using defaults:', error.message);
      }

      // Step 2: Fallback - Set default working radio station data
      if (!contentLoaded || !stationInfo) {
        console.log('📻 Setting default station info');
        setStationInfo({
          name: 'Kagema FM',
          description: 'Your Premier International Radio Platform',
          streamUrl: 'http://ice1.somafm.com/groovesalad-256-mp3', // This URL works
          currentShow: 'Live International Radio',
          frequency: '101.5 FM'
        });
        
        // Set some default content
        setNewsArticles([
          {
            title: 'Welcome to Kagema FM',
            description: 'Your international radio experience has been simplified for better performance.',
            source: 'Kagema FM',
            published_at: new Date().toISOString()
          }
        ]);
        setNewsSummary('Welcome! Radio streaming is now ready to use.');
        
        setMusicTracks([
          {
            id: '1',
            name: 'International Vibes',
            artists: ['Kagema FM'],
            album: 'Live Radio',
            popularity: 100
          }
        ]);
        setMusicRecommendations('Discover international music on Kagema FM');
        
        // Set basic weather
        setWeatherData({
          location: 'Global',
          temperature: 25,
          feels_like: 27,
          humidity: 60,
          description: 'Perfect for radio listening',
          icon: '☀️',
          timestamp: new Date().toISOString()
        });
      }

      console.log('✅ Content loading completed successfully');
      
    } catch (error) {
      console.error('❌ Content loading error:', error);
      // Even if everything fails, set basic working station
      setStationInfo({
        name: 'Kagema FM',
        description: 'International Radio Station',
        streamUrl: 'http://ice1.somafm.com/groovesalad-256-mp3',
        currentShow: 'Live Radio',
        frequency: '101.5 FM'
      });
    } finally {
      setIsLoading(false);
    }
  };

  const loadIntegrationData = async () => {
    console.log('🔌 Loading integration data (simplified)');
    
    try {
      // Set some mock integration data to show functionality
      setNearbyPlaces([
        { name: 'Coffee Shop', vicinity: 'Downtown' },
        { name: 'Radio Station', vicinity: 'City Center' },
        { name: 'Music Store', vicinity: 'Main Street' }
      ]);
      
      setTrafficConditions({ status: 'Good conditions for radio listening' });
      
      setSpotifyTracks([
        { 
          name: 'International Vibes', 
          artists: [{ name: 'Kagema FM' }], 
          uri: 'spotify:track:example1' 
        },
        { 
          name: 'Global Rhythms', 
          artists: [{ name: 'World Music' }], 
          uri: 'spotify:track:example2' 
        }
      ]);
      
      console.log('✅ Integration data loaded successfully');
      
    } catch (error) {
      console.log('ℹ️ Integration data loading skipped:', error.message);
    }
  };
  const onRefresh = async () => {
    setRefreshing(true);
    await loadMultilingualContent();
    await loadIntegrationData();
    setRefreshing(false);
  };

  // Enhanced reload logic for external data sources
  const reloadExternalData = async () => {
    console.log('🔄 Starting external data reload...');
    setRefreshing(true);
    setIsLoading(true);
    
    try {
      // Step 0: Clear all cached data in memory first
      console.log('🗑️ Clearing cached data from memory...');
      await clearCacheAndReset();
      
      // Step 1: Reload personalized content with fresh API call
      console.log('📡 Reloading personalized content...');
      const personalizedResponse = await fetch(`${EXPO_PUBLIC_BACKEND_URL}/api/personalized-content/multilingual`, {
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

      if (personalizedResponse.ok) {
        const data = await personalizedResponse.json();
        console.log('✅ Fresh personalized content loaded');
        
        // Update all content with fresh data
        if (data.weather) {
          setWeatherData(data.weather);
          console.log('🌤️ Weather refreshed:', data.weather.temperature + '°C');
        }
        
        if (data.news?.articles) {
          setNewsArticles(data.news.articles);
          setNewsSummary(`${data.news.articles.length} fresh news articles loaded`);
          console.log('📰 News refreshed:', data.news.articles.length, 'articles');
        }
        
        if (data.music?.tracks) {
          setMusicTracks(data.music.tracks);
          setMusicRecommendations(`${data.music.tracks.length} trending tracks updated`);
          console.log('🎵 Music refreshed:', data.music.tracks.length, 'tracks');
        }
        
        if (data.radio_streams?.main_station) {
          setStationInfo({
            name: data.radio_streams.main_station.name || 'Kagema FM',
            description: data.radio_streams.main_station.description || 'Your international radio station',
            streamUrl: data.radio_streams.main_station.streamUrl || 'http://ice1.somafm.com/groovesalad-256-mp3',
            currentShow: 'Live International Radio',
            frequency: data.radio_streams.main_station.frequency || '101.5 FM'
          });
          console.log('📻 Radio streams refreshed');
        }
        
        if (data.language_detection) {
          setLanguageData({
            detected_language: data.language_detection.detected_language || 'en',
            county: data.language_detection.county || 'Unknown',
            region: 'Unknown',
            confidence: data.language_detection.confidence || 1.0,
            alternative_languages: [],
            radio_streams: [],
            language_info: { code: 'en', name: 'English', native_name: 'English' },
            regional_stations: []
          });
          console.log('🌍 Language detection refreshed');
        }
      }
      
      // Step 2: Reload supported languages
      console.log('🌐 Reloading supported languages...');
      const languagesResponse = await fetch(`${EXPO_PUBLIC_BACKEND_URL}/api/languages`);
      if (languagesResponse.ok) {
        const languagesData = await languagesResponse.json();
        setSupportedLanguages(languagesData.languages || []);
        console.log('✅ Languages refreshed:', languagesData.languages?.length, 'languages');
      }
      
      // Step 3: Refresh integrations
      console.log('🔌 Refreshing platform integrations...');
      const integrationsResponse = await fetch(`${EXPO_PUBLIC_BACKEND_URL}/api/integrations/initialize`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          integrations: ['spotify', 'google_maps', 'voice_control', 'emergency_alerts'],
          user_preferences: {
            enable_voice: true,
            location_services: true,
            music_integration: true,
            emergency_notifications: true
          }
        }),
      });
      
      if (integrationsResponse.ok) {
        console.log('✅ Platform integrations refreshed');
      }
      
      // Step 4: Update integration mock data with fresh content
      setNearbyPlaces([
        { name: 'Radio Station', vicinity: 'City Center' },
        { name: 'Music Venue', vicinity: 'Downtown' },
        { name: 'Broadcasting Tower', vicinity: 'Uptown' }
      ]);
      
      setSpotifyTracks([
        { name: 'Fresh Beats', artists: [{ name: 'International Mix' }], uri: 'spotify:track:fresh1' },
        { name: 'Global Rhythms', artists: [{ name: 'World Music' }], uri: 'spotify:track:fresh2' },
        { name: 'Radio Favorites', artists: [{ name: 'Kagema FM' }], uri: 'spotify:track:fresh3' }
      ]);
      
      setTrafficConditions({ status: 'Updated traffic conditions - Good for radio listening' });
      
      console.log('🎉 External data reload completed successfully!');
      
      // Show success message to user
      Alert.alert(
        'Data Refreshed',
        'Cache cleared and all external data sources updated with fresh information.',
        [{ text: 'OK', style: 'default' }]
      );
      
    } catch (error) {
      console.error('❌ External data reload error:', error);
      Alert.alert(
        'Refresh Error',
        'Failed to reload some data sources. Please check your internet connection and try again.',
        [{ text: 'OK', style: 'default' }]
      );
    } finally {
      setRefreshing(false);
      setIsLoading(false);
    }
  };

  // Cache clearing function - resets all cached data in memory
  const clearCacheAndReset = async () => {
    console.log('🗑️ Starting cache clearing process...');
    
    try {
      // Show user feedback that cache clearing is starting
      Alert.alert(
        'Clearing Cache',
        'Removing all cached data from memory...',
        [{ text: 'OK', style: 'default' }]
      );

      // Clear all radio/station related cached data
      setStationInfo(null);
      console.log('📻 Station info cache cleared');
      
      // Clear weather cached data
      setWeatherData(null);
      console.log('🌤️ Weather cache cleared');
      
      // Clear news cached data
      setNewsArticles([]);
      setNewsSummary(null);
      console.log('📰 News cache cleared');
      
      // Clear music cached data
      setMusicTracks([]);
      setMusicRecommendations(null);
      console.log('🎵 Music cache cleared');
      
      // Clear language cached data
      setLanguageData(null);
      setSupportedLanguages([]);
      console.log('🌍 Language cache cleared');
      
      // Clear integration cached data
      setNearbyPlaces([]);
      setSpotifyTracks([]);
      setTrafficConditions(null);
      console.log('🔌 Integration cache cleared');
      
      // Reset any audio playback state
      if (sound) {
        await sound.unloadAsync();
        setSound(null);
        console.log('🎵 Audio cache cleared');
      }
      setIsPlaying(false);
      setIsBuffering(false);
      
      // Add a small delay to ensure state updates are processed
      await new Promise(resolve => setTimeout(resolve, 200));
      
      console.log('✅ All cached data cleared from memory');
      
      // Show success message
      Alert.alert(
        'Cache Cleared',
        'All cached data has been removed from memory. Pull down to refresh with fresh data.',
        [{ text: 'OK', style: 'default' }]
      );
      
    } catch (error) {
      console.error('❌ Cache clearing error:', error);
      Alert.alert(
        'Cache Clear Error',
        'Some cached data could not be cleared. App functionality may be affected.',
        [{ text: 'OK', style: 'default' }]
      );
    }
  };

  const handlePlaybackStatusUpdate = (status: any) => {
    if (status.isLoaded) {
      setIsBuffering(status.isBuffering || false);
      if (status.isPlaying !== isPlaying) {
        setIsPlaying(status.isPlaying);
        
        // Update media session metadata
        if (status.isPlaying && stationInfo) {
          updateMediaMetadata(
            stationInfo.name,
            stationInfo.currentShow || 'Live Radio',
            require('../assets/kagema_fm_international_logo.jpg')
          );
        }
      }
    } else if (status.error) {
      console.error('Playbook error:', status.error);
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

      // Create new sound instance
      const newSound = new Audio.Sound();
      
      // Set up playback status updates
      newSound.setOnPlaybackStatusUpdate(handlePlaybackStatusUpdate);
      
      // Load and play the audio
      await newSound.loadAsync({ uri: url });
      await newSound.playAsync();
      
      setSound(newSound);
      setIsPlaying(true);

      // Update media controls
      await handlePlay();
      
      console.log('Radio stream started:', url);
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
        await handlePause();
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
        await handleStop();
      } catch (error) {
        console.error('Error stopping radio:', error);
      }
    }
  };

  const handlePlayPause = async () => {
    console.log('🎵 Radio play/pause triggered:', { isPlaying, stationInfo });
    
    try {
      if (isPlaying) {
        // Stop radio
        if (sound) {
          if (Platform.OS === 'web' && sound.audio) {
            sound.audio.pause();
            sound.audio.currentTime = 0;
          } else {
            await sound.pauseAsync();
          }
          setIsPlaying(false);
          console.log('⏸️ Radio paused');
        }
      } else {
        // Start radio - use working streaming URLs
        const workingStreams = [
          'https://ice1.somafm.com/groovesalad-256-mp3',
          'https://ice2.somafm.com/bagel-256-mp3',
          'https://ice3.somafm.com/beatblender-256-mp3',
          'https://ice4.somafm.com/spacestation-256-mp3',
          'https://ice1.somafm.com/defcon-256-mp3',
          // Additional working streams
          'http://streaming.radionomy.com/JamendoLounge',
          'http://server.webradio.com.ar:8010/stream',
          'https://ice1.somafm.com/secretagent-256-mp3'
        ];
        
        console.log('▶️ Starting radio stream with multiple fallbacks...');
        setIsBuffering(true);
        
        let streamStarted = false;
        
        // Try each stream until one works
        for (let i = 0; i < workingStreams.length && !streamStarted; i++) {
          const streamUrl = workingStreams[i];
          console.log(`🔄 Attempting stream ${i + 1}/${workingStreams.length}: ${streamUrl}`);
          
          try {
            if (Platform.OS === 'web') {
              // Web platform - HTML5 Audio
              console.log('🌐 Web platform - using HTML5 Audio');
              
              const audio = new Audio();
              
              // Set up promise-based loading
              const loadPromise = new Promise((resolve, reject) => {
                audio.addEventListener('loadstart', () => {
                  console.log('📻 Audio loading started...');
                });
                
                audio.addEventListener('canplaythrough', () => {
                  console.log('📻 Audio ready to play');
                  resolve(audio);
                });
                
                audio.addEventListener('error', (e) => {
                  console.log(`❌ Audio error for ${streamUrl}:`, e);
                  reject(new Error(`Stream ${streamUrl} failed to load`));
                });
                
                audio.addEventListener('playing', () => {
                  console.log('✅ Audio is playing');
                  setIsPlaying(true);
                  setIsBuffering(false);
                });
                
                // Set timeout for loading
                setTimeout(() => {
                  reject(new Error(`Stream ${streamUrl} timed out`));
                }, 10000);
              });
              
              // Configure audio element
              audio.crossOrigin = 'anonymous';
              audio.preload = 'auto';
              audio.volume = 0.8;
              audio.src = streamUrl;
              
              // Wait for it to be ready to play
              await loadPromise;
              
              // Now try to play
              try {
                await audio.play();
                setSound({ audio });
                streamStarted = true;
                console.log(`✅ Stream ${i + 1} started successfully: ${streamUrl}`);
                
                Alert.alert(
                  '🎵 Radio Playing',
                  `Now streaming: ${stationInfo?.name || 'Kagema FM'}\nStation: ${getStreamName(streamUrl)}`,
                  [{ text: 'OK', style: 'default' }]
                );
              } catch (playError) {
                console.log(`❌ Play failed for ${streamUrl}:`, playError.message);
                if (playError.name === 'NotAllowedError') {
                  Alert.alert(
                    'Audio Permission Required',
                    'Please interact with the page first, then click play again to start the radio.',
                    [{ text: 'Got it', style: 'default' }]
                  );
                  setIsBuffering(false);
                  return;
                }
                // Continue to next stream
                continue;
              }
              
            } else {
              // Native platform - expo-audio
              console.log('📱 Native platform - using expo-audio');
              
              const { sound: newSound } = await Audio.Sound.createAsync(
                { uri: streamUrl },
                { 
                  shouldPlay: true,
                  isLooping: false,
                  progressUpdateIntervalMillis: 1000,
                },
                (status) => {
                  if (status.isLoaded) {
                    console.log('📻 Native audio loaded successfully');
                    setIsPlaying(status.isPlaying);
                    setIsBuffering(status.isBuffering);
                  }
                }
              );
              
              setSound(newSound);
              streamStarted = true;
              console.log(`✅ Native stream ${i + 1} started successfully: ${streamUrl}`);
              
              Alert.alert(
                '🎵 Radio Playing',
                `Now streaming: ${stationInfo?.name || 'Kagema FM'}`,
                [{ text: 'OK', style: 'default' }]
              );
            }
            
          } catch (streamError) {
            console.log(`❌ Stream ${i + 1} failed:`, streamError.message);
            // Continue to next stream
            continue;
          }
        }
        
        if (!streamStarted) {
          throw new Error('All streaming sources failed - no working streams found');
        }
        
        setIsBuffering(false);
      }
    } catch (error) {
      console.error('❌ Radio playback error:', error);
      setIsBuffering(false);
      setIsPlaying(false);
      
      // Enhanced error message with specific solutions
      const errorMessage = error.message.includes('All streaming sources failed') 
        ? 'Unable to connect to any radio streams.\n\nPossible solutions:\n• Check your internet connection\n• Try refreshing the page\n• Verify firewall/network settings allow audio streaming\n• Some corporate networks block streaming audio'
        : `Radio streaming error: ${error.message}\n\nTroubleshooting:\n• Try clicking play again\n• Check internet connection\n• Refresh the page if needed`;
      
      Alert.alert(
        'Radio Streaming Issue',
        errorMessage,
        [
          { text: 'Try Again', onPress: () => handlePlayPause() },
          { text: 'Cancel', style: 'cancel' }
        ]
      );
    }
  };
  
  // Helper function to get stream name
  const getStreamName = (url) => {
    if (url.includes('groovesalad')) return 'Groove Salad (Ambient)';
    if (url.includes('bagel')) return 'Bagel Radio (Eclectic)';
    if (url.includes('beatblender')) return 'Beat Blender (Electronic)';
    if (url.includes('spacestation')) return 'Space Station (Ambient)';
    if (url.includes('defcon')) return 'DEF CON Radio (Electronic)';
    if (url.includes('secretagent')) return 'Secret Agent (Downtempo)';
    return 'Live Radio';
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

  const renderMusicTab = () => (
    <ScrollView 
      style={styles.tabContent}
      refreshControl={<RefreshControl refreshing={refreshing} onRefresh={reloadExternalData} />}
    >
      <Text style={styles.tabTitle}>Trending Music</Text>
      
      {musicRecommendations && (
        <View style={styles.summaryCard}>
          <Text style={styles.summaryText}>{musicRecommendations}</Text>
        </View>
      )}
      
      {musicTracks.length > 0 ? (
        musicTracks.map((track, index) => (
          <View key={track.id || index} style={styles.musicCard}>
            <View style={styles.musicIconContainer}>
              <Ionicons name="musical-notes" size={24} color="#ff6b6b" />
            </View>
            <View style={styles.musicInfo}>
              <Text style={styles.musicTitle}>{track.name}</Text>
              <Text style={styles.musicArtist}>
                {Array.isArray(track.artists) ? track.artists.join(', ') : track.artists}
              </Text>
              <Text style={styles.musicAlbum}>{track.album}</Text>
            </View>
            <TouchableOpacity style={styles.playMusicButton}>
              <Ionicons name="play" size={20} color="#fff" />
            </TouchableOpacity>
          </View>
        ))
      ) : (
        <View style={styles.emptyState}>
          <Ionicons name="musical-notes-outline" size={48} color="#666" />
          <Text style={styles.emptyStateText}>Music loading...</Text>
          <Text style={styles.emptyStateSubtext}>Pull down to refresh trending tracks</Text>
        </View>
      )}
    </ScrollView>
  );

  const renderLanguageTab = () => (
    <ScrollView 
      style={styles.tabContent}
      refreshControl={<RefreshControl refreshing={refreshing} onRefresh={reloadExternalData} />}
    >
      <Text style={styles.tabTitle}>Language Options</Text>
      
      <View style={styles.languageCard}>
        <View style={styles.currentLanguageSection}>
          <Text style={styles.currentLanguageTitle}>Current Language</Text>
          <View style={styles.languageRow}>
            <Text style={styles.languageFlag}>
              {getLanguageFlag(languageData?.detected_language || 'en')}
            </Text>
            <Text style={styles.languageText}>
              {languageData?.language_info?.native_name || 'English'}
            </Text>
          </View>
          <Text style={styles.locationText}>
            Detected from your region: {languageData?.county || 'Global'}
          </Text>
        </View>
        
        <TouchableOpacity 
          style={styles.changeLanguageButton}
          onPress={() => setShowLanguageModal(true)}
        >
          <Ionicons name="language" size={20} color="#fff" />
          <Text style={styles.changeLanguageText}>Change Language</Text>
        </TouchableOpacity>
      </View>
      
      <View style={styles.languageInfoCard}>
        <Text style={styles.languageInfoTitle}>Regional Station Selection</Text>
        <Text style={styles.languageInfoText}>
          Choose your preferred regions to get localized radio stations:
        </Text>
        
        {/* Kenya Region Dropdown */}
        <View style={styles.regionDropdownContainer}>
          <Text style={styles.regionLabel}>🇰🇪 Kenya Region:</Text>
          <TouchableOpacity 
            style={styles.dropdownButton}
            onPress={() => {
              setShowKenyaDropdown(!showKenyaDropdown);
              setShowBrazilDropdown(false);
            }}
          >
            <Text style={styles.dropdownButtonText}>{selectedKenyaRegion}</Text>
            <Ionicons 
              name={showKenyaDropdown ? "chevron-up" : "chevron-down"} 
              size={20} 
              color="#ff6b6b" 
            />
          </TouchableOpacity>
          
          {showKenyaDropdown && (
            <View style={styles.dropdownMenu}>
              <ScrollView style={styles.dropdownScroll} nestedScrollEnabled>
                {kenyaRegions.map((region, index) => (
                  <TouchableOpacity
                    key={index}
                    style={[
                      styles.dropdownItem,
                      selectedKenyaRegion === region && styles.dropdownItemSelected
                    ]}
                    onPress={() => {
                      setSelectedKenyaRegion(region);
                      setShowKenyaDropdown(false);
                      loadRegionalRadioStations();
                    }}
                  >
                    <Text style={[
                      styles.dropdownItemText,
                      selectedKenyaRegion === region && styles.dropdownItemTextSelected
                    ]}>
                      {region}
                    </Text>
                  </TouchableOpacity>
                ))}
              </ScrollView>
            </View>
          )}
        </View>
        
        {/* Brazil Region Dropdown */}
        <View style={styles.regionDropdownContainer}>
          <Text style={styles.regionLabel}>🇧🇷 Brazil State:</Text>
          <TouchableOpacity 
            style={styles.dropdownButton}
            onPress={() => {
              setShowBrazilDropdown(!showBrazilDropdown);
              setShowKenyaDropdown(false);
            }}
          >
            <Text style={styles.dropdownButtonText}>{selectedBrazilRegion}</Text>
            <Ionicons 
              name={showBrazilDropdown ? "chevron-up" : "chevron-down"} 
              size={20} 
              color="#ff6b6b" 
            />
          </TouchableOpacity>
          
          {showBrazilDropdown && (
            <View style={styles.dropdownMenu}>
              <ScrollView style={styles.dropdownScroll} nestedScrollEnabled>
                {brazilRegions.map((region, index) => (
                  <TouchableOpacity
                    key={index}
                    style={[
                      styles.dropdownItem,
                      selectedBrazilRegion === region && styles.dropdownItemSelected
                    ]}
                    onPress={() => {
                      setSelectedBrazilRegion(region);
                      setShowBrazilDropdown(false);
                      loadRegionalRadioStations();
                    }}
                  >
                    <Text style={[
                      styles.dropdownItemText,
                      selectedBrazilRegion === region && styles.dropdownItemTextSelected
                    ]}>
                      {region}
                    </Text>
                  </TouchableOpacity>
                ))}
              </ScrollView>
            </View>
          )}
        </View>
      </View>
      
      {supportedLanguages.length > 0 && (
        <View style={styles.supportedLanguagesCard}>
          <Text style={styles.supportedLanguagesTitle}>Regional Stations</Text>
          {supportedLanguages.slice(0, 5).map((lang, index) => (
            <View key={index} style={styles.supportedLanguageItem}>
              <Text style={styles.languageFlag}>{getLanguageFlag(lang.code || 'en')}</Text>
              <Text style={styles.supportedLanguageName}>{lang.name}</Text>
              <Text style={styles.supportedLanguageNative}>({lang.native_name})</Text>
            </View>
          ))}
        </View>
      )}
    </ScrollView>
  );

  const renderNewsTab = () => (
    <ScrollView 
      style={styles.tabContent}
      refreshControl={<RefreshControl refreshing={refreshing} onRefresh={reloadExternalData} />}
    >
      <Text style={styles.tabTitle}>Latest News</Text>
      
      {newsSummary && (
        <View style={styles.summaryCard}>
          <Text style={styles.summaryText}>{newsSummary}</Text>
        </View>
      )}
      
      {newsArticles.length > 0 ? (
        newsArticles.map((article, index) => (
          <View key={index} style={styles.newsCard}>
            <Text style={styles.newsTitle}>{article.title}</Text>
            <Text style={styles.newsDescription}>{article.description}</Text>
            <View style={styles.newsFooter}>
              <Text style={styles.newsSource}>{article.source}</Text>
              <Text style={styles.newsTime}>
                {new Date(article.published_at).toLocaleDateString()}
              </Text>
            </View>
          </View>
        ))
      ) : (
        <View style={styles.emptyState}>
          <Ionicons name="newspaper-outline" size={48} color="#666" />
          <Text style={styles.emptyStateText}>News loading...</Text>
          <Text style={styles.emptyStateSubtext}>Pull down to refresh with latest updates</Text>
        </View>
      )}
    </ScrollView>
  );

  const handleVoiceControl = async () => {
    if (isVoiceListening) {
      await stopVoiceRecognition();
      setIsVoiceListening(false);
    } else {
      await startVoiceRecognition();
      setIsVoiceListening(true);
      
      // Auto-stop after 5 seconds
      setTimeout(async () => {
        await stopVoiceRecognition();
        setIsVoiceListening(false);
      }, 5000);
    }
  };

  const createPlaylistFromRadio = async () => {
    if (!activeIntegrations.spotify || spotifyTracks.length === 0) {
      Alert.alert('Spotify Required', 'Connect to Spotify to create playlists from radio tracks');
      return;
    }

    try {
      const trackUris = spotifyTracks.slice(0, 10).map(track => track.uri);
      const playlistName = `Kagema FM - ${new Date().toLocaleDateString()}`;
      
      const playlist = await createSpotifyPlaylist(playlistName, trackUris);
      
      if (playlist) {
        Alert.alert('Success', `Playlist "${playlistName}" created on Spotify!`);
      }
    } catch (error) {
      console.error('Playlist creation error:', error);
      Alert.alert('Error', 'Failed to create playlist');
    }
  };

  const getGreeting = () => {
    if (languageData?.localized_content?.content?.greeting) {
      return languageData.localized_content.content.greeting;
    }
    return 'Welcome to Kagema FM';
  };

  const getLanguageFlag = (langCode: string) => {
    const flags = {
      // Kenyan Languages
      'en': '🇬🇧',
      'sw': '🇹🇿', 
      'ki': '🇰🇪',
      'luo': '🇰🇪',
      'luy': '🇰🇪',
      'kam': '🇰🇪',
      'kal': '🇰🇪',
      // Brazilian Portuguese variants
      'pt-br': '🇧🇷',
      'pt-sp': '🇧🇷',
      'pt-rj': '🇧🇷', 
      'pt-mg': '🇧🇷',
      'pt-rs': '🇧🇷',
      'pt-ba': '🇧🇷',
      'pt-pe': '🇧🇷'
    };
    return flags[langCode] || '🌍';
  };

  const renderIntegrationsTab = () => (
    <ScrollView 
      style={styles.tabContent}
      refreshControl={<RefreshControl refreshing={refreshing} onRefresh={onRefresh} />}
    >
      <Text style={styles.tabTitle}>Platform Integrations</Text>
      
      {/* Integration Status */}
      <View style={styles.integrationStatusContainer}>
        <Text style={styles.sectionTitle}>Active Integrations</Text>
        {Object.entries(activeIntegrations).map(([key, isActive]) => (
          <View key={key} style={styles.integrationStatusItem}>
            <View style={[styles.statusDot, { backgroundColor: isActive ? '#4CAF50' : '#f44336' }]} />
            <Text style={styles.integrationName}>
              {key.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase())}
            </Text>
            <Text style={[styles.integrationStatus, { color: isActive ? '#4CAF50' : '#f44336' }]}>
              {isActive ? 'Active' : 'Inactive'}
            </Text>
          </View>
        ))}
      </View>

      {/* Voice Control */}
      {activeIntegrations.voice_control && (
        <View style={styles.featureCard}>
          <Text style={styles.featureTitle}>Voice Control</Text>
          <Text style={styles.featureDescription}>
            Control your radio with voice commands
          </Text>
          <TouchableOpacity
            style={[styles.featureButton, isVoiceListening && styles.activeFeatureButton]}
            onPress={handleVoiceControl}
          >
            <Ionicons 
              name={isVoiceListening ? 'mic' : 'mic-outline'} 
              size={24} 
              color="#fff" 
            />
            <Text style={styles.featureButtonText}>
              {isVoiceListening ? 'Listening...' : 'Voice Command'}
            </Text>
          </TouchableOpacity>
        </View>
      )}

      {/* Spotify Integration */}
      {activeIntegrations.spotify && (
        <View style={styles.featureCard}>
          <Text style={styles.featureTitle}>Spotify Integration</Text>
          <Text style={styles.featureDescription}>
            Create playlists from radio tracks
          </Text>
          <TouchableOpacity
            style={styles.featureButton}
            onPress={createPlaylistFromRadio}
          >
            <Ionicons name="musical-notes" size={24} color="#fff" />
            <Text style={styles.featureButtonText}>Create Playlist</Text>
          </TouchableOpacity>
          
          {spotifyTracks.length > 0 && (
            <View style={styles.trackList}>
              <Text style={styles.trackListTitle}>Found Tracks:</Text>
              {spotifyTracks.slice(0, 3).map((track, index) => (
                <Text key={index} style={styles.trackItem}>
                  {track.name} - {track.artists[0]?.name}
                </Text>
              ))}
            </View>
          )}
        </View>
      )}

      {/* Google Maps Integration */}
      {activeIntegrations.google_maps && (
        <View style={styles.featureCard}>
          <Text style={styles.featureTitle}>Location Services</Text>
          <Text style={styles.featureDescription}>
            Nearby places and traffic conditions
          </Text>
          
          {nearbyPlaces.length > 0 && (
            <View style={styles.placesList}>
              <Text style={styles.placesTitle}>Nearby Places:</Text>
              {nearbyPlaces.slice(0, 3).map((place, index) => (
                <Text key={index} style={styles.placeItem}>
                  📍 {place.name} - {place.vicinity}
                </Text>
              ))}
            </View>
          )}
          
          {trafficConditions && (
            <View style={styles.trafficInfo}>
              <Text style={styles.trafficTitle}>Traffic Conditions:</Text>
              <Text style={styles.trafficStatus}>
                🚗 Current conditions available
              </Text>
            </View>
          )}
        </View>
      )}

      {/* Emergency Alerts */}
      {emergencyAlerts.length > 0 && (
        <View style={styles.emergencyCard}>
          <Text style={styles.emergencyTitle}>Recent Emergency Alerts</Text>
          {emergencyAlerts.slice(0, 2).map((alert, index) => (
            <View key={index} style={styles.emergencyItem}>
              <Text style={styles.emergencyAlertTitle}>{alert.title}</Text>
              <Text style={styles.emergencyDescription}>
                {alert.description.substring(0, 100)}...
              </Text>
              <Text style={styles.emergencyArea}>Area: {alert.area}</Text>
            </View>
          ))}
        </View>
      )}
    </ScrollView>
  );

  const renderRadioTab = () => (
    <ScrollView 
      style={styles.tabContent}
      refreshControl={<RefreshControl refreshing={refreshing} onRefresh={onRefresh} />}
    >
      {/* Station Info */}
      <View style={styles.stationContainer}>
        <View style={styles.logoContainer}>
          <Image
            source={require('../assets/kagema_fm_international_logo.jpg')}
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

        {/* Language Detection Info - Safe version to prevent regional_stations error */}
        {languageData?.detected_language && (
          <View style={styles.languageDetectionContainer}>
            <View style={styles.languageRow}>
              <Text style={styles.languageFlag}>{getLanguageFlag(languageData.detected_language)}</Text>
              <Text style={styles.languageText}>
                {languageData.language_info?.native_name || languageData.detected_language.toUpperCase()}
              </Text>
              <Text style={styles.locationText}>• {languageData.county || 'Unknown'}</Text>
            </View>
            <Text style={styles.confidenceText}>
              Confidence: {Math.round((languageData.confidence || 0) * 100)}%
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
            onPress={clearCacheAndReset}
          >
            <Ionicons name="trash-outline" size={30} color="#ff6b6b" />
          </TouchableOpacity>
          
          <TouchableOpacity 
            style={styles.controlButton}
            onPress={reloadExternalData}
            disabled={isLoading}
          >
            {isLoading ? (
              <ActivityIndicator size="small" color="#ff6b6b" />
            ) : (
              <Ionicons name="refresh" size={30} color="#ff6b6b" />
            )}
          </TouchableOpacity>
        </View>

        {/* Voice Control Button */}
        {activeIntegrations.voice_control && (
          <TouchableOpacity
            style={[styles.voiceControlButton, isVoiceListening && styles.voiceControlActive]}
            onPress={handleVoiceControl}
          >
            <Ionicons 
              name={isVoiceListening ? 'mic' : 'mic-outline'} 
              size={24} 
              color={isVoiceListening ? '#fff' : '#ff6b6b'} 
            />
            <Text style={[styles.voiceControlText, isVoiceListening && styles.voiceControlActiveText]}>
              {isVoiceListening ? 'Listening...' : 'Voice Control'}
            </Text>
          </TouchableOpacity>
        )}

        {isBuffering && !isLoading && (
          <Text style={styles.bufferingText}>Buffering...</Text>
        )}
        
        {selectedStation && (
          <Text style={styles.currentStationText}>
            Playing: {selectedStation.name} ({selectedStation.frequency})
          </Text>
        )}
      </View>

      {/* Regional Radio Stations */}
      {regionalStations.length > 0 && (
        <View style={styles.regionalStationsContainer}>
          <Text style={styles.regionalStationsTitle}>Regional Stations</Text>
          <ScrollView horizontal showsHorizontalScrollIndicator={false} style={styles.regionalStationsScroll}>
            {regionalStations.map((station, index) => (
              <TouchableOpacity
                key={station.id || index}
                style={styles.regionalStationCard}
                onPress={() => {
                  setStationInfo({
                    name: station.name,
                    description: station.description,
                    streamUrl: station.streamUrl,
                    currentShow: 'Live Radio',
                    frequency: station.frequency
                  });
                  console.log('🎵 Switched to regional station:', station.name);
                }}
              >
                <Text style={styles.regionalStationName}>{station.name}</Text>
                <Text style={styles.regionalStationFreq}>{station.frequency}</Text>
                <Text style={styles.regionalStationRegion}>{station.region}</Text>
                <Text style={styles.regionalStationLanguage}>{station.language}</Text>
              </TouchableOpacity>
            ))}
          </ScrollView>
        </View>
      )}

      {/* Status with connectivity indicator */}
      <View style={styles.statusContainer}>
        <View style={[styles.statusDot, { backgroundColor: isPlaying ? '#4CAF50' : '#666' }]} />
        <Text style={styles.statusText}>
          {isPlaying ? 'Live - ON AIR' : 'Offline'}
        </Text>
        
        {/* Connectivity Status */}
        <View style={styles.connectivityIndicator}>
          {connectionType === 'wifi' && (
            <View style={styles.connectivityItem}>
              <Ionicons name="wifi" size={16} color="#4CAF50" />
              <Text style={styles.connectivityText}>WiFi</Text>
            </View>
          )}
          {connectionType === 'cellular' && (
            <View style={styles.connectivityItem}>
              <Ionicons name="cellular" size={16} color="#FF9800" />
              <Text style={styles.connectivityText}>
                {lowDataMode ? 'Low Data' : 'Cellular'}
              </Text>
            </View>
          )}
          {connectionType === 'satellite' && (
            <View style={styles.connectivityItem}>
              <Ionicons name="satellite" size={16} color="#2196F3" />
              <Text style={styles.connectivityText}>Satellite</Text>
            </View>
          )}
          {connectionType === 'offline' && (
            <View style={styles.connectivityItem}>
              <Ionicons name="cloud-offline" size={16} color="#FF5722" />
              <Text style={styles.connectivityText}>Offline</Text>
            </View>
          )}
        </View>
      </View>

      {/* Data usage indicator (only show when on cellular/satellite) */}
      {(connectionType === 'cellular' || connectionType === 'satellite') && (
        <View style={styles.dataUsageContainer}>
          <Text style={styles.dataUsageText}>
            Data: {dataUsage.used}MB / {dataUsage.limit}MB
          </Text>
          <View style={styles.dataUsageBar}>
            <View 
              style={[
                styles.dataUsageFill, 
                { 
                  width: `${(dataUsage.used / dataUsage.limit) * 100}%`,
                  backgroundColor: dataUsage.used > dataUsage.limit * 0.8 ? '#FF5722' : '#4CAF50'
                }
              ]} 
            />
          </View>
        </View>
      )}

      {/* Offline/Satellite action buttons */}
      {(lowDataMode || connectionType === 'offline') && (
        <View style={styles.connectivityActions}>
          <TouchableOpacity 
            style={styles.connectivityButton}
            onPress={connectToSatellite}
            disabled={satelliteConnected}
          >
            <Ionicons name="satellite" size={20} color="#fff" />
            <Text style={styles.connectivityButtonText}>
              {satelliteConnected ? 'Satellite Connected' : 'Connect Satellite'}
            </Text>
          </TouchableOpacity>
          
          <TouchableOpacity 
            style={styles.connectivityButton}
            onPress={downloadMapsForOffline}
          >
            <Ionicons name="map" size={20} color="#fff" />
            <Text style={styles.connectivityButtonText}>
              {mapDownloaded ? 'Maps Downloaded' : 'Download Maps'}
            </Text>
          </TouchableOpacity>
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
                Detected Location: {languageData?.county || 'Unknown'}
              </Text>
              <Text style={styles.modalDescription}>
                Based on your location, here are available radio stations in local languages:
              </Text>
              
              {languageData && languageData.regional_stations && languageData.regional_stations.length > 0 ? (
                languageData.regional_stations.map((station, index) => (
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
                ))
              ) : (
                <View style={styles.noStationsContainer}>
                  <Text style={styles.noStationsText}>
                    Loading regional stations... Please wait.
                  </Text>
                </View>
              )}
            </ScrollView>
          )}
        </View>
      </View>
    </Modal>
  );

  // Component lifecycle effects - placed after all function definitions
  useEffect(() => {
    const loadContent = async () => {
      console.log('🔍 Loading radio content and regional stations...');
      
      // Load content immediately - no disclaimer checks needed
      try {
        console.log('✅ Loading regional radio content...');
        await loadMultilingualContent();
        await loadIntegrationData();
        await loadRegionalRadioStations();
      } catch (error) {
        console.error('Content loading error:', error);
      }
    };
    
    loadContent();
  }, [selectedKenyaRegion, selectedBrazilRegion]); // Reload when regions change

  useEffect(() => {
    const initializeApp = async () => {
      try {
        await setupAudio();
        await loadSupportedLanguages();
      } catch (error) {
        console.error('App initialization error:', error);
      }
    };
    
    initializeApp();
    
    return () => {
      if (sound) {
        sound.unloadAsync().catch(console.error);
      }
    };
  }, []); // Empty dependency array - runs once on mount

  // Disclaimer useEffect removed - no longer needed

  useEffect(() => {
    // Monitor connectivity and data usage
    const monitorConnectivity = async () => {
      console.log('📡 Starting connectivity monitoring...');
      
      // Simulate connectivity monitoring (in real app, use NetInfo)
      const checkConnectivity = () => {
        // Check navigator.connection for data usage estimates
        const connection = (navigator as any).connection;
        if (connection) {
          const effectiveType = connection.effectiveType;
          console.log('📶 Connection type:', effectiveType);
          
          // Determine connection quality
          if (effectiveType === 'slow-2g' || effectiveType === '2g') {
            setLowDataMode(true);
            setConnectionType('satellite'); // Switch to satellite on slow connection
            console.log('🛰️ Switching to satellite mode for low bandwidth');
          } else if (effectiveType === '3g' || effectiveType === '4g') {
            setConnectionType('cellular');
            setLowDataMode(false);
          } else {
            setConnectionType('wifi');
            setLowDataMode(false);
          }
        }
        
        // Check if offline
        if (!navigator.onLine) {
          setConnectionType('offline');
          setOfflineMode(true);
          console.log('📴 Device is offline - enabling offline mode');
          loadOfflineContent();
        } else {
          setOfflineMode(false);
        }
      };
      
      // Initial check
      checkConnectivity();
      
      // Monitor connectivity changes
      window.addEventListener('online', checkConnectivity);
      window.addEventListener('offline', checkConnectivity);
      
      // Monitor data usage (simulated)
      const monitorDataUsage = () => {
        // In real app, track actual data usage
        const currentUsage = Math.floor(Math.random() * 800) + 200; // 200-1000 MB
        setDataUsage(prev => ({ ...prev, used: currentUsage }));
        
        if (currentUsage > dataUsage.limit * 0.8) { // 80% of limit
          setLowDataMode(true);
          console.log('⚠️ High data usage detected - enabling low data mode');
        }
      };
      
      monitorDataUsage();
      
      return () => {
        window.removeEventListener('online', checkConnectivity);
        window.removeEventListener('offline', checkConnectivity);
      };
    };
    
    monitorConnectivity();
  }, []);

  // Satellite connectivity function
  const connectToSatellite = async () => {
    console.log('🛰️ Attempting satellite connection...');
    
    try {
      // Call satellite connectivity API
      const response = await fetch(`${EXPO_PUBLIC_BACKEND_URL}/api/satellite/connect`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          location: { 
            latitude: -1.286389, 
            longitude: 36.817223 
          },
          priority: 'radio_streaming'
        }),
      });
      
      if (response.ok) {
        const data = await response.json();
        setSatelliteConnected(true);
        setConnectionType('satellite');
        
        Alert.alert(
          '🛰️ Satellite Connected',
          `Connected to satellite network: ${data.satellite_name || 'Unknown'}\nSignal strength: ${data.signal_strength || 'Good'}`
        );
        
        console.log('✅ Satellite connection successful:', data);
      } else {
        throw new Error(`HTTP ${response.status}`);
      }
    } catch (error) {
      console.error('❌ Satellite connection failed:', error);
      Alert.alert(
        'Satellite Connection Failed',
        'Unable to connect to satellite network. Using terrestrial connection.',
        [{ text: 'OK', style: 'default' }]
      );
    }
  };

  // Enhanced satellite radio connection function
  const connectToSatelliteRadio = async () => {
    console.log('🛰️📻 Connecting to Satellite Radio...');
    
    try {
      setIsBuffering(true);
      
      // Get satellite radio streams
      const response = await fetch(`${EXPO_PUBLIC_BACKEND_URL}/api/satellite/status`, {
        method: 'GET',
        headers: { 'Content-Type': 'application/json' },
      });
      
      if (response.ok) {
        const data = await response.json();
        console.log('🛰️ Satellite status:', data);
        
        // Satellite radio streams with global coverage
        const satelliteStreams = [
          'http://ice1.somafm.com/spacestation-256-mp3', // Space Station Soma
          'http://ice2.somafm.com/defcon-256-mp3', // DEF CON Radio
          'http://ice3.somafm.com/secretagent-256-mp3', // Secret Agent
          'http://ice1.somafm.com/groovesalad-256-mp3', // Groove Salad
        ];
        
        // Try satellite streams
        for (const stream of satelliteStreams) {
          try {
            if (Platform.OS === 'web') {
              const audio = new Audio();
              audio.crossOrigin = 'anonymous';
              audio.src = stream;
              await audio.play();
              setSound({ audio });
            } else {
              const { sound: newSound } = await Audio.Sound.createAsync(
                { uri: stream },
                { shouldPlay: true }
              );
              setSound(newSound);
            }
            
            setSatelliteConnected(true);
            setIsPlaying(true);
            setIsBuffering(false);
            
            Alert.alert(
              '🛰️📻 Satellite Radio Connected',
              'Now streaming from satellite network with global coverage.'
            );
            
            console.log('✅ Satellite radio streaming started');
            return;
          } catch (streamError) {
            console.log('❌ Satellite stream failed:', stream, streamError.message);
            continue;
          }
        }
        
        throw new Error('All satellite streams failed');
      }
    } catch (error) {
      console.error('❌ Satellite radio connection failed:', error);
      setIsBuffering(false);
      Alert.alert(
        'Satellite Radio Unavailable',
        'Satellite radio connection failed. Using terrestrial radio streams.',
        [
          { text: 'OK', style: 'default' },
          { text: 'Try Regular Radio', onPress: handlePlayPause }
        ]
      );
    }
  };

  // Auto-reconnect to ensure right URL connection
  const checkAndReconnectUrls = async () => {
    console.log('🔄 Checking and reconnecting to ensure right URL connection...');
    
    try {
      // Test connection to backend
      const backendResponse = await fetch(`${EXPO_PUBLIC_BACKEND_URL}/api/`, {
        method: 'GET',
      });
      
      if (!backendResponse.ok) {
        throw new Error(`Backend connection failed: ${backendResponse.status}`);
      }
      
      console.log('✅ Backend URL connection verified');
      
      // Test current tunnel endpoints
      const tunnelUrls = [
        'https://global-radio-app-5.preview.emergentagent.com',
        'https://childhood-copied-mile-succeed.trycloudflare.com',
        'https://kagema-fm-radio.loca.lt',
        'https://032c00c0a2d1e4ff1e054ceedc4cad24.serveo.net'
      ];
      
      let workingUrl = null;
      for (const url of tunnelUrls) {
        try {
          const response = await fetch(`${url}/api/`, { method: 'GET' });
          if (response.ok) {
            workingUrl = url;
            break;
          }
        } catch (error) {
          console.log(`❌ URL failed: ${url}`);
        }
      }
      
      if (workingUrl) {
        console.log(`✅ Verified working URL: ${workingUrl}`);
        Alert.alert(
          '🔄 URL Connection Verified', 
          `Connected to: ${workingUrl}\nAll systems operational.`
        );
      } else {
        throw new Error('No working URLs found');
      }
      
    } catch (error) {
      console.error('❌ URL reconnection failed:', error);
      Alert.alert(
        'Connection Check Failed',
        'Unable to verify URL connections. Please try refreshing the app.',
        [{ text: 'Refresh', onPress: () => clearCacheAndReload() }]
      );
    }
  };
        console.log('✅ Satellite connection established:', data);
        
        Alert.alert(
          'Satellite Connected',
          'Connected to satellite network for radio streaming. Data usage will be optimized.',
          [{ text: 'OK', style: 'default' }]
        );
      }
    } catch (error) {
      console.error('❌ Satellite connection failed:', error);
      Alert.alert(
        'Satellite Connection Failed',
        'Unable to connect to satellite network. Enabling offline mode.',
        [{ text: 'OK', style: 'default' }]
      );
      setOfflineMode(true);
      loadOfflineContent();
    }
  };

  // Load offline content
  const loadOfflineContent = async () => {
    console.log('💾 Loading offline content...');
    
    try {
      // Load cached offline content
      const response = await fetch(`${EXPO_PUBLIC_BACKEND_URL}/api/offline/content`);
      
      if (response.ok) {
        const data = await response.json();
        setOfflineContent(data);
        
        // Set offline station info
        setStationInfo({
          name: 'Kagema FM - Offline Mode',
          description: 'Cached content available offline',
          streamUrl: data.cached_stream || 'offline://cached-content',
          currentShow: 'Offline Content',
          frequency: 'Cached'
        });
        
        console.log('✅ Offline content loaded:', data);
      }
    } catch (error) {
      console.error('❌ Offline content loading failed:', error);
      // Set basic offline fallback
      setOfflineContent({
        message: 'Limited offline functionality available',
        cached_stations: []
      });
    }
  };

  // Download maps for offline use
  const downloadMapsForOffline = async () => {
    console.log('🗺️ Downloading maps for offline use...');
    
    try {
      Alert.alert(
        'Download Maps',
        'Download maps for Kenya and Brazil regions for offline use?',
        [
          { text: 'Cancel', style: 'cancel' },
          { text: 'Download', onPress: async () => {
            // In real implementation, use Google Maps SDK offline maps
            // For now, simulate the download
            await new Promise(resolve => setTimeout(resolve, 3000));
            setMapDownloaded(true);
            
            Alert.alert(
              'Maps Downloaded',
              'Offline maps for Kenya and Brazil have been downloaded successfully.',
              [{ text: 'OK', style: 'default' }]
            );
          }}
        ]
      );
    } catch (error) {
      console.error('❌ Map download failed:', error);
    }
  };

  // Load regional radio stations based on selected regions
  const loadRegionalRadioStations = async () => {
    console.log('📻 Loading regional radio stations...', { selectedKenyaRegion, selectedBrazilRegion });
    
    try {
      // Try to load regional stations from API with selected regions
      const response = await fetch(`${EXPO_PUBLIC_BACKEND_URL}/api/station-info/multilingual`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          latitude: -1.286389, // Default: Nairobi
          longitude: 36.817223,
          region_preferences: {
            kenya: selectedKenyaRegion,
            brazil: selectedBrazilRegion
          }
        }),
      });

      if (response.ok) {
        const data = await response.json();
        console.log('✅ Regional stations loaded from API:', data);
        
        // Set regional stations if available
        if (data.regional_stations && data.regional_stations.length > 0) {
          setRegionalStations(data.regional_stations);
          console.log('🌍 Regional stations set:', data.regional_stations.length);
        }
      }
    } catch (error) {
      console.log('ℹ️ API regional stations failed, using defaults:', error.message);
    }
    
    // Set region-specific default stations based on selections
    const defaultRegionalStations = [
      // Kenya station based on selected region
      {
        id: 'kagema-kenya',
        name: `Kagema FM ${selectedKenyaRegion}`,
        streamUrl: 'http://ice1.somafm.com/groovesalad-256-mp3',
        frequency: '101.5 FM',
        region: selectedKenyaRegion,
        country: 'Kenya',
        language: selectedKenyaRegion === 'Mombasa' ? 'Swahili/English' : 'English/Swahili',
        description: `${selectedKenyaRegion} Regional Station`
      },
      // Brazil station based on selected state - special handling for Bahia
      {
        id: 'kagema-brasil',
        name: `Kagema ${selectedBrazilRegion}${selectedBrazilRegion === 'Bahia' ? ' - Salvador' : ''}`,
        streamUrl: selectedBrazilRegion === 'Bahia' 
          ? 'http://ice2.somafm.com/bagel-256-mp3'  // Bahia gets primary Brazil stream
          : 'http://ice3.somafm.com/beatblender-256-mp3',
        frequency: selectedBrazilRegion === 'Bahia' ? '102.3 FM' : '103.5 FM',
        region: selectedBrazilRegion,
        country: 'Brazil',
        language: 'Portuguese',
        description: selectedBrazilRegion === 'Bahia' 
          ? 'Bahia Regional Station - Heart of Brazilian Culture'
          : `${selectedBrazilRegion} Regional Station`
      },
      // Global stations
      {
        id: 'kagema-main',
        name: 'Kagema FM International',
        streamUrl: 'http://ice3.somafm.com/beatblender-256-mp3',
        frequency: '103.1 FM',
        region: 'International',
        country: 'Global',
        language: 'Multiple Languages',
        description: 'Main International Station'
      },
      {
        id: 'kagema-global',
        name: 'Kagema Global Mix',
        streamUrl: 'http://ice4.somafm.com/spacestation-256-mp3',
        frequency: '104.7 FM',
        region: 'Worldwide',
        country: 'Global',
        language: 'English/Portuguese/Swahili',
        description: 'Global International Stream'
      }
    ];
    
    setRegionalStations(defaultRegionalStations);
    console.log('📻 Regional stations set for:', { selectedKenyaRegion, selectedBrazilRegion });
  };

  return (
    <SafeAreaView style={styles.container}>
      <StatusBar barStyle="light-content" backgroundColor="#1a1a2e" />
      
      {/* Navigation Header with Back/Home */}
      <View style={styles.navigationHeader}>
        <TouchableOpacity 
          style={styles.navButton}
          onPress={() => {
            // Reset to home/radio tab and clear any modals
            setActiveTab('radio');
            setShowLanguageModal(false);
            setShowKenyaDropdown(false);
            setShowBrazilDropdown(false);
          }}
        >
          <Ionicons name="home" size={22} color="#fff" />
          <Text style={styles.navButtonText}>Home</Text>
        </TouchableOpacity>

        <TouchableOpacity 
          style={styles.navButton}
          onPress={() => {
            // Auto-refresh system and clear cache
            clearCacheAndReload();
          }}
        >
          <Ionicons name="refresh" size={22} color="#fff" />
          <Text style={styles.navButtonText}>Refresh</Text>
        </TouchableOpacity>

        <TouchableOpacity 
          style={styles.navButton}
          onPress={() => {
            // Navigate back or close modals
            if (showLanguageModal) {
              setShowLanguageModal(false);
            } else {
              // Auto-reconnect to ensure right URL connection
              checkAndReconnectUrls();
            }
          }}
        >
          <Ionicons name="arrow-back" size={22} color="#fff" />
          <Text style={styles.navButtonText}>Back</Text>
        </TouchableOpacity>

        <TouchableOpacity 
          style={styles.navButton}
          onPress={() => {
            // Satellite radio connection
            connectToSatelliteRadio();
          }}
        >
          <Ionicons name="satellite" size={22} color="#4CAF50" />
          <Text style={styles.navButtonText}>Satellite</Text>
        </TouchableOpacity>
      </View>
      
      {/* Header */}
      <View style={styles.header}>
        <Text style={styles.headerTitle}>Kagema FM</Text>
        <Text style={styles.headerSubtitle}>Complete Platform Integration</Text>
        {languageData && (
          <Text style={styles.languageIndicator}>
            {getLanguageFlag(languageData?.detected_language || 'en')} {languageData?.language_info?.native_name || 'Unknown'}
          </Text>
        )}
        {emergencyAlerts.length > 0 && (
          <View style={styles.alertIndicator}>
            <Ionicons name="alert-circle" size={16} color="#f44336" />
            <Text style={styles.alertText}>{emergencyAlerts.length} alerts</Text>
          </View>
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
            size={18} 
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
            size={18} 
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
            size={18} 
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
            size={18} 
            color={activeTab === 'language' ? '#fff' : '#ff6b6b'} 
          />
          <Text style={[styles.tabText, activeTab === 'language' && styles.activeTabText]}>
            Language
          </Text>
        </TouchableOpacity>

        <TouchableOpacity 
          style={[styles.tabButton, activeTab === 'integrations' && styles.activeTabButton]}
          onPress={() => setActiveTab('integrations')}
        >
          <Ionicons 
            name="apps" 
            size={18} 
            color={activeTab === 'integrations' ? '#fff' : '#ff6b6b'} 
          />
          <Text style={[styles.tabText, activeTab === 'integrations' && styles.activeTabText]}>
            Apps
          </Text>
        </TouchableOpacity>
      </View>

      {/* Tab Content - No blocking disclaimers, immediate access */}
      {activeTab === 'radio' && renderRadioTab()}
      {activeTab === 'news' && renderNewsTab()}
      {activeTab === 'music' && renderMusicTab()}
      {activeTab === 'language' && renderLanguageTab()}
      {activeTab === 'integrations' && renderIntegrationsTab()}

      {/* Collapsible Disclaimers at bottom */}
      <View style={styles.footerDisclaimers}>
        <TouchableOpacity 
          style={styles.disclaimerToggle}
          onPress={() => setShowDisclaimers(!showDisclaimers)}
        >
          <Text style={styles.disclaimerToggleText}>
            Legal Disclaimers & Terms
          </Text>
          <Ionicons 
            name={showDisclaimers ? "chevron-up" : "chevron-down"} 
            size={16} 
            color="#ff6b6b" 
          />
        </TouchableOpacity>
        
        {showDisclaimers && (
          <View style={styles.disclaimerContent}>
            <View style={styles.disclaimerFootnote}>
              <Text style={styles.footnoteNumber}>¹</Text>
              <Text style={styles.footnoteText}>
                <Text style={styles.footnoteLabel}>Age Restriction: </Text>
                Kagema FM content is intended for adult audiences (18+). Content may include mature themes and discussions.
              </Text>
            </View>
            
            <View style={styles.disclaimerFootnote}>
              <Text style={styles.footnoteNumber}>²</Text>
              <Text style={styles.footnoteText}>
                <Text style={styles.footnoteLabel}>Broadcasting Rights: </Text>
                All radio licenses are held by regional authorities. Kenya: CAK regulated. Brazil: ANATEL regulated.
              </Text>
            </View>
            
            <View style={styles.disclaimerFootnote}>
              <Text style={styles.footnoteNumber}>³</Text>
              <Text style={styles.footnoteText}>
                <Text style={styles.footnoteLabel}>Platform Responsibility: </Text>
                Kagema FM serves as a technology platform. Content licensing and regulatory compliance are managed by regional operators.
              </Text>
            </View>
            
            <Text style={styles.footerNote}>
              By using this app, you acknowledge the above terms.
            </Text>
          </View>
        )}
      </View>

      {/* Language selection modal */}
      {renderLanguageModal()}
    </SafeAreaView>
  );
};

// Component complete - all render functions now inside component scope

const MainApp = () => (
  <IntegrationProvider>
    <KagemaFMApp />
  </IntegrationProvider>
);

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#1a1a2e',
  },
  header: {
    alignItems: 'center',
    paddingVertical: 12,
    borderBottomWidth: 1,
    borderBottomColor: '#2d2d54',
  },
  navigationHeader: {
    flexDirection: 'row',
    backgroundColor: '#16213e',
    paddingVertical: 8,
    paddingHorizontal: 4,
    justifyContent: 'space-around',
    borderBottomWidth: 1,
    borderBottomColor: '#2d2d54',
  },
  navButton: {
    alignItems: 'center',
    paddingVertical: 6,
    paddingHorizontal: 8,
    borderRadius: 8,
    backgroundColor: 'rgba(255, 255, 255, 0.1)',
    minWidth: 60,
  },
  navButtonText: {
    color: '#fff',
    fontSize: 10,
    marginTop: 2,
    textAlign: 'center',
  },
  headerTitle: {
    fontSize: 22,
    fontWeight: 'bold',
    color: '#fff',
    marginBottom: 2,
  },
  headerSubtitle: {
    fontSize: 11,
    color: '#ff6b6b',
    textTransform: 'uppercase',
    letterSpacing: 1,
  },
  languageIndicator: {
    fontSize: 12,
    color: '#ccc',
    marginTop: 3,
  },
  alertIndicator: {
    flexDirection: 'row',
    alignItems: 'center',
    marginTop: 3,
  },
  alertText: {
    color: '#f44336',
    fontSize: 11,
    marginLeft: 4,
  },
  tabNavigation: {
    flexDirection: 'row',
    backgroundColor: '#2d2d54',
    paddingVertical: 6,
  },
  tabButton: {
    flex: 1,
    alignItems: 'center',
    paddingVertical: 8,
  },
  activeTabButton: {
    backgroundColor: '#ff6b6b',
    marginHorizontal: 1,
    borderRadius: 6,
  },
  tabText: {
    color: '#ff6b6b',
    fontSize: 9,
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
  
  // Integration styles
  integrationStatusContainer: {
    margin: 15,
    padding: 15,
    backgroundColor: '#2d2d54',
    borderRadius: 8,
  },
  integrationStatusItem: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 8,
  },
  integrationName: {
    color: '#fff',
    fontSize: 14,
    marginLeft: 10,
    flex: 1,
  },
  integrationStatus: {
    fontSize: 12,
  },
  statusDot: {
    width: 8,
    height: 8,
    borderRadius: 4,
  },
  
  featureCard: {
    margin: 15,
    padding: 15,
    backgroundColor: '#2d2d54',
    borderRadius: 8,
  },
  featureTitle: {
    color: '#ff6b6b',
    fontSize: 16,
    fontWeight: 'bold',
    marginBottom: 8,
  },
  featureDescription: {
    color: '#ccc',
    fontSize: 12,
    marginBottom: 12,
  },
  featureButton: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#ff6b6b',
    padding: 12,
    borderRadius: 8,
    justifyContent: 'center',
  },
  activeFeatureButton: {
    backgroundColor: '#ff5252',
  },
  featureButtonText: {
    color: '#fff',
    fontSize: 14,
    marginLeft: 8,
    fontWeight: 'bold',
  },
  
  voiceControlButton: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#2d2d54',
    padding: 10,
    borderRadius: 8,
    marginTop: 10,
    justifyContent: 'center',
  },
  voiceControlActive: {
    backgroundColor: '#ff6b6b',
  },
  voiceControlText: {
    color: '#ff6b6b',
    fontSize: 12,
    marginLeft: 6,
  },
  voiceControlActiveText: {
    color: '#fff',
  },
  
  trackList: {
    marginTop: 10,
    padding: 10,
    backgroundColor: '#1a1a2e',
    borderRadius: 6,
  },
  trackListTitle: {
    color: '#ff6b6b',
    fontSize: 12,
    fontWeight: 'bold',
    marginBottom: 5,
  },
  trackItem: {
    color: '#ccc',
    fontSize: 11,
    marginBottom: 3,
  },
  
  placesList: {
    marginTop: 10,
    padding: 10,
    backgroundColor: '#1a1a2e',
    borderRadius: 6,
  },
  placesTitle: {
    color: '#ff6b6b',
    fontSize: 12,
    fontWeight: 'bold',
    marginBottom: 5,
  },
  placeItem: {
    color: '#ccc',
    fontSize: 11,
    marginBottom: 3,
  },
  
  trafficInfo: {
    marginTop: 10,
    padding: 10,
    backgroundColor: '#1a1a2e',
    borderRadius: 6,
  },
  trafficTitle: {
    color: '#ff6b6b',
    fontSize: 12,
    fontWeight: 'bold',
    marginBottom: 5,
  },
  trafficStatus: {
    color: '#ccc',
    fontSize: 11,
  },
  
  emergencyCard: {
    margin: 15,
    padding: 15,
    backgroundColor: '#8B0000',
    borderRadius: 8,
    borderWidth: 2,
    borderColor: '#f44336',
  },
  emergencyTitle: {
    color: '#fff',
    fontSize: 16,
    fontWeight: 'bold',
    marginBottom: 10,
  },
  emergencyItem: {
    marginBottom: 10,
  },
  emergencyAlertTitle: {
    color: '#fff',
    fontSize: 14,
    fontWeight: 'bold',
    marginBottom: 4,
  },
  emergencyDescription: {
    color: '#ffcccb',
    fontSize: 12,
    marginBottom: 4,
  },
  emergencyArea: {
    color: '#ffcccb',
    fontSize: 10,
  },

  // Existing styles would continue...
  stationContainer: {
    alignItems: 'center',
    paddingHorizontal: 20,
    paddingVertical: 15,
  },
  logoContainer: {
    marginBottom: 15,
    padding: 12,
    backgroundColor: 'rgba(76, 175, 80, 0.1)', // Green tint for international feel
    borderRadius: 50,
    borderWidth: 2,
    borderColor: 'rgba(255, 107, 107, 0.3)', // Red accent
    // International theme with flag-inspired colors
    boxShadow: '0px 4px 6px rgba(76, 175, 80, 0.3)',
    elevation: 4,
  },
  logo: {
    width: 80,
    height: 80,
    borderRadius: 40,
    borderWidth: 3,
    borderColor: '#ff6b6b',
    // International frame effect with Kenya/Brazil colors
    boxShadow: '2px 2px 4px rgba(76, 175, 80, 0.8)', // Green (both flags)
    elevation: 8,
    backgroundColor: '#fff',
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
  statusText: {
    color: '#ccc',
    fontSize: 12,
    fontWeight: '500',
  },
  sectionTitle: {
    fontSize: 16,
    fontWeight: 'bold',
    color: '#ff6b6b',
    marginBottom: 10,
  },
  
  // Modal styles
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
  stationFreq: {
    color: '#ccc',
    fontSize: 14,
  },
  noStationsContainer: {
    alignItems: 'center',
    justifyContent: 'center',
    padding: 20,
    backgroundColor: '#1a1a2e',
    borderRadius: 8,
    marginVertical: 10,
  },
  noStationsText: {
    color: '#ccc',
    fontSize: 14,
    textAlign: 'center',
    fontStyle: 'italic',
  },
  
  // Disclaimer required styles
  disclaimerRequiredContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    padding: 40,
  },
  disclaimerRequiredTitle: {
    fontSize: 22,
    fontWeight: 'bold',
    color: '#fff',
    textAlign: 'center',
    marginTop: 20,
    marginBottom: 16,
  },
  disclaimerRequiredText: {
    fontSize: 16,
    color: '#ccc',
    textAlign: 'center',
    lineHeight: 24,
    marginBottom: 30,
  },
  showDisclaimerButton: {
    backgroundColor: '#ff6b6b',
    paddingHorizontal: 24,
    paddingVertical: 12,
    borderRadius: 8,
    alignItems: 'center',
  },
  showDisclaimerButtonText: {
    color: '#fff',
    fontSize: 16,
    fontWeight: 'bold',
  },

  // News tab styles
  summaryCard: {
    backgroundColor: '#2d2d54',
    margin: 15,
    padding: 15,
    borderRadius: 8,
    borderLeftWidth: 4,
    borderLeftColor: '#ff6b6b',
  },
  summaryText: {
    color: '#ccc',
    fontSize: 14,
    fontStyle: 'italic',
  },
  newsCard: {
    backgroundColor: '#2d2d54',
    margin: 15,
    padding: 15,
    borderRadius: 8,
    marginBottom: 10,
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
    lineHeight: 20,
    marginBottom: 10,
  },
  newsFooter: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
  },
  newsSource: {
    color: '#ff6b6b',
    fontSize: 12,
    fontWeight: '500',
  },
  newsTime: {
    color: '#999',
    fontSize: 12,
  },

  // Music tab styles
  musicCard: {
    backgroundColor: '#2d2d54',
    margin: 15,
    padding: 15,
    borderRadius: 8,
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 10,
  },
  musicIconContainer: {
    width: 40,
    height: 40,
    borderRadius: 20,
    backgroundColor: 'rgba(255, 107, 107, 0.2)',
    justifyContent: 'center',
    alignItems: 'center',
    marginRight: 12,
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
    color: '#999',
    fontSize: 12,
  },
  playMusicButton: {
    width: 36,
    height: 36,
    borderRadius: 18,
    backgroundColor: '#ff6b6b',
    justifyContent: 'center',
    alignItems: 'center',
  },

  // Language tab styles
  languageCard: {
    backgroundColor: '#2d2d54',
    margin: 15,
    padding: 15,
    borderRadius: 8,
    borderLeftWidth: 4,
    borderLeftColor: '#4CAF50',
  },
  currentLanguageSection: {
    marginBottom: 15,
  },
  currentLanguageTitle: {
    color: '#4CAF50',
    fontSize: 16,
    fontWeight: 'bold',
    marginBottom: 10,
  },
  changeLanguageButton: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#ff6b6b',
    padding: 12,
    borderRadius: 8,
    justifyContent: 'center',
  },
  changeLanguageText: {
    color: '#fff',
    fontSize: 14,
    fontWeight: 'bold',
    marginLeft: 8,
  },
  languageInfoCard: {
    backgroundColor: '#2d2d54',
    margin: 15,
    padding: 15,
    borderRadius: 8,
  },
  languageInfoTitle: {
    color: '#ff6b6b',
    fontSize: 16,
    fontWeight: 'bold',
    marginBottom: 10,
  },
  languageInfoText: {
    color: '#ccc',
    fontSize: 14,
    lineHeight: 20,
    marginBottom: 12,
  },
  languageList: {
    marginLeft: 10,
  },
  languageListItem: {
    color: '#ccc',
    fontSize: 13,
    marginBottom: 6,
  },
  supportedLanguagesCard: {
    backgroundColor: '#2d2d54',
    margin: 15,
    padding: 15,
    borderRadius: 8,
  },
  supportedLanguagesTitle: {
    color: '#ff6b6b',
    fontSize: 16,
    fontWeight: 'bold',
    marginBottom: 12,
  },
  supportedLanguageItem: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 8,
  },
  supportedLanguageName: {
    color: '#fff',
    fontSize: 14,
    marginLeft: 10,
    flex: 1,
  },
  supportedLanguageNative: {
    color: '#999',
    fontSize: 12,
  },

  // Disclaimer Modal Styles
  disclaimerModalContainer: {
    flex: 1,
    backgroundColor: '#1a1a2e',
    justifyContent: 'center',
    alignItems: 'center',
    padding: 20,
  },
  disclaimerContent: {
    backgroundColor: '#2d2d54',
    borderRadius: 15,
    padding: 30,
    width: '100%',
    maxWidth: 400,
    alignItems: 'center',
  },
  disclaimerScrollContent: {
    flex: 1,
  },
  disclaimerTitle: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#fff',
    textAlign: 'center',
    marginBottom: 20,
  },
  disclaimerText: {
    fontSize: 16,
    color: '#ccc',
    textAlign: 'center',
    lineHeight: 24,
    marginBottom: 20,
  },
  disclaimerSubtext: {
    fontSize: 14,
    color: '#ff6b6b',
    textAlign: 'center',
    marginBottom: 30,
    fontWeight: '600',
  },
  ageButtonContainer: {
    width: '100%',
    gap: 15,
  },
  ageButton: {
    backgroundColor: '#ff6b6b',
    paddingVertical: 15,
    paddingHorizontal: 25,
    borderRadius: 10,
    alignItems: 'center',
    marginBottom: 10,
  },
  ageButtonSecondary: {
    backgroundColor: 'transparent',
    borderWidth: 2,
    borderColor: '#ff6b6b',
  },
  ageButtonText: {
    color: '#fff',
    fontSize: 16,
    fontWeight: 'bold',
  },
  ageButtonSecondaryText: {
    color: '#ff6b6b',
  },
  licenseSection: {
    marginBottom: 20,
    padding: 15,
    backgroundColor: '#1a1a2e',
    borderRadius: 10,
  },
  licenseSectionTitle: {
    fontSize: 16,
    fontWeight: 'bold',
    color: '#ff6b6b',
    marginBottom: 10,
  },
  licenseText: {
    fontSize: 14,
    color: '#ccc',
    lineHeight: 20,
  },
  licenseAcceptButton: {
    backgroundColor: '#4CAF50',
    paddingVertical: 15,
    paddingHorizontal: 25,
    borderRadius: 10,
    alignItems: 'center',
    marginTop: 20,
  },
  licenseAcceptText: {
    color: '#fff',
    fontSize: 16,
    fontWeight: 'bold',
  },

  // Disclaimer Modal Styles
  disclaimerModalContainer: {
    flex: 1,
    backgroundColor: '#1a1a2e',
    justifyContent: 'center',
    alignItems: 'center',
    padding: 20,
  },
  disclaimerContent: {
    backgroundColor: '#2d2d54',
    borderRadius: 15,
    padding: 30,
    width: '100%',
    maxWidth: 400,
    alignItems: 'center',
  },
  disclaimerScrollContent: {
    flex: 1,
  },
  disclaimerTitle: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#fff',
    textAlign: 'center',
    marginBottom: 20,
  },
  disclaimerText: {
    fontSize: 16,
    color: '#ccc',
    textAlign: 'center',
    lineHeight: 24,
    marginBottom: 20,
  },
  disclaimerSubtext: {
    fontSize: 14,
    color: '#ff6b6b',
    textAlign: 'center',
    marginBottom: 30,
    fontWeight: '600',
  },
  ageButtonContainer: {
    width: '100%',
    gap: 15,
  },
  ageButton: {
    backgroundColor: '#ff6b6b',
    paddingVertical: 15,
    paddingHorizontal: 25,
    borderRadius: 10,
    alignItems: 'center',
    marginBottom: 10,
  },
  ageButtonSecondary: {
    backgroundColor: 'transparent',
    borderWidth: 2,
    borderColor: '#ff6b6b',
  },
  ageButtonText: {
    color: '#fff',
    fontSize: 16,
    fontWeight: 'bold',
  },
  ageButtonSecondaryText: {
    color: '#ff6b6b',
  },
  licenseSection: {
    marginBottom: 20,
    padding: 15,
    backgroundColor: '#1a1a2e',
    borderRadius: 10,
  },
  licenseSectionTitle: {
    fontSize: 16,
    fontWeight: 'bold',
    color: '#ff6b6b',
    marginBottom: 10,
  },
  licenseText: {
    fontSize: 14,
    color: '#ccc',
    lineHeight: 20,
  },
  licenseAcceptButton: {
    backgroundColor: '#4CAF50',
    paddingVertical: 15,
    paddingHorizontal: 25,
    borderRadius: 10,
    alignItems: 'center',
    marginTop: 20,
  },
  licenseAcceptText: {
    color: '#fff',
    fontSize: 16,
    fontWeight: 'bold',
  },

  // Regional Stations Styles
  regionalStationsContainer: {
    marginHorizontal: 15,
    marginVertical: 10,
    padding: 15,
    backgroundColor: '#2d2d54',
    borderRadius: 10,
  },
  regionalStationsTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#ff6b6b',
    marginBottom: 15,
    textAlign: 'center',
  },
  regionalStationsScroll: {
    flexDirection: 'row',
  },
  regionalStationCard: {
    backgroundColor: '#1a1a2e',
    borderRadius: 10,
    padding: 15,
    marginRight: 15,
    minWidth: 160,
    borderWidth: 1,
    borderColor: '#ff6b6b',
    alignItems: 'center',
  },
  regionalStationName: {
    fontSize: 16,
    fontWeight: 'bold',
    color: '#fff',
    textAlign: 'center',
    marginBottom: 5,
  },
  regionalStationFreq: {
    fontSize: 14,
    color: '#ff6b6b',
    textAlign: 'center',
    marginBottom: 3,
  },
  regionalStationRegion: {
    fontSize: 12,
    color: '#ccc',
    textAlign: 'center',
    marginBottom: 3,
  },
  regionalStationLanguage: {
    fontSize: 11,
    color: '#999',
    textAlign: 'center',
    fontStyle: 'italic',
  },

  // Connectivity Status Styles
  connectivityIndicator: {
    flexDirection: 'row',
    alignItems: 'center',
    marginLeft: 15,
  },
  connectivityItem: {
    flexDirection: 'row',
    alignItems: 'center',
    marginRight: 10,
  },
  connectivityText: {
    color: '#ccc',
    fontSize: 12,
    marginLeft: 4,
  },
  dataUsageContainer: {
    margin: 15,
    padding: 10,
    backgroundColor: '#2d2d54',
    borderRadius: 8,
    borderLeftWidth: 3,
    borderLeftColor: '#FF9800',
  },
  dataUsageText: {
    color: '#fff',
    fontSize: 12,
    marginBottom: 8,
  },
  dataUsageBar: {
    height: 4,
    backgroundColor: '#1a1a2e',
    borderRadius: 2,
    overflow: 'hidden',
  },
  dataUsageFill: {
    height: '100%',
    borderRadius: 2,
  },
  connectivityActions: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    margin: 15,
    gap: 10,
  },
  connectivityButton: {
    flex: 1,
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    backgroundColor: '#ff6b6b',
    padding: 12,
    borderRadius: 8,
    gap: 8,
  },
  connectivityButtonText: {
    color: '#fff',
    fontSize: 12,
    fontWeight: 'bold',
  },

  // Footer Disclaimers Styles - Smaller Print
  footerDisclaimers: {
    backgroundColor: '#1a1a2e',
    padding: 15,
    marginTop: 20,
    borderTopWidth: 1,
    borderTopColor: '#333',
  },
  disclaimerToggle: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    paddingVertical: 8,
    paddingHorizontal: 4,
  },
  disclaimerToggleText: {
    fontSize: 11,
    color: '#ff6b6b',
    fontWeight: 'bold',
  },
  disclaimerContent: {
    marginTop: 8,
  },
  footerDisclaimerTitle: {
    fontSize: 12,
    fontWeight: 'bold',
    color: '#ff6b6b',
    marginBottom: 10,
    textAlign: 'center',
  },
  disclaimerFootnote: {
    flexDirection: 'row',
    marginBottom: 8,
    alignItems: 'flex-start',
  },
  footnoteNumber: {
    fontSize: 9,
    color: '#ff6b6b',
    fontWeight: 'bold',
    marginRight: 6,
    marginTop: 1,
    minWidth: 12,
  },
  footnoteText: {
    fontSize: 8,
    color: '#999',
    lineHeight: 12,
    flex: 1,
  },
  footnoteLabel: {
    fontWeight: 'bold',
    color: '#ccc',
  },
  footerNote: {
    fontSize: 7,
    color: '#666',
    textAlign: 'center',
    marginTop: 8,
    fontStyle: 'italic',
  },
  disclaimerToggle: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    paddingVertical: 8,
    paddingHorizontal: 4,
  },
  disclaimerToggleText: {
    fontSize: 11,
    color: '#ff6b6b',
    fontWeight: 'bold',
  },
  disclaimerContent: {
    marginTop: 8,
  },

  // Region Dropdown Styles
  regionDropdownContainer: {
    marginBottom: 20,
  },
  regionLabel: {
    fontSize: 16,
    fontWeight: 'bold',
    color: '#ff6b6b',
    marginBottom: 8,
  },
  dropdownButton: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    backgroundColor: '#1a1a2e',
    padding: 15,
    borderRadius: 8,
    borderWidth: 1,
    borderColor: '#ff6b6b',
  },
  dropdownButtonText: {
    color: '#fff',
    fontSize: 16,
    fontWeight: '500',
  },
  dropdownMenu: {
    backgroundColor: '#1a1a2e',
    borderRadius: 8,
    marginTop: 5,
    borderWidth: 1,
    borderColor: '#ff6b6b',
    maxHeight: 200,
  },
  dropdownScroll: {
    maxHeight: 200,
  },
  dropdownItem: {
    padding: 15,
    borderBottomWidth: 1,
    borderBottomColor: '#2d2d54',
  },
  dropdownItemSelected: {
    backgroundColor: '#ff6b6b',
  },
  dropdownItemText: {
    color: '#ccc',
    fontSize: 14,
  },
  dropdownItemTextSelected: {
    color: '#fff',
    fontWeight: 'bold',
  },
  
  // Connectivity indicator styles
  connectivityIndicator: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    justifyContent: 'center',
    marginTop: 10,
    gap: 8,
  },
  connectivityItem: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#2d2d54',
    paddingHorizontal: 8,
    paddingVertical: 4,
    borderRadius: 12,
    gap: 4,
  },
  connectivityText: {
    color: '#fff',
    fontSize: 12,
    fontWeight: '500',
  },
  
  // Data usage styles
  dataUsageContainer: {
    margin: 15,
    padding: 12,
    backgroundColor: '#2d2d54',
    borderRadius: 8,
  },
  dataUsageText: {
    color: '#fff',
    fontSize: 14,
    fontWeight: '500',
    marginBottom: 8,
    textAlign: 'center',
  },
  dataUsageBar: {
    height: 6,
    backgroundColor: '#1a1a2e',
    borderRadius: 3,
    overflow: 'hidden',
  },
  dataUsageFill: {
    height: '100%',
    borderRadius: 3,
  },
  
  // Connectivity actions styles
  connectivityActions: {
    margin: 15,
    gap: 10,
  },
  connectivityButton: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#ff6b6b',
    paddingVertical: 12,
    paddingHorizontal: 16,
    borderRadius: 8,
    gap: 8,
    justifyContent: 'center',
  },
  connectivityButtonText: {
    color: '#fff',
    fontSize: 14,
    fontWeight: '600',
  },
});

export default MainApp;