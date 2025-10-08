import React, { useState, useEffect, useRef, useCallback, useMemo } from 'react';
import {
  View,
  Text,
  StyleSheet,
  Animated,
  Dimensions,
  Platform,
} from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { useTheme } from '../../contexts/ThemeContext';
import { shadowStyles } from '../../utils/shadowStyles';
import { Button } from './Button';
import { Card } from './Card';
import { LoadingSpinner } from './LoadingSpinner';
import { iOSAudioInputPicker } from '../iOSAudioInputPicker';
import { 
  PerformanceMonitor, 
  debounce, 
  optimizeAudioStream,
  useOptimizedCallback,
  useOptimizedMemo 
} from '../../utils/performance';

const { width } = Dimensions.get('window');

interface EnhancedAudioPlayerProps {
  title: string;
  subtitle?: string;
  streamUrl: string;
  isPlaying: boolean;
  isLoading: boolean;
  isBuffering: boolean;
  onPlay: () => void;
  onPause: () => void;
  onStop: () => void;
  onSeek?: (position: number) => void;
  position?: number;
  duration?: number;
  volume?: number;
  onVolumeChange?: (volume: number) => void;
  artwork?: string;
  showWaveform?: boolean;
  quality?: 'low' | 'medium' | 'high';
  onQualityChange?: (quality: 'low' | 'medium' | 'high') => void;
  showiOSAudioPicker?: boolean;
  onAudioInputSelected?: (input: any) => void;
}

export const EnhancedAudioPlayerUI: React.FC<EnhancedAudioPlayerProps> = ({
  title,
  subtitle,
  streamUrl,
  isPlaying,
  isLoading,
  isBuffering,
  onPlay,
  onPause,
  onStop,
  onSeek,
  position = 0,
  duration = 0,
  volume = 1,
  onVolumeChange,
  artwork,
  showWaveform = false,
  quality = 'medium',
  onQualityChange,
  showiOSAudioPicker = true,
  onAudioInputSelected,
}) => {
  const { colors } = useTheme();
  
  // Performance optimized state
  const [localVolume, setLocalVolume] = useState(volume);
  const [showControls, setShowControls] = useState(true);
  
  // Animated values for smooth UX
  const scaleAnimation = useRef(new Animated.Value(1)).current;
  const waveformAnimation = useRef(new Animated.Value(0)).current;
  const pulseAnimation = useRef(new Animated.Value(1)).current;

  // Optimized callbacks with debouncing
  const debouncedVolumeChange = useOptimizedCallback(
    debounce((vol: number) => {
      onVolumeChange?.(vol);
    }, 300),
    [onVolumeChange]
  );

  const handleVolumeChange = useOptimizedCallback((newVolume: number) => {
    setLocalVolume(newVolume);
    debouncedVolumeChange(newVolume);
  }, [debouncedVolumeChange]);

  const handlePlayPause = useOptimizedCallback(() => {
    PerformanceMonitor.start('audio-action');
    
    // Button animation feedback
    Animated.sequence([
      Animated.timing(scaleAnimation, {
        toValue: 0.95,
        duration: 100,
        useNativeDriver: true,
      }),
      Animated.timing(scaleAnimation, {
        toValue: 1,
        duration: 100,
        useNativeDriver: true,
      }),
    ]).start();

    if (isPlaying) {
      onPause();
    } else {
      onPlay();
    }
    
    PerformanceMonitor.end('audio-action');
  }, [isPlaying, onPlay, onPause, scaleAnimation]);

  // Optimized stream URL
  const optimizedStreamUrl = useOptimizedMemo(() => {
    return optimizeAudioStream(streamUrl, quality);
  }, [streamUrl, quality]);

  // Waveform animation effect
  useEffect(() => {
    if (showWaveform && isPlaying) {
      const waveAnimation = Animated.loop(
        Animated.sequence([
          Animated.timing(waveformAnimation, {
            toValue: 1,
            duration: 1500,
            useNativeDriver: false,
          }),
          Animated.timing(waveformAnimation, {
            toValue: 0,
            duration: 1500,
            useNativeDriver: false,
          }),
        ])
      );
      waveAnimation.start();
      return () => waveAnimation.stop();
    } else {
      waveformAnimation.setValue(0);
    }
  }, [showWaveform, isPlaying, waveformAnimation]);

  // Pulse animation for play button
  useEffect(() => {
    if (isPlaying) {
      const pulseAnim = Animated.loop(
        Animated.sequence([
          Animated.timing(pulseAnimation, {
            toValue: 1.1,
            duration: 1000,
            useNativeDriver: true,
          }),
          Animated.timing(pulseAnimation, {
            toValue: 1,
            duration: 1000,
            useNativeDriver: true,
          }),
        ])
      );
      pulseAnim.start();
      return () => pulseAnim.stop();
    } else {
      pulseAnimation.setValue(1);
    }
  }, [isPlaying, pulseAnimation]);

  // Format time display
  const formatTime = useOptimizedCallback((time: number) => {
    const minutes = Math.floor(time / 60);
    const seconds = Math.floor(time % 60);
    return `${minutes}:${seconds.toString().padStart(2, '0')}`;
  }, []);

  // Progress bar component
  const ProgressBar = useOptimizedMemo(() => {
    if (!duration || duration === 0) return null;

    const progress = position / duration;
    
    return (
      <View style={styles.progressContainer}>
        <View style={[styles.progressBar, { backgroundColor: colors.border }]}>
          <View 
            style={[
              styles.progressFill,
              { 
                backgroundColor: colors.primary,
                width: `${progress * 100}%`
              }
            ]} 
          />
        </View>
        <View style={styles.timeContainer}>
          <Text style={[styles.timeText, { color: colors.textSecondary }]}>
            {formatTime(position)}
          </Text>
          <Text style={[styles.timeText, { color: colors.textSecondary }]}>
            {formatTime(duration)}
          </Text>
        </View>
      </View>
    );
  }, [position, duration, colors, formatTime]);

  // Waveform visualization
  const WaveformVisualization = useOptimizedMemo(() => {
    if (!showWaveform) return null;

    const bars = Array.from({ length: 20 }, (_, i) => (
      <Animated.View
        key={i}
        style={[
          styles.waveformBar,
          {
            backgroundColor: colors.primary,
            height: waveformAnimation.interpolate({
              inputRange: [0, 1],
              outputRange: [4, Math.random() * 30 + 10],
            }),
          },
        ]}
      />
    ));

    return <View style={styles.waveformContainer}>{bars}</View>;
  }, [showWaveform, colors, waveformAnimation]);

  return (
    <Card style={[styles.container, { backgroundColor: colors.card }]} padding="large">
      {/* Header with title and artwork */}
      <View style={styles.header}>
        {artwork && (
          <View style={[styles.artworkContainer, ...shadowStyles.small]}>
            {/* Artwork placeholder - in real app, use Image component */}
            <View style={[styles.artwork, { backgroundColor: colors.surface }]}>
              <Ionicons 
                name="musical-notes" 
                size={24} 
                color={colors.textSecondary} 
              />
            </View>
          </View>
        )}
        <View style={styles.titleContainer}>
          <Text style={[styles.title, { color: colors.text }]} numberOfLines={1}>
            {title}
          </Text>
          {subtitle && (
            <Text style={[styles.subtitle, { color: colors.textSecondary }]} numberOfLines={1}>
              {subtitle}
            </Text>
          )}
        </View>
      </View>

      {/* Waveform Visualization */}
      {WaveformVisualization}

      {/* Progress Bar */}
      {ProgressBar}

      {/* Main Controls */}
      <View style={styles.controlsContainer}>
        <Button
          title=""
          icon="stop"
          variant="ghost"
          size="medium"
          onPress={onStop}
          style={styles.secondaryButton}
        />
        
        <Animated.View style={{ transform: [{ scale: scaleAnimation }] }}>
          <Button
            title=""
            icon={isPlaying ? 'pause' : 'play'}
            variant="primary"
            size="large"
            onPress={handlePlayPause}
            loading={isLoading}
            disabled={isLoading || isBuffering}
            style={[
              styles.playButton,
              {
                transform: [{ scale: pulseAnimation }],
              },
            ]}
          />
        </Animated.View>

        <Button
          title=""
          icon="volume-high"
          variant="ghost"
          size="medium"
          onPress={() => setShowControls(!showControls)}
          style={styles.secondaryButton}
        />
      </View>

      {/* Buffering Indicator */}
      {isBuffering && (
        <View style={styles.bufferingContainer}>
          <LoadingSpinner size="small" message="Buffering..." />
        </View>
      )}

      {/* Stream Quality Indicator */}
      <View style={styles.qualityContainer}>
        <Text style={[styles.qualityText, { color: colors.textSecondary }]}>
          Quality: {quality.toUpperCase()}
        </Text>
        <View style={[
          styles.qualityDot,
          { backgroundColor: quality === 'high' ? colors.success : 
                            quality === 'medium' ? colors.warning : colors.error }
        ]} />
      </View>
    </Card>
  );
};

const styles = StyleSheet.create({
  container: {
    marginVertical: 12,
  },
  header: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 16,
  },
  artworkContainer: {
    marginRight: 12,
  },
  artwork: {
    width: 50,
    height: 50,
    borderRadius: 8,
    justifyContent: 'center',
    alignItems: 'center',
  },
  titleContainer: {
    flex: 1,
  },
  title: {
    fontSize: 18,
    fontWeight: '600',
    marginBottom: 4,
  },
  subtitle: {
    fontSize: 14,
    fontWeight: '400',
  },
  waveformContainer: {
    flexDirection: 'row',
    alignItems: 'flex-end',
    justifyContent: 'center',
    height: 40,
    marginVertical: 16,
  },
  waveformBar: {
    width: 3,
    marginHorizontal: 1,
    borderRadius: 2,
  },
  progressContainer: {
    marginVertical: 16,
  },
  progressBar: {
    height: 4,
    borderRadius: 2,
    overflow: 'hidden',
  },
  progressFill: {
    height: '100%',
    borderRadius: 2,
  },
  timeContainer: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    marginTop: 8,
  },
  timeText: {
    fontSize: 12,
    fontWeight: '500',
  },
  controlsContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    marginVertical: 16,
  },
  playButton: {
    marginHorizontal: 20,
    width: 64,
    height: 64,
    borderRadius: 32,
  },
  secondaryButton: {
    width: 44,
    height: 44,
    borderRadius: 22,
  },
  bufferingContainer: {
    position: 'absolute',
    top: '50%',
    left: '50%',
    transform: [{ translateX: -50 }, { translateY: -50 }],
  },
  qualityContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    marginTop: 8,
  },
  qualityText: {
    fontSize: 12,
    marginRight: 8,
  },
  qualityDot: {
    width: 8,
    height: 8,
    borderRadius: 4,
  },
});