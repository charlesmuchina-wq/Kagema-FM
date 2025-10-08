import { Platform } from 'react-native';
import * as Audio from 'expo-audio';

// Human Interface Guidelines compliant audio controls
export interface HIGAudioControl {
  id: string;
  type: 'play' | 'pause' | 'stop' | 'skip-forward' | 'skip-backward' | 'seek' | 'volume' | 'custom';
  title: string;
  systemIcon?: string; // SF Symbols for iOS, Material for Android
  customIcon?: string;
  enabled: boolean;
  visible: boolean;
  accessibilityLabel: string;
  accessibilityHint?: string;
}

export interface UISound {
  id: string;
  name: string;
  type: 'feedback' | 'alert' | 'navigation' | 'success' | 'error' | 'warning';
  soundFile: string;
  volume: number;
  priority: 'low' | 'medium' | 'high';
  respectsSilentMode: boolean;
  duration: number; // milliseconds
}

export interface MediaSessionMetadata {
  title: string;
  artist: string;
  album: string;
  artwork: string;
  duration: number;
  position: number;
  playbackRate: number;
  playbackState: 'playing' | 'paused' | 'stopped' | 'buffering';
}

export interface AccessibilityOptions {
  enableVoiceOver: boolean;
  enableReducedMotion: boolean;
  enableHighContrast: boolean;
  fontSize: 'small' | 'medium' | 'large' | 'extraLarge';
  enableHapticFeedback: boolean;
}

class HIGAudioControlsService {
  private isInitialized = false;
  private activeControls: Map<string, HIGAudioControl> = new Map();
  private uiSounds: Map<string, UISound> = new Map();
  private mediaSession: MediaSessionMetadata | null = null;
  private accessibilityOptions: AccessibilityOptions;
  private listeners: Set<(event: any) => void> = new Set();

  // HIG-compliant system audio controls
  public readonly systemControls: HIGAudioControl[] = [
    {
      id: 'play',
      type: 'play',
      title: 'Play',
      systemIcon: Platform.OS === 'ios' ? 'play.fill' : 'play_arrow',
      enabled: true,
      visible: true,
      accessibilityLabel: 'Play audio',
      accessibilityHint: 'Starts audio playback'
    },
    {
      id: 'pause',
      type: 'pause',
      title: 'Pause',
      systemIcon: Platform.OS === 'ios' ? 'pause.fill' : 'pause',
      enabled: true,
      visible: false, // Initially hidden
      accessibilityLabel: 'Pause audio',
      accessibilityHint: 'Pauses audio playback'
    },
    {
      id: 'stop',
      type: 'stop',
      title: 'Stop',
      systemIcon: Platform.OS === 'ios' ? 'stop.fill' : 'stop',
      enabled: true,
      visible: true,
      accessibilityLabel: 'Stop audio',
      accessibilityHint: 'Stops audio playback completely'
    },
    {
      id: 'skip_forward_15',
      type: 'skip-forward',
      title: 'Skip Forward 15s',
      systemIcon: Platform.OS === 'ios' ? 'goforward.15' : 'forward_15',
      enabled: true,
      visible: true,
      accessibilityLabel: 'Skip forward 15 seconds',
      accessibilityHint: 'Moves playback position forward by 15 seconds'
    },
    {
      id: 'skip_backward_15',
      type: 'skip-backward',
      title: 'Skip Backward 15s',
      systemIcon: Platform.OS === 'ios' ? 'gobackward.15' : 'replay_15',
      enabled: true,
      visible: true,
      accessibilityLabel: 'Skip backward 15 seconds',
      accessibilityHint: 'Moves playback position backward by 15 seconds'
    }
  ];

  // Subtle UI feedback sounds following HIG
  public readonly systemUISounds: UISound[] = [
    {
      id: 'button_tap',
      name: 'Button Tap',
      type: 'feedback',
      soundFile: 'system://button_tap',
      volume: 0.3,
      priority: 'low',
      respectsSilentMode: true,
      duration: 50
    },
    {
      id: 'success_chime',
      name: 'Success Chime',
      type: 'success',
      soundFile: 'system://success',
      volume: 0.5,
      priority: 'medium',
      respectsSilentMode: false,
      duration: 200
    },
    {
      id: 'error_beep',
      name: 'Error Beep',
      type: 'error',
      soundFile: 'system://error',
      volume: 0.4,
      priority: 'high',
      respectsSilentMode: false,
      duration: 300
    },
    {
      id: 'navigation_swoosh',
      name: 'Navigation Swoosh',
      type: 'navigation',
      soundFile: 'system://navigation',
      volume: 0.2,
      priority: 'low',
      respectsSilentMode: true,
      duration: 150
    },
    {
      id: 'radio_tune',
      name: 'Radio Tune',
      type: 'feedback',
      soundFile: 'assets://radio_tune.wav',
      volume: 0.3,
      priority: 'medium',
      respectsSilentMode: true,
      duration: 400
    }
  ];

  constructor() {
    this.accessibilityOptions = {
      enableVoiceOver: false,
      enableReducedMotion: false,
      enableHighContrast: false,
      fontSize: 'medium',
      enableHapticFeedback: true
    };

    this.initializeHIGControls();
  }

  private async initializeHIGControls(): Promise<void> {
    try {
      console.log('🎮 Initializing HIG-compliant audio controls...');

      // Initialize system controls
      this.initializeSystemControls();

      // Load UI sounds
      await this.loadUISounds();

      // Configure accessibility
      await this.configureAccessibility();

      // Setup media session
      await this.initializeMediaSession();

      this.isInitialized = true;
      console.log('✅ HIG Audio Controls Service initialized');
    } catch (error) {
      console.error('❌ Failed to initialize HIG Audio Controls:', error);
    }
  }

  private initializeSystemControls(): void {
    try {
      // Add system controls to active controls map
      this.systemControls.forEach(control => {
        this.activeControls.set(control.id, { ...control });
      });

      console.log(`🎛️ Loaded ${this.systemControls.length} system audio controls`);
    } catch (error) {
      console.error('❌ Failed to initialize system controls:', error);
    }
  }

  private async loadUISounds(): Promise<void> {
    try {
      // Load and cache UI sounds
      for (const sound of this.systemUISounds) {
        this.uiSounds.set(sound.id, { ...sound });
      }

      console.log(`🔊 Loaded ${this.systemUISounds.length} UI feedback sounds`);
    } catch (error) {
      console.error('❌ Failed to load UI sounds:', error);
    }
  }

  private async configureAccessibility(): Promise<void> {
    try {
      // Configure accessibility options based on system settings
      // In real implementation: Read from AccessibilityInfo
      
      console.log('♿ Configured accessibility options');
    } catch (error) {
      console.error('❌ Failed to configure accessibility:', error);
    }
  }

  private async initializeMediaSession(): Promise<void> {
    try {
      // Initialize media session for lock screen controls
      // In real implementation: Configure MPNowPlayingInfoCenter (iOS) or MediaSession (Android)
      
      console.log('📱 Initialized media session for system integration');
    } catch (error) {
      console.error('❌ Failed to initialize media session:', error);
    }
  }

  /**
   * Update media session metadata following HIG
   */
  async updateMediaSession(metadata: MediaSessionMetadata): Promise<boolean> {
    try {
      this.mediaSession = { ...metadata };

      // Update system media controls
      if (Platform.OS === 'ios') {
        // Update MPNowPlayingInfoCenter
        const nowPlayingInfo = {
          [MPMediaItemPropertyTitle]: metadata.title,
          [MPMediaItemPropertyArtist]: metadata.artist,
          [MPMediaItemPropertyAlbumTitle]: metadata.album,
          [MPMediaItemPropertyPlaybackDuration]: metadata.duration,
          [MPNowPlayingInfoPropertyElapsedPlaybackTime]: metadata.position,
          [MPNowPlayingInfoPropertyPlaybackRate]: metadata.playbackRate,
        };
        
        // MPNowPlayingInfoCenter.defaultCenter.nowPlayingInfo = nowPlayingInfo;
        console.log('📱 Updated iOS media session');
      } else {
        // Update Android MediaSession
        console.log('📱 Updated Android media session');
      }

      // Update control visibility based on playback state
      await this.updateControlVisibility(metadata.playbackState);

      this.notifyListeners({
        type: 'mediaSessionUpdated',
        metadata
      });

      return true;
    } catch (error) {
      console.error('❌ Failed to update media session:', error);
      return false;
    }
  }

  /**
   * Update control visibility based on playback state
   */
  private async updateControlVisibility(playbackState: string): Promise<void> {
    try {
      const playControl = this.activeControls.get('play');
      const pauseControl = this.activeControls.get('pause');

      if (playControl && pauseControl) {
        if (playbackState === 'playing') {
          playControl.visible = false;
          pauseControl.visible = true;
        } else {
          playControl.visible = true;
          pauseControl.visible = false;
        }
      }

      console.log(`🎮 Updated control visibility for state: ${playbackState}`);
    } catch (error) {
      console.error('❌ Failed to update control visibility:', error);
    }
  }

  /**
   * Play UI feedback sound following HIG guidelines
   */
  async playUISound(soundId: string): Promise<boolean> {
    try {
      const sound = this.uiSounds.get(soundId);
      if (!sound) {
        console.log(`⚠️ UI sound not found: ${soundId}`);
        return false;
      }

      // Check if sound should respect silent mode
      const shouldPlay = !sound.respectsSilentMode || await this.shouldPlaySound();

      if (!shouldPlay) {
        console.log(`🔇 UI sound skipped (silent mode): ${sound.name}`);
        return true; // Return true as it's expected behavior
      }

      // Play sound with appropriate volume and timing
      await this.playSoundFile(sound);

      // Provide haptic feedback if enabled
      if (this.accessibilityOptions.enableHapticFeedback) {
        await this.provideHapticFeedback(sound.type);
      }

      console.log(`🔊 Played UI sound: ${sound.name}`);
      return true;
    } catch (error) {
      console.error('❌ Failed to play UI sound:', error);
      return false;
    }
  }

  /**
   * Add custom audio control (only if unique functionality)
   */
  async addCustomControl(control: HIGAudioControl): Promise<boolean> {
    try {
      // Validate that custom control provides unique functionality
      if (control.type !== 'custom') {
        console.log('⚠️ Custom controls should use type: "custom"');
        return false;
      }

      // Check for conflicts with system controls
      const hasConflict = Array.from(this.activeControls.values()).some(
        existingControl => existingControl.title === control.title
      );

      if (hasConflict) {
        console.log('⚠️ Custom control conflicts with existing control');
        return false;
      }

      this.activeControls.set(control.id, { ...control });

      console.log(`🎛️ Added custom control: ${control.title}`);
      
      this.notifyListeners({
        type: 'customControlAdded',
        control
      });

      return true;
    } catch (error) {
      console.error('❌ Failed to add custom control:', error);
      return false;
    }
  }

  /**
   * Configure accessibility options
   */
  async setAccessibilityOptions(options: Partial<AccessibilityOptions>): Promise<boolean> {
    try {
      this.accessibilityOptions = {
        ...this.accessibilityOptions,
        ...options
      };

      // Update UI based on accessibility settings
      await this.updateUIForAccessibility();

      console.log('♿ Updated accessibility options');
      
      this.notifyListeners({
        type: 'accessibilityOptionsChanged',
        options: this.accessibilityOptions
      });

      return true;
    } catch (error) {
      console.error('❌ Failed to set accessibility options:', error);
      return false;
    }
  }

  private async updateUIForAccessibility(): Promise<void> {
    try {
      // Update controls based on accessibility settings
      for (const control of this.activeControls.values()) {
        // Enhance labels for VoiceOver users
        if (this.accessibilityOptions.enableVoiceOver) {
          control.accessibilityHint = control.accessibilityHint || `${control.title} button`;
        }

        // Adjust for reduced motion
        if (this.accessibilityOptions.enableReducedMotion) {
          // Disable animations and transitions
        }
      }

      console.log('♿ Updated UI for accessibility');
    } catch (error) {
      console.error('❌ Failed to update UI for accessibility:', error);
    }
  }

  private async shouldPlaySound(): Promise<boolean> {
    try {
      // Check system audio settings
      // In real implementation: Check AVAudioSession silentMode or AudioManager
      return true; // Mock implementation
    } catch (error) {
      console.error('❌ Failed to check audio settings:', error);
      return false;
    }
  }

  private async playSoundFile(sound: UISound): Promise<void> {
    try {
      if (sound.soundFile.startsWith('system://')) {
        // Play system sound
        // In real implementation: AudioServicesPlaySystemSound (iOS) or ToneGenerator (Android)
        console.log(`🎵 Playing system sound: ${sound.soundFile}`);
      } else {
        // Play custom sound file
        const { sound: audioObject } = await Audio.Sound.createAsync(
          { uri: sound.soundFile },
          { shouldPlay: true, volume: sound.volume }
        );
        
        // Clean up after playback
        setTimeout(() => {
          audioObject.unloadAsync();
        }, sound.duration + 100);
      }
    } catch (error) {
      console.error('❌ Failed to play sound file:', error);
    }
  }

  private async provideHapticFeedback(feedbackType: string): Promise<void> {
    try {
      // Provide appropriate haptic feedback
      // In real implementation: UIImpactFeedbackGenerator (iOS) or Vibrator (Android)
      
      const feedbackMap: { [key: string]: string } = {
        'success': 'notificationSuccess',
        'error': 'notificationError',
        'warning': 'notificationWarning',
        'feedback': 'impactLight',
        'navigation': 'impactMedium'
      };

      const feedbackStyle = feedbackMap[feedbackType] || 'impactLight';
      console.log(`📳 Haptic feedback: ${feedbackStyle}`);
    } catch (error) {
      console.error('❌ Failed to provide haptic feedback:', error);
    }
  }

  /**
   * Get control configuration for UI rendering
   */
  getControlConfiguration(controlId: string): HIGAudioControl | null {
    const control = this.activeControls.get(controlId);
    return control ? { ...control } : null;
  }

  /**
   * Get all visible controls
   */
  getVisibleControls(): HIGAudioControl[] {
    return Array.from(this.activeControls.values()).filter(control => control.visible);
  }

  /**
   * Enable/disable control
   */
  async setControlEnabled(controlId: string, enabled: boolean): Promise<boolean> {
    try {
      const control = this.activeControls.get(controlId);
      if (!control) {
        return false;
      }

      control.enabled = enabled;

      this.notifyListeners({
        type: 'controlStateChanged',
        controlId,
        enabled
      });

      return true;
    } catch (error) {
      console.error('❌ Failed to set control enabled:', error);
      return false;
    }
  }

  /**
   * Show/hide control
   */
  async setControlVisible(controlId: string, visible: boolean): Promise<boolean> {
    try {
      const control = this.activeControls.get(controlId);
      if (!control) {
        return false;
      }

      control.visible = visible;

      this.notifyListeners({
        type: 'controlVisibilityChanged',
        controlId,
        visible
      });

      return true;
    } catch (error) {
      console.error('❌ Failed to set control visibility:', error);
      return false;
    }
  }

  /**
   * Get current accessibility options
   */
  getAccessibilityOptions(): AccessibilityOptions {
    return { ...this.accessibilityOptions };
  }

  /**
   * Get current media session
   */
  getMediaSession(): MediaSessionMetadata | null {
    return this.mediaSession ? { ...this.mediaSession } : null;
  }

  /**
   * Add event listener
   */
  addListener(callback: (event: any) => void): () => void {
    this.listeners.add(callback);
    return () => this.listeners.delete(callback);
  }

  private notifyListeners(event: any): void {
    this.listeners.forEach(callback => {
      try {
        callback(event);
      } catch (error) {
        console.error('❌ HIG Controls listener error:', error);
      }
    });
  }

  /**
   * Clean up HIG audio controls service
   */
  async cleanup(): Promise<void> {
    try {
      // Clear active controls
      this.activeControls.clear();

      // Clear UI sounds
      this.uiSounds.clear();

      // Clear media session
      this.mediaSession = null;

      // Clear listeners
      this.listeners.clear();

      console.log('🧹 HIG Audio Controls Service cleaned up');
    } catch (error) {
      console.error('❌ HIG Controls cleanup error:', error);
    }
  }
}

// Export singleton instance
export const higAudioControlsService = new HIGAudioControlsService();
export default HIGAudioControlsService;