import React from 'react';
import { Station } from '../types/station';
import {
  View,
  Text,
  StyleSheet,
  TouchableOpacity,
  ActivityIndicator,
} from 'react-native';
import { Ionicons } from '@expo/vector-icons';

interface NowPlayingMetadata {
  title: string;
  artist: string;
  album?: string;
  artwork?: string;
}

interface NowPlayingCardProps {
  station: Station | null;
  metadata: NowPlayingMetadata | null;
  isPlaying: boolean;
  isLoading: boolean;
  isBuffering: boolean;
  volume: number;
  isFavorite: boolean;
  onTogglePlayPause: () => void;
  onToggleFavorite: () => void;
  onVolumeUp: () => void;
  onVolumeDown: () => void;
  onStop: () => void;
}

export const NowPlayingCard: React.FC<NowPlayingCardProps> = ({
  station,
  metadata,
  isPlaying,
  isLoading,
  isBuffering,
  volume,
  isFavorite,
  onTogglePlayPause,
  onToggleFavorite,
  onVolumeUp,
  onVolumeDown,
  onStop,
}) => {
  if (!station) {
    return null;
  }

  return (
    <View style={styles.container}>
      <View style={styles.header}>
        <Text style={styles.label}>NOW PLAYING</Text>
        {isBuffering && (
          <View style={styles.bufferingContainer}>
            <ActivityIndicator size="small" color="#FF6B35" />
            <Text style={styles.bufferingText}>Buffering...</Text>
          </View>
        )}
      </View>

      {/* Station & Metadata Info */}
      <View style={styles.infoSection}>
        <View style={styles.stationInfo}>
          <Text style={styles.stationName} numberOfLines={2}>
            {metadata?.title || station.standard_display_name || station.name}
          </Text>
          {station.call_sign && (
            <Text style={styles.callSign}>{station.call_sign}</Text>
          )}
          {metadata?.artist && metadata.artist !== 'Live Radio' && (
            <Text style={styles.artist} numberOfLines={1}>
              {metadata.artist}
            </Text>
          )}
          <Text style={styles.stationMeta}>
            {station.country} • Quality: {station.quality_score}
          </Text>
        </View>

        {/* Main Play Button */}
        <TouchableOpacity
          style={[
            styles.playButton,
            isLoading && styles.playButtonLoading
          ]}
          onPress={onTogglePlayPause}
          disabled={isLoading}
        >
          {isLoading ? (
            <ActivityIndicator size="large" color="#fff" />
          ) : (
            <Ionicons
              name={isPlaying ? 'pause' : 'play'}
              size={48}
              color="#fff"
            />
          )}
        </TouchableOpacity>
      </View>

      {/* Controls Section */}
      <View style={styles.controlsSection}>
        {/* Volume Controls */}
        <View style={styles.volumeControls}>
          <TouchableOpacity
            style={styles.volumeButton}
            onPress={onVolumeDown}
          >
            <Ionicons name="volume-low" size={24} color="#8B92B0" />
          </TouchableOpacity>
          
          <View style={styles.volumeIndicator}>
            <View style={styles.volumeBarContainer}>
              {[...Array(10)].map((_, index) => (
                <View
                  key={index}
                  style={[
                    styles.volumeBar,
                    index < Math.floor(volume * 10) && styles.volumeBarActive
                  ]}
                />
              ))}
            </View>
            <Text style={styles.volumeText}>{Math.round(volume * 100)}%</Text>
          </View>

          <TouchableOpacity
            style={styles.volumeButton}
            onPress={onVolumeUp}
          >
            <Ionicons name="volume-high" size={24} color="#8B92B0" />
          </TouchableOpacity>
        </View>

        {/* Action Buttons */}
        <View style={styles.actionButtons}>
          <TouchableOpacity
            style={styles.actionButton}
            onPress={onToggleFavorite}
          >
            <Ionicons
              name={isFavorite ? 'heart' : 'heart-outline'}
              size={24}
              color={isFavorite ? '#FF6B35' : '#8B92B0'}
            />
            <Text style={[
              styles.actionButtonText,
              isFavorite && styles.actionButtonTextActive
            ]}>
              {isFavorite ? 'Favorited' : 'Favorite'}
            </Text>
          </TouchableOpacity>

          <TouchableOpacity
            style={styles.actionButton}
            onPress={onStop}
          >
            <Ionicons name="stop-circle" size={24} color="#8B92B0" />
            <Text style={styles.actionButtonText}>Stop</Text>
          </TouchableOpacity>
        </View>
      </View>

      {/* Dragon Icon */}
      <View style={styles.dragonIconContainer}>
        <Text style={styles.dragonIcon}>🐉</Text>
        <Text style={styles.liveIndicator}>● LIVE</Text>
      </View>
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    backgroundColor: 'rgba(26, 31, 58, 0.95)',
    borderRadius: 20,
    padding: 24,
    marginBottom: 32,
    borderWidth: 1,
    borderColor: 'rgba(255, 107, 53, 0.3)',
    shadowColor: '#FF6B35',
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.3,
    shadowRadius: 12,
  },
  header: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 16,
  },
  label: {
    fontSize: 12,
    color: '#FF6B35',
    fontWeight: '700',
    letterSpacing: 2,
  },
  bufferingContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 8,
  },
  bufferingText: {
    fontSize: 12,
    color: '#FF6B35',
    fontWeight: '600',
  },
  infoSection: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    marginBottom: 20,
  },
  stationInfo: {
    flex: 1,
    marginRight: 16,
  },
  stationName: {
    fontSize: 24,
    fontWeight: '700',
    color: '#fff',
    marginBottom: 8,
  },
  callSign: {
    fontSize: 16,
    color: '#FF6B35',
    fontWeight: '700',
    marginBottom: 4,
  },
  artist: {
    fontSize: 14,
    color: '#FFFFFF',
    fontWeight: '600',
    marginBottom: 4,
    opacity: 0.9,
  },
  stationMeta: {
    fontSize: 12,
    color: '#8B92B0',
  },
  playButton: {
    width: 80,
    height: 80,
    borderRadius: 40,
    backgroundColor: '#FF6B35',
    justifyContent: 'center',
    alignItems: 'center',
    shadowColor: '#FF6B35',
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.5,
    shadowRadius: 12,
  },
  playButtonLoading: {
    backgroundColor: 'rgba(255, 107, 53, 0.6)',
  },
  controlsSection: {
    borderTopWidth: 1,
    borderTopColor: 'rgba(139, 146, 176, 0.2)',
    paddingTop: 20,
  },
  volumeControls: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 20,
    gap: 12,
  },
  volumeButton: {
    padding: 8,
  },
  volumeIndicator: {
    flex: 1,
    alignItems: 'center',
    gap: 8,
  },
  volumeBarContainer: {
    flexDirection: 'row',
    gap: 4,
    width: '100%',
    height: 4,
  },
  volumeBar: {
    flex: 1,
    height: 4,
    backgroundColor: 'rgba(139, 146, 176, 0.3)',
    borderRadius: 2,
  },
  volumeBarActive: {
    backgroundColor: '#FF6B35',
  },
  volumeText: {
    fontSize: 12,
    color: '#8B92B0',
    fontWeight: '600',
  },
  actionButtons: {
    flexDirection: 'row',
    gap: 12,
  },
  actionButton: {
    flex: 1,
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    backgroundColor: 'rgba(139, 146, 176, 0.2)',
    paddingVertical: 12,
    paddingHorizontal: 16,
    borderRadius: 12,
    borderWidth: 1,
    borderColor: 'rgba(139, 146, 176, 0.3)',
    gap: 8,
  },
  actionButtonText: {
    color: '#8B92B0',
    fontSize: 14,
    fontWeight: '600',
  },
  actionButtonTextActive: {
    color: '#FF6B35',
  },
  dragonIconContainer: {
    alignItems: 'center',
    marginTop: 16,
    flexDirection: 'row',
    justifyContent: 'center',
    gap: 12,
  },
  dragonIcon: {
    fontSize: 32,
  },
  liveIndicator: {
    fontSize: 12,
    color: '#FF6B35',
    fontWeight: '700',
    letterSpacing: 1,
  },
});
