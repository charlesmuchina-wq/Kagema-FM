import React, { useState, useEffect, createContext, useContext } from 'react';
import { Platform, Alert, Linking, AppState } from 'react-native';
import AsyncStorage from '@react-native-async-storage/async-storage';
import PushNotification from 'react-native-push-notification';
import Voice from '@react-native-voice/voice';
import Tts from 'react-native-tts';
import MusicControl from 'react-native-music-control';
import TrackPlayer from 'react-native-track-player';

const EXPO_PUBLIC_BACKEND_URL = process.env.EXPO_PUBLIC_BACKEND_URL;

// Integration Context
const IntegrationContext = createContext({});

export const useIntegrations = () => {
  const context = useContext(IntegrationContext);
  if (!context) {
    throw new Error('useIntegrations must be used within an IntegrationProvider');
  }
  return context;
};

export const IntegrationProvider = ({ children }) => {
  const [activeIntegrations, setActiveIntegrations] = useState({});
  const [isInitialized, setIsInitialized] = useState(false);
  const [emergencyAlerts, setEmergencyAlerts] = useState([]);

  useEffect(() => {
    initializeAllIntegrations();
    return () => {
      cleanup();
    };
  }, []);

  const initializeAllIntegrations = async () => {
    try {
      // Initialize core integrations
      await Promise.all([
        initializeGoogleMaps(),
        initializeSpotify(),
        initializeVoiceControl(),
        initializePushNotifications(),
        initializeMediaControls(),
        initializeEmergencyAlerts()
      ]);

      setIsInitialized(true);
    } catch (error) {
      console.error('Integration initialization error:', error);
    }
  };

  const initializeGoogleMaps = async () => {
    try {
      const response = await fetch(`${EXPO_PUBLIC_BACKEND_URL}/api/integrations/initialize`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': 'Bearer YOUR_API_TOKEN'
        },
        body: JSON.stringify({
          integration_type: 'google_maps',
          config: {
            api_key: 'GOOGLE_MAPS_API_KEY'
          }
        })
      });

      if (response.ok) {
        setActiveIntegrations(prev => ({ ...prev, google_maps: true }));
      }
    } catch (error) {
      console.error('Google Maps initialization error:', error);
    }
  };

  const initializeSpotify = async () => {
    try {
      const response = await fetch(`${EXPO_PUBLIC_BACKEND_URL}/api/integrations/initialize`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': 'Bearer YOUR_API_TOKEN'
        },
        body: JSON.stringify({
          integration_type: 'spotify',
          config: {
            client_id: 'SPOTIFY_CLIENT_ID',
            client_secret: 'SPOTIFY_CLIENT_SECRET',
            redirect_uri: 'kagema://spotify/callback'
          }
        })
      });

      if (response.ok) {
        setActiveIntegrations(prev => ({ ...prev, spotify: true }));
      }
    } catch (error) {
      console.error('Spotify initialization error:', error);
    }
  };

  const initializeVoiceControl = async () => {
    try {
      Voice.onSpeechStart = onSpeechStart;
      Voice.onSpeechEnd = onSpeechEnd;
      Voice.onSpeechResults = onSpeechResults;
      Voice.onSpeechError = onSpeechError;

      // Initialize TTS
      await Tts.setDefaultLanguage('en-US');
      await Tts.setDefaultRate(0.5);

      const response = await fetch(`${EXPO_PUBLIC_BACKEND_URL}/api/integrations/initialize`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': 'Bearer YOUR_API_TOKEN'
        },
        body: JSON.stringify({
          integration_type: 'voice_control',
          config: {}
        })
      });

      if (response.ok) {
        setActiveIntegrations(prev => ({ ...prev, voice_control: true }));
      }
    } catch (error) {
      console.error('Voice control initialization error:', error);
    }
  };

  const initializePushNotifications = () => {
    PushNotification.configure({
      onRegister: function (token) {
        console.log('Push notification token:', token);
        // Send token to backend for emergency alerts
        registerForEmergencyAlerts(token.token);
      },

      onNotification: function (notification) {
        console.log('Push notification received:', notification);
        
        if (notification.data && notification.data.alert_id) {
          handleEmergencyAlert(notification.data);
        }
        
        notification.finish(PushNotification.FetchResult.NoData);
      },

      permissions: {
        alert: true,
        badge: true,
        sound: true,
      },

      popInitialNotification: true,
      requestPermissions: true,
    });

    setActiveIntegrations(prev => ({ ...prev, push_notifications: true }));
  };

  const initializeMediaControls = async () => {
    try {
      // Enable media control
      MusicControl.enableControl('play', true);
      MusicControl.enableControl('pause', true);
      MusicControl.enableControl('stop', true);
      MusicControl.enableControl('nextTrack', true);
      MusicControl.enableControl('previousTrack', true);

      // Set event handlers
      MusicControl.on('play', handlePlay);
      MusicControl.on('pause', handlePause);
      MusicControl.on('stop', handleStop);
      MusicControl.on('nextTrack', handleNextTrack);
      MusicControl.on('previousTrack', handlePreviousTrack);

      // Initialize TrackPlayer
      await TrackPlayer.setupPlayer({
        waitForBuffer: true,
      });

      setActiveIntegrations(prev => ({ ...prev, media_controls: true }));
    } catch (error) {
      console.error('Media controls initialization error:', error);
    }
  };

  const initializeEmergencyAlerts = () => {
    // Create WebSocket connection for real-time emergency alerts
    const websocket = new WebSocket(`ws://localhost:8001/ws/emergency-alerts`);
    
    websocket.onopen = () => {
      console.log('Emergency alerts WebSocket connected');
      setActiveIntegrations(prev => ({ ...prev, emergency_alerts: true }));
    };

    websocket.onmessage = (event) => {
      const data = JSON.parse(event.data);
      if (data.type === 'emergency_alert') {
        handleEmergencyAlert(data.data);
      }
    };

    websocket.onerror = (error) => {
      console.error('Emergency alerts WebSocket error:', error);
    };
  };

  // Voice Control Handlers
  const onSpeechStart = () => {
    console.log('Voice recognition started');
  };

  const onSpeechEnd = () => {
    console.log('Voice recognition ended');
  };

  const onSpeechResults = async (event) => {
    const results = event.value;
    if (results && results.length > 0) {
      const command = results[0];
      await processVoiceCommand(command);
    }
  };

  const onSpeechError = (event) => {
    console.error('Voice recognition error:', event);
  };

  const processVoiceCommand = async (command) => {
    try {
      const response = await fetch(`${EXPO_PUBLIC_BACKEND_URL}/api/voice/process-command`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': 'Bearer YOUR_API_TOKEN'
        },
        body: JSON.stringify({
          command: command,
          language: 'en',
          user_id: 'current_user'
        })
      });

      const result = await response.json();
      
      if (result.success) {
        await executeVoiceCommand(result);
        if (result.response) {
          await Tts.speak(result.response);
        }
      }
    } catch (error) {
      console.error('Voice command processing error:', error);
    }
  };

  const executeVoiceCommand = async (commandResult) => {
    const { intent, entities } = commandResult;
    
    switch (intent) {
      case 'play_station':
        await playRadioStation(entities[0]);
        break;
      case 'pause':
        await pausePlayback();
        break;
      case 'resume':
        await resumePlayback();
        break;
      case 'volume_up':
        await adjustVolume('up');
        break;
      case 'volume_down':
        await adjustVolume('down');
        break;
    }
  };

  // Media Control Handlers
  const handlePlay = async () => {
    await TrackPlayer.play();
  };

  const handlePause = async () => {
    await TrackPlayer.pause();
  };

  const handleStop = async () => {
    await TrackPlayer.stop();
  };

  const handleNextTrack = async () => {
    await TrackPlayer.skipToNext();
  };

  const handlePreviousTrack = async () => {
    await TrackPlayer.skipToPrevious();
  };

  // Integration Methods
  const searchSpotify = async (query) => {
    if (!activeIntegrations.spotify) {
      throw new Error('Spotify integration not available');
    }

    try {
      const response = await fetch(`${EXPO_PUBLIC_BACKEND_URL}/api/spotify/search`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': 'Bearer YOUR_API_TOKEN'
        },
        body: JSON.stringify({ query, limit: 20 })
      });

      return await response.json();
    } catch (error) {
      console.error('Spotify search error:', error);
      return { tracks: { items: [] } };
    }
  };

  const createSpotifyPlaylist = async (playlistName, trackUris) => {
    if (!activeIntegrations.spotify) {
      throw new Error('Spotify integration not available');
    }

    try {
      const response = await fetch(`${EXPO_PUBLIC_BACKEND_URL}/api/spotify/create-playlist`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': 'Bearer YOUR_API_TOKEN'
        },
        body: JSON.stringify({
          user_id: 'current_user',
          playlist_name: playlistName,
          track_uris: trackUris
        })
      });

      return await response.json();
    } catch (error) {
      console.error('Spotify playlist creation error:', error);
      return null;
    }
  };

  const getNearbyPlaces = async (latitude, longitude, radius = 5000) => {
    if (!activeIntegrations.google_maps) {
      throw new Error('Google Maps integration not available');
    }

    try {
      const response = await fetch(`${EXPO_PUBLIC_BACKEND_URL}/api/google-maps/nearby-places`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': 'Bearer YOUR_API_TOKEN'
        },
        body: JSON.stringify({ lat: latitude, lng: longitude, radius })
      });

      return await response.json();
    } catch (error) {
      console.error('Google Maps nearby places error:', error);
      return { results: [] };
    }
  };

  const getTrafficConditions = async (latitude, longitude) => {
    if (!activeIntegrations.google_maps) {
      throw new Error('Google Maps integration not available');
    }

    try {
      const response = await fetch(`${EXPO_PUBLIC_BACKEND_URL}/api/google-maps/traffic`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': 'Bearer YOUR_API_TOKEN'
        },
        body: JSON.stringify({ lat: latitude, lng: longitude })
      });

      return await response.json();
    } catch (error) {
      console.error('Traffic conditions error:', error);
      return { routes: [] };
    }
  };

  const startVoiceRecognition = async () => {
    try {
      await Voice.start('en-US');
    } catch (error) {
      console.error('Start voice recognition error:', error);
    }
  };

  const stopVoiceRecognition = async () => {
    try {
      await Voice.stop();
    } catch (error) {
      console.error('Stop voice recognition error:', error);
    }
  };

  const handleEmergencyAlert = (alertData) => {
    setEmergencyAlerts(prev => [alertData, ...prev]);
    
    // Show emergency alert dialog
    Alert.alert(
      `${alertData.severity.toUpperCase()} ALERT`,
      `${alertData.title}\n\n${alertData.description}\n\nArea: ${alertData.area}`,
      [
        { text: 'Dismiss', style: 'cancel' },
        { text: 'More Info', onPress: () => showEmergencyDetails(alertData) }
      ],
      { cancelable: false }
    );
  };

  const showEmergencyDetails = (alertData) => {
    // Navigate to emergency alert details screen
    console.log('Show emergency details:', alertData);
  };

  const registerForEmergencyAlerts = async (pushToken) => {
    try {
      await fetch(`${EXPO_PUBLIC_BACKEND_URL}/api/push/register`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': 'Bearer YOUR_API_TOKEN'
        },
        body: JSON.stringify({
          token: pushToken,
          platform: Platform.OS,
          user_id: 'current_user'
        })
      });
    } catch (error) {
      console.error('Push token registration error:', error);
    }
  };

  const updateMediaMetadata = (title, subtitle, artwork) => {
    MusicControl.setNowPlaying({
      title: title,
      artwork: artwork,
      artist: subtitle,
      album: 'Kagema FM',
      genre: 'Radio',
      duration: 0,
      description: '',
      color: 0xffffff,
      colorized: true,
      state: MusicControl.STATE_PLAYING,
      speed: 1.0
    });
  };

  const cleanup = () => {
    Voice.destroy().then(Voice.removeAllListeners);
    MusicControl.stopControl();
    TrackPlayer.destroy();
  };

  const contextValue = {
    activeIntegrations,
    isInitialized,
    emergencyAlerts,
    
    // Voice Control
    startVoiceRecognition,
    stopVoiceRecognition,
    processVoiceCommand,
    
    // Music Integration
    searchSpotify,
    createSpotifyPlaylist,
    updateMediaMetadata,
    
    // Maps Integration
    getNearbyPlaces,
    getTrafficConditions,
    
    // Emergency Alerts
    handleEmergencyAlert,
    
    // Media Controls
    handlePlay,
    handlePause,
    handleStop,
    handleNextTrack,
    handlePreviousTrack
  };

  return (
    <IntegrationContext.Provider value={contextValue}>
      {children}
    </IntegrationContext.Provider>
  );
};

export default IntegrationProvider;