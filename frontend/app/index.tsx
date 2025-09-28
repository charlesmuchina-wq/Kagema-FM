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
} from 'react-native';
import { Audio, AVPlaybackStatus } from 'expo-av';
import { Ionicons } from '@expo/vector-icons';

const { width } = Dimensions.get('window');
const EXPO_PUBLIC_BACKEND_URL = process.env.EXPO_PUBLIC_BACKEND_URL;

interface StationInfo {
  name: string;
  description: string;
  streamUrl: string;
  currentShow?: string;
}

export default function KagemaFMApp() {
  const [sound, setSound] = useState<Audio.Sound | null>(null);
  const [isPlaying, setIsPlaying] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [isBuffering, setIsBuffering] = useState(false);
  const [stationInfo, setStationInfo] = useState<StationInfo | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    setupAudio();
    fetchStationInfo();
    
    return () => {
      if (sound) {
        sound.unloadAsync();
      }
    };
  }, []);

  const setupAudio = async () => {
    try {
      await Audio.setAudioModeAsync({
        staysActiveInBackground: true,
        interruptionModeIOS: Audio.INTERRUPTION_MODE_IOS_DO_NOT_MIX,
        playsInSilentModeIOS: true,
        shouldDuckAndroid: false,
        interruptionModeAndroid: Audio.INTERRUPTION_MODE_ANDROID_DO_NOT_MIX,
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
      // Fallback station info
      setStationInfo({
        name: 'Kagema FM',
        description: 'Your favorite radio station',
        streamUrl: 'http://ice1.somafm.com/groovesalad-256-mp3', // Working SomaFM stream
      });
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

  return (
    <SafeAreaView style={styles.container}>
      <StatusBar barStyle="light-content" backgroundColor="#1a1a2e" />
      
      {/* Header */}
      <View style={styles.header}>
        <Text style={styles.headerTitle}>Kagema FM</Text>
        <Text style={styles.headerSubtitle}>Live Radio</Text>
      </View>

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
            onPress={fetchStationInfo}
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
    fontSize: 16,
    color: '#ff6b6b',
    textTransform: 'uppercase',
    letterSpacing: 2,
  },
  stationContainer: {
    flex: 1,
    alignItems: 'center',
    justifyContent: 'center',
    paddingHorizontal: 30,
  },
  logoContainer: {
    marginBottom: 30,
  },
  logo: {
    width: 120,
    height: 120,
    borderRadius: 60,
    borderWidth: 3,
    borderColor: '#ff6b6b',
  },
  logoPlaceholder: {
    width: 120,
    height: 120,
    borderRadius: 60,
    backgroundColor: '#2d2d54',
    alignItems: 'center',
    justifyContent: 'center',
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
    paddingBottom: 30,
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
});