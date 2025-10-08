import { Audio, AVPlaybackStatus, InterruptionModeIOS, InterruptionModeAndroid } from 'expo-audio';
import * as MediaLibrary from 'expo-media-library';
import { AppState, AppStateStatus, Platform } from 'react-native';
import * as TaskManager from 'expo-task-manager';
import * as BackgroundFetch from 'expo-background-fetch';

export interface MediaMetadata {
  title: string;
  artist: string;
  artwork?: string;
  album?: string;
  duration?: number;
}

export interface BackgroundAudioState {
  isPlaying: boolean;
  position: number;
  duration: number;
  buffering: boolean;
  metadata: MediaMetadata | null;
  volume: number;
  playbackRate: number;
}

const BACKGROUND_AUDIO_TASK = 'background-audio-task';

class EnhancedBackgroundAudioService {
  private sound: Audio.Sound | null = null;
  private listeners: Set<(state: BackgroundAudioState) => void> = new Set();
  private currentState: BackgroundAudioState = {
    isPlaying: false,
    position: 0,
    duration: 0,
    buffering: false,
    metadata: null,
    volume: 1.0,
    playbackRate: 1.0
  };
  private appStateSubscription: any = null;
  private playbackStatusUpdate: any = null;
  private backgroundTaskRegistered = false;

  constructor() {
    this.initializeAudioSession();
    this.setupAppStateListener();
    this.registerBackgroundTask();
  }

  private async initializeAudioSession(): Promise<void> {
    try {
      // Configure audio session for background playback
      await Audio.setAudioModeAsync({
        allowsRecordingIOS: false,
        playsInSilentModeIOS: true,
        shouldDuckAndroid: false,
        playThroughEarpieceAndroid: false,
        staysActiveInBackground: true,
        interruptionModeIOS: InterruptionModeIOS.DoNotMix,
        interruptionModeAndroid: InterruptionModeAndroid.DoNotMix,
      });

      console.log('🎵 Enhanced background audio session initialized');
    } catch (error) {
      console.error('❌ Failed to initialize audio session:', error);
    }
  }

  private setupAppStateListener(): void {
    this.appStateSubscription = AppState.addEventListener(
      'change',
      this.handleAppStateChange.bind(this)
    );
  }

  private async registerBackgroundTask(): Promise<void> {
    try {
      // Define background task
      TaskManager.defineTask(BACKGROUND_AUDIO_TASK, () => {
        try {
          console.log('🔄 Background audio task executed');
          // Keep audio session active
          return BackgroundFetch.BackgroundFetchResult.NewData;
        } catch (error) {
          console.error('❌ Background task error:', error);
          return BackgroundFetch.BackgroundFetchResult.Failed;
        }
      });

      // Register background fetch
      const status = await BackgroundFetch.getStatusAsync();
      if (status === BackgroundFetch.BackgroundFetchStatus.Available) {
        await BackgroundFetch.registerTaskAsync(BACKGROUND_AUDIO_TASK, {
          minimumInterval: 15000, // 15 seconds
          stopOnTerminate: false,
          startOnBoot: false,
        });
        
        this.backgroundTaskRegistered = true;
        console.log('✅ Background audio task registered');
      }
    } catch (error) {
      console.error('❌ Failed to register background task:', error);
    }
  }

  private handleAppStateChange = (nextAppState: AppStateStatus) => {
    console.log(`📱 App state changed to: ${nextAppState}`);
    
    if (nextAppState === 'background') {
      this.handleAppBackground();
    } else if (nextAppState === 'active') {
      this.handleAppForeground();
    }
  };

  private async handleAppBackground(): Promise<void> {
    try {
      console.log('📱 App going to background, maintaining audio session');
      
      // Ensure audio continues in background
      if (this.sound && this.currentState.isPlaying) {
        await Audio.setAudioModeAsync({
          allowsRecordingIOS: false,
          playsInSilentModeIOS: true,
          shouldDuckAndroid: false,
          playThroughEarpieceAndroid: false,
          staysActiveInBackground: true,
          interruptionModeIOS: InterruptionModeIOS.DoNotMix,
          interruptionModeAndroid: InterruptionModeAndroid.DoNotMix,
        });

        // Set up media session metadata for lock screen controls
        await this.updateMediaSessionMetadata();
      }
    } catch (error) {
      console.error('❌ Error handling app background:', error);
    }
  }

  private async handleAppForeground(): Promise<void> {
    try {
      console.log('📱 App returned to foreground');
      
      // Refresh playback status
      if (this.sound) {
        const status = await this.sound.getStatusAsync();
        this.handlePlaybackStatusUpdate(status);
      }
    } catch (error) {
      console.error('❌ Error handling app foreground:', error);
    }
  }

  private async updateMediaSessionMetadata(): Promise<void> {
    try {
      if (!this.currentState.metadata) return;

      // Set media session metadata for lock screen controls
      const metadata = this.currentState.metadata;
      
      if (Platform.OS === 'ios') {
        // iOS Media Player framework integration would go here
        // For now, we'll use the available expo-audio features
        console.log('🎵 Updated iOS media session:', metadata.title);
      } else {
        // Android MediaSession integration would go here
        console.log('🎵 Updated Android media session:', metadata.title);
      }
    } catch (error) {
      console.error('❌ Failed to update media session:', error);
    }
  }

  /**
   * Load and prepare audio for playback
   */
  async loadAudio(uri: string, metadata: MediaMetadata): Promise<boolean> {
    try {
      // Unload previous sound
      if (this.sound) {
        await this.unloadAudio();
      }

      console.log('🎵 Loading audio:', uri);

      // Create new sound instance
      const { sound } = await Audio.Sound.createAsync(
        { uri },
        {
          shouldPlay: false,
          isLooping: false,
          volume: this.currentState.volume,
          rate: this.currentState.playbackRate,
        },
        this.handlePlaybackStatusUpdate.bind(this)
      );

      this.sound = sound;

      // Update metadata
      this.currentState.metadata = metadata;
      
      // Set up playback status updates
      await this.sound.setOnPlaybackStatusUpdate(
        this.handlePlaybackStatusUpdate.bind(this)
      );

      console.log('✅ Audio loaded successfully');
      this.notifyListeners();
      return true;
    } catch (error) {
      console.error('❌ Failed to load audio:', error);
      return false;
    }
  }

  /**
   * Start or resume playback
   */
  async play(): Promise<boolean> {
    try {
      if (!this.sound) {
        console.log('⚠️ No audio loaded');
        return false;
      }

      await this.sound.playAsync();
      await this.updateMediaSessionMetadata();
      
      console.log('▶️ Playback started');
      return true;
    } catch (error) {
      console.error('❌ Failed to start playback:', error);
      return false;
    }
  }

  /**
   * Pause playback
   */
  async pause(): Promise<boolean> {
    try {
      if (!this.sound) {
        console.log('⚠️ No audio loaded');
        return false;
      }

      await this.sound.pauseAsync();
      console.log('⏸️ Playback paused');
      return true;
    } catch (error) {
      console.error('❌ Failed to pause playback:', error);
      return false;
    }
  }

  /**
   * Stop playback
   */
  async stop(): Promise<boolean> {
    try {
      if (!this.sound) {
        console.log('⚠️ No audio loaded');
        return false;
      }

      await this.sound.stopAsync();
      console.log('⏹️ Playback stopped');
      return true;
    } catch (error) {
      console.error('❌ Failed to stop playback:', error);
      return false;
    }
  }

  /**
   * Seek to specific position
   */
  async seekTo(positionMillis: number): Promise<boolean> {
    try {
      if (!this.sound) {
        console.log('⚠️ No audio loaded');
        return false;
      }

      await this.sound.setPositionAsync(positionMillis);
      console.log('⏭️ Seeked to:', positionMillis);
      return true;
    } catch (error) {
      console.error('❌ Failed to seek:', error);
      return false;
    }
  }

  /**
   * Set playback volume (0.0 to 1.0)
   */
  async setVolume(volume: number): Promise<boolean> {
    try {
      const clampedVolume = Math.max(0, Math.min(1, volume));
      
      if (this.sound) {
        await this.sound.setVolumeAsync(clampedVolume);
      }
      
      this.currentState.volume = clampedVolume;
      this.notifyListeners();
      
      console.log('🔊 Volume set to:', clampedVolume);
      return true;
    } catch (error) {
      console.error('❌ Failed to set volume:', error);
      return false;
    }
  }

  /**
   * Set playback rate (0.5 to 2.0)
   */
  async setPlaybackRate(rate: number): Promise<boolean> {
    try {
      const clampedRate = Math.max(0.5, Math.min(2.0, rate));
      
      if (this.sound) {
        await this.sound.setRateAsync(clampedRate, true);
      }
      
      this.currentState.playbackRate = clampedRate;
      this.notifyListeners();
      
      console.log('⚡ Playback rate set to:', clampedRate);
      return true;
    } catch (error) {
      console.error('❌ Failed to set playback rate:', error);
      return false;
    }
  }

  /**
   * Handle playback status updates
   */
  private handlePlaybackStatusUpdate = (status: AVPlaybackStatus) => {
    if (!status.isLoaded) {
      console.log('⚠️ Audio not loaded');
      return;
    }

    // Update current state
    this.currentState = {
      ...this.currentState,
      isPlaying: status.isPlaying || false,
      position: status.positionMillis || 0,
      duration: status.durationMillis || 0,
      buffering: status.isBuffering || false,
    };

    // Handle playback completion
    if (status.didJustFinish && !status.isLooping) {
      console.log('🏁 Playback completed');
      this.currentState.isPlaying = false;
    }

    // Handle errors
    if (status.error) {
      console.error('❌ Playback error:', status.error);
    }

    this.notifyListeners();
  };

  /**
   * Unload current audio
   */
  async unloadAudio(): Promise<void> {
    try {
      if (this.sound) {
        await this.sound.unloadAsync();
        this.sound = null;
        console.log('🗑️ Audio unloaded');
      }

      // Reset state
      this.currentState = {
        isPlaying: false,
        position: 0,
        duration: 0,
        buffering: false,
        metadata: null,
        volume: this.currentState.volume,
        playbackRate: this.currentState.playbackRate
      };

      this.notifyListeners();
    } catch (error) {
      console.error('❌ Failed to unload audio:', error);
    }
  }

  /**
   * Get current playback state
   */
  getState(): BackgroundAudioState {
    return { ...this.currentState };
  }

  /**
   * Check if audio is currently loaded
   */
  isLoaded(): boolean {
    return this.sound !== null;
  }

  /**
   * Add state change listener
   */
  addListener(callback: (state: BackgroundAudioState) => void): () => void {
    this.listeners.add(callback);
    
    // Return unsubscribe function
    return () => {
      this.listeners.delete(callback);
    };
  }

  /**
   * Notify all listeners of state changes
   */
  private notifyListeners(): void {
    this.listeners.forEach(callback => {
      try {
        callback({ ...this.currentState });
      } catch (error) {
        console.error('❌ Background audio listener error:', error);
      }
    });
  }

  /**
   * Get formatted time string
   */
  getFormattedTime(milliseconds: number): string {
    const totalSeconds = Math.floor(milliseconds / 1000);
    const minutes = Math.floor(totalSeconds / 60);
    const seconds = totalSeconds % 60;
    return `${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`;
  }

  /**
   * Get playback progress percentage
   */
  getProgress(): number {
    if (this.currentState.duration === 0) return 0;
    return (this.currentState.position / this.currentState.duration) * 100;
  }

  /**
   * Clean up resources
   */
  async cleanup(): Promise<void> {
    try {
      // Unload audio
      await this.unloadAudio();
      
      // Remove app state listener
      if (this.appStateSubscription) {
        this.appStateSubscription.remove();
      }
      
      // Unregister background task
      if (this.backgroundTaskRegistered) {
        await BackgroundFetch.unregisterTaskAsync(BACKGROUND_AUDIO_TASK);
      }
      
      // Clear listeners
      this.listeners.clear();
      
      console.log('🧹 Enhanced background audio service cleaned up');
    } catch (error) {
      console.error('❌ Cleanup error:', error);
    }
  }
}

// Export singleton instance
export const enhancedBackgroundAudioService = new EnhancedBackgroundAudioService();
export default EnhancedBackgroundAudioService;