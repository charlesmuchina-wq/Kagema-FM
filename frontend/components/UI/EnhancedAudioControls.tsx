import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  StyleSheet,
  TouchableOpacity,
  Animated,
  Dimensions,
  PanGestureHandler,
  GestureHandlerRootView,
  PanGestureHandlerGestureEvent,
} from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { useTheme } from '../../contexts/ThemeContext';
import { Button } from './Button';
import * as Haptics from 'expo-haptics';

const { width } = Dimensions.get('window');

interface EnhancedAudioControlsProps {
  isPlaying: boolean;
  onPlayPause: () => void;
  onNext?: () => void;
  onPrevious?: () => void;
  onVolumeChange?: (volume: number) => void;
  currentTrack?: {
    title: string;
    artist: string;
    duration?: number;
    position?: number;
  };
  showExtendedControls?: boolean;
}

export const EnhancedAudioControls: React.FC<EnhancedAudioControlsProps> = ({
  isPlaying,
  onPlayPause,
  onNext,
  onPrevious,
  onVolumeChange,
  currentTrack,
  showExtendedControls = true,
}) => {
  const { colors, isDark } = useTheme();
  const [volume, setVolume] = useState(0.7);
  const [showVolumeSlider, setShowVolumeSlider] = useState(false);
  
  // Animations
  const playButtonScale = new Animated.Value(1);
  const playButtonRotation = new Animated.Value(0);
  const volumeSliderOpacity = new Animated.Value(0);
  const waveAnimations = [
    new Animated.Value(0),
    new Animated.Value(0),
    new Animated.Value(0),
  ];

  // Animated waveform effect when playing
  useEffect(() => {
    if (isPlaying) {
      const animations = waveAnimations.map((anim, index) =>
        Animated.loop(
          Animated.sequence([
            Animated.timing(anim, {
              toValue: 1,
              duration: 800 + index * 200,
              useNativeDriver: false,
            }),
            Animated.timing(anim, {
              toValue: 0,
              duration: 800 + index * 200,
              useNativeDriver: false,
            }),
          ])
        )
      );
      
      animations.forEach(animation => animation.start());
      
      return () => {
        animations.forEach(animation => animation.stop());
      };
    } else {
      waveAnimations.forEach(anim => anim.setValue(0));
    }
  }, [isPlaying]);

  const handlePlayPause = async () => {
    // Haptic feedback
    await Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Medium);
    
    // Scale animation
    Animated.sequence([
      Animated.timing(playButtonScale, {
        toValue: 0.9,
        duration: 100,
        useNativeDriver: true,
      }),
      Animated.timing(playButtonScale, {
        toValue: 1,
        duration: 100,
        useNativeDriver: true,
      }),
    ]).start();
    
    onPlayPause();
  };

  const handleNext = async () => {
    if (onNext) {
      await Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Light);
      onNext();
    }
  };

  const handlePrevious = async () => {
    if (onPrevious) {
      await Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Light);
      onPrevious();
    }
  };

  const toggleVolumeSlider = () => {
    setShowVolumeSlider(!showVolumeSlider);
    Animated.timing(volumeSliderOpacity, {
      toValue: showVolumeSlider ? 0 : 1,
      duration: 300,
      useNativeDriver: false,
    }).start();
  };

  const handleVolumeGesture = (event: PanGestureHandlerGestureEvent) => {
    const { translationX } = event.nativeEvent;
    const maxWidth = width * 0.6;
    const newVolume = Math.max(0, Math.min(1, volume + translationX / maxWidth));
    setVolume(newVolume);
    onVolumeChange?.(newVolume);
  };

  const formatTime = (seconds: number = 0) => {
    const mins = Math.floor(seconds / 60);
    const secs = Math.floor(seconds % 60);
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  const styles = StyleSheet.create({
    container: {
      backgroundColor: colors.card,
      borderRadius: 20,
      padding: 20,
      margin: 16,
      shadowColor: colors.shadow,
      shadowOffset: { width: 0, height: 4 },
      shadowOpacity: 0.3,
      shadowRadius: 8,
      elevation: 8,
    },
    trackInfo: {
      alignItems: 'center',
      marginBottom: 20,
    },
    trackTitle: {
      fontSize: 18,
      fontWeight: '600',
      color: colors.text,
      textAlign: 'center',
      marginBottom: 4,
    },
    trackArtist: {
      fontSize: 14,
      color: colors.textSecondary,
      textAlign: 'center',
    },
    waveformContainer: {
      flexDirection: 'row',
      alignItems: 'center',
      justifyContent: 'center',
      height: 40,
      marginVertical: 10,
    },
    waveBar: {
      width: 4,
      borderRadius: 2,
      backgroundColor: colors.primary,
      marginHorizontal: 2,
    },
    controlsContainer: {
      flexDirection: 'row',
      alignItems: 'center',
      justifyContent: 'space-around',
      paddingVertical: 20,
    },
    controlButton: {
      width: 50,
      height: 50,
      borderRadius: 25,
      backgroundColor: colors.surface,
      alignItems: 'center',
      justifyContent: 'center',
    },
    playButton: {
      width: 70,
      height: 70,
      borderRadius: 35,
      backgroundColor: colors.primary,
      alignItems: 'center',
      justifyContent: 'center',
      shadowColor: colors.primary,
      shadowOffset: { width: 0, height: 4 },
      shadowOpacity: 0.4,
      shadowRadius: 8,
      elevation: 8,
    },
    extendedControls: {
      flexDirection: 'row',
      alignItems: 'center',
      justifyContent: 'space-between',
      marginTop: 15,
      paddingHorizontal: 10,
    },
    volumeContainer: {
      flexDirection: 'row',
      alignItems: 'center',
    },
    volumeSlider: {
      width: width * 0.6,
      height: 4,
      backgroundColor: colors.border,
      borderRadius: 2,
      marginHorizontal: 10,
    },
    volumeProgress: {
      height: '100%',
      backgroundColor: colors.primary,
      borderRadius: 2,
    },
    progressContainer: {
      marginTop: 10,
    },
    progressBar: {
      height: 4,
      backgroundColor: colors.border,
      borderRadius: 2,
      marginVertical: 10,
    },
    progressFill: {
      height: '100%',
      backgroundColor: colors.primary,
      borderRadius: 2,
    },
    timeContainer: {
      flexDirection: 'row',
      justifyContent: 'space-between',
    },
    timeText: {
      fontSize: 12,
      color: colors.textSecondary,
    },
  });

  return (
    <GestureHandlerRootView style={{ flex: 1 }}>
      <View style={styles.container}>
        {/* Track Information */}
        {currentTrack && (
          <View style={styles.trackInfo}>
            <Text style={styles.trackTitle} numberOfLines={2}>
              {currentTrack.title || 'Unknown Track'}
            </Text>
            <Text style={styles.trackArtist} numberOfLines={1}>
              {currentTrack.artist || 'Unknown Artist'}
            </Text>
          </View>
        )}

        {/* Animated Waveform */}
        <View style={styles.waveformContainer}>
          {waveAnimations.map((anim, index) => (
            <Animated.View
              key={index}
              style={[
                styles.waveBar,
                {
                  height: anim.interpolate({
                    inputRange: [0, 1],
                    outputRange: [5, 30],
                  }),
                },
              ]}
            />
          ))}
        </View>

        {/* Main Controls */}
        <View style={styles.controlsContainer}>
          {onPrevious && (
            <TouchableOpacity
              style={styles.controlButton}
              onPress={handlePrevious}
              accessible={true}
              accessibilityLabel="Previous track"
              accessibilityRole="button"
            >
              <Ionicons name="play-skip-back" size={24} color={colors.text} />
            </TouchableOpacity>
          )}

          <Animated.View style={{ transform: [{ scale: playButtonScale }] }}>
            <TouchableOpacity
              style={styles.playButton}
              onPress={handlePlayPause}
              accessible={true}
              accessibilityLabel={isPlaying ? "Pause" : "Play"}
              accessibilityRole="button"
            >
              <Ionicons
                name={isPlaying ? "pause" : "play"}
                size={32}
                color="#FFFFFF"
              />
            </TouchableOpacity>
          </Animated.View>

          {onNext && (
            <TouchableOpacity
              style={styles.controlButton}
              onPress={handleNext}
              accessible={true}
              accessibilityLabel="Next track"
              accessibilityRole="button"
            >
              <Ionicons name="play-skip-forward" size={24} color={colors.text} />
            </TouchableOpacity>
          )}
        </View>

        {/* Progress Bar */}
        {currentTrack?.duration && (
          <View style={styles.progressContainer}>
            <View style={styles.progressBar}>
              <View
                style={[
                  styles.progressFill,
                  {
                    width: `${((currentTrack.position || 0) / currentTrack.duration) * 100}%`,
                  },
                ]}
              />
            </View>
            <View style={styles.timeContainer}>
              <Text style={styles.timeText}>
                {formatTime(currentTrack.position)}
              </Text>
              <Text style={styles.timeText}>
                {formatTime(currentTrack.duration)}
              </Text>
            </View>
          </View>
        )}

        {/* Extended Controls */}
        {showExtendedControls && (
          <View style={styles.extendedControls}>
            <TouchableOpacity onPress={toggleVolumeSlider}>
              <Ionicons name="volume-medium" size={24} color={colors.text} />
            </TouchableOpacity>

            {/* Volume Slider */}
            <Animated.View
              style={[
                styles.volumeContainer,
                { opacity: volumeSliderOpacity },
              ]}
            >
              <PanGestureHandler onGestureEvent={handleVolumeGesture}>
                <View style={styles.volumeSlider}>
                  <View
                    style={[
                      styles.volumeProgress,
                      { width: `${volume * 100}%` },
                    ]}
                  />
                </View>
              </PanGestureHandler>
            </Animated.View>

            <TouchableOpacity>
              <Ionicons name="heart-outline" size={24} color={colors.text} />
            </TouchableOpacity>
          </View>
        )}
      </View>
    </GestureHandlerRootView>
  );
};