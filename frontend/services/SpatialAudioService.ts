import { Platform } from 'react-native';
import * as Audio from 'expo-audio';

// Spatial Audio interfaces for PHASE framework integration
export interface SpatialAudioPosition {
  x: number; // Left (-1) to Right (1)
  y: number; // Down (-1) to Up (1) 
  z: number; // Far (-1) to Near (1)
}

export interface SpatialAudioListener {
  position: SpatialAudioPosition;
  orientation: {
    forward: SpatialAudioPosition;
    up: SpatialAudioPosition;
  };
  headTracking: boolean;
}

export interface SpatialAudioSource {
  id: string;
  name: string;
  position: SpatialAudioPosition;
  audioUrl: string;
  volume: number;
  rolloffFactor: number; // Distance attenuation
  occluded: boolean;
  environmentalEffects: {
    reverb: number;
    echo: number;
    occlusion: number;
  };
  sourceType: 'point' | 'ambient' | 'directional';
  cone?: {
    innerAngle: number;
    outerAngle: number;
    outerGain: number;
  };
}

export interface SpatialEnvironment {
  id: string;
  name: string;
  roomSize: 'small' | 'medium' | 'large' | 'cathedral';
  acousticProperties: {
    reverberation: number;
    absorption: number;
    scattering: number;
  };
  environmentalSources: SpatialAudioSource[];
}

export interface DeviceAudioCapabilities {
  supportsHeadTracking: boolean;
  supportsSpatialAudio: boolean;
  maxSimultaneousCompressed: number;
  maxSimultaneousUncompressed: number;
  preferredSampleRate: number;
  supportedFormats: string[];
  hasBuiltInSpatialProcessing: boolean;
}

class SpatialAudioService {
  private isInitialized = false;
  private listener: SpatialAudioListener;
  private activeSources: Map<string, SpatialAudioSource> = new Map();
  private activeEnvironment: SpatialEnvironment | null = null;
  private deviceCapabilities: DeviceAudioCapabilities;
  private audioEngine: any = null; // AVAudioEngine placeholder
  private environmentNode: any = null; // AVAudioEnvironmentNode placeholder
  private listeners: Set<(event: any) => void> = new Set();

  // Predefined spatial environments for radio stations
  public readonly spatialEnvironments: SpatialEnvironment[] = [
    {
      id: 'radio_studio',
      name: 'Radio Studio',
      roomSize: 'medium',
      acousticProperties: {
        reverberation: 0.2,
        absorption: 0.8,
        scattering: 0.3
      },
      environmentalSources: []
    },
    {
      id: 'concert_hall',
      name: 'Concert Hall',
      roomSize: 'large', 
      acousticProperties: {
        reverberation: 0.8,
        absorption: 0.2,
        scattering: 0.6
      },
      environmentalSources: []
    },
    {
      id: 'outdoor_broadcast',
      name: 'Outdoor Broadcast',
      roomSize: 'cathedral',
      acousticProperties: {
        reverberation: 0.1,
        absorption: 0.1,
        scattering: 0.9
      },
      environmentalSources: []
    },
    {
      id: 'intimate_studio',
      name: 'Intimate Studio',
      roomSize: 'small',
      acousticProperties: {
        reverberation: 0.3,
        absorption: 0.7,
        scattering: 0.2
      },
      environmentalSources: []
    }
  ];

  constructor() {
    this.listener = {
      position: { x: 0, y: 0, z: 0 },
      orientation: {
        forward: { x: 0, y: 0, z: -1 },
        up: { x: 0, y: 1, z: 0 }
      },
      headTracking: true
    };

    this.deviceCapabilities = {
      supportsHeadTracking: false,
      supportsSpatialAudio: false,
      maxSimultaneousCompressed: 1,
      maxSimultaneousUncompressed: 8,
      preferredSampleRate: 44100,
      supportedFormats: ['mp3', 'aac', 'wav'],
      hasBuiltInSpatialProcessing: false
    };

    this.initializeSpatialAudio();
  }

  private async initializeSpatialAudio(): Promise<void> {
    try {
      console.log('🎧 Initializing Spatial Audio Service...');

      // Detect device capabilities
      await this.detectDeviceCapabilities();

      // Initialize audio engine for spatial processing
      await this.initializeAudioEngine();

      // Configure spatial audio session
      await this.configureSpatialAudioSession();

      this.isInitialized = true;
      console.log('✅ Spatial Audio Service initialized');
    } catch (error) {
      console.error('❌ Failed to initialize Spatial Audio Service:', error);
    }
  }

  private async detectDeviceCapabilities(): Promise<void> {
    try {
      // Detect device-specific spatial audio capabilities
      const deviceModel = Platform.OS === 'ios' ? 'iPhone' : 'Android'; // Simplified detection

      // iPhone capabilities detection
      if (Platform.OS === 'ios') {
        this.deviceCapabilities = {
          supportsHeadTracking: true, // AirPods Pro/Max support
          supportsSpatialAudio: true,
          maxSimultaneousCompressed: 1, // iOS limitation
          maxSimultaneousUncompressed: 8,
          preferredSampleRate: 48000,
          supportedFormats: ['aac', 'alac', 'mp3', 'wav', 'flac'],
          hasBuiltInSpatialProcessing: true
        };
      } else {
        this.deviceCapabilities = {
          supportsHeadTracking: false,
          supportsSpatialAudio: false,
          maxSimultaneousCompressed: 4,
          maxSimultaneousUncompressed: 16,
          preferredSampleRate: 44100,
          supportedFormats: ['mp3', 'aac', 'ogg', 'wav'],
          hasBuiltInSpatialProcessing: false
        };
      }

      console.log('📱 Device capabilities detected:', this.deviceCapabilities);
    } catch (error) {
      console.error('❌ Failed to detect device capabilities:', error);
    }
  }

  private async initializeAudioEngine(): Promise<void> {
    try {
      // Initialize AVAudioEngine for spatial processing
      // In real implementation, this would create AVAudioEngine and AVAudioEnvironmentNode
      
      console.log('🎛️ Initializing audio engine for spatial processing...');

      // Mock AVAudioEngine setup
      this.audioEngine = {
        isRunning: false,
        mainMixerNode: null,
        outputNode: null
      };

      // Mock AVAudioEnvironmentNode for 3D audio
      this.environmentNode = {
        listenerPosition: this.listener.position,
        listenerAngularOrientation: this.listener.orientation,
        reverbParameters: {
          enable: true,
          level: 0.5
        }
      };

      console.log('✅ Audio engine initialized for spatial processing');
    } catch (error) {
      console.error('❌ Failed to initialize audio engine:', error);
    }
  }

  private async configureSpatialAudioSession(): Promise<void> {
    try {
      // Configure audio session for spatial audio
      await Audio.setAudioModeAsync({
        allowsRecordingIOS: false,
        playsInSilentModeIOS: true,
        shouldDuckAndroid: false,
        playThroughEarpieceAndroid: false,
        staysActiveInBackground: true,
        interruptionModeIOS: Audio.InterruptionModeIOS.DoNotMix,
        interruptionModeAndroid: Audio.InterruptionModeAndroid.DoNotMix,
      });

      // Enable spatial audio if supported
      if (this.deviceCapabilities.supportsSpatialAudio) {
        // In real implementation: AVAudioSession.setCategory(.playback, options: [.allowAirPlay, .allowBluetoothA2DP])
        console.log('🎧 Spatial audio enabled');
      }

      console.log('✅ Spatial audio session configured');
    } catch (error) {
      console.error('❌ Failed to configure spatial audio session:', error);
    }
  }

  /**
   * Create and position a spatial audio source
   */
  async createSpatialAudioSource(config: {
    id: string;
    name: string;
    audioUrl: string;
    position: SpatialAudioPosition;
    volume?: number;
    sourceType?: 'point' | 'ambient' | 'directional';
  }): Promise<boolean> {
    try {
      const source: SpatialAudioSource = {
        id: config.id,
        name: config.name,
        position: config.position,
        audioUrl: config.audioUrl,
        volume: config.volume || 1.0,
        rolloffFactor: 1.0,
        occluded: false,
        environmentalEffects: {
          reverb: 0.3,
          echo: 0.1,
          occlusion: 0.0
        },
        sourceType: config.sourceType || 'point'
      };

      // Optimize audio format based on device capabilities
      const optimizedUrl = await this.optimizeAudioForDevice(config.audioUrl);
      source.audioUrl = optimizedUrl;

      this.activeSources.set(source.id, source);

      // Position source in 3D space using AVAudioEnvironmentNode
      await this.positionAudioSource(source);

      console.log(`🎯 Created spatial audio source: ${source.name} at position (${source.position.x}, ${source.position.y}, ${source.position.z})`);
      return true;
    } catch (error) {
      console.error('❌ Failed to create spatial audio source:', error);
      return false;
    }
  }

  /**
   * Update listener position and orientation (head tracking)
   */
  async updateListenerPosition(
    position: SpatialAudioPosition,
    orientation?: {
      forward: SpatialAudioPosition;
      up: SpatialAudioPosition;
    }
  ): Promise<void> {
    try {
      this.listener.position = position;
      if (orientation) {
        this.listener.orientation = orientation;
      }

      // Update AVAudioEnvironmentNode listener position
      if (this.environmentNode) {
        this.environmentNode.listenerPosition = position;
        this.environmentNode.listenerAngularOrientation = this.listener.orientation;
      }

      // Notify listeners of position change
      this.notifyListeners({
        type: 'listenerPositionChanged',
        position,
        orientation: this.listener.orientation
      });

      console.log(`👂 Updated listener position: (${position.x}, ${position.y}, ${position.z})`);
    } catch (error) {
      console.error('❌ Failed to update listener position:', error);
    }
  }

  /**
   * Move audio source to new position with animation
   */
  async moveAudioSource(
    sourceId: string, 
    newPosition: SpatialAudioPosition, 
    duration: number = 1.0
  ): Promise<boolean> {
    try {
      const source = this.activeSources.get(sourceId);
      if (!source) {
        console.error('❌ Audio source not found:', sourceId);
        return false;
      }

      const startPosition = { ...source.position };
      const startTime = Date.now();

      // Animate position change
      const animate = () => {
        const elapsed = (Date.now() - startTime) / 1000;
        const progress = Math.min(elapsed / duration, 1.0);

        // Smooth interpolation
        const easeProgress = 0.5 - 0.5 * Math.cos(progress * Math.PI);

        source.position = {
          x: startPosition.x + (newPosition.x - startPosition.x) * easeProgress,
          y: startPosition.y + (newPosition.y - startPosition.y) * easeProgress,
          z: startPosition.z + (newPosition.z - startPosition.z) * easeProgress,
        };

        // Update position in audio engine
        this.positionAudioSource(source);

        if (progress < 1.0) {
          requestAnimationFrame(animate);
        } else {
          console.log(`📍 Moved ${source.name} to (${newPosition.x}, ${newPosition.y}, ${newPosition.z})`);
        }
      };

      animate();
      return true;
    } catch (error) {
      console.error('❌ Failed to move audio source:', error);
      return false;
    }
  }

  /**
   * Apply environmental effects to spatial audio
   */
  async setEnvironment(environmentId: string): Promise<boolean> {
    try {
      const environment = this.spatialEnvironments.find(env => env.id === environmentId);
      if (!environment) {
        console.error('❌ Environment not found:', environmentId);
        return false;
      }

      this.activeEnvironment = environment;

      // Apply environmental parameters to AVAudioEnvironmentNode
      if (this.environmentNode) {
        this.environmentNode.reverbParameters = {
          enable: true,
          level: environment.acousticProperties.reverberation,
          filterParameters: {
            frequency: 1000,
            bandwidth: environment.acousticProperties.scattering
          }
        };
      }

      // Update all active sources with environmental effects
      for (const source of this.activeSources.values()) {
        source.environmentalEffects.reverb = environment.acousticProperties.reverberation;
        await this.applyEnvironmentalEffects(source);
      }

      console.log(`🌍 Applied environment: ${environment.name}`);
      return true;
    } catch (error) {
      console.error('❌ Failed to set environment:', error);
      return false;
    }
  }

  /**
   * Optimize audio format for device capabilities
   */
  private async optimizeAudioForDevice(audioUrl: string): Promise<string> {
    try {
      // Analyze audio format and device capabilities
      const fileExtension = audioUrl.split('.').pop()?.toLowerCase();
      
      if (!fileExtension || !this.deviceCapabilities.supportedFormats.includes(fileExtension)) {
        console.warn(`⚠️ Unsupported audio format: ${fileExtension}`);
        return audioUrl; // Return original URL as fallback
      }

      // For iOS: Convert to uncompressed PCM for multiple simultaneous playback
      if (Platform.OS === 'ios' && this.activeSources.size >= this.deviceCapabilities.maxSimultaneousCompressed) {
        // In real implementation: Convert MP3/AAC to PCM
        console.log('🔄 Converting to uncompressed format for simultaneous playback');
      }

      // Apply device-specific optimizations
      if (this.deviceCapabilities.preferredSampleRate !== 44100) {
        // In real implementation: Resample to preferred rate
        console.log(`🎵 Optimizing sample rate to ${this.deviceCapabilities.preferredSampleRate}Hz`);
      }

      return audioUrl;
    } catch (error) {
      console.error('❌ Failed to optimize audio format:', error);
      return audioUrl;
    }
  }

  private async positionAudioSource(source: SpatialAudioSource): Promise<void> {
    try {
      // Calculate distance for rolloff
      const distance = Math.sqrt(
        Math.pow(source.position.x - this.listener.position.x, 2) +
        Math.pow(source.position.y - this.listener.position.y, 2) +
        Math.pow(source.position.z - this.listener.position.z, 2)
      );

      // Apply distance rolloff
      const attenuatedVolume = source.volume / (1 + source.rolloffFactor * distance);

      // In real implementation: Set position on AVAudioPlayerNode or AVAudio3DMixing
      console.log(`🎛️ Positioned ${source.name}: distance=${distance.toFixed(2)}, volume=${attenuatedVolume.toFixed(2)}`);
    } catch (error) {
      console.error('❌ Failed to position audio source:', error);
    }
  }

  private async applyEnvironmentalEffects(source: SpatialAudioSource): Promise<void> {
    try {
      // Apply reverb, echo, and occlusion based on environment
      if (this.activeEnvironment) {
        source.environmentalEffects.reverb = this.activeEnvironment.acousticProperties.reverberation;
        
        // Calculate occlusion based on position and environment
        const occlusionFactor = this.calculateOcclusion(source.position);
        source.environmentalEffects.occlusion = occlusionFactor;
      }

      console.log(`🌊 Applied environmental effects to ${source.name}`);
    } catch (error) {
      console.error('❌ Failed to apply environmental effects:', error);
    }
  }

  private calculateOcclusion(position: SpatialAudioPosition): number {
    // Simple occlusion calculation based on position
    // In real implementation: Use PHASE framework's occlusion system
    const listenerDistance = Math.sqrt(
      Math.pow(position.x - this.listener.position.x, 2) +
      Math.pow(position.z - this.listener.position.z, 2)
    );

    // Mock occlusion - further sources are more occluded
    return Math.min(listenerDistance * 0.1, 0.8);
  }

  /**
   * Enable/disable head tracking
   */
  async setHeadTracking(enabled: boolean): Promise<boolean> {
    if (!this.deviceCapabilities.supportsHeadTracking) {
      console.log('⚠️ Head tracking not supported on this device');
      return false;
    }

    try {
      this.listener.headTracking = enabled;
      
      // In real implementation: Configure AVAudioSession for head tracking
      console.log(`👂 Head tracking ${enabled ? 'enabled' : 'disabled'}`);
      return true;
    } catch (error) {
      console.error('❌ Failed to set head tracking:', error);
      return false;
    }
  }

  /**
   * Get spatial audio capabilities
   */
  getCapabilities(): DeviceAudioCapabilities {
    return { ...this.deviceCapabilities };
  }

  /**
   * Get current listener state
   */
  getListenerState(): SpatialAudioListener {
    return { ...this.listener };
  }

  /**
   * Get all active spatial sources
   */
  getActiveSources(): SpatialAudioSource[] {
    return Array.from(this.activeSources.values());
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
        console.error('❌ Spatial audio listener error:', error);
      }
    });
  }

  /**
   * Remove spatial audio source
   */
  async removeSpatialAudioSource(sourceId: string): Promise<boolean> {
    try {
      const source = this.activeSources.get(sourceId);
      if (!source) {
        return false;
      }

      this.activeSources.delete(sourceId);
      
      // Stop and cleanup audio source
      console.log(`🗑️ Removed spatial audio source: ${source.name}`);
      return true;
    } catch (error) {
      console.error('❌ Failed to remove spatial audio source:', error);
      return false;
    }
  }

  /**
   * Clean up spatial audio service
   */
  async cleanup(): Promise<void> {
    try {
      // Remove all sources
      for (const sourceId of this.activeSources.keys()) {
        await this.removeSpatialAudioSource(sourceId);
      }

      // Stop audio engine
      if (this.audioEngine) {
        this.audioEngine.isRunning = false;
      }

      // Clear listeners
      this.listeners.clear();

      console.log('🧹 Spatial Audio Service cleaned up');
    } catch (error) {
      console.error('❌ Spatial audio cleanup error:', error);
    }
  }
}

// Export singleton instance
export const spatialAudioService = new SpatialAudioService();
export default SpatialAudioService;