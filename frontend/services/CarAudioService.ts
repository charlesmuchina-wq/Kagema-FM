import { Audio } from 'expo-av';
import { Platform } from 'react-native';
import * as MediaLibrary from 'expo-media-library';
import { activateKeepAwake, deactivateKeepAwake } from 'expo-keep-awake';

export interface CarAudioTrack {
  id: string;
  title: string;
  artist: string;
  uri: string;
  artwork?: string;
  genre?: string;
  isLiveStream?: boolean;
}

export interface CarAudioState {
  isPlaying: boolean;
  currentTrack: CarAudioTrack | null;
  position: number;
  duration: number;
  volume: number;
  buffering: boolean;
}

export class CarAudioService {
  private sound: Audio.Sound | null = null;
  private currentTrack: CarAudioTrack | null = null;
  private isPlaying = false;
  private carModeActive = false;
  private listeners: Set<(state: CarAudioState) => void> = new Set();
  private updateInterval: NodeJS.Timeout | null = null;

  constructor() {
    this.initializeAudio();
  }

  private async initializeAudio() {
    try {
      // Configure audio session for car environment
      await Audio.setAudioModeAsync({
        allowsRecordingIOS: false,
        interruptionModeIOS: Audio.INTERRUPTION_MODE_IOS_DO_NOT_MIX,
        playsInSilentModeIOS: true, // Essential for car mode
        shouldDuckAndroid: false, // Don't lower volume for other apps
        interruptionModeAndroid: Audio.INTERRUPTION_MODE_ANDROID_DO_NOT_MIX,
        playThroughEarpieceAndroid: false,
        staysActiveInBackground: true, // Keep audio active in background
      });

      console.log('✅ Car audio service initialized');
    } catch (error) {
      console.error('❌ Failed to initialize car audio service:', error);
    }
  }

  // Enable car mode with optimized audio settings
  async enableCarMode(): Promise<void> {
    try {
      this.carModeActive = true;
      activateKeepAwake('CarAudioPlayback');

      // Enhanced audio configuration for automotive environment
      await Audio.setAudioModeAsync({
        allowsRecordingIOS: false,
        interruptionModeIOS: Audio.INTERRUPTION_MODE_IOS_DUCK_OTHERS,
        playsInSilentModeIOS: true,
        shouldDuckAndroid: false,
        interruptionModeAndroid: Audio.INTERRUPTION_MODE_ANDROID_DUCK_OTHERS,
        playThroughEarpieceAndroid: false,
        staysActiveInBackground: true,
      });

      // Start position updates for car UI
      this.startPositionUpdates();

      console.log('🚗 Car mode audio enabled');
    } catch (error) {
      console.error('❌ Failed to enable car mode:', error);
    }
  }

  // Disable car mode
  async disableCarMode(): Promise<void> {
    try {
      this.carModeActive = false;
      deactivateKeepAwake('CarAudioPlayback');
      this.stopPositionUpdates();

      // Reset to normal audio mode
      await Audio.setAudioModeAsync({
        allowsRecordingIOS: true,
        interruptionModeIOS: Audio.INTERRUPTION_MODE_IOS_MIX_WITH_OTHERS,
        playsInSilentModeIOS: false,
        shouldDuckAndroid: true,
        interruptionModeAndroid: Audio.INTERRUPTION_MODE_ANDROID_MIX_WITH_OTHERS,
        playThroughEarpieceAndroid: false,
        staysActiveInBackground: false,
      });

      console.log('📱 Car mode audio disabled');
    } catch (error) {
      console.error('❌ Failed to disable car mode:', error);
    }
  }

  // Play a track with car-optimized loading
  async playTrack(track: CarAudioTrack): Promise<boolean> {
    try {
      // Stop current track
      if (this.sound) {
        await this.sound.unloadAsync();
        this.sound = null;
      }

      // Create new sound instance
      const { sound } = await Audio.Sound.createAsync(
        { uri: track.uri },
        {
          shouldPlay: true,
          isLooping: track.isLiveStream || false,
          volume: 1.0,
          rate: 1.0,
          shouldCorrectPitch: true,
        },
        this.onPlaybackStatusUpdate.bind(this)
      );

      this.sound = sound;
      this.currentTrack = track;
      this.isPlaying = true;

      // Update media session metadata for car integration
      await this.updateMediaSessionMetadata(track);

      this.notifyListeners();
      console.log(`🎵 Playing: ${track.title} by ${track.artist}`);
      return true;

    } catch (error) {
      console.error('❌ Failed to play track:', error);
      this.isPlaying = false;
      this.notifyListeners();
      return false;
    }
  }

  // Pause playback
  async pause(): Promise<void> {
    try {
      if (this.sound && this.isPlaying) {
        await this.sound.pauseAsync();
        this.isPlaying = false;
        this.notifyListeners();
        console.log('⏸️ Playback paused');
      }
    } catch (error) {
      console.error('❌ Failed to pause:', error);
    }
  }

  // Resume playback
  async resume(): Promise<void> {
    try {
      if (this.sound && !this.isPlaying) {
        await this.sound.playAsync();
        this.isPlaying = true;
        this.notifyListeners();
        console.log('▶️ Playback resumed');
      }
    } catch (error) {
      console.error('❌ Failed to resume:', error);
    }
  }

  // Stop playback
  async stop(): Promise<void> {
    try {
      if (this.sound) {
        await this.sound.stopAsync();
        this.isPlaying = false;
        this.notifyListeners();
        console.log('⏹️ Playback stopped');
      }
    } catch (error) {
      console.error('❌ Failed to stop:', error);
    }
  }

  // Set volume (0.0 to 1.0)
  async setVolume(volume: number): Promise<void> {
    try {
      if (this.sound) {
        await this.sound.setVolumeAsync(Math.max(0, Math.min(1, volume)));
        this.notifyListeners();
      }
    } catch (error) {
      console.error('❌ Failed to set volume:', error);
    }
  }

  // Seek to position (for non-live streams)
  async seekTo(positionMillis: number): Promise<void> {
    try {
      if (this.sound && this.currentTrack && !this.currentTrack.isLiveStream) {
        await this.sound.setPositionAsync(positionMillis);
        this.notifyListeners();
      }
    } catch (error) {
      console.error('❌ Failed to seek:', error);
    }
  }

  // Handle physical car button presses (if available)
  handleCarButtonPress(button: 'play_pause' | 'next' | 'previous' | 'voice'): void {
    console.log(`🚗 Car button pressed: ${button}`);
    
    switch (button) {
      case 'play_pause':
        this.isPlaying ? this.pause() : this.resume();
        break;
      case 'next':
        // Emit event for next track (handled by parent component)
        this.notifyListeners();
        break;
      case 'previous':
        // Emit event for previous track (handled by parent component)
        this.notifyListeners();
        break;
      case 'voice':
        // Trigger voice command (handled by parent component)
        this.notifyListeners();
        break;
    }
  }

  // Update media session metadata for car display
  private async updateMediaSessionMetadata(track: CarAudioTrack): Promise<void> {
    try {
      if (Platform.OS === 'ios') {
        // iOS Now Playing Info Center
        const MPNowPlayingInfoCenter = require('react-native').NativeModules.MPNowPlayingInfoCenter;
        
        if (MPNowPlayingInfoCenter) {
          await MPNowPlayingInfoCenter.setNowPlayingInfo({
            title: track.title,
            artist: track.artist,
            album: track.genre || 'Radio',
            artwork: track.artwork,
            playbackRate: this.isPlaying ? 1.0 : 0.0,
            elapsedPlaybackTime: 0,
          });
        }
      } else if (Platform.OS === 'android') {
        // Android MediaSession (would require native implementation)
        console.log('📱 Android media session update needed');
      }
    } catch (error) {
      console.log('ℹ️ Media session metadata not available:', error.message);
    }
  }

  // Playback status update callback
  private onPlaybackStatusUpdate = (status: any) => {
    if (status.isLoaded) {
      this.isPlaying = status.isPlaying;
      this.notifyListeners();
      
      // Handle errors
      if (status.error) {
        console.error('❌ Playback error:', status.error);
        this.isPlaying = false;
        this.notifyListeners();
      }
    }
  };

  // Position update timer for car UI
  private startPositionUpdates(): void {
    if (this.updateInterval) {
      clearInterval(this.updateInterval);
    }
    
    this.updateInterval = setInterval(async () => {
      if (this.sound && this.isPlaying && this.carModeActive) {
        try {
          const status = await this.sound.getStatusAsync();
          if (status.isLoaded) {
            this.notifyListeners();
          }
        } catch (error) {
          console.error('❌ Position update error:', error);
        }
      }
    }, 1000); // Update every second in car mode
  }

  private stopPositionUpdates(): void {
    if (this.updateInterval) {
      clearInterval(this.updateInterval);
      this.updateInterval = null;
    }
  }

  // Listener management
  addListener(callback: (state: CarAudioState) => void): () => void {
    this.listeners.add(callback);
    
    // Return unsubscribe function
    return () => {
      this.listeners.delete(callback);
    };
  }

  private notifyListeners(): void {
    const state: CarAudioState = {
      isPlaying: this.isPlaying,
      currentTrack: this.currentTrack,
      position: 0, // Would be updated from sound status
      duration: 0, // Would be updated from sound status
      volume: 1.0, // Would be updated from sound status
      buffering: false, // Would be updated from sound status
    };

    this.listeners.forEach(callback => {
      try {
        callback(state);
      } catch (error) {
        console.error('❌ Listener callback error:', error);
      }
    });
  }

  // Get current audio state
  getState(): CarAudioState {
    return {
      isPlaying: this.isPlaying,
      currentTrack: this.currentTrack,
      position: 0,
      duration: 0,
      volume: 1.0,
      buffering: false,
    };
  }

  // Clean up resources
  async cleanup(): Promise<void> {
    try {
      this.stopPositionUpdates();
      
      if (this.sound) {
        await this.sound.unloadAsync();
        this.sound = null;
      }
      
      this.listeners.clear();
      deactivateKeepAwake('CarAudioPlayback');
      
      console.log('🧹 Car audio service cleaned up');
    } catch (error) {
      console.error('❌ Cleanup error:', error);
    }
  }
}

// Export singleton instance
export const carAudioService = new CarAudioService();