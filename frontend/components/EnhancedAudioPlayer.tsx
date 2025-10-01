import React, { useState, useEffect, useRef } from 'react';
import {
  View,
  Text,
  StyleSheet,
  TouchableOpacity,
  ActivityIndicator,
  Alert,
  Animated,
  PanGestureHandler,
  State,
  Dimensions,
  Platform,
} from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { useTheme } from '../contexts/ThemeContext';
import Slider from '@react-native-community/slider';
import AsyncStorage from '@react-native-async-storage/async-storage';
import * as Haptics from 'expo-haptics';

const { width } = Dimensions.get('window');

interface AudioPlayerProps {
  streamUrl: string;
  title: string;
  subtitle: string;
  onPlayStateChange?: (isPlaying: boolean) => void;
  onError?: (error: string) => void;
}

export const EnhancedAudioPlayer: React.FC<AudioPlayerProps> = ({
  streamUrl,
  title,
  subtitle,
  onPlayStateChange,
  onError,
}) => {
  const { colors, isDark } = useTheme();
  const [isPlaying, setIsPlaying] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [volume, setVolume] = useState(0.8);
  const [quality, setQuality] = useState<'high' | 'medium' | 'low'>('high');
  const [showControls, setShowControls] = useState(true);
  const [sleepTimer, setSleepTimer] = useState<number | null>(null);
  const [isBuffering, setIsBuffering] = useState(false);
  
  // Animations
  const pulseAnim = useRef(new Animated.Value(1)).current;
  const fadeAnim = useRef(new Animated.Value(1)).current;
  const controlsAnim = useRef(new Animated.Value(1)).current;
  
  // Audio instance
  const audioRef = useRef<any>(null);
  const sleepTimerRef = useRef<NodeJS.Timeout | null>(null);

  // Initialize audio settings
  useEffect(() => {
    loadAudioSettings();
    startPulseAnimation();
    
    return () => {
      if (sleepTimerRef.current) {
        clearTimeout(sleepTimerRef.current);
      }
    };
  }, []);

  const loadAudioSettings = async () => {
    try {
      const savedVolume = await AsyncStorage.getItem('audio_volume');
      const savedQuality = await AsyncStorage.getItem('audio_quality');
      
      if (savedVolume) setVolume(parseFloat(savedVolume));
      if (savedQuality) setQuality(savedQuality as 'high' | 'medium' | 'low');
    } catch (error) {
      console.log('Error loading audio settings:', error);
    }
  };

  const saveAudioSettings = async () => {
    try {
      await AsyncStorage.setItem('audio_volume', volume.toString());
      await AsyncStorage.setItem('audio_quality', quality);
    } catch (error) {
      console.log('Error saving audio settings:', error);
    }
  };

  const startPulseAnimation = () => {
    Animated.loop(
      Animated.sequence([
        Animated.timing(pulseAnim, {
          toValue: 1.1,
          duration: 1000,
          useNativeDriver: true,
        }),
        Animated.timing(pulseAnim, {
          toValue: 1,
          duration: 1000,
          useNativeDriver: true,
        }),
      ])
    ).start();
  };

  const toggleControls = () => {
    const toValue = showControls ? 0 : 1;
    setShowControls(!showControls);
    
    Animated.timing(controlsAnim, {
      toValue,
      duration: 300,
      useNativeDriver: true,
    }).start();
  };

  const handlePlayPause = async () => {
    try {
      if (isPlaying) {
        await pauseAudio();
      } else {
        await playAudio();
      }
      
      // Haptic feedback
      await Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Medium);
    } catch (error) {
      onError?.(error instanceof Error ? error.message : 'Playback error');
    }
  };

  const playAudio = async () => {
    setIsLoading(true);
    setIsBuffering(true);
    
    try {
      // Platform-specific audio implementation
      if (Platform.OS === 'web') {
        if (audioRef.current) {
          audioRef.current.pause();
        }
        
        const audio = new Audio();
        audio.crossOrigin = 'anonymous';
        audio.preload = 'auto';
        audio.volume = volume;
        
        // Get quality-adjusted URL
        const qualityUrl = getQualityAdjustedUrl(streamUrl);
        audio.src = qualityUrl;
        
        audio.addEventListener('loadstart', () => {
          setIsBuffering(true);
        });
        
        audio.addEventListener('canplaythrough', () => {
          setIsBuffering(false);
        });
        
        audio.addEventListener('playing', () => {
          setIsPlaying(true);
          setIsBuffering(false);
          onPlayStateChange?.(true);
        });
        
        audio.addEventListener('pause', () => {
          setIsPlaying(false);
          onPlayStateChange?.(false);
        });
        
        audio.addEventListener('error', (e) => {
          console.error('Audio error:', e);
          onError?.('Failed to load audio stream');
          setIsPlaying(false);
          setIsBuffering(false);
        });
        
        await audio.play();
        audioRef.current = audio;
        
      } else {
        // Native implementation using expo-av
        const { Audio } = require('expo-av');
        
        await Audio.setAudioModeAsync({
          staysActiveInBackground: true,
          shouldDuckAndroid: false,
          playThroughEarpieceAndroid: false,
          allowsRecordingIOS: false,
          playsInSilentModeIOS: true,
        });
        
        const { sound } = await Audio.Sound.createAsync(
          { uri: getQualityAdjustedUrl(streamUrl) },
          { 
            shouldPlay: true,
            volume: volume,
            progressUpdateIntervalMillis: 1000,
          }
        );
        
        sound.setOnPlaybackStatusUpdate((status) => {
          if (status.isLoaded) {
            setIsPlaying(status.isPlaying || false);
            setIsBuffering(status.isBuffering || false);
            onPlayStateChange?.(status.isPlaying || false);
          }
        });
        
        audioRef.current = sound;
      }
      
    } catch (error) {
      console.error('Play error:', error);
      onError?.(error instanceof Error ? error.message : 'Failed to play audio');
    } finally {
      setIsLoading(false);
    }
  };

  const pauseAudio = async () => {
    if (audioRef.current) {
      try {
        if (Platform.OS === 'web') {
          audioRef.current.pause();
        } else {
          await audioRef.current.pauseAsync();
        }
        setIsPlaying(false);
        onPlayStateChange?.(false);
      } catch (error) {
        console.error('Pause error:', error);
      }
    }
  };

  const stopAudio = async () => {
    if (audioRef.current) {
      try {
        if (Platform.OS === 'web') {
          audioRef.current.pause();
          audioRef.current.currentTime = 0;
        } else {
          await audioRef.current.stopAsync();
          await audioRef.current.unloadAsync();
        }
        audioRef.current = null;
        setIsPlaying(false);
        onPlayStateChange?.(false);
      } catch (error) {
        console.error('Stop error:', error);
      }
    }
  };

  const handleVolumeChange = (newVolume: number) => {
    setVolume(newVolume);
    if (audioRef.current) {
      if (Platform.OS === 'web') {
        audioRef.current.volume = newVolume;
      } else {
        audioRef.current.setVolumeAsync(newVolume);
      }
    }
    saveAudioSettings();
  };

  const getQualityAdjustedUrl = (url: string): string => {
    // Adjust URL based on quality setting
    switch (quality) {
      case 'high':
        return url.replace('128', '256').replace('midfi', 'hifi');
      case 'medium':
        return url.replace('256', '128').replace('hifi', 'midfi');
      case 'low':
        return url.replace('256', '64').replace('128', '64').replace('hifi', 'lofi').replace('midfi', 'lofi');
      default:
        return url;
    }
  };

  const toggleQuality = () => {
    const qualities: Array<'high' | 'medium' | 'low'> = ['high', 'medium', 'low'];
    const currentIndex = qualities.indexOf(quality);
    const nextQuality = qualities[(currentIndex + 1) % qualities.length];
    setQuality(nextQuality);
    
    Alert.alert(
      'Audio Quality',
      `Changed to ${nextQuality} quality. Restart playback to apply changes.`,
      [{ text: 'OK' }]
    );
    
    saveAudioSettings();
  };

  const setSleepTimerMinutes = (minutes: number) => {
    if (sleepTimerRef.current) {
      clearTimeout(sleepTimerRef.current);
    }
    
    setSleepTimer(minutes);
    
    sleepTimerRef.current = setTimeout(() => {
      stopAudio();
      setSleepTimer(null);
      Alert.alert('Sleep Timer', 'Audio stopped automatically');
    }, minutes * 60 * 1000);
    
    Alert.alert('Sleep Timer', `Audio will stop in ${minutes} minutes`);
  };

  const clearSleepTimer = () => {
    if (sleepTimerRef.current) {
      clearTimeout(sleepTimerRef.current);
      sleepTimerRef.current = null;
    }
    setSleepTimer(null);
  };

  const styles = StyleSheet.create({
    container: {
      backgroundColor: colors.card,
      borderRadius: 16,
      padding: 20,
      margin: 16,
      shadowColor: colors.shadow,
      shadowOffset: { width: 0, height: 4 },
      shadowOpacity: 0.1,
      shadowRadius: 8,
      elevation: 4,
    },
    titleContainer: {
      alignItems: 'center',
      marginBottom: 20,
    },
    title: {
      fontSize: 18,
      fontWeight: '600',
      color: colors.text,
      textAlign: 'center',
    },
    subtitle: {
      fontSize: 14,
      color: colors.textSecondary,
      textAlign: 'center',
      marginTop: 4,
    },
    playButton: {
      width: 80,
      height: 80,
      borderRadius: 40,
      backgroundColor: colors.primary,
      alignItems: 'center',
      justifyContent: 'center',
      alignSelf: 'center',
      marginVertical: 20,
      shadowColor: colors.primary,
      shadowOffset: { width: 0, height: 4 },
      shadowOpacity: 0.3,
      shadowRadius: 8,
      elevation: 6,
    },
    controlsContainer: {
      flexDirection: 'row',
      alignItems: 'center',
      justifyContent: 'space-around',
      marginTop: 20,
    },
    controlButton: {
      padding: 12,
      borderRadius: 8,
      backgroundColor: colors.surface,
    },
    volumeContainer: {
      marginTop: 20,
      paddingHorizontal: 10,
    },
    volumeLabel: {
      fontSize: 14,
      color: colors.textSecondary,
      textAlign: 'center',
      marginBottom: 10,
    },
    qualityContainer: {
      flexDirection: 'row',
      alignItems: 'center',
      justifyContent: 'center',
      marginTop: 15,
    },
    qualityText: {
      fontSize: 12,
      color: colors.textSecondary,
      marginRight: 8,
    },
    sleepTimerContainer: {
      flexDirection: 'row',
      justifyContent: 'space-around',
      marginTop: 15,
      paddingTop: 15,
      borderTopWidth: 1,
      borderTopColor: colors.border,
    },
    sleepTimerButton: {
      paddingHorizontal: 12,
      paddingVertical: 6,
      borderRadius: 12,
      backgroundColor: colors.surface,
    },
    sleepTimerButtonActive: {
      backgroundColor: colors.primary,
    },
    sleepTimerText: {
      fontSize: 12,
      color: colors.textSecondary,
    },
    sleepTimerTextActive: {
      color: colors.background,
    },
    bufferingContainer: {
      alignItems: 'center',
      marginVertical: 10,
    },
    bufferingText: {
      fontSize: 12,
      color: colors.textSecondary,
      marginTop: 4,
    },
  });

  return (
    <View style={styles.container}>
      <TouchableOpacity onPress={toggleControls} style={styles.titleContainer}>
        <Text style={styles.title}>{title}</Text>
        <Text style={styles.subtitle}>{subtitle}</Text>
      </TouchableOpacity>

      <Animated.View style={{ transform: [{ scale: isPlaying ? pulseAnim : 1 }] }}>
        <TouchableOpacity style={styles.playButton} onPress={handlePlayPause}>
          {isLoading ? (
            <ActivityIndicator size="large" color="#fff" />
          ) : (
            <Ionicons
              name={isPlaying ? 'pause' : 'play'}
              size={32}
              color="#fff"
            />
          )}
        </TouchableOpacity>
      </Animated.View>

      {isBuffering && (
        <View style={styles.bufferingContainer}>
          <ActivityIndicator size="small" color={colors.primary} />
          <Text style={styles.bufferingText}>Buffering...</Text>
        </View>
      )}

      <Animated.View style={{ opacity: controlsAnim }}>
        <View style={styles.controlsContainer}>
          <TouchableOpacity style={styles.controlButton} onPress={stopAudio}>
            <Ionicons name="stop" size={24} color={colors.text} />
          </TouchableOpacity>
          
          <TouchableOpacity style={styles.controlButton} onPress={toggleQuality}>
            <Ionicons name="settings" size={24} color={colors.text} />
          </TouchableOpacity>
          
          <TouchableOpacity 
            style={styles.controlButton} 
            onPress={() => setSleepTimerMinutes(30)}
          >
            <Ionicons name="moon" size={24} color={colors.text} />
          </TouchableOpacity>
        </View>

        <View style={styles.volumeContainer}>
          <Text style={styles.volumeLabel}>Volume: {Math.round(volume * 100)}%</Text>
          <Slider
            style={{ width: '100%', height: 40 }}
            minimumValue={0}
            maximumValue={1}
            value={volume}
            onValueChange={handleVolumeChange}
            minimumTrackTintColor={colors.primary}
            maximumTrackTintColor={colors.border}
            thumbStyle={{ backgroundColor: colors.primary }}
          />
        </View>

        <View style={styles.qualityContainer}>
          <Text style={styles.qualityText}>Quality: {quality.toUpperCase()}</Text>
          <TouchableOpacity onPress={toggleQuality}>
            <Ionicons name="chevron-forward" size={16} color={colors.textSecondary} />
          </TouchableOpacity>
        </View>

        <View style={styles.sleepTimerContainer}>
          {[15, 30, 60].map((minutes) => (
            <TouchableOpacity
              key={minutes}
              style={[
                styles.sleepTimerButton,
                sleepTimer === minutes && styles.sleepTimerButtonActive,
              ]}
              onPress={() => setSleepTimerMinutes(minutes)}
            >
              <Text
                style={[
                  styles.sleepTimerText,
                  sleepTimer === minutes && styles.sleepTimerTextActive,
                ]}
              >
                {minutes}min
              </Text>
            </TouchableOpacity>
          ))}
          
          {sleepTimer && (
            <TouchableOpacity
              style={styles.sleepTimerButton}
              onPress={clearSleepTimer}
            >
              <Text style={styles.sleepTimerText}>Clear</Text>
            </TouchableOpacity>
          )}
        </View>
      </Animated.View>
    </View>
  );
};