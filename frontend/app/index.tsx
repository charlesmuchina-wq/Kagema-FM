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
  const [activeTab, setActiveTab] = useState<'radio' | 'news' | 'music' | 'language' | 'integrations'>('radio');
  
  // Language detection state
  const [languageData, setLanguageData] = useState<LanguageData | null>(null);
  const [showLanguageModal, setShowLanguageModal] = useState(false);
  const [supportedLanguages, setSupportedLanguages] = useState<any[]>([]);
  const [selectedStation, setSelectedStation] = useState<any>(null);
  
  // Integration state
  const [spotifyTracks, setSpotifyTracks] = useState<any[]>([]);
  const [nearbyPlaces, setNearbyPlaces] = useState<any[]>([]);
  const [trafficConditions, setTrafficConditions] = useState<any>(null);
  const [isVoiceListening, setIsVoiceListening] = useState(false);
  
  // Content disclaimer state
  const [showDisclaimerModal, setShowDisclaimerModal] = useState(false);
  const [disclaimerAccepted, setDisclaimerAccepted] = useState(false);
  const [countryCode, setCountryCode] = useState('GLOBAL');
  const [currentLanguageCode, setCurrentLanguageCode] = useState('en');
  
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

  // Check disclaimer acceptance when location is available
  const checkDisclaimerStatus = async () => {
    if (!location) return;

    const detectedCountryCode = ContentDisclaimerService.getCountryCodeFromLocation(
      location.coords.latitude,
      location.coords.longitude
    );
    
    setCountryCode(detectedCountryCode);

    // Determine language code from detected language
    if (languageData?.detected_language) {
      const langCode = languageData.detected_language.includes('pt') ? 'pt-br' : 'en';
      setCurrentLanguageCode(langCode);
    }

    // Check if user has already acknowledged disclaimers today
    const hasAcknowledged = await ContentDisclaimerService.hasUserAcknowledgedToday(detectedCountryCode);
    
    if (!hasAcknowledged) {
      setShowDisclaimerModal(true);
    } else {
      setDisclaimerAccepted(true);
    }
  };

  const handleDisclaimerAccept = () => {
    setDisclaimerAccepted(true);
    setShowDisclaimerModal(false);
  };

  const handleDisclaimerClose = () => {
    // If user closes without accepting, they cannot use the app
    Alert.alert(
      currentLanguageCode.startsWith('pt') ? 'Aceitação Necessária' : 'Acceptance Required',
      currentLanguageCode.startsWith('pt') 
        ? 'Você deve aceitar os avisos de conteúdo para usar o Kagema FM.'
        : 'You must accept the content disclaimers to use Kagema FM.',
      [
        { 
          text: currentLanguageCode.startsWith('pt') ? 'Revisar' : 'Review',
          onPress: () => setShowDisclaimerModal(true)
        }
      ]
    );
  };

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
    if (!location) return;

    try {
      setIsLoading(true);

      // First try the personalized content API
      try {
        const response = await fetch(`${EXPO_PUBLIC_BACKEND_URL}/api/personalized-content/multilingual`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            location: {
              latitude: location.coords.latitude,
              longitude: location.coords.longitude
            },
            preferences: {
              interests: ['radio', 'music', 'news'],
              favorite_genres: ['general'],
              location: locationInfo?.location || 'Unknown',
              age_group: 'adult',
              preferred_language: 'auto'
            }
          }),
        });

        if (response.ok) {
          const personalizedContent = await response.json();
          console.log('Personalized content loaded:', personalizedContent);

          // Set language data from personalized content
          if (personalizedContent.language_detection) {
            setLanguageData(personalizedContent.language_detection);
          }

          // Set station info from radio streams
          if (personalizedContent.radio_streams && personalizedContent.radio_streams.main_station) {
            setStationInfo({
              name: personalizedContent.radio_streams.main_station.name,
              description: personalizedContent.radio_streams.main_station.description,
              streamUrl: personalizedContent.radio_streams.main_station.streamUrl,
              currentShow: 'Live Radio',
              frequency: personalizedContent.radio_streams.main_station.frequency,
              alternative_streams: personalizedContent.radio_streams.alternative_streams || [],
              regional_stations: personalizedContent.radio_streams.regional_stations || []
            });
            console.log('Radio station info set:', personalizedContent.radio_streams.main_station);
          }

          // Set weather data
          if (personalizedContent.weather) {
            setWeatherData(personalizedContent.weather);
            console.log('Weather data set:', personalizedContent.weather);
          }

          // Set news data
          if (personalizedContent.news && personalizedContent.news.articles) {
            setNewsArticles(personalizedContent.news.articles);
            setNewsSummary('Stay updated with the latest news from your region.');
            console.log('News data set:', personalizedContent.news.articles.length, 'articles');
          }

          // Set music data
          if (personalizedContent.music && personalizedContent.music.tracks) {
            setMusicTracks(personalizedContent.music.tracks);
            setMusicRecommendations('Discover trending music in your area.');
            console.log('Music data set:', personalizedContent.music.tracks.length, 'tracks');
          }

          return; // Success, exit early
        }
      } catch (error) {
        console.error('Personalized content API failed:', error);
      }

      // Fallback: Try multilingual station info if personalized content fails
      try {
        const response = await fetch(`${EXPO_PUBLIC_BACKEND_URL}/api/station-info/multilingual`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            latitude: location.coords.latitude,
            longitude: location.coords.longitude
          }),
        });

        if (response.ok) {
          const stationData = await response.json();
          console.log('Station data loaded:', stationData);
          
          setStationInfo({
            name: stationData.station_name || 'Kagema FM',
            description: stationData.description || 'Your premier international radio platform',
            streamUrl: stationData.streamUrl || 'http://ice1.somafm.com/groovesalad-256-mp3',
            currentShow: stationData.currentShow || 'Live Radio',
            frequency: stationData.frequency || '101.5 FM',
            detected_language: stationData.detected_language,
            alternative_streams: stationData.alternative_streams || [],
            regional_stations: stationData.regional_stations || []
          });

          if (stationData.detected_language) {
            setLanguageData({
              detected_language: stationData.detected_language,
              alternative_languages: stationData.alternative_languages || [],
              county: stationData.county || 'Unknown',
              confidence: stationData.confidence || 1.0
            });
          }
        }
      } catch (error) {
        console.error('Station info API failed:', error);
      }

      // Final fallback - set default data
      if (!stationInfo) {
        console.log('Setting default station info');
        setStationInfo({
          name: 'Kagema FM',
          description: 'Your premier international radio platform',
          streamUrl: 'http://ice1.somafm.com/groovesalad-256-mp3',
          currentShow: 'Live Radio',
          frequency: '101.5 FM'
        });
      }

    } catch (error) {
      console.error('Error loading multilingual content:', error);
      // Set default fallback data
      setStationInfo({
        name: 'Kagema FM',
        description: 'Your premier international radio platform',  
        streamUrl: 'http://ice1.somafm.com/groovesalad-256-mp3',
        currentShow: 'Live Radio',
        frequency: '101.5 FM'
      });
    } finally {
      setIsLoading(false);
    }
  };

  const loadIntegrationData = async () => {
    if (!location || !activeIntegrations) return;

    try {
      // Load Google Maps data
      if (activeIntegrations.google_maps) {
        const places = await getNearbyPlaces(
          location.coords.latitude,
          location.coords.longitude,
          5000
        );
        setNearbyPlaces(places.results || []);

        const traffic = await getTrafficConditions(
          location.coords.latitude,
          location.coords.longitude
        );
        setTrafficConditions(traffic);
      }

      // Search for current radio tracks on Spotify
      if (activeIntegrations.spotify && stationInfo) {
        const tracks = await searchSpotify(`Kagema FM ${languageData?.detected_language || 'Kenya'}`);
        setSpotifyTracks(tracks.tracks?.items || []);
      }

    } catch (error) {
      console.error('Error loading integration data:', error);
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
    await loadIntegrationData();
    setRefreshing(false);
  };

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

        {/* Language Detection Info */}
        {languageData && (
          <View style={styles.languageDetectionContainer}>
            <View style={styles.languageRow}>
              <Text style={styles.languageFlag}>{getLanguageFlag(languageData?.detected_language || 'en')}</Text>
              <Text style={styles.languageText}>
                {languageData?.language_info?.native_name || languageData?.detected_language?.toUpperCase() || 'UNKNOWN'}
              </Text>
              <Text style={styles.locationText}>• {languageData?.county || 'Unknown'}</Text>
            </View>
            <Text style={styles.confidenceText}>
              Confidence: {Math.round((languageData?.confidence || 0) * 100)}%
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

      {/* Status */}
      <View style={styles.statusContainer}>
        <View style={[styles.statusDot, { backgroundColor: isPlaying ? '#4CAF50' : '#666' }]} />
        <Text style={styles.statusText}>
          {isPlaying ? 'Live - ON AIR' : 'Offline'}
        </Text>
      </View>
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

  useEffect(() => {
    const loadContent = async () => {
      if (location && locationInfo && isInitialized) {
        try {
          await checkDisclaimerStatus();
          await loadMultilingualContent();
          await loadIntegrationData();
        } catch (error) {
          console.error('Content loading error:', error);
        }
      }
    };
    
    loadContent();
  }, [location, locationInfo, isInitialized]); // Proper dependencies

  return (
    <SafeAreaView style={styles.container}>
      <StatusBar barStyle="light-content" backgroundColor="#1a1a2e" />
      
      {/* Header */}
      <View style={styles.header}>
        <Text style={styles.headerTitle}>Kagema FM</Text>
        <Text style={styles.headerSubtitle}>Complete Platform Integration</Text>
        {languageData && (
          <Text style={styles.languageIndicator}>
            {getLanguageFlag(languageData.detected_language)} {languageData.language_info?.native_name}
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

      {/* Tab Content */}
      {!disclaimerAccepted ? (
        <View style={styles.disclaimerRequiredContainer}>
          <Ionicons name="warning-outline" size={64} color="#ff6b6b" />
          <Text style={styles.disclaimerRequiredTitle}>
            {currentLanguageCode.startsWith('pt') ? 'Aceitação Necessária' : 'Content Disclaimer Required'}
          </Text>
          <Text style={styles.disclaimerRequiredText}>
            {currentLanguageCode.startsWith('pt') 
              ? 'Por favor, aceite os avisos de conteúdo para usar o Kagema FM.'
              : 'Please accept the content disclaimers to use Kagema FM.'}
          </Text>
          <TouchableOpacity 
            style={styles.showDisclaimerButton}
            onPress={() => setShowDisclaimerModal(true)}
          >
            <Text style={styles.showDisclaimerButtonText}>
              {currentLanguageCode.startsWith('pt') ? 'Ver Avisos' : 'View Disclaimers'}
            </Text>
          </TouchableOpacity>
        </View>
      ) : (
        <>
          {activeTab === 'radio' && renderRadioTab()}
          {activeTab === 'news' && renderNewsTab()}
          {activeTab === 'music' && renderMusicTab()}
          {activeTab === 'language' && renderLanguageTab()}
          {activeTab === 'integrations' && renderIntegrationsTab()}
        </>
      )}

      {/* Language Selection Modal */}
      {renderLanguageModal()}
      
      {/* Content Disclaimer Modal - Simplified for testing */}
      <Modal
        animationType="slide"
        transparent={false}
        visible={showDisclaimerModal}
        presentationStyle="fullScreen"
      >
        <SafeAreaView style={{ flex: 1, backgroundColor: '#1a1a2e', padding: 20, justifyContent: 'center' }}>
          <Text style={{ color: '#fff', fontSize: 24, textAlign: 'center', marginBottom: 20 }}>
            Content Disclaimer - Age Verification
          </Text>
          <Text style={{ color: '#ccc', fontSize: 16, textAlign: 'center', marginBottom: 30 }}>
            This application contains mature content intended for adults (18+). Please confirm your age to continue.
          </Text>
          <TouchableOpacity 
            style={{ backgroundColor: '#4CAF50', padding: 16, borderRadius: 8, marginBottom: 10 }}
            onPress={handleDisclaimerAccept}
          >
            <Text style={{ color: '#fff', fontSize: 16, fontWeight: 'bold', textAlign: 'center' }}>
              I am 18+ and Accept Terms
            </Text>
          </TouchableOpacity>
          <TouchableOpacity 
            style={{ backgroundColor: '#666', padding: 16, borderRadius: 8 }}
            onPress={handleDisclaimerClose}
          >
            <Text style={{ color: '#fff', fontSize: 16, textAlign: 'center' }}>
              Cancel
            </Text>
          </TouchableOpacity>
        </SafeAreaView>
      </Modal>
    </SafeAreaView>
  );
};

// Existing render methods would continue here (renderNewsTab, renderMusicTab, renderLanguageTab)
const renderNewsTab = () => (
  <ScrollView style={styles.tabContent}>
    <Text style={styles.tabTitle}>News</Text>
    {/* News content implementation */}
  </ScrollView>
);

const renderMusicTab = () => (
  <ScrollView style={styles.tabContent}>
    <Text style={styles.tabTitle}>Music</Text>
    {/* Music content implementation */}  
  </ScrollView>
);

const renderLanguageTab = () => (
  <ScrollView style={styles.tabContent}>
    <Text style={styles.tabTitle}>Language</Text>
    {/* Language content implementation */}
  </ScrollView>
);

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
});

export default MainApp;