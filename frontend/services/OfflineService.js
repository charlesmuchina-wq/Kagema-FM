import AsyncStorage from '@react-native-async-storage/async-storage';
import NetInfo from '@react-native-netinfo/netinfo';
import { Platform, Alert } from 'react-native';
import { Audio } from 'expo-audio';

const EXPO_PUBLIC_BACKEND_URL = process.env.EXPO_PUBLIC_BACKEND_URL;

class OfflineService {
  constructor() {
    this.isOfflineMode = false;
    this.connectionType = 'unknown';
    this.connectionQuality = 'unknown';
    this.satelliteProviders = [
      'Starlink',
      'OneWeb', 
      'Iridium',
      'Open Satellite Network',
      'GlobalSat Free'
    ];
    this.cachedContent = new Map();
    this.setupNetworkMonitoring();
  }

  async setupNetworkMonitoring() {
    try {
      // Monitor network state changes
      NetInfo.addEventListener(state => {
        this.handleNetworkStateChange(state);
      });

      // Get initial network state
      const initialState = await NetInfo.fetch();
      this.handleNetworkStateChange(initialState);
    } catch (error) {
      console.error('Network monitoring setup error:', error);
    }
  }

  handleNetworkStateChange(state) {
    const wasOffline = !this.isConnected();
    
    this.connectionType = state.type;
    this.connectionQuality = this.assessConnectionQuality(state);
    
    console.log(`Network state changed: ${state.type}, Connected: ${state.isConnected}, Quality: ${this.connectionQuality}`);
    
    // If connection was lost, try satellite backup
    if (state.isConnected === false || this.connectionQuality === 'poor') {
      this.attemptSatelliteConnection();
    }
    
    // If we regained connection from offline
    if (wasOffline && state.isConnected) {
      this.syncCachedData();
    }
  }

  assessConnectionQuality(state) {
    if (!state.isConnected) return 'offline';
    
    // Assess quality based on connection details
    if (state.details) {
      const { strength, frequency } = state.details;
      
      if (strength && strength > 80) return 'excellent';
      if (strength && strength > 50) return 'good';
      if (strength && strength > 20) return 'poor';
    }
    
    // Default assessment based on type
    switch (state.type) {
      case 'wifi':
        return 'good';
      case 'cellular':
        return 'fair';
      case 'satellite':
        return 'fair';
      default:
        return 'unknown';
    }
  }

  async attemptSatelliteConnection() {
    try {
      console.log('Attempting satellite connection...');
      
      // Check for satellite connectivity APIs
      const satelliteStatus = await this.checkSatelliteProviders();
      
      if (satelliteStatus.available) {
        console.log(`Satellite connection available via ${satelliteStatus.provider}`);
        
        // Attempt to establish satellite connection
        const connected = await this.connectToSatellite(satelliteStatus.provider);
        
        if (connected) {
          Alert.alert(
            'Satellite Connected', 
            `Connected to ${satelliteStatus.provider} satellite internet. Radio streaming is available.`,
            [{ text: 'OK' }]
          );
          return true;
        }
      }
      
      // If no satellite available, enable offline mode
      await this.enableOfflineMode();
      return false;
      
    } catch (error) {
      console.error('Satellite connection attempt failed:', error);
      await this.enableOfflineMode();
      return false;
    }
  }

  async checkSatelliteProviders() {
    try {
      // Check backend for satellite provider status
      const response = await fetch(`${EXPO_PUBLIC_BACKEND_URL}/api/satellite/status`, {
        method: 'GET',
        timeout: 5000
      });
      
      if (response.ok) {
        const data = await response.json();
        return {
          available: data.available || false,
          provider: data.provider || 'Unknown',
          signal_strength: data.signal_strength || 0,
          estimated_speed: data.estimated_speed || 0
        };
      }
      
      // Mock satellite availability for demo
      return {
        available: Math.random() > 0.5, // 50% chance of satellite availability
        provider: 'Open Satellite Network',
        signal_strength: Math.floor(Math.random() * 100),
        estimated_speed: Math.floor(Math.random() * 10) + 1
      };
      
    } catch (error) {
      console.error('Satellite provider check failed:', error);
      return { available: false };
    }
  }

  async connectToSatellite(provider) {
    try {
      console.log(`Attempting connection to ${provider}...`);
      
      // Simulate satellite connection process
      const connectionAttempt = await fetch(`${EXPO_PUBLIC_BACKEND_URL}/api/satellite/connect`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          provider: provider,
          client_id: 'kagema_fm_mobile',
          location: 'auto'
        }),
        timeout: 30000
      });
      
      if (connectionAttempt.ok) {
        const result = await connectionAttempt.json();
        return result.connected || false;
      }
      
      return false;
    } catch (error) {
      console.error(`Satellite connection to ${provider} failed:`, error);
      return false;
    }
  }

  async enableOfflineMode() {
    try {
      this.isOfflineMode = true;
      await AsyncStorage.setItem('offlineMode', 'true');
      
      console.log('Offline mode enabled');
      
      // Notify user about offline mode
      Alert.alert(
        'Offline Mode Activated',
        'No internet connection available. Using cached content. Some features may be limited.',
        [
          { text: 'OK' },
          { text: 'Try Satellite', onPress: () => this.attemptSatelliteConnection() }
        ]
      );
      
      // Load cached content
      await this.loadCachedContent();
      
    } catch (error) {
      console.error('Offline mode activation error:', error);
    }
  }

  async disableOfflineMode() {
    try {
      this.isOfflineMode = false;
      await AsyncStorage.setItem('offlineMode', 'false');
      console.log('Offline mode disabled');
    } catch (error) {
      console.error('Offline mode deactivation error:', error);
    }
  }

  isConnected() {
    return this.connectionType !== 'none' && this.connectionType !== 'unknown' && !this.isOfflineMode;
  }

  getConnectionQuality() {
    return this.connectionQuality;
  }

  getConnectionType() {
    return this.connectionType;
  }

  // Cache Management
  async cacheRadioStations(stations) {
    try {
      const cacheData = {
        stations: stations,
        cachedAt: new Date().toISOString(),
        expiresAt: new Date(Date.now() + 24 * 60 * 60 * 1000).toISOString() // 24 hours
      };
      
      await AsyncStorage.setItem('cached_radio_stations', JSON.stringify(cacheData));
      this.cachedContent.set('radio_stations', cacheData);
      
      console.log(`Cached ${stations.length} radio stations`);
    } catch (error) {
      console.error('Radio stations caching error:', error);
    }
  }

  async cacheNewsArticles(articles) {
    try {
      const cacheData = {
        articles: articles,
        cachedAt: new Date().toISOString(),
        expiresAt: new Date(Date.now() + 6 * 60 * 60 * 1000).toISOString() // 6 hours
      };
      
      await AsyncStorage.setItem('cached_news_articles', JSON.stringify(cacheData));
      this.cachedContent.set('news_articles', cacheData);
      
      console.log(`Cached ${articles.length} news articles`);
    } catch (error) {
      console.error('News articles caching error:', error);
    }
  }

  async cacheWeatherData(weather, location) {
    try {
      const cacheData = {
        weather: weather,
        location: location,
        cachedAt: new Date().toISOString(),
        expiresAt: new Date(Date.now() + 60 * 60 * 1000).toISOString() // 1 hour
      };
      
      await AsyncStorage.setItem(`cached_weather_${location}`, JSON.stringify(cacheData));
      this.cachedContent.set(`weather_${location}`, cacheData);
      
      console.log(`Cached weather data for ${location}`);
    } catch (error) {
      console.error('Weather data caching error:', error);
    }
  }

  async cacheMusicTracks(tracks) {
    try {
      const cacheData = {
        tracks: tracks,
        cachedAt: new Date().toISOString(),
        expiresAt: new Date(Date.now() + 12 * 60 * 60 * 1000).toISOString() // 12 hours
      };
      
      await AsyncStorage.setItem('cached_music_tracks', JSON.stringify(cacheData));
      this.cachedContent.set('music_tracks', cacheData);
      
      console.log(`Cached ${tracks.length} music tracks`);
    } catch (error) {
      console.error('Music tracks caching error:', error);
    }
  }

  async cacheLanguageData(languageData) {
    try {
      const cacheData = {
        languageData: languageData,
        cachedAt: new Date().toISOString(),
        expiresAt: new Date(Date.now() + 48 * 60 * 60 * 1000).toISOString() // 48 hours
      };
      
      await AsyncStorage.setItem('cached_language_data', JSON.stringify(cacheData));
      this.cachedContent.set('language_data', cacheData);
      
      console.log('Cached language detection data');
    } catch (error) {
      console.error('Language data caching error:', error);
    }
  }

  async cacheAudioStream(streamUrl, durationMinutes = 30) {
    try {
      // For mobile, we'll cache stream metadata rather than the actual audio file
      // due to storage limitations and streaming nature of radio
      const cacheData = {
        streamUrl: streamUrl,
        cachedAt: new Date().toISOString(),
        availableOffline: false, // Audio streams require internet
        fallbackMessage: 'Audio streaming requires internet connection'
      };
      
      await AsyncStorage.setItem('cached_audio_stream', JSON.stringify(cacheData));
      
      console.log('Cached audio stream metadata');
      return null; // Cannot cache actual stream on mobile
    } catch (error) {
      console.error('Audio stream caching error:', error);
      return null;
    }
  }

  // Retrieve Cached Content
  async getCachedRadioStations() {
    try {
      const cached = await this.getCachedData('cached_radio_stations');
      return cached ? cached.stations : [];
    } catch (error) {
      console.error('Cached radio stations retrieval error:', error);
      return [];
    }
  }

  async getCachedNews() {
    try {
      const cached = await this.getCachedData('cached_news_articles');
      return cached ? cached.articles : [];
    } catch (error) {
      console.error('Cached news retrieval error:', error);
      return [];
    }
  }

  async getCachedWeather(location) {
    try {
      const cached = await this.getCachedData(`cached_weather_${location}`);
      return cached ? cached.weather : null;
    } catch (error) {
      console.error('Cached weather retrieval error:', error);
      return null;
    }
  }

  async getCachedMusic() {
    try {
      const cached = await this.getCachedData('cached_music_tracks');
      return cached ? cached.tracks : [];
    } catch (error) {
      console.error('Cached music retrieval error:', error);
      return [];
    }
  }

  async getCachedLanguageData() {
    try {
      const cached = await this.getCachedData('cached_language_data');
      return cached ? cached.languageData : null;
    } catch (error) {
      console.error('Cached language data retrieval error:', error);
      return null;
    }
  }

  async getCachedData(key) {
    try {
      const cachedJson = await AsyncStorage.getItem(key);
      if (cachedJson) {
        const cached = JSON.parse(cachedJson);
        
        // Check if cache has expired
        if (cached.expiresAt && new Date() > new Date(cached.expiresAt)) {
          await AsyncStorage.removeItem(key);
          return null;
        }
        
        return cached;
      }
      return null;
    } catch (error) {
      console.error(`Cache retrieval error for ${key}:`, error);
      return null;
    }
  }

  async loadCachedContent() {
    try {
      console.log('Loading cached content for offline mode...');
      
      const cachedStations = await this.getCachedRadioStations();
      const cachedNews = await this.getCachedNews(); 
      const cachedMusic = await this.getCachedMusic();
      
      console.log(`Loaded offline content: ${cachedStations.length} stations, ${cachedNews.length} news articles, ${cachedMusic.length} music tracks`);
      
      return {
        stations: cachedStations,
        news: cachedNews,
        music: cachedMusic
      };
    } catch (error) {
      console.error('Cached content loading error:', error);
      return { stations: [], news: [], music: [] };
    }
  }

  async syncCachedData() {
    try {
      console.log('Syncing cached data with server...');
      // Sync logic would go here - upload any offline changes, download updates
    } catch (error) {
      console.error('Data sync error:', error);
    }
  }

  async getCacheStats() {
    try {
      const keys = await AsyncStorage.getAllKeys();
      const cacheKeys = keys.filter(key => key.startsWith('cached_'));
      
      let totalSize = 0;
      const stats = {};
      
      for (const key of cacheKeys) {
        const data = await AsyncStorage.getItem(key);
        if (data) {
          const size = new Blob([data]).size;
          totalSize += size;
          stats[key] = {
            size: size,
            items: JSON.parse(data).articles?.length || JSON.parse(data).stations?.length || JSON.parse(data).tracks?.length || 1
          };
        }
      }
      
      return {
        totalSizeBytes: totalSize,
        totalSizeMB: (totalSize / 1024 / 1024).toFixed(2),
        cacheKeys: cacheKeys.length,
        breakdown: stats
      };
    } catch (error) {
      console.error('Cache stats error:', error);
      return { totalSizeBytes: 0, totalSizeMB: '0.00', cacheKeys: 0, breakdown: {} };
    }
  }

  async clearCache() {
    try {
      const keys = await AsyncStorage.getAllKeys();
      const cacheKeys = keys.filter(key => key.startsWith('cached_'));
      await AsyncStorage.multiRemove(cacheKeys);
      this.cachedContent.clear();
      console.log('Cache cleared');
    } catch (error) {
      console.error('Cache clearing error:', error);
    }
  }

  async getOfflineCapabilities() {
    return {
      canPlayRadio: false, // Requires internet for streaming
      canViewNews: true,   // Cached articles available
      canViewWeather: true, // Cached weather available (limited freshness)
      canViewMusic: true,   // Cached music info available
      canDetectLanguage: true, // Cached language data available
      canSwitchStations: true, // Cached station info available
      limitations: [
        'Live radio streaming requires internet connection',
        'Weather data may be outdated',
        'News articles have limited freshness',
        'Music discovery limited to cached content',
        'Real-time features unavailable'
      ]
    };
  }
}

export default new OfflineService();